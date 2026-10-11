#!/usr/bin/env python3
"""Four TS44 scenarios with actual loopback HTTP and explicitly authored DOM/reviews.

Apache-2.0. Six bounded anonymous requests; offline replay never recollects.
"""
import argparse
import copy
from datetime import datetime, timedelta, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import re
import socket
import socketserver
import sys
import tempfile
import threading
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from adapters import captures, replay as bundle_replay
from collectors import ts01
from conformance import critical_content as content
from conformance.http import message
from provenance.runtime import loaded_sources, runtime_identity

VERSION = '1'
FIXTURE = 'tests/fixtures/critical-content-laboratory-v1.json'
FREEZE = 'tests/fixtures/critical-content-laboratory-v1.sha256'
RULES = ['TS44-A01', 'TS44-A02', 'TS44-A03']
UA = 'TSEPContentTest/1.0'
ASSESSOR = 'Automated controlled laboratory; no human review'
SELECTION = 'Four prefrozen fictional scenarios; actual loopback HTTP, authored DOM and reviews'
SCOPE = ('Actual HTTP exchanges with a controlled fictional site. DOM rédigé, non observé '
         'dans un navigateur. Fictional reviews and content; 1.8 s is not a performance '
         'measurement. No Edikka audit, actual agent visit, identity, ingestion or citation.')


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(value):
    return hashlib.sha256(value.encode('utf-8') if isinstance(value, str) else value).hexdigest()


def fixture():
    tsep.require(tsep.digest(ROOT/FIXTURE) == (ROOT/FREEZE).read_text().strip(),
                 'Frozen laboratory recipe mismatch')
    return tsep.read_json(ROOT/FIXTURE)


def sources():
    result = captures.source_files()
    result.update(loaded_sources(ROOT, {'examples/critical_content_laboratory.py':sys.modules[__name__],
        'collectors/ts01.py':ts01, 'adapters/replay.py':bundle_replay}))
    for name in (FIXTURE, FREEZE, 'spec/protocol.json', 'schemas/report.schema.json'):
        result[name] = tsep.digest(ROOT/name)
    return result


def loopback(base):
    tsep.require(isinstance(base, str) and re.fullmatch(r'http://127\.0\.0\.1:[1-9][0-9]{0,4}', base)
                 and 0 < urlsplit(base).port <= 65535, 'Only a numeric loopback origin is permitted')
    return urlsplit(base)


def template(case, base):
    loopback(base)
    replacements = [('https://example.test/article.json', base+'/'+case['id']+'.json'),
                    ('https://example.test/article', base+'/'+case['id'])]
    def visit(value):
        if isinstance(value, str):
            for old, new in replacements: value = value.replace(old, new)
            return value
        if isinstance(value, list): return [visit(v) for v in value]
        if isinstance(value, dict): return {k:visit(v) for k,v in value.items()}
        return value
    return visit(case['authored_template_input']['targets'][0])


def plans(base, declared, reviewed, start, end):
    result = {}
    for case in fixture()['cases']:
        t = template(case, base)
        t['intent']['declared_at'] = declared
        t['intent']['critical_content'].update(window_start=start, window_end=end,
                                               max_duration_ms=3000, origins=[base+'/'])
        prior = {'url':t['url'], 'intent':t['intent'],
                 'critical_plan_review':copy.deepcopy(t['critical_plan_review'])}
        prior['critical_plan_review'].update(observed_at=reviewed, binding_sha256=content.plan_binding(prior))
        result[case['id']] = prior
    return result


def responses(base):
    result = {}
    for case in fixture()['cases']:
        t = template(case, base)
        hops = t['http'] + [hop for doc in t.get('documents', []) for hop in doc['http']]
        for hop in hops:
            first, headers, body = message(hop['response'])
            path = urlsplit(hop['url']).path
            tsep.require(path in case['paths'] and first.startswith('HTTP/1.1 200 '), 'Unexpected response template')
            result[path] = {'body':body, 'media_type':headers['content-type'][0], 'body_sha256':sha(body)}
    return result


class Server(HTTPServer):
    def server_bind(self):
        # HTTPServer otherwise calls getfqdn while binding. This experiment needs no DNS.
        socketserver.TCPServer.server_bind(self)
        self.server_name, self.server_port = self.server_address


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def setup(self):
        super().setup()
        self.connection.settimeout(3)

    def log_message(self, *args):
        pass

    def do_GET(self):
        server = self.server
        if (len(server.records) >= 6 or self.path not in server.responses
                or self.headers.get('User-Agent') != UA
                or self.headers.get('Authorization') or self.headers.get('Cookie')):
            server.scope_error = 'Unexpected or excessive laboratory request'
            self.close_connection = True
            return
        value = server.responses[self.path]
        raw = value['body'].encode('utf-8')
        request_id = 'critical-request-'+str(len(server.records)+1)
        server.records.append({'request_id':request_id, 'request_at':now(), 'method':'GET',
            'url':server.base+self.path, 'user_agent':self.headers.get('User-Agent'),
            'peer_ip':self.client_address[0], 'status':200, 'body_sha256':sha(raw)})
        self.send_response_only(200)
        self.send_header('Content-Type', value['media_type'])
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('X-Lab-Request-ID', request_id)
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(raw)


def fetch(base, path):
    parts = loopback(base)
    tsep.require(path in responses(base), 'Unplanned laboratory path')
    request = ('GET '+path+' HTTP/1.1\r\nHost: '+parts.netloc+'\r\nUser-Agent: '+UA+
               '\r\nConnection: close\r\n\r\n')
    sent = now(); deadline = time.monotonic()+3; chunks = []; size = 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.settimeout(3); client.connect(('127.0.0.1', parts.port))
        peer = client.getpeername()[0]
        client.settimeout(max(0.001, deadline-time.monotonic())); client.sendall(request.encode('ascii'))
        while True:
            remaining = deadline-time.monotonic()
            tsep.require(remaining > 0, 'Laboratory response duration bound exceeded')
            client.settimeout(remaining)
            raw = client.recv(4096)
            if not raw: break
            size += len(raw); tsep.require(size <= 16384, 'Laboratory response byte bound exceeded')
            chunks.append(raw)
    return {'url':base+path, 'complete':True, 'sent_at':sent, 'received_at':now(),
            'peer_address':peer, 'request':request, 'response':b''.join(chunks).decode('utf-8')}


def authored_state(case, base, http, created):
    state = template(case, base)['render']['states'][0]
    state['observed_at'] = created
    envelope = state['structured_dom']
    envelope['snapshot_sha256'] = content.digest(envelope['snapshot'])
    envelope['acquisition']['http_sha256'] = content.digest(http)
    envelope['acquisition']['navigation_id'] = 'authored-laboratory-'+case['id']
    support = ('DOM rédigé, non observé dans un navigateur. Authored from the frozen recipe '
               'after actual controlled HTTP; no JavaScript was executed or browser observed.')
    envelope['acquisition']['support'] = [{'name':'attribution', 'content':support, 'sha256':sha(support)}]
    return state


def input_for(case, registration, phase, receipt):
    t = copy.deepcopy(registration['plans'][case['id']])
    t.update(observed_at=receipt['assessed_at'], http=copy.deepcopy(phase['http'][:1]),
        context={'network':'Numeric 127.0.0.1 only; no DNS/proxy/external requests',
            'bounds':'Six total GETs; each <=3 seconds and <=16384 response bytes',
            'tool':'TSEP controlled critical-content laboratory', 'tool_version':VERSION, 'scope':SCOPE},
        render={'states':[copy.deepcopy(phase['authored_state'])]})
    if len(phase['http']) == 2:
        t['documents'] = [{'id':'resource', 'url':phase['http'][1]['url'], 'http':[copy.deepcopy(phase['http'][1])]}]
    t['critical_reviews'] = template(case, registration['base'])['critical_reviews']
    for review in t['critical_reviews']:
        review.update(observed_at=receipt['synthetic_review_at'],
                      binding_sha256=content.content_binding(t, review['representation_id']))
    return {'input_version':'1', 'rules':list(RULES), 'targets':[t]}


def check_capture(registration, evidence, records, receipt):
    recipe = fixture(); base = registration['base']; loopback(base)
    expected_plans = plans(base, registration['declared_at'], registration['synthetic_plan_review_at'],
                           registration['window_start'], registration['window_end'])
    tsep.require(registration['plans'] == expected_plans and registration['responses'] == responses(base),
                 'Registered plans or response bodies differ')
    prior, reviewed, start, end = [tsep.timestamp(registration[k]) for k in
        ('declared_at', 'synthetic_plan_review_at', 'window_start', 'window_end')]
    tsep.require(prior <= reviewed <= start < end and end-start == timedelta(seconds=2),
                 'Invalid laboratory registration chronology')
    phases = evidence['phases']
    tsep.require(len(phases) == 4 and len(records) == recipe['max_requests'] == 6,
                 'Laboratory request count mismatch')
    index = 0
    for case, phase in zip(recipe['cases'], phases):
        begin, finish = tsep.timestamp(phase['started_at']), tsep.timestamp(phase['ended_at'])
        tsep.require(phase['id'] == case['id'] and len(phase['http']) == case['requests']
            and prior <= begin <= finish <= end and start <= begin, 'Laboratory phase scope/chronology mismatch')
        last = begin
        for path, hop in zip(case['paths'], phase['http']):
            sent, received = tsep.timestamp(hop['sent_at']), tsep.timestamp(hop['received_at'])
            record = records[index]; index += 1
            first, headers, body = message(hop['response']); request, reqheaders, reqbody = message(hop['request'])
            wanted = registration['responses'][path]
            tsep.require(last <= sent <= received <= finish and (received-sent).total_seconds() <= 3,
                         'Exchange outside bounded execution interval')
            tsep.require(hop['url'] == base+path and hop['peer_address'] == '127.0.0.1'
                and hop['complete'] is True and request == 'GET '+path+' HTTP/1.1'
                and reqheaders == {'host':[urlsplit(base).netloc], 'user-agent':[UA], 'connection':['close']}
                and reqbody == '', 'Observed request scope mismatch')
            tsep.require(first == 'HTTP/1.1 200 OK' and body == wanted['body']
                and len(hop['response'].encode('utf-8')) <= 16384
                and headers == {'content-type':[wanted['media_type']],
                    'content-length':[str(len(body.encode('utf-8')))], 'connection':['close'],
                    'x-lab-request-id':['critical-request-'+str(index)]}, 'Observed response differs from recipe')
            tsep.require(record == {'request_id':'critical-request-'+str(index),
                'request_at':record['request_at'], 'method':'GET', 'url':base+path,
                'user_agent':UA, 'peer_ip':'127.0.0.1', 'status':200, 'body_sha256':sha(body)}
                and sent <= tsep.timestamp(record['request_at']) <= received, 'Native request log mismatch')
            last = received
        created = phase['authored_state']['observed_at']
        tsep.require(last <= tsep.timestamp(created) <= finish
            and phase['authored_state'] == authored_state(case, base, phase['http'][:1], created),
            'Authored DOM attribution or content differs')
        prior = finish
    exported, reviewed, assessed = [tsep.timestamp(receipt[k]) for k in
        ('exported_at', 'synthetic_review_at', 'assessed_at')]
    tsep.require(end <= exported <= reviewed <= assessed and receipt['collection_complete'] is True,
                 'Receipt chronology or collection completion mismatch')


def row(case, folder):
    atoms = tsep.read_json(folder/'bundle/assessment.json')
    report = tsep.read_json(folder/'bundle/report.json')
    actual = {'atomic_outcomes':[a['outcome'] for a in atoms], 'control_status':report['results'][0]['status']}
    expected = {'atomic_outcomes':case['expected_atomic_outcomes'], 'control_status':case['expected_control_status']}
    return {'id':case['id'], 'actual':actual, 'expected':expected,
            'matches_expectations':actual == expected,
            'report':case['id']+'/bundle/report.json', 'input':case['id']+'/input.json'}


def summary(registration, rows):
    return {'kind':'controlled-critical-content-laboratory', 'version':VERSION, 'scope':SCOPE,
        'registered_at':registration['declared_at'], 'source_files':registration['source_files'],
        'runtime':registration['runtime'], 'protocol_version':tsep.read_json(ROOT/'spec/protocol.json')['version'],
        'actual_http_requests':6, 'cases':rows,
        'all_expectations_matched':all(r['matches_expectations'] for r in rows),
        'human_review_performed':False, 'browser_observed':False, 'actual_agent_visit_established':False}


def run(output):
    before = sources(); recipe = fixture(); root = ts01.new_directory(output)
    evidence = {'phases':[]}; records = []; server = None; thread = None
    try:
        server = Server(('127.0.0.1', 0), Handler)
        server.base = 'http://127.0.0.1:'+str(server.server_port)
        server.records = records; server.scope_error = None; server.responses = responses(server.base)
        declared, reviewed, start = now(), now(), now()
        end = (tsep.timestamp(start)+timedelta(seconds=2)).isoformat()
        registration = {'kind':'critical-content-laboratory-registration', 'version':VERSION,
            'synthetic':True, 'base':server.base, 'declared_at':declared,
            'synthetic_plan_review_at':reviewed, 'window_start':start, 'window_end':end,
            'plans':plans(server.base, declared, reviewed, start, end), 'responses':server.responses,
            'recipe':recipe, 'source_files':before, 'runtime':runtime_identity()}
        ts01.save(root/'registration.json', registration)
        thread = threading.Thread(target=server.serve_forever, kwargs={'poll_interval':0.01}, daemon=True)
        thread.start()
        for case in recipe['cases']:
            phase = {'id':case['id'], 'started_at':now(), 'http':[]}
            evidence['phases'].append(phase)
            for path in case['paths']: phase['http'].append(fetch(server.base, path))
            phase['authored_state'] = authored_state(case, server.base, phase['http'][:1], now())
            phase['ended_at'] = now()
        tsep.require(server.scope_error is None, server.scope_error or 'Laboratory scope mismatch')
        remaining = (tsep.timestamp(end)-datetime.now(timezone.utc)).total_seconds()
        if remaining > 0: time.sleep(remaining)
    except Exception as error:
        ts01.save(root/'failure.json', {'at':now(), 'phase':'transport',
            'type':type(error).__name__, 'error':str(error), 'collection_complete':False})
        raise
    finally:
        if thread is not None: server.shutdown(); thread.join(timeout=4)
        if server is not None: server.server_close()
        ts01.save(root/'exchanges.json', evidence)
        (root/'requests.jsonl').write_text(''.join(json.dumps(r, separators=(',',':'))+'\n' for r in records), encoding='utf-8')
    receipt = {'exported_at':now(), 'synthetic_review_at':now(), 'assessed_at':now(), 'collection_complete':True}
    ts01.save(root/'receipt.json', receipt)
    try:
        check_capture(registration, evidence, records, receipt)
        rows = []; names = ['registration.json', 'exchanges.json', 'requests.jsonl', 'receipt.json', 'results.json']
        for case, phase in zip(recipe['cases'], evidence['phases']):
            folder = root/case['id']; folder.mkdir()
            ts01.save(folder/'input.json', input_for(case, registration, phase, receipt))
            captures.build(folder/'input.json', folder/'bundle', assessor=ASSESSOR,
                label='SYNTHETIC SITE / actual HTTP / TS44 '+case['id'],
                selection_method=SELECTION, access='synthetic', mode='semiAuto')
            rows.append(row(case, folder)); names.extend([case['id']+'/input.json', case['id']+'/bundle/SHA256SUMS'])
        result = summary(registration, rows); ts01.save(root/'results.json', result)
        tsep.require(before == sources(), 'Laboratory sources changed during execution')
        ts01.manifest(root, names)
        return result
    except Exception as error:
        ts01.save(root/'failure.json', {'at':now(), 'phase':'interpretation',
            'type':type(error).__name__, 'error':str(error), 'collection_complete':True})
        raise


def replay(root):
    root = Path(root); before = sources(); inventory = ts01.verify(root)
    registration = tsep.read_json(root/'registration.json'); recipe = fixture()
    tsep.require(registration.get('kind') == 'critical-content-laboratory-registration'
        and registration.get('version') == VERSION and registration.get('synthetic') is True
        and registration.get('source_files') == before and registration.get('recipe') == recipe,
        'Laboratory source/recipe mismatch')
    expected = {'registration.json', 'exchanges.json', 'requests.jsonl', 'receipt.json', 'results.json'}
    expected.update(c['id']+'/'+n for c in recipe['cases'] for n in ('input.json', 'bundle/SHA256SUMS'))
    tsep.require(set(inventory) == expected, 'Incomplete laboratory manifest')
    evidence = tsep.read_json(root/'exchanges.json'); receipt = tsep.read_json(root/'receipt.json')
    records = [tsep.parse_json(line.encode('utf-8')) for line in (root/'requests.jsonl').read_text().splitlines()]
    check_capture(registration, evidence, records, receipt); rows = []
    for case, phase in zip(recipe['cases'], evidence['phases']):
        folder = root/case['id']; data = input_for(case, registration, phase, receipt)
        tsep.require(data == tsep.read_json(folder/'input.json') == tsep.read_json(folder/'bundle/input.json'),
                     'Capture/input binding mismatch')
        report = tsep.read_json(folder/'bundle/report.json')
        tsep.require(report['assessor'] == {'name':ASSESSOR, 'mode':'semiAuto',
            'tool':{'name':captures.NAME, 'version':captures.VERSION}}
            and report['scope'] == {'label':'SYNTHETIC SITE / actual HTTP / TS44 '+case['id'],
                'targets':[data['targets'][0]['url']], 'selection_method':SELECTION, 'exclusions':[]}
            and all(a['access'] == 'synthetic' for a in report['artifacts']), 'Synthetic report identity mismatch')
        with tempfile.TemporaryDirectory() as tmp:
            bundle_replay.replay(folder/'bundle', Path(tmp)/'replay')
        rows.append(row(case, folder))
    tsep.require(summary(registration, rows) == tsep.read_json(root/'results.json'), 'Replayed summary differs')
    tsep.require(before == sources(), 'Laboratory sources changed during replay')
    return {'kind':'critical-content-laboratory-offline-replay', 'version':VERSION,
        'cases':4, 'network_requests':0, 'same_observations_and_results':True,
        'all_expectations_matched':all(r['matches_expectations'] for r in rows),
        'scope':SCOPE, 'source_files':before, 'runtime':runtime_identity()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    create = sub.add_parser('run'); create.add_argument('--output', type=Path, required=True)
    review = sub.add_parser('replay'); review.add_argument('laboratory', type=Path)
    review.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'run': result = run(args.output)
        else:
            tsep.require(not args.output.exists() and not args.output.is_symlink(), 'Choose a NEW replay output')
            result = replay(args.laboratory); ts01.save(args.output, result)
        print(json.dumps({k:v for k,v in result.items() if k not in ('source_files','runtime')}, ensure_ascii=False))
        return 0 if result['all_expectations_matched'] else 2
    except (tsep.Invalid, OSError, ValueError, KeyError, TypeError) as error:
        print(str(error), file=sys.stderr); return 1


if __name__ == '__main__': raise SystemExit(main())
