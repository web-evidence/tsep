#!/usr/bin/env python3
"""Prepare blank evidence-bound reviews and import completed responses. Apache-2.0.

Workflow only: no generated human opinion, no reviewer authentication, no changes
of normative semantics. Supported records: TS04/TS07 access and TS10 content review.
"""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from adapters import captures, package
from adapters.package import inventory, json_bytes, publish, regular, seal
from conformance.canonical import content_binding
from conformance.robots_control import access_binding
from provenance.runtime import loaded_sources

VERSION = '2'
ACCESS = ('public', 'restricted', 'synthetic')


def source_files():
    return dict(captures.source_files(), **loaded_sources(ROOT, {
        'adapters/review.py': sys.modules[__name__], 'adapters/package.py': package}))


def now():
    return datetime.now(timezone.utc).isoformat()


def tasks(data):
    result = []
    for index, target in enumerate(data['targets'], 1):
        for rule, field, title in (
            ('TS04-A02', 'resources_review', 'Accès aux ressources nécessaires / Required resource access'),
            ('TS07-A02', 'access_review', 'Accès à la directive / Access to the directive'),
            ('TS10-A02', 'content_review', 'Compatibilité du contenu / Content compatibility')):
            if rule not in data['rules']:
                continue
            if rule == 'TS04-A02':
                resources = target['intent']['robots_plan']['resources']
                urls = [row['url'] for row in resources if row['required']]
                if not urls:
                    continue  # Prior inventory exemption is not fabricated after capture.
                tsep.require(len(urls) == len(set(urls)), 'Duplicate required resources')
                choices = ['no-obstacle', 'obstacle', 'inconclusive']
                prompt = ('Examiner chaque réponse et son contenu : obstacle prouvé, absence d’obstacle observé ou doute. '
                          'Le statut 200 seul ne suffit pas. / Review each actual resource response and content; '
                          'a 200 status alone is insufficient. Explain evidence of an obstacle or any uncertainty.')
            elif rule == 'TS10-A02':
                members = target['intent']['canonical']['members']
                urls = [row['url'] for row in members]
                tsep.require(urls and len(urls) == len(set(urls)), 'Missing/duplicate canonical members')
                choices = ['compatible', 'incompatible', 'inconclusive']
                prompt = ('Comparer chaque membre à la préférence déclarée, y compris la préférence elle-même ; '
                          'justifier avec les contenus examinés. / Compare each member with the declared preference and explain.')
            else:
                urls = [target['url']]
                choices = ['no-obstacle', 'unresolved-challenge']
                prompt = ('Examiner la réponse du client de test et ses limites d’accès. Une réponse 200 ne suffit pas. '
                          'Un obstacle ou doute non résolu reste unresolved-challenge. / Review observed test-client access; '
                          '200 alone is insufficient. Unresolved obstacles remain inconclusive.')
            result.append({'id': 'target-'+str(index)+'-'+rule, 'target_index': index-1,
                'target': target['url'], 'rule_id': rule, 'field': field, 'title': title,
                'question': prompt, 'comparison_urls': urls, 'choices': choices})
    tsep.require(result, 'No supported human review task; select TS04-A02, TS07-A02 or TS10-A02 with applicable resources')
    return result


def response(task):
    return {'task_id': task['id'], 'reviewer': '', 'observed_at': '', 'provenance': None,
            'assistance': '', 'examined_evidence': [], 'reason': '',
            'comparisons': [{'url': url, 'outcome': None, 'reason': ''} for url in task['comparison_urls']]}


def prepare(bundle, output):
    sources = source_files()
    bundle, output = Path(bundle), Path(output)
    entries = inventory(bundle)
    report = tsep.read_json(bundle/'report.json')
    tsep.validate(report, bundle)
    meta = tsep.read_json(bundle/'import.json')
    tsep.require(meta['input_sha256'] == entries['input.json'], 'Input/import binding mismatch')
    tsep.require(meta['access'] in ACCESS, 'Missing evidence-access classification')
    raw = regular(bundle/'input.json', tsep.MAX_JSON_BYTES)
    data = tsep.parse_json(raw)
    planned = tasks(data)
    request = {'kind': 'tsep-review-request', 'workflow_version': VERSION,
               'workflow_source_files': sources,
               'created_at': now(), 'protocol': report['protocol'],
               'input_sha256': entries['input.json'], 'access': meta['access'],
               'original_manifest_sha256': tsep.digest(bundle/'SHA256SUMS'),
               'tasks': planned}
    tsep.require(output.parent.is_dir() and not output.exists() and not output.is_symlink(),
                 'Choose a NEW output directory with an existing parent')
    with tempfile.TemporaryDirectory(prefix='.tsep-review-', dir=output.parent) as folder:
        stage = Path(folder)
        (stage/'input.json').write_bytes(raw)
        (stage/'evidence').mkdir()
        for task in planned:
            name = 'evidence/'+task['id']+'.json'
            (stage/name).write_bytes(json_bytes(data['targets'][task['target_index']]))
            task['evidence'] = [{'path': name, 'sha256': tsep.digest(stage/name)}]
        (stage/'request.json').write_bytes(json_bytes(request))
        template = {'kind': 'tsep-review-response', 'workflow_version': VERSION,
                    'request_sha256': tsep.digest(stage/'request.json'),
                    'responses': [response(task) for task in planned]}
        (stage/'response-template.json').write_bytes(json_bytes(template))
        instructions = '''Revue humaine TSEP / TSEP human review

Aucune décision n’est préremplie. Les preuves restent dans input.json et evidence/.
No decision is prefilled. Original supplied records stay in input.json and evidence/.

1. Copier response-template.json HORS de ce dossier sous un nouveau nom.
   Copy response-template.json OUTSIDE this sealed directory to a new file.
2. Lire request.json, puis chaque pièce evidence/. Ne pas modifier leurs octets.
   Read request.json and every listed evidence file; leave them unchanged.
3. Remplir soi-même les réponses : nom, date avec fuseau, motif et décision par URL.
   Fill in your own name, dated observation with timezone, reasons and per-URL decisions.
4. provenance : human, human-assisted, ou synthetic-exercise uniquement pour un exercice.
   assistance décrit l’aide réellement utilisée (ou « aucune » / « none »).
   Dans examined_evidence, recopier les objets path/sha256 des pièces réellement examinées.
   No empty/default decision is accepted; list the exact evidence objects you examined.
5. Importer le fichier rempli avec adapters/review.py import ; un nouveau paquet est créé.
   Import using adapters/review.py import; the previous input and reviews are preserved.

Les autres limites (HTML non pris en charge, rendu manquant, robots incomplet) restent
indéterminées. Cette fiche ne remplace ni le plan de rendu ni une revue d’exemption.
Une revue compatible ne garantit donc pas C. Les exercices restent synthétiques.
Other gaps remain unresolved. This does not create a rendering plan or exemption;
a positive review does not guarantee C. Synthetic exercises remain synthetic.

Le logiciel vérifie liens, dates et complétude ; il ne prouve pas que les pièces ont été
lues ni que le nom correspond à la personne. Les empreintes ne sont pas des signatures.
Software checks bindings/dates/completeness, not reviewer identity or truth of the review.
Hashes are not signatures. Do not treat an AI-generated response as human review.
'''
        (stage/'READ-ME.txt').write_text(instructions, encoding='utf-8')
        seal(stage)
        inventory(stage)
        tsep.require(source_files() == sources, 'Review workflow sources changed during preparation')
        publish(stage, output)
    return {'prepared': True, 'tasks': len(planned), 'human_decisions_created': 0, 'output': str(output)}


def completed(request, answered):
    tsep.require(set(answered) == {'kind', 'workflow_version', 'request_sha256', 'responses'}
                 and answered['kind'] == 'tsep-review-response' and answered['workflow_version'] == VERSION,
                 'Unsupported review response')
    rows = answered['responses']
    tsep.require(isinstance(rows, list) and len(rows) == len(request['tasks']), 'Missing/extra review responses')
    tsep.unique([r['task_id'] for r in rows], 'review task')
    tsep.require({r['task_id'] for r in rows} == {t['id'] for t in request['tasks']}, 'Different review population')
    current = tsep.timestamp(now())
    result = {}
    for task in request['tasks']:
        row = next(r for r in rows if r['task_id'] == task['id'])
        tsep.require(set(row) == set(response(task)), 'Unknown/missing response fields')
        for field in ('reviewer', 'observed_at', 'assistance', 'reason'):
            tsep.require(isinstance(row[field], str) and row[field].strip(), 'Missing human response: '+field)
        stamp = tsep.timestamp(row['observed_at'])
        tsep.require(tsep.timestamp(request['created_at']) <= stamp <= current, 'Review predates request or is future-dated')
        allowed = ['synthetic-exercise'] if request['access'] == 'synthetic' else ['human', 'human-assisted']
        tsep.require(row['provenance'] in allowed, 'Review provenance incompatible with evidence access')
        tsep.require(row['examined_evidence'] == task['evidence'], 'Review must reference the exact examined evidence')
        comparisons = row['comparisons']
        tsep.require(isinstance(comparisons, list) and len(comparisons) == len(task['comparison_urls']), 'Incomplete comparison population')
        tsep.unique([r['url'] for r in comparisons], 'review comparison')
        tsep.require({r['url'] for r in comparisons} == set(task['comparison_urls']), 'Different comparison URLs')
        for item in comparisons:
            tsep.require(set(item) == {'url', 'outcome', 'reason'} and item['outcome'] in task['choices']
                         and isinstance(item['reason'], str) and item['reason'].strip(), 'Missing/unsupported reasoned decision')
        result[task['id']] = row
    return result


def apply_review(request_dir, response_file, output):
    request_dir, output = Path(request_dir), Path(output)
    entries = inventory(request_dir)
    request = tsep.read_json(request_dir/'request.json')
    tsep.require(request['kind'] == 'tsep-review-request' and request['workflow_version'] == VERSION,
                 'Unsupported review request')
    sources = source_files()
    tsep.require(request['workflow_source_files'] == sources, 'Review workflow changed; use its historical tool archive')
    tsep.require(request['input_sha256'] == entries['input.json'], 'Changed review input')
    raw_answer = regular(response_file, tsep.MAX_JSON_BYTES)
    answered = tsep.parse_json(raw_answer)
    tsep.require(answered['request_sha256'] == entries['request.json'], 'Response belongs to different/stale request')
    original = tsep.read_json(request_dir/'input.json')
    planned = tasks(original)
    expected_tasks = copy.deepcopy(planned)
    for task in expected_tasks:
        name = 'evidence/'+task['id']+'.json'
        expected = json_bytes(original['targets'][task['target_index']])
        tsep.require(regular(request_dir/name) == expected, 'Evidence differs from original input')
        task['evidence'] = [{'path': name, 'sha256': hashlib.sha256(expected).hexdigest()}]
    tsep.require(request['tasks'] == expected_tasks, 'Review questions/population were changed')
    tsep.require(request['protocol']['sha256'] == tsep.digest(tsep.PROTOCOL_PATH),
                 'Protocol changed; prepare a new review request for the new assessment')
    answers = completed(request, answered)
    data = copy.deepcopy(original)
    for task in request['tasks']:
        answer = answers[task['id']]
        target = data['targets'][task['target_index']]
        details = {key: answer[key] for key in ('reviewer', 'observed_at', 'reason', 'provenance', 'assistance', 'examined_evidence')}
        details['workflow_input_sha256'] = entries['input.json']
        if task['field'] == 'resources_review':
            for comparison in answer['comparisons']:
                docs = [d for d in target.get('documents', []) if d.get('url') == comparison['url']]
                tsep.require(len(docs) == 1, 'Required resource response missing or ambiguous')
                doc = docs[0]
                tsep.require(tsep.timestamp(answer['observed_at']) >= tsep.timestamp(doc['observed_at']),
                             'Review predates resource capture')
                doc['access_review'] = dict(details, outcome=comparison['outcome'], reason=comparison['reason'],
                                            source_sha256=access_binding(target, doc))
            continue
        elif task['field'] == 'access_review':
            tsep.require(tsep.timestamp(answer['observed_at']) >= tsep.timestamp(target['observed_at']),
                         'Review predates access observation')
            details['outcome'] = answer['comparisons'][0]['outcome']
            details['comparison_reason'] = answer['comparisons'][0]['reason']
        else:
            # TS10 observed_at closes the assessment interval; source and DOM
            # capture dates remain unchanged. The original end date is retained.
            tsep.require(tsep.timestamp(answer['observed_at']) >= tsep.timestamp(target['observed_at']),
                         'Review predates previous assessment end')
            for doc in target.get('documents', []):
                tsep.require(tsep.timestamp(answer['observed_at']) >= tsep.timestamp(doc['observed_at']), 'Review predates content capture')
                for state in doc.get('render', {}).get('states', []):
                    tsep.require(tsep.timestamp(answer['observed_at']) >= tsep.timestamp(state['observed_at']), 'Review predates rendered capture')
            details.update(mode='manual', source_sha256=content_binding(target), comparisons=answer['comparisons'],
                           previous_assessment_end=target['observed_at'])
            target['observed_at'] = answer['observed_at']
        target[task['field']] = details
    tsep.require(output.parent.is_dir() and not output.exists() and not output.is_symlink(),
                 'Choose a NEW output directory with an existing parent')
    with tempfile.TemporaryDirectory(prefix='.tsep-reviewed-', dir=output.parent) as folder:
        stage = Path(folder)
        (stage/'original-input.json').write_bytes(regular(request_dir/'input.json'))
        (stage/'request.json').write_bytes(regular(request_dir/'request.json'))
        (stage/'completed-response.json').write_bytes(raw_answer)
        (stage/'reviewed-input.json').write_bytes(json_bytes(data))
        (stage/'evidence').mkdir()
        for task in request['tasks']:
            for evidence in task['evidence']:
                (stage/evidence['path']).write_bytes(regular(request_dir/evidence['path']))
        mode = 'manual' if any(t['rule_id'].startswith('TS10') for t in request['tasks']) else 'semiAuto'
        summary = captures.build(stage/'reviewed-input.json', stage/'bundle',
            assessor='; '.join(dict.fromkeys(a['reviewer'] for a in answers.values())),
            label='Evidence-bound supplied review / Revue fournie liée aux preuves',
            selection_method='Same explicit input population; new supplied review, not a new capture',
            access=request['access'], mode=mode,
            exclusions=['No authentication of reviewer identity or truth; unsupported/missing evidence remains unresolved'])
        receipt = {'kind': 'tsep-review-import', 'workflow_version': VERSION,
                   'workflow_source_files': sources,
                   'original_input_sha256': entries['input.json'],
                   'reviewed_input_sha256': tsep.digest(stage/'reviewed-input.json'),
                   'request_sha256': entries['request.json'], 'response_sha256': hashlib.sha256(raw_answer).hexdigest(),
                   'provenance': [a['provenance'] for a in answers.values()],
                   'decision': summary['decision'], 'network_requests': 0,
                   'limitations': 'Supplied judgments, not authenticated human identity; source captures and previous input retained unchanged.'}
        (stage/'receipt.json').write_bytes(json_bytes(receipt))
        seal(stage)
        inventory(stage)
        tsep.require(source_files() == sources, 'Review workflow sources changed during import')
        publish(stage, output)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    prepare_args = sub.add_parser('prepare')
    prepare_args.add_argument('bundle', type=Path)
    prepare_args.add_argument('--output', type=Path, required=True)
    import_args = sub.add_parser('import')
    import_args.add_argument('request', type=Path)
    import_args.add_argument('--response', type=Path, required=True)
    import_args.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        value = prepare(args.bundle, args.output) if args.command == 'prepare' else apply_review(args.request, args.response, args.output)
        print(json_bytes(value).decode(), end='')
        return 0
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as error:
        print(str(error), file=sys.stderr)
        return 64


if __name__ == '__main__':
    sys.exit(main())
