#!/usr/bin/env python3
"""Qualify TS01's opt-in marker policy and authored native bundles with explicit Node."""
import argparse
import copy
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from adapters import captures, replay
from conformance.evaluate import evaluate
from reports import html
from scripts.source_markers_check import fixture as frozen


def fixture():
    return frozen('identity-markers-v1.json')


def check(node, output):
    output.mkdir(parents=True, exist_ok=False)
    previous = os.environ.get('TSEP_SOURCE_NODE')
    os.environ['TSEP_SOURCE_NODE'] = node
    rows, bundles = [], []
    try:
        cases = fixture()['cases']
        for case in cases:
            notes = []
            actual = evaluate(case['input'], source_observations=notes)
            expected = case['expected'][0]['outcome']
            record = {'id': case['id'], 'expected': expected, 'actual': actual, 'observations': notes,
                      'matches': len(actual) == 1 and actual[0]['outcome'] == expected}
            (output/(case['id']+'.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
            rows.append({k: v for k, v in record.items() if k != 'observations'})
        indexed = {c['id']: c for c in cases}
        recipe = frozen('identity-markers-bundles-v1.json')
        for plan in recipe['cases']:
            case = indexed[plan['case_id']]
            folder = output/('bundle-'+case['id']); folder.mkdir()
            data = copy.deepcopy(case['input']); data['rules'] = recipe['rules']
            source = folder/'input.json'; source.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
            captures.build(source, folder/'bundle', assessor='Authored synthetic fixture',
                           label='Synthetic TS01 profile qualification', selection_method='Prefrozen synthetic case',
                           access='synthetic', mode='automatic')
            report = json.loads((folder/'bundle/report.json').read_text())
            status = next(r['status'] for r in report['results'] if r['control_id'] == 'TS01')
            result = replay.replay(folder/'bundle', folder/'replay')
            for language in ('fr', 'en'):
                html.write(folder/'bundle/report.json', folder/('report-'+language+'.html'), language=language)
            bundles.append({'id': case['id'], 'expected_control_status': plan['expected_control_status'],
                            'actual_control_status': status, 'matches': status == plan['expected_control_status'],
                            'exact_replay': result['replayed'] and result['same_source_observations'],
                            'rendered_languages': ['fr', 'en']})
    finally:
        if previous is None: os.environ.pop('TSEP_SOURCE_NODE', None)
        else: os.environ['TSEP_SOURCE_NODE'] = previous
    result = {'kind': 'identity-markers-policy-qualification', 'synthetic': True,
              'matched': sum(r['matches'] for r in rows), 'total': len(rows), 'rows': rows,
              'bundle_matches': sum(b['matches'] for b in bundles), 'bundle_total': len(bundles),
              'exact_bundle_replays': sum(b['exact_replay'] for b in bundles), 'bundles': bundles,
              'scope': 'Authored inputs, actual offline parsing, native report/replay and FR/EN HTML generation. '
                       'No network, browser rendering, visual QA, real owner intent or Edikka assessment.'}
    (output/'qualification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--node', required=True); p.add_argument('--output-dir', type=Path, required=True)
    a = p.parse_args(); r = check(a.node, a.output_dir)
    print(json.dumps({k: v for k, v in r.items() if k not in ('rows', 'bundles')}))
    return 0 if r['matched'] == r['total'] and r['bundle_matches'] == r['exact_bundle_replays'] == r['bundle_total'] else 1


if __name__ == '__main__': sys.exit(main())
