"""Core guards need no Node; actual Node verdict qualification is a separate command."""
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from conformance.evaluate import evaluate, directive_result, directive_values
from conformance import source_directives as policy
from adapters import captures, replay
from scripts.source_directives_check import fixture

ROOT = Path(__file__).resolve().parents[1]


class SourceDirectivePolicy(unittest.TestCase):
    def test_historical_451_inputs_and_computed_results(self):
        cases=json.loads((ROOT/'conformance/cases.json').read_text())['cases'][:451]
        actual=[{'id':c['id'],'input':c['input'],'results':evaluate(c['input'])} for c in cases]
        expected=json.loads((ROOT/'tests/fixtures/source-directives-legacy.json').read_text())
        encoded=json.dumps(actual,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
        self.assertEqual(hashlib.sha256(encoded).hexdigest(),expected['sha256'])
        fixture()

    def test_consensus_alternatives_not_simultaneous_states(self):
        for a in ('pass','fail','inconclusive'):
            for b in ('pass','fail','inconclusive'):
                self.assertEqual(policy.consensus({'enabled':{'outcome':a},'disabled':{'outcome':b}}),
                                 a if a==b and a!='inconclusive' else 'inconclusive')

    def test_unknown_and_absent_runtime_never_fall_back(self):
        for reader in ('unknown',None,policy.READER):
            data=copy.deepcopy(fixture()['cases'][0]['input']);data['targets'][0]['intent']['source_reader']=reader
            with patch.dict(os.environ,{'TSEP_SOURCE_NODE':'/definitely/not/a/runtime'}):
                notes=[];result=evaluate(data,source_observations=notes)
            self.assertEqual(result[0]['outcome'],'inconclusive');self.assertEqual(len(notes),1)
            self.assertEqual(notes[0]['observations'][0]['outcome'],'inconclusive')

    def test_source_profile_never_reparses_a_serialized_dom(self):
        intent={'crawler':'googlebot','indexing':'allow','source_reader':policy.READER}
        with patch.object(policy.source_http,'inventory',side_effect=AssertionError('must not execute')):
            outcome,_=directive_result({'content-type':['text/html; charset=utf-8']},
                '<html><head></head><body></body></html>',intent)
        self.assertEqual(outcome,'pass')

    @staticmethod
    def reading():
        return {'complete':True,'parse_errors':[],'template_containers':[], 'metadata':[]}

    def test_foreign_and_ambiguous_metadata_are_not_absence(self):
        item={'template_indices':[],'attributes':{'name':'robots','content':'noindex'},
              'namespace':policy.HTML,'context':'body','ancestor_namespaces':[None,policy.HTML]}
        intent={'crawler':'googlebot','indexing':'allow'}
        base=self.reading();base['metadata']=[item]
        self.assertEqual(policy.decide_reading(base,{},intent,directive_values)[0],'fail')
        for kind in ('namespace','ancestor','pseudo','missing','mixed'):
            reading=copy.deepcopy(base);r=reading['metadata'][0]
            if kind=='namespace':r['namespace']='svg'
            if kind=='ancestor':r['ancestor_namespaces'].append('svg')
            if kind=='pseudo':r['attributes']={'http-equiv':'X-Robots-Tag','content':'noindex'}
            if kind=='missing':r['attributes'].pop('content')
            if kind=='mixed':r['attributes']['itemprop']='robots'
            with self.subTest(kind=kind),self.assertRaises(ValueError):
                policy.decide_reading(reading,{},intent,directive_values)
        base['metadata'][0]['template_indices']=[0]
        self.assertEqual(policy.decide_reading(base,{},intent,directive_values)[0],'pass')

    def test_size_refusal_and_recorded_runtime_failure(self):
        inv={'readings':{mode:self.reading() for mode in ('enabled','disabled')},'runtime':{'node':'synthetic'}}
        with patch.object(policy.source_http,'inventory',return_value=inv),patch.object(policy,'MAX_DIAGNOSTIC_BYTES',1):
            records=[];result=policy.assess({},b'x',{'source_reader':policy.READER,'crawler':'googlebot','indexing':'allow'},combine=directive_values,diagnostics=records)
        self.assertEqual(result[0],'inconclusive');self.assertNotIn('inventory',records[0])
        self.assertIn('4 MiB',result[1])

    def test_final_diagnostic_budget_includes_decisions_and_formatted_reasons(self):
        inv={'readings':{mode:self.reading() for mode in ('enabled','disabled')}}
        with patch.object(policy.source_http,'inventory',return_value=inv),patch.object(policy,'MAX_DIAGNOSTIC_BYTES',1500):
            notes=[]
            result=policy.assess({},b'x',{'source_reader':policy.READER},
                combine=lambda *args:('pass','x'*1500),diagnostics=notes)
        self.assertEqual(result[0],'inconclusive')
        self.assertLessEqual(len(json.dumps(notes[0],ensure_ascii=False,indent=2).encode()),1500)
        self.assertNotIn('inventory',notes[0]);self.assertNotIn('hypotheses',notes[0])

    def test_bundle_retains_and_replay_checks_even_unavailable_reader(self):
        data=fixture()['cases'][0]['input']
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{'TSEP_SOURCE_NODE':'/missing'}):
            work=Path(folder);source=work/'input.json';source.write_text(json.dumps(data))
            captures.build(source,work/'bundle',assessor='Synthetic author',label='Synthetic source reader refusal',
                           selection_method='Frozen case',access='synthetic')
            observed=work/'bundle/observations/source-observation-1.json'
            self.assertTrue(observed.exists())
            self.assertEqual(json.loads(observed.read_text())['observations'][0]['outcome'],'inconclusive')
            result=replay.replay(work/'bundle',work/'replay')
            self.assertTrue(result['same_source_observations']);self.assertTrue(result['replayed'])
            # A coherently rehashed extra diagnostic still cannot be replayed as equivalent.
            changed=json.loads(observed.read_text());changed['observations'][0]['reason']='invented'
            observed.write_text(json.dumps(changed))
            report_path=work/'bundle/report.json';report=json.loads(report_path.read_text())
            for artifact in report['artifacts']:
                if artifact['path']==str(observed.relative_to(work/'bundle')):artifact['sha256']=hashlib.sha256(observed.read_bytes()).hexdigest()
            report_path.write_text(json.dumps(report))
            from adapters.package import seal
            seal(work/'bundle')
            with self.assertRaisesRegex(ValueError,'Replay differs'):
                replay.replay(work/'bundle',work/'different')
            self.assertFalse(json.loads((work/'different/replay.json').read_text())['same_source_observations'])


if __name__=='__main__':unittest.main()
