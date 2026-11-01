#!/usr/bin/env python3
"""Render nonsecret OpenClaw/OpenShell 0.1.2 inputs for the pod-only track."""
import argparse
import copy
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import urlsplit, urlunsplit

import yaml


def executable(value):
    path = PurePosixPath(value)
    if (not path.is_absolute() or '..' in path.parts
            or any(c in value for c in '*?[]\\\r\n\t ')
            or not value.startswith(('/usr/', '/opt/', '/bin/'))
            or value != str(path)):
        raise argparse.ArgumentTypeError('Use an exact executable path on a read-only image filesystem')
    return value


def endpoint(value, keyless):
    if any(c.isspace() or ord(c) < 32 for c in value):
        raise ValueError('Endpoint URL must not contain whitespace or control characters')
    try:
        url = urlsplit(value)
        port = url.port or (443 if url.scheme == 'https' else 80)
        host = url.hostname
    except ValueError as exc:
        raise ValueError('Invalid endpoint URL') from exc
    if (url.scheme not in ('https', 'http') or not host or url.username is not None
            or url.password is not None or url.query or url.fragment
            or not re.fullmatch(r'[A-Za-z0-9.-]+', host)
            or any(not part or len(part) > 63 or part.startswith('-') or part.endswith('-')
                   for part in host.split('.'))
            or not 1 <= port <= 65535
            or not re.fullmatch(r'/[A-Za-z0-9._~/-]*', url.path)
            or '//' in url.path or any(part in ('.', '..') for part in url.path.split('/'))
            or not url.path.rstrip('/').endswith('/v1')):
        raise ValueError('Use an HTTP(S) DNS/IPv4 endpoint ending /v1 without credentials, query or fragment')
    if not keyless and url.scheme != 'https':
        raise ValueError('Keyed endpoints require verified HTTPS; use --keyless only for an endpoint needing no key')
    if host in ('localhost', '127.0.0.1', '0.0.0.0'):
        raise ValueError('Endpoint must be reachable from the supervisor; loopback points at the wrong process')
    base = urlunsplit((url.scheme, url.netloc, url.path.rstrip('/'), '', ''))
    return base, {'host': host.lower(), 'port': port, 'path': url.path.rstrip('/') + '/**',
                  'protocol': 'rest', 'access': 'read-write', 'enforcement': 'enforce'}


def render(args):
    base, model_endpoint = endpoint(args.endpoint, args.keyless)
    if not args.model.strip() or args.model != args.model.strip() or any(c in args.model for c in '\r\n\0'):
        raise ValueError('Supply the exact nonempty model ID reported by the endpoint')
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,62}', args.profile_id):
        raise ValueError('Profile ID must be a lowercase name starting with a letter')
    if not 0 < args.max_tokens <= args.context_window:
        raise ValueError('Require 0 < max-tokens <= context-window')
    policy = {
        'version': 1,
        'filesystem_policy': {'include_workdir': False,
                              'read_only': ['/bin', '/usr', '/lib', '/proc', '/dev/urandom', '/app', '/etc', '/var/log', '/opt'],
                              'read_write': ['/sandbox', '/tmp', '/dev/null']},
        'landlock': {'compatibility': 'hard_requirement'},
        'network_policies': {},
    }
    if args.keyless:
        policy['network_policies']['model_endpoint'] = {
            'endpoints': [model_endpoint], 'binaries': [{'path': args.node_binary}]}
    readonly = copy.deepcopy(policy)
    # The exercise sandbox receives no inference provider or endpoint.
    readonly['network_policies'] = {
        'github_api': {
            'endpoints': [{'host': 'api.github.com', 'port': 443, 'protocol': 'rest',
                           'access': 'read-only', 'enforcement': 'enforce'}],
            'binaries': [{'path': args.curl_binary}],
        }
    }
    deny = copy.deepcopy(policy)
    deny['network_policies'] = {}
    config = {
        'gateway': {'port': 18789, 'bind': 'loopback', 'mode': 'local', 'auth': {'mode': 'none'}},
        'channels': {},
        'agents': {'defaults': {'model': 'vllm/' + args.model, 'sandbox': {'mode': 'off'}}},
        'models': {'mode': 'replace', 'providers': {'vllm': {
            'baseUrl': base, 'api': 'openai-completions',
            'apiKey': 'not-needed' if args.keyless else '${VLLM_API_KEY}',
            'models': [{'id': args.model, 'name': args.model, 'reasoning': False,
                        'input': ['text'], 'contextWindow': args.context_window,
                        'maxTokens': args.max_tokens}],
        }}},
        'plugins': {},
        'tools': {'deny': ['group:web', 'browser']},
    }
    files = {
        'openclaw-config.json': json.dumps(config, indent=2) + '\n',
        'sandbox-policy.yaml': yaml.safe_dump(policy, sort_keys=False),
        'module2-readonly.yaml': yaml.safe_dump(readonly, sort_keys=False),
        'module2-deny.yaml': yaml.safe_dump(deny, sort_keys=False),
    }
    if not args.keyless:
        profile = {
            'id': args.profile_id, 'display_name': 'OpenClaw model endpoint',
            'description': 'Endpoint-bound model credential for the pod-only OpenClaw lab',
            'category': 'inference', 'inference_capable': True,
            'credentials': [{'name': 'api_key', 'env_vars': ['VLLM_API_KEY'], 'required': True,
                             'auth_style': 'bearer', 'header_name': 'authorization'}],
            'discovery': {'credentials': ['api_key']},
            'endpoints': [model_endpoint], 'binaries': [args.node_binary],
        }
        files['model-profile.yaml'] = yaml.safe_dump(profile, sort_keys=False)
    dest = args.out.resolve()
    dest.mkdir(parents=True, exist_ok=True, mode=0o700)
    for name, content in files.items():
        target = dest / name
        if target.is_symlink() or (target.exists() and target.read_text() != content):
            raise ValueError('Refusing to overwrite different content or a symlink: ' + str(target))
    if args.keyless and (dest / 'model-profile.yaml').exists():
        raise ValueError('Use a new output directory when switching to keyless mode')
    for name, content in files.items():
        target = dest / name
        if not target.exists():
            with target.open('x', encoding='utf-8') as handle:
                handle.write(content)
    return dest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--endpoint', required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--keyless', action='store_true')
    parser.add_argument('--profile-id', default='openclaw-model')
    parser.add_argument('--node-binary', type=executable, default='/usr/local/bin/node')
    parser.add_argument('--curl-binary', type=executable, default='/usr/bin/curl')
    parser.add_argument('--context-window', type=int, default=32768)
    parser.add_argument('--max-tokens', type=int, default=4096)
    args = parser.parse_args()
    try:
        print('Rendered nonsecret files:', render(args))
    except (ValueError, OSError) as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    main()
