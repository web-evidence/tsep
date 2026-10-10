"""Profile selection, independent surfaces, finite bounds and delivery propagation."""
import copy,hashlib,itertools,json,os,tempfile,unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch
from conformance import source_link_policy as policy
from conformance.evaluate import evaluate,binding_digest
from scripts.source_link_policy_check import fixture
from adapters import captures,replay
from reports.html import render
import tsep

ROOT=Path(__file__).resolve().parents[1]
class SourceLinkPolicy(unittest.TestCase):
    def data(self,name):
        return copy.deepcopy(next(c['input'] for c in fixture()['cases'] if c['id']=='source-link-policy-'+name))

    @contextmanager
    def retained(self,name):
        p=ROOT/'tests/fixtures/source-link-policy-observation-v1.json';raw=p.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),p.with_suffix('.sha256').read_text().strip())
        r=json.loads(raw)['rows'][name];runs=itertools.cycle(r['url_runs'])
        def resolve(requests,**kwargs):
            run=copy.deepcopy(next(runs))
            self.assertEqual(run['request_sha256'],hashlib.sha256(policy.url_resolution.validate_requests(requests)).hexdigest())
            return run
        with patch.object(policy.link_elements,'inventory',side_effect=lambda *a,**k:copy.deepcopy(r['inventory'])), \
             patch.object(policy.url_resolution,'resolve',side_effect=resolve):yield r

    def test_frozen_active_corpus_and_correction_provenance(self):
        cases=fixture()['cases'];self.assertEqual(len(cases),58)
        corpus={c['id']:c for c in tsep.read_json(ROOT/'conformance/cases.json')['cases']}
        for c in cases:self.assertEqual(corpus[c['id']],c)
        v1=tsep.read_json(ROOT/'tests/fixtures/source-link-policy-v1.json')
        self.assertEqual(len(v1['cases']),57)
        correction=tsep.read_json(ROOT/'provenance/source-link-oracle-correction.json')
        self.assertEqual(correction['initial']['matched'],56)
        self.assertEqual(correction['failed_case']['actual'],'pass')

    def test_missing_runtime_or_selection_never_falls_back(self):
        for selector in [None,'unknown',policy.READER]:
            data=self.data('ordinary');data['targets'][0]['intent']['canonical']['links']['source_reader']=selector
            with patch.dict(os.environ,{'TSEP_SOURCE_NODE':'/missing/node24'}):
                notes=[];r=evaluate(data,source_observations=notes)
            self.assertEqual(r[0]['outcome'],'inconclusive');self.assertTrue(notes)

    def test_absent_selector_preserves_legacy_without_optional_process(self):
        data=self.data('ordinary');del data['targets'][0]['intent']['canonical']['links']['source_reader']
        with patch.object(policy.url_resolution,'resolve',side_effect=AssertionError('No implicit profile')):
            self.assertEqual(evaluate(data)[0]['outcome'],'pass')

    def test_rendered_failure_survives_missing_source_runtime(self):
        with patch.dict(os.environ,{'TSEP_SOURCE_NODE':'/missing/node24'}):
            self.assertEqual(evaluate(self.data('structured-links-conflict'))[0]['outcome'],'fail')

    def test_redirect_diagnostic_keeps_request_and_final_distinct(self):
        with patch.dict(os.environ,{'TSEP_SOURCE_NODE':'/missing/node24'}):
            notes=[];evaluate(self.data('redirect-final-fallback'),source_observations=notes)
        record=notes[0]['observations'][0]
        self.assertEqual(record['requested_url'],'https://example.com/catalog')
        self.assertEqual(record['document_url'],'https://example.com/product')

    def test_diagnostic_limit_also_invalidates_computed_contradiction(self):
        def call():
            notes=[];r=evaluate(self.data('competing-relative'),source_observations=notes)
            return r,notes[0]['observations'][0]
        with self.retained('competing-relative'):
            r,n=call();self.assertEqual(r[0]['outcome'],'fail');size=len(json.dumps(n,ensure_ascii=False,indent=2).encode())
            with patch.object(policy,'MAX_DIAGNOSTIC_BYTES',size):self.assertEqual(call()[0][0]['outcome'],'fail')
            with patch.object(policy,'MAX_DIAGNOSTIC_BYTES',size-1):
                r,n=call();self.assertEqual(r[0]['outcome'],'inconclusive');self.assertNotIn('inventory',n)

    def test_incomplete_inventory_never_exposes_partial_conflict(self):
        p=tsep.read_json(ROOT/'tests/fixtures/source-link-policy-observation-v1.json')['rows']['competing-relative']
        reading=copy.deepcopy(p['inventory']['readings']['enabled']);reading['complete']=False
        with self.assertRaisesRegex(ValueError,'Incomplete'):
            policy.decide_reading(reading,None,{},'https://example.com/catalog',[],None,set(),lambda x:[])

    def test_zero_family_scope_reaches_control_gate_html_earl_and_replay(self):
        data=self.data('zero-family-links');data['rules']=['TS10-A01','TS10-A02','TS10-A03','TS10-A04']
        t=data['targets'][0];t['content_review']['source_sha256']=binding_digest({k:t[k] for k in ('intent','context','documents')})
        with self.retained('zero-family-links'),tempfile.TemporaryDirectory() as folder:
            root=Path(folder);inp=root/'input.json';inp.write_text(json.dumps(data))
            captures.build(inp,root/'bundle',assessor='Synthetic author',label='SYNTHETIC finite family',selection_method='Authored scenario',access='synthetic')
            report=tsep.read_json(root/'bundle/report.json');gate=tsep.read_json(root/'bundle/gate.json')
            self.assertEqual(report['results'][0]['status'],'C')
            phrase='0 links to the declared family observed'
            for content in [report['results'][0]['reason'],json.dumps(gate),tsep.readable_summary(gate,'fr'),
                            render(root/'bundle/report.json',language='fr'),(root/'bundle/earl.jsonld').read_text()]:
                self.assertIn(phrase,content)
            self.assertTrue(replay.replay(root/'bundle',root/'replay')['same_source_observations'])

if __name__=='__main__':unittest.main()
