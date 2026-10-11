#!/usr/bin/env python3
"""TS43 controlled loopback experiment: actual HTTP/logs, fictional operator and reviews.

Apache-2.0. Eight bounded local requests; offline replay never makes a request.
"""
import argparse
import copy
from datetime import datetime, timedelta, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import ipaddress
import json
from pathlib import Path
import re
import socket
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
from conformance import agent_access
from conformance.evaluate import evaluate
from conformance.http import message
from provenance.runtime import loaded_sources, runtime_identity

VERSION = '1'
FIXTURE = 'tests/fixtures/agent-access-laboratory-v1.json'
FREEZE = 'tests/fixtures/agent-access-laboratory-v1.sha256'
RULES = ['TS43-A01', 'TS43-A02', 'TS43-A03']
UA = 'Mozilla/5.0 (compatible; ExampleSearch/1.0; +https://provider.example/bots)'
BODY = b'Expected public content'
ASSESSOR = 'Automated controlled laboratory; no human review'
SELECTION = 'Six prefrozen fictional scenarios, actual loopback exchanges; not a site sample'
SCOPE = ('Controlled synthetic site, fictional provider and supplied synthetic reviews. Actual '
         'loopback HTTP and native server logs. No Edikka observation, real provider identity, '
         'operator visit, security certification, indexing or citation established.')


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(raw):
    return hashlib.sha256(raw.encode('utf-8') if isinstance(raw, str) else raw).hexdigest()


def sources():
    result = captures.source_files()
    result.update(loaded_sources(ROOT, {'examples/agent_access_laboratory.py':sys.modules[__name__],
                                       'collectors/ts01.py':ts01, 'adapters/replay.py':bundle_replay}))
    for name in (FIXTURE, FREEZE, 'spec/protocol.json', 'schemas/report.schema.json'):
        result[name] = tsep.digest(ROOT/name)
    return result


def fixture():
    tsep.require(tsep.digest(ROOT/FIXTURE) == (ROOT/FREEZE).read_text().strip(), 'Frozen laboratory recipe mismatch')
    return tsep.read_json(ROOT/FIXTURE)


def plans(base, declared, start, end):
    result = {}
    for case in fixture()['cases']:
        expectation = {'action':case['test_action'], 'policy_basis':case['basis'],
                       'reason':'Predeclared fictional policy for this controlled test client',
                       'status':case['expected_status'], 'final_url':base+case.get('final_path',case['path'])}
        if 'expected_body' in case:
            expectation['expected_body_sha256'] = sha(case['expected_body'])
        result[case['id']] = {'declared_at':declared, 'agent_access':{
            'reader':'agent-access-v1', 'client':{'operator':'Fictional Example provider',
                'actor_kind':'crawler', 'product_token':'ExampleSearch', 'full_user_agent':UA, 'source_ids':['doc']},
            'operator_access':'allow', 'test_access':expectation, 'origins':[base+'/'],
            'log_layer':'application', 'id_header':'x-request-id', 'window_start':start,
            'window_end':end, 'clock_skew_ms':0, 'max_duration_ms':3000, 'max_source_age_days':0}}
    return result


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, *args):
        pass

    def do_GET(self):
        server = self.server
        if len(server.records) >= 8:
            server.scope_error = 'More than eight requests'; self.close_connection = True; return
        # This is deliberately a fictional allowlist, never provider authentication.
        trusted = ipaddress.ip_address(self.client_address[0]) in ipaddress.ip_network('192.0.2.0/24')
        agent = self.headers.get('User-Agent', '')
        status, body = 200, BODY
        if self.path == '/identity-gated':
            if not trusted or agent != UA:
                status, body = 403, b'Unrecognized test client'
        elif self.path in ('/ua-only', '/gate-removed'):
            if agent != UA:
                status, body = 403, b'Unexpected test client'
        elif self.path == '/redirect':
            status, body = 302, b'Redirect to controlled content'
        elif self.path != '/cached':
            server.scope_error = 'Unexpected request path'; status, body = 404, b'Outside scope'
        request_id = 'local-request-'+str(len(server.records)+1)
        server.records.append({'request_id':request_id, 'request_at':now(), 'method':'GET',
            'url':server.base+self.path, 'user_agent':agent, 'status':status, 'layer':'application',
            'peer_ip':self.client_address[0], 'forwarded_for':self.headers.get('X-Forwarded-For'),
            'fictional_allowlist_match':trusted})
        response_id = request_id
        if self.path == '/cached':
            if server.cached_id is None:
                server.cached_id = request_id
            response_id = server.cached_id
        self.send_response_only(status)
        self.send_header('Content-Type','text/plain; charset=utf-8')
        self.send_header('Content-Length',str(len(body)))
        self.send_header('Connection','close')
        self.send_header('X-Request-ID',response_id)
        if self.path == '/redirect': self.send_header('Location','/ua-only')
        self.end_headers(); self.wfile.write(body)


def fetch(base, path, user_agent, forwarded=None):
    parts = urlsplit(base)
    tsep.require(parts.scheme == 'http' and parts.hostname == '127.0.0.1'
                 and parts.port and parts.path == '' and not parts.query and not parts.fragment,
                 'Only the controlled numeric loopback origin is permitted')
    tsep.require(path in ('/ua-only','/identity-gated','/gate-removed','/cached','/redirect'), 'Unplanned path')
    request = 'GET '+path+' HTTP/1.1\r\nHost: '+parts.netloc+'\r\nUser-Agent: '+user_agent+'\r\nConnection: close\r\n'
    if forwarded is not None:
        tsep.require(forwarded == '192.0.2.5', 'Unplanned forwarded value')
        request += 'X-Forwarded-For: '+forwarded+'\r\n'
    request += '\r\n'
    sent = now(); chunks = []; size = 0
    # Numeric AF_INET socket: no DNS, proxy, redirects or external destination.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.settimeout(3); client.connect(('127.0.0.1',parts.port))
        peer = client.getpeername()[0]; client.sendall(request.encode('ascii'))
        while True:
            raw = client.recv(4096)
            if not raw: break
            size += len(raw); tsep.require(size <= 16384, 'Response exceeds laboratory byte bound')
            chunks.append(raw)
    return {'url':base+path, 'complete':True, 'sent_at':sent, 'received_at':now(),
            'peer_address':peer, 'request':request, 'response':b''.join(chunks).decode('ascii')}


def synthetic_review(stamp):
    return {'reviewer':'Fictional laboratory reviewer', 'provenance':'synthetic-exercise',
            'assistance':'Authored synthetic assumption; no real human review', 'observed_at':stamp,
            'reason':'Controlled test fixture, neither independent review nor source authentication'}


def input_for(case, registration, capture, raw_logs, exported, reviewed, assessed):
    intent = copy.deepcopy(registration['plans'][case['id']]); plan = intent['agent_access']
    source_text = 'Fictional operator documentation authored for this laboratory only. Full HTTP client: '+UA
    docs = [{'id':'doc', 'source_url':'https://provider.example/bots',
             'observed_at':registration['declared_at'], 'raw_text':source_text, 'sha256':sha(source_text)}]
    t = {'url':registration['base']+case['path'], 'observed_at':assessed, 'intent':intent,
         'context':{'tool':'TSEP controlled agent-access laboratory', 'tool_version':VERSION,
                    'network':'127.0.0.1 only; numeric IPv4 socket without DNS',
                    'bounds':'8 total requests; 3 seconds and 16384 response bytes per request',
                    'scope':SCOPE}, 'http':copy.deepcopy(capture['http']), 'client_documents':docs,
         'execution':{'origin':'assessor-test', 'initiator':'Automated controlled laboratory',
             'command':registration['invocation'], 'invocation_kind':'python-function-call',
             'started_at':capture['started_at'], 'ended_at':capture['ended_at']},
         'logs':{'reader':'tsep-request-log-v1', 'format':'native-jsonl', 'raw_jsonl':raw_logs,
             'sha256':sha(raw_logs), 'observed_at':exported, 'window_start':plan['window_start'],
             'window_end':plan['window_end'], 'origins':plan['origins'], 'layer':'application', 'complete':True}}
    t['client_review'] = dict(synthetic_review(reviewed), full_user_agent='supported',
                            binding_sha256=agent_access.client_binding(plan['client'], docs))
    t['log_review'] = dict(synthetic_review(reviewed), server_generated_id=True, per_request_id=True,
        client_facing=True, clock_bound_confirmed=True, complete=True,
        binding_sha256=agent_access.correlation_binding(t))
    if case['id'] == 'cached-id':
        t['log_review']['reason'] = ('Deliberately overconfident SYNTHETIC per-response-ID assertion: '
            'the controlled cache reuses an old ID. The temporal guard must reject its attribution. '
            'This is an erroneous fixture judgment, never an actual approved review.')
    t['attribution'] = dict(synthetic_review(reviewed), request_origin='assessor-test',
        operator_identity='not-verified', claims_operator_visit=False,
        binding_sha256=agent_access.attribution_binding(t))
    return {'input_version':'1', 'rules':list(RULES), 'targets':[t]}


def row(case, folder):
    atoms = tsep.read_json(folder/'bundle/assessment.json')
    report = tsep.read_json(folder/'bundle/report.json')
    actual = {'atomic_outcomes':[a['outcome'] for a in atoms], 'control_status':report['results'][0]['status']}
    expected = {k:case[k] for k in ('atomic_outcomes','control_status')}
    return {'id':case['id'], 'actual':actual, 'expected':expected, 'matches_expectations':actual == expected,
            'report':case['id']+'/bundle/report.json', 'input':case['id']+'/input.json'}


def summary(registration, rows):
    return {'kind':'controlled-agent-access-laboratory', 'version':VERSION, 'scope':SCOPE,
            'registered_at':registration['declared_at'], 'source_files':registration['source_files'],
            'runtime':registration['runtime'], 'protocol_version':tsep.read_json(ROOT/'spec/protocol.json')['version'],
            'requests':8, 'cases':rows, 'all_expectations_matched':all(r['matches_expectations'] for r in rows),
            'human_review_performed':False, 'actual_operator_visits_established':False}


def check_capture(registration, evidence, records):
    recipe = fixture(); base = registration['base']; phases = evidence['phases']
    tsep.require(len(phases) == 6 and len(records) == recipe['max_requests'] == 8, 'Laboratory request count mismatch')
    captures_in_order = [evidence['primer']]
    expected = [(recipe['primer']['path'], recipe['primer']['user_agent'], None)]
    prior = tsep.timestamp(evidence['primer']['received_at'])
    tsep.require(prior <= tsep.timestamp(registration['declared_at']), 'Primer must precede plans')
    for case, phase in zip(recipe['cases'], phases):
        tsep.require(phase['id'] == case['id'], 'Phase order mismatch')
        begin, end = tsep.timestamp(phase['started_at']), tsep.timestamp(phase['ended_at'])
        plan = registration['plans'][case['id']]['agent_access']
        tsep.require(prior <= begin <= end <= tsep.timestamp(plan['window_end']) and
                     tsep.timestamp(plan['window_start']) <= begin, 'Capture chronology mismatch')
        paths = [case['path']] + (['/ua-only'] if case['id'] == 'redirect' else [])
        tsep.require(len(phase['http']) == len(paths), 'Unplanned HTTP hop count')
        for path, hop in zip(paths,phase['http']):
            tsep.require(begin <= tsep.timestamp(hop['sent_at']) <= tsep.timestamp(hop['received_at']) <= end,
                         'HTTP interval outside execution receipt')
            begin = tsep.timestamp(hop['received_at'])
            captures_in_order.append(hop); expected.append((path,UA,case.get('forwarded_for')))
        prior = end
    for hop, record, (path,agent,forwarded) in zip(captures_in_order, records, expected):
        _, headers, _ = message(hop['request'])
        tsep.require(hop['url'] == base+path and hop['peer_address'] == '127.0.0.1'
            and headers.get('user-agent') == [agent]
            and headers.get('x-forwarded-for') == ([forwarded] if forwarded else None), 'Captured request scope mismatch')
        tsep.require(record['url'] == hop['url'] and record['user_agent'] == agent and record['peer_ip'] == '127.0.0.1'
            and record['forwarded_for'] == forwarded and record['fictional_allowlist_match'] is False
            and tsep.timestamp(hop['sent_at']) <= tsep.timestamp(record['request_at']) <= tsep.timestamp(hop['received_at']),
            'Native request log scope/clock mismatch')


def run(output):
    before = sources(); recipe = fixture(); root = ts01.new_directory(output)
    server = HTTPServer(('127.0.0.1',0), Handler); server.records=[]; server.cached_id=None; server.scope_error=None
    server.base = 'http://127.0.0.1:'+str(server.server_port)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    evidence = {'phases':[]}
    try:
        evidence['primer'] = fetch(server.base, '/cached', 'OtherClient/1')
        declared = now(); start = now(); end = (datetime.now(timezone.utc)+timedelta(seconds=2)).isoformat()
        registration = {'kind':'agent-access-laboratory-registration', 'version':VERSION, 'synthetic':True,
            'base':server.base, 'declared_at':declared, 'window_start':start, 'window_end':end,
            'plans':plans(server.base,declared,start,end), 'recipe':recipe, 'source_files':before,
            'runtime':runtime_identity(), 'invocation':['examples.agent_access_laboratory.run', str(root.resolve())]}
        ts01.save(root/'registration.json',registration)
        for case in recipe['cases']:
            phase = {'id':case['id'], 'started_at':now(), 'http':[]}
            phase['http'].append(fetch(server.base,case['path'],UA,case.get('forwarded_for')))
            if case['id'] == 'redirect':
                phase['http'].append(fetch(server.base,'/ua-only',UA))
            phase['ended_at'] = now(); evidence['phases'].append(phase)
        remaining = (tsep.timestamp(end)-datetime.now(timezone.utc)).total_seconds()
        if remaining > 0: time.sleep(remaining)
    finally:
        server.shutdown(); server.server_close(); thread.join()
        ts01.save(root/'exchanges.json',evidence)
        raw_logs = ''.join(json.dumps(r, ensure_ascii=False, separators=(',',':'))+'\n' for r in server.records)
        (root/'requests.jsonl').write_text(raw_logs,encoding='utf-8')
    tsep.require(server.scope_error is None, server.scope_error or 'Laboratory scope mismatch')
    check_capture(registration,evidence,server.records)
    exported, reviewed, assessed = now(), now(), now()
    receipt = {'exported_at':exported, 'synthetic_review_at':reviewed, 'assessed_at':assessed}
    ts01.save(root/'receipt.json',receipt)
    rows=[]; names=['registration.json','exchanges.json','requests.jsonl','receipt.json','results.json']
    for case, phase in zip(recipe['cases'], evidence['phases']):
        folder=root/case['id']; folder.mkdir()
        data=input_for(case,registration,phase,raw_logs,exported,reviewed,assessed)
        ts01.save(folder/'input.json',data)
        captures.build(folder/'input.json',folder/'bundle',assessor=ASSESSOR,label='SYNTHETIC TS43 / '+case['id'],
                       selection_method=SELECTION,access='synthetic',mode='semiAuto')
        rows.append(row(case,folder)); names.extend([case['id']+'/input.json',case['id']+'/bundle/SHA256SUMS'])
    result=summary(registration,rows); ts01.save(root/'results.json',result)
    tsep.require(sources() == before, 'Laboratory sources changed during collection')
    ts01.manifest(root,names)
    return result


def replay(root):
    root=Path(root); before=sources(); inventory=ts01.verify(root)
    registration=tsep.read_json(root/'registration.json'); recipe=fixture()
    tsep.require(registration.get('kind') == 'agent-access-laboratory-registration'
        and registration.get('version') == VERSION and registration.get('synthetic') is True
        and registration.get('source_files') == before and registration.get('recipe') == recipe,
        'Laboratory source/plan mismatch')
    tsep.require(re.fullmatch(r'http://127\.0\.0\.1:[1-9][0-9]{0,4}',registration['base'])
        and 0 < urlsplit(registration['base']).port <= 65535, 'Invalid loopback origin')
    tsep.require(registration['plans'] == plans(registration['base'],registration['declared_at'],
        registration['window_start'],registration['window_end']), 'Registered test plans differ')
    expected={'registration.json','exchanges.json','requests.jsonl','receipt.json','results.json'}
    expected.update(c['id']+'/'+n for c in recipe['cases'] for n in ('input.json','bundle/SHA256SUMS'))
    tsep.require(set(inventory) == expected, 'Incomplete laboratory manifest')
    evidence=tsep.read_json(root/'exchanges.json'); raw_logs=(root/'requests.jsonl').read_text(encoding='utf-8')
    records=[tsep.parse_json(line.encode()) for line in raw_logs.splitlines()]
    check_capture(registration,evidence,records); receipt=tsep.read_json(root/'receipt.json'); rows=[]
    for case,phase in zip(recipe['cases'],evidence['phases']):
        folder=root/case['id']
        data=input_for(case,registration,phase,raw_logs,receipt['exported_at'],receipt['synthetic_review_at'],receipt['assessed_at'])
        tsep.require(data == tsep.read_json(folder/'input.json') == tsep.read_json(folder/'bundle/input.json'),
                     'Capture/input binding mismatch')
        report=tsep.read_json(folder/'bundle/report.json')
        tsep.require(report['assessor'] == {'name':ASSESSOR,'mode':'semiAuto',
            'tool':{'name':captures.NAME,'version':captures.VERSION}}
            and report['scope'] == {'label':'SYNTHETIC TS43 / '+case['id'], 'targets':[data['targets'][0]['url']],
                'selection_method':SELECTION,'exclusions':[]}
            and all(a['access'] == 'synthetic' for a in report['artifacts']), 'Synthetic report identity mismatch')
        with tempfile.TemporaryDirectory() as tmp:
            bundle_replay.replay(folder/'bundle',Path(tmp)/'replay')
        tsep.require(evaluate(data) == tsep.read_json(folder/'bundle/assessment.json'), 'Replayed assessments differ')
        rows.append(row(case,folder))
    tsep.require(summary(registration,rows) == tsep.read_json(root/'results.json'), 'Replayed summary differs')
    tsep.require(before == sources(), 'Laboratory sources changed during replay')
    return {'kind':'agent-access-laboratory-offline-replay', 'version':VERSION, 'cases':6, 'network_requests':0,
            'same_observations_and_results':True,'all_expectations_matched':all(r['matches_expectations'] for r in rows),
            'scope':SCOPE, 'source_files':before, 'runtime':runtime_identity()}


def main():
    parser=argparse.ArgumentParser(description=__doc__); sub=parser.add_subparsers(dest='command',required=True)
    run_parser=sub.add_parser('run'); run_parser.add_argument('--output',type=Path,required=True)
    replay_parser=sub.add_parser('replay'); replay_parser.add_argument('laboratory',type=Path)
    replay_parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:
        if args.command == 'run': result=run(args.output)
        else:
            tsep.require(not args.output.exists() and not args.output.is_symlink(),'Choose a NEW replay output')
            result=replay(args.laboratory); ts01.save(args.output,result)
        print(json.dumps({k:v for k,v in result.items() if k not in ('source_files','runtime')},ensure_ascii=False))
        return 0 if result['all_expectations_matched'] else 2
    except (tsep.Invalid, OSError, ValueError, KeyError, TypeError) as error:
        print(str(error),file=sys.stderr); return 1


if __name__ == '__main__': raise SystemExit(main())
