#!/usr/bin/env python3
"""Render a certificate-gated OpenClaw Route through OpenShell 0.1.2."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

import yaml


def dns(value):
    if (value != value.lower() or len(value) > 253 or '.' not in value
            or any(not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', part)
                   for part in value.split('.'))):
        raise argparse.ArgumentTypeError('Use a lowercase DNS name with valid labels')
    return value


def label(value):
    if not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', value) or '--' in value:
        raise argparse.ArgumentTypeError('Use a DNS label without consecutive hyphens')
    return value


def origin(value):
    try:
        url = urlsplit(value)
        port = url.port
    except ValueError as exc:
        raise argparse.ArgumentTypeError('Invalid origin') from exc
    if (any(c.isspace() or ord(c) < 32 for c in value) or '?' in value or '#' in value
            or url.username is not None or url.password is not None
            or url.path or url.query or url.fragment or not url.hostname
            or url.scheme not in ('https', 'http') or (port is not None and not 1 <= port <= 65535)):
        raise argparse.ArgumentTypeError('Use an exact origin without a path or credentials')
    if url.scheme == 'http' and url.hostname not in ('127.0.0.1', 'localhost', '::1'):
        raise argparse.ArgumentTypeError('Plain HTTP origins are limited to loopback')
    if url.scheme == 'https':
        dns(url.hostname)
    host = '[' + url.hostname + ']' if ':' in url.hostname else url.hostname
    suffix = '' if port in (None, 443 if url.scheme == 'https' else 80) else ':' + str(port)
    return url.scheme + '://' + host + suffix


def san(value):
    dns(value[2:] if value.startswith('*.') else value)
    return value


def render(args):
    host = f'{args.workspace}--{args.sandbox}--{args.service}.{args.service_domain}'
    dns(host)  # Also reject an encoded service label longer than 63 characters.
    url = 'https://' + host
    names = list(dict.fromkeys(['*.' + args.service_domain, *args.extra_san]))
    origins = list(dict.fromkeys(['http://127.0.0.1:18789', 'http://localhost:18789',
                                *args.keep_origin, url]))
    values = {
        'server': {'disableTls': False, 'tls': {'enableMtls': True},
                   'enableLoopbackServiceHttp': False},
        'certManager' if args.certificate_mode == 'cert-manager' else 'pkiInitJob': {
            'serverDnsNames': names},
    }
    route = {
        'apiVersion': 'route.openshift.io/v1', 'kind': 'Route',
        'metadata': {'name': args.route_name, 'namespace': args.namespace,
                     'labels': {'app.kubernetes.io/part-of': 'openclaw-pod-lab'},
                     'annotations': {'haproxy.router.openshift.io/timeout': '1800s',
                                     'haproxy.router.openshift.io/timeout-tunnel': '1800s'}},
        'spec': {'host': host, 'to': {'kind': 'Service', 'name': args.release},
                 'port': {'targetPort': 'grpc'}, 'tls': {'termination': 'passthrough'},
                 'wildcardPolicy': 'None'},
    }
    patch = {'gateway': {'controlUi': {'allowedOrigins': origins}}}
    details = {'public_url': url, 'route_host': host, 'workspace': args.workspace,
               'sandbox': args.sandbox, 'service': args.service, 'target_port': 18789,
               'gateway_service': args.release, 'namespace': args.namespace,
               'required_browser_auth': 'client certificate (mTLS)',
               'certificate_mode': args.certificate_mode,
               'certificate_dns_sans': names}
    files = {'gateway-ui-values.yaml': yaml.safe_dump(values, sort_keys=False),
             'openclaw-ui-route.yaml': yaml.safe_dump(route, sort_keys=False),
             'openclaw-ui-patch.json': json.dumps(patch, indent=2) + '\n',
             'external-access.json': json.dumps(details, indent=2) + '\n'}
    dest = args.out.resolve()
    dest.mkdir(mode=0o700, parents=True, exist_ok=True)
    for name, content in files.items():
        target = dest/name
        if target.is_symlink() or (target.exists() and target.read_text() != content):
            raise ValueError('Refusing to overwrite different content or a symlink: ' + str(target))
    for name, content in files.items():
        target = dest/name
        if not target.exists():
            with target.open('x', encoding='utf-8') as handle:
                handle.write(content)
    return url


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--namespace', type=label, required=True)
    parser.add_argument('--release', type=label, required=True,
                        help='Actual gateway Service name, equal to release with the lab fullnameOverride')
    parser.add_argument('--service-domain', type=dns, required=True)
    parser.add_argument('--workspace', type=label, default='default')
    parser.add_argument('--sandbox', type=label, default='openclaw-lab')
    parser.add_argument('--service', type=label, default='ui')
    parser.add_argument('--route-name', type=label, default='openclaw-ui')
    parser.add_argument('--certificate-mode', choices=['builtin', 'cert-manager'], default='builtin')
    parser.add_argument('--extra-san', type=san, action='append', default=[])
    parser.add_argument('--keep-origin', type=origin, action='append', default=[])
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        print('External OpenClaw URL (requires browser mTLS):', render(args))
    except (OSError, ValueError, argparse.ArgumentTypeError) as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    main()
