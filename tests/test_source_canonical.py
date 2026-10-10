"""Core refusal/independence/replay guards; actual Node qualification is separate."""
import copy,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch

from adapters import captures,replay
from conformance.evaluate import evaluate
from conformance import source_canonical as policy
from scripts.source_canonical_check import fixture

ROOT=Path(__file__).resolve().parents[1]

class CanonicalSourcePolicy(unittest.TestCase):
    def data(self,name):
        return copy.deepcopy(next(c['input'] for c in fixture()['cases'] if c['id']=='source-canonical-'+name))

    def test_frozen_cases_present_without_rewriting_expectations(self):
        allcases={c['id']:c for c in json.loads((ROOT/'conformance/cases.json').read_text())['cases']}
        rows=fixture()['cases'];self.assertEqual(len(rows),55)
        for row in rows:self.assertEqual(allcases[row['id']],row)

    def test_unknown_and_missing_runtime_never_fall_back(self):
        for selection in ('unknown',None,policy.READER):
            data=self.data('ordinary-head');data['targets'][0]['intent']['canonical']['source_reader']=selection
            with patch.dict(os.environ,{'TSEP_SOURCE_NODE':'/missing/node24'}):
                notes=[];result=evaluate(data,source_observations=notes)
            self.assertEqual(result[0]['outcome'],'inconclusive')
            self.assertEqual(notes[0]['observations'][0]['document_url'],'https://example.com/product')
            self.assertEqual(notes[0]['observations'][0]['outcome'],'inconclusive')

    def test_independent_http_conflicts_survive_missing_runtime_and_invalid_media(self):
        cases=[c for c in fixture()['cases'] if c['id'].startswith('source-canonical-extra-')]
        with patch.dict(os.environ,{'TSEP_SOURCE_NODE':'/missing/node24'}):
            for c in cases:self.assertEqual(evaluate(c['input'])[0]['outcome'],'fail',c['id'])

    def test_a04_does_not_implicitly_use_the_new_source_policy(self):
        with patch.object(policy.source_head,'inventory',side_effect=AssertionError('A04 must not use new reader')):
            self.assertEqual(evaluate(self.data('a04-unchanged'))[0]['outcome'],'pass')

    def test_qualified_conflict_is_distinct_from_unknown_canonical(self):
        inv=json.loads((ROOT/'tests/fixtures/source-head-observation-v1.json').read_text())
        r=inv['readings']['enabled'];p='https://example.test/preferred'
        unknown=copy.deepcopy(r['inventory']['canonical'][0]);unknown['attributes']['hreflang']='fr'
        unknown['attributes']['href']='https://example.test/unknown'
        r['inventory']['canonical'].append(unknown)
        self.assertEqual(policy.decide_reading(r,p,True)[0],'inconclusive')
        r['inventory']['canonical'][0]['attributes']['href']='/relative'
        self.assertEqual(policy.decide_reading(r,p,True)[0],'fail')

    def test_full_formatted_diagnostic_bound_refuses_without_truncation(self):
        inv=json.loads((ROOT/'tests/fixtures/source-head-observation-v1.json').read_text())
        with patch.object(policy.source_head,'inventory',return_value=inv),patch.object(policy,'MAX_DIAGNOSTIC_BYTES',1500):
            notes=[];surface=policy.Surface({},b'SYNTHETIC',policy.READER,'https://example.test/preferred',True,
                                           document_url='https://example.test/preferred',diagnostics=notes)
        self.assertEqual(surface.source_decision[0],'inconclusive');self.assertFalse(surface.reviewable)
        self.assertNotIn('inventory',notes[0]);self.assertIn('4 MiB',surface.source_decision[1])
        self.assertLessEqual(len(json.dumps(notes[0],ensure_ascii=False,indent=2).encode()),1500)

    def test_diagnostic_boundary_also_refuses_a_computed_source_failure(self):
        inv=json.loads((ROOT/'tests/fixtures/source-head-observation-v1.json').read_text())
        for r in inv['readings'].values():r['inventory']['canonical'][0]['attributes']['href']='/wrong'
        def observe():
            notes=[]
            result=policy.Surface({},b'SYNTHETIC',policy.READER,'https://example.test/preferred',True,
                                  document_url='https://example.test/preferred',diagnostics=notes)
            return result,notes
        with patch.object(policy.source_head,'inventory',return_value=inv):
            result,notes=observe();self.assertEqual(result.source_decision[0],'fail')
            size=len(json.dumps(notes[0],ensure_ascii=False,indent=2).encode())
            with patch.object(policy,'MAX_DIAGNOSTIC_BYTES',size):
                self.assertEqual(observe()[0].source_decision[0],'fail')
            with patch.object(policy,'MAX_DIAGNOSTIC_BYTES',size-1):
                refused,retained=observe()
                self.assertEqual(refused.source_decision[0],'inconclusive')
                self.assertNotIn('inventory',retained[0])

    def test_bundle_preserves_source_refusal_and_exact_diagnostic_replay(self):
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{'TSEP_SOURCE_NODE':'/missing/node24'}):
            work=Path(folder);input=work/'input.json';input.write_text(json.dumps(self.data('ordinary-head')))
            captures.build(input,work/'bundle',assessor='Synthetic test',label='SYNTHETIC canonical source',
                           selection_method='Authored case',access='synthetic')
            note=work/'bundle/observations/source-observation-1.json'
            self.assertTrue(note.exists())
            self.assertEqual(json.loads(note.read_text())['observations'][0]['outcome'],'inconclusive')
            r=replay.replay(work/'bundle',work/'replay')
            self.assertTrue(r['same_source_observations']);self.assertTrue(r['replayed'])

if __name__=='__main__':unittest.main()
