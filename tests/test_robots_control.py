"""TS04 frozen rules, aggregation, bound reviews and replay. Apache-2.0."""
import copy
from datetime import datetime, timezone
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
from adapters.review import prepare, apply_review
from conformance.evaluate import evaluate
from conformance.run import compare

FILES = {'robots-control-v1-cases.json': '85db764e98a5ed6f5c1382c7ec8dbb13e2c5c60708856a0178da5a63e8747f3c',
         'robots-control-v1-extra.json': '285f20f4974923704d31458b442b8bdec06c0ab296246f5ae65d2164ea8f0f6f'}
CASES = {c['id'].removeprefix('robots-control-'): c for name in FILES
         for c in tsep.read_json(ROOT/'tests/fixtures'/name)['cases']}


def imported(root, name, data=None):
    source = root/'input.json'
    source.write_text(json.dumps(data or CASES[name]['input']))
    return build(source, root/'bundle', assessor='Synthetic author', label=name,
                 selection_method='Prefrozen synthetic case', access='synthetic', mode='manual')


class RobotsControl(unittest.TestCase):
    def test_prefrozen_expectations_and_exact_corpus_copy(self):
        corpus = {c['id']: c for c in tsep.read_json(ROOT/'conformance/cases.json')['cases']}
        for name, digest in FILES.items():
            file = ROOT/'tests/fixtures'/name
            self.assertEqual(hashlib.sha256(file.read_bytes()).hexdigest(), digest)
        self.assertEqual(len(CASES), 45)
        for name, case in CASES.items():
            with self.subTest(case=name):
                self.assertEqual(corpus[case['id']], case)
                self.assertEqual(compare(case['expected'], evaluate(case['input']))[1:], ([], []))

    def test_aggregation_evidence_kinds_and_network_forbidden_replay(self):
        for name, expected in [('correct', 'C'), ('preproduction', 'NC'), ('missing-review', 'NT'),
                               ('http-fail-missing-robots', 'NC'), ('no-required-positive-exemption', 'C')]:
            with self.subTest(case=name), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                with patch.object(socket, 'socket', side_effect=AssertionError('Network forbidden')):
                    imported(root, name)
                    report = tsep.read_json(root/'bundle/report.json')
                    self.assertEqual(report['results'][0]['status'], expected)
                    self.assertTrue({'http', 'intent'} <= {a['kind'] for a in report['artifacts']})
                    receipt = replay(root/'bundle', root/'replay')
                    self.assertTrue(receipt['replayed'])
                    self.assertEqual(receipt['network_requests'], 0)

    def test_missing_rule_not_whole_control_and_no_automatic_review(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); data = copy.deepcopy(CASES['correct']['input'])
            data['rules'] = ['TS04-A01']
            imported(root, 'partial', data)
            self.assertEqual(tsep.read_json(root/'bundle/report.json')['results'][0]['status'], 'NT')
            full = root/'full-input.json'
            full.write_text(json.dumps(CASES['correct']['input']))
            with self.assertRaisesRegex(tsep.Invalid, 'automatic'):
                build(full, root/'automatic', assessor='Fixture', label='Fixture',
                      selection_method='Fixture', access='synthetic', mode='automatic')

    def test_synthetic_reviews_never_public_and_stale_review_never_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); imported(root, 'correct')
            with self.assertRaisesRegex(tsep.Invalid, 'provenance'):
                build(root/'input.json', root/'public', assessor='Fixture', label='Fixture',
                      selection_method='Fixture', access='public')
        data = copy.deepcopy(CASES['correct']['input'])
        data['targets'][0]['context']['network'] = 'changed'
        self.assertEqual([r['outcome'] for r in evaluate(data)], ['pass', 'inconclusive'])

    def test_blank_resource_review_workflow_then_supplied_synthetic_response(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); data = copy.deepcopy(CASES['correct']['input'])
            for d in data['targets'][0]['documents']:
                del d['access_review']
            imported(root, 'unreviewed', data)
            prepared = prepare(root/'bundle', root/'request')
            self.assertEqual(prepared['human_decisions_created'], 0)
            template = tsep.read_json(root/'request/response-template.json')
            self.assertEqual(len(template['responses']), 1)
            self.assertEqual([c['outcome'] for c in template['responses'][0]['comparisons']], [None, None])
            empty = root/'empty.json'; empty.write_text(json.dumps(template))
            with self.assertRaisesRegex(tsep.Invalid, 'Missing human response'):
                apply_review(root/'request', empty, root/'rejected')
            request = tsep.read_json(root/'request/request.json')
            row = template['responses'][0]
            row.update(reviewer='Synthetic fixture author', observed_at=datetime.now(timezone.utc).isoformat(),
                       provenance='synthetic-exercise', assistance='Authored fixture', reason='Synthetic reviewed resources',
                       examined_evidence=request['tasks'][0]['evidence'])
            for comparison in row['comparisons']:
                comparison.update(outcome='no-obstacle', reason='Synthetic reviewed content')
            completed = root/'response.json'; completed.write_text(json.dumps(template))
            apply_review(root/'request', completed, root/'reviewed')
            self.assertEqual(tsep.read_json(root/'reviewed/bundle/report.json')['results'][0]['status'], 'C')
            self.assertEqual(tsep.read_json(root/'reviewed/original-input.json'), data)

    def test_positive_review_cannot_erase_robots_failure(self):
        rows = evaluate(CASES['blocked-css']['input'])
        self.assertEqual([r['outcome'] for r in rows], ['fail', 'fail'])
        self.assertIn('disallow', rows[0]['reason'])


if __name__ == '__main__':
    unittest.main()
