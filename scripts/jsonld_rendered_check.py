#!/usr/bin/env python3
"""Qualify frozen authored supplied-rendered JSON-LD cases with explicit Node.

Apache-2.0. This runs the readers, never a browser or an external HTTP collector.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments import jsonld_rendered as workflow
from scripts.source_http_check import fixture


def save(path, value):
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n')


def surface_projection(actual):
    return dict(usable_surface=True,
        ordinary_html_script_payloads=[s['payload'] for s in actual['scripts']
            if s['namespace'] == workflow.rendered_metadata.HTML and s['position'] != 'open-shadow'],
        open_shadow_script_payloads=[s['payload'] for s in actual['scripts'] if s['position'] == 'open-shadow'],
        foreign_script_payloads=[s['payload'] for s in actual['scripts']
            if s['namespace'] != workflow.rendered_metadata.HTML],
        base_uri=actual['base_uri'], authored=actual['authored'])


def projection(actual):
    states = []
    for s in actual['states']:
        first_id = None
        if s['processing_index'] is not None:
            p = actual['processing'][s['processing_index']]['observation']
            graph = p['documents'][0]['flattened'] if p else None
            if graph: first_id = graph[0].get('@id')
        states.append(dict(id=s['id'], status=s['status'],
            comparison=[s['comparison'][m]['status'] for m in ('enabled', 'disabled')],
            selected_count=s['reading']['selected_count'] if s['reading'] else None,
            base_uri=s['inventory']['base_uri'] if s['inventory'] else None, first_id=first_id))
    return dict(accepted=True, source_status=[actual['source']['readings'][m]['status']
        if actual['source'] else 'unavailable' for m in ('enabled', 'disabled')], states=states,
        unexpected_states=[s['id'] for s in actual['unexpected_states']])


def check(node, output_dir):
    output_dir.mkdir(parents=True, exist_ok=False)
    rows = []; failures = []; replays = []
    for name in ('jsonld-rendered-surfaces-v1.json', 'jsonld-rendered-workflow-v1.json',
                 'jsonld-rendered-boundaries-v1.json', 'jsonld-rendered-dom-boundaries-v1.json'):
        oracle = fixture(name); save(output_dir/name, oracle)
        for case in oracle['cases']:
            kind = 'surface' if 'surfaces' in name else 'workflow'; stem = kind+'-'+case['id']
            actual = None; error = None
            try:
                if kind == 'surface':
                    actual = workflow.surface(case['input']); value = surface_projection(actual)
                else:
                    actual = workflow.observe(case['request'], node=node); value = projection(actual)
                save(output_dir/(stem+'.json'), actual)
            except workflow.ERRORS as exc:
                error = str(exc); value = {'usable_surface': False} if kind == 'surface' else {'accepted': False}
                save(output_dir/(stem+'-refusal.json'), dict(reason=error, actual=value))
            expected = case['expected']
            matched = value == expected if kind == 'workflow' or expected['usable_surface'] else value == {'usable_surface': False}
            rows.append(dict(id=stem, expected=expected, actual=value, matches=matched, reason=error))
            if actual is not None and kind == 'workflow':
                try:
                    workflow.replay(actual, node=node); replays.append(stem)
                except workflow.ERRORS as exc: failures.append(dict(id=stem, reason=str(exc)))
    result = dict(kind='rendered-jsonld-qualification', synthetic=True, normative_effect='none',
        source_sha256=workflow.identity(), qualifier_sha256=workflow.sha(Path(__file__).read_bytes()),
        matched=sum(r['matches'] for r in rows), total=len(rows), expected_total=63,
        replayed=len(replays), expected_replays=29, rows=rows, replays=replays, failures=failures,
        scope='29 authored supplied surfaces, 23 prefrozen authored workflows and eleven later frozen review boundaries. Actual reader/processor execution, no browser execution or site assessment.')
    save(output_dir/'qualification.json', result); return result


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--node', required=True)
    p.add_argument('--output-dir', type=Path, required=True); args = p.parse_args()
    r = check(args.node, args.output_dir)
    print(json.dumps({k:v for k,v in r.items() if k not in ('rows', 'replays', 'source_sha256')}))
    return 0 if r['matched'] == r['total'] == 63 and r['replayed'] == 29 and not r['failures'] else 1


if __name__ == '__main__': sys.exit(main())
