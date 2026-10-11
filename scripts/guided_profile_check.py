#!/usr/bin/env python3
"""Exercise the guided TS01 CLI with frozen authored pages and actual loopback HTTP."""
import argparse
from datetime import datetime, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]


def save(path, value):
    with path.open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2); handle.write('\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, *args):
        pass

    def do_GET(self):
        raw = self.server.body.encode('utf-8')
        self.server.requests.append({'path': self.path, 'observed_at': datetime.now(timezone.utc).isoformat(),
                                     'body_sha256': hashlib.sha256(raw).hexdigest()})
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers(); self.wfile.write(raw); self.close_connection = True


def run(tool_root, output, node):
    fixture = tool_root/'tests/fixtures/guided-profile-v2.json'
    if sha(fixture) != fixture.with_suffix('.sha256').read_text().split()[0]:
        raise ValueError('Frozen fixture fingerprint differs')
    recipe = json.loads(fixture.read_text())
    if output.exists() or output.is_symlink() or not output.parent.is_dir():
        raise ValueError('Use a new output directory with an existing parent')
    output.mkdir()
    (output/'frozen-fixture.json').write_bytes(fixture.read_bytes())
    (output/'runner.py').write_bytes(Path(__file__).read_bytes())
    environment = dict(os.environ, TSEP_SOURCE_NODE=str(node))
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    server.daemon_threads = True; server.requests = []
    url = 'http://127.0.0.1:'+str(server.server_port)+'/'
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    save(output/'resolved-plan.json', {'recorded_at': datetime.now(timezone.utc).isoformat(),
        'fixture_sha256': sha(fixture), 'url': url, 'cases': [c['id'] for c in recipe['cases']],
        'expected_requests': 14, 'scope': 'Synthetic pages and choices; real loopback transport. No external collection.'})
    commands, results = [], []
    collector = str(tool_root/'collectors/ts01.py')

    def command(directory, name, arguments, expected_exit=0, offline=False):
        args = [sys.executable, collector]+arguments
        if offline:
            # Protect Python socket/DNS entry points in this subprocess. Node's
            # existing API guard is separate; this is not OS network isolation.
            script = ('import runpy,socket,sys,ssl\n'
                      'def refused(*a,**k): raise AssertionError("Qualification forbids Python network")\n'
                      'socket.socket=refused; socket.getaddrinfo=refused\n'
                      'sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name="__main__")\n')
            args = [sys.executable, '-c', script, collector]+arguments
        completed = subprocess.run(args, env=environment, capture_output=True, cwd=tool_root, timeout=120)
        (directory/(name+'.stdout')).write_bytes(completed.stdout)
        (directory/(name+'.stderr')).write_bytes(completed.stderr)
        row = {'case': directory.name, 'phase': name, 'exit': completed.returncode,
               'expected_exit': expected_exit, 'matches': completed.returncode == expected_exit,
               'arguments': arguments, 'python_network_guard': offline}
        commands.append(row)
        save(directory/(name+'-command.json'), row)
        if not row['matches']:
            raise ValueError('Unexpected CLI exit: '+directory.name+'/'+name+'; original stdout/stderr retained')
        return json.loads(completed.stdout) if completed.stdout else None

    try:
        for case in recipe['cases']:
            directory = output/case['id']; directory.mkdir()
            server.body = case['reference_body']
            command(directory, 'reference', ['reference', '--target', url, '--allow-loopback',
                '--network', 'Actual local loopback HTTP', '--selection-method', 'One authored fixture URL',
                '--access', 'synthetic', '--output', str(directory/'reference')])
            options = {'policy': 'markers', **{k: case[k] for k in
                ('identity_reader', 'required_markers', 'forbidden_markers') if k in case}}
            save(directory/'criteria.json', {url: options})
            rejected = case['expected_reference_preflight'] == 'contradiction'
            before_seal = len(server.requests)
            sealed = command(directory, 'seal', ['seal', '--reference', str(directory/'reference/reference'),
                '--criteria', str(directory/'criteria.json'), '--assessor', 'Authored synthetic laboratory',
                '--label', case['id'], '--output', str(directory/'intent.json')], 64 if rejected else 0, offline=True)
            if len(server.requests) != before_seal:
                raise ValueError('Seal unexpectedly requested the loopback server')
            if rejected:
                if (directory/'intent.json').exists(): raise ValueError('Contradictory reference was sealed')
                results.append({'id': case['id'], 'seal': 'refused', 'evaluation_requests': 0, 'matches': True})
                continue
            if sealed['reference_preflight'][0]['state'] != case['expected_reference_preflight']:
                raise ValueError('Unexpected reference preflight state')
            server.body = case['evaluation_body']
            evaluated = command(directory, 'evaluate', ['evaluate', '--reference', str(directory/'reference/reference'),
                '--intent', str(directory/'intent.json'), '--output', str(directory/'evaluation')])
            if evaluated['counts'][case['expected_control_status']] != 1:
                raise ValueError('Unexpected control result: '+case['id'])
            before_replay = len(server.requests)
            replayed = command(directory, 'replay', ['replay', str(directory/'evaluation'),
                '--output', str(directory/'replay')], offline=True)
            if not replayed['replayed'] or len(server.requests) != before_replay:
                raise ValueError('Replay differed or requested the loopback server')
            results.append({'id': case['id'], 'seal': 'accepted', 'expected': case['expected_control_status'],
                            'actual': case['expected_control_status'], 'matches': True, 'exact_replay': True})
    finally:
        server.shutdown(); server.server_close(); thread.join()
        save(output/'server-requests.json', server.requests)
        save(output/'commands.json', commands)
        save(output/'observed-results.json', results)
    summary = {'kind': 'guided-ts01-parsed-profile-laboratory', 'fixture_sha256': sha(fixture),
               'runner_sha256': sha(Path(__file__)), 'cases': len(results), 'matched': sum(r['matches'] for r in results),
               'requests': len(server.requests), 'exact_replays': sum(r.get('exact_replay', False) for r in results),
               'seal_refusals': sum(r['seal'] == 'refused' for r in results),
               'scope': 'Authored pages and intent; actual loopback HTTP and CLI exits. No real-site conformity, browser or human approval.',
               'results': results}
    if len(results) != 8 or len(server.requests) != 14: raise ValueError('Unexpected laboratory population')
    save(output/'summary.json', summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tool-root', type=Path, default=ROOT)
    parser.add_argument('--node', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.tool_root.resolve(), args.output.resolve(), args.node.resolve()), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
