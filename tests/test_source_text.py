"""Frozen source-text counterexamples and selected independent HTML expectations."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from conformance.evaluate import evaluate, identity_text, identity_result
from conformance.http import Unknown
from conformance.source_text import extract, characters, MAX_TAG, MAX_TOKENS
from provenance.runtime import runtime_identity

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT/'tests/fixtures'
HEADERS = {'content-type': ['text/html; charset=utf-8']}


def frozen_results(cases=None):
    rows = []
    if cases is None:
        cases = json.loads((FIXTURES/'source-text-cases.json').read_text())['cases']
    for case in cases:
        try:
            segments = identity_text(HEADERS, case['html'])
            outcome = identity_result('https://example.com/', HEADERS, case['html'],
                                      {'expected_final_url': 'https://example.com/',
                                       'expected_body_sha256': '0'*64,
                                       'required_markers': ['Expected'], 'forbidden_markers': ['Forbidden']})[0]
        except Unknown:
            segments, outcome = None, 'inconclusive'
        rows.append({'id': case['id'], 'segments': segments, 'outcome': outcome})
    return rows


class SourceText(unittest.TestCase):
    def test_v5_fixture_freeze_and_no_v4_expectation_replacement(self):
        expected, name = (FIXTURES/'source-text-v5-freeze.sha256').read_text().strip().split('  ', 1)
        self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(), expected)
        data = json.loads((FIXTURES/'source-text-v5-cases.json').read_text())
        prior = data['supersedes']
        self.assertEqual(hashlib.sha256((ROOT/prior['file']).read_bytes()).hexdigest(), prior['sha256'])
        self.assertEqual(prior['changes'], [])
        original = json.loads((FIXTURES/'source-text-cases.json').read_text())['cases']
        ids = [c['id'] for c in original+data['cases']]
        self.assertEqual(len(ids), len(set(ids)))

    def test_v5_frozen_segments_and_atomic_outcomes(self):
        cases = json.loads((FIXTURES/'source-text-v5-cases.json').read_text())['cases']
        for case, actual in zip(cases, frozen_results(cases)):
            with self.subTest(case=case['id']):
                self.assertEqual(actual, {k: case[k] for k in ('id', 'segments', 'outcome')})

    def test_svg_style_preflight_uses_complete_extraction(self):
        from collectors.preflight import reference_check
        for content, state in [('<svg><style>Forbidden</style></svg>Expected', 'matches'),
                               ('<svg><style>Expected</style></svg>Other', 'contradiction'),
                               ('Expected Forbidden<svg><style><p>x</p></style></svg>', 'unavailable')]:
            with self.subTest(state=state):
                body = ('<html><body>'+content+'</body></html>').encode()
                self.assertEqual(reference_check(HEADERS, body, 'markers', ['Expected'], ['Forbidden'])['state'], state)

    def test_frozen_inventory_is_unchanged(self):
        for row in (FIXTURES/'source-text-freeze.sha256').read_text().splitlines():
            expected, name = row.split('  ', 1)
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(), expected)

    def test_all_frozen_source_segments_and_atomic_outcomes(self):
        expected = json.loads((FIXTURES/'source-text-cases.json').read_text())['cases']
        changes = {r['id']: r for r in json.loads((FIXTURES/'source-text-v6-cases.json').read_text())['supersedes']['changes']}
        for case, actual in zip(expected, frozen_results()):
            with self.subTest(case=case['id']):
                self.assertEqual(actual, {k: changes.get(case['id'], case)[k] for k in ('id', 'segments', 'outcome')})

    def test_v6_frozen_cases_and_explicit_v4_migration(self):
        expected, name = (FIXTURES/'source-text-v6-freeze.sha256').read_text().strip().split('  ', 1)
        self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(), expected)
        data = json.loads((FIXTURES/'source-text-v6-cases.json').read_text())
        prior = data['supersedes']
        self.assertEqual(hashlib.sha256((ROOT/prior['file']).read_bytes()).hexdigest(), prior['sha256'])
        self.assertEqual([r['id'] for r in prior['changes']], ['select-context'])
        self.assertEqual(prior['changes'][0]['outcome'], 'pass')
        for case, actual in zip(data['cases'], frozen_results(data['cases'])):
            with self.subTest(case=case['id']):
                self.assertEqual(actual, {k: case[k] for k in ('id', 'segments', 'outcome')})

    def test_v6_common_complete_readings_match_experiment_without_noscript(self):
        # Internal differential check only: both readers share lexical helpers.
        # A refusal by either reader does not become an agreement or a pass.
        from experiments.noscript import reading
        both = 0
        for name in ('source-text-cases.json', 'source-text-v5-cases.json',
                     'source-text-v6-cases.json', 'noscript-experiment-v3-cases.json',
                     'noscript-experiment-v4-cases.json'):
            for case in json.loads((FIXTURES/name).read_text())['cases']:
                if '<noscript' in case['html'].lower():
                    continue
                try:
                    active = extract(case['html'])
                except Unknown:
                    continue
                for mode in ('enabled', 'disabled'):
                    trial = reading(case['html'], mode)
                    if trial['complete']:
                        both += 1
                        with self.subTest(fixture=name, case=case['id'], mode=mode):
                            self.assertEqual(active, [s['text'] for s in trial['segments']])
        self.assertEqual(both, 324)

    def test_independent_character_reference_expectations(self):
        cases = json.loads((FIXTURES/'html5-character-cases.json').read_text())['cases']
        for case in cases:
            with self.subTest(case=case['id']):
                self.assertEqual(characters(case['input']), case['text'])
                self.assertEqual(extract('<html><body>'+case['input']+'</body></html>'),
                                 [case['text']] if case['text'] else [])

    def test_no_htmlparser_dependency_for_ts01(self):
        with patch('html.parser.HTMLParser.feed', side_effect=AssertionError('TS01 must use its own bounded extractor')):
            self.assertEqual(identity_text(HEADERS, '<html><body><section>Expected</section></body></html>'), ['Expected'])

    def test_ts07_and_ts10_outputs_match_prechange_baseline(self):
        corpus = json.loads((ROOT/'conformance/cases.json').read_text())
        additions = {c['id'] for c in json.loads((FIXTURES/'redirect-cases-v1.json').read_text())['cases']}
        for name in ('robots-control-v1-cases.json', 'robots-control-v1-extra.json', 'structured-rendering-v1-cases.json', 'directive-agent-v1-cases.json', 'directive-agent-access-v1-cases.json'):
            additions.update(c['id'] for c in json.loads((FIXTURES/name).read_text())['cases'])
        data = [{'id': c['id'], 'rows': [r for r in evaluate(c['input']) if r['rule_id'].startswith(('TS07-', 'TS10-'))]}
                for c in corpus['cases'] if c['id'] not in additions]
        self.assertEqual(len(data), 216)
        raw = (json.dumps(data, ensure_ascii=False, sort_keys=True)+'\n').encode()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), '79176096946f5173cde969a54c34d188852cc8a117d6161ffa07e705da081bc0')

    def test_numeric_controls_noncharacters_and_overflow_preserve_contract(self):
        self.assertEqual(characters('&#127;&#1;&#xFDD0;&#x10FFFF;'), '\x7f\x01\ufdd0\U0010ffff')
        self.assertEqual(characters('&#xD800;&#1114112;&#0;'), '\ufffd'*3)
        self.assertEqual(characters('&#'+'0'*10000+'65;'), 'A')
        self.assertEqual(characters('&#'+'9'*10000+';'), '\ufffd')

    def test_tag_and_token_bounds_and_long_inert_content(self):
        for body in ('<div title="'+'x'*MAX_TAG+'"></div>', '<br>'*(MAX_TOKENS+1)):
            with self.subTest(kind=body[:20]), self.assertRaisesRegex(Unknown, 'limit|excessive'):
                extract('<html><body>'+body+'</body></html>')
        # An external deadline catches accidental quadratic scans of successive raw contexts.
        code = ('from conformance.source_text import extract; '
                'assert extract("<html><body>"+"<script>ignored</script>"*20000+"Expected</body></html>")==["Expected"]')
        result = subprocess.run([sys.executable, '-c', code], cwd=ROOT, capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_boolean_and_unicode_attribute_boundaries(self):
        self.assertEqual(extract('<html><body><input required disabled><p İ="Forbidden">Expected</p></body></html>'), ['Expected'])
        self.assertEqual(extract('<html><body><input İ disabled>Expected</body></html>'), ['Expected'])

    def test_runtime_identity_is_explicit_and_has_no_absolute_paths(self):
        info = runtime_identity()
        self.assertIn('python', info)
        self.assertEqual(set(info['stdlib_source_sha256']), {'html', 'html.entities', 'html.parser'})
        self.assertNotIn(str(ROOT), json.dumps(info))


if __name__ == '__main__':
    unittest.main()
