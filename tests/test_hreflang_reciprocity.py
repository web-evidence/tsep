"""TS23 adapter integrity, coexistence, genuine originals, HTML and exact replay."""
import copy
import hashlib
import json
import os
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch
import tsep
from conformance.evaluate import evaluate
from conformance import hreflang_reciprocity as native
from adapters import captures,replay
from reports import html

ROOT=Path(__file__).resolve().parents[1]

def cases(name='cases'):
 path=ROOT/'tests/fixtures'/('hreflang-reciprocity-'+name+'-v1.json')
 raw=path.read_bytes();expected=path.with_suffix('.sha256').read_text().strip()
 if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('Changed authored TS23 fixture')
 return json.loads(raw)['cases']

def data(name='complete-native-http'):
 return copy.deepcopy(next(c['input'] for c in cases() if c['id']==name))

def build(root,d,access='synthetic'):
 raw=(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode();(root/'input.json').write_bytes(raw)
 captures.build(root/'input.json',root/'bundle',assessor='Authored synthetic exercise',label='Synthetic TS23',selection_method='Prior authored bounded language group',access=access)
 return raw

class HreflangReciprocity(unittest.TestCase):
 def test_transport_and_integration_expectations(self):
  count=0
  for group in ('cases','integration','review','containers'):
   for c in cases(group):
    count+=1
    with self.subTest(case=c['id']),patch.object(socket,'socket',side_effect=AssertionError('No acquisition')):
     before=copy.deepcopy(c['input'])
     if c['expected']=='technical-refusal':
      with self.assertRaises(tsep.Invalid):evaluate(c['input'])
     else:self.assertEqual(evaluate(c['input'])[0]['outcome'],{'C':'pass','NC':'fail','NT':'inconclusive'}[c['expected']])
     self.assertEqual(before,c['input'])
  self.assertEqual(count,82)

 def test_corruption_refused_before_output_preserving_original_input(self):
  for c in cases()+cases('integration')+cases('review')+cases('containers'):
   if c['expected']!='technical-refusal':continue
   with self.subTest(case=c['id']),tempfile.TemporaryDirectory() as folder:
    root=Path(folder)
    with self.assertRaises(tsep.Invalid):build(root,c['input'])
    self.assertFalse((root/'bundle').exists());self.assertEqual(tsep.read_json(root/'input.json'),c['input'])

 def test_bundles_exact_originals_bilingual_html_and_offline_replay(self):
  for name,status in [('complete-native-http','C'),('native-known-missing-return','NC'),('missing-plan','NT'),('binary-pdf-http-primary','C')]:
   with self.subTest(case=name),tempfile.TemporaryDirectory() as folder,patch.object(socket,'socket',side_effect=AssertionError('No acquisition')):
    root=Path(folder);d=data(name);d['targets'][0]['hreflang']={'legacy':'Uninterpreted supplied annotation retained only as original input'};raw=build(root,d);r=tsep.read_json(root/'bundle/report.json')
    self.assertEqual(r['results'][0]['status'],status);self.assertEqual((root/'bundle/input.json').read_bytes(),raw)
    self.assertTrue(tsep.decision(r)['synthetic_evidence']);self.assertIn('hreflang_interpretation',tsep.decision(r))
    result=replay.replay(root/'bundle',root/'replay');self.assertTrue(result['same_atomic_results']);self.assertTrue(result['same_gate'])
    for lang in ('fr','en'):
     rendered=html.render(root/'bundle/report.json',language=lang);self.assertIn(html.TEXT[lang]['hreflang_title'],rendered);self.assertIn(html.TEXT[lang]['hreflang_note'],rendered)

 def test_nested_evidence_kept_alongside_legacy_originals(self):
  d=data();t=d['targets'][0];t['http']=copy.deepcopy(t['hreflang_documents'][0]['http']);t['hreflang']={'legacy':'supplied annotation evidence'}
  p=captures.pieces(t)
  self.assertEqual(p['http']['hreflang_documents'],t['hreflang_documents']);self.assertEqual(p['http']['other_supplied_evidence']['http'],t['http'])
  text=json.dumps(p['hreflang']);self.assertIn('native_hreflang_sources',text);self.assertIn('unsupported_supplied_channels',text)

 def test_provenance_missing_plan_runtime_and_existing_output(self):
  for flag,access in [(True,'public'),(False,'synthetic'),('yes','synthetic')]:
   for planned in (True,False):
    d=data();d['targets'][0]['hreflang_synthetic']=flag
    if not planned:d['targets'][0].pop('intent')
    with tempfile.TemporaryDirectory() as folder:
     root=Path(folder)
     with self.assertRaises(tsep.Invalid):build(root,d,access)
     self.assertFalse((root/'bundle').exists())
  with patch.dict(os.environ,{},clear=True):self.assertEqual(evaluate(data())[0]['outcome'],'inconclusive')
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);(root/'bundle').mkdir();(root/'bundle/original').write_bytes(b'keep')
   with self.assertRaises(tsep.Invalid):build(root,data())
   self.assertEqual((root/'bundle/original').read_bytes(),b'keep')

 def test_multiple_dossiers_do_not_share_outcomes(self):
  d=data();other=data('native-known-missing-return')['targets'][0];other['url']='https://example.test/another-dossier';d['targets'].append(other)
  self.assertEqual([r['outcome'] for r in evaluate(d)],['pass','fail'])

 def test_oversized_diagnostic_cannot_preserve_pass(self):
  with patch.object(native,'qualify',return_value={'outcome':'C','diagnostic':'x'*(4*1024*1024)}):self.assertEqual(native.assess({},'TS23-A01')[0],'inconclusive')

 def test_renderer_escapes_native_text_without_recalculation(self):
  note={'measurement':{'pages':[{'url':'<img src=x onerror=bad>','primary':'html','outcome':'NT','reason':'<script>bad</script>','channels':{}}]}}
  for lang in ('fr','en'):
   with patch.object(native,'qualify',side_effect=AssertionError('No reevaluation')):text=html.hreflang_values({'reason':native.PREFIX+json.dumps(note)},html.TEXT[lang])
   self.assertNotIn('<img ',text);self.assertNotIn('<script>',text);self.assertIn('&lt;img ',text)

 def test_complete_secondary_is_explicitly_a_plan_mode_mismatch(self):
  from conformance import hreflang_native
  fixture=json.loads((ROOT/'tests/fixtures/hreflang-native-v1.json').read_text())['cases']
  case=next(c for c in fixture if c['id']=='empty-primary-complete-secondary')
  result=hreflang_native.assess(case['input']);self.assertEqual(result['outcome'],'NC')
  for lang in ('fr','en'):
   text=html.hreflang_values({'reason':native.PREFIX+json.dumps({'measurement':result})},html.TEXT[lang])
   self.assertIn(html.TEXT[lang]['hreflang_mode_http'],text)
  case=next(c for c in fixture if c['id']=='relative-href')
  self.assertIn('relative URL outside profile',json.dumps(hreflang_native.assess(case['input'])))

 def test_fingerprints_and_corpus_preserve_authored_expectations(self):
  for n in ('conformance/hreflang_native.py','conformance/hreflang_reciprocity.py','adapters/hreflang_intake.py'):self.assertIn(n,captures.source_files())
  from conformance.corpus import expand
  corpus=[c for c in expand(tsep.read_json(ROOT/'conformance/cases.json'))['cases'] if c['id'].startswith('hreflang-reciprocity-v1-')]
  rows=[c for c in cases() if c['expected']!='technical-refusal'];self.assertEqual(len(rows),32);self.assertEqual(len(corpus),32)
  for row,c in zip(corpus,rows):self.assertEqual(row['input'],c['input']);self.assertEqual(row['expected'][0]['outcome'],{'C':'pass','NC':'fail','NT':'inconclusive'}[c['expected']])

if __name__=='__main__':unittest.main()
