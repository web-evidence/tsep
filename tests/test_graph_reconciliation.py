"""TS18 prefrozen outcomes, independent dossiers, original integrity and replay."""
import copy
import base64
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
from conformance import graph_reconciliation as native
from adapters import captures
from adapters.graph_intake import verify_target
from reports import html
from adapters import replay

ROOT=Path(__file__).resolve().parents[1]
SHA='e6d907a55a94e5afa6dd25e64613d379728520bd72e232cfea1cbbc3415dea96'

def cases():
 raw=(ROOT/'tests/fixtures/graph-reconciliation-cases-v1.json').read_bytes()
 if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('Changed authored TS18 fixture')
 return json.loads(raw)['cases']

def data(id='complete_documented_chain'):
 return copy.deepcopy(next(c['input'] for c in cases() if c['id']==id))

def build(root,d,access='synthetic',name='bundle'):
 raw=(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode();(root/'input.json').write_bytes(raw)
 captures.build(root/'input.json',root/name,assessor='Authored synthetic exercise; no human approval',label='Synthetic TS18',selection_method='Prior authored bounded graph population',access=access)
 return raw

class GraphReconciliation(unittest.TestCase):
 def test_frozen_native_outcomes_with_no_acquisition(self):
  self.assertEqual(len(cases()),34);count=0
  for c in cases():
   if c['expected_atomic']=='technical-refusal':continue
   with self.subTest(case=c['id']),patch.object(socket,'socket',side_effect=AssertionError('Offline only')):
    before=copy.deepcopy(c['input']);rows=evaluate(c['input'])
    self.assertEqual([r['outcome'] for r in rows],c['expected_atomic']);self.assertEqual(before,c['input']);count+=1
    if 'expected_dates' in c:
     layer=json.loads(rows[0]['reason'][len(native.PREFIX):])['measurement']
     for role in ('crawl','cms','sitemap'):self.assertEqual(layer['inventories'][role]['observed_at'],c['input']['targets'][0]['graph_inventories'][role]['observed_at'])
    if 'expected_node' in c:
     e=c['expected_node'];layer=json.loads(rows[1]['reason'][len(native.PREFIX):])['measurement']['measurement']['graph'];node=next(n for n in layer['nodes'] if n['node']==e['url'])
     for k in ('incoming_lower','incoming_upper','bounded_orphan_candidate'):self.assertEqual(node[k],e[k])
  self.assertEqual(count,32)

 def test_intake_corrupt_originals_refuse_before_output(self):
  samples=[c['input'] for c in cases() if c['expected_atomic']=='technical-refusal']
  for field in ('request','response'):
   d=data();record=d['targets'][0]['graph_documents'][0]['http'][0][field]
   raw=record.encode('utf-8') if isinstance(record,str) else base64.b64decode(record['base64'])
   d['targets'][0]['graph_documents'][0]['http'][0][field]={'base64':base64.b64encode(raw).decode(),'sha256':'0'*64};samples.append(d)
  d=data();d['targets'][0]['graph_documents'][0]['render']['states'][0]['structured_dom']['snapshot_sha256']='0'*64;samples.append(d)
  for d in samples:
   with self.subTest(),tempfile.TemporaryDirectory() as folder:
    root=Path(folder)
    with self.assertRaises(tsep.Invalid):build(root,d)
    self.assertFalse((root/'bundle').exists());self.assertEqual(tsep.read_json(root/'input.json'),d)

 def test_bundles_exact_originals_html_and_offline_replay(self):
  for id,status in [('complete_documented_chain','C'),('cms_difference_known_defect','NC'),('no_reviews','NT')]:
   with self.subTest(case=id),tempfile.TemporaryDirectory() as folder,patch.object(socket,'socket',side_effect=AssertionError('No acquisition')):
    root=Path(folder);d=data(id);raw=build(root,d);report=tsep.read_json(root/'bundle/report.json')
    self.assertEqual(report['results'][0]['status'],status);self.assertEqual((root/'bundle/input.json').read_bytes(),raw)
    summary=tsep.decision(report);self.assertTrue(summary['synthetic_evidence']);self.assertIn('graph_interpretation',summary)
    result=replay.replay(root/'bundle',root/'replay');self.assertTrue(result['same_atomic_results']);self.assertTrue(result['same_gate'])
    for language in ('fr','en'):
     text=html.render(root/'bundle/report.json',language=language)
     self.assertIn(html.TEXT[language]['graph_note'],text);self.assertIn(html.TEXT[language]['graph_title'],text);self.assertIn('2026-10-14T08:09:00Z',text)

 def test_nested_originals_coexist_without_overwriting_other_evidence(self):
  d=data();t=d['targets'][0];doc=t['graph_documents'][0]
  t['http']=copy.deepcopy(doc['http']);t['render']=copy.deepcopy(doc['render']);t['crawl']={'retained':'unrelated original crawl'};t['sitemaps']={'retained':'unrelated sitemap original'}
  p=captures.pieces(t)
  self.assertEqual(p['http']['graph_documents'],t['graph_documents']);self.assertEqual(p['http']['other_supplied_evidence']['http'],t['http'])
  self.assertEqual(p['inventory']['graph_inventories'],t['graph_inventories']);self.assertEqual(p['crawl']['other_supplied_evidence'],t['crawl']);self.assertEqual(p['sitemap']['other_supplied_evidence'],t['sitemaps'])
  self.assertEqual(p['intent']['graph_reviews'],t['graph_reviews']);self.assertEqual(p['intent']['other_supplied_evidence']['intent'],t['intent'])
  self.assertIn('other_supplied_evidence',p['render'])

 def test_partial_measurement_never_completes_control_or_fabricates_reviews(self):
  d=data('no_reviews');d['rules']=['TS18-A01','TS18-A02']
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);build(root,d);r=tsep.read_json(root/'bundle/report.json');self.assertEqual(r['results'][0]['status'],'NT')
   self.assertEqual(tsep.read_json(root/'bundle/input.json')['targets'][0]['graph_reviews'],[])
  d=data('cms_difference_known_defect');d['rules']=['TS18-A03']
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);build(root,d);self.assertEqual(tsep.read_json(root/'bundle/report.json')['results'][0]['status'],'NC')

 def test_provenance_runtime_missing_and_existing_output(self):
  for flag,access in [(True,'public'),(False,'synthetic'),('true','synthetic')]:
   for prior in (True,False):
    d=data();d['targets'][0]['graph_synthetic']=flag
    if not prior:d['targets'][0].pop('intent')
    with tempfile.TemporaryDirectory() as folder:
     root=Path(folder)
     with self.assertRaises(tsep.Invalid):build(root,d,access)
     self.assertFalse((root/'bundle').exists())
  with patch.dict(os.environ,{},clear=True):self.assertEqual([r['outcome'] for r in evaluate(data())],['inconclusive']*3)
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);(root/'bundle').mkdir();(root/'bundle/keep').write_bytes(b'original')
   with self.assertRaises(tsep.Invalid):build(root,data())
   self.assertEqual((root/'bundle/keep').read_bytes(),b'original')

 def test_separate_dossiers_do_not_share_review_results(self):
  good=data();bad=data('cms_difference_known_defect');bad['targets'][0]['url']='https://example.test/reconciliation-second'
  both={**good,'targets':good['targets']+bad['targets']}
  results=evaluate(both);self.assertEqual([r['outcome'] for r in results],['pass']*3+['pass','pass','fail'])

 def test_html_escapes_supplied_subjects_without_evaluation(self):
  note={'kind':native.PROFILE,'rule':'TS18-A03','measurement':{'subjects':[{'subject':'<img src=x onerror=alert(1)>','reviewer':'<script>bad</script>','rationale':'<svg onload=bad>','outcome':'fail'}]}}
  for language in ('fr','en'):
   with patch.object(native,'assess_target',side_effect=AssertionError('HTML never evaluates')):text=html.graph_values({'reason':native.PREFIX+json.dumps(note)},html.TEXT[language])
   self.assertNotIn('<img ',text);self.assertNotIn('<script>',text);self.assertNotIn('<svg ',text);self.assertIn('&lt;img ',text)

 def test_oversized_diagnostic_does_not_preserve_success(self):
  huge={'kind':native.PROFILE,'layers':{r:{'outcome':'pass'} for r in native.RULES},'diagnostic':'x'*(4*1024*1024)}
  for rule in native.RULES:self.assertEqual(native.assess({},rule,assessment=huge)[0],'inconclusive')

 def test_reader_sources_and_corpus_are_bound(self):
  files=captures.source_files()
  for module in ('graph_bounds','graph_documents','graph_inventories','graph_reviews','graph_reconciliation'):self.assertIn('conformance/'+module+'.py',files)
  self.assertIn('adapters/graph_intake.py',files)
  from conformance.corpus import expand
  rows=[c for c in expand(tsep.read_json(ROOT/'conformance/cases.json'))['cases'] if c['id'].startswith('graph-reconciliation-v1-')]
  originals=[c for c in cases() if c['expected_atomic']!='technical-refusal'];self.assertEqual(len(rows),len(originals))
  for row,c in zip(rows,originals):self.assertEqual(row['input'],c['input']);self.assertEqual([e['outcome'] for e in row['expected']],c['expected_atomic'])

if __name__=='__main__':unittest.main()
