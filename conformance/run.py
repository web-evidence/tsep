#!/usr/bin/env python3
"""Compare declared expectations to an interpreter over raw inputs. Apache-2.0."""
import argparse
import json
from pathlib import Path
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from conformance.evaluate import RULES, evaluate


def outcomes(rows):
    result = {}
    for row in rows:
        key = (row['rule_id'], row['target'])
        tsep.require(key not in result, 'Duplicate result pair')
        tsep.require(row['outcome'] in ('pass', 'fail', 'inconclusive', 'not-applicable'), 'Unknown outcome')
        result[key] = row['outcome']
    return result


def compare(expected_rows, actual_rows):
    """Normative expectations never change to match an implementation's limits."""
    expected, actual = outcomes(expected_rows), outcomes(actual_rows)
    limits = set()
    for row in expected_rows:
        tsep.require(type(row.get('reference_limit', False)) is bool, 'Invalid reference_limit')
        if row.get('reference_limit'):
            tsep.require(isinstance(row.get('basis'), str) and row['basis'].strip(), 'Reference limit needs normative basis')
            limits.add((row['rule_id'], row['target']))
    agreements, differences, reduced = [], [], []
    for key in sorted(set(expected) | set(actual)):
        item = {'rule_id': key[0], 'target': key[1], 'expected': expected.get(key), 'actual': actual.get(key)}
        if key in expected and actual.get(key) == expected[key]:
            agreements.append(item)
        elif key in limits and actual.get(key) == 'inconclusive':
            reduced.append(item)
        else:
            differences.append(item)
    return agreements, differences, reduced


def run(corpus, command=None):
    tsep.require(corpus['protocol_version'] == tsep.read_json(tsep.PROTOCOL_PATH)['version'], 'Stale conformance version')
    seen = {rule: set() for rule in RULES}
    cases = corpus['cases']
    tsep.unique([case['id'] for case in cases], 'conformance case')
    failures = []
    reduced_coverage = []
    agreements = disagreements = conclusive_expected = conclusive_agreements = 0
    by_rule = {rule: {'agreements': 0, 'disagreements': 0, 'reduced_coverage': 0} for rule in RULES}
    pairs = 0
    for case in cases:
        expected = outcomes(case['expected'])
        tsep.require(type(case.get('reference_limit', False)) is bool, 'Invalid case reference_limit')
        tsep.require(case.get('reference_limit', False) == any(r.get('reference_limit', False) for r in case['expected']),
                     'Reference limits must identify exact pairs: ' + case['id'])
        declared = {(r, t['url']) for r in case['input']['rules'] for t in case['input']['targets']}
        tsep.require(set(expected) == declared, 'Incomplete expected matrix: ' + case['id'])
        for (rule, _), outcome in expected.items():
            seen[rule].add(outcome)
        if command:
            completed = subprocess.run(shlex.split(command), input=json.dumps(case['input']),
                                       text=True, encoding='utf-8', capture_output=True, timeout=15)
            tsep.require(completed.returncode == 0, 'Implementation failed: ' + case['id'] + ': ' + completed.stderr[:1000])
            actual_rows = json.loads(completed.stdout, object_pairs_hook=tsep.unique_object)
        else:
            actual_rows = evaluate(case['input'])
        pairs += len(expected)
        agreed, differences, reduced = compare(case['expected'], actual_rows)
        agreements += len(agreed)
        disagreements += len(differences)
        conclusive_expected += sum(value != 'inconclusive' for value in expected.values())
        conclusive_agreements += sum(r['expected'] != 'inconclusive' for r in agreed)
        for rows, field in ((agreed, 'agreements'), (differences, 'disagreements'), (reduced, 'reduced_coverage')):
            for row in rows:
                if row['rule_id'] in by_rule:
                    by_rule[row['rule_id']][field] += 1
        if differences:
            failures.append({'case': case['id'], 'differences': differences})
        if reduced:
            reduced_coverage.append({'case': case['id'], 'pairs': reduced})
    tsep.require(all({'pass', 'fail', 'inconclusive'} <= values for values in seen.values()), 'Missing contradictory coverage per rule')
    return {'success': not failures, 'protocol_version': corpus['protocol_version'], 'synthetic': True,
            'cases': len(cases), 'rule_target_pairs': pairs, 'rules': list(RULES),
            'agreements': agreements, 'disagreements': disagreements,
            'coverage': {'conclusive_expected': conclusive_expected, 'conclusive_agreements': conclusive_agreements,
                         'percent': round(100 * conclusive_agreements / conclusive_expected, 2) if conclusive_expected else None,
                         'reduced_pairs': sum(len(c['pairs']) for c in reduced_coverage), 'by_rule': by_rule},
            'reduced_coverage': reduced_coverage, 'failures': failures,
            'limitations': 'Nine bounded atomic rules; supplied source/DOM/XML comparison and human TS10 content review. No JavaScript execution, global conformity or live observations.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', type=Path, default=ROOT/'conformance/cases.json')
    parser.add_argument('--command', help='External adapter, argv parsed without shell; input JSON on stdin, results array on stdout')
    args = parser.parse_args()
    try:
        result = run(tsep.read_json(args.cases), args.command)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result['success'] else 1)
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(json.dumps({'success': False, 'error': str(error)}))
        sys.exit(64)
