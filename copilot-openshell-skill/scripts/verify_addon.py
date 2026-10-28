#!/usr/bin/env python3
"""Verify a named Copilot add-on through an existing gateway; never install/delete resources."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

HOSTS = ('api.githubcopilot.com', 'api.individual.githubcopilot.com',
         'api.business.githubcopilot.com', 'api.enterprise.githubcopilot.com')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--gateway', required=True)
    p.add_argument('--workspace', default='default')
    p.add_argument('--sandbox', default='copilot-lab')
    p.add_argument('--service-host', choices=HOSTS, default=HOSTS[0])
    p.add_argument('--model-smoke', action='store_true')
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    if a.output and a.output.exists():
        p.error('Evidence output already exists; choose a new filename')
    prefix = ['openshell', '--gateway', a.gateway, '--workspace', a.workspace]
    results = []

    def run(args, timeout=35):
        try:
            r = subprocess.run(prefix + args, capture_output=True, text=True, timeout=timeout)
            return r.returncode, r.stdout, r.stderr
        except subprocess.TimeoutExpired:
            return 124, '', 'Command timed out'
        except FileNotFoundError:
            return 127, '', 'OpenShell CLI not installed'

    def remote(args, timeout=35):
        return run(['sandbox', 'exec', '-n', a.sandbox, '--workdir', '/sandbox',
                    '--timeout', str(max(1, timeout - 5)), '--no-tty', '--'] + args, timeout)

    def result(name, passed, note):
        results.append({'check': name, 'status': 'PASS' if passed else 'FAIL', 'note': note})

    rc, _, _ = run(['status'])
    result('existing-gateway-reachable', rc == 0, 'Uses the explicitly named existing gateway')
    if rc:
        print(json.dumps({'all_requested_checks_passed': False, 'results': results}, indent=2))
        return 1
    rc, version, _ = remote(['copilot', '--version'])
    result('copilot-executable', rc == 0 and bool(re.search(r'\d+\.\d+\.\d+', version)),
           'Copilot version command returned successfully' if rc == 0 else 'Inspect the image/runtime')
    rc, identity, _ = remote(['id', '-un'])
    result('nonroot-sandbox-identity', rc == 0 and identity.strip() == 'sandbox',
           'Expected the configured sandbox user')
    rc, _, _ = remote(['sh', '-c', 'umask 077; p=/sandbox/.copilot-addon-probe-$$; : > "$p" && rm -f "$p"'])
    result('allowed-workspace-write', rc == 0, 'Created and removed only a disposable probe file')
    rc, mode, _ = remote(['stat', '-c', '%a', '/var/tmp'])
    mode_ok = rc == 0 and mode.strip() == '1777'
    rc, _, _ = remote(['sh', '-c',
        'p=/var/tmp/.copilot-addon-probe-$$; if touch "$p"; then rm -f "$p"; exit 0; else exit 1; fi'])
    result('outside-path-write-denied', mode_ok and rc != 0 and rc != 124,
           'Requires allowed-path control and mode 1777; inspect SELinux before attributing specifically to Landlock')

    token = os.environ.get('COPILOT_GITHUB_TOKEN')
    if token:
        rc, digest, _ = remote(['python3', '-c',
            'import hashlib,os; v=os.environ.get("COPILOT_GITHUB_TOKEN",""); '
            'print(hashlib.sha256(v.encode()).hexdigest() if v else "MISSING")'])
        observed = digest.strip()
        ok = rc == 0 and bool(re.fullmatch('[0-9a-f]{64}', observed)) and observed != hashlib.sha256(token.encode()).hexdigest()
        result('credential-is-present-and-not-real-host-token', ok,
               'Compared only hashes in memory; no token or hash emitted. Pair with successful live inference.')
    else:
        results.append({'check': 'credential-is-present-and-not-real-host-token', 'status': 'NOT_VERIFIED',
                        'note': 'Host token unavailable for a private comparison'})

    rc, _, _ = remote(['sh', '-c', 'command -v curl >/dev/null'])
    curl_available = rc == 0
    _, before, _ = run(['logs', a.sandbox, '--since', '2m'])
    baseline = Counter(before.splitlines())
    attempts = []
    for host in ('example.com', a.service_host):
        rc, _, _ = remote(['curl', '-fsS', '--connect-timeout', '5', '--max-time', '10',
                            'https://' + host + '/'], 20)
        attempts.append((host, curl_available and rc not in (0, 124)))
    # Gateway activity arrives asynchronously. Bound the wait, then require new evidence.
    time.sleep(6)
    rc, after, _ = run(['logs', a.sandbox, '--since', '2m'])
    fresh = []
    for line in after.splitlines():
        if baseline[line]:
            baseline[line] -= 1
        else:
            fresh.append(line)
    for host, failed in attempts:
        evidence = any(host in line and re.search(r'denied|deny|blocked', line, re.I)
                       and 'curl' in line.lower() for line in fresh)
        result('curl-denied-' + host, failed and rc == 0 and evidence,
               'Requires a new matching host/curl denial event; connectivity failure alone is insufficient')

    if a.model_smoke:
        rc, help_text, _ = remote(['copilot', '--help'])
        needed = ('--no-auto-update', '--disable-builtin-mcps', '--deny-tool')
        supported = rc == 0 and all(flag in help_text for flag in needed)
        if supported:
            rc, reply, _ = remote(['copilot', '--no-auto-update', '--disable-builtin-mcps',
                                   '--deny-tool', 'shell', '--deny-tool', 'write', '-p',
                                   'Reply with COPILOT_GATEWAY_OK. Do not use any tools.'], 150)
            result('live-model-smoke', rc == 0 and 'COPILOT_GATEWAY_OK' in reply,
                   'Real provider-backed inference; no prompt/response or credential emitted by this verifier')
        else:
            result('live-model-smoke', False, 'Installed Copilot lacks required tested options; adapt explicitly')
    else:
        results.append({'check': 'live-model-smoke', 'status': 'NOT_VERIFIED',
                        'note': 'Re-run with --model-smoke when the account and provider are ready'})

    report = {'gateway': a.gateway, 'workspace': a.workspace, 'sandbox': a.sandbox,
              'all_requested_checks_passed': all(x['status'] != 'FAIL' for x in results),
              'all_listed_checks_verified': all(x['status'] == 'PASS' for x in results),
              'still_require': ['gateway/unrelated-sandbox before-after inventory',
                               'effective policy/profile/provider attachment inspection',
                               'independent calculator demo and unchanged test checksum'],
              'results': results}
    rendered = json.dumps(report, indent=2)
    if a.output:
        fd = os.open(a.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(rendered + '\n')
    print(rendered)
    return 0 if report['all_requested_checks_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
