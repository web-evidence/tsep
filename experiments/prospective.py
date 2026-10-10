#!/usr/bin/env python3
"""Local prospective marker experiment, kept separate from draft.7 reports. Apache-2.0."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from collectors import ts01
from collectors.preflight import reference_check
from conformance.evaluate import trace, media_type
from conformance.http import body_digest, text_body, Unknown
from diagnostics import campaign
from experiments import noscript
from provenance.runtime import loaded_sources, runtime_identity

VERSION = '1'
need = tsep.require


def sources():
    result = ts01.collection_sources()
    result.update(loaded_sources(ROOT, {'experiments/prospective.py': sys.modules[__name__],
                                      'experiments/noscript.py': noscript,
                                      'diagnostics/campaign.py': campaign}))
    return result


def semantic(value):
    if isinstance(value, dict):
        return {k: semantic(v) for k, v in value.items() if k != 'runtime'}
    if isinstance(value, list):
        return [semantic(v) for v in value]
    return value


def probe(headers, body, intent):
    kind, params = media_type(headers)
    need(kind == 'text/html' and params.get('charset') == 'utf-8',
         'Experimental prospective probe requires explicit UTF-8 HTML')
    criteria = {k: intent.get(k, []) for k in ('required_markers', 'forbidden_markers')}
    value = noscript.experiment(text_body(body), criteria)
    need(value['source_utf8_sha256'] == body_digest(body), 'Experiment/body byte binding mismatch')
    return value


def inspect_reference(reference, intent_path):
    ref, binding = campaign.phase(Path(reference))
    raw, intent = campaign.read(Path(intent_path))
    ts01.same_collector(ref)
    ts01.validate_settings(ref['settings'])
    need(intent['intent_version'] == '3' and intent['settings'] == ref['settings'], 'Intent/reference settings mismatch')
    need(intent['reference_manifest_sha256'] == binding['manifest_sha256'] and
         intent['reference_source_files'] == ref['source_files'], 'Intent/reference binding mismatch')
    urls = ref['settings']['urls']
    need([r['url'] for r in ref['targets']] == urls == [r['url'] for r in intent['targets']], 'Reference scope mismatch')
    declared = tsep.timestamp(intent['declared_at'])
    need(tsep.timestamp(ref['started_at']) <= tsep.timestamp(ref['finished_at']) <= declared, 'Intent predates reference completion')
    rows = []
    for target, chosen in zip(ref['targets'], intent['targets']):
        criterion, basis = chosen['intent'], chosen['identity_basis']
        need(criterion['declared_at'] == intent['declared_at'] and criterion['public_canonical'] is True and
             criterion['crawler'] == ref['settings']['agent'], 'Inconsistent intent context')
        need(tsep.timestamp(target['observed_at']) <= declared, 'Reference after intent')
        final, status, headers, body = trace(target['http'], target['url'], criterion['crawler'])
        need(status == 200 and not target.get('collection_error'), 'Incomplete/non-200 reference')
        need(criterion['expected_final_url'] == final and criterion['expected_body_sha256'] == body_digest(body), 'Reference URL/body mismatch')
        policy = basis['policy']
        actual = 'stable' if criterion.get('representation') == 'stable' else 'markers' if criterion.get('required_markers') else 'digest'
        need(policy == actual and policy in ('digest', 'stable', 'markers'), 'Intent policy mismatch')
        need(basis['origin'] in ('reference-adopted', 'operator-final-url'), 'Unknown identity origin')
        need(basis['origin'] != 'operator-final-url' or basis['declared_final_url'] == final, 'Declared final URL mismatch')
        checked = reference_check(headers, body, policy, criterion.get('required_markers', []), criterion.get('forbidden_markers', []))
        need(checked == chosen['reference_preflight'] and checked['state'] != 'contradiction', 'Reference preflight mismatch')
        experimental = probe(headers, body, criterion) if policy == 'markers' else None
        need(experimental is None or experimental['candidate_consensus'] == 'pass',
             'Reference does not satisfy both complete experimental marker readings')
        rows.append({'url': target['url'], 'policy': policy, 'intent': criterion,
                     'identity_basis': basis, 'active_preflight': checked, 'experimental_reference': experimental})
    return ref, intent, {'reference': binding, 'intent_sha256': hashlib.sha256(raw).hexdigest(), 'targets': rows}


def prepare(reference, intent_path, output):
    before = sources()
    ref, intent, checked = inspect_reference(reference, intent_path)
    prepared = ts01.now()
    need(tsep.timestamp(intent['declared_at']) <= tsep.timestamp(prepared), 'Future intent')
    need(sources() == before, 'Trial sources changed during preparation')
    receipt = {'kind': 'prospective-experiment-receipt', 'version': VERSION,
               'prepared_at': prepared, 'checked_reference': checked, 'source_files': before,
               'normative_effect': 'none', 'runtime': runtime_identity(),
               'chronology': 'Local clock and files only; no trusted timestamp, signature, independent attestation or human approval.'}
    ts01.save(output, receipt)
    return receipt


def compare(reference, assessment, receipt_path):
    before = sources()
    assessment = Path(assessment)
    _, receipt = campaign.read(Path(receipt_path))
    need(receipt['kind'] == 'prospective-experiment-receipt' and receipt['version'] == VERSION and
         receipt['normative_effect'] == 'none' and receipt['source_files'] == before, 'Trial source/receipt mismatch')
    ts01.verify(assessment)
    ref, intent, checked = inspect_reference(reference, assessment/'intent.json')
    need(semantic(checked) == semantic(receipt['checked_reference']), 'Frozen reference/intent/probe changed')
    measurement, phase_binding = campaign.phase(assessment/'evaluation')
    ts01.same_collector(measurement)
    need(measurement['source_files'] == ref['source_files'] and measurement['settings'] == ref['settings'], 'Measurement settings/sources differ')
    need([r['url'] for r in measurement['targets']] == ref['settings']['urls'], 'Measurement scope mismatch')
    prepared, declared = tsep.timestamp(receipt['prepared_at']), tsep.timestamp(intent['declared_at'])
    start, finish = tsep.timestamp(measurement['started_at']), tsep.timestamp(measurement['finished_at'])
    need(declared <= prepared <= start <= finish, 'Receipt must precede measurement start')
    _, input_data = campaign.read(assessment/'input.json')
    need(input_data['rules'] == ts01.RULES and len(input_data['targets']) == len(ref['targets']), 'Assessment input scope mismatch')
    for row, prior, actual, chosen in zip(input_data['targets'], ref['targets'], measurement['targets'], intent['targets']):
        need(all(row.get(k) == v for k, v in actual.items()), 'Assessment/evaluation binding mismatch')
        need(row['intent'] == chosen['intent'] and row['reference']['http'] == prior['http'] and
             row['reference']['observed_at'] == prior['observed_at'], 'Assessment/reference/intent binding mismatch')
        need(row['reference']['reference_manifest_sha256'] == checked['reference']['manifest_sha256'] and
             row['reference']['source_files'] == ref['source_files'], 'Assessment reference provenance mismatch')
        context = row['context']
        settings = ref['settings']
        need(context['network'] == settings['network'] and context['tool'] == ts01.NAME and
             context['tool_version'] == ts01.VERSION and context['accept_encoding'] == settings['accept_encoding'] and
             context['collection_environment'] == measurement['environment'] and
             context['bounds'] == {k: settings[k] for k in ('timeout', 'max_bytes', 'max_redirects', 'origins', 'allow_loopback')},
             'Assessment collection context mismatch')
        need(context['intent_file_sha256'] == checked['intent_sha256'] and context['reference_manifest_sha256'] == checked['reference']['manifest_sha256'] and
             context['collection_source_files'] == measurement['source_files'] and context['collector_matches_reference'] is True and
             context['reference_preflight'] == chosen['reference_preflight'] and context['identity_basis'] == chosen['identity_basis'], 'Assessment context binding mismatch')
        need(start <= tsep.timestamp(actual['started_at']) <= tsep.timestamp(actual['observed_at']) <= finish, 'Invalid target chronology')
        for hop in actual['http']:
            need(prepared <= tsep.timestamp(hop['started_at']) <= tsep.timestamp(hop['finished_at']) <= finish, 'Hop predates receipt or exceeds measurement')
    # Keep the normative report intact and verify its actual observations separately.
    with tempfile.TemporaryDirectory(prefix='tsep-prospective-replay-') as folder:
        output = Path(folder)/'replay'
        ts01.replay(assessment, output)
        replay_record = tsep.read_json(output/'replay.json')
    atoms = tsep.read_json(assessment/'bundle/assessment.json')
    rows = []
    for target, chosen in zip(input_data['targets'], intent['targets']):
        criterion = chosen['intent']
        row = {'url': target['url'], 'policy': chosen['identity_basis']['policy'],
               'active_observations': [a for a in atoms if a['target'] == target['url']],
               'marker_experiment': None, 'normative_effect': 'none'}
        try:
            final, status, headers, body = trace(target['http'], target['url'], criterion['crawler'])
            need(not target.get('collection_error'), 'Collection failed')
            row.update(decoded_body_sha256=body_digest(body), reference_body_sha256=criterion['expected_body_sha256'])
            if status != 200:
                eligibility = 'not-eligible-status'
            elif final != criterion['expected_final_url']:
                eligibility = 'not-eligible-url'
            elif row['decoded_body_sha256'] == row['reference_body_sha256']:
                eligibility = 'not-needed-digest'
            elif chosen['identity_basis']['policy'] == 'stable':
                eligibility = 'not-eligible-stable-policy'
            elif chosen['identity_basis']['policy'] != 'markers':
                eligibility = 'not-eligible-no-markers'
            else:
                eligibility = 'changed-body-markers'
                row['marker_experiment'] = probe(headers, body, criterion)
                row['same_decoded_body_bytes'] = row['marker_experiment']['source_utf8_sha256'] == row['decoded_body_sha256']
            row['eligibility'] = eligibility
        except (ValueError, KeyError, TypeError, Unknown) as error:
            row.update(eligibility='unavailable', reason=str(error))
        rows.append(row)
    need(sources() == before, 'Trial sources changed during comparison')
    return {'kind': 'prospective-experiment-comparison', 'version': VERSION, 'normative_effect': 'none',
            'receipt_sha256': tsep.digest(Path(receipt_path)), 'input_sha256': tsep.digest(assessment/'input.json'),
            'reference': checked['reference'], 'evaluation': phase_binding, 'source_files': before,
            'prepared_at': receipt['prepared_at'], 'measurement_started_at': measurement['started_at'],
            'reference_to_measurement_seconds': (start-tsep.timestamp(ref['finished_at'])).total_seconds(),
            'active_report_replayed': replay_record, 'runtime': runtime_identity(), 'targets': rows,
            'network_requests': 0, 'chronology': receipt['chronology'],
            'scope': 'Prior locally recorded criteria; unchanged draft.7 observations and separate bounded marker candidates. No TSEP report upgrade, site verdict, longitudinal stability or human validation.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    first = sub.add_parser('prepare'); first.add_argument('--intent', type=Path, required=True)
    second = sub.add_parser('compare'); second.add_argument('--assessment', type=Path, required=True); second.add_argument('--receipt', type=Path, required=True)
    for item in (first, second):
        item.add_argument('--reference', type=Path, required=True); item.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    try:
        if a.command == 'prepare':
            value = prepare(a.reference, a.intent, a.output)
        else:
            value = compare(a.reference, a.assessment, a.receipt); ts01.save(a.output, value)
        print(json.dumps({'kind': value['kind'], 'normative_effect': value['normative_effect']}))
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({'kind':'prospective-experiment-error','error':str(error)}), file=sys.stderr); return 64
    return 0

if __name__ == '__main__':sys.exit(main())
