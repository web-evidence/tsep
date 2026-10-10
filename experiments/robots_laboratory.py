#!/usr/bin/env python3
"""Collect synthetic robots scenarios over real loopback HTTP. Apache-2.0.

Creates a new evidence folder; no external collection or website modification.
No TS04 conformity claim. The active TS07 comparison retains missing human review.
"""
import argparse
from datetime import datetime, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import socket
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from conformance.evaluate import evaluate
from conformance.http import encoded, message, need
from experiments.robots_policy import GOOGLE, inspect_capture, LIMITATION

VERSION = '2'  # The first local run used Googlebot; active TS07 requires literal googlebot.
SCENARIOS = (
    {'id': 'preproduction', 'before': 'User-agent: *\nDisallow: /\n',
     'after': 'User-agent: *\nAllow: /\n', 'paths': ['/catalogue']},
    {'id': 'essential-css', 'before': 'User-agent: *\nAllow: /\nDisallow: /assets/\n',
     'after': 'User-agent: *\nAllow: /\nDisallow: /assets/\nAllow: /assets/main.css\n',
     'paths': ['/catalogue', '/assets/main.css']},
    {'id': 'noindex-disallow', 'before': 'User-agent: *\nDisallow: /retired\n',
     'after': 'User-agent: *\nAllow: /retired\n', 'paths': ['/retired']},
    {'id': 'correct-control', 'before': 'User-agent: *\nAllow: /\n',
     'after': 'User-agent: *\nAllow: /\n', 'paths': ['/catalogue']},
)


def now():
    return datetime.now(timezone.utc).isoformat()


def write(path, value):
    with path.open('x', encoding='utf-8') as handle:
        handle.write(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def collect(port, path):
    host = '127.0.0.1:'+str(port)
    request = ('GET '+path+' HTTP/1.1\r\nHost: '+host+'\r\nUser-Agent: googlebot\r\nConnection: close\r\n\r\n').encode()
    content = bytearray()
    with socket.create_connection(('127.0.0.1', port), timeout=5) as connection:
        connection.settimeout(5)
        connection.sendall(request)
        while True:
            block = connection.recv(8192)
            if not block:
                break
            content.extend(block)
            need(len(content) <= 512*1024+65536, 'Loopback response bound exceeded')
    return {'url': 'http://'+host+path, 'complete': True,
            'request': encoded(request), 'response': encoded(bytes(content))}


def run(output):
    output.mkdir(parents=True, exist_ok=False)
    plan = {'label': 'SYNTHETIC LABORATORY; real loopback sockets, fictional defects',
            'declared_at': now(), 'profile': GOOGLE, 'scenarios': list(SCENARIOS),
            'expected_policy': 'allow for every listed path, including essential CSS and the noindex document',
            'indexing_intent': {'/retired': 'exclude'}, 'limitation': LIMITATION}
    write(output/'plan-before-capture.json', plan)
    state, journal = {}, []

    class Handler(BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'

        def log_message(self, *_):
            pass

        def do_GET(self):
            journal.append({'scenario': state['scenario'], 'phase': state['phase'],
                            'path': self.path, 'observed_at': now()})
            kind = 'text/html; charset=utf-8'
            body = '<html><head><title>Laboratory</title></head><body><h1>Catalogue</h1></body></html>'
            if self.path == '/robots.txt':
                kind, body = 'text/plain; charset=utf-8', state['robots']
            elif self.path == '/assets/main.css':
                kind, body = 'text/css; charset=utf-8', 'body { color: black; }'
            elif self.path == '/retired':
                body = '<html><head><meta name="robots" content="noindex"></head><body><h1>Retired</h1></body></html>'
            raw = body.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', kind)
            self.send_header('Content-Length', str(len(raw)))
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(raw)
            self.close_connection = True

    server = HTTPServer(('127.0.0.1', 0), Handler)
    server.timeout = 5
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    rows = []
    try:
        port = server.server_address[1]
        origin = 'http://127.0.0.1:'+str(port)+'/'
        for scenario in SCENARIOS:
            for phase in ('before', 'after'):
                state.update(scenario=scenario['id'], phase=phase, robots=scenario[phase])
                folder = output/scenario['id']/phase
                folder.mkdir(parents=True)
                robot_hop = collect(port, '/robots.txt')
                captured = now()
                for number, path in enumerate(scenario['paths'], 1):
                    data = {'profile': GOOGLE, 'origin': origin, 'target': origin.rstrip('/')+path,
                            'product_token': 'Googlebot', 'request_user_agent': 'googlebot',
                            'declared_at': plan['declared_at'], 'observed_at': captured,
                            'context': {'network': '127.0.0.1 synthetic laboratory', 'bounds': 'one complete robots response; 500 KiB body model',
                                        'tool': 'tsep-experimental-robots-laboratory', 'tool_version': VERSION},
                            'http': [robot_hop]}
                    page = collect(port, path)
                    write(folder/('input-'+str(number)+'.json'), data)
                    write(folder/('resource-'+str(number)+'.json'), {'captured_at': now(), 'http': [page],
                                                                   'role': 'required-css' if path.endswith('.css') else 'document'})
                    result = inspect_capture(data)
                    write(folder/('observation-'+str(number)+'.json'), result)
                    row = {'scenario': scenario['id'], 'phase': phase, 'path': path,
                           'expected_policy': 'allow', 'observed_model': result['decision'],
                           'winning_lines': result.get('body_reading', {}).get('winning_lines', []),
                           'resource_http_status': message(page['response'], True)[0], 'synthetic': True}
                    if scenario['id'] == 'noindex-disallow':
                        target = {'url': data['target'], 'observed_at': now(), 'context': data['context'],
                                  'intent': {'declared_at': plan['declared_at'], 'crawler': 'googlebot',
                                             'public_canonical': True, 'indexing': 'exclude', 'access_basis': 'test-client-only'},
                                  'http': [page], 'robots': {'observed_at': captured, 'http': [robot_hop]}}
                        active = {'input_version': '2', 'rules': ['TS07-A01', 'TS07-A02'], 'targets': [target]}
                        write(folder/'active-ts07-input.json', active)
                        comparison = evaluate(active)
                        write(folder/'active-ts07-comparison.json', comparison)
                        row['active_ts07'] = comparison
                    rows.append(row)
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)
    write(output/'request-journal.json', journal)
    summary = {'label': plan['label'], 'observed_at': now(), 'network_requests': len(journal),
               'external_requests': 0, 'rows': rows, 'limitation': LIMITATION,
               'human_review': 'None supplied; active TS07 access remains inconclusive after correction',
               'source_files': {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in (
                   'experiments/robots_laboratory.py', 'experiments/robots_policy.py',
                   'conformance/evaluate.py', 'conformance/http.py', 'tsep.py')}}
    write(output/'summary.json', summary)
    inventory = sorted(p for p in output.rglob('*') if p.is_file())
    (output/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(output).as_posix()+'\n' for p in inventory))
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        summary = run(args.output)
        print(json.dumps({'output': str(args.output), 'network_requests': summary['network_requests'],
                          'decisions': [r['observed_model'] for r in summary['rows']], 'scope': summary['label']}))
    except (ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(64)
