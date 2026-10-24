"""TS36 prefrozen chronology, retained contradictions, intake and exact replay."""
from pathlib import Path
import copy,hashlib,json,socket,subprocess,tempfile,unittest
from unittest.mock import patch
import tsep
from adapters import captures,replay,monitoring_intake as intake
from conformance import release_monitoring as m
from conformance.evaluate import evaluate
from reports import html
ROOT=Path(__file__).resolve().parents[1]
FROZEN='c993be1553c4e30683c4c863c5bb3fadd238582f84adea71d24d469b2dc50497'
def cases():
 rows=[]
 for name in ('release-monitoring-v1.json','release-monitoring-boundaries-v1.json'):
  p=ROOT/'tests/fixtures'/name;raw=p.read_bytes();want=p.with_suffix('.sha256').read_text().strip()
  if hashlib.sha256(raw).hexdigest()!=want or name=='release-monitoring-v1.json' and want!=FROZEN:raise ValueError('Changed frozen TS36 oracle')
  rows.extend(json.loads(raw)['cases'])
 return rows
def data(name='complete-cycle'):return copy.deepcopy(next(c['input'] for c in cases() if c['id']=='release-monitoring-v1-'+name))
class ReleaseMonitoring(unittest.TestCase):
 def test_prefrozen_cases_no_collection(self):
  rows=cases();self.assertEqual(len(rows),65);self.assertEqual(tsep.read_json(ROOT/'conformance/cases.json')['cases'][1370:1435],rows)
  with patch.object(socket,'socket',side_effect=AssertionError('No network')),patch.object(subprocess,'Popen',side_effect=AssertionError('No processes')):
   for c in rows:
    with self.subTest(case=c['id']):self.assertEqual([(x['rule_id'],x['target'],x['outcome']) for x in evaluate(c['input'])],[(x['rule_id'],x['target'],x['outcome']) for x in c['expected']])
 def test_pending_time_never_heals_false_early_closure(self):
  t=data('false-early-closure')['targets'][0]
  self.assertEqual(m.assess(t,'TS36-A03')[0],'fail');t['observed_at']='2026-10-10T00:00:00Z'
  self.assertEqual(m.assess(t,'TS36-A03')[0],'fail')
 def test_independent_known_claim_contradictions(self):
  for name in ('known-api-failure-missing-log','known-log-failure-api-error','known-failure-with-future-stages'):
   with self.subTest(name=name):self.assertEqual(m.assess(data(name)['targets'][0],'TS36-A03')[0],'fail')
 def test_nanosecond_half_open_stage_boundary(self):
  t=data()['targets'][0];r=t['monitoring_checkpoints'][1]['inspection_records'][0]
  r['retrieved_at']='2026-08-03T00:59:59.999999999Z';self.assertEqual(m.assess(t,'TS36-A02')[0],'pass')
  r['retrieved_at']='2026-08-03T01:00:00Z';self.assertEqual(m.assess(t,'TS36-A02')[0],'inconclusive')
 def test_utc_format_retains_fraction(self):
  self.assertEqual(m.utc(m.stamp('2026-08-03T00:59:59.123456789+00:00')),'2026-08-03T00:59:59.123456789Z')
 def test_bound_refusal_retains_no_partial_failure(self):
  t=data('wrong-api-claim')['targets'][0]
  with patch.object(m,'MAX_BYTES',1):
   outcome,reason=m.assess(t,'TS36-A03');self.assertEqual(outcome,'inconclusive');self.assertIn('no truncated conclusion',reason)
 def test_malformed_top_level_evidence_is_not_success(self):
  for key in ('intent','monitoring_deployment','monitoring_checkpoints','monitoring_reviews','monitoring_closure_review'):
   for value in (None,True,'bad',{},[]):
    t=data()['targets'][0];t[key]=value
    for rule in intake.RULES:
     with self.subTest(key=key,value=value,rule=rule):self.assertIn(m.assess(t,rule)[0],('pass','inconclusive'))
 def test_complete_adverse_pending_false_closure_reports_and_replay(self):
  for name,status in [('complete-cycle','C'),('adverse-observed-documented','C'),('future-stages','NT'),('false-early-closure','NC')]:
   with self.subTest(name=name),tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp);p=root/'input.json';p.write_text(json.dumps(data(name)))
    captures.build(p,root/'bundle',assessor='Fictional author',label='Authored TS36',selection_method='Fictional singleton',access='synthetic',mode='semiAuto')
    r=tsep.read_json(root/'bundle/report.json');self.assertEqual(r['results'][0]['status'],status)
    self.assertTrue({'logs','search-console','change-history','intent'}<={a['kind'] for a in r['artifacts']})
    self.assertIn('release_monitoring_interpretation',tsep.decision(r))
    rep=replay.replay(root/'bundle',root/'replay');self.assertTrue(rep['replayed']);self.assertTrue(rep['same_atomic_results']);self.assertTrue(rep['same_gate'])
    for language in ('fr','en'):
     out=html.render(root/'bundle/report.json',language=language);self.assertIn(html.TEXT[language]['monitoring_note'],out);self.assertIn('Google (API)',out)
 def test_partial_rule_and_synthetic_restriction(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);d=data();d['rules']=['TS36-A01'];p=root/'input.json';p.write_text(json.dumps(d))
   captures.build(p,root/'bundle',assessor='Fictional',label='Partial',selection_method='Authored',access='synthetic',mode='semiAuto');self.assertEqual(tsep.read_json(root/'bundle/report.json')['results'][0]['status'],'NT')
   with self.assertRaises(tsep.Invalid):captures.build(p,root/'public',assessor='Fictional',label='Wrong',selection_method='Authored',access='public',mode='semiAuto')
 def test_intake_separate_blank_closure_and_tamper(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);t=data()['targets'][0];reviews=t.pop('monitoring_reviews');closure=t.pop('monitoring_closure_review');pieces={k:t.pop(k) for k in ('monitoring_deployment','monitoring_checkpoints')}
   p=root/'plan.json';p.write_text(json.dumps(t));e=root/'evidence.json';e.write_text(json.dumps(pieces))
   intake.prepare(p,e,root/'prepared');blank=root/'prepared/review-request.json';r=tsep.read_json(blank)
   self.assertTrue(all(not q['complete'] and q['reviewer'] is None for q in r['reviews']))
   intake.build(root/'prepared',blank,root/'blank','Fictional');self.assertEqual(tsep.read_json(root/'blank/report.json')['results'][0]['status'],'NT')
   r['reviews']=reviews;sup=root/'reviews.json';sup.write_text(json.dumps(r));intake.closure_request(root/'prepared',sup,root/'closure')
   c=tsep.read_json(root/'closure/closure-request.json');self.assertFalse(c['review']['complete']);self.assertIsNone(c['review']['completed']);self.assertEqual(c['review']['binding_sha256'],closure['binding_sha256'])
   intake.build(root/'prepared',sup,root/'open','Fictional');self.assertEqual(tsep.read_json(root/'open/report.json')['results'][0]['status'],'NT')
   c['review']=closure;cp=root/'closure.json';cp.write_text(json.dumps(c));intake.build(root/'prepared',sup,root/'closed','Fictional',cp);self.assertEqual(tsep.read_json(root/'closed/report.json')['results'][0]['status'],'C')
   r['reviews'][0]['reason']+=' changed';sup.write_text(json.dumps(r));intake.build(root/'prepared',sup,root/'stale-closure','Fictional',cp);self.assertEqual(tsep.read_json(root/'stale-closure/report.json')['results'][0]['status'],'NT')
   (root/'prepared/originals/evidence.json').write_text('{}')
   with self.assertRaisesRegex(tsep.Invalid,'Changed intake file'):intake.build(root/'prepared',sup,root/'tampered','Fictional')
 def test_report_escapes_and_never_reassesses(self):
  atom={'reason':m.PREFIX+json.dumps({'stages':[{'id':'<script>alert(1)</script>'}]})}
  with patch.object(m,'assess',side_effect=AssertionError('No reassessment')):out=html.monitoring_values(atom,html.TEXT['fr'])
  self.assertNotIn('<script>',out);self.assertIn('&lt;script&gt;',out)
if __name__=='__main__':unittest.main()
