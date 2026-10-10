#!/usr/bin/env python3
"""Predeclared SYNTHETIC canonical laboratory; no normative assessment. Apache-2.0."""
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
from examples import rendered_metadata_lab as transport
from experiments import rendered_canonical_v2 as candidate
from experiments import rendered_metadata as metadata
from provenance.runtime import loaded_sources

VERSION = '1'
RECIPE = 'tests/fixtures/predeclared-canonical-v1.json'
PAGE_SCRIPT = 'examples/predeclared_canonical_page.js'
AGENT = 'TSEP-predeclared-source/1'


def recipes():
    path = ROOT/RECIPE
    tsep.require(tsep.digest(path) == path.with_suffix('.sha256').read_text().split()[0], 'Recipe digest mismatch')
    result = tsep.read_json(path)
    tsep.require(result['capture_script_sha256'] == metadata.script_digest(), 'Recipe script mismatch')
    return result


def sources():
    result = dict(transport.sources(), **candidate.sources())
    result.update(loaded_sources(ROOT, {'examples/predeclared_canonical_lab.py': sys.modules[__name__]}))
    for name in (RECIPE, RECIPE.replace('.json', '.sha256'), PAGE_SCRIPT):
        result[name] = tsep.digest(ROOT/name)
    return result


def page(case, token, endpoint):
    script = (ROOT/PAGE_SCRIPT).read_text()
    for key, value in [('__SCRIPT_SHA__', metadata.script_digest()), ('__CONTEXT__', token),
                       ('__ENDPOINT__', endpoint), ('__TRIGGER__', case['trigger'])]:
        script = script.replace(key, json.dumps(value))
    script = script.replace('__CAPTURE_EXPRESSION__', (ROOT/metadata.SCRIPT).read_text().strip())
    return ('<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>TSEP · '+case['id']+'</title>'+
            case['head']+'<style>body{font:18px/1.6 system-ui;background:#102032;color:#edf3f8;max-width:1000px;margin:40px auto}h1{font-size:36px}code{color:#b8ed76;overflow-wrap:anywhere}</style></head><body>'+
            '<p>LABORATOIRE SYNTHÉTIQUE · CRITÈRES PRÉDÉCLARÉS</p><h1>'+case['id']+'</h1>'+
            '<p>Déclenchement : <code id="lab-state">'+case['trigger']+'</code></p>'+
            '<p>Contexte : <code id="lab-context">'+token+'</code></p>'+
            '<p>Agent : <code id="lab-agent">pending</code></p><p>Document : <code id="lab-url">pending</code></p>'+
            '<p>Erreurs signalées : <code id="lab-errors">[]</code></p><p>Reçu local : <code id="lab-receipt">pending</code></p>'+
            '<script>const failures=[];function error(x){failures.push(String(x));document.getElementById("lab-errors").textContent=JSON.stringify(failures)};'+
            'window.addEventListener("error",e=>error(e.message));window.addEventListener("unhandledrejection",e=>error(e.reason));'+
            'try{'+case['script']+'}catch(e){error(e)};document.getElementById("lab-agent").textContent=navigator.userAgent;'+
            'document.getElementById("lab-url").textContent=location.href;</script><script>'+script+'</script>'+case['tail']+'</body></html>')


def scope(base, token):
    origin = base.rsplit('/', 1)[0]
    cases = [transport.substitute(c, base, '') for c in recipes()['cases']]
    tasks = []; responses = {}
    for env in recipes()['environments']:
        for case in cases:
            url = base+'/case/'+env+'/'+case['id']
            raw = transport.wire(page(case, token, base+'/capture'), [origin], True)
            tasks.append({'id': env+'/'+case['id'], 'case': case['id'], 'environment': env, 'url': url,
                          'intent': case['intent'], 'trigger': case['trigger'], 'response_sha256': metadata.sha(raw)})
            responses[url] = raw
    return cases, tasks, responses


def start(output):
    folder = ts01.new_directory(output); before = sources(); plan = recipes()
    server = ThreadingHTTPServer(('127.0.0.1', 0), transport.Handler)
    origin = 'http://127.0.0.1:'+str(server.server_port); token = secrets.token_hex(8); base = origin+'/'+token
    cases, tasks, responses = scope(base, token)
    reg = {'kind': 'predeclared-canonical-laboratory', 'version': VERSION, 'normative': False,
           'registered_at': ts01.now(), 'base': base, 'token': token, 'origin': origin,
           'source_files': before, 'recipe': plan, 'cases': cases, 'tasks': tasks,
           'environments': plan['environments'], 'capture_endpoint': base+'/capture',
           'script_sha256': metadata.script_digest(), 'execution_context': 'not-attested'}
    ts01.save(folder/'registration.json', reg); (folder/'requests.jsonl').touch()
    server.folder = folder; server.origin = origin; server.lock = threading.Lock(); server.responses = responses
    server.daemon_threads = True; server.endpoint = reg['capture_endpoint']; server.token = token
    server.task_urls = set(responses)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    try:
        phases = []
        for i in range(0, len(tasks), 10):
            name = 'source-'+str(i//10+1); phases.append(name)
            ts01.capture({'urls': [t['url'] for t in tasks[i:i+10]], 'origins': [origin], 'agent': AGENT,
                          'accept_encoding': 'identity', 'timeout': 3, 'max_bytes': 262144, 'max_redirects': 0,
                          'allow_loopback': True, 'network': 'controlled loopback synthetic',
                          'selection_method': 'All predeclared environment-specific tasks', 'access': 'synthetic'}, folder/name)
        ts01.save(folder/'receipt.json', {'created_at': ts01.now(), 'registration_sha256': tsep.digest(folder/'registration.json'),
                  'phases': {n: tsep.digest(folder/n/'SHA256SUMS') for n in phases}, 'source_files': before})
        tsep.require(sources() == before, 'Sources changed before browser collection')
        return [server], [thread], reg
    except BaseException:
        transport.stop([server], [thread]); raise


def assertions(case, result, tree, errors):
    expected = case['expected']
    actual = {'outcome': result['outcome'], 'reasons': result['reasons'], 'ready_state': tree['ready_state'],
              'traversal_complete': result['coverage']['traversal_complete'], 'stop_reason': result['coverage']['stop_reason'],
              'canonicals': [{'id': c['id_attribute'], **{k: c[k] for k in ('raw_href', 'resolved_href', 'position')}}
                             for c in result['canonical']]}
    return [{'check': k, 'expected': v, 'observed': actual[k], 'matches': actual[k] == v} for k, v in expected.items()] + [
        {'check': 'page-errors', 'expected': [], 'observed': errors, 'matches': errors == []}]


def analyze(source, observations):
    source = Path(source); reg = tsep.read_json(source/'registration.json'); receipt = tsep.read_json(source/'receipt.json')
    tsep.require(reg['kind'] == 'predeclared-canonical-laboratory' and reg['version'] == VERSION, 'Unsupported laboratory')
    tsep.require(reg['source_files'] == receipt['source_files'] == sources(), 'Changed laboratory sources')
    tsep.require(receipt['registration_sha256'] == tsep.digest(source/'registration.json'), 'Registration changed')
    tsep.require(reg['recipe'] == recipes() and reg['environments'] == recipes()['environments'], 'Changed recipes/environments')
    url = urlsplit(reg['origin'])
    tsep.require(url.scheme == 'http' and url.hostname == '127.0.0.1' and url.port and
                 reg['origin'] == 'http://127.0.0.1:'+str(url.port) and re.fullmatch('[0-9a-f]{16}', reg['token']) and
                 reg['base'] == reg['origin']+'/'+reg['token'] and reg['capture_endpoint'] == reg['base']+'/capture', 'Changed endpoint')
    cases, tasks, responses = scope(reg['base'], reg['token'])
    tsep.require(reg['cases'] == cases and reg['tasks'] == tasks and reg['script_sha256'] == metadata.script_digest(), 'Changed registered scope')
    expected_urls = [t['url'] for t in tasks]
    phases = ['source-'+str(i//10+1) for i in range(0, len(tasks), 10)]
    tsep.require(list(receipt['phases']) == phases, 'Unexpected source phases')
    for i, name in enumerate(phases):
        tsep.require(tsep.digest(source/name/'SHA256SUMS') == receipt['phases'][name], 'Source phase changed')
        ts01.verify(source/name); phase = tsep.read_json(source/name/'capture.json'); ts01.same_collector(phase)
        selected = expected_urls[i*10:i*10+10]
        tsep.require(phase['settings']['urls'] == selected and [t['url'] for t in phase['targets']] == selected and
                     phase['settings']['agent'] == AGENT, 'Changed source selection')
        tsep.require(phase['sources_unchanged_during_collection'] is True and
                     tsep.timestamp(reg['registered_at']) <= tsep.timestamp(phase['started_at']) <=
                     tsep.timestamp(phase['finished_at']) <= tsep.timestamp(receipt['created_at']), 'Source chronology mismatch')
        for n, target in enumerate(phase['targets'], 1):
            tsep.require(len(target['http']) == 1 and target['http'][0]['complete'] is True, 'Incomplete source')
            for kind in ('request', 'response'):
                tsep.require((source/name/('target-'+str(n)+'-hop-1-'+kind+'.bin')).read_bytes() ==
                             raw_bytes(target['http'][0][kind]), 'Source JSON/sidecar mismatch')
            tsep.require(raw_bytes(target['http'][0]['response']) == responses[target['url']], 'Served source differs from preregistered bytes')
    logs = [json.loads(x) for x in (source/'requests.jsonl').read_text().splitlines()]; used = set()
    payloads = {}
    for i, row in enumerate(logs):
        tsep.require(row['peer'] == '127.0.0.1' and row['complete'] is True, 'Incomplete/non-local request')
        if row.get('method') == 'POST':
            tsep.require(row['url'] == reg['capture_endpoint'] and row['status'] == 200 and
                         re.fullmatch('[0-9a-f]{64}', row['receipt']), 'Invalid page POST')
            raw = (source/'posts'/(row['receipt']+'.json')).read_bytes()
            tsep.require(metadata.sha(raw) == row['receipt'] and
                         tsep.digest(source/'posts'/(row['receipt']+'.response.bin')) == row['response_sha256'], 'Changed page POST bytes')
            payloads[i] = transport.decode_page_export(raw)
        else:
            tsep.require(row['url'] in responses and row['response_sha256'] == metadata.sha(responses[row['url']]), 'Unexpected/different server response')
            if row['agent'] == AGENT:
                tsep.require(tsep.timestamp(reg['registered_at']) <= tsep.timestamp(row['observed_at']) <=
                             tsep.timestamp(receipt['created_at']), 'Source log chronology mismatch')
                used.add(i)
    tsep.require(Counter(logs[i]['url'] for i in used) == Counter(expected_urls), 'Source request scope')
    tsep.require(set(observations) == set(reg['environments']), 'Missing browser environment')
    results = {}; total = 0
    for env in reg['environments']:
        observed = observations[env]; env_tasks = [t for t in tasks if t['environment'] == env]
        if observed.get('status') == 'not-collected':
            tsep.require(set(observed) == {'status', 'reason'} and isinstance(observed['reason'], str) and observed['reason'].strip(), 'Missing unavailability reason')
            results[env] = observed; continue
        tsep.require(set(observed) == {'status', 'records'} and observed['status'] == 'collected' and
                     set(observed['records']) == {t['case'] for t in env_tasks}, 'Missing/extra browser task')
        rows = []
        for task, case in zip(env_tasks, cases):
            record = observed['records'][case['id']]; receipt_id = record['page_receipt']
            tsep.require(isinstance(receipt_id, str) and re.fullmatch('[0-9a-f]{64}', receipt_id), 'Invalid page receipt')
            posts = [i for i, r in enumerate(logs) if r.get('receipt') == receipt_id]
            tsep.require(len(posts) == 1 and posts[0] not in used, 'Missing/ambiguous page POST')
            post = posts[0]; payload = payloads[post]; used.add(post)
            tsep.require(all(payload[k] == record[k] for k in ('tree', 'script_sha256', 'context', 'url', 'state', 'errors', 'capture_started_at', 'captured_at'))
                         and payload['user_agent'] == record['browser']['user_agent'], 'Page/operator record mismatch')
            tsep.require(payload['url'] == task['url'] == payload['tree']['document_url'] and payload['context'] == reg['token'] and
                         payload['state'] == task['trigger'], 'Wrong page/context/trigger')
            ua = payload['user_agent']
            tsep.require(ua and ua != AGENT and logs[post]['agent'] == ua and all(record['browser'].get(k) for k in ('name', 'version')), 'Missing/different browser identity')
            dates = [receipt['created_at'], record['navigation_started_at'], payload['capture_started_at'],
                     payload['captured_at'], logs[post]['observed_at'], record['observed_at']]
            tsep.require(all(tsep.timestamp(a) <= tsep.timestamp(b) for a, b in zip(dates, dates[1:])), 'Browser/capture chronology mismatch')
            gets = [i for i, r in enumerate(logs) if r.get('method') != 'POST' and r['url'] == task['url'] and r['agent'] == ua and i not in used]
            tsep.require(len(gets) == 1, 'Missing/ambiguous browser GET')
            get = gets[0]; used.add(get)
            tsep.require(tsep.timestamp(record['navigation_started_at']) <= tsep.timestamp(logs[get]['observed_at']) <=
                         tsep.timestamp(logs[post]['observed_at']), 'Browser GET chronology mismatch')
            snapshot = {k: payload[k] for k in ('tree', 'script_sha256')}
            intent = dict(task['intent'], format='rendered-canonical-intent', version='2', mode=candidate.MODE,
                          document_url=task['url'], record_sha256=candidate.core.digest(snapshot),
                          registration_sha256=candidate.core.digest(reg), case_id=task['id'])
            assessment = candidate.assess(snapshot, intent, reg)
            checks = assertions(case, assessment, payload['tree'], payload['errors'])
            rows.append({'id': case['id'], 'assessment': assessment, 'checks': checks,
                         'checks_matched': all(c['matches'] for c in checks), 'page_receipt': receipt_id,
                         'source_response_sha256': task['response_sha256'], 'source_initial_canonical': case['head'],
                         'operator_record_sha256': candidate.core.digest(record), 'developer_logs': record['devLogs'],
                         'server_log_indices': {'GET': get, 'POST': post}})
        results[env] = {'status': 'collected', 'records': rows}; total += len(rows)
    tsep.require(len(used) == len(logs), 'Extra/unmatched requests; retain attempts, do not resample')
    collected = [r for env in results.values() if env['status'] == 'collected' for r in env['records']]
    return {'kind': 'predeclared-synthetic-canonical-results', 'version': VERSION, 'normative': False,
            'registration_sha256': receipt['registration_sha256'], 'environments': results, 'observations': total,
            'server_requests': len(logs), 'all_collected_checks_matched': all(r['checks_matched'] for r in collected) if collected else None,
            'all_environments_collected': all(e['status'] == 'collected' for e in results.values()),
            'limitations': recipes()['limitations'] + ['Recipes authored knowing comparison core; no independent validation',
                'Chronology is internally checked but not attested by a trusted clock', 'Developer logs retained; not used as proof of absence of errors']}


def finish(source, observation_file, output):
    source = Path(source); result = analyze(source, tsep.read_json(observation_file)); output = ts01.new_directory(output); names = []
    for name in transport.source_names(source):
        target = output/'source'/name; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source/name, target); names.append('source/'+name)
    shutil.copyfile(observation_file, output/'observations.json'); names.append('observations.json')
    ts01.save(output/'results.json', result); names.append('results.json'); ts01.manifest(output, names)
    return result


def replay(folder):
    folder = Path(folder); manifest = ts01.verify(folder)
    tsep.require(set(manifest) == {'observations.json', 'results.json'} | {'source/'+n for n in transport.source_names(folder/'source')}, 'Unexpected manifest file')
    actual = {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file() or p.is_symlink()}
    tsep.require(actual == set(manifest) | {'SHA256SUMS'}, 'Unexpected file')
    result = analyze(folder/'source', tsep.read_json(folder/'observations.json'))
    tsep.require(result == tsep.read_json(folder/'results.json'), 'Replayed result differs')
    return {'same_results': True, 'observations': result['observations'], 'network_requests': 0, 'browser_executed': False,
            'all_collected_checks_matched': result['all_collected_checks_matched'], 'all_environments_collected': result['all_environments_collected']}


def main():
    p = argparse.ArgumentParser(description=__doc__); sub = p.add_subparsers(dest='command', required=True)
    s = sub.add_parser('serve'); s.add_argument('--output', required=True)
    f = sub.add_parser('finish'); f.add_argument('source'); f.add_argument('--observations', required=True); f.add_argument('--output', required=True)
    r = sub.add_parser('replay'); r.add_argument('folder'); args = p.parse_args()
    try:
        if args.command == 'serve':
            servers, threads, reg = start(args.output); print(json.dumps({'ready': True, 'tasks': reg['tasks']}), flush=True)
            try: threads[0].join()
            except KeyboardInterrupt: transport.stop(servers, threads)
            return 0
        result = finish(args.source, args.observations, args.output) if args.command == 'finish' else replay(args.folder)
        print(json.dumps({k: v for k, v in result.items() if k != 'environments'}))
        return 0 if result['all_collected_checks_matched'] is True and result['all_environments_collected'] else 2
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(str(error), file=sys.stderr); return 64


if __name__ == '__main__': sys.exit(main())
