"""Legacy preservation, lossless diagnostic contexts and prospective opt-in guards."""
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from adapters import captures, replay
from conformance.evaluate import evaluate
from conformance import source_markers as policy
from experiments import source_markers as observer
from reports import html
from scripts.identity_markers_check import fixture
from scripts.source_markers_check import fixture as frozen

ROOT = Path(__file__).resolve().parents[1]


class IdentityMarkers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {c['id']: c for c in fixture()['cases']}
        cls.inventories = {r['id']: r['inventory'] for r in frozen('source-markers-observations-v1.json')['observations']}

    def observe_retained(self, id):
        case = self.cases['identity-markers-'+id]
        intent = case['input']['targets'][0]['intent']
        criteria = {k: intent[k] for k in ('required_markers', 'forbidden_markers')}
        readings, result = observer.hypotheses(self.inventories[id], criteria)
        return {'experiment_version': observer.VERSION, 'source_sha256': observer.identity(),
                'content_types': ['text/html; charset=utf-8'], 'inventory': self.inventories[id],
                'readings': readings, 'candidate_consensus': result}

    def test_legacy_inputs_and_all_174_ts01_results_unchanged(self):
        baseline = json.loads((ROOT/'tests/fixtures/identity-markers-legacy.json').read_text())
        cases = json.loads((ROOT/'conformance/cases.json').read_text())['cases'][:baseline['corpus_prefix_cases']]
        rows = []
        with patch.object(policy.reader, 'observe', side_effect=AssertionError('no legacy opt-in')):
            for case in cases:
                data = copy.deepcopy(case['input']); data['rules'] = [r for r in data['rules'] if r.startswith('TS01-')]
                if data['rules']: rows.append({'id': case['id'], 'input': case['input'], 'results': evaluate(data)})
        encoded = json.dumps(rows, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()
        self.assertEqual(len(rows), baseline['selected_cases'])
        self.assertEqual(sum(len(r['results']) for r in rows), 174)
        self.assertEqual(hashlib.sha256(encoded).hexdigest(), baseline['sha256'])

    def test_frozen_cases_are_distributed_unchanged_in_conformance(self):
        expected = fixture()['cases']
        cases = json.loads((ROOT/'conformance/cases.json').read_text())['cases']
        self.assertEqual(cases[1181:1257], expected)
        self.assertEqual(len(expected), 76)
        self.assertEqual(len(frozen('identity-markers-bundles-v1.json')['cases']), 8)

    def test_all_retained_structural_observations_reach_expected_atomic_outcomes(self):
        for id in self.inventories:
            case = self.cases['identity-markers-'+id]
            observed = self.observe_retained(id)
            with self.subTest(id=id), patch.object(policy.reader, 'observe', return_value=observed):
                notes = []; result = evaluate(case['input'], source_observations=notes)
                self.assertEqual(result[0]['outcome'], case['expected'][0]['outcome'])
                self.assertEqual(notes[0]['observations'][0]['outcome'], result[0]['outcome'])

    def test_context_interning_is_lossless_for_every_admitted_and_excluded_record(self):
        for id in self.inventories:
            original = self.observe_retained(id); before = copy.deepcopy(original)
            packed = policy.compact(original)
            self.assertEqual(original, before)
            for mode in observer.MODES:
                row = packed['hypotheses'][mode]
                for kind in ('segments', 'excluded'):
                    restored = None if row[kind] is None else [dict({k:v for k,v in r.items() if k!='context_id'},
                        ancestors=row['contexts'][r['context_id']]) for r in row[kind]]
                    self.assertEqual(restored, original['readings'][mode][kind], (id,mode,kind))
                self.assertEqual(row['tree']['parse_errors'], original['inventory']['readings'][mode]['parse_errors'])

    def test_precedence_and_chronology_never_invoke_projection(self):
        ids = ('wrong-url-before-missing-hash','missing-hash-before-marker','invalid-hash-before-marker',
               'equal-hash-before-unknown-profile','equal-hash-before-projection','stable-before-marker',
               'missing-hash-before-stability','unsupported-representation','incomplete-http','late-intent')
        with patch.object(policy.reader, 'observe', side_effect=AssertionError('precedence bypassed')):
            for id in ids:
                case = self.cases['identity-markers-'+id]; notes=[]
                self.assertEqual(evaluate(case['input'],source_observations=notes)[0]['outcome'],case['expected'][0]['outcome'])
                self.assertEqual(notes,[])

    def test_context_ids_are_local_to_each_hypothesis_and_keep_records_distinct(self):
        observed = self.observe_retained('ordinary')
        for mode in observer.MODES:
            original = observed['readings'][mode]['segments'][0]
            rows = [copy.deepcopy(original) for _ in range(4)]
            for i, row in enumerate(rows): row['node_id'] = 100 + i
            rows[2]['ancestors'][-1]['name'] = 'div'
            rows[3]['ancestors'][-1]['namespace'] = 'urn:authored-context-difference'
            observed['readings'][mode]['segments'] = rows
        packed = policy.compact(observed)
        policy.verify_projection(observed, packed)
        for mode in observer.MODES:
            rows = packed['hypotheses'][mode]['segments']
            self.assertEqual([r['context_id'] for r in rows], [0, 0, 1, 2])
            self.assertEqual([r['node_id'] for r in rows], [100, 101, 102, 103])
        self.assertEqual(packed, policy.compact(observed))

    def test_compaction_corruption_cannot_produce_conclusive_result(self):
        observed = self.observe_retained('ordinary')
        mutations = ('data', 'context', 'count', 'outcome', 'tree')
        for mutation in mutations:
            packed = policy.compact(observed)
            row = packed['hypotheses']['enabled']
            if mutation == 'data': row['segments'][0]['data'] = 'silently changed'
            elif mutation == 'context': row['segments'][0]['context_id'] = len(row['contexts'])
            elif mutation == 'count': row['segments'].pop()
            elif mutation == 'outcome': row['outcome'] = 'fail'
            else: row['tree']['parse_errors'] = [{'code': 'invented-error'}]
            with self.subTest(mutation=mutation), patch.object(policy.reader, 'observe', return_value=observed), \
                    patch.object(policy, 'compact', return_value=packed):
                notes = []
                result = evaluate(self.cases['identity-markers-ordinary']['input'], source_observations=notes)
                self.assertEqual(result[0]['outcome'], 'inconclusive')
                self.assertNotIn('hypotheses', notes[0]['observations'][0])

    def test_absent_runtime_and_unknown_profiles_never_fall_back(self):
        for id in ('noscript-image','unknown-profile','null-profile'):
            with self.subTest(id=id), patch.dict(os.environ, {'TSEP_SOURCE_NODE':'/missing/node'}):
                notes=[]; result=evaluate(self.cases['identity-markers-'+id]['input'],source_observations=notes)
            self.assertEqual(result[0]['outcome'],'inconclusive');self.assertEqual(len(notes),1)
            self.assertEqual(notes[0]['observations'][0]['outcome'],'inconclusive')

    def test_media_profile_stays_explicit_before_runtime(self):
        for id in ('plain-under-new-profile','missing-explicit-charset','unsupported-charset'):
            with patch.dict(os.environ,{'TSEP_SOURCE_NODE':'/missing/node'}):
                result=evaluate(self.cases['identity-markers-'+id]['input'])
            self.assertEqual(result[0]['outcome'],'inconclusive')
            self.assertIn('Content-Type',result[0]['reason'])

    def test_invalid_marker_bounds_never_invoke_parser(self):
        with patch.object(policy.reader,'observe',side_effect=AssertionError('invalid criteria')):
            for id in ('excessive-marker-count','excessive-marker-size','contradictory-criteria','missing-all-markers'):
                self.assertEqual(evaluate(self.cases['identity-markers-'+id]['input'])[0]['outcome'],'inconclusive')

    def test_excessive_markers_are_refused_before_cross_product_comparison(self):
        class ComparisonMustNotRun(str):
            def __contains__(self, other):
                raise AssertionError('Marker comparison ran before the profile bound')
        data = copy.deepcopy(self.cases['identity-markers-ordinary']['input'])
        data['targets'][0]['intent']['required_markers'] = [
            ComparisonMustNotRun('Required '+str(i)) for i in range(65)]
        data['targets'][0]['intent']['forbidden_markers'] = ['Forbidden']
        with patch.object(policy.reader, 'observe', side_effect=AssertionError('Parser must not run')):
            result = evaluate(data)
        self.assertEqual(result[0]['outcome'], 'inconclusive')
        self.assertIn('excessive marker list', result[0]['reason'])

    def test_final_diagnostic_budget_keeps_no_partial_success(self):
        observed=self.observe_retained('ordinary')
        observed['readings']['enabled']['reason']='x'*4000
        with patch.object(policy.reader,'observe',return_value=observed),patch.object(policy,'MAX_DIAGNOSTIC_BYTES',1800):
            notes=[];result=evaluate(self.cases['identity-markers-ordinary']['input'],source_observations=notes)
        self.assertEqual(result[0]['outcome'],'inconclusive');record=notes[0]['observations'][0]
        self.assertNotIn('hypotheses',record);self.assertNotIn('parser',record)
        self.assertLessEqual(len(json.dumps(record,ensure_ascii=False,indent=2).encode()),1800)

    def test_missing_runtime_bundle_replays_and_coherent_tampering_is_rejected(self):
        from adapters.package import seal
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'TSEP_SOURCE_NODE':'/missing/node'}):
            folder=Path(tmp);source=folder/'input.json';source.write_text(json.dumps(self.cases['identity-markers-noscript-image']['input']))
            captures.build(source,folder/'bundle',assessor='Synthetic fixture',label='Synthetic refusal',selection_method='Authored case',access='synthetic')
            result=replay.replay(folder/'bundle',folder/'replay');self.assertTrue(result['same_source_observations'])
            path=folder/'bundle/observations/source-observation-1.json';v=json.loads(path.read_text());v['observations'][0]['reason']='changed'
            path.write_text(json.dumps(v));report_path=folder/'bundle/report.json';report=json.loads(report_path.read_text())
            for a in report['artifacts']:
                if a['path']=='observations/source-observation-1.json':a['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
            report_path.write_text(json.dumps(report));seal(folder/'bundle')
            with self.assertRaisesRegex(ValueError,'Replay differs'):replay.replay(folder/'bundle',folder/'tampered')

    def test_adapter_binds_both_normative_and_observation_sources(self):
        sources=captures.source_files()
        for name in ('conformance/source_markers.py','experiments/source_markers.py'):
            self.assertEqual(sources[name],hashlib.sha256((ROOT/name).read_bytes()).hexdigest())

    def test_report_names_supplied_profile_without_claiming_browser_observation(self):
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'TSEP_SOURCE_NODE':'/missing/node'}):
            folder=Path(tmp);source=folder/'input.json';source.write_text(json.dumps(self.cases['identity-markers-noscript-image']['input']))
            captures.build(source,folder/'bundle',assessor='Synthetic fixture',label='Synthetic report',selection_method='Authored case',access='synthetic')
            for language,phrase in [('fr','Lecteur de marqueurs déclaré'),('en','Declared marker reader')]:
                text=html.render(folder/'bundle/report.json',language=language)
                self.assertIn(phrase,text);self.assertIn(policy.READER,text)


if __name__ == '__main__': unittest.main()
