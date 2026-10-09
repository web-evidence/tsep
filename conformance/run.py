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


def run(corpus, command=None, rules=None):
    tsep.require(corpus['protocol_version'] == tsep.read_json(tsep.PROTOCOL_PATH)['version'], 'Stale conformance version')
    requested = list(RULES) if rules is None else rules
    tsep.require(isinstance(requested, (list, tuple)) and requested
                 and all(isinstance(r, str) and r in RULES for r in requested), 'Explicit nonempty supported rules required')
    tsep.unique(requested, 'declared rule')
    selected = [r for r in RULES if r in requested]
    seen = {rule: set() for rule in RULES}
    cases = corpus['cases']
    tsep.unique([case['id'] for case in cases], 'conformance case')
    failures = []
    reduced_coverage = []
    agreements = disagreements = conclusive_expected = conclusive_agreements = 0
    by_rule = {rule: {'agreements': 0, 'disagreements': 0, 'reduced_coverage': 0,
                      'conclusive_expected': 0, 'conclusive_agreements': 0} for rule in selected}
    pairs = executed = total_pairs = 0
    for case in cases:
        expected = outcomes(case['expected'])
        tsep.require(type(case.get('reference_limit', False)) is bool, 'Invalid case reference_limit')
        tsep.require(case.get('reference_limit', False) == any(r.get('reference_limit', False) for r in case['expected']),
                     'Reference limits must identify exact pairs: ' + case['id'])
        declared = {(r, t['url']) for r in case['input']['rules'] for t in case['input']['targets']}
        tsep.require(set(expected) == declared, 'Incomplete expected matrix: ' + case['id'])
        tsep.require(set(case['input']['rules']) <= set(RULES), 'Unknown corpus rule')
        tsep.unique(case['input']['rules'], 'input rule')
        tsep.unique([t['url'] for t in case['input']['targets']], 'input target')
        # Validate the full corpus even when its unselected pairs are not executed.
        compare(case['expected'], case['expected'])
        for (rule, _), outcome in expected.items():
            seen[rule].add(outcome)
        total_pairs += len(expected)
        selected_input = dict(case['input'], rules=[r for r in case['input']['rules'] if r in selected])
        if not selected_input['rules']:
            continue
        executed += 1
        expected_rows = [r for r in case['expected'] if r['rule_id'] in selected]
        expected = outcomes(expected_rows)
        if command:
            completed = subprocess.run(shlex.split(command), input=json.dumps(selected_input),
                                       text=True, encoding='utf-8', capture_output=True, timeout=15)
            tsep.require(completed.returncode == 0, 'Implementation failed: ' + case['id'] + ': ' + completed.stderr[:1000])
            actual_rows = json.loads(completed.stdout, object_pairs_hook=tsep.unique_object)
        else:
            actual_rows = evaluate(selected_input)
        pairs += len(expected)
        # Do not filter actual rows: extra, omitted and foreign-target results still fail.
        agreed, differences, reduced = compare(expected_rows, actual_rows)
        agreements += len(agreed)
        disagreements += len(differences)
        conclusive_expected += sum(value != 'inconclusive' for value in expected.values())
        conclusive_agreements += sum(r['expected'] != 'inconclusive' for r in agreed)
        for (rule, _), outcome in expected.items():
            by_rule[rule]['conclusive_expected'] += outcome != 'inconclusive'
        for row in agreed:
            by_rule[row['rule_id']]['conclusive_agreements'] += row['expected'] != 'inconclusive'
        for rows, field in ((agreed, 'agreements'), (differences, 'disagreements'), (reduced, 'reduced_coverage')):
            for row in rows:
                if row['rule_id'] in by_rule:
                    by_rule[row['rule_id']][field] += 1
        if differences:
            failures.append({'case': case['id'], 'differences': differences})
        if reduced:
            reduced_coverage.append({'case': case['id'], 'pairs': reduced})
    tsep.require(all({'pass', 'fail', 'inconclusive'} <= values for values in seen.values()), 'Missing contradictory coverage per rule')
    for values in by_rule.values():
        denominator = values['conclusive_expected']
        values['percent'] = round(100 * values['conclusive_agreements'] / denominator, 2) if denominator else None
    return {'success': not failures, 'protocol_version': corpus['protocol_version'], 'synthetic': True,
            'cases': executed, 'rule_target_pairs': pairs, 'rules': selected,
            'available_rules': list(RULES), 'omitted_rules': [r for r in RULES if r not in selected],
            'total_cases': len(cases), 'skipped_cases': len(cases) - executed,
            'total_rule_target_pairs': total_pairs, 'omitted_rule_target_pairs': total_pairs - pairs,
            'claim': ('passes TSEP ' + corpus['protocol_version'] + ' conformance for ' + ', '.join(selected)) if not failures else None,
            'agreements': agreements, 'disagreements': disagreements,
            'coverage': {'conclusive_expected': conclusive_expected, 'conclusive_agreements': conclusive_agreements,
                         'percent': round(100 * conclusive_agreements / conclusive_expected, 2) if conclusive_expected else None,
                         'reduced_pairs': sum(len(c['pairs']) for c in reduced_coverage), 'by_rule': by_rule},
            'reduced_coverage': reduced_coverage, 'failures': failures,
            'limitations': 'Declared rules only; reduced coverage must accompany any claim. Bounded supplied source/DOM/XML comparison and human TS10 content review. No JavaScript execution, global conformity or live observations.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', type=Path, default=ROOT/'conformance/cases.json')
    parser.add_argument('--command', help='External adapter, argv parsed without shell; input JSON on stdin, results array on stdout')
    parser.add_argument('--rules', help='Comma-separated rule IDs; default: all nine. Limits inputs and comparison, never control conformity')
    args = parser.parse_args()
    try:
        result = run(tsep.read_json(args.cases), args.command, args.rules.split(',') if args.rules is not None else None)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result['success'] else 1)
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(json.dumps({'success': False, 'error': str(error)}))
        sys.exit(64)
