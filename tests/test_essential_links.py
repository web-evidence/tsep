"""Prefrozen TS17 boundaries, exact originals, refusals and autonomous replay."""
import base64,copy,hashlib,json,os,socket,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import tsep
from adapters import captures,replay
from conformance import essential_links as native,essential_links_source as source,essential_links_dom as dom
from conformance.evaluate import evaluate
from conformance.corpus import expand
from reports import html
ROOT=Path(__file__).resolve().parents[1]
SHAS={'hop-boundary-v2':'44e972666676918d48dce7f02cf4f37ce1cf05d4a6d1982d52a3cfd0acf59188','hop-boundary-v1':'9ac4d2b673c08c6d81a07d45457a7f1395753e95535e86fb7acf83e08fe38eb8','source-v1':'89d049012d666e1f170bb2931903bf8e1f25dcf66f34b7cfb33202c135701246','dom-v2':'c27114b2d8fff2224dc551ba21ba722eee9d0c526f98a0751f2252bd67af220c','recipes-v1':'20f5d1fa08958096dd4716d01a46b988b9cd12cbdc5184455e16f0433b3744d4','malformed-v1':'1463e74c1c21aa1d706c2eb7278b9731de463becc2318f2d0c1a8a1825d66812','state-identity-v1':'ee2b3d5ea5ab178ce7479f15203d7f0090d415cb76bc7a256c3a2cbd635313aa'}
def fixture(name):
 p=ROOT/'tests/fixtures'/('essential-links-'+name);raw=p.with_suffix('.json').read_bytes();expected=SHAS.get(name) or p.with_suffix('.sha256').read_text().strip()
 if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('Changed prefrozen expectations')
 return json.loads(raw)['cases']
def data(name='complete'):return copy.deepcopy(next(c['input'] for c in fixture('v1') if c['id']=='essential-links-v1-'+name))
def build(p,d,access='synthetic',dest='bundle'):
 (p/'input.json').write_text(json.dumps(d,ensure_ascii=False,indent=1)+'\n');return captures.build(p/'input.json',p/dest,assessor='Fictional reviewer',label='Synthetic TS17',selection_method='Authored essential destinations',access=access)
class EssentialLinks(unittest.TestCase):
 def test_prefrozen_source_and_dom_cases(self):
  for name,reader,count in [('source-v1',source,52),('dom-v2',dom,37)]:
   rows=fixture(name);self.assertEqual(len(rows),count)
   with patch.object(socket,'socket',side_effect=AssertionError('Offline source/DOM only')):
    for c in rows:
     before=copy.deepcopy(c)
     with self.subTest(case=c['id'],reader=name):
      r=reader.assess(c if name=='source-v1' else c['input']);self.assertEqual(r['outcome'],c['expected']);self.assertEqual(c,before);self.assertFalse(r['authenticates_evidence'])
      if c['id']=='base-element':self.assertIn('base outside',r['reason'])
 def test_frozen_control_and_identity_recipes(self):
  original=fixture('recipes-v1')+fixture('state-identity-v1');rows=fixture('v1');self.assertEqual(len(rows),34);self.assertEqual(expand(tsep.read_json(ROOT/'conformance/cases.json'))['cases'][1639:1673],rows)
  with patch.object(socket,'socket',side_effect=AssertionError('No network')):
   for a,c in zip(original,rows):
    before=copy.deepcopy(c)
    with self.subTest(case=c['id']):self.assertEqual([v['outcome'] for v in c['expected']],a['expected']);self.assertEqual(c['input']['targets'][0],a['input']);self.assertEqual([r['outcome'] for r in evaluate(c['input'])],a['expected']);self.assertEqual(c,before)
 def test_malformed_inputs_do_not_crash_or_pass(self):
  rows=fixture('malformed-v1');self.assertEqual(len(rows),36)
  for c in rows:
   with self.subTest(case=c['id']):
    before=copy.deepcopy(c);r=native.assess_target(c['input']);self.assertEqual([r[k]['outcome'] for k in ('source','rendered')],c['expected']);self.assertEqual(c,before)
 def test_malformed_http_structure_intake_and_partial_replay(self):
  rows=fixture('hop-boundary-v2');self.assertEqual(len(rows),12)
  for c in rows:
   with self.subTest(case=c['id']),tempfile.TemporaryDirectory() as folder:
    d=copy.deepcopy(c['input']);r=native.assess_target(d['targets'][0]);self.assertEqual([r[k]['outcome'] for k in ('source','rendered')],c['expected'])
    p=Path(folder)
    if c['expected_import']=='technical-refusal':
     with self.assertRaisesRegex(tsep.Invalid,'TS17 HTTP structure:'):build(p,d,dest='refused')
     self.assertFalse((p/'refused').exists());self.assertEqual(json.loads((p/'input.json').read_text()),d)
    else:
     build(p,d);self.assertEqual((p/'bundle/input.json').read_bytes(),(p/'input.json').read_bytes());self.assertEqual(tsep.read_json(p/'bundle/report.json')['results'][0]['status'],c['expected_import'])
     with patch.object(socket,'socket',side_effect=AssertionError('Offline partial evidence replay')):result=replay.replay(p/'bundle',p/'replayed')
     self.assertTrue(result['same_atomic_results']);self.assertTrue(result['same_gate'])
    self.assertEqual(d,c['input'])
 def test_declared_identity_and_repeated_snapshots(self):
  for c in fixture('state-identity-v1'):
   with self.subTest(case=c['id']):
    r=native.assess_target(c['input']);self.assertEqual(r['state_identity'],'provider-declared-not-observed-interactions');self.assertEqual(r['http_dom_binding'],'supplied-association-not-authenticated-acquisition');self.assertGreaterEqual(max((len(x['state_ids']) for x in r['repeated_snapshots']),default=0),c['duplicate_group_minimum'])
 def test_actual_adapter_c_nc_nt_and_exact_offline_replay(self):
  for name,status in [('complete','C'),('source-fail-dom-missing','NC'),('source-only','NT'),('two-states','C')]:
   with self.subTest(case=name),tempfile.TemporaryDirectory() as folder:
    p=Path(folder);build(p,data(name));report=tsep.read_json(p/'bundle/report.json');self.assertEqual(report['results'][0]['status'],status);self.assertEqual((p/'bundle/input.json').read_bytes(),(p/'input.json').read_bytes());self.assertTrue(tsep.decision(report)['synthetic_evidence']);self.assertIn('essential_links_interpretation',tsep.decision(report))
    with patch.object(socket,'socket',side_effect=AssertionError('Offline replay')):r=replay.replay(p/'bundle',p/'replayed')
    self.assertTrue(r['same_atomic_results']);self.assertTrue(r['same_gate'])
    for lang in ('fr','en'):
     rendered=html.render(p/'bundle/report.json',language=lang);self.assertIn(html.TEXT[lang]['essential_links_note'],rendered);self.assertIn(html.TEXT[lang]['essential_binding'],rendered)
     if name=='two-states':self.assertIn(html.TEXT[lang]['essential_repeated'],rendered)
 def test_intake_provenance_refusals_without_prior_plan(self):
  for missing in (False,True):
   for mutation in ('false-real','not-bool','false-synthetic'):
    with self.subTest(missing=missing,mutation=mutation),tempfile.TemporaryDirectory() as folder:
     d=data();t=d['targets'][0]
     if missing:t['intent'].pop('essential_links')
     access='public' if mutation=='false-real' else 'synthetic'
     if mutation=='not-bool':t['link_synthetic']='yes'
     if mutation=='false-synthetic':t['link_synthetic']=False
     p=Path(folder)
     with self.assertRaises(tsep.Invalid):build(p,d,access,dest='refused')
     self.assertFalse((p/'refused').exists())
 def test_corrupt_original_and_existing_destination_are_preserved(self):
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder);d=data();hop=d['targets'][0]['http'][0];hop['response']={'base64':base64.b64encode(hop['response'].encode()).decode(),'sha256':'0'*64}
   with self.assertRaises(tsep.Invalid):build(p,d,dest='refused')
   self.assertFalse((p/'refused').exists());(p/'existing').mkdir();(p/'existing/untouched').write_bytes(b'original')
   with self.assertRaises(tsep.Invalid):build(p,data(),dest='existing')
   self.assertEqual((p/'existing/untouched').read_bytes(),b'original')
 def test_missing_runtime_and_partial_rule_never_establish_control_c(self):
  with patch.dict(os.environ,{},clear=True):self.assertEqual([r['outcome'] for r in evaluate(data())],['inconclusive','inconclusive'])
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder);d=data();d['rules']=['TS17-A01'];build(p,d);self.assertEqual(tsep.read_json(p/'bundle/report.json')['results'][0]['status'],'NT')
 def test_reader_sources_bound_to_adapter(self):
  files=captures.source_files()
  for name in ('essential_links','essential_links_source','essential_links_dom'):self.assertIn('conformance/'+name+'.py',files)
 def test_retained_report_diagnostic_escapes_html(self):
  note=native.assess_target(data()['targets'][0]);note['rule_stage']='source';note['source']['reason']='<img src=x onerror=alert(1)>'
  for lang in ('fr','en'):
   with patch.object(native,'assess_target',side_effect=AssertionError('No report recalculation')):out=html.essential_links_values({'reason':native.PREFIX+json.dumps(note)},html.TEXT[lang])
   self.assertNotIn('<img ',out);self.assertIn('&lt;img ',out)
if __name__=='__main__':unittest.main()
