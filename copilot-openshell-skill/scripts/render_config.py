#!/usr/bin/env python3
"""Render non-secret Copilot policy/profile assets; never contact a gateway."""
import argparse
import json
from pathlib import Path, PurePosixPath
import yaml

ROUTES = {
    'common': 'api.githubcopilot.com',
    'individual': 'api.individual.githubcopilot.com',
    'business': 'api.business.githubcopilot.com',
    'enterprise': 'api.enterprise.githubcopilot.com',
}


def binary(value):
    p = PurePosixPath(value)
    if not p.is_absolute() or '..' in p.parts or any(c in value for c in '\n\r\t '):
        raise argparse.ArgumentTypeError('Use an absolute readonly executable path without traversal or whitespace')
    if any(c in value for c in '*?[]'):
        raise argparse.ArgumentTypeError('Resolve the actual executable; wildcard binary grants are not accepted')
    if not value.startswith(('/usr/', '/opt/', '/bin/')) or value.endswith(('/', '/**', '/*')):
        raise argparse.ArgumentTypeError('Bind an executable under /usr, /opt, or /bin; do not grant a whole directory')
    return value


def documents(route, binaries, hard=True):
    binaries = list(dict.fromkeys(binaries))
    service = {'host': ROUTES[route], 'port': 443, 'protocol': 'rest',
               'tls': 'terminate', 'access': 'read-write', 'enforcement': 'enforce'}
    auth_network = {'host': 'api.github.com', 'port': 443, 'protocol': 'rest',
                    'tls': 'terminate', 'enforcement': 'enforce', 'rules': [
                        {'allow': {'method': 'GET', 'path': '/user'}},
                        {'allow': {'method': 'GET', 'path': '/copilot_internal/**'}},
                    ]}
    policy = {
        'version': 1,
        'filesystem_policy': {
            'include_workdir': True,
            'read_only': ['/usr', '/lib', '/proc', '/dev/urandom', '/app', '/etc', '/var/log', '/opt'],
            'read_write': ['/sandbox', '/tmp', '/dev/null'],
        },
        'landlock': {'compatibility': 'hard_requirement' if hard else 'best_effort'},
        'process': {'run_as_user': 'sandbox', 'run_as_group': 'sandbox'},
        'network_policies': {
            'copilot-service': {'name': 'copilot-service', 'endpoints': [service],
                                 'binaries': [{'path': x} for x in binaries]},
            'copilot-auth': {'name': 'copilot-auth', 'endpoints': [auth_network],
                              'binaries': [{'path': x} for x in binaries]},
        },
    }
    auth_bindings = [
        {'host': 'api.github.com', 'port': 443, 'path': path, 'protocol': 'rest',
         'tls': 'terminate', 'access': 'read-only', 'enforcement': 'enforce'}
        for path in ('/user', '/copilot_internal/**')
    ]
    # Profile policy can compose into a sandbox when gateway provider v2 is already enabled.
    # Preserve the same restrictions in both layers rather than relying on a global toggle.
    for entry in auth_bindings:
        entry.pop('access')
        entry['rules'] = [{'allow': {'method': 'GET', 'path': entry['path']}}]
    profile = {
        'id': 'copilot-cli', 'display_name': 'GitHub Copilot CLI add-on',
        'description': 'Copilot service and narrowly scoped GitHub authentication',
        'category': 'agent',
        'credentials': [{'name': 'api_token', 'description': 'Personal account Copilot Requests token',
                         'env_vars': ['COPILOT_GITHUB_TOKEN'], 'required': True,
                         'auth_style': 'bearer', 'header_name': 'authorization'}],
        'discovery': {'credentials': ['api_token']},
        'endpoints': [dict(service)] + auth_bindings,
        'binaries': binaries,
    }
    return policy, profile


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--route', choices=ROUTES, default='common')
    p.add_argument('--binary', type=binary, action='append', required=True)
    p.add_argument('--best-effort-landlock', action='store_true',
                   help='Explicit reduced-assurance variation; requires recording the deviation')
    a = p.parse_args()
    policy, profile = documents(a.route, a.binary, not a.best_effort_landlock)
    a.out.mkdir(parents=True, exist_ok=True)
    outputs = {'copilot-policy.yaml': policy, 'copilot-cli.yaml': profile}
    rendered_outputs = {name: yaml.safe_dump(content, sort_keys=False) for name, content in outputs.items()}
    for name, rendered in rendered_outputs.items():
        path = a.out / name
        if path.exists() and path.read_text() != rendered:
            p.error(f'{path} already has different content; choose a new output directory')
    for name, rendered in rendered_outputs.items():
        path = a.out / name
        path.write_text(rendered)
    print(json.dumps({'rendered': [str(a.out / x) for x in outputs],
                      'service_host': ROUTES[a.route], 'gateway_mutations': 0}, indent=2))


if __name__ == '__main__':
    main()
