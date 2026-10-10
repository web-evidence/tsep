#!/usr/bin/env python3
"""Serve a frozen synthetic TS07 browser laboratory on loopback. Apache-2.0.

This command captures source HTTP and prepares receipts, then waits for a browser
operator. It does NOT collect or manufacture DOM states. Ctrl-C ends the listener.
"""
import argparse
import copy
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from adapters import rendered
from collectors import ts01
from conformance.http import encoded
from diagnostics import campaign
from provenance.runtime import loaded_sources

VERSION = '1'
FIXTURE = 'tests/fixtures/render-import-cases.json'
FREEZE = 'tests/fixtures/render-import-freeze.sha256'


def fixture():
    tsep.require(tsep.digest(ROOT/FIXTURE) == (ROOT/FREEZE).read_text().strip(), 'Frozen rendered cases mismatch')
    return tsep.read_json(ROOT/FIXTURE)


def page(case, context):
    initial = '<meta name="robots" content="noindex">' if case['id'] == 'removed-initial' else ''
    onload = "document.querySelector('meta[name=robots]').remove();" if initial else ''
    action = {'added-after-click': "let meta=document.createElement('meta');meta.name='robots';meta.content='noindex';document.head.appendChild(meta);",
              'script-error': "throw new Error('Intentional synthetic laboratory error');"}.get(case['id'], '')
    # Inline resources only. HTML tags stay within the active bounded TS07 parser.
    return '''<!doctype html><html lang="fr"><head><meta charset="utf-8">'''+initial+'''<title>Laboratoire TSEP — '''+html.escape(case['label'])+'''</title>
<style>body{font:18px system-ui;max-width:900px;margin:55px auto;padding:20px;background:#101c29;color:#e8f0f6}h1{font-size:40px}a{display:inline-block;padding:16px 25px;background:#b8ed76;color:#142119;border-radius:8px;text-decoration:none}p{line-height:1.6}#state,#directives{color:#b8ed76;font-weight:bold}.detail{font-size:13px;color:#afbdc9;overflow-wrap:anywhere}</style></head><body>
<p>LABORATOIRE SYNTHÉTIQUE · TSEP TS07</p><h1>'''+html.escape(case['label'])+'''</h1>
<p>Objectif déclaré : permettre l’indexation. Deux états prévus : chargement, puis clic.</p>
<p>État : <span id="state">waiting</span> · JavaScript : <span id="js">pending</span></p>
<p>Directives meta : <span id="directives">pending</span></p><p><a href="#exercise" id="exercise">Exécuter l’étape</a></p>
<p>Erreurs observées : <span id="errors">[]</span></p>
<p class="detail">Contexte : <span id="context">'''+html.escape(context)+'''</span></p>
<p class="detail">Navigateur (User-Agent déclaré) : <span id="agent">pending</span></p>
<p class="detail">Dernière action du laboratoire : <span id="event-time">pending</span></p>
<p>Cette expérience n’établit ni visite de Googlebot, ni indexation, ni conformité globale.</p>
<script>
const errors=[];
function showError(value){errors.push(String(value));document.getElementById('errors').textContent=JSON.stringify(errors);}
window.addEventListener('error',event=>showError(event.message));
window.addEventListener('unhandledrejection',event=>showError(event.reason));
function show(){document.getElementById('directives').textContent=Array.from(document.querySelectorAll('meta[name="robots"]')).map(m=>m.content).join(' | ')||'aucune';document.getElementById('event-time').textContent=new Date().toISOString();}
document.getElementById('agent').textContent=navigator.userAgent;
'''+onload+'''
document.getElementById('js').textContent='executed';document.getElementById('state').textContent='loaded';show();
document.getElementById('exercise').addEventListener('click',event=>{event.preventDefault();document.getElementById('state').textContent='acted';
'''+('show();'+action if case['id']=='script-error' else action+'show();')+'''
});
</script></body></html>'''


def wire(body, kind='text/html', status=200):
    body = body.encode('utf-8')
    headers = ('HTTP/1.1 '+str(status)+' Laboratory\r\nContent-Type: '+kind+'; charset=utf-8\r\nContent-Length: '+str(len(body))+
               '\r\nCache-Control: no-store\r\nContent-Security-Policy: default-src \'none\'; script-src \'unsafe-inline\'; style-src \'unsafe-inline\'\r\nConnection: close\r\n\r\n')
    return headers.encode('ascii')+body


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, *args):
        pass

    def do_GET(self):
        raw = self.server.responses.get(self.path, wire('Outside registered scope', 'text/plain', 404))
        record = {'url': self.server.base+self.path, 'observed_at': ts01.now(), 'complete': False,
                  'request_agent': self.headers.get('User-Agent'), 'response': encoded(raw),
                  'peer': self.client_address[0], 'scope': 'Exact server-written response; separate from collector request'}
        try:
            self.wfile.write(raw); self.wfile.flush(); record['complete'] = True
        finally:
            with self.server.log_lock, (self.server.folder/'requests.jsonl').open('a', encoding='utf-8') as handle:
                handle.write(json.dumps(record, ensure_ascii=False)+'\n')
        self.close_connection = True


def start(output):
    plan = fixture()
    folder = ts01.new_directory(output)
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    server.daemon_threads = True
    server.log_lock = threading.Lock()
    server.folder = folder; server.base = 'http://127.0.0.1:'+str(server.server_port)
    token = secrets.token_hex(8)
    contexts = {case['id']: 'synthetic-'+token+'-'+case['id'] for case in plan['cases']}
    paths = {case['id']: '/'+token+'/'+case['id'] for case in plan['cases']}
    server.responses = {paths[case['id']]: wire(page(case, contexts[case['id']])) for case in plan['cases']}
    server.responses['/robots.txt'] = wire('User-agent: *\nDisallow:\n', 'text/plain')
    registration = {'registered_at': ts01.now(), 'synthetic': True, 'plan': plan, 'contexts': contexts,
                    'urls': {key:server.base+path for key,path in paths.items()}, 'subresources': [],
                    'source_files': dict(rendered.sources(), **loaded_sources(ROOT, {'examples/rendered_ts07_lab.py': sys.modules[__name__]})),
                    'responses': {server.base+path:encoded(raw) for path,raw in server.responses.items()},
                    'note': 'No DOM collected by this command. Inline scripts/styles, uncompressed immutable bytes, no-store.'}
    ts01.save(folder/'registration.json', registration)
    (folder/'requests.jsonl').touch()
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    try:
        settings = {'urls': [server.base+'/robots.txt']+list(registration['urls'].values()), 'origins':[server.base],
                    'agent':'googlebot', 'accept_encoding':'identity', 'timeout':3, 'max_bytes':32768, 'max_redirects':0,
                    'allow_loopback':True, 'network':'Controlled 127.0.0.1 laboratory only', 'access':'synthetic',
                    'selection_method':'Five synthetic scenarios frozen before browser execution'}
        ts01.capture(settings, folder/'source-capture')
        phase, _ = campaign.phase(folder/'source-capture')
        robots = phase['targets'][0]
        for case, original in zip(plan['cases'], phase['targets'][1:]):
            target = copy.deepcopy(original)
            target['context'] = {'id': contexts[case['id']], 'network':settings['network'], 'tool':'TSEP laboratory source collector',
                                 'tool_version': ts01.VERSION, 'bounds': '3s / 32768 bytes / 0 redirects'}
            target['intent'] = {'declared_at':registration['registered_at'], 'crawler':'googlebot', 'public_canonical':True,
                                'indexing':'allow', 'following':'unspecified', 'access_basis':'test-client-only',
                                'rendering':{'mode':'required', 'required_states':copy.deepcopy(plan['states'])}}
            target['robots'] = {'observed_at':robots['observed_at'], 'http':robots['http']}
            casefolder = folder/case['id']; casefolder.mkdir()
            ts01.save(casefolder/'source.json', {'input_version':'2','rules':plan['rules'],'targets':[target]})
            rendered.prepare(casefolder/'source.json', casefolder/'receipt.json')
        ts01.manifest(folder, ['registration.json', 'source-capture/SHA256SUMS']+
                      [case['id']+'/'+name for case in plan['cases'] for name in ('source.json','receipt.json')])
        return server, thread, registration
    except BaseException:
        server.shutdown(); server.server_close(); thread.join(); raise


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', required=True)
    args = parser.parse_args()
    server, thread, registration = start(args.output)
    print(json.dumps({'ready':True, 'urls':registration['urls'], 'output':args.output}), flush=True)
    try:
        thread.join()
    except KeyboardInterrupt:
        server.shutdown(); server.server_close(); thread.join()


if __name__ == '__main__':
    main()
