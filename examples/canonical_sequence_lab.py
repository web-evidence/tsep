#!/usr/bin/env python3
"""SYNTHETIC three-state browser laboratory, without sequence verdict. Apache-2.0."""
import argparse
from collections import Counter
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import re
import secrets
import shutil
import sys
import threading
from urllib.parse import urlsplit
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from collectors import ts01
from conformance.http import raw_bytes
from examples import predeclared_canonical_lab as single
from experiments import canonical_sequence as sequence
from experiments import rendered_metadata as metadata
from provenance.runtime import loaded_sources

VERSION = '1'
RECIPE = 'tests/fixtures/canonical-state-sequences-v1.json'
PAGE_SCRIPT = 'examples/canonical_sequence_page.js'
AGENT = 'TSEP-sequence-source/1'
transport = single.transport
FIELDS = ('tree', 'script_sha256', 'context', 'url', 'state', 'errors', 'capture_started_at',
          'captured_at', 'sequence_index', 'action', 'previous_receipt')


def recipes():
    path = ROOT/RECIPE
    tsep.require(tsep.digest(path) == path.with_suffix('.sha256').read_text().split()[0], 'Sequence recipe changed')
    plan = tsep.read_json(path)
    tsep.require(plan['capture_script_sha256'] == metadata.script_digest() and plan['method'] == sequence.METHOD, 'Sequence method changed')
    return plan


def sources():
    result = dict(single.sources(), **sequence.sources())
    result.update(loaded_sources(ROOT, {'examples/canonical_sequence_lab.py': sys.modules[__name__]}))
    for name in (RECIPE, RECIPE.replace('.json', '.sha256'), PAGE_SCRIPT): result[name] = tsep.digest(ROOT/name)
    return result


def page(case, token, endpoint):
    script = (ROOT/PAGE_SCRIPT).read_text()
    for key, value in [('__STATES__', [{'id': s['id'], 'action': s['action']} for s in case['states']]),
                       ('__SCRIPT_SHA__', metadata.script_digest()), ('__CONTEXT__', token), ('__ENDPOINT__', endpoint)]:
        script = script.replace(key, json.dumps(value))
    script = script.replace('__ACTIONS__', '['+','.join('()=>{'+s+'}' for s in case['actions'])+']')
    script = script.replace('__CAPTURE_EXPRESSION__', (ROOT/metadata.SCRIPT).read_text().strip())
    return ('<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>TSEP séquence · '+case['id']+'</title>'+case['head']+
        '<style>body{font:18px/1.6 system-ui;background:#102032;color:#edf3f8;max-width:1050px;margin:40px auto}h1{font-size:34px}code{color:#b8ed76;overflow-wrap:anywhere}button{font:inherit;padding:12px 22px;background:#daf296;border:0;border-radius:8px}button:disabled{opacity:.6}</style></head><body>'+
        '<p>LABORATOIRE SYNTHÉTIQUE · TROIS ÉTATS PRÉDÉCLARÉS</p><h1>'+case['id']+'</h1>'+
        '<p>État : <code id="lab-state">pending</code></p><p>Contexte : <code id="lab-context">'+token+'</code></p>'+
        '<p>Agent : <code id="lab-agent">pending</code></p><p>Document : <code id="lab-url">pending</code></p>'+
        '<p>Erreurs signalées : <code id="lab-errors">[]</code></p><p>Reçu local : <code id="lab-receipt">pending</code></p>'+
        '<button id="advance" disabled>Attente du premier reçu</button><script>'+script+'</script></body></html>')


def scope(base, token):
    cases = [transport.substitute(c, base, '') for c in recipes()['cases']]
    pages = []; tasks = []; responses = {}
    for env in recipes()['environments']:
        for case in cases:
            page_id = env+'/'+case['id']; url = base+'/case/'+page_id
            raw = transport.wire(page(case, token, base+'/capture'), [base.rsplit('/', 1)[0]], True)
            ids = []
            for index, state in enumerate(case['states']):
                task_id = page_id+'/'+state['id']; ids.append(task_id)
                tasks.append({'id': task_id, 'page_id': page_id, 'state_id': state['id'], 'sequence_index': index,
                    'url': url, 'action': state['action'], 'intent': dict(case['intent'], state_label=state['action']+'; synchronous capture after mutation')})
            pages.append({'id': page_id, 'case': case['id'], 'environment': env, 'url': url, 'task_ids': ids,
                          'response_sha256': metadata.sha(raw)})
            responses[url] = raw
    return cases, pages, tasks, responses


def start(output):
    folder = ts01.new_directory(output); before = sources(); plan = recipes()
    server = ThreadingHTTPServer(('127.0.0.1', 0), transport.Handler)
    origin = 'http://127.0.0.1:'+str(server.server_port); token = secrets.token_hex(8); base = origin+'/'+token
    cases, pages, tasks, responses = scope(base, token)
    reg = {'kind': 'predeclared-canonical-laboratory', 'version': '1', 'method': sequence.METHOD, 'normative': False,
           'registered_at': ts01.now(), 'base': base, 'token': token, 'origin': origin, 'source_files': before,
           'recipe': plan, 'cases': cases, 'pages': pages, 'tasks': tasks, 'environments': plan['environments'],
           'capture_endpoint': base+'/capture', 'script_sha256': metadata.script_digest(), 'execution_context': 'not-attested'}
    ts01.save(folder/'registration.json', reg); (folder/'requests.jsonl').touch()
    server.folder = folder; server.origin = origin; server.lock = threading.Lock(); server.responses = responses
    server.daemon_threads = True; server.endpoint = reg['capture_endpoint']; server.token = token; server.task_urls = set(responses)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    try:
        ts01.capture({'urls': [p['url'] for p in pages], 'origins': [origin], 'agent': AGENT, 'accept_encoding': 'identity',
            'timeout': 3, 'max_bytes': 262144, 'max_redirects': 0, 'allow_loopback': True, 'network': 'controlled loopback synthetic',
            'selection_method': 'All predeclared sequence pages, one source per environment/case', 'access': 'synthetic'}, folder/'source-1')
        ts01.save(folder/'receipt.json', {'created_at': ts01.now(), 'registration_sha256': tsep.digest(folder/'registration.json'),
            'phases': {'source-1': tsep.digest(folder/'source-1/SHA256SUMS')}, 'source_files': before})
        tsep.require(sources() == before, 'Sources changed before browser collection')
        return [server], [thread], reg
    except BaseException:
        transport.stop([server], [thread]); raise


def response_bytes(receipt_id):
    body = json.dumps({'receipt': receipt_id}).encode()
    return ('HTTP/1.1 200 Capture\r\nContent-Type: application/json\r\nContent-Length: '+str(len(body))+
            '\r\nConnection: close\r\n\r\n').encode()+body


def chronological(*dates):
    parsed = [tsep.timestamp(d) for d in dates]
    tsep.require(all(a <= b for a, b in zip(parsed, parsed[1:])), 'Sequence chronology mismatch')


def marker(tree):
    ids = [n['id'] for n in tree['nodes'] if n['type'] == 1 and metadata.attrs(n).get('id') == 'lab-state']
    if len(ids) != 1: return None
    return ''.join(n['data'] for n in tree['nodes'] if n['parent'] == ids[0] and n['type'] == 3)


def analyze(source, observations):
    source = Path(source); reg = tsep.read_json(source/'registration.json'); receipt = tsep.read_json(source/'receipt.json')
    tsep.require(reg['kind'] == 'predeclared-canonical-laboratory' and reg['version'] == '1' and reg['method'] == sequence.METHOD, 'Unsupported sequence lab')
    tsep.require(reg['source_files'] == receipt['source_files'] == sources(), 'Changed sequence sources')
    tsep.require(receipt['registration_sha256'] == tsep.digest(source/'registration.json'), 'Registration changed')
    tsep.require(reg['recipe'] == recipes() and reg['environments'] == recipes()['environments'], 'Changed recipes/environments')
    url = urlsplit(reg['origin'])
    tsep.require(url.scheme == 'http' and url.hostname == '127.0.0.1' and url.port and reg['origin'] == 'http://127.0.0.1:'+str(url.port)
        and re.fullmatch('[0-9a-f]{16}', reg['token']) and reg['base'] == reg['origin']+'/'+reg['token']
        and reg['capture_endpoint'] == reg['base']+'/capture', 'Changed endpoint')
    cases, pages, tasks, responses = scope(reg['base'], reg['token'])
    tsep.require(reg['cases'] == cases and reg['pages'] == pages and reg['tasks'] == tasks and reg['script_sha256'] == metadata.script_digest(), 'Changed registered sequence scope')
    tsep.require(receipt['phases'] == {'source-1': tsep.digest(source/'source-1/SHA256SUMS')}, 'Changed source manifest')
    ts01.verify(source/'source-1'); phase = tsep.read_json(source/'source-1/capture.json'); ts01.same_collector(phase)
    urls = [p['url'] for p in pages]
    tsep.require(phase['settings']['urls'] == urls and [t['url'] for t in phase['targets']] == urls and phase['settings']['agent'] == AGENT
        and phase['sources_unchanged_during_collection'] is True, 'Changed source selection')
    chronological(reg['registered_at'], phase['started_at'], phase['finished_at'], receipt['created_at'])
    for n, target in enumerate(phase['targets'], 1):
        tsep.require(len(target['http']) == 1 and target['http'][0]['complete'] is True, 'Incomplete source')
        for kind in ('request', 'response'):
            tsep.require((source/'source-1'/('target-'+str(n)+'-hop-1-'+kind+'.bin')).read_bytes() == raw_bytes(target['http'][0][kind]), 'Source JSON/sidecar mismatch')
        tsep.require(raw_bytes(target['http'][0]['response']) == responses[target['url']], 'Preregistered source bytes differ')
    logs = [json.loads(x) for x in (source/'requests.jsonl').read_text().splitlines()]; used = set(); payloads = {}
    for i, row in enumerate(logs):
        tsep.require(row['peer'] == '127.0.0.1' and row['complete'] is True, 'Incomplete/non-local request')
        if row.get('method') == 'POST':
            tsep.require(row['url'] == reg['capture_endpoint'] and row['status'] == 200 and re.fullmatch('[0-9a-f]{64}', row['receipt']), 'Invalid page POST')
            raw = (source/'posts'/(row['receipt']+'.json')).read_bytes()
            tsep.require(metadata.sha(raw) == row['receipt'] and tsep.digest(source/'posts'/(row['receipt']+'.response.bin')) == row['response_sha256'], 'Changed POST bytes')
            tsep.require((source/'posts'/(row['receipt']+'.response.bin')).read_bytes() == response_bytes(row['receipt']), 'Wrong receiver response receipt')
            payloads[i] = transport.decode_page_export(raw)
        else:
            tsep.require(row['url'] in responses and row['response_sha256'] == metadata.sha(responses[row['url']]), 'Unexpected server response')
            if row['agent'] == AGENT:
                chronological(reg['registered_at'], row['observed_at'], receipt['created_at']); used.add(i)
    tsep.require(Counter(logs[i]['url'] for i in used) == Counter(urls), 'Source request scope')
    tsep.require(set(observations) == set(reg['environments']), 'Missing environment')
    results = {}; count = 0; all_checks = []; all_received = True
    for env in reg['environments']:
        observed = observations[env]
        if observed.get('status') == 'not-collected':
            tsep.require(set(observed) == {'status', 'reason'} and isinstance(observed['reason'], str) and observed['reason'].strip(), 'Unavailability needs reason')
            results[env] = observed; all_received = False; continue
        env_pages = [p for p in pages if p['environment'] == env]
        tsep.require(set(observed) == {'status', 'pages'} and observed['status'] == 'collected' and
                     set(observed['pages']) == {p['case'] for p in env_pages}, 'Missing/extra sequence page')
        page_results = []
        for page_record, case in zip(env_pages, cases):
            operator = observed['pages'][case['id']]; browser = operator['browser']; ua = browser['user_agent']
            tsep.require(ua and ua != AGENT and browser['name'] and browser['version'], 'Missing browser identity')
            chronological(receipt['created_at'], operator['navigation_started_at'], operator['observed_at'])
            gets = [i for i, r in enumerate(logs) if r.get('method') != 'POST' and r['url'] == page_record['url'] and r['agent'] == ua and i not in used]
            tsep.require(len(gets) == 1, 'Missing/ambiguous browser navigation'); get = gets[0]; used.add(get)
            chronological(operator['navigation_started_at'], logs[get]['observed_at'], operator['observed_at'])
            states = operator['states']; ids = [s['id'] for s in case['states']]
            tsep.require(set(states) == set(ids), 'Every planned state needs a record or missing reason')
            previous = None; previous_observed = operator['navigation_started_at']; gap = False; inputs = {}; checks = []; indices = []
            for index, state in enumerate(case['states']):
                task_id = page_record['task_ids'][index]; record = states[state['id']]
                if set(record) == {'missing_reason'}:
                    inputs[task_id] = {'snapshot': None, 'missing_reason': record['missing_reason']}; gap = True; all_received = False; continue
                tsep.require(not gap, 'Sequence continued after missing state')
                receipt_id = record['page_receipt']
                tsep.require(isinstance(receipt_id, str) and re.fullmatch('[0-9a-f]{64}', receipt_id), 'Invalid receipt id')
                posts = [i for i, r in enumerate(logs) if r.get('receipt') == receipt_id]
                tsep.require(len(posts) == 1 and posts[0] not in used, 'Missing/ambiguous state POST')
                post = posts[0]; payload = payloads[post]; used.add(post); indices.append(post)
                tsep.require(all(payload[k] == record[k] for k in FIELDS) and payload['user_agent'] == ua == logs[post]['agent'], 'Page/operator state mismatch')
                tsep.require(payload['context'] == reg['token'] and payload['url'] == page_record['url'] == payload['tree']['document_url'] and
                    payload['state'] == state['id'] and payload['action'] == state['action'] and type(payload['sequence_index']) is int and
                    payload['sequence_index'] == index and payload['previous_receipt'] == previous, 'Wrong state/action/receipt chain')
                chronological(previous_observed, record['action_started_at'], payload['capture_started_at'], payload['captured_at'],
                              logs[post]['observed_at'], record['observed_at'], operator['observed_at'])
                chronological(logs[get]['observed_at'], logs[post]['observed_at'])
                previous = receipt_id; previous_observed = record['observed_at']
                inputs[task_id] = {'snapshot': {k: payload[k] for k in ('tree', 'script_sha256')}, 'missing_reason': None}; count += 1
            ledger = sequence.assess(reg, page_record['id'], inputs)
            for state, row in zip(case['states'], ledger['states']):
                if row['assessment'] is None: continue
                record = states[state['id']]
                planned = single.assertions(state, row['assessment'], record['tree'], record['errors'])
                planned.append({'check': 'captured-state-marker', 'expected': state['id'], 'observed': marker(record['tree']), 'matches': marker(record['tree']) == state['id']})
                checks.append({'state_id': state['id'], 'checks': planned}); all_checks += planned
            page_results.append({'id': case['id'], 'ledger': ledger, 'checks': checks, 'receipt_chain_complete': not gap,
                'source_initial_canonical': case['head'], 'source_response_sha256': page_record['response_sha256'],
                'operator_record_sha256': sequence.candidate.core.digest(operator), 'GET_log_index': get, 'POST_log_indices': indices,
                'developer_logs': {k: r['devLogs'] for k, r in states.items() if 'devLogs' in r}})
        results[env] = {'status': 'collected', 'pages': page_results}
    tsep.require(len(used) == len(logs), 'Extra/unmatched requests; retain attempts, do not retry')
    return {'kind': 'synthetic-canonical-sequence-campaign', 'version': VERSION, 'normative': False,
        'registration_sha256': receipt['registration_sha256'], 'environments': results, 'observations': count, 'server_requests': len(logs),
        'all_planned_states_received': all_received, 'all_collected_checks_matched': all(c['matches'] for c in all_checks) if all_checks else None,
        'recipe_checks': len(all_checks), 'limitations': recipes()['limitations']}


def finish(source, observation_file, output):
    source = Path(source); result = analyze(source, tsep.read_json(observation_file)); output = ts01.new_directory(output); names = []
    for name in transport.source_names(source):
        dest = output/'source'/name; dest.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source/name, dest); names.append('source/'+name)
    shutil.copyfile(observation_file, output/'observations.json'); names.append('observations.json')
    ts01.save(output/'results.json', result); names.append('results.json'); ts01.manifest(output, names); return result


def replay(folder):
    folder = Path(folder); manifest = ts01.verify(folder)
    tsep.require(set(manifest) == {'observations.json', 'results.json'} | {'source/'+n for n in transport.source_names(folder/'source')}, 'Unexpected manifest file')
    tsep.require({p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file() or p.is_symlink()} == set(manifest) | {'SHA256SUMS'}, 'Unexpected file')
    result = analyze(folder/'source', tsep.read_json(folder/'observations.json'))
    tsep.require(result == tsep.read_json(folder/'results.json'), 'Replayed sequence differs')
    return {'same_results': True, 'observations': result['observations'], 'recipe_checks': result['recipe_checks'],
        'all_planned_states_received': result['all_planned_states_received'], 'all_collected_checks_matched': result['all_collected_checks_matched'],
        'network_requests': 0, 'browser_executed': False}


def main():
    p = argparse.ArgumentParser(description=__doc__); sub = p.add_subparsers(dest='command', required=True)
    s = sub.add_parser('serve'); s.add_argument('--output', required=True)
    f = sub.add_parser('finish'); f.add_argument('source'); f.add_argument('--observations', required=True); f.add_argument('--output', required=True)
    r = sub.add_parser('replay'); r.add_argument('folder'); args = p.parse_args()
    try:
        if args.command == 'serve':
            servers, threads, reg = start(args.output); print(json.dumps({'ready': True, 'pages': reg['pages']}), flush=True)
            try: threads[0].join()
            except KeyboardInterrupt: transport.stop(servers, threads)
            return 0
        result = finish(args.source, args.observations, args.output) if args.command == 'finish' else replay(args.folder)
        print(json.dumps({k: v for k, v in result.items() if k != 'environments'}))
        return 0 if result['all_collected_checks_matched'] is True and result['all_planned_states_received'] else 2
    except (ValueError, KeyError, TypeError, OSError) as error: print(str(error), file=sys.stderr); return 64


if __name__ == '__main__': sys.exit(main())
