"""Frozen synthetic inspection cases and offline comparison workflow. Apache-2.0."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import tsep
from adapters.captures import build as build_technical
from adapters.package import json_bytes, inventory, seal
from diagnostics import search_console as sc

FIXTURE = ROOT/'tests/fixtures/search-console-v1-cases.json'
FROZEN = tsep.read_json(FIXTURE)


class SearchConsoleComparison(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
        self.observation=self.root/'observation'; self.observation.mkdir()
        self.bundle=self.root/'technical'; self.output=self.root/'comparison'
        self.request={'inspectionUrl':'https://example.com/product','siteUrl':'sc-domain:example.com'}
        self.response={'inspectionResult':{'indexStatusResult':copy.deepcopy(FROZEN['cases'][0]['index_status_result'])}}
        self.meta={'kind':'tsep-url-inspection-observation','format_version':'1','provenance':'synthetic-exercise',
                   'description':'Authored API-shaped response; no Google request/account data',
                   'retrieved_at':FROZEN['retrieved_at'],'http_status':200,'request_sha256':'','response_sha256':'','change':None}

    def tearDown(self):
        self.temp.cleanup()

    def write(self):
        for name,value in [('request',self.request),('response',self.response)]:
            raw=json_bytes(value);(self.observation/(name+'.json')).write_bytes(raw)
            self.meta[name+'_sha256']=hashlib.sha256(raw).hexdigest()
        (self.observation/'manifest.json').write_bytes(json_bytes(self.meta))

    def prepare(self):
        self.write()
        build_technical(ROOT/'examples/captures/ts10-family.json',self.bundle,assessor='Synthetic author',
                        label='Synthetic technical evidence',selection_method='Authored example; no actual capture',
                        access='synthetic',mode='manual')

    def test_prefrozen_google_fields_and_literal_comparisons(self):
        self.assertEqual(tsep.digest(FIXTURE),'cd5832d8d76175528631dae464577be7f9f78b77f10500c8b82f9d47428240df')
        self.assertEqual(FIXTURE.with_suffix('.sha256').read_text().strip(),tsep.digest(FIXTURE))
        for case in FROZEN['cases']:
            with self.subTest(case=case['id']):
                value=sc.engine_state({'inspectionResult':{'indexStatusResult':case['index_status_result']}},200,FROZEN['retrieved_at'])
                actual={'canonical':value['google_vs_user_canonical'],'crawl':value['fields']['lastCrawlTime']['state'],
                        'indexing':value['fields']['indexingState']['state']}
                self.assertEqual(actual,case['expected'])

    def test_property_binding_has_host_boundaries_and_path_case(self):
        for request in [{'inspectionUrl':'https://example.com.evil.test/product','siteUrl':'sc-domain:example.com'},
                        {'inspectionUrl':'https://otherexample.com/product','siteUrl':'sc-domain:example.com'},
                        {'inspectionUrl':'http://example.com/product','siteUrl':'https://example.com/'},
                        {'inspectionUrl':'https://example.com/Sub/item','siteUrl':'https://example.com/sub/'},
                        {'inspectionUrl':'https://example.com/submarine/item','siteUrl':'https://example.com/sub/'},
                        {'inspectionUrl':'https://example.com/sub/../outside','siteUrl':'https://example.com/sub/'},
                        {'inspectionUrl':'https://example.com/sub/%2e%2e/outside','siteUrl':'https://example.com/sub/'},
                        dict(self.request,access_token='not-allowed')]:
            with self.subTest(request=request),self.assertRaises(ValueError):sc.check_request(request)
        self.assertEqual(sc.check_request({'inspectionUrl':'https://shop.example.com/product','siteUrl':'sc-domain:example.com'}),'https://shop.example.com/product')
        self.assertEqual(sc.check_request({'inspectionUrl':'https://example.com/sub/item','siteUrl':'https://example.com/sub/'}),'https://example.com/sub/item')

    def test_nanoseconds_and_timezones_keep_order(self):
        a='2026-10-09T10:00:00.123456788Z';b='2026-10-09T10:00:00.123456789Z'
        self.assertEqual(sc.relation(a,b),'before')
        self.assertEqual(sc.relation(b,'2026-10-09T12:00:00.123456789+02:00'),'same-time')
        self.assertEqual(sc.relation(None,b),'unavailable')

    def test_compare_replay_offline_retains_raw_and_does_not_change_technical_verdict(self):
        self.prepare();before=inventory(self.bundle)
        raw=(self.observation/'response.json').read_bytes()
        with patch('socket.socket',side_effect=AssertionError('Network forbidden')),patch('socket.getaddrinfo',side_effect=AssertionError('DNS forbidden')):
            result=sc.build(self.observation,self.bundle,self.output)
            replay=sc.replay(self.output,self.root/'replayed')
        self.assertTrue(replay['same_comparison']);self.assertTrue(result['technical_replayed'])
        self.assertFalse(result['tsep_verdict_created'])
        self.assertEqual(result['comparisons']['google_vs_declared_preference'],'equal')
        self.assertEqual(result['comparisons']['crawl_vs_change'],'unavailable')
        self.assertEqual(result['comparisons']['crawl_vs_technical_source'],'after')
        self.assertEqual((self.output/'observation/response.json').read_bytes(),raw)
        self.assertEqual(inventory(self.bundle),before)
        self.assertIn('EXEMPLE SYNTHÉTIQUE',(self.output/'report-fr.html').read_text())
        self.assertTrue(result['technical']['canonical_signals'])

    def test_deep_family_member_is_exactly_bound_not_a_family_verdict_per_url(self):
        self.request['inspectionUrl']='https://example.com/product?color=blue'
        self.prepare();result=sc.build(self.observation,self.bundle,self.output)
        self.assertEqual(result['technical']['inspected_url'],self.request['inspectionUrl'])
        self.assertEqual(result['technical']['assessment_target'],'https://example.com/product')
        self.assertIn('not automatically',result['technical']['atomic_result_scope'])

    def test_mismatched_url_and_synthetic_real_mixing_are_rejected(self):
        self.prepare()
        self.request['inspectionUrl']='https://example.com/unrelated';self.write()
        with self.assertRaisesRegex(ValueError,'unique exact'):sc.build(self.observation,self.bundle,self.output)
        self.assertFalse(self.output.exists())
        self.meta['provenance']='supplied-google-api';self.write()
        with self.assertRaisesRegex(ValueError,'mix synthetic'):sc.build(self.observation,self.bundle,self.output)

    def test_api_errors_and_missing_index_results_remain_unavailable(self):
        for response,status in [({'error':{'code':403,'message':'Authored permission failure'}},403),
                                ({'inspectionResult':{}},200),({},200)]:
            value=sc.engine_state(response,status,FROZEN['retrieved_at'])
            self.assertNotEqual(value['state'],'recorded')
            self.assertEqual(value['google_vs_user_canonical'],'unavailable')
            self.assertEqual(value['fields']['googleCanonical']['state'],'absent')

    def test_malformed_known_fields_and_unfamiliar_fields_are_retained(self):
        index={'googleCanonical':None,'indexingState':{'new':'shape'},'lastCrawlTime':'bad','newField':'retained'}
        value=sc.engine_state({'inspectionResult':{'indexStatusResult':index}},200,FROZEN['retrieved_at'])
        self.assertEqual(value['fields']['indexingState'],{'state':'invalid','value':{'new':'shape'}})
        self.assertEqual(value['uninterpreted_index_fields'],['newField'])

    def test_prior_crawl_and_future_crawl_dont_become_regressions(self):
        self.prepare()
        self.response['inspectionResult']['indexStatusResult']['lastCrawlTime']='2026-10-01T00:00:00Z';self.write()
        result=sc.build(self.observation,self.bundle,self.output)
        self.assertEqual(result['comparisons']['crawl_vs_technical_source'],'before')
        self.output=self.root/'future'
        self.response['inspectionResult']['indexStatusResult']['lastCrawlTime']='2099-01-01T00:00:00Z';self.write()
        result=sc.build(self.observation,self.bundle,self.output)
        self.assertEqual(result['engine']['crawl_vs_retrieval'],'inconsistent-crawl-after-retrieval')
        self.assertEqual(result['comparisons']['crawl_vs_technical_source'],'unavailable')

    def test_change_needs_separate_evidence_and_keeps_chronology(self):
        raw=b'Synthetic deployment record: canonical changed; not actual site evidence.\n'
        self.meta['change']={'occurred_at':'2026-10-09T09:30:00Z','description':'Authored deployment example',
                             'evidence_sha256':hashlib.sha256(raw).hexdigest()}
        self.prepare()
        with self.assertRaises(ValueError):sc.build(self.observation,self.bundle,self.output)
        (self.observation/'change-evidence.txt').write_bytes(raw)
        result=sc.build(self.observation,self.bundle,self.output)
        self.assertEqual(result['comparisons']['crawl_vs_change'],'after')
        self.assertEqual(result['comparisons']['change_vs_technical_source'],'before')
        self.assertEqual((self.output/'observation/change-evidence.txt').read_bytes(),raw)

    def test_changed_raw_evidence_or_computed_comparison_is_rejected(self):
        self.prepare()
        (self.observation/'response.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'Changed response'):sc.build(self.observation,self.bundle,self.output)
        self.write();sc.build(self.observation,self.bundle,self.output)
        value=tsep.read_json(self.output/'comparison.json');value['comparisons']['google_vs_declared_preference']='different'
        (self.output/'comparison.json').write_bytes(json_bytes(value));seal(self.output)
        with self.assertRaisesRegex(ValueError,'Comparison differs'):sc.replay(self.output,self.root/'replayed')
        self.assertTrue((self.root/'replayed/comparison.json').exists())

    def test_indexing_permission_is_not_reported_as_actual_indexing(self):
        engine=sc.engine_state({'inspectionResult':{'indexStatusResult':{'indexingState':'INDEXING_ALLOWED','verdict':'NEUTRAL'}}},200,FROZEN['retrieved_at'])
        local={'indexing_intent':'allow','canonical_intent':{'state':'absent','value':None},'canonical_signals':[],'source_observed_at':None}
        result=sc.compare(self.meta,self.request,engine,local)
        self.assertEqual(result['comparisons']['indexing_permission_vs_intent'],'equal')
        self.assertEqual(result['engine']['fields']['verdict']['value'],'NEUTRAL')
        self.assertFalse(result['tsep_verdict_created'])

    def test_cli_and_html_escape_untrusted_fields(self):
        self.response['inspectionResult']['indexStatusResult']['coverageState']='<script>bad()</script>'
        self.prepare()
        run=subprocess.run([sys.executable,str(ROOT/'diagnostics/search_console.py'),'compare',str(self.observation),'--technical',str(self.bundle),'--output',str(self.output)],cwd=self.root,text=True,capture_output=True)
        self.assertEqual(run.returncode,0,run.stderr)
        html=(self.output/'report-fr.html').read_text()
        self.assertIn('&lt;script&gt;',html);self.assertNotIn('<script>',html)
        self.assertEqual(json.loads(run.stdout)['network_requests'],0)

    def test_google_verdict_and_coverage_text_do_not_replace_tsep_results(self):
        self.response['inspectionResult']['indexStatusResult'].update(verdict='FAIL',coverageState='PASS — arbitrary localized description')
        self.prepare();result=sc.build(self.observation,self.bundle,self.output)
        original=tsep.read_json(self.bundle/'report.json')
        self.assertEqual(tsep.read_json(self.output/'technical-original/report.json'),original)
        self.assertEqual(result['engine']['fields']['verdict']['value'],'FAIL')
        html=(self.output/'report-fr.html').read_text()
        self.assertIn('Verdict rapporté par Google (API)',html)
        self.assertEqual(result['technical']['http_client'],'googlebot')
        self.assertFalse(result['tsep_verdict_created'])


if __name__=='__main__':unittest.main()
