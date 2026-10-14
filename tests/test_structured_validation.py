"""TS33 prefrozen cases, native classifications and standalone report/replay."""
import copy, hashlib, json, os, socket, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import tsep
from adapters import captures, replay
from conformance import structured_validation as s
from conformance.corpus import expand
from conformance.evaluate import evaluate
from reports import html

ROOT=Path(__file__).resolve().parents[1]
NODE=os.environ.get('TSEP_SOURCE_NODE')
FROZEN='8679acd7176851b4f2a0dc495e78bf77591422d2cdbe3b287808d6b34ca732cf'
def cases():
 p=ROOT/'tests/fixtures/structured-validation-v1.json';raw=p.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=FROZEN or p.with_suffix('.sha256').read_text().strip()!=FROZEN:
  raise ValueError('Changed prefrozen TS33 expectations')
 return json.loads(raw)['cases']
def data(name='complete'):
 return copy.deepcopy(next(c['input'] for c in cases() if c['id']=='structured-validation-v1-'+name))

class StructuredValidation(unittest.TestCase):
 def test_prefrozen_expected_matrix_is_distributed(self):
  rows=cases();self.assertEqual(len(rows),52)
  corpus=expand(tsep.read_json(ROOT/'conformance/cases.json'))
  self.assertEqual(corpus['cases'][1556:1608],rows)
  self.assertEqual(len(corpus['cases']),1608)
 @unittest.skipUnless(NODE,'Explicit Node24 needed for native TS33 surfaces')
 def test_all_prefrozen_cases_without_network_or_input_changes(self):
  with patch.object(socket,'socket',side_effect=AssertionError('No external collection')):
   for c in cases():
    before=copy.deepcopy(c['input'])
    with self.subTest(case=c['id']):
     actual=evaluate(c['input'])
     self.assertEqual([r['outcome'] for r in actual],[r['outcome'] for r in c['expected']],json.dumps(actual,ensure_ascii=False))
     self.assertEqual(c['input'],before)
 def test_missing_runtime_keeps_google_layer_separate(self):
  with patch.dict(os.environ,{},clear=True):
   result=evaluate(data());self.assertEqual([r['outcome'] for r in result],['pass','inconclusive','pass'])
   self.assertIn('TSEP_SOURCE_NODE',result[1]['reason'])
 def test_malformed_inputs_do_not_raise_or_pass(self):
  for key in ('jsonld','intent','context'):
   for value in (None,False,[],{},'broken'):
    t=data()['targets'][0];t[key]=value
    for rule in s.RULES:
     with self.subTest(key=key,value=value,rule=rule):self.assertEqual(s.assess(t,rule)[0],'inconclusive')
 def test_vocabulary_namespace_and_role_boundaries(self):
  v=s.vocabulary()
  self.assertEqual(s.term_result('class','http://schema.org/Thing',v)[0],'pass')
  self.assertEqual(s.term_result('class','https://schema.org/Thing',v)[0],'pass')
  self.assertEqual(s.term_result('property','https://schema.org/Thing',v)[0],'fail')
  self.assertEqual(s.term_result('class','https://schema.org/TsepInvented',v)[0],'fail')
  self.assertEqual(s.term_result('property','https://schema.org/actors',v)[0],'pass')
  self.assertIn('supersededBy',s.term_result('property','https://schema.org/actors',v)[1])
  self.assertEqual(s.terms([{'@id':'x','https://schema.org/name':[{'@value':{'foreign':'data'},'@type':'@json'}]}]),[('property','https://schema.org/name')])
 def test_vocabulary_bytes_are_pinned(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);p=root/s.VOCABULARY;p.parent.mkdir(parents=True);p.write_text('{}')
   with patch.object(s,'ROOT',root),self.assertRaises(ValueError):s.vocabulary()
 @unittest.skipUnless(NODE,'Explicit Node24 for actual native TS33 report/replay')
 def test_c_nc_nt_and_technical_failure_replay(self):
  for name,status in [('complete','C'),('blocking-error','NC'),('source-invalid-json','NC'),('missing-review','NT'),('api403','NT')]:
   with self.subTest(name=name),tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp);p=root/'input.json';p.write_text(json.dumps(data(name)))
    before=p.read_bytes()
    captures.build(p,root/'bundle',assessor='Fictional reviewer',label='Authored TS33',selection_method='One fictional page',access='synthetic',mode='semiAuto')
    report=tsep.read_json(root/'bundle/report.json');self.assertEqual(report['results'][0]['status'],status)
    self.assertTrue({'structured-data','validator-output','intent'}<={a['kind'] for a in report['artifacts']})
    self.assertTrue(tsep.decision(report)['synthetic_evidence']);self.assertIn('structured_validation_interpretation',tsep.decision(report))
    result=replay.replay(root/'bundle',root/'replayed');self.assertTrue(result['same_atomic_results']);self.assertTrue(result['same_gate'])
    self.assertEqual(p.read_bytes(),before)
    for language in ('fr','en'):
     output=html.render(root/'bundle/report.json',language=language)
     self.assertIn(html.TEXT[language]['validation_note'],output);self.assertIn(html.TEXT[language]['validation_values'],output)
 def test_partial_scope_and_false_provenance_refused(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);d=data();d['rules']=['TS33-A01'];p=root/'input.json';p.write_text(json.dumps(d))
   captures.build(p,root/'bundle',assessor='Fictional',label='Partial TS33',selection_method='Authored',access='synthetic',mode='semiAuto')
   self.assertEqual(tsep.read_json(root/'bundle/report.json')['results'][0]['status'],'NT')
   with self.assertRaises(tsep.Invalid):captures.build(p,root/'public',assessor='Fictional',label='False public',selection_method='Authored',access='public',mode='semiAuto')
   d['targets'][0]['validation_plan_review']['provenance']='human';p.write_text(json.dumps(d))
   with self.assertRaises(tsep.Invalid):captures.build(p,root/'mixed',assessor='Fictional',label='False human',selection_method='Authored',access='synthetic',mode='semiAuto')
 def test_html_escapes_without_reassessment(self):
  atom={'reason':s.PREFIX+json.dumps({'rows':[dict(subject='<script>x</script>',outcome='inconclusive',reason='<img>')]})}
  with patch.object(s,'assess',side_effect=AssertionError('No reassessment')):out=html.validation_values(atom,html.TEXT['fr'])
  self.assertNotIn('<script>',out);self.assertNotIn('<img>',out);self.assertIn('&lt;script&gt;',out)
 def test_source_identity_contains_module_and_vocabulary(self):
  files=captures.source_files();self.assertIn('conformance/structured_validation.py',files)
  self.assertEqual(files[s.VOCABULARY],s.VOCABULARY_SHA256)

 def test_other_page_plan_never_becomes_c(self):
  t=data()['targets'][0];t['url']='https://example.test/other'
  self.assertEqual([s.assess(t,r)[0] for r in s.RULES],['inconclusive']*3)
 def test_separate_snapshot_dates_visible_without_correspondence_claim(self):
  t=data()['targets'][0];outcome,reason=s.assess(t,'TS33-A03')
  self.assertEqual(outcome,'pass')
  note=json.loads(reason[len(s.PREFIX):]);snap=note['indexed_snapshot']
  self.assertEqual(snap['correspondence'],'not-established')
  self.assertEqual(snap['page_http_received_at'],t['jsonld']['http_received_at'])
  self.assertEqual(snap['page_dom_observed_at'][0]['observed_at'],t['jsonld']['states'][0]['observed_at'])
  self.assertNotEqual(snap['last_crawl_time'],snap['page_http_received_at'])
  for lang in ('fr','en'):
   rendered=html.validation_values({'reason':reason},html.TEXT[lang])
   self.assertIn('not-established',rendered);self.assertIn(snap['page_http_received_at'],rendered)
   self.assertIn(snap['last_crawl_time'],rendered)

 def test_native_validation_provenance_survives_missing_plan(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);source=root/'in.json';payload=data();target=payload['targets'][0]
   target['intent']={};target.pop('jsonld',None)
   for access in ('public','restricted'):
    source.write_text(json.dumps(payload));destination=root/access
    with self.subTest(access=access),self.assertRaises(tsep.Invalid):
     captures.build(source,destination,assessor='Fictional',label='Synthetic missing-plan counterexample',selection_method='Authored',access=access,mode='semiAuto')
    self.assertFalse(destination.exists())
   mixed=copy.deepcopy(payload);mixed['targets'][0]['validation_plan_review']['provenance']='human';source.write_text(json.dumps(mixed))
   with self.assertRaises(tsep.Invalid):
    captures.build(source,root/'mixed',assessor='Fictional',label='Mixed supplied provenance',selection_method='Authored',access='synthetic',mode='semiAuto')
   self.assertFalse((root/'mixed').exists())
   source.write_text(json.dumps(payload));original=source.read_bytes()
   captures.build(source,root/'intact',assessor='Fictional',label='Intact synthetic missing plan',selection_method='Authored',access='synthetic',mode='semiAuto')
   report=tsep.read_json(root/'intact/report.json');self.assertEqual(report['results'][0]['status'],'NT')
   self.assertTrue(tsep.decision(report)['synthetic_evidence']);self.assertEqual((root/'intact/input.json').read_bytes(),original)

 def test_wrapped_validation_provenance_cannot_be_made_public(self):
  child=data();t=child['targets'][0];t['intent']={};t.pop('jsonld',None)
  outer=dict(input_version='2',rules=['TS41-A01'],targets=[dict(url=t['url'],observed_at=t['observed_at'],intent={},release_runs=[dict(input_json=json.dumps(child))])])
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);source=root/'in.json';source.write_text(json.dumps(outer));original=source.read_bytes()
   for access in ('public','restricted'):
    with self.subTest(access=access),self.assertRaises(tsep.Invalid):
     captures.build(source,root/access,assessor='Fictional',label='Synthetic TS33 wrapped in release input',selection_method='Authored',access=access,mode='semiAuto')
    self.assertFalse((root/access).exists())
   captures.build(source,root/'synthetic',assessor='Fictional',label='Synthetic wrapped missing plan',selection_method='Authored',access='synthetic',mode='semiAuto')
   report=tsep.read_json(root/'synthetic/report.json');self.assertEqual(report['results'][0]['status'],'NT')
   self.assertTrue(tsep.decision(report)['synthetic_evidence']);self.assertEqual((root/'synthetic/input.json').read_bytes(),original)

 def test_explicit_provenance_flags_survive_missing_plan_and_records(self):
  original=data()['targets'][0]
  flags=('delivery_synthetic','identity_synthetic','structured_synthetic','inspection_synthetic')
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);source=root/'in.json'
   for flag in flags:
    for index,(value,access) in enumerate([(True,'public'),(True,'restricted'),(False,'synthetic'),('true','synthetic'),(None,'public')]):
     target=dict(url=original['url'],observed_at=original['observed_at'],intent={},**{flag:value})
     payload=dict(input_version='2',rules=['TS33-A01'],targets=[target]);source.write_text(json.dumps(payload));dest=root/(flag+str(index))
     with self.subTest(flag=flag,value=value,access=access),self.assertRaises(tsep.Invalid):
      captures.build(source,dest,assessor='Fictional',label='Explicit provenance counterexample',selection_method='Authored',access=access)
     self.assertFalse(dest.exists())
   target=dict(url=original['url'],observed_at=original['observed_at'],intent={},structured_synthetic=True)
   source.write_text(json.dumps(dict(input_version='2',rules=['TS33-A01'],targets=[target])))
   captures.build(source,root/'intact',assessor='Fictional',label='Synthetic incomplete dossier',selection_method='Authored',access='synthetic')
   report=tsep.read_json(root/'intact/report.json');self.assertEqual(report['results'][0]['status'],'NT');self.assertTrue(tsep.decision(report)['synthetic_evidence'])
