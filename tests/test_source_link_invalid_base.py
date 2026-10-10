"""Versioned uncertainty, independent contradictions and end-to-end scope retention."""
import copy,hashlib,itertools,json,os,tempfile,unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch
from conformance import source_link_policy as policy
from conformance.evaluate import evaluate
from scripts.source_link_invalid_base_check import fixture
from adapters import captures,replay
from reports.html import render
import tsep
ROOT=Path(__file__).resolve().parents[1]

class SourceLinkInvalidBase(unittest.TestCase):
    def data(self,name):
        return copy.deepcopy(next(c['input'] for c in fixture()['cases'] if c['id']=='source-link-policy-invalid-base-v2-'+name))

    @contextmanager
    def retained(self,name):
        p=ROOT/'tests/fixtures/source-link-invalid-base-observations.json';raw=p.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),p.with_suffix('.sha256').read_text().strip())
        r=json.loads(raw)['rows'][name];runs=itertools.cycle(r['url_runs'])
        def resolve(requests,**kwargs):
            run=copy.deepcopy(next(runs))
            self.assertEqual(run['request_sha256'],hashlib.sha256(policy.url_resolution.validate_requests(requests)).hexdigest())
            return run
        with patch.object(policy.link_elements,'inventory',side_effect=lambda *a,**k:copy.deepcopy(r['inventory'])), \
             patch.object(policy.source_http,'inventory',side_effect=lambda *a,**k:copy.deepcopy(r.get('base_policy_metadata'))), \
             patch.object(policy.url_resolution,'resolve',side_effect=resolve):yield r

    def run_case(self,name):
        notes=[];actual=evaluate(self.data(name),source_observations=notes)
        return actual,notes[0]['observations'][0]

    def test_frozen_cases_are_in_normative_corpus(self):
        cases=fixture()['cases'];self.assertEqual(len(cases),39)
        corpus={c['id']:c for c in tsep.read_json(ROOT/'conformance/cases.json')['cases']}
        for c in cases:self.assertEqual(corpus[c['id']],c)

    def test_v1_fallback_and_v2_unknown_are_explicitly_different(self):
        for name,old in [('relative-preferred','pass'),('relative-competing','fail')]:
            with self.subTest(name=name),self.retained(name):
                data=self.data(name);data['targets'][0]['intent']['canonical']['links']['source_reader']='html-tree-links-v1'
                self.assertEqual(evaluate(data)[0]['outcome'],old)
                actual,record=self.run_case(name);self.assertEqual(actual[0]['outcome'],'inconclusive')
                self.assertEqual(record['policy_version'],'2')
                for d in record['hypotheses'].values():
                    self.assertEqual(d['candidate_base']['basis'],'first-invalid-base-unknown')
                    self.assertEqual(d['links'][0]['classification'],'unknown-base')
                    self.assertNotIn('destination',d['links'][0])
                    self.assertEqual(d['counts']['unknown_links'],1)

    def test_independent_source_conflict_survives_relative_unknown(self):
        with self.retained('independent-conflict-plus-relative'):
            actual,record=self.run_case('independent-conflict-plus-relative');self.assertEqual(actual[0]['outcome'],'fail')
            for d in record['hypotheses'].values():
                self.assertEqual(d['counts']['competing_links'],1);self.assertEqual(d['counts']['unknown_links'],1)

    def test_rendered_conflict_survives_inconclusive_source(self):
        with self.retained('rendered-independent-fail'):
            actual,record=self.run_case('rendered-independent-fail')
            self.assertEqual(actual[0]['outcome'],'fail');self.assertEqual(record['outcome'],'inconclusive')

    def test_noscript_hypotheses_cannot_be_merged(self):
        with self.retained('noscript-invalid-first'):
            actual,record=self.run_case('noscript-invalid-first');self.assertEqual(actual[0]['outcome'],'inconclusive')
            self.assertEqual(record['hypotheses']['enabled']['outcome'],'pass')
            self.assertEqual(record['hypotheses']['disabled']['outcome'],'inconclusive')

    def test_empty_and_whitespace_base_are_not_parse_failure(self):
        for name in ['base-href-empty','base-href-whitespace']:
            with self.subTest(name=name),self.retained(name):
                actual,record=self.run_case(name);self.assertEqual(actual[0]['outcome'],'fail')
                for d in record['hypotheses'].values():self.assertEqual(d['candidate_base']['unknowns'],[])

    def test_no_runtime_cannot_promote_v2(self):
        with patch.dict(os.environ,{'TSEP_SOURCE_NODE':'/missing/node24'}):
            self.assertEqual(evaluate(self.data('zero-href'))[0]['outcome'],'inconclusive')
            self.assertEqual(evaluate(self.data('rendered-independent-fail'))[0]['outcome'],'fail')

    def test_oversized_diagnostic_cannot_keep_a_conflict(self):
        with self.retained('independent-conflict-plus-relative'),patch.object(policy,'MAX_DIAGNOSTIC_BYTES',1):
            actual,record=self.run_case('independent-conflict-plus-relative')
            self.assertEqual(actual[0]['outcome'],'inconclusive');self.assertEqual(record['policy_version'],'2')
            self.assertEqual(record['reader'],'html-tree-links-v2');self.assertNotIn('inventory',record)

    def test_zero_with_invalid_base_reaches_gate_html_earl_and_replay(self):
        data=self.data('zero-href');data['rules']=['TS10-A01','TS10-A02','TS10-A03','TS10-A04']
        with self.retained('zero-href'),tempfile.TemporaryDirectory() as folder:
            root=Path(folder);inp=root/'input.json';inp.write_text(json.dumps(data))
            captures.build(inp,root/'bundle',assessor='Synthetic author',label='SYNTHETIC zero family',selection_method='Authored no-href case with fictitious supplied reviews',access='synthetic')
            report=tsep.read_json(root/'bundle/report.json');gate=tsep.read_json(root/'bundle/gate.json')
            self.assertEqual(report['results'][0]['status'],'C')
            for content in [report['results'][0]['reason'],json.dumps(gate),tsep.readable_summary(gate,'fr'),render(root/'bundle/report.json',language='fr'),(root/'bundle/earl.jsonld').read_text()]:
                self.assertIn('0 links to the declared family observed',content)
                self.assertIn('html-tree-links-v2:',content)
            self.assertTrue(replay.replay(root/'bundle',root/'replay')['same_source_observations'])

if __name__=='__main__':unittest.main()
