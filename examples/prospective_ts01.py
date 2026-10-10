#!/usr/bin/env python3
"""Synthetic prospective TS01 laboratory: loopback only, no external requests."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from collectors import ts01
from experiments import prospective


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, *args):
        pass

    def do_GET(self):
        case = self.path.strip('/')
        after = self.server.measuring
        self.server.requests.append({'path': self.path, 'phase': 'measurement' if after else 'reference'})
        if case == 'different-url' and after:
            self.send_response(302)
            self.send_header('Location', '/destination')
            self.send_header('Content-Length', '0')
            self.end_headers()
            return
        marker = 'Other' if case == 'required-missing' and after else 'Expected'
        extra = '<p>Forbidden</p>' if case == 'forbidden-present' and after else ''
        if case == 'unsupported-reading' and after:
            extra += '<iframe>Unsupported context</iframe>'
        fallback = '' if case == 'markers-simple' else '<noscript><img alt="Other"></noscript>'
        nonce = 'fixed' if case in ('digest-same', 'http-error') else str(after)
        body = ('<!doctype html><html><head><title>Laboratory</title></head><body><p>' + marker +
                '</p>' + extra + '<script>"' + nonce + '";</script>' + fallback + '</body></html>').encode()
        self.send_response(503 if case == 'http-error' and after else 200)
        self.send_header('Content-Type', 'text/html; charset=UTF-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run(output):
    output = ts01.new_directory(output)
    fixture = tsep.read_json(ROOT/'tests/fixtures/prospective-ts01-cases.json')
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    server.daemon_threads = True
    server.measuring = False
    server.requests = []
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        origin = 'http://127.0.0.1:' + str(server.server_port)
        settings = {'urls': [origin+'/'+c['id'] for c in fixture['cases']], 'origins': [origin],
                    'agent': 'TSEP-synthetic-prospective/1', 'accept_encoding': 'identity',
                    'timeout': 2, 'max_bytes': 16384, 'max_redirects': 1, 'allow_loopback': True,
                    'network': 'Synthetic loopback HTTP server', 'access': 'synthetic',
                    'selection_method': 'Nine prefrozen synthetic workflow cases, no real-site inference'}
        ts01.reference(settings, output/'first')
        criteria = {url: {'policy': 'stable'} if url.endswith('/stable-policy') else
                    {'policy': 'markers', 'required_markers': ['Expected'], 'forbidden_markers': ['Forbidden']}
                    for url in settings['urls']}
        ts01.save(output/'criteria.json', criteria)
        ts01.seal(output/'first/reference', output/'intent.json', assessor='Synthetic laboratory author',
                  label='Synthetic prospective TS01 laboratory', criteria=criteria)
        prospective.prepare(output/'first/reference', output/'intent.json', output/'receipt.json')
        server.measuring = True  # Never alter the reference response before the receipt exists.
        ts01.evaluate(output/'first/reference', output/'intent.json', output/'assessment')
        result = prospective.compare(output/'first/reference', output/'assessment', output/'receipt.json')
        ts01.save(output/'comparison.json', result)
        ts01.save(output/'laboratory.json', {'synthetic': True, 'external_requests': 0,
                                          'requests': server.requests, 'fixture_sha256': tsep.digest(ROOT/'tests/fixtures/prospective-ts01-cases.json')})
        return result
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.output)
    print('Synthetic laboratory retained in ' + str(args.output))
