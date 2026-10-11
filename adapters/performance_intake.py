#!/usr/bin/env python3
"""Offline native-performance intake, immutable successive packages. Apache-2.0.

Workflow v1 does not change draft.21 verdicts. Local hashes are not signatures;
slot assignment is supplied, and unreported attempts cannot be detected.
"""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re
import sys
import tempfile
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from adapters import captures, package
from adapters.package import inventory, json_bytes, publish, regular, seal
from conformance import performance
from provenance.runtime import loaded_sources

VERSION = '1'
NATIVE_LIMIT = 4 * 1024 * 1024
RULES = {'field': ['TS34-A01', 'TS34-A02', 'TS34-A03'], 'lab': ['TS35-A01', 'TS35-A02']}
LIMITS = [
    'Affectation des passages déclarée par l’opérateur / Operator-declared slot assignment.',
    'Passages non fournis indétectables / Unreported attempts cannot be detected.',
    'Un ancien dossier peut servir à créer une autre branche ; aucun registre global / An old package can start another branch; no global journal.',
    'Configuration déclarée ; comparabilité de la machine non qualifiée / Declared settings; host comparability unqualified.',
    'Dates locales et empreintes non authentifiées / Local timestamps and hashes are not authenticated.',
    'Pas de conclusion avant/après, terrain depuis laboratoire ou classement / No before-after, lab-to-field or ranking conclusion.',
]


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def source_files():
    return dict(captures.source_files(), **loaded_sources(ROOT, {
        'adapters/performance_intake.py': sys.modules[__name__], 'adapters/package.py': package}))


def protocol():
    return {'version': tsep.read_json(tsep.PROTOCOL_PATH)['version'], 'sha256': tsep.digest(tsep.PROTOCOL_PATH)}


def text(value, label):
    tsep.require(performance.text(value), 'Supply '+label)


def url(value):
    text(value, 'HTTP(S) URL')
    parsed = urlsplit(value)
    tsep.require(parsed.scheme in ('http', 'https') and parsed.hostname and not parsed.username
                 and not parsed.password and not parsed.fragment and not any(c.isspace() for c in value),
                 'Expected a credential-free HTTP(S) URL without fragment')
    return parsed


def native(path):
    raw = regular(path, NATIVE_LIMIT)
    tsep.require(raw, 'Native file is empty; declare an unavailable slot instead')
    try:
        raw.decode('utf-8')  # Do not strip BOM or normalize newline bytes.
    except UnicodeDecodeError as error:
        raise tsep.Invalid('Only native UTF-8 text is supported; original unchanged') from error
    return raw


def parsed_native(raw):
    try:
        result = tsep.parse_json(raw)
        return result if isinstance(result, dict) else {}
    except (ValueError, TypeError, RecursionError):
        return {}


def write_files(stage, files):
    for name, raw in files.items():
        dest = stage/name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)


def deliver(output, files, sources):
    output = Path(output)
    tsep.require(output.parent.is_dir() and not output.exists() and not output.is_symlink(),
                 'Choose a NEW output directory with an existing parent')
    with tempfile.TemporaryDirectory(prefix='.tsep-performance-', dir=output.parent) as folder:
        stage = Path(folder)
        write_files(stage, files)
        seal(stage)
        inventory(stage)
        tsep.require(source_files() == sources, 'Workflow sources changed during operation')
        publish(stage, output)
    return {'output': str(output), 'manifest_sha256': tsep.digest(output/'SHA256SUMS'),
            'workflow_version': VERSION, 'network_requests': 0}


def plan(output, *, kind, target, operator, access, selection_reason, max_age_days,
         request_file=None, granularity=None, form_factor=None, calibration=None,
         final_url=None, run_count=None):
    sources = source_files()
    created = now()
    url(target)
    text(operator, 'operator'); text(selection_reason, 'selection reason')
    tsep.require(access in captures.ACCESS and kind in RULES, 'Unsupported access or performance kind')
    tsep.require(type(max_age_days) is int and 0 <= max_age_days <= 3660, 'Invalid maximum age')
    files = {}
    if kind == 'field':
        tsep.require(request_file is not None and calibration is None and run_count is None
                     and final_url is None, 'Field plan needs only a native request reference')
        tsep.require(granularity in ('url', 'origin') and form_factor in ('PHONE', 'TABLET', 'DESKTOP', 'ALL'),
                     'Declare field granularity and device')
        if granularity == 'origin':
            parsed = url(target)
            tsep.require(not parsed.path and not parsed.query, 'Origin must have no path or query')
        raw = native(request_file)
        request = tsep.parse_json(raw)
        tsep.require(isinstance(request, dict) and set(request) <= {'url', 'origin', 'formFactor', 'metrics'}
                     and (('url' in request) != ('origin' in request)) and granularity in request,
                     'Supply the original CrUX body without credentials, with matching granularity')
        url(request[granularity])
        tsep.require(request.get('formFactor', 'ALL') == form_factor, 'Request device differs from plan')
        if 'metrics' in request:
            tsep.require(isinstance(request['metrics'], list) and request['metrics']
                         and all(isinstance(m, str) and m in {v[0] for v in performance.FIELD_METRICS.values()}
                                 for m in request['metrics']), 'Unsupported requested field metrics')
        files['reference/request.json'] = raw
        settings = {'granularity': granularity, 'key': target, 'form_factor': form_factor,
                    'max_age_days': max_age_days}
        slots = 1
    else:
        tsep.require(calibration is not None and request_file is None and granularity is None
                     and form_factor is None, 'Lab plan adopts an explicit calibration file')
        url(final_url)
        tsep.require(type(run_count) is int and 2 <= run_count <= 10, 'Declare 2–10 planned lab runs')
        raw = native(calibration)
        data = parsed_native(raw)
        cfg = data.get('configSettings', {})
        env = data.get('environment', {})
        tsep.require(data.get('gatherMode') == 'navigation' and isinstance(cfg, dict)
                     and isinstance(env, dict) and all(k in cfg for k in performance.SETTING_KEYS),
                     'Calibration requires explicit navigation settings and environment')
        version = data.get('lighthouseVersion')
        tsep.require(isinstance(version, str) and re.fullmatch(r'\d+\.\d+\.\d+', version), 'Missing Lighthouse version')
        text(env.get('hostUserAgent'), 'host user agent'); text(env.get('networkUserAgent'), 'network user agent')
        tsep.require(tsep.timestamp(data.get('fetchTime')) <= tsep.timestamp(created), 'Calibration postdates plan')
        tsep.require(cfg.get('formFactor') in ('mobile', 'desktop') and type(cfg.get('disableStorageReset')) is bool
                     and isinstance(cfg.get('throttling'), dict) and isinstance(cfg.get('screenEmulation'), dict)
                     and performance.text(cfg.get('emulatedUserAgent'))
                     and cfg.get('throttlingMethod') in ('simulate', 'devtools', 'provided')
                     and (cfg['blockedUrlPatterns'] is None or isinstance(cfg['blockedUrlPatterns'], list))
                     and (cfg['extraHeaders'] is None or isinstance(cfg['extraHeaders'], dict)),
                     'Unsupported calibration collection context')
        settings = {'requested_url': target, 'final_url': final_url, 'run_count': run_count,
                    'max_age_days': max_age_days, 'form_factor': cfg['formFactor'], 'settings': cfg,
                    'lighthouse_version': version, 'host_user_agent': env['hostUserAgent'],
                    'network_user_agent': env['networkUserAgent']}
        files['reference/calibration.json'] = raw
        slots = run_count
    record = {'kind': 'tsep-performance-plan', 'workflow_version': VERSION,
              'workflow_source_files': sources, 'protocol': protocol(), 'created_at': created,
              'performance_kind': kind, 'target': target, 'operator': operator, 'access': access,
              'selection_reason': selection_reason, 'settings': settings, 'slot_count': slots,
              'references': {name: sha(raw) for name, raw in files.items()}, 'limitations': LIMITS}
    files['plan.json'] = json_bytes(record)
    return deliver(output, files, sources)


def manifest_bytes(files):
    return ''.join(sha(files[name])+'  '+name+'\n' for name in sorted(files)).encode('utf-8')


def session(root):
    root = Path(root)
    entries = inventory(root)
    files = {name: regular(root/name) for name in entries}
    tsep.require({name: sha(raw) for name, raw in files.items()} == entries,
                 'Session files changed while being read')
    plan_data = tsep.parse_json(files['plan.json'])
    tsep.require(plan_data['kind'] == 'tsep-performance-plan' and plan_data['workflow_version'] == VERSION,
                 'Unsupported performance plan')
    tsep.require(plan_data['workflow_source_files'] == source_files() and plan_data['protocol'] == protocol(),
                 'Workflow/protocol changed; use the historical tools')
    tsep.require(set(plan_data) == {'kind', 'workflow_version', 'workflow_source_files', 'protocol',
                 'created_at', 'performance_kind', 'target', 'operator', 'access', 'selection_reason',
                 'settings', 'slot_count', 'references', 'limitations'}
                 and plan_data['access'] in captures.ACCESS and plan_data['limitations'] == LIMITS,
                 'Unsupported plan structure/access/limits')
    url(plan_data['target'])
    text(plan_data['operator'], 'operator'); text(plan_data['selection_reason'], 'selection reason')
    kind = plan_data['performance_kind']
    tsep.require(kind in RULES, 'Unsupported performance kind')
    count = plan_data['slot_count']
    tsep.require(type(count) is int and (count == 1 if kind == 'field' else 2 <= count <= 10), 'Invalid slot count')
    reference = 'reference/'+('request.json' if kind == 'field' else 'calibration.json')
    tsep.require(plan_data['references'] == {reference: entries.get(reference)}, 'Reference binding differs')
    settings = plan_data['settings']
    tsep.require(isinstance(settings, dict) and type(settings.get('max_age_days')) is int
                 and 0 <= settings['max_age_days'] <= 3660, 'Invalid planned age')
    if kind == 'lab':
        calibration = parsed_native(files[reference])
        env = calibration.get('environment', {})
        tsep.require(settings.get('settings') == calibration.get('configSettings')
                     and settings.get('run_count') == count and settings.get('requested_url') == plan_data['target']
                     and settings.get('lighthouse_version') == calibration.get('lighthouseVersion')
                     and settings.get('host_user_agent') == env.get('hostUserAgent')
                     and settings.get('network_user_agent') == env.get('networkUserAgent'),
                     'Adopted configuration differs from its calibration reference')
    else:
        request = tsep.parse_json(files[reference])
        tsep.require(isinstance(request, dict) and settings.get('granularity') in request
                     and settings.get('key') == plan_data['target']
                     and settings.get('form_factor') == request.get('formFactor', 'ALL'),
                     'Field settings differ from request or target')
    prior = {name: files[name] for name in ('plan.json', reference)}
    records = []
    last_time = tsep.timestamp(plan_data['created_at'])
    for index in range(1, count+1):
        name = 'receipts/%02d.json' % index
        if name not in files:
            break
        history = 'history/%02d-SHA256SUMS' % index
        raw_manifest = manifest_bytes(prior)
        tsep.require(files.get(history) == raw_manifest, 'Earlier package manifest does not match retained files')
        rec = tsep.parse_json(files[name])
        tsep.require(isinstance(rec, dict) and set(rec) == {'slot', 'plan_sha256', 'previous_manifest_sha256',
                     'observed_at', 'status', 'source_url', 'reason', 'original', 'sha256'}
                     and rec['slot'] == index and rec['plan_sha256'] == entries['plan.json']
                     and rec['previous_manifest_sha256'] == sha(raw_manifest), 'Receipt/plan/history binding differs')
        observed = tsep.timestamp(rec['observed_at'])
        tsep.require(last_time <= observed <= tsep.timestamp(now()), 'Receipt chronology is inconsistent')
        last_time = observed
        tsep.require(rec['status'] in ('supplied', 'unavailable'), 'Unsupported slot status')
        if rec['status'] == 'supplied':
            expected_name = 'originals/%02d.json' % index
            url(rec['source_url'])
            tsep.require(rec['reason'] is None, 'Supplied slot cannot conceal a missing reason')
        else:
            text(rec['reason'], 'reason for unavailable attempt')
            tsep.require(rec['source_url'] is None, 'Unavailable attempt has no fabricated source URL')
            expected_name = 'errors/%02d.txt' % index if rec['original'] is not None else None
        tsep.require(rec['original'] == expected_name, 'Invalid original path')
        if expected_name:
            tsep.require(expected_name in files and rec['sha256'] == entries[expected_name], 'Original/receipt binding differs')
            native(root/expected_name)
            prior[expected_name] = files[expected_name]
        else:
            tsep.require(rec['sha256'] is None, 'Missing attempt cannot fabricate an original hash')
        prior[name] = files[name]; prior[history] = files[history]
        records.append(rec)
    tsep.require(set(prior) == set(files), 'Unexpected session files or nonsequential slots')
    return plan_data, records, files


def record(root, output, *, slot, file=None, source_url=None, missing_reason=None, error_file=None):
    p, records, files = session(root)
    tsep.require(type(slot) is int and slot == len(records)+1 and slot <= p['slot_count'],
                 'Append only the next planned slot; replacement, skipping and extra slots are forbidden')
    observed = now()
    prior_time = records[-1]['observed_at'] if records else p['created_at']
    tsep.require(tsep.timestamp(observed) >= tsep.timestamp(prior_time), 'Clock precedes previous operation')
    history = manifest_bytes(files)
    if file is not None:
        tsep.require(missing_reason is None and error_file is None, 'Choose a file OR an unavailable attempt')
        url(source_url)
        name = 'originals/%02d.json' % slot
        payload = native(file)
        status = 'supplied'
    else:
        text(missing_reason, 'unavailable attempt reason')
        tsep.require(source_url is None, 'Do not invent a source URL for a missing original')
        name = 'errors/%02d.txt' % slot if error_file is not None else None
        payload = native(error_file) if error_file is not None else None
        status = 'unavailable'
    receipt = {'slot': slot, 'plan_sha256': sha(files['plan.json']), 'previous_manifest_sha256': sha(history),
               'observed_at': observed, 'status': status, 'source_url': source_url,
               'reason': missing_reason, 'original': name, 'sha256': sha(payload) if payload else None}
    if name:
        files[name] = payload
    files['receipts/%02d.json' % slot] = json_bytes(receipt)
    files['history/%02d-SHA256SUMS' % slot] = history
    return deliver(output, files, p['workflow_source_files'])


def capture_data(p, records, files, assessed):
    tsep.require(tsep.timestamp(assessed) >= tsep.timestamp(records[-1]['observed_at'] if records else p['created_at']),
                 'Assessment precedes intake')
    kind = p['performance_kind']
    slots = [dict(r) for r in records]
    slots += [{'slot': i, 'status': 'unrecorded'} for i in range(len(records)+1, p['slot_count']+1)]
    available = []
    for r in records:
        if r['status'] == 'supplied':
            available.append({'raw_json': files[r['original']].decode('utf-8'), 'sha256': r['sha256'],
                              'observed_at': r['observed_at'], 'source_url': r['source_url']})
    target = {'url': p['target'], 'observed_at': assessed,
              'intent': {'declared_at': p['created_at'], 'performance': {kind: p['settings']}}}
    if kind == 'field':
        target['field'] = dict(available[0] if available else {}, reader='crux-api-v1',
                              request=tsep.parse_json(files['reference/request.json']), slots=slots)
    else:
        target['lab'] = {'reader': 'lighthouse-json-v1', 'runs': available, 'slots': slots}
    return {'input_version': '1', 'rules': RULES[kind], 'targets': [target]}


def overview(p, records, files):
    rows = []
    for r in records:
        data = parsed_native(files[r['original']]) if r['status'] == 'supplied' else {}
        env = data.get('environment', {})
        rows.append({'slot': r['slot'], 'status': r['status'], 'reason': r['reason'],
                     'imported_at': r['observed_at'], 'source_sha256': r['sha256'],
                     'native_fetch_time': data.get('fetchTime'),
                     'native_environment': env,
                     'calibration_reused': r['sha256'] == p['references'].get('reference/calibration.json'),
                     'environment_assessment': 'Retained, not assessed / Conservé, non évalué'})
    rows += [{'slot': i, 'status': 'unrecorded'} for i in range(len(records)+1, p['slot_count']+1)]
    reference = parsed_native(files.get('reference/calibration.json', b''))
    return {'slots': rows, 'limitations': LIMITS, 'review_created': False,
            'calibration_environment': reference.get('environment'),
            'acquisition_basis': 'File imported locally; native dates preserved / Import local, dates natives conservées'}


def blank_response(request_digest, kind):
    result = {'kind': 'tsep-performance-response', 'workflow_version': VERSION,
              'request_sha256': request_digest, 'reviewer': '', 'observed_at': '',
              'provenance': None, 'assistance': '', 'examined_evidence': []}
    if kind == 'field':
        result['metrics'] = {k: {'classification': None, 'reason': '', 'action': ''} for k in performance.FIELD_METRICS}
    else:
        result.update(hypothesis='', metrics=[], next_measurement='', claims_field_cwv=None, claims_inp_from_tbt=None)
    return result


def build_bundle(stage, data, p):
    raw = json_bytes(data)
    tsep.require(len(raw) <= tsep.MAX_JSON_BYTES, 'Assembled capture input exceeds 8 MiB')
    (stage/'input.json').write_bytes(raw)
    captures.build(stage/'input.json', stage/'bundle', assessor=p['operator'],
                   label='Performance intake: '+p['target'], selection_method=p['selection_reason'], access=p['access'])


def finalize(root, output):
    p, records, files = session(root)
    assessed = now()
    data = capture_data(p, records, files, assessed)
    output = Path(output)
    tsep.require(output.parent.is_dir() and not output.exists() and not output.is_symlink(), 'Choose a NEW output directory')
    with tempfile.TemporaryDirectory(prefix='.tsep-performance-', dir=output.parent) as folder:
        stage = Path(folder)
        write_files(stage, {'session/'+name: raw for name, raw in files.items()})
        (stage/'session/SHA256SUMS').write_bytes(manifest_bytes(files))
        build_bundle(stage, data, p)
        evidence = [{'path': 'session/'+name, 'sha256': sha(raw)} for name, raw in sorted(files.items())]
        request = {'kind': 'tsep-performance-review-request', 'workflow_version': VERSION,
                   'workflow_source_files': p['workflow_source_files'], 'protocol': p['protocol'],
                   'created_at': assessed, 'performance_kind': p['performance_kind'], 'access': p['access'],
                   'input_sha256': tsep.digest(stage/'input.json'), 'evidence': evidence,
                   'limitations': LIMITS}
        (stage/'request.json').write_bytes(json_bytes(request))
        (stage/'response-template.json').write_bytes(json_bytes(blank_response(tsep.digest(stage/'request.json'), p['performance_kind'])))
        view = overview(p, records, files)
        (stage/'overview.json').write_bytes(json_bytes(view))
        lines = ['Passages prévus / Planned slots: '+str(p['slot_count']),
                 'Statut des preuves / Evidence status: '+p['access'],
                 'Cible / Target: '+p['target'], '', view['acquisition_basis'], '']
        for row in view['slots']:
            lines.append('Passage / Slot '+str(row['slot'])+': '+row['status'])
            for key in ('reason', 'imported_at', 'native_fetch_time', 'native_environment', 'calibration_reused'):
                if key in row:
                    lines.append('  '+key+': '+str(row[key]))
        lines += ['', 'Calibration (réglages seulement / settings only): '+str(view['calibration_environment']), '', *LIMITS]
        (stage/'overview.txt').write_text('\n'.join(lines)+'\n', encoding='utf-8')
        (stage/'READ-ME.txt').write_text(
            'Revue à fournir / Review required\n\n'
            'Lire overview.json et les pièces request.json/evidence. Copier response-template.json HORS de ce dossier.\n'
            'Read overview.json and every request.json/evidence item. Copy response-template.json OUTSIDE this directory.\n'
            'Remplir reviewer, observed_at (date avec fuseau), provenance (human, human-assisted, synthetic-exercise),\n'
            'assistance, examined_evidence (objets path/sha256 réellement examinés) et chaque décision.\n'
            'Supply the actual author, time, provenance, assistance, examined evidence objects and every decision.\n'
            'Aucune opinion préremplie ; réponse IA non assimilable à une revue humaine.\n'
            'No prefilled opinion; an AI response is not a human review. Identity/judgment are not authenticated.\n'
            'Conserver les valeurs défavorables. C concerne la documentation, pas de bonnes performances.\n'
            'Retain poor values. C concerns documentation, not good performance.\n\n'+'\n'.join(LIMITS)+'\n', encoding='utf-8')
        seal(stage); inventory(stage)
        tsep.require(source_files() == p['workflow_source_files'], 'Workflow changed during finalization')
        publish(stage, output)
    return {'output': str(output), 'status': tsep.read_json(output/'bundle/report.json')['results'][0]['status'],
            'recorded_slots': len(records), 'planned_slots': p['slot_count'], 'reviews_created': 0, 'network_requests': 0}


def review(root, response_file, output):
    root, output = Path(root), Path(output)
    entries = inventory(root)
    p, records, files = session(root/'session')
    request = tsep.read_json(root/'request.json')
    tsep.require(request['workflow_source_files'] == source_files() and request['protocol'] == protocol()
                 and request['performance_kind'] == p['performance_kind'] and request['access'] == p['access'],
                 'Request differs from plan/tools')
    original_data = capture_data(p, records, files, request['created_at'])
    raw_input = json_bytes(original_data)
    tsep.require(regular(root/'input.json') == raw_input and regular(root/'bundle/input.json') == raw_input
                 and request['input_sha256'] == sha(raw_input), 'Request/capture/session binding differs')
    evidence = [{'path': 'session/'+name, 'sha256': sha(raw)} for name, raw in sorted(files.items())]
    tsep.require(request['evidence'] == evidence, 'Request evidence differs from session')
    raw_response = regular(response_file, tsep.MAX_JSON_BYTES)
    answer = tsep.parse_json(raw_response)
    expected = blank_response(entries['request.json'], p['performance_kind'])
    tsep.require(isinstance(answer, dict) and set(answer) == set(expected)
                 and answer['kind'] == expected['kind'] and answer['workflow_version'] == VERSION
                 and answer['request_sha256'] == entries['request.json'], 'Wrong review response or request binding')
    tsep.require(answer['examined_evidence'] == evidence, 'Declare the exact examined evidence objects')
    for key in ('reviewer', 'assistance'):
        text(answer[key], key)
    imported = now()
    tsep.require(tsep.timestamp(request['created_at']) <= tsep.timestamp(answer['observed_at']) <= tsep.timestamp(imported),
                 'Review must follow request and precede import')
    provenance = answer['provenance']
    tsep.require(provenance in ('human', 'human-assisted', 'synthetic-exercise')
                 and (provenance == 'synthetic-exercise') == (p['access'] == 'synthetic'), 'Review provenance/access mismatch')
    supplied = {'reviewer': answer['reviewer'], 'observed_at': answer['observed_at'],
                'provenance': 'synthetic-exercise' if provenance == 'synthetic-exercise' else 'supplied-review'}
    kind = p['performance_kind']
    hashes = [r['sha256'] for r in records if r['status'] == 'supplied']
    supplied['source_sha256'] = (hashes[0] if hashes else None) if kind == 'field' else hashes
    if kind == 'field':
        metrics = answer['metrics']
        tsep.require(isinstance(metrics, dict) and set(metrics) == set(performance.FIELD_METRICS), 'Review each field metric')
        for metric, decision in metrics.items():
            tsep.require(isinstance(decision, dict) and set(decision) == {'classification', 'reason', 'action'}
                         and decision['classification'] in ('good', 'needs-improvement', 'poor', 'unknown'),
                         'Supply an explicit metric classification')
            text(decision['reason'], metric+' reason'); text(decision['action'], metric+' action')
        supplied['metrics'] = metrics
    else:
        for key in ('hypothesis', 'next_measurement'):
            text(answer[key], key); supplied[key] = answer[key]
        metrics = answer['metrics']
        tsep.require(isinstance(metrics, list) and metrics and all(isinstance(k, str) and k in performance.LAB_METRICS for k in metrics)
                     and len(set(metrics)) == len(metrics), 'Reference measured lab metrics')
        supplied['metrics'] = metrics
        for key in ('claims_field_cwv', 'claims_inp_from_tbt'):
            tsep.require(type(answer[key]) is bool, 'Declare '+key)
            supplied[key] = answer[key]  # Retain contradictions; do not "correct" them.
    data = copy.deepcopy(original_data)
    data['targets'][0]['observed_at'] = imported
    data['targets'][0][kind+'_review'] = supplied
    tsep.require(output.parent.is_dir() and not output.exists() and not output.is_symlink(), 'Choose a NEW output directory')
    with tempfile.TemporaryDirectory(prefix='.tsep-performance-', dir=output.parent) as folder:
        stage = Path(folder)
        write_files(stage, {'intake/'+name: regular(root/name) for name in entries})
        (stage/'intake/SHA256SUMS').write_bytes(regular(root/'SHA256SUMS'))
        (stage/'response.json').write_bytes(raw_response)
        (stage/'review-import.json').write_bytes(json_bytes({'workflow_version': VERSION,
            'workflow_source_files': p['workflow_source_files'], 'request_sha256': entries['request.json'],
            'response_sha256': sha(raw_response), 'imported_at': imported,
            'original_assessed_at': request['created_at'], 'provenance': provenance,
            'assistance': answer['assistance'], 'limitations': LIMITS}))
        build_bundle(stage, data, p)
        seal(stage); inventory(stage)
        tsep.require(inventory(root) == entries, 'Original intake changed during review import')
        tsep.require(source_files() == p['workflow_source_files'], 'Workflow changed during review import')
        publish(stage, output)
    return {'output': str(output), 'status': tsep.read_json(output/'bundle/report.json')['results'][0]['status'],
            'review_imported': True, 'review_authenticated': False, 'network_requests': 0}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for kind in RULES:
        cmd = sub.add_parser('plan-'+kind)
        for name in ('target', 'operator', 'access', 'selection-reason', 'output'):
            cmd.add_argument('--'+name, required=True)
        cmd.add_argument('--max-age-days', type=int, required=True)
        if kind == 'field':
            cmd.add_argument('--request-file', required=True)
            cmd.add_argument('--granularity', choices=('url', 'origin'), required=True)
            cmd.add_argument('--form-factor', choices=('PHONE', 'TABLET', 'DESKTOP', 'ALL'), required=True)
        else:
            cmd.add_argument('--calibration', required=True)
            cmd.add_argument('--final-url', required=True)
            cmd.add_argument('--run-count', type=int, required=True)
    cmd = sub.add_parser('record')
    cmd.add_argument('root'); cmd.add_argument('--slot', required=True, type=int)
    choice = cmd.add_mutually_exclusive_group(required=True)
    choice.add_argument('--file'); choice.add_argument('--missing-reason')
    cmd.add_argument('--source-url'); cmd.add_argument('--error-file'); cmd.add_argument('--output', required=True)
    cmd = sub.add_parser('finalize'); cmd.add_argument('root'); cmd.add_argument('--output', required=True)
    cmd = sub.add_parser('review'); cmd.add_argument('root'); cmd.add_argument('response_file'); cmd.add_argument('--output', required=True)
    args = vars(parser.parse_args(argv)); command = args.pop('command')
    try:
        if command.startswith('plan-'):
            result = plan(kind=command[5:], **args)
        else:
            result = {'record': record, 'finalize': finalize, 'review': review}[command](**args)
        tsep.emit(result)
        return 0
    except (ValueError, OSError, KeyError, TypeError, RecursionError) as error:
        print('ERROR: '+str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
