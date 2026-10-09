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


def run(corpus, command=None):
    tsep.require(corpus['protocol_version'] == tsep.read_json(tsep.PROTOCOL_PATH)['version'], 'Stale conformance version')
    seen = {rule: set() for rule in RULES}
    cases = corpus['cases']
    tsep.unique([case['id'] for case in cases], 'conformance case')
    failures = []
    pairs = 0
    for case in cases:
        expected = outcomes(case['expected'])
        declared = {(r, t['url']) for r in case['input']['rules'] for t in case['input']['targets']}
        tsep.require(set(expected) == declared, 'Incomplete expected matrix: ' + case['id'])
        for (rule, _), outcome in expected.items():
            seen[rule].add(outcome)
        if command:
            completed = subprocess.run(shlex.split(command), input=json.dumps(case['input']),
                                       text=True, encoding='utf-8', capture_output=True, timeout=15)
            tsep.require(completed.returncode == 0, 'Implementation failed: ' + case['id'] + ': ' + completed.stderr[:1000])
            actual = outcomes(json.loads(completed.stdout, object_pairs_hook=tsep.unique_object))
        else:
            actual = outcomes(evaluate(case['input']))
        pairs += len(expected)
        if actual != expected:
            failures.append({'case': case['id'], 'differences': [
                {'rule_id': k[0], 'target': k[1], 'expected': expected.get(k), 'actual': actual.get(k)}
                for k in sorted(set(expected) | set(actual)) if expected.get(k) != actual.get(k)]})
    tsep.require(all({'pass', 'fail', 'inconclusive'} <= values for values in seen.values()), 'Missing contradictory coverage per rule')
    return {'success': not failures, 'protocol_version': corpus['protocol_version'], 'synthetic': True,
            'cases': len(cases), 'rule_target_pairs': pairs, 'rules': list(RULES), 'failures': failures,
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
