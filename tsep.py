#!/usr/bin/env python3
"""TSEP report interchange reference implementation. Apache-2.0.

No network, third-party dependencies or automatic SEO assessments.
The shape checker implements only the keywords used by the bundled schema;
it is deliberately not a general-purpose JSON Schema implementation.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

ROOT = Path(__file__).resolve().parent
PROTOCOL_PATH = ROOT / 'spec/protocol.json'
MAX_JSON_BYTES = 8 * 1024 * 1024


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON key: ' + key)
        result[key] = value
    return result


def read_json(path):
    with Path(path).open('rb') as handle:
        data = handle.read(MAX_JSON_BYTES + 1)
    require(len(data) <= MAX_JSON_BYTES, 'JSON exceeds 8 MiB')
    def bad_constant(value):
        raise Invalid('Non-finite JSON number: ' + value)
    return json.loads(data, object_pairs_hook=unique_object,
                      parse_constant=bad_constant)


def digest(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda: handle.read(65536), b''):
            value.update(chunk)
    return value.hexdigest()


def timestamp(value):
    require(isinstance(value, str) and re.fullmatch(
        r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})', value),
        'Timestamp must include date, time and timezone: ' + str(value))
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(parsed.utcoffset() is not None, 'Timestamp lacks timezone')
    return parsed


def shape(value, schema, where='$'):
    supported = {'$schema', '$id', 'title', 'type', 'properties', 'required',
                 'additionalProperties', 'items', 'minItems', 'minLength',
                 'enum', 'const', 'pattern'}
    require(not set(schema) - supported, 'Unsupported schema keyword at ' + where)
    types = {'object': dict, 'array': list, 'string': str}
    if 'type' in schema:
        require(type(value) is types[schema['type']], 'Wrong type at ' + where)
    if 'const' in schema:
        require(value == schema['const'], 'Wrong constant at ' + where)
    if 'enum' in schema:
        require(value in schema['enum'], 'Unknown value at ' + where)
    if isinstance(value, dict):
        require(set(schema.get('required', [])) <= set(value), 'Missing fields at ' + where)
        props = schema.get('properties', {})
        if schema.get('additionalProperties') is False:
            require(set(value) <= set(props), 'Unknown fields at ' + where)
        for key, item in value.items():
            if key in props:
                shape(item, props[key], where + '.' + key)
    if isinstance(value, list):
        require(len(value) >= schema.get('minItems', 0), 'Too few items at ' + where)
        for i, item in enumerate(value):
            shape(item, schema['items'], where + '[' + str(i) + ']')
    if isinstance(value, str):
        require(len(value) >= schema.get('minLength', 0), 'Empty text at ' + where)
        if schema.get('minLength', 0):
            require(bool(value.strip()), 'Blank text at ' + where)
        if 'pattern' in schema:
            require(re.search(schema['pattern'], value) is not None,
                    'Pattern mismatch at ' + where)


def unique(values, label):
    require(len(values) == len(set(values)), 'Duplicate ' + label)


def evidence_path(root, relative):
    require('\\' not in relative, 'Use POSIX relative evidence paths')
    path = PurePosixPath(relative)
    require(not path.is_absolute() and '..' not in path.parts
            and path.parts and path.as_posix() == relative,
            'Unsafe evidence path: ' + relative)
    resolved_root = Path(root).resolve()
    full = (resolved_root / relative).resolve()
    require(resolved_root in full.parents and full.is_file(),
            'Evidence missing or outside bundle: ' + relative)
    return full


def validate_atomic_results(result, control, targets, artifacts):
    """Check declared rule evidence/coverage; never infer SEO truth from a capture."""
    rules = {r['id']: r for r in control.get('rules', [])}
    atoms = result.get('atomic_results', [])
    require(rules or not atoms, 'No atomic rules defined for ' + control['id'])
    unique([(a['rule_id'], a['target']) for a in atoms], 'rule/target observation')
    by_pair = {}
    for atom in atoms:
        rid, target = atom['rule_id'], atom['target']
        require(rid in rules, 'Unknown or foreign atomic rule: ' + rid)
        require(target in result['evaluated_targets'], 'Atomic target not evaluated: ' + target)
        refs = atom['evidence_ids']
        unique(refs, 'atomic evidence reference')
        require(set(refs) <= set(result['evidence_ids']), 'Atomic evidence not linked by control')
        require(all(target in artifacts[ref]['targets'] for ref in refs),
                'Atomic evidence does not cover its target')
        outcome = atom['outcome']
        if outcome != 'inconclusive':
            require(refs, 'Conclusive atomic outcome requires evidence')
        if outcome in ('pass', 'not-applicable'):
            key = 'required_inputs' if outcome == 'pass' else 'na_inputs'
            needed = rules[rid][key]
            require(needed, 'Atomic exemption is not allowed: ' + rid)
            require(set(needed) <= {artifacts[ref]['kind'] for ref in refs},
                    'Missing atomic input coverage: ' + rid)
        by_pair[(rid, target)] = outcome
    if not rules:
        return
    status = result['status']
    has_failure = 'fail' in by_pair.values()
    if status == 'C':
        require(set(by_pair) == {(rid, target) for rid in rules for target in targets},
                'C requires every atomic rule for every target')
        require(all(x in ('pass', 'not-applicable') for x in by_pair.values()),
                'Partial or failing atomic results cannot yield C')
        require('pass' in by_pair.values(), 'All atomic exemptions cannot yield C')
    elif status == 'NC':
        require(has_failure, 'NC requires an evidenced atomic contradiction')
    elif status == 'NA':
        require(not atoms, 'Whole-control NA cannot contain applicable atomic observations')
        for target in targets:
            require(any(artifacts[ref]['kind'] == 'intent' and target in artifacts[ref]['targets']
                        for ref in result['evidence_ids']),
                    'Whole-control NA requires applicability evidence in intent per target')
    else:
        require(not has_failure, 'An evidenced atomic contradiction must remain NC')
        if result['evaluation_state'] == 'not-started':
            require(not atoms, 'Unstarted control cannot contain atomic observations')


def validate(report, evidence_root):
    shape(report, read_json(ROOT / 'schemas/report.schema.json'))
    protocol = read_json(PROTOCOL_PATH)
    for document in protocol['normative_documents']:
        require(digest(ROOT / document['path']) == document['sha256'],
                'Normative document fingerprint mismatch: ' + document['path'])
    controls = {c['id']: c for c in protocol['controls']}
    require(report['protocol']['sha256'] == digest(PROTOCOL_PATH),
            'Protocol fingerprint mismatch')
    issued = timestamp(report['issued_at'])
    targets = set(report['scope']['targets'])
    unique(report['scope']['targets'], 'scope target')
    unique(report['controls'], 'selected control')
    profiles = {p['id']: p for p in read_json(PROTOCOL_PATH)['profiles']}
    if report['profile'] != 'custom':
        require(set(report['controls']) == set(profiles[report['profile']]['controls']),
                'Profile requires its complete control set')
    unique([r['control_id'] for r in report['results']], 'result')
    require({r['control_id'] for r in report['results']} == set(report['controls']),
            'Results must match selected controls exactly')
    artifacts = {a['id']: a for a in report['artifacts']}
    require(len(artifacts) == len(report['artifacts']), 'Duplicate artifact ID')
    unique([a['path'] for a in report['artifacts']], 'artifact path')
    for artifact in artifacts.values():
        unique(artifact['targets'], 'artifact target')
        require(set(artifact['targets']) <= targets, 'Artifact target outside scope')
        require(timestamp(artifact['observed_at']) <= issued,
                'Evidence observed after report was issued')
        allowed_private = {'intent'} if report['profile'] == 'TSEP-1' else {'intent', 'search-console'}
        if report['profile'] in ('TSEP-1', 'TSEP-2') and artifact['kind'] not in allowed_private:
            require(artifact['access'] == 'public', 'Profile requires public evidence: ' + artifact['id'])
        path = evidence_path(evidence_root, artifact['path'])
        require(digest(path) == artifact['sha256'],
                'Evidence fingerprint mismatch: ' + artifact['id'])
    for result in report['results']:
        cid = result['control_id']
        unique(result['evidence_ids'], 'evidence reference for ' + cid)
        unique(result['evaluated_targets'], 'evaluated target for ' + cid)
        refs = set(result['evidence_ids'])
        require(refs <= set(artifacts), 'Unknown evidence reference for ' + cid)
        evaluated = set(result['evaluated_targets'])
        require(evaluated <= targets, 'Evaluated target outside scope for ' + cid)
        status = result['status']
        state = result['evaluation_state']
        if status == 'NT':
            require(state in ('not-started', 'inconclusive'), 'NT cannot be complete')
            if state == 'not-started':
                require(not evaluated and not refs, 'Unstarted check cannot claim observations')
        else:
            require(state == 'complete' and refs and evaluated,
                    'C/NC/NA require completed assessment, targets and evidence: ' + cid)
            covered = set().union(*(set(artifacts[x]['targets']) for x in refs))
            require(evaluated <= covered, 'Evidence does not cover evaluated targets: ' + cid)
            if status in ('C', 'NA'):
                require(evaluated == targets, 'C/NA must cover all declared targets: ' + cid)
            if status == 'C':
                require(report['assessor']['mode'] != 'automatic',
                        'This draft has no fully automated control implementation: ' + cid)
                for kind in controls[cid]['required_inputs']:
                    kind_targets = set().union(*(set(artifacts[x]['targets']) for x in refs
                                                if artifacts[x]['kind'] == kind))
                    require(targets <= kind_targets, 'Missing input coverage ' + kind + ': ' + cid)
        validate_atomic_results(result, controls[cid], targets, artifacts)
    return decision(report, controls)


def decision(report, controls=None):
    if controls is None:
        controls = {c['id']: c for c in read_json(PROTOCOL_PATH)['controls']}
    counts = {status: sum(r['status'] == status for r in report['results'])
              for status in ('C', 'NC', 'NA', 'NT')}
    blocking = [r['control_id'] for r in report['results']
                if controls[r['control_id']]['severity'] == 'blocking'
                and r['status'] in ('NC', 'NT')]
    if blocking:
        gate = 'NO_GO'
    elif counts['NT'] or counts['NA'] == len(report['results']):
        gate = 'INCOMPLETE'
    elif any(r['status'] == 'NC' and controls[r['control_id']]['severity'] == 'major'
             for r in report['results']):
        gate = 'REVIEW'
    else:
        gate = 'GO_WITH_RESERVATIONS'
    return {'valid': True, 'decision': gate, 'profile': report['profile'],
            'scope': report['scope'], 'counts': counts, 'blocking': blocking,
            'synthetic_evidence': any(a['access'] == 'synthetic' for a in report['artifacts']),
            'selected_controls': len(report['controls']), 'protocol_controls': len(controls),
            'unevaluated_controls': sorted(set(controls) - set(report['controls'])),
            'interpretation': 'Declared scope and selected controls only; validates report '
                              'consistency and file integrity, not the truth of an assessment.'}


def initialize(targets, selected, profile, assessor, label, selection_method):
    protocol = read_json(PROTOCOL_PATH)
    profiles = {p['id']: p for p in read_json(PROTOCOL_PATH)['profiles']}
    if profile != 'custom':
        require(not selected, '--controls cannot narrow a named profile')
        selected = profiles[profile]['controls']
    selected = selected or [c['id'] for c in protocol['controls']]
    require(set(selected) <= {c['id'] for c in protocol['controls']}, 'Unknown control')
    unique(selected, 'selected control')
    unique(targets, 'target')
    return {'format_version': '2', 'protocol': {'name': 'TSEP', 'version': protocol['version'],
            'sha256': digest(PROTOCOL_PATH)}, 'issued_at': datetime.now(timezone.utc).isoformat(),
            'assessor': {'name': assessor, 'mode': 'manual'},
            'scope': {'label': label, 'targets': targets, 'selection_method': selection_method,
                      'exclusions': []}, 'profile': profile, 'controls': selected,
            'claim': 'scoped-assessment', 'artifacts': [],
            'results': [{'control_id': cid, 'status': 'NT', 'evaluation_state': 'not-started',
                         'reason': 'Not assessed / Non évalué',
                         'procedure': 'No procedure executed / Aucune procédure exécutée',
                         'evaluated_targets': [], 'evidence_ids': []} for cid in selected]}


def earl(report, summary):
    """Export an embedded-context JSON-LD assertion per control about the whole scope."""
    mapping = {'C': 'passed', 'NC': 'failed', 'NA': 'inapplicable'}
    subject = {'@id': '_:scope', '@type': 'earl:TestSubject',
               'dct:title': report['scope']['label'],
               'dct:description': json.dumps(report['scope'], ensure_ascii=False)}
    graph = [subject, {'@id': '_:assertor', '@type': 'earl:Assertor',
                       'dct:title': report['assessor']['name']}]
    for result in report['results']:
        outcome = mapping.get(result['status'], 'untested' if result['evaluation_state']
                              == 'not-started' else 'cantTell')
        graph.append({'@type': 'earl:Assertion', 'earl:assertedBy': {'@id': '_:assertor'},
                      'earl:subject': {'@id': '_:scope'},
                      'earl:test': {'@id': 'urn:tsep:' + report['protocol']['version'] + ':'
                                   + result['control_id'], '@type': 'earl:TestCriterion'},
                      'earl:mode': {'@id': 'earl:' + (report['assessor']['mode']
                                    if result['evaluation_state'] != 'not-started' else 'unknownMode')},
                      'earl:result': {'@type': 'earl:TestResult',
                                      'earl:outcome': {'@id': 'earl:' + outcome},
                                      'dct:date': {'@value': report['issued_at'], '@type': 'xsd:dateTime'},
                                      'earl:info': result['reason'] + '\nEvidence: '
                                      + ', '.join(result['evidence_ids'])}})
    return {'@context': {'earl': 'http://www.w3.org/ns/earl#',
                          'dct': 'http://purl.org/dc/terms/',
                          'xsd': 'http://www.w3.org/2001/XMLSchema#'}, '@graph': graph}


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init', help='Create an untested scoped report; no network requests')
    init.add_argument('--target', action='append', required=True)
    init.add_argument('--controls', help='Comma-separated IDs for a custom scope')
    init.add_argument('--profile', choices=['custom', 'TSEP-1', 'TSEP-2', 'TSEP-3'], default='custom')
    init.add_argument('--assessor', required=True)
    init.add_argument('--label', required=True)
    init.add_argument('--selection-method', required=True)
    for command in ('validate', 'gate', 'earl'):
        p = sub.add_parser(command)
        p.add_argument('report', type=Path)
        p.add_argument('--evidence-root', type=Path,
                       help='Defaults to the directory containing the report')
    args = parser.parse_args(argv)
    try:
        if args.command == 'init':
            report = initialize(args.target, args.controls.split(',') if args.controls else None,
                                args.profile, args.assessor, args.label, args.selection_method)
            validate(report, ROOT)
            emit(report)
            return 0
        report = read_json(args.report)
        summary = validate(report, args.evidence_root or args.report.parent)
        emit(earl(report, summary) if args.command == 'earl' else summary)
        if args.command == 'gate':
            return {'GO_WITH_RESERVATIONS': 0, 'NO_GO': 1, 'INCOMPLETE': 2, 'REVIEW': 2}[summary['decision']]
        return 0
    except (Invalid, ValueError, OSError, RecursionError) as error:
        print(json.dumps({'valid': False, 'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 64


if __name__ == '__main__':
    sys.exit(main())
