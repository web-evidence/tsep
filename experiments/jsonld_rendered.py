#!/usr/bin/env python3
"""Attributed supplied rendered JSON-LD, source comparison and exact offline replay.

Apache-2.0. No browser/network collection, factual validation or TSEP outcome.
"""
import argparse
import base64
from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from conformance import evaluate, http, structured_dom
from experiments import jsonld_html as html
from experiments import jsonld_processing as processor
from experiments import rendered_metadata, rendered_canonical
from provenance import runtime

need, sha, serialized = processor.need, processor.sha, processor.serialized
PROFILE = 'structured-rendered-jsonld-exact-type-v1'
MAX_INPUT = 32 * 1024 * 1024
MAX_OUTPUT = 128 * 1024 * 1024
MAX_STATES = 16
ERRORS = (ValueError, KeyError, TypeError, OSError, RecursionError, OverflowError)


def identity(root=ROOT):
    modules = {'experiments/jsonld_rendered.py': sys.modules[__name__],
        'conformance/structured_dom.py': structured_dom, 'conformance/evaluate.py': evaluate,
        'conformance/http.py': http, 'experiments/rendered_metadata.py': rendered_metadata,
        'experiments/rendered_canonical.py': rendered_canonical,
        'provenance/runtime.py': runtime, 'tsep.py': tsep}
    return dict(html.identity(root), **runtime.loaded_sources(root, modules),
                **{rendered_metadata.SCRIPT: sha((root/rendered_metadata.SCRIPT).read_bytes())})


def named(value):
    return type(value) is str and 0 < len(value) <= 4096 and bool(value.strip())


def native_http(hops, final_url, crawler, start_url=None):
    need(type(hops) is list and 1 <= len(hops) <= 20, 'Missing or excessive HTTP trace')
    need(all(type(h) is dict for h in hops), 'Malformed HTTP trace member')
    need(named(crawler), 'Missing HTTP client')
    actual, status, headers, body = evaluate.trace(hops, start_url or hops[0]['url'], crawler)
    need(actual == final_url and status == 200, 'Expected final complete HTTP 200 representation missing')
    raw = body.encode('utf-8') if isinstance(body, str) else body
    html.scripts.http.decode(raw, headers.get('content-type', []))
    return raw, headers['content-type']


def surface(request):
    """Interpret one supplied state; this alone does not establish a prior plan."""
    need(type(request) is dict and set(request) == {'final_url', 'http', 'crawler',
        'http_received_at', 'window_end', 'state', 'contexts'}, 'Unexpected rendered surface request')
    need(len(serialized(request)) <= MAX_INPUT, 'Rendered request byte bound exceeded')
    native_http(request['http'], request['final_url'], request['crawler'])
    state = request['state']
    need(type(state) is dict and named(state.get('id')), 'Missing named rendered state')
    required = {'id', 'observed_at', 'complete', 'errors', 'javascript_enabled',
                'browser', 'browser_version', 'structured_dom'}
    need(required <= set(state) <= required | {'scenario', 'dom'}, 'Unexpected supplied state fields')
    when = tsep.timestamp(state['observed_at'])
    need(tsep.timestamp(request['http_received_at']) <= when <= tsep.timestamp(request['window_end']),
         'Rendered state outside supplied HTTP/window chronology')
    need(state.get('complete') is True and state.get('errors') == [] and
         state.get('javascript_enabled') is True and named(state.get('browser')) and
         named(state.get('browser_version')), 'Incomplete state or missing browser context')
    supplied = structured_dom.Surface(state, request['final_url'], request['http'], request['crawler'])
    tree = supplied.tree
    processor.prepare({'documents': [dict(id='preflight', raw_json='{}',
        base_iri=tree['base_uri'], contexts=request['contexts'])]})
    nodes = tree['nodes']
    # The transport historically permits null character data. It cannot mean empty text here.
    need(all(type(n['data']) is str for n in nodes if n['type'] in (3, 8)),
         'Missing character data in supplied tree')
    facts = {n['node_id']: n for n in supplied.facts['elements']}
    children = {}
    for n in nodes[1:]:
        if n['edge'] == 'child': children.setdefault(n['parent'], []).append(n['id'])
    scripts = []
    for n in nodes:
        if n['type'] != 1 or n['name'] != 'script': continue
        fact = facts[n['id']]
        parts = []; pending = list(reversed(children.get(n['id'], [])))
        while pending:
            child = nodes[pending.pop()]
            if child['type'] == 3: parts.append(dict(node_id=child['id'], data=child['data']))
            pending.extend(reversed(children.get(child['id'], [])))
        # No HTML reparsing, entity decoding, normalization or shadow/slot flattening.
        scripts.append(dict(node_id=n['id'], name='script', namespace=n['namespace'],
            attributes=[dict(name=a['local_name'], namespace=a['namespace'], prefix=None,
                             value=a['value']) for a in n['attributes']],
            template_path=[], path=fact['path'], position=fact['position'],
            payload_parts=parts, payload=''.join(p['data'] for p in parts)))
    acquisition = state['structured_dom']['acquisition']
    return dict(kind='supplied-rendered-script-inventory', version='1', complete=True,
        scripts=scripts, boundaries=supplied.facts['boundaries'],
        metadata=supplied.facts['metadata'], base_uri=tree['base_uri'],
        snapshot_sha256=state['structured_dom']['snapshot_sha256'],
        acquisition=acquisition['kind'], navigation_id=acquisition['navigation_id'],
        observed_at=state['observed_at'], browser=state['browser'], browser_version=state['browser_version'],
        scope=supplied.detail, base_attribution='supplied snapshot document.baseURI; not independently authenticated',
        authored=acquisition['kind'] == 'authored-synthetic')


def combine(inventory):
    # Reuse the exact HTML combination semantics without modifying the historical reader.
    ordinary = dict(inventory, scripts=[s for s in inventory['scripts'] if s['position'] != 'open-shadow'])
    result = html.combine(ordinary)
    excluded = [dict(node_id=s['node_id'], selection='excluded-open-shadow',
        payload_sha256=sha(s['payload']), status='not-selected', reason=None, root_items=None)
        for s in inventory['scripts'] if s['position'] == 'open-shadow']
    result['diagnostics'] = sorted(result['diagnostics'] + excluded, key=lambda d: d['node_id'])
    return result


def validate_request(request):
    need(type(request) is dict and set(request) == {'plan', 'http', 'http_received_at', 'contexts', 'states'},
         'Unexpected rendered workflow fields')
    need(len(serialized(request)) <= MAX_INPUT, 'Workflow input byte bound exceeded')
    p = request['plan']
    need(type(p) is dict and set(p) == {'format', 'version', 'declared_at', 'window_start', 'window_end',
        'start_url', 'final_url', 'crawler', 'source_base_iri', 'states'}, 'Unexpected rendered plan fields')
    need(p['format'] == 'jsonld-rendered-plan' and p['version'] == '1', 'Unknown plan profile')
    need(tsep.timestamp(p['declared_at']) <= tsep.timestamp(p['window_start']) <=
         tsep.timestamp(request['http_received_at']) <= tsep.timestamp(p['window_end']),
         'Plan or HTTP/window chronology inconsistent')
    for key in ('start_url', 'final_url', 'source_base_iri'): processor.absolute(p[key])
    processor.prepare({'documents': [dict(id='preflight', raw_json='{}',
        base_iri=p['source_base_iri'], contexts=request['contexts'])]})
    need(type(p['states']) is list and 1 <= len(p['states']) <= MAX_STATES, 'Expected 1–16 planned states')
    seen = set()
    for s in p['states']:
        need(type(s) is dict and set(s) == {'id', 'browser', 'browser_version', 'scenario'} and
             all(named(v) for v in s.values()) and len(s['id']) <= 128 and s['id'] not in seen,
             'Invalid/repeated planned state or browser/scenario'); seen.add(s['id'])
    need(type(request['states']) is list and len(request['states']) <= MAX_STATES and
         all(type(s) is dict and named(s.get('id')) for s in request['states']), 'Invalid supplied state population')
    raw, types = native_http(request['http'], p['final_url'], p['crawler'], p['start_url'])
    return raw, types


def payloads(inventory, reading):
    if not inventory or not reading or not inventory.get('complete'): return None
    if any(d['selection'] == 'unresolved-type-variant' for d in reading['diagnostics']): return None
    by_id = {s['node_id']: s for s in inventory['scripts']}
    return [by_id[d['node_id']]['payload'] for d in reading['diagnostics'] if d['selection'] == 'selected']


def compare(source_inventory, source_reading, rendered_inventory, rendered_reading, source_base):
    left = payloads(source_inventory, source_reading)
    right = payloads(rendered_inventory, rendered_reading)
    result = dict(status='unavailable', source_count=None, rendered_count=None,
        added_payloads=None, removed_payloads=None, order_only_difference=None, same_base_parameter=None,
        meaning='Exact selected text sequence only; no cross-surface node identity, semantic equivalence, cause or SEO verdict.')
    if left is None or right is None: return result
    a, b = Counter(left), Counter(right)
    result.update(status='equal' if left == right else 'different', source_count=len(left), rendered_count=len(right),
        added_payloads=[dict(sha256=sha(v), count=n) for v, n in sorted((b-a).items())],
        removed_payloads=[dict(sha256=sha(v), count=n) for v, n in sorted((a-b).items())],
        order_only_difference=left != right and a == b,
        same_base_parameter=source_base == rendered_inventory['base_uri'])
    return result


def observe(request, *, node, root=ROOT):
    raw, types = validate_request(request); before = identity(root); p = request['plan']
    source = None; source_error = None
    try:
        source = html.observe(dict(body_base64=base64.b64encode(raw).decode(), content_types=types,
            base_iri=p['source_base_iri'], contexts=request['contexts']), node=node, root=root)
    except ERRORS as error: source_error = str(error)
    rows = []; documents = []
    for planned in p['states']:
        row = dict(id=planned['id'], status='unavailable', reason=None, inventory=None, reading=None,
                   processing_index=None, comparison={})
        rows.append(row)
        try:
            candidates = [s for s in request['states'] if s['id'] == planned['id']]
            need(len(candidates) == 1, 'Missing or duplicate required state')
            state = candidates[0]
            need(all(state.get(k) == planned[k] for k in ('browser', 'browser_version', 'scenario')),
                 'Supplied browser/scenario differs from prior plan')
            inv = surface(dict(final_url=p['final_url'], http=request['http'], crawler=p['crawler'],
                http_received_at=request['http_received_at'], window_end=p['window_end'],
                state=state, contexts=request['contexts']))
            row['inventory'] = inv; reading = combine(inv); row['reading'] = reading
            row['status'] = reading['status']
            if reading['status'] == 'prepared':
                row['processing_index'] = len(documents)
                documents.append(dict(id=planned['id'], raw_json=reading['combined_json'],
                    base_iri=inv['base_uri'], contexts=request['contexts']))
            del reading['combined_json']
        except ERRORS as error: row['reason'] = str(error)
        for mode in ('enabled', 'disabled'):
            row['comparison'][mode] = compare(source['source']['readings'][mode] if source else None,
                source['readings'][mode] if source else None, row['inventory'], row['reading'], p['source_base_iri'])
    # One process per state preserves independent failures and the processor's input budget.
    processing = []
    for row in rows:
        if row['processing_index'] is None: continue
        doc = documents[row['processing_index']]
        item = dict(state_id=row['id'], observation=None, error=None)
        try:
            item['observation'] = processor.observe({'documents': [doc]}, node=node, root=root)
            row['status'] = 'processed' if item['observation']['documents'][0]['status'] == 'observed' else 'processing-unavailable'
        except ERRORS as error:
            item['error'] = str(error); row['status'] = 'processing-unavailable'
        row['reading']['status'] = row['status']; processing.append(item)
    expected = {s['id'] for s in p['states']}
    unexpected = [dict(id=s['id'], input_index=i, input_sha256=sha(serialized(s)))
                  for i, s in enumerate(request['states']) if s['id'] not in expected]
    need(identity(root) == before, 'Rendered workflow source changed during execution')
    result = dict(kind='unapplied-rendered-jsonld', version='1', normative_effect='none', profile=PROFILE,
        input=request, input_sha256=sha(serialized(request)), source_sha256=before,
        runtime=runtime.runtime_identity(), source=source, source_error=source_error,
        states=rows, unexpected_states=unexpected, processing=processing,
        limitations=[
            'Supplied plan dates, context, HTTP/DOM attribution and document.baseURI are checked, not authenticated.',
            'Authored trees remain synthetic. No browser or network request occurs; this does not qualify a real capture chain.',
            'Source uses two static hypotheses and a supplied base. Each rendered state uses its supplied snapshot base; neither replaces the other.',
            'Text nodes are concatenated without HTML reparsing. Comments, shadow edges and slots do not contribute to light-tree script text.',
            'Open-shadow scripts are inventoried separately. Frame documents, template fragments and closed shadow are outside coverage.',
            'Unknown required states and unexpected supplied states remain explicit. Source diagnostics survive rendered failures.',
            'Exact payload differences do not identify a script across states, prove a JavaScript cause or establish semantic/factual contradiction.',
            'No Schema.org validity, rich-result eligibility, whole-page absence, TSEP result, indexing or ranking is established.'])
    need(len(serialized(result)) <= MAX_OUTPUT, 'Rendered observation output bound exceeded')
    return result


def replay(observation, *, node, root=ROOT):
    need(type(observation) is dict and len(serialized(observation)) <= MAX_OUTPUT, 'Invalid retained observation')
    need(observation.get('source_sha256') == identity(root), 'Retained rendered workflow sources differ')
    need(observation.get('input_sha256') == sha(serialized(observation['input'])), 'Retained rendered input differs')
    actual = observe(observation['input'], node=node, root=root)
    need(actual == observation, 'Rendered observation replay differs; retain both attempts')
    return actual


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path); parser.add_argument('--node', required=True)
    parser.add_argument('--replay', action='store_true'); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        need(not args.output.exists() and not args.output.is_symlink(), 'Choose a new output path')
        limit = MAX_OUTPUT if args.replay else MAX_INPUT
        with args.input.open('rb') as f: raw = f.read(limit+1)
        need(len(raw) <= limit, 'Input byte bound exceeded')
        result = (replay if args.replay else observe)(processor.strict_json(raw), node=args.node)
        with args.output.open('x', encoding='utf-8') as f: json.dump(result, f, ensure_ascii=False, indent=2); f.write('\n')
        print(json.dumps(dict(states=[dict(id=s['id'], status=s['status']) for s in result['states']],
                              unexpected=len(result['unexpected_states'])))); return 0
    except ERRORS as error:
        print(json.dumps(dict(kind='rendered-jsonld-unavailable', reason=str(error), normative_effect='none')), file=sys.stderr)
        return 64


if __name__ == '__main__': sys.exit(main())
