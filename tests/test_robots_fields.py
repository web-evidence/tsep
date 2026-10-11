"""Known ancillary fields, independent grouping expectations and retained scope."""
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
from conformance import robots
from conformance.evaluate import evaluate
from reports.html import render

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT/'tests/fixtures'
DIGESTS = {
    'robots-fields-body-v1-cases': '5965fb189ab4b6ea945de6493441ddb649cb306d6d757ff5cc114b0b625d8824',
    'robots-fields-control-v1-cases': '850abe87f911933db80e54632d79be48cba5f452f7ec8d4e49c962876ad3554c',
}
BODY = tsep.read_json(FIX/'robots-fields-body-v1-cases.json')['cases']
CONTROLS = tsep.read_json(FIX/'robots-fields-control-v1-cases.json')['cases']


def canonical_digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


class RobotsFields(unittest.TestCase):
    def test_prefrozen_body_expectations_and_exact_fields(self):
        for stem, digest in DIGESTS.items():
            self.assertEqual(tsep.digest(FIX/(stem+'.json')), digest)
            self.assertEqual((FIX/(stem+'.sha256')).read_text().split()[0], digest)
        self.assertEqual(len(BODY), 44)
        for case in BODY:
            with self.subTest(case=case['id']):
                value = robots.body_policy(case['body'], case['target'], case['product_token'], robots.GOOGLE_FIELDS)
                self.assertEqual(value['decision'], case['expected_v2'], value)
                self.assertEqual([r['line'] for r in value['winning_lines']], case['winning_lines'])
                self.assertEqual([[r['line'], r['field']] for r in value['ignored_fields']], case['ignored_fields'])
                old = robots.body_policy(case['body'],case['target'],case['product_token'],robots.GOOGLE)
                self.assertEqual(old['decision'],case['expected_v1'])

    def test_prefrozen_control_expectations_and_corpus(self):
        corpus = {c['id']: c for c in tsep.read_json(ROOT/'conformance/cases.json')['cases']}
        self.assertEqual(len(CONTROLS), 18)
        for case in CONTROLS:
            with self.subTest(case=case['id']):
                original = copy.deepcopy(case)
                actual = [{k:r[k] for k in ('rule_id','target','outcome')} for r in evaluate(case['input'])]
                self.assertEqual(actual,case['expected'])
                self.assertEqual(case,original)
                self.assertEqual(case,corpus[case['id']])

    def test_retained_full_line_is_outside_access_scope(self):
        raw = '\tCoNtEnT-SiGnAl : search=no, ai-train=no # retained comment'
        value = robots.body_policy('User-agent: *\n'+raw+'\nAllow: /\n',
                                   'https://example.com/page','Googlebot',robots.GOOGLE_FIELDS)
        self.assertEqual(value['decision'],'allow')
        self.assertEqual(value['ignored_fields'][0]['raw_line'],raw)
        self.assertEqual(value['ignored_fields'][0]['value'],'search=no, ai-train=no')
        self.assertIn('no usage-policy assessment',value['ignored_fields'][0]['scope'])
        self.assertIn('22b355ff855419e6a3ff8ff09c0ad7fdb17116f9',value['ignored_fields_source'])

    def test_pinned_registry_has_an_explicit_source(self):
        record = tsep.read_json(ROOT/'provenance/robots-fields-v2.json')
        self.assertEqual(set(record['registry']),robots.NON_ACCESS_FIELDS)
        self.assertEqual(len(record['registry']),13)
        self.assertEqual(record['google_code_commit'],'22b355ff855419e6a3ff8ff09c0ad7fdb17116f9')
        self.assertEqual(len(record['sources']),5)
        self.assertTrue(all(len(s['sha256'])==64 and s['captured_at'] for s in record['sources']))

    def test_status_wrapper_preserves_google_policy_and_attribution(self):
        from tests.test_robots_policy import capture, hop
        data = capture();data['profile']=robots.GOOGLE_FIELDS
        for code, expected in [(200,'disallow'),(204,'allow'),(403,'allow'),(429,'unknown'),(503,'unknown')]:
            with self.subTest(status=code):
                data['http']=[hop('https://example.com/robots.txt',code,
                    b'User-agent: *\nContent-signal: search=yes\nDisallow: /private\n' if code==200 else b'')]
                self.assertEqual(robots.inspect_capture(data)['decision'],expected)
        data['http']=[hop('https://example.com/robots.txt')]
        data['request_user_agent']='Different'
        self.assertEqual(robots.inspect_capture(data)['decision'],'unknown')

    def test_bounded_previews_keep_full_capture_and_escape_html(self):
        case = copy.deepcopy(CONTROLS[0]['input']);target=case['targets'][0]
        value='<script>alert(1)</script>'+('x'*170)
        body='User-agent: *\n'+('Content-signal: '+value+'\n')*18+'Allow: /\n'
        target['robots']['http'][0]['response']='HTTP/1.1 200 Test\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: '+str(len(body.encode()))+'\r\n\r\n'+body
        reading=robots.body_policy(body,'https://example.com/page','Googlebot',robots.GOOGLE_FIELDS)
        self.assertEqual(len(reading['ignored_fields']),18)
        self.assertEqual(reading['ignored_fields'][-1]['value'],value)
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'input.json';source.write_text(json.dumps(case))
            build(source,root/'bundle',assessor='Synthetic author',label='Synthetic field handling',
                  selection_method='Authored fixture',access='synthetic',mode='automatic')
            reason=tsep.read_json(root/'bundle/assessment.json')[0]['reason']
            self.assertIn('additional fields=2',reason)
            self.assertIn('"value_truncated": true',reason)
            self.assertEqual(tsep.read_json(root/'bundle/input.json'),case)
            html=render(root/'bundle/report.json',language='fr')
            self.assertNotIn('<script>alert(1)</script>',html)
            self.assertIn('&lt;script&gt;',html)

    def test_results_replay_and_do_not_create_whole_control_success(self):
        for name,status in [('allowed-missing-review','NT'),('blocked-css','NC'),('synthetic-reviewed','C')]:
            case=next(c for c in CONTROLS if c['id']=='robots-fields-'+name)
            with self.subTest(case=name), tempfile.TemporaryDirectory() as folder:
                root=Path(folder);source=root/'input.json';source.write_text(json.dumps(case['input']))
                with patch.object(socket,'socket',side_effect=AssertionError('No network')):
                    result=build(source,root/'bundle',assessor='Synthetic author',label='Synthetic',
                        selection_method='Authored fixture',access='synthetic',mode='manual')
                    self.assertEqual(result['counts'][status],1)
                    self.assertTrue(replay(root/'bundle',root/'replay')['replayed'])
                report=tsep.read_json(root/'bundle/report.json')
                self.assertIn('actual Googlebot access unobserved',report['results'][0]['reason'])
                self.assertIn('google-robotstxt-fields-v2',render(root/'bundle/report.json',language='fr'))

    def test_prior_cases_and_body_profiles_are_exactly_preserved(self):
        corpus=tsep.read_json(ROOT/'conformance/cases.json')['cases']
        prior=[{'case':c,'rows':evaluate(c['input'])} for c in corpus if not c['id'].startswith(('robots-fields-', 'sitemap-locations-', 'source-directives-', 'source-canonical-', 'source-link-policy-', 'http-canonical-', 'preview-', 'performance-', 'agents-'))]
        self.assertEqual(len(prior),409)
        self.assertEqual(canonical_digest(prior),'4f7a447d9c6b54fbc1bf331a33861451ad0ce5cff73ee2a1c823dfb89c675da5')
        body=[{'case':c['id'],'profile':p,'result':robots.body_policy(c['body'],c['target'],c['product_token'],p)}
              for c in BODY[:42] for p in [robots.GOOGLE,robots.RFC]]
        self.assertEqual(canonical_digest(body),'52bca2accba19b1f638b242bee8e801744a19b2dcfa730f4f157cd4261b1f026')


if __name__=='__main__':
    unittest.main()
