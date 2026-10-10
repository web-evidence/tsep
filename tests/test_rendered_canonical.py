"""Authored candidate cases, never represented as browser or normative results."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from experiments import rendered_canonical as c

FIXTURE = c.ROOT/'tests/fixtures/rendered-canonical-v1-cases.json'
FROZEN = 'abf711d6478c5c7acfadeb429a2866c32f9a918d1131c05110362edc156e3ef0'


class RenderedCanonical(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads(FIXTURE.read_bytes())['cases']

    def case(self, name='exact'):
        return copy.deepcopy(next(x for x in self.cases if x['id'] == name))

    def test_all_prefrozen_authored_outcomes_and_reasons(self):
        self.assertEqual(hashlib.sha256(FIXTURE.read_bytes()).hexdigest(), FROZEN)
        self.assertEqual(FIXTURE.with_suffix('.sha256').read_text().split()[0], FROZEN)
        self.assertEqual(len(self.cases), 59)
        for case in self.cases:
            with self.subTest(case=case['id']):
                before = copy.deepcopy(case)
                result = c.assess(case['record'], case['intent'])
                self.assertEqual(result['outcome'], case['expected']['outcome'])
                self.assertEqual(result['reasons'], case['expected']['reasons'])
                self.assertFalse(result['normative'])
                self.assertEqual(case, before)

    def test_partial_contradiction_does_not_gain_complete_coverage(self):
        case = self.case('partial-conflict')
        result = c.assess(case['record'], case['intent'])
        self.assertFalse(result['coverage']['traversal_complete'])
        self.assertEqual(result['coverage']['stop_reason'], 'node-limit')
        self.assertEqual(result['coverage_gaps'], ['incomplete-tree'])
        self.assertEqual(result['diagnostics'][0]['raw_href'], 'https://example.test/product/other')

    def test_review_cases_frozen_before_correction_after_initial_code(self):
        path = c.ROOT/'tests/fixtures/rendered-canonical-v1-review-cases.json'
        expected_hash = '650be991acb047b4081e8de9344bf779ef50ad5f092ae22812b236407ec2bd8d'
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected_hash)
        self.assertEqual(path.with_suffix('.sha256').read_text().split()[0], expected_hash)
        cases = json.loads(path.read_bytes())['cases']
        self.assertEqual(len(cases), 5)
        for case in cases:
            with self.subTest(case=case['id']):
                result = c.assess(case['record'], case['intent'])
                self.assertEqual(result['outcome'], case['expected']['outcome'])
                self.assertEqual(result['reasons'], case['expected']['reasons'])

    def test_url_prefix_review_cases_and_raw_strings_preserved(self):
        path = c.ROOT/'tests/fixtures/rendered-canonical-v1-url-prefix-cases.json'
        expected_hash = 'e8370129bcbf686a57b5b3d1371ec110a460a48a01a426034e0a6e2ce980bbc9'
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected_hash)
        self.assertEqual(path.with_suffix('.sha256').read_text().split()[0], expected_hash)
        cases = json.loads(path.read_bytes())['cases']
        self.assertEqual(len(cases), 5)
        for case in cases:
            with self.subTest(case=case['id']):
                result = c.assess(case['record'], case['intent'])
                self.assertEqual(result['outcome'], case['expected']['outcome'])
                self.assertEqual(result['reasons'], case['expected']['reasons'])
                self.assertEqual(result['canonical'][0]['raw_href'], case['record']['tree']['nodes'][3]['attributes'][1]['value'])

    def test_guards_preserve_diagnostics_without_promoting_them(self):
        case = self.case('fabricated-contradiction-known')
        result = c.assess(case['record'], case['intent'])
        self.assertEqual(result['outcome'], 'undetermined')
        self.assertEqual(result['diagnostics'][0]['reason'], 'raw-href-differs')
        self.assertEqual(result['intent']['known_integrity_issues'], case['intent']['known_integrity_issues'])

    def test_duplicate_order_and_shadow_paths_stay_visible(self):
        case = self.case('conflicting-duplicates')
        result = c.assess(case['record'], case['intent'])
        self.assertEqual([x['node_id'] for x in result['canonical']], [3, 4])
        case = self.case('head-and-shadow')
        result = c.assess(case['record'], case['intent'])
        self.assertEqual(len(result['canonical']), 2)
        self.assertIn('shadow:0', result['canonical'][1]['path'])
        self.assertEqual(result['diagnostics'], [])

    def test_noindex_and_exclusions_survive_canonical_agreement(self):
        case = self.case('robots-never-cleared-or-evaluated')
        result = c.assess(case['record'], case['intent'])
        self.assertEqual(result['outcome'], 'agreement-in-record')
        self.assertEqual(result['other_metadata'][0]['content'], 'noindex')
        self.assertEqual(result['coverage']['api_authenticity'], 'not-established')
        case = self.case('excluded-frame-template')
        result = c.assess(case['record'], case['intent'])
        self.assertEqual([x['kind'] for x in result['boundaries']], ['iframe', 'template'])

    def test_retrospective_label_cannot_be_promoted_to_prospective(self):
        case = self.case('retrospective-label-retained')
        self.assertEqual(c.assess(case['record'], case['intent'])['mode'], 'retrospective')
        case['intent']['mode'] = 'prospective'
        with self.assertRaisesRegex(ValueError, 'contract/mode'):
            c.assess(case['record'], case['intent'])

    def test_non_normalized_preference_followup_after_design_review(self):
        # Added after initial code, not part of the 59 prefrozen cases.
        case = self.case()
        case['intent']['preferred_url'] = 'https://EXAMPLE.test/product'
        self.assertEqual(c.assess(case['record'], case['intent'])['outcome'],
                         'contradiction-in-record')
        case['record']['tree']['nodes'][3]['attributes'][1]['value'] = 'https://EXAMPLE.test/product'
        case['intent']['record_sha256'] = c.digest(case['record'])
        result = c.assess(case['record'], case['intent'])
        self.assertEqual(result['outcome'], 'undetermined')
        self.assertEqual(result['reasons'], ['absolute-raw-resolved-difference'])

    def test_invalid_trees_and_incompatible_scripts_are_rejected(self):
        for change in ('count', 'parent', 'attribute', 'script', 'fields'):
            case = self.case(); record = case['record']
            if change == 'count': record['tree']['reported_node_count'] += 1
            elif change == 'parent': record['tree']['nodes'][3]['parent'] = 90
            elif change == 'attribute': del record['tree']['nodes'][3]['attributes'][0]['namespace']
            elif change == 'script': record['script_sha256'] = '0'*64
            else: record['extra'] = True
            with self.subTest(change=change), self.assertRaises(ValueError):
                c.assess(record, case['intent'])

    def test_intent_shape_and_bounds_are_not_treated_as_missing_evidence(self):
        for key, value in [('html_canonical_required', 1), ('known_integrity_issues', ['x']*65),
                           ('known_integrity_issues', ['']), ('state_label', 'x'*4097),
                           ('record_sha256', 'unbound'), ('extra', True), ('mode', [])]:
            case = self.case(); case['intent'][key] = value
            with self.subTest(key=key, value=str(value)[:20]), self.assertRaises(ValueError):
                c.assess(case['record'], case['intent'])
        case = self.case(); del case['intent']['known_integrity_issues']
        with self.assertRaises(ValueError): c.assess(case['record'], case['intent'])

    def test_supported_reference_subset_and_exact_comparison(self):
        for url in ['https://example.test/product', 'http://127.0.0.1:52354/product?a=1&b=2',
                    'HTTPS://EXAMPLE.test/A%20B']:
            self.assertTrue(c.supported_url(url), url)
        for url in ['http://[::1]/', 'https://user@example.test/', 'https://example.test/#',
                    'https://example.test:0/', 'https://example.test:65536/',
                    'https://example.test/a b', 'https://example.test/a\\b',
                    'https://example.test/%X0', 'https://example.test/\n',
                    'https://-bad.test/', 'https://example..test/', '//example.test/']:
            self.assertFalse(c.supported_url(url), url)

    def test_cli_is_offline_isolated_and_records_source_and_input_bytes(self):
        case = self.case()
        script = '''import importlib.abc, runpy, socket, sys
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.startswith('conformance') or fullname.startswith('collectors'):
            raise RuntimeError('Normative/collector import forbidden: '+fullname)
sys.meta_path.insert(0, Block())
def forbidden(*a, **k): raise RuntimeError('Network forbidden')
socket.socket = socket.create_connection = socket.getaddrinfo = forbidden
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
'''
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory); snapshot = folder/'snapshot.json'; intent = folder/'intent.json'; out = folder/'result.json'
            snapshot.write_text(json.dumps(case['record']), encoding='utf-8')
            intent.write_text(json.dumps(case['intent']), encoding='utf-8')
            args = [sys.executable, '-c', script, str(c.ROOT/'experiments/rendered_canonical.py'),
                    str(snapshot), '--intent', str(intent), '--output', str(out)]
            run = subprocess.run(args, capture_output=True, text=True, cwd=directory, timeout=15)
            self.assertEqual(run.returncode, 0, run.stderr)
            result = json.loads(out.read_bytes())
            self.assertEqual(result['outcome'], 'agreement-in-record')
            self.assertEqual(result['input_files_sha256']['snapshot'], hashlib.sha256(snapshot.read_bytes()).hexdigest())
            self.assertEqual(result['source_files_sha256'], c.sources())
            before = out.read_bytes()
            run = subprocess.run(args, capture_output=True, text=True, cwd=directory, timeout=15)
            self.assertEqual(run.returncode, 64)
            self.assertEqual(out.read_bytes(), before)

    def test_strict_json_rejects_duplicate_nonfinite_and_oversize(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'input.json'
            for raw in [b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}']:
                path.write_bytes(raw)
                with self.subTest(raw=raw), self.assertRaises(ValueError): c.read_input(path, 100)
            path.write_bytes(b' '*101)
            with self.assertRaisesRegex(ValueError, 'bound'): c.read_input(path, 100)

    def test_mixed_module_origin_is_rejected(self):
        with patch.object(c.metadata, '__file__', '/tmp/another-checkout/rendered_metadata.py'):
            with self.assertRaisesRegex(ValueError, 'origin'): c.sources()


if __name__ == '__main__':
    unittest.main()
