"""TS06 synthetic route/access fixtures; no DNS, socket, authentication or live crawl."""
import copy
import json
from pathlib import Path
import socket
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from conformance.corpus import expand
from conformance.evaluate import evaluate
from conformance.http import Unknown
from conformance.ts06_access import assess, _target_url_for_hop, _url
from adapters.captures import build
from adapters.replay import replay

FIXTURE = tsep.read_json(ROOT / 'tests/fixtures/ts06-access-cases.json')
CASES = {case['id']: case for case in FIXTURE['cases']}


class TS06Access(unittest.TestCase):
    def test_all_frozen_fixtures_match_native_and_reference_interpreter_without_network(self):
        self.assertTrue(FIXTURE['synthetic'])
        self.assertEqual(len(CASES), 23)
        corpus = expand(tsep.read_json(ROOT / 'conformance/cases.json'))
        native_cases = [case for case in corpus['cases'] if case['id'] in CASES]
        self.assertEqual(len(native_cases), len(CASES))
        for case in native_cases:
            with self.subTest(case=case['id']), patch.object(
                    socket, 'socket', side_effect=AssertionError('No socket allowed')), patch.object(
                    socket, 'create_connection', side_effect=AssertionError('No network allowed')), patch.object(
                    socket, 'getaddrinfo', side_effect=AssertionError('No DNS allowed')):
                before = copy.deepcopy(case['input'])
                outcome, _ = assess(case['input']['targets'][0], 'TS06-A01')
                self.assertEqual(outcome, case['expected'][0]['outcome'])
                evaluated = evaluate(case['input'])
                self.assertEqual(
                    [(row['rule_id'], row['target'], row['outcome']) for row in evaluated],
                    [(row['rule_id'], row['target'], row['outcome']) for row in case['expected']])
                self.assertEqual(before, case['input'])

    def test_canary_leak_survives_duplicate_cell_check(self):
        case = CASES['ts06-duplicate-leaking-trace-preserves-fail']
        self.assertEqual(evaluate(case['input'])[0]['outcome'], 'fail')

    def test_same_origin_redirect_uses_scheme_host_and_effective_port(self):
        self.assertEqual(_target_url_for_hop(
            'https://example.invalid:443/login',
            'https://example.invalid/private/record'),
            'https://example.invalid:443/login')
        for destination in ('https://other.invalid/login', 'http://example.invalid/login'):
            with self.subTest(destination=destination), self.assertRaises(Unknown):
                _target_url_for_hop(destination, 'https://example.invalid/private/record')

    def test_live_or_query_bearing_urls_are_not_fixture_targets(self):
        for value in ('https://example.invalid/private?token=x',
                      'https://public.example/private',
                      'https://user@example.invalid/private'):
            with self.subTest(url=value), self.assertRaises(Unknown):
                _url(value, 'test')

    def test_native_import_export_and_offline_replay_for_pass_fail_and_whole_na(self):
        for case_id, expected_status in (
                ('ts06-safe-synthetic-matrix', 'C'),
                ('ts06-canary-in-403', 'NC'),
                ('ts06-dated-positive-na', 'NA')):
            with self.subTest(case=case_id), tempfile.TemporaryDirectory() as temp:
                base = Path(temp)
                source = base / 'input.json'
                bundle = base / 'bundle'
                replayed = base / 'replayed'
                source.write_text(json.dumps(CASES[case_id]['input'], ensure_ascii=False),
                                  encoding='utf-8')
                summary = build(source, bundle, assessor='Synthetic reviewer',
                                label='TS06 synthetic fixture',
                                selection_method='Named .invalid fixture only',
                                access='synthetic')
                report = tsep.read_json(bundle / 'report.json')
                self.assertEqual(report['results'][0]['status'], expected_status)
                self.assertEqual(summary, tsep.validate(report, bundle))
                replay_summary = replay(bundle, replayed)
                replay_record = tsep.read_json(replayed / 'replay.json')
                self.assertTrue(replay_record['replayed'])
                self.assertTrue(replay_record['same_report_results'])
                self.assertTrue(replay_record['same_gate'])
                self.assertEqual(replay_summary['decision'], summary['decision'])

    def test_pass_reason_keeps_real_identity_and_shared_cache_out_of_scope(self):
        outcome, reason = assess(CASES['ts06-safe-synthetic-matrix']['input']['targets'][0],
                                 'TS06-A01')
        self.assertEqual(outcome, 'pass')
        self.assertIn('does not establish a real identity', reason)
        self.assertIn('shared cache', reason)


if __name__ == '__main__':
    unittest.main()
