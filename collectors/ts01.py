#!/usr/bin/env python3
"""Guided TS01: reference → frozen intent → evaluation → offline replay. Apache-2.0."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib
import json
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import ssl
import subprocess
import sys
import tempfile
import time
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from adapters.captures import build
from conformance.evaluate import trace
from conformance.http import Unknown, body_digest, encoded, header_fields, message, raw_bytes
from collectors.http import request_bytes
from reports.html import write as write_html
from provenance.runtime import loaded_sources

VERSION = '2'
NAME = 'TSEP guided TS01 collector'
RULES = ['TS01-A01', 'TS01-A02']
MAX_TOTAL = 2*1024*1024  # Raw responses per phase; both phases fit input JSON v2.


def collection_sources():
    modules = {'collectors/ts01.py': sys.modules[__name__], 'tsep.py': tsep}
    for name in ('collectors.http', 'conformance.http', 'conformance.evaluate', 'provenance.runtime'):
        modules[name.replace('.', '/')+'.py'] = importlib.import_module(name)
    return loaded_sources(ROOT, modules)


def same_collector(reference):
    tsep.require(reference.get('collector_version') == VERSION and
                 reference.get('sources_unchanged_during_collection') is True and
                 reference.get('source_files') == collection_sources(),
                 'Collector sources differ from reference; retain it and collect a new reference with this version')


def now():
    return datetime.now(timezone.utc).isoformat()


def save(path, data):
    with Path(path).open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write('\n')


def manifest(root, names):
    names = sorted(set(names))
    with (root/'SHA256SUMS').open('x', encoding='utf-8') as handle:
        handle.write(''.join(tsep.digest(root/name)+'  '+name+'\n' for name in names))


def verify(root):
    root = Path(root)
    entries = {}
    for line in (root/'SHA256SUMS').read_text().splitlines():
        fingerprint, name = line.split('  ', 1)
        relative = PurePosixPath(name)
        tsep.require(re.fullmatch('[a-f0-9]{64}', fingerprint) and name not in entries
                     and not relative.is_absolute() and '..' not in relative.parts
                     and relative.as_posix() == name and '\\' not in name, 'Invalid collection manifest')
        path = tsep.evidence_path(root, name)
        tsep.require(tsep.digest(path) == fingerprint, 'Collection integrity mismatch: '+name)
        entries[name] = fingerprint
    return entries


def new_directory(path):
    path = Path(path)
    tsep.require(not path.exists() and not path.is_symlink(), 'Choose a NEW output directory')
    tsep.require(path.parent.is_dir(), 'Output parent directory must exist')
    path.mkdir(mode=0o700)
    return path


def origin(url):
    parts = urlsplit(url)
    tsep.require(parts.scheme in ('http', 'https') and parts.hostname and not parts.username
                 and not parts.password and not parts.fragment and not re.search(r'[\s\x00-\x20\x7f\\]', url),
                 'Expected an anonymous absolute HTTP(S) URL without fragment')
    tsep.require(url.isascii() and len(url) <= 4096, 'Use an ASCII/punycode/percent-encoded URL, at most 4096 characters')
    port = parts.port or (443 if parts.scheme == 'https' else 80)
    return (parts.scheme, parts.hostname.lower(), port)


def validate_settings(settings):
    tsep.require(isinstance(settings, dict) and set(settings) == {'urls', 'origins', 'agent', 'accept_encoding',
                 'timeout', 'max_bytes', 'max_redirects', 'allow_loopback', 'network', 'selection_method', 'access'},
                 'Invalid collector settings')
    urls = settings['urls']
    tsep.require(isinstance(urls, list) and 1 <= len(urls) <= 10 and all(isinstance(u, str) for u in urls), 'Select 1–10 explicit URLs')
    tsep.unique(urls, 'collector target')
    allowed = settings['origins']
    tsep.require(isinstance(allowed, list) and 1 <= len(allowed) <= 20, 'Declare allowed origins')
    origins = {origin(u) for u in allowed}
    tsep.require(all(origin(u) in origins for u in urls), 'Target outside allowed origins')
    tsep.require(settings['accept_encoding'] in ('identity', 'gzip, deflate'), 'Accept-Encoding must be identity or gzip, deflate')
    tsep.require(type(settings['timeout']) in (float, int) and .1 <= settings['timeout'] <= 30, 'Timeout must be 0.1–30 seconds per hop')
    tsep.require(type(settings['max_bytes']) is int and 1024 <= settings['max_bytes'] <= 1024*1024, 'Response bound must be 1 KiB–1 MiB')
    tsep.require(type(settings['max_redirects']) is int and 0 <= settings['max_redirects'] <= 5, 'Redirect bound must be 0–5')
    tsep.require(type(settings['allow_loopback']) is bool, 'Explicit loopback setting required')
    tsep.require(settings['access'] in ('public', 'restricted', 'synthetic'), 'Declare evidence access')
    for key in ('agent', 'network', 'selection_method'):
        tsep.require(isinstance(settings[key], str) and settings[key].strip() and len(settings[key]) <= 1000, 'Declare '+key)
    tsep.require(settings['agent'].isascii() and not re.search(r'[\x00-\x1f\x7f]', settings['agent']), 'Invalid User-Agent')
    return settings


def capture(settings, output):
    """Retain every attempt, including partial responses and out-of-scope redirects."""
    validate_settings(settings)
    sources = collection_sources()
    started, timer = now(), time.monotonic()
    output.mkdir()
    names, targets, total = [], [], 0
    allowed = {origin(u) for u in settings['origins']}
    for number, url in enumerate(settings['urls'], 1):
        target = {'url': url, 'started_at': now(), 'http': []}
        current = url
        for hop_index in range(settings['max_redirects']+1):
            if origin(current) not in allowed:
                target['collection_error'] = 'Redirect outside declared origins; destination not fetched'
                break
            if total >= MAX_TOTAL:
                target['collection_error'] = 'Phase byte bound reached; no further request'
                break
            config = {key: settings[key] for key in ('agent', 'accept_encoding', 'timeout', 'max_bytes', 'allow_loopback')}
            config.update(url=current, max_bytes=min(config['max_bytes'], MAX_TOTAL-total))
            begin = now()
            with tempfile.TemporaryDirectory(prefix='tsep-http-') as folder:
                config['directory'] = folder
                metadata = {'started_at': begin, 'complete': False}
                try:
                    run = subprocess.run([sys.executable, str(ROOT/'collectors/http.py')],
                                         input=json.dumps(config), text=True, capture_output=True,
                                         timeout=settings['timeout']+1)
                    if (Path(folder)/'metadata.json').exists():
                        metadata = tsep.read_json(Path(folder)/'metadata.json')
                    if run.returncode:
                        metadata.update(complete=False, error='Worker failed: '+run.stderr[-1000:])
                except subprocess.TimeoutExpired:
                    metadata.update(complete=False, error='Supervisor deadline reached (including DNS)')
                metadata['finished_at'] = now()
                req = request_bytes(current, settings['agent'], settings['accept_encoding'])
                response_file = Path(folder)/'response.bin'
                response = response_file.read_bytes() if response_file.exists() else b''
            total += len(response)
            stem = 'target-'+str(number)+'-hop-'+str(hop_index+1)
            for suffix, raw in (('request.bin', req), ('response.bin', response)):
                name = stem+'-'+suffix
                (output/name).write_bytes(raw)
                names.append(name)
            hop = dict(metadata, url=current, request=encoded(req), response=encoded(response))
            target['http'].append(hop)
            if not metadata['complete']:
                break
            try:
                status, headers, _ = message(hop['response'], True)
                if status in (301, 302, 303, 307, 308):
                    locations = headers.get('location', [])
                    if len(locations) != 1 or not locations[0]:
                        raise Unknown('Missing or ambiguous Location')
                    destination = urljoin(current, locations[0])
                    origin(destination)
                    if urlsplit(current).scheme == 'https' and urlsplit(destination).scheme != 'https':
                        raise Unknown('HTTPS downgrade redirect refused')
                    if hop_index == settings['max_redirects']:
                        raise Unknown('Redirect bound reached; next hop not fetched')
                    current = destination
                    continue
            except ValueError as error:
                target['collection_error'] = str(error)
            break
        target['observed_at'] = now()
        try:
            final, status, headers, body = trace(target['http'], url, settings['agent'])
            target['reference_candidate'] = {'expected_final_url': final, 'expected_body_sha256': body_digest(body), 'status': status}
        except (ValueError, KeyError, TypeError) as error:
            target['interpretation_limit'] = str(error)
        targets.append(target)
    result = {'collector_version': VERSION, 'started_at': started, 'finished_at': now(),
              'seconds': round(time.monotonic()-timer, 3), 'settings': settings,
              'phase_response_bytes': total, 'phase_response_byte_limit': MAX_TOTAL,
              'environment': {'python': platform.python_version(), 'platform': platform.platform(), 'openssl': ssl.OPENSSL_VERSION},
              'source_files': sources,
              'sources_unchanged_during_collection': collection_sources() == sources,
              'targets': targets}
    save(output/'capture.json', result)
    manifest(output, names+['capture.json'])
    tsep.require(result['sources_unchanged_during_collection'],
                 'Collector source files changed during collection; raw attempts retained, no assessment emitted')
    return result


def reference(settings, output):
    validate_settings(settings)
    output = new_directory(output)
    collected = capture(settings, output/'reference')
    # The phase is immutable; its own manifest is the seal's fingerprint anchor.
    return {'reference': str(output/'reference'),
            'candidates': [{'url': t['url'], 'candidate': t.get('reference_candidate'),
                            'limit': t.get('interpretation_limit', t.get('collection_error'))} for t in collected['targets']],
            'eligible_for_seal': all(t.get('reference_candidate', {}).get('status') == 200 for t in collected['targets']),
            'next': 'Review retained references, then seal: choose digest, stable or explicit markers before evaluation'}


def seal(reference_dir, output, *, assessor, label, policy='digest', criteria=None):
    verify(reference_dir)
    ref = tsep.read_json(Path(reference_dir)/'capture.json')
    same_collector(ref)
    validate_settings(ref['settings'])
    tsep.require([t['url'] for t in ref['targets']] == ref['settings']['urls'], 'Reference target scope mismatch')
    tsep.require(policy in ('digest', 'stable', 'markers'), 'Unknown identity policy')
    criteria = criteria or {}
    tsep.require(isinstance(criteria, dict) and set(criteria) <= set(ref['settings']['urls']), 'Unknown criteria target')
    declared = now()
    rows = []
    for target in ref['targets']:
        tsep.require(tsep.timestamp(target['observed_at']) <= tsep.timestamp(declared), 'Reference date is in the future')
        final, status, headers, body = trace(target['http'], target['url'], ref['settings']['agent'])
        candidate = {'expected_final_url': final, 'expected_body_sha256': body_digest(body), 'status': status}
        tsep.require(candidate == target.get('reference_candidate'), 'Reference summary does not match retained bytes')
        tsep.require(candidate.get('status') == 200, 'Cannot seal incomplete/non-200 reference: '+target['url'])
        options = criteria.get(target['url'], {'policy': policy})
        tsep.require(isinstance(options, dict) and set(options) <= {'policy', 'required_markers', 'forbidden_markers', 'expected_final_url'}, 'Invalid identity criteria')
        choice = options.get('policy', policy)
        tsep.require(choice in ('digest', 'stable', 'markers'), 'Unknown identity policy')
        declared_final = options.get('expected_final_url')
        if declared_final is not None:
            origin(declared_final)
            tsep.require(declared_final == final, 'Declared final URL differs from captured reference; seal refused')
        intent = {'declared_at': declared, 'public_canonical': True, 'crawler': ref['settings']['agent'],
                  'expected_final_url': candidate['expected_final_url'], 'expected_body_sha256': candidate['expected_body_sha256']}
        if choice == 'stable':
            intent['representation'] = 'stable'
        if choice == 'markers':
            required, forbidden = options.get('required_markers', []), options.get('forbidden_markers', [])
            tsep.require(isinstance(required, list) and required and isinstance(forbidden, list), 'Markers require a positive required marker')
            for values in (required, forbidden):
                tsep.require(all(isinstance(v, str) and v.strip() for v in values) and len(values) == len(set(values)), 'Invalid/duplicate markers')
            tsep.require(not any(bad in good for good in required for bad in forbidden), 'Contradictory markers')
            intent.update(required_markers=required, forbidden_markers=forbidden)
        else:
            tsep.require(not options.get('required_markers') and not options.get('forbidden_markers'), 'Markers require markers policy')
        rows.append({'url': target['url'], 'intent': intent,
                     'identity_basis': {'origin': 'operator-final-url' if declared_final is not None else 'reference-adopted',
                                        'policy': choice, 'body_reference': 'captured-reference',
                                        'declared_final_url': declared_final}})
    value = {'intent_version': '2', 'declared_at': declared, 'reference_manifest_sha256': tsep.digest(Path(reference_dir)/'SHA256SUMS'),
             'reference_source_files': ref['source_files'],
             'assessor': assessor, 'label': label, 'settings': ref['settings'], 'targets': rows,
             'meaning': 'Operator-selected prior criteria from retained references; no trusted timestamp or correctness certification.'}
    tsep.require(all(isinstance(x, str) and x.strip() for x in (assessor, label)), 'Declare assessor and label')
    save(output, value)
    return {'intent': str(output), 'sha256': tsep.digest(Path(output)), 'next': 'evaluate with this unchanged reference and intent',
            'stable_policy_warning': 'Explicit stable policy: any decoded body change, including a nonce or timestamp, fails TS01-A02.'
                                     if any(row['identity_basis']['policy'] == 'stable' for row in rows) else None}


def evaluate(reference_dir, intent_path, output, language='fr'):
    verify(reference_dir)
    reference_dir, intent_path = Path(reference_dir), Path(intent_path)
    ref, intent = tsep.read_json(reference_dir/'capture.json'), tsep.read_json(intent_path)
    same_collector(ref)
    tsep.require(intent['intent_version'] == '2' and intent['reference_manifest_sha256'] == tsep.digest(reference_dir/'SHA256SUMS'), 'Intent/reference binding mismatch; use this collector version to create a new reference and intent')
    tsep.require(intent.get('reference_source_files') == ref['source_files'], 'Intent collector sources differ from reference')
    tsep.require(intent['settings'] == ref['settings'], 'Request settings changed after reference')
    validate_settings(intent['settings'])
    tsep.require([t['url'] for t in ref['targets']] == ref['settings']['urls'], 'Reference target scope mismatch')
    tsep.require([t['url'] for t in intent['targets']] == ref['settings']['urls'], 'Intent target scope changed')
    started = now()
    tsep.require(tsep.timestamp(intent['declared_at']) <= tsep.timestamp(started), 'Intent is in the future')
    tsep.require(tsep.timestamp(ref['finished_at']) <= tsep.timestamp(intent['declared_at']), 'Intent predates reference completion')
    for row in intent['targets']:
        tsep.require(row['intent']['declared_at'] == intent['declared_at'], 'Inconsistent intent dates')
        tsep.require(row['intent']['crawler'] == intent['settings']['agent'], 'Intent crawler differs from frozen request settings')
        basis = row.get('identity_basis', {})
        actual_policy = ('stable' if row['intent'].get('representation') == 'stable' else
                         'markers' if row['intent'].get('required_markers') else 'digest')
        tsep.require(basis.get('policy') == actual_policy and basis.get('origin') in ('reference-adopted', 'operator-final-url'),
                     'Identity basis does not match frozen criteria')
        tsep.require(basis.get('origin') != 'operator-final-url' or
                     basis.get('declared_final_url') == row['intent']['expected_final_url'], 'Declared final URL does not match intent')
    output = new_directory(output)
    shutil.copyfile(intent_path, output/'intent.json')
    observations = capture(intent['settings'], output/'evaluation')
    tsep.require(observations['source_files'] == ref['source_files'],
                 'Collector sources changed between phases; raw evaluation retained without assessment')
    targets = []
    for prior, criteria, observation in zip(ref['targets'], intent['targets'], observations['targets']):
        target = dict(observation)
        target['intent'] = criteria['intent']
        target['reference'] = {'observed_at': prior['observed_at'], 'http': prior['http'],
                               'source_files': ref['source_files'],
                               'reference_manifest_sha256': intent['reference_manifest_sha256']}
        target['context'] = {'network': intent['settings']['network'], 'bounds': {k: intent['settings'][k] for k in
                              ('timeout', 'max_bytes', 'max_redirects', 'origins', 'allow_loopback')},
                             'tool': NAME, 'tool_version': VERSION, 'accept_encoding': intent['settings']['accept_encoding'],
                             'collection_environment': observations['environment'], 'collection_source_files': observations['source_files'],
                             'collector_matches_reference': True, 'identity_basis': criteria['identity_basis'],
                             'run_selection': 'Only the supplied runs; this bundle does not establish an exhaustive campaign history.',
                             'intent_file_sha256': tsep.digest(output/'intent.json'), 'reference_manifest_sha256': intent['reference_manifest_sha256']}
        targets.append(target)
    data = {'input_version': '2', 'rules': RULES, 'targets': targets}
    save(output/'input.json', data)
    settings = intent['settings']
    summary = build(output/'input.json', output/'bundle', assessor=intent['assessor'], label=intent['label'],
                    selection_method=settings['selection_method'], access=settings['access'], mode='automatic',
                    exclusions=['TS02–TS44 not assessed; no site-wide conformity, indexing or ranking claim'])
    write_html(output/'bundle/report.json', output/('report-'+language+'.html'), language=language)
    # Explicit inventories only. The complete input already retains prior raw HTTP.
    names = ['intent.json', 'input.json', 'report-'+language+'.html', 'bundle/SHA256SUMS', 'evaluation/SHA256SUMS']
    names += ['bundle/'+n for n in verify(output/'bundle')]
    names += ['evaluation/'+n for n in verify(output/'evaluation')]
    manifest(output, names)
    return summary


def replay(source, output, language='fr'):
    """Recompute from retained input only, without collecting or refreezing intent."""
    source = Path(source)
    verify(source)
    report = tsep.read_json(source/'bundle/report.json')
    intent = tsep.read_json(source/'intent.json')
    output = new_directory(output)
    summary = build(source/'input.json', output/'bundle', assessor=report['assessor']['name'], label=report['scope']['label'],
                    selection_method=report['scope']['selection_method'], access=intent['settings']['access'],
                    mode=report['assessor']['mode'], selected=report['controls'], exclusions=report['scope']['exclusions'])
    same = (tsep.read_json(output/'bundle/assessment.json') == tsep.read_json(source/'bundle/assessment.json')
            and summary == tsep.read_json(source/'bundle/gate.json'))
    same_tools = (tsep.read_json(output/'bundle/import.json')['source_files'] ==
                  tsep.read_json(source/'bundle/import.json')['source_files'])
    save(output/'replay.json', {'same_atomic_observations_and_gate': same, 'input_sha256': tsep.digest(source/'input.json'),
                              'same_interpreter_adapter_sources': same_tools,
                              'network_requests': 0, 'scope': 'Same tool/protocol and retained input; no new collection'})
    tsep.require(same and same_tools, 'Replay outcomes or tool sources differ; retained output requires examination')
    write_html(output/'bundle/report.json', output/('report-'+language+'.html'), language=language)
    return {'replayed': True, 'decision': summary['decision'], 'output': str(output)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    ref = sub.add_parser('reference', help='Collect explicit authorized targets; real network requests')
    ref.add_argument('--target', action='append', required=True)
    ref.add_argument('--allow-origin', action='append', default=[])
    ref.add_argument('--agent', default='TSEP-TS01-collector/2')
    ref.add_argument('--accept-encoding', choices=['identity', 'gzip, deflate'], default='gzip, deflate')
    ref.add_argument('--timeout', type=float, default=10)
    ref.add_argument('--max-bytes', type=int, default=524288)
    ref.add_argument('--max-redirects', type=int, default=3)
    ref.add_argument('--allow-loopback', action='store_true')
    ref.add_argument('--network', required=True)
    ref.add_argument('--selection-method', required=True)
    ref.add_argument('--access', required=True, choices=['public', 'restricted', 'synthetic'])
    ref.add_argument('--output', type=Path, required=True)
    frozen = sub.add_parser('seal', help='Accept references and freeze identity criteria, without a request')
    frozen.add_argument('--reference', type=Path, required=True)
    frozen.add_argument('--output', type=Path, required=True)
    frozen.add_argument('--assessor', required=True)
    frozen.add_argument('--label', required=True)
    frozen.add_argument('--policy', choices=['digest', 'stable', 'markers'], default='digest')
    frozen.add_argument('--criteria', type=Path, help='Per-URL policy and required/forbidden markers JSON')
    for name in ('evaluate', 'replay'):
        command = sub.add_parser(name)
        command.add_argument('--output', type=Path, required=True)
        command.add_argument('--lang', choices=['fr', 'en'], default='fr')
        if name == 'evaluate':
            command.add_argument('--reference', type=Path, required=True)
            command.add_argument('--intent', type=Path, required=True)
        else:
            command.add_argument('source', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'reference':
            settings = {'urls': args.target, 'origins': list(dict.fromkeys(args.target+args.allow_origin)),
                        'agent': args.agent, 'accept_encoding': args.accept_encoding, 'timeout': args.timeout,
                        'max_bytes': args.max_bytes, 'max_redirects': args.max_redirects, 'allow_loopback': args.allow_loopback,
                        'network': args.network, 'selection_method': args.selection_method, 'access': args.access}
            result = reference(validate_settings(settings), args.output)
        elif args.command == 'seal':
            result = seal(args.reference, args.output, assessor=args.assessor, label=args.label, policy=args.policy,
                          criteria=tsep.read_json(args.criteria) if args.criteria else None)
        elif args.command == 'evaluate':
            result = evaluate(args.reference, args.intent, args.output, args.lang)
        else:
            result = replay(args.source, args.output, args.lang)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0  # Workflow success is separate from `tsep.py gate` policy exits.
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(json.dumps({'valid': False, 'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 64


if __name__ == '__main__':
    sys.exit(main())
