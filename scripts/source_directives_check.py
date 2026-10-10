#!/usr/bin/env python3
"""Qualify the optional source policy against independently frozen expectations."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from conformance.evaluate import evaluate


def fixture():
    path = ROOT/'tests/fixtures/source-directives-v2.json'
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != path.with_suffix('.sha256').read_text().strip():
        raise ValueError('Frozen source-directives fixture changed')
    data = json.loads(raw)
    rendered = ROOT/'tests/fixtures/source-directives-render-v1.json'
    raw_rendered = rendered.read_bytes()
    if hashlib.sha256(raw_rendered).hexdigest() != rendered.with_suffix('.sha256').read_text().strip():
        raise ValueError('Frozen rendered/source fixture changed')
    data['cases'].extend(json.loads(raw_rendered)['cases'])
    return data


def check(node):
    previous = os.environ.get('TSEP_SOURCE_NODE')
    os.environ['TSEP_SOURCE_NODE'] = node
    rows = []
    try:
        for case in fixture()['cases']:
            records = []
            actual = evaluate(case['input'], source_observations=records)
            expected = case['expected'][0]['outcome']
            rows.append({'id':case['id'], 'expected':expected, 'actual':actual, 'observations':records,
                         'matches':len(actual) == 1 and actual[0]['outcome'] == expected})
    finally:
        if previous is None: os.environ.pop('TSEP_SOURCE_NODE', None)
        else: os.environ['TSEP_SOURCE_NODE'] = previous
    return {'kind':'source-directives-qualification', 'synthetic':True, 'matched':sum(r['matches'] for r in rows),
            'total':len(rows), 'rows':rows,
            'scope':'Finite authored source-policy cases; actual optional Node execution, no browser, live site or Google observation. v1 oracle failure retained separately.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise ValueError('Choose a new output path')
    result = check(args.node)
    with args.output.open('x', encoding='utf-8') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2); handle.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'rows'}))
    return 0 if result['matched'] == result['total'] else 1


if __name__ == '__main__':sys.exit(main())
