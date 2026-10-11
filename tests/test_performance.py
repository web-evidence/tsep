"""Field/lab distinction, frozen contrary cases and offline evidence delivery."""
import copy
import hashlib
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch
from adapters import captures, replay
from conformance.evaluate import evaluate
from conformance import performance
from reports import html
import tsep

ROOT=Path(__file__).resolve().parents[1]
def fixture(version='v2'):
 p=ROOT/('tests/fixtures/performance-'+version+'.json');raw=p.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=p.with_suffix('.sha256').read_text().strip():raise ValueError('Frozen performance fixture changed')
 return json.loads(raw)['cases']

class Performance(unittest.TestCase):
 def data(self,name):return copy.deepcopy(next(c['input'] for c in fixture() if c['id']=='performance-'+name))
 def test_frozen_cases_and_exact_corpus(self):
  cases=fixture();self.assertEqual(len(cases),82);self.assertEqual(sum(len(c['expected']) for c in cases),216)
  corpus=tsep.read_json(ROOT/'conformance/cases.json')['cases']
  for case in cases:
   with self.subTest(case=case['id']):
    self.assertIn(case,corpus)
    self.assertEqual([{k:a[k] for k in ('rule_id','target','outcome')} for a in evaluate(case['input'])],case['expected'])
 def test_first_freeze_preserved_and_expectations_unchanged(self):
  old=fixture('v1');new=fixture();self.assertEqual(len(old),66)
  for a,b in zip(old,new):
   self.assertEqual(a['id'],b['id']);self.assertEqual(a['expected'],b['expected'])
   if a['input']['rules'][0].startswith('TS34'):self.assertEqual(a,b)
 def test_poor_quality_can_have_conforming_documentation(self):
  notes=[];target=self.data('field-poor-correctly-documented')['targets'][0]
  self.assertEqual(performance.assess(target,'TS34-A02',diagnostics=notes)[0],'pass')
  self.assertEqual(notes[0]['field_quality'],'poor');self.assertEqual(notes[0]['metrics']['LCP']['p75'],'4200')
  self.assertEqual(notes[0]['metrics']['CLS']['classification'],'poor')
 def test_missing_inp_retains_other_metrics(self):
  notes=[];target=self.data('field-no-inp')['targets'][0];performance.assess(target,'TS34-A02',diagnostics=notes)
  self.assertEqual(notes[0]['field_quality'],'unknown');self.assertEqual(notes[0]['metrics']['LCP']['p75'],'2500')
  self.assertEqual(notes[0]['metrics']['INP']['classification'],'unknown')
 def test_invalid_records_never_crash_or_pass(self):
  for kind,rid in [('field','TS34-A02'),('lab','TS35-A01')]:
   for malformed in (None,[],False,'invalid',{'reader':None}):
    t=self.data('field-good-boundaries' if kind=='field' else 'lab-context-and-supplied-review')['targets'][0];t[kind]=malformed
    self.assertEqual(performance.assess(t,rid)[0],'inconclusive')
 def test_bound_field_conflict_survives_missing_metric(self):
  self.assertEqual([r['outcome'] for r in evaluate(self.data('field-conflict-survives-missing-inp'))],['pass','fail','fail'])
 def test_field_window_cannot_postdate_its_acquisition(self):
  data=self.data('field-good-boundaries');data['targets'][0]['field']['observed_at']='2026-10-06T12:00:00Z'
  self.assertEqual([r['outcome'] for r in evaluate(data)],['inconclusive']*3)
 def test_bound_lab_substitution_survives_unrelated_context_unknown(self):
  data=self.data('lab-cache-change');data['targets'][0]['lab_review']['claims_field_cwv']=True
  self.assertEqual([r['outcome'] for r in evaluate(data)],['inconclusive','fail'])
  data['targets'][0]['lab_review']['source_sha256']=['0'*64]*3
  self.assertEqual([r['outcome'] for r in evaluate(data)],['inconclusive','inconclusive'])
 def test_deep_embedded_json_is_unknown_not_an_uncaught_error(self):
  data=self.data('field-good-boundaries');e=data['targets'][0]['field']
  e['raw_json']='['*1200+'0'+']'*1200;e['sha256']=hashlib.sha256(e['raw_json'].encode()).hexdigest()
  self.assertEqual([r['outcome'] for r in evaluate(data)],['inconclusive']*3)
 def test_field_age_uses_declared_utc_calendar_date(self):
  data=self.data('field-good-boundaries');t=data['targets'][0]
  t['observed_at']='2026-10-10T00:30:00+02:00';t['intent']['declared_at']='2026-10-09T19:00:00Z'
  t['field']['observed_at']='2026-10-09T20:00:00Z';t['field_review']['observed_at']='2026-10-09T20:00:00Z'
  t['intent']['performance']['field']['max_age_days']=2
  self.assertEqual([r['outcome'] for r in evaluate(data)],['pass']*3)
 def test_equivalent_fetch_instants_do_not_establish_distinct_runs(self):
  data=self.data('lab-context-and-supplied-review');t=data['targets'][0];e=t['lab']['runs'][1]
  raw=json.loads(e['raw_json']);raw['fetchTime']='2026-10-10T13:30:00+02:00';e['raw_json']=json.dumps(raw);e['sha256']=hashlib.sha256(e['raw_json'].encode()).hexdigest();t['lab_review']['source_sha256'][1]=e['sha256']
  self.assertEqual([r['outcome'] for r in evaluate(data)],['inconclusive']*2)
 def test_report_gate_earl_html_and_replay_retain_poor_quality(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);src=root/'input.json';src.write_text(json.dumps(self.data('field-poor-correctly-documented')))
   with patch.object(socket,'socket',side_effect=AssertionError('Network forbidden')):
    captures.build(src,root/'bundle',assessor='Synthetic reviewer',label='Synthetic poor field data',selection_method='Authored case only',access='synthetic')
    replayed=replay.replay(root/'bundle',root/'replayed')
   self.assertTrue(replayed['replayed']);self.assertTrue(replayed['same_source_observations'])
   report=tsep.read_json(root/'bundle/report.json');self.assertEqual(report['results'][0]['status'],'C')
   for name in ('gate.json','earl.jsonld'):
    text=(root/'bundle'/name).read_text();self.assertIn('4200',text);self.assertIn('poor',text);self.assertIn('not good performance',text)
   for language,label in [('fr','Mauvais'),('en','Poor')]:
    rendered=html.render(root/'bundle/report.json',language=language)
    self.assertIn('4200 ms · p75',rendered);self.assertIn(label,rendered);self.assertIn(html.TEXT[language]['performance_note'],rendered)
    self.assertNotIn('<script',rendered)
 def test_missing_review_stays_nt_and_no_review_is_generated(self):
  for name in ('field-no-review','lab-no-review'):
   with tempfile.TemporaryDirectory() as directory:
    root=Path(directory);src=root/'input.json';data=self.data(name);src.write_text(json.dumps(data))
    captures.build(src,root/'bundle',assessor='Synthetic importer',label='No supplied review',selection_method='Authored case only',access='synthetic')
    report=tsep.read_json(root/'bundle/report.json');self.assertEqual(report['results'][0]['status'],'NT')
    self.assertEqual(tsep.read_json(root/'bundle/input.json'),data)
 def test_synthetic_review_cannot_be_imported_as_real(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);src=root/'input.json';src.write_text(json.dumps(self.data('field-good-boundaries')))
   with self.assertRaises(tsep.Invalid):captures.build(src,root/'bundle',assessor='Supplied author',label='Review provenance',selection_method='One case',access='public')
 def test_html_diagnostics_are_escaped_without_reassessment(self):
  result={'atomic_results':[{'target':'<target>','reason':'Performance documentation / documentation de performance: '+json.dumps({'metrics':{'<script>':{'p75':'<bad>','unit':'ms','classification':'poor'}}})}]}
  rendered=html.performance_values(result,html.TEXT['fr']);self.assertIn('&lt;script&gt;',rendered);self.assertNotIn('<script>',rendered)

if __name__=='__main__':unittest.main()
