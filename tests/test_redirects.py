"""Frozen redirect expectations, report integration and offline replay. Apache-2.0."""
import copy
import hashlib
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
from adapters.captures import build
from adapters.replay import replay
from conformance.evaluate import evaluate
from conformance.run import compare

FROZEN = ROOT/'tests/fixtures/redirect-cases-v1.json'
CASES = {c['id']: c for c in tsep.read_json(FROZEN)['cases']}


class Redirects(unittest.TestCase):
    def test_prefrozen_expectations_and_corpus_copy(self):
        self.assertEqual(hashlib.sha256(FROZEN.read_bytes()).hexdigest(),
                         '5de7f60eefedffa868c406d9b5fa9af59c6ed9c2e368cc156d4e8063bde25770')
        corpus = {c['id']: c for c in tsep.read_json(ROOT/'conformance/cases.json')['cases']}
        for name, case in CASES.items():
            with self.subTest(case=name):
                self.assertEqual(corpus[name], case)
                actual = evaluate(case['input'])
                self.assertEqual(compare(case['expected'], actual)[1:], ([], []))

    def test_control_aggregation_and_network_forbidden_replay(self):
        for name, status in [('direct','C'), ('wrong-destination','NC'),
                             ('unfinished','NT'), ('missing-review','NT'),
                             ('failure-without-review','NC'), ('rejected-review','NC')]:
            with self.subTest(case=name), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                source = root/'input.json'
                source.write_text(json.dumps(CASES['redirect-'+name]['input']))
                with patch.object(socket, 'socket', side_effect=AssertionError('Network forbidden')):
                    summary = build(source, root/'bundle', assessor='Synthetic author', label=name,
                                    selection_method='Frozen synthetic case', access='synthetic', mode='manual')
                    report = tsep.read_json(root/'bundle/report.json')
                    self.assertEqual(report['results'][0]['status'], status)
                    receipt = replay(root/'bundle', root/'replay')
                self.assertTrue(receipt['replayed'])
                self.assertEqual(receipt['decision'], summary['decision'])
                self.assertEqual(receipt['network_requests'], 0)

    def test_missing_review_never_automatic_c_and_synthetic_never_public(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root/'input.json'
            source.write_text(json.dumps(CASES['redirect-direct']['input']))
            with self.assertRaisesRegex(tsep.Invalid, 'automatic'):
                build(source, root/'automatic', assessor='Fixture', label='Fixture',
                      selection_method='Fixture', access='synthetic', mode='automatic')
            with self.assertRaisesRegex(tsep.Invalid, 'provenance'):
                build(source, root/'public', assessor='Fixture', label='Fixture',
                      selection_method='Fixture', access='public')
            self.assertFalse((root/'automatic').exists())
            self.assertFalse((root/'public').exists())

    def test_changed_context_breaks_approval_without_hiding_http_contradiction(self):
        data = copy.deepcopy(CASES['redirect-wrong-destination']['input'])
        data['targets'][0]['context']['tool_version'] = 'other'
        rows = evaluate(data)
        self.assertEqual([r['outcome'] for r in rows], ['inconclusive', 'fail'])

    def test_http_refresh_does_not_silently_establish_complete_navigation(self):
        data = copy.deepcopy(CASES['redirect-direct']['input'])
        hop = data['targets'][0]['http'][-1]
        hop['response'] = hop['response'].replace('Content-Length:', 'Refresh: 0;url=/other\r\nContent-Length:')
        self.assertEqual(evaluate(data)[1]['outcome'], 'inconclusive')

    def test_partial_rule_matrix_is_not_a_complete_control(self):
        data = copy.deepcopy(CASES['redirect-direct']['input']); data['rules'] = ['TS02-A02']
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root/'input.json'; source.write_text(json.dumps(data))
            build(source, root/'bundle', assessor='Fixture', label='Fixture',
                  selection_method='Fixture', access='synthetic', mode='manual')
            self.assertEqual(tsep.read_json(root/'bundle/report.json')['results'][0]['status'], 'NT')


if __name__ == '__main__':
    unittest.main()
