"""TS12 frozen documentary boundaries, attribution, intake and exact replay."""
import copy
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch
import tsep
from conformance import canonical_comparison as c
from conformance.evaluate import evaluate
from conformance.run import compare
from adapters import captures,replay,comparison_intake,inspection_intake
from reports import html

ROOT=Path(__file__).resolve().parents[1]
FROZEN='d8113fa7dbd0a0388a206afcbc16088a7301c10a445dde1906caa1082ee8181c'
def cases():
 p=ROOT/'tests/fixtures/canonical-comparison-v1.json';raw=p.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=FROZEN or p.with_suffix('.sha256').read_text().strip()!=FROZEN:raise ValueError('Changed frozen TS12 oracle')
 return json.loads(raw)['cases']
def data(name='qualified-agreement'):return copy.deepcopy(next(x['input'] for x in cases() if x['id']=='canonical-comparison-v1-'+name))
class Clock(datetime):
 @classmethod
 def now(cls,tz=None):return cls(2026,10,10,12,tzinfo=timezone.utc)

class CanonicalComparison(unittest.TestCase):
 def test_frozen_cases_and_independent_unknowns(self):
  rows=cases();self.assertEqual(len(rows),66)
  self.assertEqual(tsep.read_json(ROOT/'conformance/cases.json')['cases'][1304:1370],rows)
  with patch.object(socket,'socket',side_effect=AssertionError('No Python network')):
   for case in rows:
    with self.subTest(case=case['id']):
     agrees,diffs,reduced=compare(case['expected'],evaluate(case['input']))
     self.assertEqual(diffs,[])
     if __import__('os').environ.get('TSEP_SOURCE_NODE'):self.assertEqual(reduced,[])
 def test_literal_comparison_retains_case_and_duplicates(self):
  t=data('normalization-difference-literal')['targets'][0];note=[];c.assess(t,'TS12-A02',diagnostics=note)
  m=note[0]['members'][0]
  if m['facts']['html']['state']=='unknown':self.skipTest('Optional source runtime unavailable')
  row=next(r for r in m['comparisons'] if r['surface']=='html')
  self.assertEqual(row['value'],'https://EXAMPLE.com/page');self.assertEqual(row['google'],'exact-string-different')
  note=[];c.assess(data('identical-html-duplicates-retained')['targets'][0],'TS12-A02',diagnostics=note)
  self.assertEqual(len(note[0]['members'][0]['facts']['html']['values']),2)
 def test_independent_claim_failure_needs_no_node(self):
  with patch.object(c.source_canonical,'Surface',side_effect=ValueError('No source reader')):
   for name in ('wrong-google-and-missing-render','wrong-google-and-missing-document','source-unknown-http-claim-contradicted','missing-member-independent-failure'):
    self.assertEqual(c.assess(data(name)['targets'][0],'TS12-A03')[0],'fail',name)
 def test_bound_refusal_does_not_retain_partial_failure(self):
  with patch.object(c,'MAX_DIAGNOSTIC_BYTES',1):
   outcome,reason=c.assess(data('wrong-google-claim')['targets'][0],'TS12-A03')
   self.assertEqual(outcome,'inconclusive');self.assertIn('no truncated conclusion',reason)
 def test_malformed_top_level_values_do_not_crash(self):
  for key in ('intent','inspection_records','documents','comparison_reviews','inspection_plan_review'):
   for value in (None,True,[],'bad',{}):
    t=data()['targets'][0];t[key]=value
    for rule in comparison_intake.RULES:
     with self.subTest(key=key,value=value,rule=rule):self.assertIn(c.assess(t,rule)[0],('pass','inconclusive'))
 def test_bundles_C_C_NC_NT_and_bilingual_exact_replay(self):
  for name,want in [('qualified-agreement','C'),('qualified-divergence','C'),('wrong-google-and-missing-render','NC'),('source-only','NT')]:
   with self.subTest(name=name),tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp);p=root/'input.json';p.write_text(json.dumps(data(name)))
    captures.build(p,root/'bundle',assessor='Fictional author',label='Authored TS12',selection_method='Fixed fictional singleton',access='synthetic',mode='semiAuto')
    report=tsep.read_json(root/'bundle/report.json')
    if want=='C' and not __import__('os').environ.get('TSEP_SOURCE_NODE'):want='NT'
    self.assertEqual(report['results'][0]['status'],want)
    self.assertTrue({'intent','search-console','http','html'}<={x['kind'] for x in report['artifacts']})
    result=replay.replay(root/'bundle',root/'replay');self.assertTrue(result['replayed']);self.assertTrue(result['same_source_observations'])
    for language in ('fr','en'):
     rendered=html.render(root/'bundle/report.json',language=language)
     self.assertIn(html.TEXT[language]['comparison_note'],rendered);self.assertIn('googleCanonical',rendered)
 def test_partial_control_cannot_pass(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);v=data();v['rules']=['TS12-A01'];p=root/'input.json';p.write_text(json.dumps(v))
   captures.build(p,root/'bundle',assessor='Fictional',label='Partial',selection_method='Authored',access='synthetic',mode='semiAuto')
   self.assertEqual(tsep.read_json(root/'bundle/report.json')['results'][0]['status'],'NT')
 def test_intake_blank_supplied_review_and_tamper(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(comparison_intake,'datetime',Clock),patch.object(inspection_intake,'datetime',Clock),patch.object(captures,'datetime',Clock):
   root=Path(tmp);t=data()['targets'][0];rec=t.pop('inspection_records')[0];docs=t.pop('documents');q=t.pop('comparison_reviews')[0]
   plan=root/'plan.json';plan.write_text(json.dumps(t));technical=root/'documents.json';technical.write_text(json.dumps(docs))
   obs=root/'observation';obs.mkdir()
   for key in ('request','response'):(obs/(key+'.json')).write_text(rec[key]['raw_text'])
   manifest={'kind':'tsep-url-inspection-observation','format_version':'1','provenance':'synthetic-exercise','description':'Authored API files','retrieved_at':rec['retrieved_at'],'http_status':200,'change':None,'request_sha256':rec['request']['sha256'],'response_sha256':rec['response']['sha256']}
   (obs/'manifest.json').write_text(json.dumps(manifest))
   comparison_intake.prepare(plan,[obs],technical,root/'prepared')
   request=tsep.read_json(root/'prepared/review-request.json');blank=request['reviews'][0]
   self.assertFalse(blank['complete']);self.assertIsNone(blank['reviewer']);self.assertTrue(all(v['state']=='unknown' for v in blank['claims'].values()))
   comparison_intake.build(root/'prepared',root/'prepared/review-request.json',root/'blank','Fictional')
   self.assertEqual(tsep.read_json(root/'blank/report.json')['results'][0]['status'],'NT')
   imported=tsep.read_json(root/'prepared/input.json')['targets'][0]
   self.assertEqual(blank['binding_sha256'],c.binding(imported,imported['inspection_records'][0],imported['documents'][0]))
   q['binding_sha256']=blank['binding_sha256'];request['reviews']=[q]
   supplied=root/'reviews.json';supplied.write_text(json.dumps(request))
   comparison_intake.build(root/'prepared',supplied,root/'supplied','Fictional')
   expected='C' if __import__('os').environ.get('TSEP_SOURCE_NODE') else 'NT'
   self.assertEqual(tsep.read_json(root/'supplied/report.json')['results'][0]['status'],expected)
   self.assertTrue(replay.replay(root/'supplied',root/'replay')['replayed'])
   (root/'prepared/originals/technical.json').write_text('[]')
   with self.assertRaisesRegex(tsep.Invalid,'Changed intake file'):comparison_intake.build(root/'prepared',supplied,root/'altered','Fictional')
 def test_report_escapes_without_reassessing(self):
  atom={'reason':c.PREFIX+json.dumps({'members':[{'value':'<script>alert(1)</script>'}]})}
  with patch.object(c,'assess',side_effect=AssertionError('No recalculation')):text=html.comparison_values(atom,html.TEXT['fr'])
  self.assertIn('&lt;script&gt;',text);self.assertNotIn('<script>',text)
 def test_restricted_real_provenance_cannot_be_public(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);p=root/'input.json';p.write_text(json.dumps(data()))
   with self.assertRaises(tsep.Invalid):captures.build(p,root/'bad',assessor='Fictional',label='Bad access',selection_method='Authored',access='public',mode='semiAuto')

if __name__=='__main__':unittest.main()
