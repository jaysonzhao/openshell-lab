#!/usr/bin/env python3
"""Workshop browser client; fixed guardrails upstream, no Kubernetes permissions."""
import json
import os
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
BASE = os.environ.get('GUARDRAILS_BASE_URL', '').rstrip('/')
MODEL = os.environ.get('MODEL_NAME', '')
CONFIG_ID = os.environ.get('GUARDRAILS_CONFIG_ID', 'nemo-guardrails-config')
MAX_BODY = 32768
MAX_RESPONSE = 4 * 1024 * 1024


def upstream(path, payload=None):
    headers = {'Accept': 'application/json'}
    data = None
    if payload is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(payload).encode()
    if os.environ.get('GUARDRAILS_API_KEY'):
        headers['Authorization'] = 'Bearer ' + os.environ['GUARDRAILS_API_KEY']
    request = Request(BASE + path, data=data, headers=headers)
    with urlopen(request, timeout=4 if path == '/health' else 120) as response:
        if path == '/health':
            return {'reachable': True}
        body = response.read(MAX_RESPONSE + 1)
        if len(body) > MAX_RESPONSE:
            raise ValueError('response too large')
        return json.loads(body or b'{}')


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Avoid storing prompts, response text or credentials in application logs.
        return

    def send(self, status, body, content_type='application/json'):
        if content_type == 'application/json':
            body = json.dumps(body).encode()
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/live':
            return self.send(200, {'alive': True})
        if self.path == '/api/health':
            try:
                upstream('/health')
                return self.send(200, {'ready': True, 'model': MODEL, 'config_id': CONFIG_ID})
            except Exception:
                return self.send(503, {'ready': False, 'error': 'Guardrails service unavailable'})
        assets = {'/': ('index.html', 'text/html; charset=utf-8'),
                  '/app.js': ('app.js', 'text/javascript; charset=utf-8')}
        if self.path in assets:
            file, kind = assets[self.path]
            return self.send(200, (ROOT / file).read_bytes(), kind)
        return self.send(404, {'error': 'Not found'})

    def do_POST(self):
        if self.path not in ('/api/chat', '/api/check'):
            return self.send(404, {'error': 'Not found'})
        origin = self.headers.get('Origin')
        if origin and urlsplit(origin).netloc != self.headers.get('Host'):
            return self.send(403, {'error': 'Origin rejected'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if size <= 0 or size > MAX_BODY:
                return self.send(413, {'error': 'Request size rejected'})
            body = json.loads(self.rfile.read(size))
            prompt = body.get('prompt') if isinstance(body, dict) else None
            if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 8000:
                return self.send(400, {'error': 'Provide a prompt of 1–8000 characters'})
        except (ValueError, UnicodeDecodeError):
            return self.send(400, {'error': 'Invalid JSON request'})
        payload = {'model': MODEL, 'messages': [{'role': 'user', 'content': prompt}]}
        if self.path == '/api/check':
            payload.update(config_id=CONFIG_ID, rail_types=['input'])
            path = '/checks'
        else:
            payload['stream'] = False
            path = '/chat/completions'
        try:
            result = upstream(path, payload)
            return self.send(200, result)
        except HTTPError as exc:
            return self.send(502, {'error': 'Guardrails upstream rejected the request',
                                   'upstream_status': exc.code})
        except Exception:
            return self.send(502, {'error': 'Guardrails request failed; inspect server health and configuration'})


def main():
    parts = urlsplit(BASE)
    if parts.scheme not in ('http', 'https') or not parts.netloc or not MODEL:
        raise SystemExit('Set GUARDRAILS_BASE_URL (including /v1) and MODEL_NAME')
    if parts.path.rstrip('/') != '/v1' or parts.query or parts.fragment or parts.username:
        raise SystemExit('Use the guardrails service URL ending /v1 without credentials/query')
    ThreadingHTTPServer((os.environ.get('BIND_ADDRESS', '127.0.0.1'),
                         int(os.environ.get('PORT', '8080'))), Handler).serve_forever()


if __name__ == '__main__':
    main()
