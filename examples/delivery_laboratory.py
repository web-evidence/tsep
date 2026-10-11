#!/usr/bin/env python3
"""TS39 laboratory: actual bounded origin/cache HTTP, authored policies and reviews.

Apache-2.0. Eight prefrozen scenarios; offline replay never recollects or purges.
"""
import argparse
import copy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import tempfile
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from adapters import captures, replay as bundle_replay
from collectors import ts01
from conformance import delivery
from conformance.http import raw_bytes, message
from examples import delivery_cache_transport as transport
from provenance.runtime import loaded_sources, runtime_identity

VERSION = '1'
FIXTURE = 'tests/fixtures/delivery-laboratory-v1.json'
FREEZE = 'tests/fixtures/delivery-laboratory-v1.sha256'
RULES = ['TS39-A01', 'TS39-A02', 'TS39-A03']
ASSESSOR = 'Controlled TS39 laboratory; all reviews authored, no human review'
SELECTION = 'Eight prefrozen fictional cases; actual loopback origin/cache operations, no production or geographic inference'
SCOPE = 'Actual HTTP/cache experiment with a fictional site and authored reviews. No Edikka, production CDN, geographic coverage, authenticated reviewer or actual operator visit.'
now, compact, sha = transport.now, transport.compact, transport.sha
save = ts01.save


def fixture():
    tsep.require(tsep.digest(ROOT / FIXTURE) == (ROOT / FREEZE).read_text().strip(), 'Frozen delivery recipe changed')
    return tsep.read_json(ROOT / FIXTURE)


def sources():
    result = captures.source_files()
    result.update(loaded_sources(ROOT, {'examples/delivery_laboratory.py': sys.modules[__name__],
        'examples/delivery_cache_transport.py': transport, 'collectors/ts01.py': ts01,
        'adapters/replay.py': bundle_replay}))
    for name in (FIXTURE, FREEZE, 'spec/protocol.json', 'schemas/report.schema.json'):
        result[name] = tsep.digest(ROOT / name)
    return result


def configurations():
    return {c['id']: {k: c[k] for k in ('id', 'mode', 'representation')} for c in fixture()['cases']}


def review(binding, at, **values):
    return dict(reviewer='Fictional laboratory reviewer', assistance='Authored from the frozen laboratory recipe',
        reason='Synthetic exercise review; actual local observations are separate from these authored judgments.',
        provenance='synthetic-exercise', observed_at=at, binding_sha256=binding, complete=True, **values)


def document(id, uri, value, at):
    raw = compact(value)
    return {'id': id, 'source_uri': uri, 'raw_text': raw, 'sha256': sha(raw), 'observed_at': at}


def native_intent(base, declared):
    return {'declared_at': declared, 'crawler': transport.UA, 'directive_crawler': 'googlebot',
        'robots_policy': {'profile': 'google-documented-core-v1', 'product_token': 'googlebot'},
        'public_canonical': True, 'indexing': 'allow', 'following': 'unspecified', 'access_basis': 'test-client-only',
        'rendering': {'mode': 'exempt', 'basis': 'reviewed-stable'},
        'canonical': {'preferred_url': base + '/page', 'members': [{'url': base + '/page',
            'required_methods': ['html'], 'rendering': {'mode': 'exempt', 'basis': 'reviewed-stable'}}]}}


def plans(base, declared, reviewed, start, end):
    recipe = fixture(); result = {}
    for case in recipe['cases']:
        cells = []
        for step in case['steps']:
            language = 'fr' if case['representation'] in ('bilingual', 'encoding') or step['accept_language'] is None else 'de'
            marker = recipe['page']['bilingual' if case['representation'] == 'bilingual' else language]
            cells.append({'id': step['id'], 'url': base + '/page', 'user_agent': transport.UA,
                'request_fields': {'accept-language': None if step['accept_language'] is None else [step['accept_language']],
                    'accept-encoding': [step['accept_encoding']], 'cookie': None, 'authorization': None},
                'context_claims': {'network': 'numeric-loopback', 'geography': 'not-observed'},
                'context_id': step['id'], 'mode': 'representation',
                'expectation': {'status': 200, 'final_url': base + '/page', 'language': language, 'content': marker},
                'seo_intent': native_intent(base, declared)})
        config = document('configuration', base + '/retained/configuration/' + case['id'],
            {'planned_configuration': configurations()[case['id']], 'request_profile': recipe['request_profile'],
             'freshness_policy': recipe['freshness'], 'scope': SCOPE}, declared)
        target = {'url': base + '/scope/' + case['id'], 'intent': {'declared_at': declared, 'delivery': {
            'reader': delivery.READER, 'window_start': start, 'window_end': end, 'cells': cells,
            'pairs': [{'id': 'pair-' + str(i), 'left': cells[i]['id'], 'right': cells[i+1]['id']} for i in range(len(cells)-1)],
            'mechanisms': ['negotiation'] + ([] if case['mode'] == 'bypass' else ['cache']),
            'cache_checks': [{'id': 'reuse-' + a + b, 'stored_cell': a, 'served_cell': b,
                'layer': 'controlled-edge', 'clock_skew_ms': 0, 'transformation': 'none'} for a, b in case['reuses']]}},
            'delivery_configuration': config}
        binding = delivery.digest({k: target[k] for k in ('url', 'intent', 'delivery_configuration')})
        target['delivery_plan_review'] = review(binding, reviewed, judgment='supported', representative=True, operator_policy_supported=True)
        result[case['id']] = target
    return result


def native(cell, hop, robots, at):
    support = 'Authored static-template review: the frozen origin emits no executable script or later metadata mutation. Not a browser or human observation.'
    exemption = {'basis': 'reviewed-stable', 'reviewer': 'Fictional laboratory reviewer',
        'reason': support, 'observed_at': at, 'source_http_sha256': delivery.digest([hop]),
        'provenance': 'synthetic-exercise', 'support': [{'name': 'Authored static-template inventory',
            'content': support, 'sha256': sha(support)}]}
    return {'url': cell['url'], 'observed_at': at, 'intent': copy.deepcopy(cell['seo_intent']),
        'context': {'id': cell['context_id'], 'network': 'Numeric loopback only', 'bounds': 'One complete GET, 3s/32768 bytes',
                    'tool': 'TSEP controlled delivery laboratory', 'tool_version': VERSION},
        'http': [hop], 'exemption_review': exemption,
        'documents': [{'url': cell['url'], 'observed_at': at, 'context_id': cell['context_id'],
                       'http': [hop], 'exemption_review': copy.deepcopy(exemption)}],
        'robots': {'observed_at': robots['received_at'], 'http': [robots]},
        'access_review': {'observed_at': at, 'outcome': 'no-obstacle', 'provenance': 'synthetic-exercise',
                         'reason': 'Authored review of this test-client path only; no actual Googlebot access.'}}


def input_for(case, registration, phase, records, robots, receipt):
    t = copy.deepcopy(registration['plans'][case['id']]); p = t['intent']['delivery']
    at = receipt['synthetic_review_at']; t.update(observed_at=receipt['assessed_at'], delivery_synthetic=True,
        context={'network': 'Numeric 127.0.0.1, no DNS or proxy', 'bounds': 'Closed recipe, actual HTTP/cache; 15s window',
                 'tool': 'TSEP controlled delivery laboratory', 'tool_version': VERSION})
    t['delivery_observations'] = [{'cell_id': cell['id'], 'http': [hop],
        'native': native(cell, hop, robots, phase['synthetic_review_at'])} for cell, hop in zip(p['cells'], phase['http'])]
    t['delivery_sources'] = [copy.deepcopy(t['delivery_configuration'])]
    selected = [r for r in records if r['id'] in phase['edge_record_ids']]
    if not case.get('withhold_cache_evidence'):
        t['delivery_sources'].append(document('cache-journal', registration['edge_base'] + '/retained/journal/' + case['id'],
                                              selected, receipt['exported_at']))
    refs = [s['id'] for s in t['delivery_sources']]
    t['delivery_semantic_reviews'] = []; t['delivery_context_reviews'] = []
    for cell, observation in zip(p['cells'], t['delivery_observations']):
        _, _, body = message(observation['http'][0]['response'], True); text = body.decode('utf-8')
        binding = {'url': t['url'], 'intent': t['intent'], 'cell': cell, 'observation': observation}
        t['delivery_semantic_reviews'].append(dict(review(delivery.digest(binding), at,
            language='supported' if 'lang="' + cell['expectation']['language'] + '"' in text else 'contradiction',
            content='supported' if cell['expectation']['content'] in text else 'contradiction', accessibility='supported'), cell_id=cell['id']))
        binding['sources'] = t['delivery_sources']
        t['delivery_context_reviews'].append(dict(review(delivery.digest(binding), at, context='supported', mechanism='supported',
            operator_policy='supported', actual_context=cell['context_claims'], claims_operator_visit=False), cell_id=cell['id'], source_ids=refs))
    t['delivery_cache_records'] = []
    if not case.get('withhold_cache_evidence'):
        mapping = dict(zip([s['id'] for s in case['steps']], selected))
        for check in p['cache_checks']:
            rows = []
            for kind, cid in [('store', check['stored_cell']), ('serve', check['served_cell'])]:
                event = mapping[cid]['cache_event']
                tsep.require(event and event['kind'] == kind, 'Observed cache action differs from prior reuse check')
                row = {k: event[k] for k in ('event_id', 'kind', 'entry_id', 'layer', 'at', 'request_sha256', 'response_sha256', 'body_sha256')}
                rows.append(dict(row, cell_id=cid))
            raw = ''.join(compact(r) + '\n' for r in rows)
            record = {'id': check['id'], 'raw_jsonl': raw, 'sha256': sha(raw), 'exported_at': receipt['exported_at']}
            binding = {'url': t['url'], 'intent': t['intent'], 'check': check, 'record': copy.deepcopy(record), 'sources': t['delivery_sources']}
            record['review'] = dict(review(delivery.digest(binding), at, linkage='supported', clock='supported',
                no_transform='supported', freshness='supported'), source_ids=refs)
            t['delivery_cache_records'].append(record)
    return {'input_version': '2', 'rules': list(RULES), 'targets': [t]}


def check_capture(reg, evidence, edge, origin, operations, receipt):
    recipe = fixture(); base = reg['edge_base']; origin_base = reg['origin_base']
    transport.loopback(base); transport.loopback(origin_base)
    tsep.require(base != origin_base, 'Origin and cache must be distinct listeners')
    tsep.require(reg['recipe'] == recipe and reg['configurations'] == configurations(), 'Frozen recipe/configuration differs')
    tsep.require(reg['plans'] == plans(base, reg['declared_at'], reg['synthetic_plan_review_at'], reg['window_start'], reg['window_end']),
                 'Registered delivery plans differ')
    start, end = map(tsep.timestamp, (reg['window_start'], reg['window_end']))
    tsep.require(tsep.timestamp(reg['declared_at']) <= tsep.timestamp(reg['synthetic_plan_review_at']) < start
                 and (end-start).total_seconds() == 15 and end <= tsep.timestamp(receipt['exported_at'])
                 <= tsep.timestamp(receipt['synthetic_review_at']) <= tsep.timestamp(receipt['assessed_at']), 'Registration/receipt chronology differs')
    tsep.require(receipt.get('collection_complete') is True and len(edge) == recipe['expected_edge_requests']
        and len(origin) == recipe['expected_origin_requests'] and len(evidence['phases']) == len(recipe['cases']), 'HTTP or phase population differs')
    for layer, rows in [('edge', edge), ('origin', origin)]:
        tsep.require([r['id'] for r in rows] == [layer+'-'+str(i+1) for i in range(len(rows))], 'Server record IDs/order differ')
    for r in edge + origin:
        tsep.require(r['peer_address'] == '127.0.0.1' and start <= tsep.timestamp(r['at']) <= tsep.timestamp(r['sent_at']) <= end,
                     'Server peer/time differs from closed scope')
        config = configurations()[r['phase']]
        tsep.require(r['configuration_sha256'] == sha(compact(config)+'\n'), 'Observed configuration differs')
    clients = [evidence['robots']] + [h for p in evidence['phases'] for h in p['http']]
    for h, r in zip(clients, edge):
        tsep.require(h['complete'] is True and h['peer_address'] == '127.0.0.1'
            and h['request'] == r['request'] and h['response'] == r['response'] and h['url'] == r['url'], 'Client/server bytes differ')
        tsep.require(start <= tsep.timestamp(h['sent_at']) <= tsep.timestamp(r['at']) <= tsep.timestamp(r['sent_at'])
            <= tsep.timestamp(h['received_at']) <= end and h['start_mono_ns'] <= r['mono_ns'] <= h['end_mono_ns'], 'Client/server chronology differs')
        transport.request_values(raw_bytes(h['request']), base); message(h['response'], True)
    forwarded = [(r['origin_exchange'], r) for r in edge if r['origin_exchange'] is not None]
    tsep.require(len(forwarded) == len(origin), 'Origin forwarding population differs')
    for (h, parent), r in zip(forwarded, origin):
        config = configurations()[r['phase']]
        path, language, encoding = transport.request_values(raw_bytes(r['request']), origin_base)
        expected_wire = transport.origin_response(recipe, config, base, path, language, encoding, r['at'])
        edge_path, edge_language, edge_encoding = transport.request_values(raw_bytes(parent['request']), base)
        tsep.require(r['phase'] == parent['phase'] and (path, language, encoding) == (edge_path, edge_language, edge_encoding)
            and tsep.timestamp(parent['at']) <= tsep.timestamp(h['sent_at']) <= tsep.timestamp(h['received_at'])
            <= tsep.timestamp(parent['sent_at']), 'Forwarded request or parent phase differs')
        tsep.require(h['complete'] is True and h['peer_address'] == '127.0.0.1' and h['url'] == r['url']
            and h['request'] == r['request'] and h['response'] == r['response']
            and raw_bytes(r['response']) == expected_wire, 'Origin bytes differ from frozen representation')
        tsep.require(tsep.timestamp(h['sent_at']) <= tsep.timestamp(r['at']) <= tsep.timestamp(r['sent_at'])
            <= tsep.timestamp(h['received_at']) and h['start_mono_ns'] <= r['mono_ns'] <= h['end_mono_ns'], 'Origin chronology differs')
    robots = edge[0]
    tsep.require(evidence['robots']['url'] == base+'/robots.txt' and robots['action'] == 'bypass'
        and raw_bytes(robots['request']) == transport.request(base, '/robots.txt', None, 'identity')
        and robots['phase'] == recipe['cases'][0]['id'] and robots['origin_exchange'] is not None
        and robots['response'] == robots['origin_exchange']['response']
        and robots['entry_id'] is None and robots['cache_event'] is None
        and robots['cache_before'] == robots['cache_after'] == [], 'Robots exchange differs')
    entries = []; serial = 0; position = 1; previous_config = None
    tsep.require(len(operations) == 2*len(recipe['cases']), 'Configuration/purge population differs')
    for number, (case, phase) in enumerate(zip(recipe['cases'], evidence['phases'])):
        tsep.require(phase['id'] == case['id'] and len(phase['http']) == len(case['steps']), 'Phase differs')
        config = configurations()[case['id']]; config_op, purge_op = operations[2*number:2*number+2]
        for op in (config_op, purge_op):
            tsep.require(op['phase'] == case['id'] and tsep.timestamp(op['started_at']) <= tsep.timestamp(op['ended_at'])
                <= tsep.timestamp(phase['http'][0]['sent_at']), 'Configuration/purge chronology differs')
        tsep.require(config_op['kind'] == 'configuration' and config_op['previous_raw'] == previous_config
            and config_op['new_raw'] == compact(config)+'\n' and config_op['before'] == transport.snapshot(entries)
            and config_op['after'] == transport.snapshot(entries), 'Configuration operation or retained state differs')
        tsep.require(purge_op['kind'] == 'purge' and purge_op['before'] == transport.snapshot(entries)
            and purge_op['after'] == [] and tsep.timestamp(config_op['ended_at']) <= tsep.timestamp(purge_op['started_at']), 'Purge operation differs')
        if case.get('repair_of'):
            tsep.require(number > 0 and recipe['cases'][number-1]['id'] == case['repair_of'] and entries
                and json.loads(previous_config)['mode'] == 'ignore-vary' and config['mode'] == 'honor', 'Repair lacks preceding defective state')
        entries = []; previous_config = compact(config)+'\n'; selected = edge[position:position+len(case['steps'])]
        tsep.require(phase['edge_record_ids'] == [r['id'] for r in selected], 'Phase/server attribution differs')
        tsep.require(sum(r['origin_exchange'] is not None for r in selected) == case['expected_origin_requests'], 'Unexpected origin count in phase')
        for step, h, r in zip(case['steps'], phase['http'], selected):
            tsep.require(r['phase'] == case['id'] and raw_bytes(h['request']) == transport.request(base, '/page', step['accept_language'], step['accept_encoding']),
                         'Unplanned request or injected field')
            tsep.require(tsep.timestamp(h['received_at']) <= tsep.timestamp(phase['synthetic_review_at']) <= end, 'Authored native review time differs')
            tsep.require(r['cache_before'] == transport.snapshot(entries), 'Cache before-state differs')
            candidate = next((e for e in entries if e['key'] == transport.selected_key(config['mode'], base, '/page', step['accept_language'], step['accept_encoding'], e['vary'])), None)
            if config['mode'] == 'bypass':
                tsep.require(r['action'] == 'bypass' and r['cache_event'] is None and r['entry_id'] is None
                    and r['origin_exchange'] is not None and r['response'] == r['origin_exchange']['response'], 'Bypass falsely attributed to cache')
            else:
                event = r['cache_event']; action = 'serve' if candidate is not None else 'store'
                tsep.require(event and r['action'] == event['kind'] == action, 'Cache action differs from actual key/state')
                if candidate is None:
                    origin_hop = r['origin_exchange']; tsep.require(origin_hop is not None, 'Store lacks actual origin exchange')
                    _, fields, _ = message(origin_hop['response'], True); vary = fields['vary'][0]; serial += 1
                    candidate = {'entry_id': 'entry-'+str(serial), 'key': transport.selected_key(config['mode'], base, '/page', step['accept_language'], step['accept_encoding'], vary),
                        'vary': vary, 'origin': origin_hop, 'stored_request': r['request'],
                        'initial_age_ns': transport.initial_age(origin_hop), 'stored_mono_ns': origin_hop['end_mono_ns']}
                    entries.append(candidate)
                else: tsep.require(r['origin_exchange'] is None, 'Reuse falsely includes new origin request')
                current_age = candidate['initial_age_ns'] + event['mono_ns'] - candidate['stored_mono_ns']
                tsep.require(h['start_mono_ns'] <= event['mono_ns'] <= h['end_mono_ns'] and 0 <= current_age < 300*10**9,
                             'Cache age/monotonic interval differs')
                expected_wire = transport.wire_with_age(raw_bytes(candidate['origin']['response']), current_age//10**9)
                _, _, body = message(expected_wire, True)
                expected_event = {'event_id': 'cache-'+r['id'].split('-')[1], 'kind': action, 'entry_id': candidate['entry_id'],
                    'layer': 'controlled-edge', 'at': event['at'], 'mono_ns': event['mono_ns'],
                    'request_sha256': h['request']['sha256'], 'response_sha256': sha(expected_wire), 'body_sha256': sha(body),
                    'key': candidate['key'], 'initial_age_ns': candidate['initial_age_ns'], 'stored_mono_ns': candidate['stored_mono_ns'],
                    'current_age_ns': current_age, 'stored_request': candidate['stored_request'], 'origin_response': candidate['origin']['response']}
                tsep.require(event == expected_event and r['entry_id'] == candidate['entry_id'] and raw_bytes(r['response']) == expected_wire
                    and tsep.timestamp(h['sent_at']) <= tsep.timestamp(event['at']) <= tsep.timestamp(h['received_at']), 'Cache event/entry/bytes differ')
            tsep.require(r['cache_after'] == transport.snapshot(entries), 'Cache after-state differs')
        position += len(case['steps'])


def result_row(case, folder):
    atoms = tsep.read_json(folder/'bundle/assessment.json'); report = tsep.read_json(folder/'bundle/report.json')
    actual = {'atomic_outcomes': [r['outcome'] for r in atoms], 'control_status': report['results'][0]['status']}
    expected = {'atomic_outcomes': case['expected_atomic_outcomes'], 'control_status': case['expected_control_status']}
    return {'id': case['id'], 'actual': actual, 'expected': expected, 'matches_expectations': actual == expected,
            'report': case['id']+'/bundle/report.json', 'cache_evidence_withheld': bool(case.get('withhold_cache_evidence'))}


def summary(reg, rows):
    return {'kind': 'controlled-delivery-laboratory', 'version': VERSION, 'scope': SCOPE,
        'protocol_version': tsep.read_json(ROOT/'spec/protocol.json')['version'], 'source_files': reg['source_files'],
        'runtime': reg['runtime'], 'registered_at': reg['declared_at'], 'actual_edge_requests': 24,
        'actual_origin_requests': 14, 'actual_total_http_requests': 38, 'cases': rows,
        'all_expectations_matched': all(r['matches_expectations'] for r in rows),
        'human_review_performed': False, 'browser_observed': False, 'actual_operator_visit_established': False}


ROOT_FILES = ['registration.json', 'exchanges.json', 'edge.json', 'origin.json', 'operations.json', 'receipt.json',
              'results.json', 'edge-configuration.json', 'origin-configuration.json']


def run(output):
    source_files = sources(); recipe = fixture(); root = ts01.new_directory(output)
    edge = origin = None; threads = []; evidence = {'phases': []}; operations = []
    try:
        origin = transport.Server(('127.0.0.1', 0), transport.Handler)
        edge = transport.Server(('127.0.0.1', 0), transport.Handler)
        for server, layer, maximum in ((origin, 'origin', 14), (edge, 'edge', 24)):
            server.base = 'http://127.0.0.1:'+str(server.server_address[1]); server.layer = layer
            server.config_path = root/(layer+'-configuration.json'); server.configurations = configurations()
            server.recipe = recipe; server.records = []; server.scope_error = None; server.max_requests = maximum
        origin.public_base = edge.base; edge.origin_base = origin.base; edge.entries = []; edge.entry_serial = 0
        declared, reviewed = now(), now()
        start = (datetime.now(timezone.utc)+timedelta(seconds=0.25)).isoformat()
        end = (tsep.timestamp(start)+timedelta(seconds=15)).isoformat()
        reg = {'kind': 'delivery-laboratory-registration', 'version': VERSION, 'synthetic': True,
            'edge_base': edge.base, 'origin_base': origin.base, 'declared_at': declared,
            'synthetic_plan_review_at': reviewed, 'window_start': start, 'window_end': end,
            'configurations': configurations(), 'plans': plans(edge.base, declared, reviewed, start, end),
            'recipe': recipe, 'source_files': source_files, 'runtime': runtime_identity()}
        save(root/'registration.json', reg)
        for server in (origin, edge):
            thread = threading.Thread(target=server.serve_forever, kwargs={'poll_interval': 0.01}, daemon=True)
            thread.start(); threads.append((server, thread))
        remaining = (tsep.timestamp(start)-datetime.now(timezone.utc)).total_seconds()
        if remaining > 0: time.sleep(remaining)
        for index, case in enumerate(recipe['cases']):
            transport.set_configuration(edge, origin, configurations()[case['id']], operations)
            transport.purge(edge, case['id'], 'explicit-repair-purge' if case.get('repair_of') else 'independent-phase-reset', operations)
            if index == 0: evidence['robots'] = transport.fetch(edge.base, '/robots.txt')
            phase = {'id': case['id'], 'http': [], 'edge_record_ids': []}; evidence['phases'].append(phase)
            for step in case['steps']:
                phase['http'].append(transport.fetch(edge.base, '/page', step['accept_language'], step['accept_encoding']))
                phase['edge_record_ids'].append(edge.records[-1]['id'])
            phase['synthetic_review_at'] = now()
        tsep.require(edge.scope_error is None and origin.scope_error is None, 'Server scope failure')
        remaining = (tsep.timestamp(end)-datetime.now(timezone.utc)).total_seconds()
        if remaining > 0: time.sleep(remaining)
    except Exception as error:
        save(root/'failure.json', {'at': now(), 'stage': 'transport', 'type': type(error).__name__, 'error': str(error), 'complete': False})
        raise
    finally:
        for server, thread in threads: server.shutdown(); thread.join(timeout=4)
        for server in (edge, origin):
            if server is not None: server.server_close()
        save(root/'exchanges.json', evidence); save(root/'operations.json', operations)
        save(root/'edge.json', edge.records if edge is not None and hasattr(edge, 'records') else [])
        save(root/'origin.json', origin.records if origin is not None and hasattr(origin, 'records') else [])
    receipt = {'exported_at': now(), 'synthetic_review_at': now(), 'assessed_at': now(), 'collection_complete': True}
    save(root/'receipt.json', receipt)
    try:
        check_capture(reg, evidence, edge.records, origin.records, operations, receipt)
        rows = []; names = list(ROOT_FILES)
        for case, phase in zip(recipe['cases'], evidence['phases']):
            folder = root/case['id']; folder.mkdir(); data = input_for(case, reg, phase, edge.records, evidence['robots'], receipt)
            save(folder/'input.json', data)
            captures.build(folder/'input.json', folder/'bundle', assessor=ASSESSOR,
                label='Fictional site / actual origin-cache HTTP / TS39 '+case['id'], selection_method=SELECTION, access='synthetic', mode='semiAuto')
            rows.append(result_row(case, folder)); names.extend([case['id']+'/input.json', case['id']+'/bundle/SHA256SUMS'])
        result = summary(reg, rows); save(root/'results.json', result)
        tsep.require(source_files == sources(), 'Laboratory sources changed during execution')
        ts01.manifest(root, names); return result
    except Exception as error:
        save(root/'failure.json', {'at': now(), 'stage': 'interpretation', 'type': type(error).__name__, 'error': str(error), 'complete': True})
        raise


def replay(root):
    root = Path(root); source_files = sources(); inventory = ts01.verify(root); recipe = fixture()
    reg = tsep.read_json(root/'registration.json')
    tsep.require(reg.get('kind') == 'delivery-laboratory-registration' and reg.get('version') == VERSION
        and reg.get('synthetic') is True and reg.get('source_files') == source_files, 'Laboratory source or provenance differs')
    names = set(ROOT_FILES)
    names.update(c['id']+'/'+n for c in recipe['cases'] for n in ('input.json', 'bundle/SHA256SUMS'))
    tsep.require(set(inventory) == names, 'Laboratory manifest population differs')
    all_files = names | {'SHA256SUMS'}
    for case in recipe['cases']:
        for name in ts01.verify(root/case['id']/'bundle'):
            all_files.add(case['id']+'/bundle/'+name)
    tsep.require(not any(p.is_symlink() for p in root.rglob('*'))
        and {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == all_files, 'Extra or symlink laboratory files')
    evidence = tsep.read_json(root/'exchanges.json'); receipt = tsep.read_json(root/'receipt.json')
    edge = tsep.read_json(root/'edge.json'); origin = tsep.read_json(root/'origin.json'); operations = tsep.read_json(root/'operations.json')
    check_capture(reg, evidence, edge, origin, operations, receipt)
    final = compact(configurations()[recipe['cases'][-1]['id']])+'\n'
    for layer in ('edge', 'origin'):
        tsep.require((root/(layer+'-configuration.json')).read_text() == final, 'Final active configuration differs')
    rows = []
    for case, phase in zip(recipe['cases'], evidence['phases']):
        folder = root/case['id']; expected = input_for(case, reg, phase, edge, evidence['robots'], receipt)
        tsep.require(expected == tsep.read_json(folder/'input.json') == tsep.read_json(folder/'bundle/input.json'), 'Native input binding differs')
        report = tsep.read_json(folder/'bundle/report.json')
        tsep.require(report['assessor'] == {'name': ASSESSOR, 'mode': 'semiAuto', 'tool': {'name': captures.NAME, 'version': captures.VERSION}}
            and report['scope'] == {'label': 'Fictional site / actual origin-cache HTTP / TS39 '+case['id'],
                'targets': [expected['targets'][0]['url']], 'selection_method': SELECTION, 'exclusions': []}
            and all(a['access'] == 'synthetic' for a in report['artifacts']), 'Synthetic report identity differs')
        with tempfile.TemporaryDirectory() as tmp: bundle_replay.replay(folder/'bundle', Path(tmp)/'replay')
        rows.append(result_row(case, folder))
    tsep.require(summary(reg, rows) == tsep.read_json(root/'results.json'), 'Replayed summary differs')
    tsep.require(source_files == sources(), 'Laboratory sources changed during replay')
    return {'kind': 'controlled-delivery-offline-replay', 'version': VERSION, 'cases': 8,
        'network_requests': 0, 'same_observations_and_results': True, 'scope': SCOPE,
        'all_expectations_matched': all(r['matches_expectations'] for r in rows), 'source_files': source_files, 'runtime': runtime_identity()}


def main():
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest='command', required=True)
    run_parser = sub.add_parser('run'); run_parser.add_argument('--output', type=Path, required=True)
    replay_parser = sub.add_parser('replay'); replay_parser.add_argument('laboratory', type=Path)
    replay_parser.add_argument('--output', type=Path, required=True); args = parser.parse_args()
    try:
        if args.command == 'run': result = run(args.output)
        else:
            tsep.require(not args.output.exists() and not args.output.is_symlink(), 'Choose a NEW replay output')
            result = replay(args.laboratory); save(args.output, result)
        print(json.dumps(result, ensure_ascii=False, indent=2)); return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=False), file=sys.stderr); return 1


if __name__ == '__main__': sys.exit(main())
