#!/usr/bin/env python3
"""Prior TS02 owner-plan workflow; offline, without invented review. Apache-2.0."""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
from html import escape
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from adapters import captures, package
from adapters.package import inventory, json_bytes, publish, regular, seal
from conformance import redirects
from provenance.runtime import loaded_sources

VERSION = '1'
RULES = ['TS02-A01', 'TS02-A02']


def now():
    return datetime.now(timezone.utc).isoformat()


def source_files():
    return dict(captures.source_files(), **loaded_sources(ROOT, {
        'adapters/redirect_plan.py': sys.modules[__name__], 'adapters/package.py': package}))


def protocol():
    return {'version': tsep.read_json(tsep.PROTOCOL_PATH)['version'],
            'sha256': tsep.digest(tsep.PROTOCOL_PATH)}


def validate_plan(data, created_at):
    tsep.require(set(data) == {'kind', 'access', 'selection_reason', 'targets'}
                 and data['kind'] == 'tsep-redirect-plan', 'Unsupported plan document')
    tsep.require(data['access'] in captures.ACCESS, 'Missing evidence-access classification')
    tsep.require(redirects.present(data['selection_reason']), 'Explain the selected URL population')
    rows = data['targets']
    tsep.require(isinstance(rows, list) and 0 < len(rows) <= 100, 'Plan requires 1–100 targets')
    tsep.unique([t['url'] for t in rows], 'plan URL')
    for target in rows:
        tsep.require(set(target) == {'url', 'intent', 'context'},
                     'Plan contains captured data or unknown fields')
        fields = set(target['intent'])
        expected = {'declared_at', 'crawler', 'redirect_plan'}
        if 'redirect_reader' in fields:
            tsep.require(target['intent']['redirect_reader'] == redirects.HEADER_READER,
                         'Unsupported redirect reader in prior plan')
            expected.add('redirect_reader')
        tsep.require(fields == expected,
                     'Plan intent must be unreviewed and contain only TS02 expectations')
        # Reuse normative validation without storing a fictional capture timestamp.
        redirects.plan(dict(target, observed_at=created_at))
        tsep.require(tsep.timestamp(target['intent']['declared_at']) <= tsep.timestamp(created_at),
                     'Future plan declaration')
    return rows


def tasks(data):
    return [{'id': 'target-'+str(i), 'target_index': i-1, 'url': target['url'],
             'plan_sha256': redirects.review_binding(target),
             'choices': ['approved', 'rejected']}
            for i, target in enumerate(data['targets'], 1)]


def template(request, digest):
    return {'kind': 'tsep-redirect-plan-response', 'workflow_version': VERSION,
            'request_sha256': digest,
            'responses': [{'task_id': task['id'], 'plan_sha256': task['plan_sha256'],
                           'reviewer': '', 'role': 'responsible-owner', 'observed_at': '',
                           'outcome': None, 'reason': '', 'assistance': '', 'provenance': None}
                          for task in request['tasks']]}


def readable(data, request):
    parts = ['<!doctype html><html lang="fr"><meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width, initial-scale=1">',
             '<title>Plan préalable TS02 / Prior TS02 plan</title>',
             '<style>body{font:17px/1.55 system-ui;max-width:980px;margin:40px auto;padding:0 20px;'
             'color:#172538;background:#fafbfc}section{background:white;border:1px solid #bdc9d6;'
             'padding:20px;margin:22px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;'
             'font-size:14px}dt{font-weight:700}dd{margin:0 0 12px;overflow-wrap:anywhere}</style>',
             '<h1>Plan préalable de redirections TS02</h1>',
             '<p><strong>À examiner — aucune décision humaine enregistrée.</strong> '
             '/ Awaiting review — no human decision recorded.</p>',
             '<p>Vérifier la pertinence de chaque destination, les codes autorisés, les sauts et le contexte '
             'avant la collecte. / Review destinations, statuses, hop limits and context before capture.</p>',
             '<p>Sélection / Selection: '+escape(data['selection_reason'])+'</p>',
             '<p>Preuves prévues / Planned evidence: '+escape(data['access'])+'</p>',
             '<p>Préparé le / Prepared at: '+escape(request['created_at'])+'</p>']
    for task, target in zip(request['tasks'], data['targets']):
        plan = target['intent']['redirect_plan']
        parts += ['<section><h2>'+escape(task['id'])+'</h2><dl>']
        for title, value in [('Source', target['url']), ('Destination attendue / Expected destination', plan['expected_final_url']),
                             ('Redirections min–max / Redirect bounds', str(plan['min_redirects'])+'–'+str(plan['max_redirects'])),
                             ('Codes de redirection / Redirect statuses', str(plan['redirect_statuses'])),
                             ('Codes terminaux / Terminal statuses', str(plan['terminal_statuses'])),
                             ('Client HTTP / HTTP client', target['intent']['crawler']),
                             ('Intention déclarée / Intent declared', target['intent']['declared_at'])]:
            parts += ['<dt>'+title+'</dt><dd>'+escape(value)+'</dd>']
        parts += ['</dl><p>Contexte intégral / Full context:</p><pre>'+escape(json_bytes(target['context']).decode())+'</pre>',
                  '<p>Empreinte du plan et contexte / Binding:</p><pre>'+task['plan_sha256']+'</pre></section>']
    parts += ['<p>Copier response-template.json hors de ce dossier, renseigner les décisions et motifs, '
              'puis importer. Ne pas modifier ce dossier. / Copy the template outside this directory, '
              'supply your own decisions and reasons, then import. Keep this package unchanged.</p>',
              '<p>Une empreinte ne prouve ni l’identité ni la sincérité. Aucun résultat de capture ou '
              'd’indexation n’est établi par cette fiche. / Hashes do not authenticate the reviewer; '
              'this sheet establishes no capture or indexing result.</p></html>']
    return '\n'.join(parts).encode('utf-8')


def write_package(output, contents):
    output = Path(output)
    tsep.require(output.parent.is_dir() and not output.exists() and not output.is_symlink(),
                 'Choose a NEW output directory with an existing parent')
    with tempfile.TemporaryDirectory(prefix='.tsep-plan-', dir=output.parent) as folder:
        stage = Path(folder)
        for name, raw in contents.items():
            (stage/name).parent.mkdir(parents=True, exist_ok=True)
            (stage/name).write_bytes(raw)
        seal(stage)
        inventory(stage)
        publish(stage, output)


def prepare(plan_file, output):
    sources = source_files()
    raw = regular(plan_file, tsep.MAX_JSON_BYTES)
    data = tsep.parse_json(raw)
    created = now()
    validate_plan(data, created)
    request = {'kind': 'tsep-redirect-plan-request', 'workflow_version': VERSION,
               'workflow_source_files': sources, 'protocol': protocol(), 'created_at': created,
               'plan_sha256': hashlib.sha256(raw).hexdigest(), 'tasks': tasks(data)}
    encoded = json_bytes(request)
    answer = template(request, hashlib.sha256(encoded).hexdigest())
    tsep.require(source_files() == sources, 'Workflow changed during preparation')
    write_package(output, {'plan.json': raw, 'request.json': encoded,
                          'response-template.json': json_bytes(answer), 'plan.html': readable(data, request)})
    return {'prepared': True, 'targets': len(data['targets']), 'human_decisions_created': 0,
            'network_requests': 0, 'output': str(output)}


def request_data(root, reviewed=False):
    root = Path(root)
    entries = inventory(root)
    expected_files = {'plan.json', 'request.json', 'response-template.json', 'plan.html'}
    if reviewed:
        expected_files |= {'completed-response.json', 'reviewed-plan.json', 'receipt.json'}
    tsep.require(set(entries) == expected_files, 'Wrong plan-workflow package stage or unexpected files')
    request = tsep.read_json(root/'request.json')
    data = tsep.read_json(root/'plan.json')
    tsep.require(request['kind'] == 'tsep-redirect-plan-request' and request['workflow_version'] == VERSION,
                 'Unsupported prior-plan request')
    tsep.require(request['workflow_source_files'] == source_files() and request['protocol'] == protocol(),
                 'Workflow/protocol changed; retain and use the historical tools')
    tsep.require(request['plan_sha256'] == entries['plan.json'], 'Changed plan bytes')
    validate_plan(data, request['created_at'])
    tsep.require(tsep.timestamp(request['created_at']) <= tsep.timestamp(now()), 'Future request')
    tsep.require(request['tasks'] == tasks(data), 'Changed questions or population')
    tsep.require(regular(root/'plan.html') == readable(data, request), 'Readable plan differs from machine plan')
    tsep.require(tsep.read_json(root/'response-template.json') == template(request, entries['request.json']),
                 'Template contains changed or prefilled answers')
    return entries, request, data


def answers(request, data, response, request_digest, imported_at):
    tsep.require(set(response) == {'kind', 'workflow_version', 'request_sha256', 'responses'}
                 and response['kind'] == 'tsep-redirect-plan-response'
                 and response['workflow_version'] == VERSION
                 and response['request_sha256'] == request_digest, 'Response belongs to another request')
    rows = response['responses']
    tsep.require(isinstance(rows, list) and len(rows) == len(request['tasks']), 'Incomplete review population')
    tsep.unique([row['task_id'] for row in rows], 'response task')
    tsep.require({r['task_id'] for r in rows} == {t['id'] for t in request['tasks']}, 'Different review population')
    result = copy.deepcopy(data)
    for task in request['tasks']:
        row = next(r for r in rows if r['task_id'] == task['id'])
        tsep.require(set(row) == set(template(request, request_digest)['responses'][0]), 'Unknown/missing response fields')
        tsep.require(row['plan_sha256'] == task['plan_sha256'], 'Response is bound to a different plan')
        tsep.require(all(redirects.present(row[k]) for k in ('reviewer', 'observed_at', 'reason', 'assistance')),
                     'Missing reasoned human response')
        tsep.require(row['role'] == 'responsible-owner' and row['outcome'] in task['choices'], 'Missing owner decision')
        allowed = ['synthetic-exercise'] if data['access'] == 'synthetic' else ['human', 'human-assisted']
        tsep.require(row['provenance'] in allowed, 'Review provenance incompatible with evidence access')
        stamp = tsep.timestamp(row['observed_at'])
        tsep.require(tsep.timestamp(request['created_at']) <= stamp <= tsep.timestamp(imported_at),
                     'Review predates request or is future-dated')
        target = result['targets'][task['target_index']]
        target['intent']['redirect_review'] = {k: v for k, v in row.items() if k != 'task_id'}
    return result


def import_response(request_dir, response_file, output):
    request_dir = Path(request_dir)
    entries, request, data = request_data(request_dir)
    raw = regular(response_file, tsep.MAX_JSON_BYTES)
    stamp = now()
    reviewed = answers(request, data, tsep.parse_json(raw), entries['request.json'], stamp)
    receipt = {'kind': 'tsep-redirect-plan-import', 'workflow_version': VERSION,
               'imported_at': stamp, 'request_sha256': entries['request.json'],
               'response_sha256': hashlib.sha256(raw).hexdigest(),
               'reviewed_plan_sha256': hashlib.sha256(json_bytes(reviewed)).hexdigest(),
               'network_requests': 0, 'human_identity_authenticated': False}
    contents = {name: regular(request_dir/name) for name in entries}
    contents.update({'completed-response.json': raw, 'reviewed-plan.json': json_bytes(reviewed),
                     'receipt.json': json_bytes(receipt)})
    tsep.require(source_files() == request['workflow_source_files'], 'Workflow changed during import')
    write_package(output, contents)
    return receipt


def attach(reviewed_dir, input_file, output):
    """Attach supplied prior review; never rewrite raw captures, dates or intent."""
    reviewed_dir, output = Path(reviewed_dir), Path(output)
    entries, request, plan = request_data(reviewed_dir, reviewed=True)
    receipt = tsep.read_json(reviewed_dir/'receipt.json')
    tsep.require(receipt['kind'] == 'tsep-redirect-plan-import' and receipt['workflow_version'] == VERSION,
                 'Not an imported plan response')
    tsep.require(receipt['request_sha256'] == entries['request.json']
                 and receipt['response_sha256'] == entries['completed-response.json']
                 and receipt['reviewed_plan_sha256'] == entries['reviewed-plan.json'], 'Changed review receipt binding')
    tsep.require(tsep.timestamp(receipt['imported_at']) <= tsep.timestamp(now()), 'Future review import')
    reviewed = answers(request, plan, tsep.read_json(reviewed_dir/'completed-response.json'),
                       entries['request.json'], receipt['imported_at'])
    tsep.require(tsep.read_json(reviewed_dir/'reviewed-plan.json') == reviewed, 'Reviewed plan differs from supplied response')
    raw = regular(input_file, tsep.MAX_JSON_BYTES)
    original = tsep.parse_json(raw)
    tsep.require(set(original) == {'input_version', 'rules', 'targets'} and original['input_version'] in ('1', '2')
                 and original['rules'] == RULES, 'Attach requires a TS02-only capture input with both rules')
    rows = original['targets']
    tsep.require(isinstance(rows, list) and len(rows) == len(plan['targets']), 'Different capture population')
    tsep.require([t['url'] for t in rows] == [t['url'] for t in plan['targets']], 'Different capture URLs/order')
    result = copy.deepcopy(original)
    for old, expected, new, approved in zip(rows, plan['targets'], result['targets'], reviewed['targets']):
        tsep.require(set(old) == {'url', 'intent', 'context', 'observed_at', 'http'}, 'Unsupported capture fields or prefilled review')
        tsep.require({k: old[k] for k in expected} == expected, 'Capture intent/context differs from prior plan')
        tsep.require(tsep.timestamp(receipt['imported_at']) <= tsep.timestamp(old['observed_at']) <= tsep.timestamp(now()),
                     'Capture predates review import or is future-dated; do not backdate approval')
        new['intent'] = approved['intent']
    tsep.require(output.parent.is_dir() and not output.exists() and not output.is_symlink(),
                 'Choose a NEW output directory with an existing parent')
    with tempfile.TemporaryDirectory(prefix='.tsep-plan-capture-', dir=output.parent) as folder:
        stage = Path(folder)
        for name in entries:
            (stage/name).parent.mkdir(parents=True, exist_ok=True)
            (stage/name).write_bytes(regular(reviewed_dir/name))
        (stage/'original-captures.json').write_bytes(raw)
        (stage/'reviewed-captures.json').write_bytes(json_bytes(result))
        summary = captures.build(stage/'reviewed-captures.json', stage/'bundle',
            assessor='; '.join(dict.fromkeys(t['intent']['redirect_review']['reviewer'] for t in reviewed['targets'])),
            label='TS02 prior owner plan / Plan préalable du responsable',
            selection_method=plan['selection_reason'], access=plan['access'], mode='semiAuto',
            exclusions=['Only declared HTTP trajectories; no content equivalence, client navigation or indexing conclusion.',
                        'Supplied owner judgments and timestamps; no independent reviewer/capture authentication.'])
        result_meta = {'kind': 'tsep-redirect-plan-capture', 'workflow_version': VERSION,
                       'original_captures_sha256': hashlib.sha256(raw).hexdigest(),
                       'request_sha256': entries['request.json'], 'response_sha256': entries['completed-response.json'],
                       'decision': summary['decision'], 'network_requests': 0,
                       'capture_collected_by_workflow': False}
        (stage/'attachment.json').write_bytes(json_bytes(result_meta))
        seal(stage)
        inventory(stage)
        tsep.require(source_files() == request['workflow_source_files'], 'Workflow changed during attachment')
        publish(stage, output)
    return result_meta


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('prepare', 'import-response', 'attach'):
        command = sub.add_parser(name)
        command.add_argument('source', type=Path)
        command.add_argument('--output', type=Path, required=True)
        if name == 'import-response':
            command.add_argument('--response', type=Path, required=True)
        elif name == 'attach':
            command.add_argument('--captures', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'prepare':
            result = prepare(args.source, args.output)
        elif args.command == 'import-response':
            result = import_response(args.source, args.response, args.output)
        else:
            result = attach(args.source, args.captures, args.output)
        print(json_bytes(result).decode(), end='')
        return 0
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as error:
        print(str(error), file=sys.stderr)
        return 64


if __name__ == '__main__':
    sys.exit(main())
