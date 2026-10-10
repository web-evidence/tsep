#!/usr/bin/env python3
"""Offline selected source-text checks and a cross-runtime result fingerprint.

Not HTML5 conformance or whole-protocol verification. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from conformance.evaluate import identity_result, identity_text
from conformance.http import Unknown
from conformance.source_text import characters
from provenance.runtime import runtime_identity


def check():
    fixtures = ROOT/'tests/fixtures'
    for line in (fixtures/'source-text-freeze.sha256').read_text().splitlines():
        expected, name = line.split('  ', 1)
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != expected:
            raise ValueError('Frozen fixture changed: '+name)
    rows = []
    cases = json.loads((fixtures/'source-text-cases.json').read_text())['cases']
    for case in cases:
        headers = {'content-type': ['text/html; charset=utf-8']}
        try:
            segments = identity_text(headers, case['html'])
            outcome = identity_result('https://example.com/', headers, case['html'],
                                      {'expected_final_url': 'https://example.com/',
                                       'expected_body_sha256': '0'*64,
                                       'required_markers': ['Expected'],
                                       'forbidden_markers': ['Forbidden']})[0]
        except Unknown:
            segments, outcome = None, 'inconclusive'
        row = {'id': case['id'], 'segments': segments, 'outcome': outcome}
        if row != {key: case[key] for key in row}:
            raise ValueError('Source-text disagreement: '+case['id'])
        rows.append(row)
    external = json.loads((fixtures/'html5-character-cases.json').read_text())['cases']
    for case in external:
        value = characters(case['input'])
        if value != case['text']:
            raise ValueError('Character-reference disagreement: '+case['id'])
        rows.append({'id': case['id'], 'text': value})
    raw = (json.dumps(rows, ensure_ascii=True, sort_keys=True, separators=(',', ':'))+'\n').encode('ascii')
    return {'passed': True, 'synthetic_source_cases': len(cases),
            'selected_upstream_character_cases': len(external),
            'result_sha256': hashlib.sha256(raw).hexdigest(), 'runtime': runtime_identity(),
            'network_requests': 0,
            'scope': 'Exact segments/outcomes and selected DATA character expectations; not HTML5 or complete TSEP conformance.'}


if __name__ == '__main__':
    try:
        print(json.dumps(check(), ensure_ascii=True, indent=2))
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({'passed': False, 'error': str(error)}))
        sys.exit(1)
