"""Prior client/product separation for TS04; no simulated engine observation."""
import copy
import hashlib
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

import tsep
from adapters.captures import build
from adapters.replay import replay
from conformance.evaluate import evaluate
from conformance import robots_control
from reports.html import render

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    'robots-agent-v1-cases': '89fb9ea0a9ca9b62f7627b05c5e18ddb9e39aa736a15010b0a59dbbdbe1f774f',
    'robots-agent-hops-v1-cases': 'f2b06529739cb9891b40c26b143b94ecbad7ee1c1527eb142cbb25be7b391863',
}
CASES = {c['id'].removeprefix('robots-agent-'): c
         for name in FILES for c in tsep.read_json(ROOT/'tests/fixtures'/(name+'.json'))['cases']}


class RobotsAgent(unittest.TestCase):
    def test_prefrozen_expectations_and_corpus(self):
        corpus = {c['id']: c for c in tsep.read_json(ROOT/'conformance/cases.json')['cases']}
        for name, sha in FILES.items():
            p = ROOT/'tests/fixtures'/(name+'.json')
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), sha)
            self.assertEqual(p.with_suffix('.sha256').read_text().split()[0], sha)
        self.assertEqual(len(CASES), 26)
        for case in CASES.values():
            with self.subTest(case=case['id']):
                before = copy.deepcopy(case)
                rows = evaluate(case['input'])
                self.assertEqual([{k: row[k] for k in ('rule_id', 'target', 'outcome')} for row in rows], case['expected'])
                self.assertEqual(case, before)
                self.assertEqual(corpus[case['id']], case)

    def test_no_engine_access_claim_on_http_denial(self):
        for code in (401, 403, 429, 503):
            rows = evaluate(CASES['client-http-'+str(code)]['input'])
            self.assertEqual([r['outcome'] for r in rows], ['pass', 'fail'])
            self.assertIn('HTTP observations refer to declared client=TSEP/0.1.0', rows[1]['reason'])
            self.assertIn('actual Googlebot HTTP access unobserved', rows[1]['reason'])

    def test_same_product_group_as_ts07_shared_reader(self):
        for name in ('google-allow-client-disallow', 'google-disallow-client-allow'):
            target = CASES[name]['input']['targets'][0]
            url = target['intent']['robots_plan']['resources'][0]['url']
            observed, reason = robots_control.ts04_policy_for(target, url)
            common, detail = robots_control.policy_for(target, url, client_representation_only=True)
            self.assertEqual(observed, common)
            self.assertTrue(reason.startswith(detail))
            self.assertIn('actual Googlebot representation unobserved', reason)

    def test_supplied_review_still_bound_to_exact_intent(self):
        data = copy.deepcopy(CASES['google-allow-client-disallow']['input'])
        data['targets'][0]['intent']['robots_policy']['product_token'] = 'GOOGLEBOT'
        self.assertEqual([r['outcome'] for r in evaluate(data)], ['pass', 'inconclusive'])

    def test_native_report_and_offline_replay_preserve_missing_review(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root/'input.json'
            source.write_text(json.dumps(CASES['missing-review']['input']))
            with patch.object(socket, 'socket', side_effect=AssertionError('No network')):
                summary = build(source, root/'bundle', assessor='Synthetic fixture author',
                    label='TS04 supplied client representation', selection_method='Prefrozen synthetic matrix',
                    access='synthetic', mode='automatic')
                self.assertEqual(summary['counts']['NT'], 1)
                self.assertTrue(replay(root/'bundle', root/'replay')['replayed'])
            self.assertEqual(tsep.read_json(root/'bundle/assessment.json')[1]['outcome'], 'inconclusive')

    def test_positive_fixture_does_not_enable_automatic_whole_control(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root/'input.json'
            source.write_text(json.dumps(CASES['google-allow-client-disallow']['input']))
            with self.assertRaisesRegex(tsep.Invalid, 'automatic'):
                build(source, root/'bundle', assessor='Synthetic fixture author', label='Synthetic',
                      selection_method='Synthetic', access='synthetic', mode='automatic')

    def test_client_scope_survives_control_gate_html_earl_and_replay(self):
        for name, expected in [('client-http-403', 'NC'), ('missing-review', 'NT'),
                               ('google-allow-client-disallow', 'C')]:
            with self.subTest(case=name), tempfile.TemporaryDirectory() as folder:
                root = Path(folder); source = root/'input.json'
                source.write_text(json.dumps(CASES[name]['input']))
                summary = build(source, root/'bundle', assessor='Synthetic fixture author',
                    label='Synthetic TS04', selection_method='Prefrozen synthetic matrix',
                    access='synthetic', mode='manual')
                report = tsep.read_json(root/'bundle/report.json')
                self.assertEqual(report['results'][0]['status'], expected)
                phrase = 'actual Googlebot access unobserved'
                self.assertIn(phrase, report['results'][0]['reason'])
                self.assertIn(phrase, summary['scope']['label'])
                self.assertIn(phrase, tsep.readable_summary(summary, 'fr'))
                self.assertIn(phrase, tsep.readable_summary(summary, 'en'))
                self.assertIn(phrase, render(root/'bundle/report.json', language='fr'))
                graph = tsep.earl(report, summary)['@graph']
                control = next(row for row in graph if row.get('earl:test', {}).get('@id', '').endswith(':TS04'))
                self.assertIn(phrase, control['earl:result']['earl:info'])
                self.assertTrue(replay(root/'bundle', root/'replay')['replayed'])


if __name__ == '__main__':
    unittest.main()
