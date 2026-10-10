#!/usr/bin/env python3
"""TS07 change/correction laboratory: synthetic site, actual loopback HTTP, offline replay.

Apache-2.0. Existing draft.7 decisions; no invented DOM, access review or C.
"""
import argparse
import copy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from adapters import captures
from collectors import ts01
from conformance import evaluate as evaluator
from conformance.http import body_digest, text_body
from diagnostics import campaign
from experiments import seo_signals, noscript
from provenance.runtime import loaded_sources, runtime_identity

VERSION = '1'
FIXTURE = 'tests/fixtures/ts07-laboratory-cases.json'
FREEZE = 'tests/fixtures/ts07-laboratory-freeze.sha256'
RULES = ['TS07-A01', 'TS07-A02', 'TS07-A03']
ASSESSOR = 'Automated synthetic laboratory; no human review'
SCOPE = ('Synthetic laboratory site; actual loopback HTTP captures. No Edikka observation, '
         'browser execution, access review, engine visit, indexing or deployment clearance. '
         'NT after correction is retained. Source inventories are experimental, never decision inputs.')


def sources():
    result = ts01.collection_sources()
    result.update(captures.source_files())
    result.update(loaded_sources(ROOT, {'examples/ts07_laboratory.py': sys.modules[__name__],
                  'diagnostics/campaign.py': campaign, 'experiments/seo_signals.py': seo_signals,
                  'experiments/noscript.py': noscript}))
    for name in (FIXTURE, FREEZE, 'spec/protocol.json', 'schemas/report.schema.json'):
        result[name] = tsep.digest(ROOT/name)
    return result


def fixture():
    tsep.require(tsep.digest(ROOT/FIXTURE) == (ROOT/FREEZE).read_text().strip(), 'Frozen fixture mismatch')
    return tsep.read_json(ROOT/FIXTURE)


def semantic(value):
    if isinstance(value, dict):
        return {k: semantic(v) for k, v in value.items() if k != 'runtime'}
    if isinstance(value, list):
        return [semantic(v) for v in value]
    return value


def settings(base):
    return {'urls': [base+'/robots.txt', base+'/page'], 'origins': [base], 'agent': 'googlebot',
            'accept_encoding': 'identity', 'timeout': 2, 'max_bytes': 16384, 'max_redirects': 0,
            'allow_loopback': True, 'network': 'Synthetic site on 127.0.0.1 only', 'access': 'synthetic',
            'selection_method': 'Prefrozen TS07 laboratory sequence, not a representative site sample'}


def intents(declared):
    return {mode: {'declared_at': declared, 'public_canonical': True, 'crawler': 'googlebot',
                   'indexing': mode, 'following': 'unspecified', 'access_basis': 'test-client-only',
                   'rendering': {'mode': 'required', 'required_states': [
                       {'id': 'loaded', 'interactions': [], 'wait': 'load + 1000 ms; planned, not performed'}]}}
            for mode in ('allow', 'exclude')}


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, *args):
        pass

    def do_GET(self):
        case = self.server.case
        self.server.requests.append({'case': case['id'], 'path': self.path,
                                     'agent': self.headers.get('User-Agent')})
        if self.path == '/robots.txt':
            body, status, kind, extra = case['robots_body'], case['robots_status'], 'text/plain', []
        elif self.path == '/page':
            body, status, kind, extra = case['page_body'], 200, 'text/html', case['page_headers']
        else:
            body, status, kind, extra = 'Outside laboratory scope', 404, 'text/plain', []
        raw = body.encode('utf-8')
        self.send_response_only(status)
        self.send_header('Content-Type', kind+'; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Connection', 'close')
        for name, value in extra:
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(raw)


def stop_server(server, thread):
    if thread.is_alive():
        server.shutdown()
    server.server_close()
    thread.join()


def capture_input(phase, registration, case):
    robots, page = phase['targets']
    target = copy.deepcopy(page)
    target.update(intent=copy.deepcopy(registration['intents'][case['indexing']]),
                  robots={'observed_at': robots['observed_at'], 'http': copy.deepcopy(robots['http'])},
                  context={'id': 'synthetic-ts07-'+case['id'], 'network': phase['settings']['network'],
                           'bounds': {k: phase['settings'][k] for k in ('timeout', 'max_bytes', 'max_redirects')},
                           'tool': 'TS07 synthetic laboratory using TSEP HTTP collector',
                           'tool_version': VERSION, 'collector_version': ts01.VERSION,
                           'agent_scope': 'Literal googlebot request header, not an authenticated engine',
                           'access_review': 'Not performed', 'render_capture': 'Not performed'})
    return {'input_version': '2', 'rules': list(RULES), 'targets': [target]}


def observe(data):
    target = data['targets'][0]
    result = {'http_available': False, 'lexical_inventory': None}
    try:
        url, status, headers, body = evaluator.trace(target['http'], target['url'], 'googlebot')
        result.update(http_available=True, url=url, status=status,
                      decoded_body_sha256=body_digest(body), x_robots_tag=headers.get('x-robots-tag', []),
                      lexical_inventory=seo_signals.experiment(text_body(body)))
    except (ValueError, KeyError, TypeError) as error:
        result['reason'] = str(error)
    return result


def check_phase(phase, registration, previous_finish):
    tsep.require(phase['settings'] == registration['settings'], 'Registered collection settings mismatch')
    ts01.same_collector(phase)
    tsep.require(phase['source_files'] == {k: registration['source_files'][k] for k in phase['source_files']},
                 'Registered collector sources mismatch')
    stamp = tsep.timestamp
    start, finish = stamp(phase['started_at']), stamp(phase['finished_at'])
    tsep.require(stamp(previous_finish) <= start <= finish, 'Invalid phase chronology')
    tsep.require([t['url'] for t in phase['targets']] == registration['settings']['urls'], 'Captured URL order mismatch')
    prior = start
    for target in phase['targets']:
        begin, end = stamp(target['started_at']), stamp(target['observed_at'])
        tsep.require(prior <= begin <= end <= finish, 'Invalid target chronology')
        for hop in target['http']:
            tsep.require(begin <= stamp(hop['started_at']) <= stamp(hop['finished_at']) <= end, 'Invalid hop chronology')
            if 'peer_address' in hop or hop.get('complete') is True:
                tsep.require(hop.get('peer_address') == '127.0.0.1', 'Recorded peer is not laboratory loopback')
        prior = end


def check_requests(requests, plan):
    expected = [{'case': c['id'], 'path': path, 'agent': 'googlebot'}
                for c in plan['cases'] for path in ('/robots.txt', '/page')]
    tsep.require(requests == expected, 'Laboratory request scope mismatch')


def row(case, bundle, observation, initial_body):
    atoms = tsep.read_json(bundle/'assessment.json')
    report = tsep.read_json(bundle/'report.json')
    actual = {'atomic_outcomes': [a['outcome'] for a in atoms], 'control_status': report['results'][0]['status'],
              'inventory_comparison': (observation['lexical_inventory'] or {}).get('inventory_comparison', 'unavailable'),
              'body_equals_initial': observation.get('decoded_body_sha256') == initial_body if initial_body else None}
    return {'id': case['id'], 'label': case['label'], 'intent_series': case['indexing'], 'actual': actual,
            'expected': case['expected'], 'matches_expectations': actual == case['expected'],
            'atomic_results': atoms, 'observation': observation,
            'report': case['id']+'/bundle/report.json', 'input': case['id']+'/input.json'}


def summary(registration, rows):
    return {'kind': 'synthetic-ts07-change-laboratory', 'version': VERSION, 'scope': SCOPE,
            'protocol_version': tsep.read_json(ROOT/'spec/protocol.json')['version'],
            'source_files': registration['source_files'], 'runtime': runtime_identity(),
            'registered_at': registration['registered_at'], 'cases': rows,
            'all_expectations_matched': all(r['matches_expectations'] for r in rows),
            'normative_change': 'none', 'human_review_performed': False, 'browser_executed': False}


def reading_note(result):
    lines = ['Laboratoire TS07 — site synthétique, captures HTTP locales',
             'Problème introduit → contradiction NC → correction avec preuves encore partielles NT', '',
             'Le code source ne suffit pas : header-noindex conserve le même HTML que initial,',
             'mais ajoute X-Robots-Tag: noindex dans la réponse HTTP.',
             'A01 = directives source ; A02 = accès ; A03 = états rendus.',
             'Aucune capture navigateur ni revue humaine d’accès : aucune conclusion C.',
             'Le client envoie User-Agent: googlebot uniquement en loopback ; il n’est pas Googlebot.',
             'L’objectif exclude est une série distincte, déclarée avant toute capture.', '',
             'Cas | A01 / A02 / A03 | TS07 | Attente vérifiée']
    for item in result['cases']:
        value = item['actual']
        lines += [item['id']+' | '+' / '.join(value['atomic_outcomes'])+' | '+value['control_status']+
                  ' | '+str(item['matches_expectations']), '  '+item['label']['fr'],
                  '  Rapport : '+item['report']]
        lines += ['  '+a['rule_id']+' : '+a['reason'] for a in item['atomic_results']]
    lines += ['', 'Ces résultats portent sur ce laboratoire ; aucun résultat Edikka ou effet Google.',
              'Un rejeu identique démontre la reproductibilité de ce calcul, pas sa validation indépendante.',
              'Rejouer : python3 examples/ts07_laboratory.py replay CHEMIN_DU_LABO --output NOUVEAU.json',
              'Les empreintes et dates locales détectent des incohérences ; elles ne sont pas une signature.', '']
    return '\n'.join(lines)


def run(output):
    plan, before = fixture(), sources()
    output = ts01.new_directory(output)
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    server.daemon_threads, server.requests = True, []
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = 'http://127.0.0.1:'+str(server.server_port)
        declared = ts01.now()
        registration = {'kind': 'ts07-laboratory-registration', 'version': VERSION, 'registered_at': declared,
                        'synthetic': True, 'plan': plan, 'settings': settings(base), 'intents': intents(declared),
                        'source_files': before, 'scope': SCOPE}
        ts01.save(output/'registration.json', registration)
        rows, names, initial_body = [], ['registration.json'], None
        previous = declared
        for case in plan['cases']:
            tsep.require(sources() == before, 'Laboratory sources changed before collection')
            folder = output/case['id']; folder.mkdir()
            server.case = case
            ts01.capture(registration['settings'], folder/'capture')
            phase, _ = campaign.phase(folder/'capture')
            check_phase(phase, registration, previous); previous = phase['finished_at']
            data = capture_input(phase, registration, case)
            ts01.save(folder/'input.json', data)
            observation = observe(data)
            ts01.save(folder/'observations.json', observation)
            captures.build(folder/'input.json', folder/'bundle', assessor=ASSESSOR,
                           label='SYNTHETIC TS07 / '+case['id'], selection_method=registration['settings']['selection_method'],
                           access='synthetic', mode='automatic', selected=['TS07'])
            if not rows:
                initial_body = observation.get('decoded_body_sha256')
            rows.append(row(case, folder/'bundle', observation, initial_body))
            ts01.manifest(folder, ['input.json', 'observations.json', 'capture/SHA256SUMS', 'bundle/SHA256SUMS'])
            names.append(case['id']+'/SHA256SUMS')
        stop_server(server, thread)
        tsep.require(sources() == before, 'Laboratory sources changed during collection')
        ts01.save(output/'requests.json', server.requests)
        check_requests(server.requests, plan)  # Retain the log even on mismatch; never emit a success summary.
        result = summary(registration, rows)
        ts01.save(output/'results.json', result)
        (output/'README-fr.txt').write_text(reading_note(result), encoding='utf-8')
        ts01.manifest(output, names+['requests.json', 'results.json', 'README-fr.txt'])
        return result
    finally:
        stop_server(server, thread)


def replay(root):
    root, before = Path(root), sources()
    manifest = ts01.verify(root)
    registration = tsep.read_json(root/'registration.json')
    plan = fixture()
    tsep.require(registration.get('kind') == 'ts07-laboratory-registration' and registration.get('version') == VERSION
                 and registration.get('synthetic') is True, 'Invalid laboratory registration')
    tsep.require(registration['source_files'] == before and registration['plan'] == plan, 'Laboratory source/plan mismatch')
    declared = registration['registered_at']
    tsep.require(registration['intents'] == intents(declared), 'Registered intents mismatch')
    base = registration['settings']['origins'][0]
    tsep.require(ts01.origin(base)[:2] == ('http', '127.0.0.1') and
                 registration['settings'] == settings(base), 'Invalid loopback registration')
    expected_names = {'registration.json', 'requests.json', 'results.json', 'README-fr.txt'}
    expected_names.update(c['id']+'/SHA256SUMS' for c in plan['cases'])
    tsep.require(set(manifest) == expected_names, 'Incomplete laboratory manifest')
    check_requests(tsep.read_json(root/'requests.json'), plan)
    rows, initial_body, previous = [], None, declared
    for case in plan['cases']:
        folder = root/case['id']
        tsep.require(set(ts01.verify(folder)) == {'input.json', 'observations.json', 'capture/SHA256SUMS', 'bundle/SHA256SUMS'},
                     'Incomplete scenario manifest')
        phase, _ = campaign.phase(folder/'capture')
        check_phase(phase, registration, previous); previous = phase['finished_at']
        data = capture_input(phase, registration, case)
        tsep.require(data == tsep.read_json(folder/'input.json'), 'Capture/input binding mismatch')
        ts01.verify(folder/'bundle')
        tsep.require(data == tsep.read_json(folder/'bundle/input.json'), 'Bundle input mismatch')
        imported = tsep.read_json(folder/'bundle/import.json')
        tsep.require(imported['source_files'] == captures.source_files() and imported['access'] == 'synthetic'
                     and imported['input_sha256'] == tsep.digest(folder/'input.json'), 'Bundle provenance mismatch')
        atoms = evaluator.evaluate(data)
        tsep.require(atoms == tsep.read_json(folder/'bundle/assessment.json'), 'Replayed atomic results differ')
        report = tsep.read_json(folder/'bundle/report.json')
        tsep.require(report['scope'] == {'label': 'SYNTHETIC TS07 / '+case['id'],
                     'targets': [data['targets'][0]['url']],
                     'selection_method': registration['settings']['selection_method'], 'exclusions': []}
                     and report['assessor'] == {'name': ASSESSOR, 'mode': 'automatic',
                     'tool': {'name': captures.NAME, 'version': captures.VERSION}}
                     and all(a['access'] == 'synthetic' for a in report['artifacts']),
                     'Synthetic report identity mismatch')
        gate = tsep.validate(report, folder/'bundle')
        tsep.require(gate == tsep.read_json(folder/'bundle/gate.json'), 'Replayed report/gate differs')
        declared_atoms = [{k:v for k,v in a.items() if k != 'evidence_ids'} for a in report['results'][0]['atomic_results']]
        tsep.require(declared_atoms == atoms and report['assessor']['mode'] == 'automatic', 'Report atomic binding mismatch')
        observation = observe(data)
        tsep.require(semantic(observation) == semantic(tsep.read_json(folder/'observations.json')), 'Replayed lexical observations differ')
        if not rows:
            initial_body = observation.get('decoded_body_sha256')
        rows.append(row(case, folder/'bundle', observation, initial_body))
    result = summary(registration, rows)
    retained = tsep.read_json(root/'results.json')
    tsep.require(semantic(result) == semantic(retained), 'Replayed laboratory summary differs')
    tsep.require((root/'README-fr.txt').read_text() == reading_note(result), 'Reading note differs')
    tsep.require(sources() == before, 'Laboratory sources changed during replay')
    return {'kind': 'ts07-laboratory-offline-replay', 'version': VERSION,
            'same_observations_and_results': True, 'same_recorded_runtime': result['runtime'] == retained['runtime'],
            'network_requests': 0, 'cases': len(rows), 'all_expectations_matched': result['all_expectations_matched'],
            'source_files': before, 'runtime': runtime_identity(), 'scope': SCOPE}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    run_parser = sub.add_parser('run')
    run_parser.add_argument('--output', type=Path, required=True)
    replay_parser = sub.add_parser('replay')
    replay_parser.add_argument('laboratory', type=Path)
    replay_parser.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    try:
        if args.command == 'run':
            value = run(args.output)
        else:
            tsep.require(not args.output.exists() and not args.output.is_symlink(), 'Choose a NEW replay output')
            value = replay(args.laboratory); ts01.save(args.output, value)
        print(json.dumps({k:v for k,v in value.items() if k not in ('cases', 'source_files', 'runtime')}, ensure_ascii=False))
        return 0 if value['all_expectations_matched'] else 2
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({'kind': 'ts07-laboratory-error', 'error': str(error)}), file=sys.stderr)
        return 64


if __name__ == '__main__':
    sys.exit(main())
