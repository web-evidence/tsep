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
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile

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


def input_kinds(artifact):
    kinds = {artifact['kind']}
    if artifact['kind'] == 'webmaster-tools' and artifact.get('engine') == 'google':
        kinds.add('search-console')  # First normative engine series only.
    return kinds


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
            require(set(needed) <= set().union(*(input_kinds(artifacts[ref]) for ref in refs)),
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
        if artifact['kind'] == 'webmaster-tools':
            require(artifact.get('engine', '').strip(), 'Webmaster evidence requires its engine')
        if artifact['kind'] == 'search-console':
            require(artifact.get('engine', 'google') == 'google', 'Search Console evidence is Google-specific')
        allowed_private = {'intent'} if report['profile'] == 'TSEP-1' else {'intent', 'search-console', 'webmaster-tools'}
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
                if report['assessor']['mode'] == 'automatic':
                    rules = controls[cid].get('rules', [])
                    require(rules and all(r['automation'] == 'automatic' for r in rules),
                            'Automatic C requires every control rule to be automatic: ' + cid)
                    require('tool' in report['assessor'], 'Automatic C requires tool name and version')
                for kind in controls[cid]['required_inputs']:
                    kind_targets = set().union(*(set(artifacts[x]['targets']) for x in refs
                                                if kind in input_kinds(artifacts[x])))
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


def initialize(targets, selected, profile, assessor, label, selection_method,
               mode='manual', tool=None):
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
            'assessor': dict(name=assessor, mode=mode, **({'tool': tool} if tool else {})),
            'scope': {'label': label, 'targets': targets, 'selection_method': selection_method,
                      'exclusions': []}, 'profile': profile, 'controls': selected,
            'claim': 'scoped-assessment', 'artifacts': [],
            'results': [{'control_id': cid, 'status': 'NT', 'evaluation_state': 'not-started',
                         'reason': 'Not assessed / Non évalué',
                         'procedure': 'No procedure executed / Aucune procédure exécutée',
                         'evaluated_targets': [], 'evidence_ids': []} for cid in selected]}


def earl(report, summary):
    """Export scoped controls plus each atomic observation about its own target."""
    mapping = {'C': 'passed', 'NC': 'failed', 'NA': 'inapplicable'}
    subject = {'@id': '_:scope', '@type': 'earl:TestSubject',
               'dct:title': report['scope']['label'],
               'dct:description': json.dumps(report['scope'], ensure_ascii=False)}
    graph = [subject, {'@id': '_:assertor', '@type': 'earl:Assertor',
                       'dct:title': report['assessor']['name']}]
    for result in report['results']:
        outcome = mapping.get(result['status'], 'untested' if result['evaluation_state']
                              == 'not-started' else 'cantTell')
        parent = '_:control_' + result['control_id']
        graph.append({'@id': parent, '@type': 'earl:Assertion', 'earl:assertedBy': {'@id': '_:assertor'},
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
        atomic_mapping = {'pass': 'passed', 'fail': 'failed', 'not-applicable': 'inapplicable',
                          'inconclusive': 'cantTell'}
        for number, atom in enumerate(result.get('atomic_results', [])):
            # URL/URN targets retain their identity. Legacy free-text inventory labels
            # need an absolute IRI for JSON-LD without silently resolving a relative URL.
            target = atom['target']
            atomic_subject = {'@id': target} if re.fullmatch(r'[A-Za-z][A-Za-z0-9+.-]*:[^\s]+', target) else {
                '@id': 'urn:tsep:target:sha256:' + hashlib.sha256(target.encode('utf-8')).hexdigest(),
                'dct:title': target}
            graph.append({'@id': parent + '_atomic_' + str(number), '@type': 'earl:Assertion',
                          'dct:isPartOf': {'@id': parent},
                          'earl:assertedBy': {'@id': '_:assertor'},
                          'earl:subject': atomic_subject,
                          'earl:test': {'@id': 'urn:tsep:' + report['protocol']['version'] + ':' + atom['rule_id'],
                                        '@type': 'earl:TestCriterion'},
                          'earl:mode': {'@id': 'earl:' + report['assessor']['mode']},
                          'earl:result': {'@type': 'earl:TestResult',
                                         'earl:outcome': {'@id': 'earl:' + atomic_mapping[atom['outcome']]},
                                         'dct:date': {'@value': report['issued_at'], '@type': 'xsd:dateTime'},
                                         'earl:info': atom['reason'] + '\nEvidence: ' + ', '.join(atom['evidence_ids'])}})
    return {'@context': {'earl': 'http://www.w3.org/ns/earl#',
                          'dct': 'http://purl.org/dc/terms/',
                          'xsd': 'http://www.w3.org/2001/XMLSchema#'}, '@graph': graph}


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def save_report(path, report, root):
    """Validate before an atomic replacement; never overwrite a referenced artifact."""
    require(not path.is_symlink(), 'Report destination must not be a symlink')
    require(all(evidence_path(root, a['path']) != path.resolve() for a in report['artifacts']),
            'Report cannot be its own evidence')
    summary = validate(report, root)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                     prefix='.tsep-', delete=False) as handle:
        temporary = Path(handle.name)
        try:
            json.dump(report, handle, ensure_ascii=False, indent=2)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        except BaseException:
            temporary.unlink()
            raise
    try:
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return summary


def readable_summary(summary, language):
    fr = language == 'fr'
    synthetic = ('oui' if fr else 'yes') if summary['synthetic_evidence'] else ('non' if fr else 'no')
    return '\n'.join([
        ('Décision : ' if fr else 'Decision: ') + summary['decision'],
        ('Périmètre : ' if fr else 'Scope: ') + summary['scope']['label'],
        '%s : %s | %s : %s/%s' % (
            'Cibles' if fr else 'Targets', len(summary['scope']['targets']),
            'Contrôles sélectionnés' if fr else 'Selected controls',
            summary['selected_controls'], summary['protocol_controls']),
        ' · '.join('%s=%s' % item for item in summary['counts'].items()),
        ('Bloquants : ' if fr else 'Blocking: ') + (', '.join(summary['blocking']) or '—'),
        ('Preuves synthétiques : ' if fr else 'Synthetic evidence: ') + synthetic,
        ('Portée limitée aux cibles et contrôles déclarés ; aucune conformité globale. '
         'Vérifie cohérence et intégrité, pas la vérité des constats.' if fr else
         'Declared targets and selected controls only; no global conformity. '
         'Checks consistency and integrity, not the truth of findings.')])


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
    init.add_argument('--mode', choices=['manual', 'semiAuto', 'automatic'], default='manual')
    init.add_argument('--tool')
    init.add_argument('--tool-version')
    for command in ('validate', 'gate', 'earl', 'add-evidence', 'record'):
        p = sub.add_parser(command)
        p.add_argument('report', type=Path)
        p.add_argument('--evidence-root', type=Path,
                       help='Defaults to the directory containing the report')
        if command == 'gate':
            p.add_argument('--summary', action='store_true', help='Human-readable scoped summary')
            p.add_argument('--lang', choices=['en', 'fr'], default='en')
        if command == 'add-evidence':
            p.add_argument('--id', required=True)
            p.add_argument('--path', required=True, help='Existing file relative to evidence root')
            p.add_argument('--kind', required=True)
            p.add_argument('--target', action='append', required=True)
            p.add_argument('--observed-at', required=True)
            p.add_argument('--description', required=True)
            p.add_argument('--access', choices=['public', 'restricted', 'synthetic'], required=True)
            p.add_argument('--engine')
        if command == 'record':
            p.add_argument('--control', required=True)
            p.add_argument('--status', choices=['C', 'NC', 'NA', 'NT'], required=True)
            p.add_argument('--state', choices=['complete', 'not-started', 'inconclusive'])
            p.add_argument('--reason', required=True)
            p.add_argument('--procedure', required=True)
            p.add_argument('--target', action='append', default=[])
            p.add_argument('--evidence', action='append', default=[])
            p.add_argument('--atomic-results', type=Path, help='JSON array of atomic observations')
    args = parser.parse_args(argv)
    try:
        if args.command == 'init':
            require(bool(args.tool) == bool(args.tool_version), 'Use --tool and --tool-version together')
            report = initialize(args.target, args.controls.split(',') if args.controls else None,
                                args.profile, args.assessor, args.label, args.selection_method,
                                args.mode, {'name': args.tool, 'version': args.tool_version} if args.tool else None)
            validate(report, ROOT)
            emit(report)
            return 0
        report = read_json(args.report)
        root = args.evidence_root or args.report.parent
        summary = validate(report, root)
        if args.command in ('add-evidence', 'record'):
            if args.command == 'add-evidence':
                artifact = {'id': args.id, 'path': args.path,
                            'sha256': digest(evidence_path(root, args.path)), 'kind': args.kind,
                            'targets': args.target, 'observed_at': args.observed_at,
                            'description': args.description, 'access': args.access}
                if args.engine:
                    artifact['engine'] = args.engine
                report['artifacts'].append(artifact)
            else:
                require(args.control in report['controls'], 'Control is not selected')
                record = {'control_id': args.control, 'status': args.status,
                          'evaluation_state': args.state or ('inconclusive' if args.status == 'NT' else 'complete'),
                          'reason': args.reason, 'procedure': args.procedure,
                          'evaluated_targets': args.target, 'evidence_ids': args.evidence}
                if args.atomic_results:
                    record['atomic_results'] = read_json(args.atomic_results)
                report['results'] = [record if r['control_id'] == args.control else r for r in report['results']]
            report['issued_at'] = datetime.now(timezone.utc).isoformat()
            summary = save_report(args.report, report, root)
        if args.command == 'gate' and args.summary:
            print(readable_summary(summary, args.lang))
        else:
            emit(earl(report, summary) if args.command == 'earl' else summary)
        if args.command == 'gate':
            return {'GO_WITH_RESERVATIONS': 0, 'NO_GO': 1, 'INCOMPLETE': 2, 'REVIEW': 2}[summary['decision']]
        return 0
    except (Invalid, ValueError, OSError, RecursionError) as error:
        print(json.dumps({'valid': False, 'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 64


if __name__ == '__main__':
    sys.exit(main())
