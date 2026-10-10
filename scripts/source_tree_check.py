#!/usr/bin/env python3
"""Opt-in Node qualification; separate from the Python-only TSEP verifier."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments import source_tree


def frozen(name):
    path = ROOT/'tests/fixtures'/name
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != path.with_suffix('.sha256').read_text().strip():
        raise ValueError('Changed frozen fixture: '+name)
    return json.loads(raw), digest


def project(reading):
    result = {k: [] for k in ('head', 'body', 'template')}
    for item in reading['inventory_order']:
        record = (reading['template_signals'] if item['group'] == 'template' else
                  reading['inventory'][item['group']])[item['index']]
        if record['group'] in ('robots', 'canonical'):
            result[record['context']].append(record['attributes'].get('id'))
    return result


def check(node):
    first, first_sha = frozen('source-tree-cases-v1.json')
    second, second_sha = frozen('source-tree-cases-v2.json')
    groups, group_sha = frozen('source-tree-groups-v1.json')
    rows, group_rows, versions = [], [], set()
    for old, case in zip(first['cases'], second['cases']):
        assert old['id'] == case['id'] and old['html'] == case['html']
        result = source_tree.inventory(case['html'].encode(), encoding='utf-8', node=node)
        versions.add(json.dumps(result['runtime'], sort_keys=True))
        for mode, reading in result['readings'].items():
            assert reading['complete'], (case['id'], reading.get('reason'))
            actual = project(reading)
            assert actual == case['expected'][mode], (case['id'], mode, actual)
            rows.append({'id': case['id'], 'mode': mode, 'actual': actual,
                         'original_matches': actual == old['expected'][mode],
                         'corrected_matches': True, 'parse_errors': reading['parse_errors']})
    assert len(rows) == 72 and sum(x['original_matches'] for x in rows) == 71
    for case in groups['cases']:
        result = source_tree.inventory(case['html'].encode(), encoding='utf-8', node=node)
        assert result['comparisons'] == case['comparisons'], (case['id'], result['comparisons'])
        for mode, reading in result['readings'].items():
            assert reading['complete'], (case['id'], mode)
            inv = reading['inventory']
            if 'active_counts' in case:
                assert [len(inv[g]) for g in source_tree.GROUPS] == case['active_counts']
            if 'template_count' in case:
                assert len(reading['template_signals']) == case['template_count']
            if 'parse_error' in case:
                assert case['parse_error'] in [e['code'] for e in reading['parse_errors']]
            if 'robots_contexts' in case:
                assert [r['context'] for r in inv['robots']] == case['robots_contexts']
            if 'anchor_href' in case:
                assert inv['anchors'][0]['attributes']['href'] == case['anchor_href']
        group_rows.append({'id': case['id'], 'comparisons': result['comparisons'], 'matches': True})
    bounds = []
    for name, source in [('depth', '<!doctype html><html><body>'+'<div>'*270+'x'+'</div>'*270+'</body></html>'),
                         ('parse-errors', '<!doctype html><html><body>'+('<p a=1 a=2>x</p>'*1002)+'</body></html>')]:
        result = source_tree.inventory(source.encode(), encoding='utf-8', node=node)
        assert set(result['comparisons'].values()) == {'unavailable'}
        assert all(not r['complete'] and not any(r['inventory'].values()) for r in result['readings'].values())
        bounds.append({'id': name, 'readings': {m: r['reason'] for m, r in result['readings'].items()}})
    return {'kind': 'optional-static-source-tree-qualification', 'normative_effect': 'none',
            'fixture_sha256': {'original': first_sha, 'corrected': second_sha, 'groups': group_sha},
            'runtimes': [json.loads(v) for v in sorted(versions)], 'rows': rows, 'group_cases': group_rows,
            'bounded_refusals': bounds, 'summary': {'original_matches': 71, 'corrected_matches': 72,
            'readings': 72, 'group_cases': 12, 'bounded_refusals': 2},
            'source_sha256': source_tree.identity(),
            'scope': 'Authored finite expectations; v2 corrects one v1 oracle after comparison. No independent review, browser equivalence or Google/TSEP result.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output already exists')
    result = check(args.node)
    with args.output.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2); handle.write('\n')
    print(json.dumps(result['summary']))


if __name__ == '__main__':
    main()
