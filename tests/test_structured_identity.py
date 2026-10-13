"""TS32 frozen contradictions and evidence-bound report/replay integration."""
import copy,hashlib,json,os,socket,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import tsep
from adapters import captures,replay
from conformance import structured_identity as s
from conformance.corpus import expand
from conformance.evaluate import evaluate
from reports import html
ROOT=Path(__file__).resolve().parents[1]
NODE=os.environ.get('TSEP_SOURCE_NODE')
FROZEN={'structured-identity-v1.json':'26b2cbe0223642f82b7ac3d0840653547c6dd9d47610ac45af31729ccaae631b','structured-identity-boundaries-v1.json':'5836410891c28c0a8230eaca7804248ab379a673612bbccc8d13ef7367e7e96a'}
def cases():
 rows=[]
 for name,want in FROZEN.items():
  p=ROOT/'tests/fixtures'/name;raw=p.read_bytes()
  if hashlib.sha256(raw).hexdigest()!=want or p.with_suffix('.sha256').read_text().strip()!=want:raise ValueError('Changed prefrozen TS32 oracle')
  rows.extend(json.loads(raw)['cases'])
 return rows
def data(name='complete'):return copy.deepcopy(next(c['input'] for c in cases() if c['id']=='structured-identity-v1-'+name))
class StructuredIdentity(unittest.TestCase):
 def test_prefrozen_oracles_are_distributed_unchanged(self):
  rows=cases();self.assertEqual(len(rows),62)
  corpus=expand(tsep.read_json(ROOT/'conformance/cases.json'));self.assertEqual(corpus['cases'][1494:],rows);self.assertEqual(len(corpus['cases']),1556)
 @unittest.skipUnless(NODE,'Explicit Node 24 for full native TS32 observations')
 def test_all_prefrozen_cases_offline(self):
  with patch.object(socket,'socket',side_effect=AssertionError('No network collection')):
   for c in cases():
    before=copy.deepcopy(c['input'])
    with self.subTest(case=c['id']):
     self.assertEqual([r['outcome'] for r in evaluate(c['input'])],[r['outcome'] for r in c['expected']]);self.assertEqual(c['input'],before)
 def test_missing_runtime_stays_unknown(self):
  with patch.dict(os.environ,{},clear=True):
   rows=evaluate(data());self.assertEqual([r['outcome'] for r in rows],['pass','inconclusive','inconclusive']);self.assertIn('TSEP_SOURCE_NODE',rows[1]['reason'])
 def test_malformed_inputs_never_raise_or_pass(self):
  for key in ('intent','context','identity_documents'):
   for v in (None,False,[],{},'broken'):
    t=data()['targets'][0];t[key]=v
    for rule in (s.RULES if key!='identity_documents' else s.RULES[1:]):
     with self.subTest(key=key,value=v,rule=rule):self.assertEqual(s.assess(t,rule)[0],'inconclusive')
 @unittest.skipUnless(NODE,'Explicit Node 24 for TS32 bundle/replay')
 def test_reports_replay_and_labels(self):
  for name,status in [('complete','C'),('required-identifier-changed','NC'),('missing-review','NT'),('known-collision-missing-document','NC')]:
   with self.subTest(name=name),tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp);p=root/'input.json';p.write_text(json.dumps(data(name)))
    captures.build(p,root/'bundle',assessor='Fictional reviewer',label='Authored TS32',selection_method='Declared fictional corpus',access='synthetic',mode='semiAuto')
    report=tsep.read_json(root/'bundle/report.json');self.assertEqual(report['results'][0]['status'],status)
    self.assertTrue({'structured-data','intent'}<={a['kind'] for a in report['artifacts']});self.assertIn('structured_identity_interpretation',tsep.decision(report))
    result=replay.replay(root/'bundle',root/'replay');self.assertTrue(result['same_atomic_results']);self.assertTrue(result['same_gate'])
    for lang in ('fr','en'):
     out=html.render(root/'bundle/report.json',language=lang);self.assertIn(html.TEXT[lang]['identity_note'],out);self.assertIn(html.TEXT[lang]['identity_values'],out)
 def test_partial_scope_and_provenance(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);d=data();d['rules']=['TS32-A01'];p=root/'input.json';p.write_text(json.dumps(d))
   captures.build(p,root/'bundle',assessor='Fictional reviewer',label='Partial TS32',selection_method='Authored',access='synthetic',mode='semiAuto')
   self.assertEqual(tsep.read_json(root/'bundle/report.json')['results'][0]['status'],'NT')
   with self.assertRaisesRegex(tsep.Invalid,'provenance'):captures.build(p,root/'public',assessor='Fictional',label='Invalid',selection_method='Authored',access='public',mode='semiAuto')
   d=data('false-human-review');p.write_text(json.dumps(d))
   with self.assertRaisesRegex(tsep.Invalid,'review provenance'):captures.build(p,root/'mixed',assessor='Fictional',label='Invalid',selection_method='Authored',access='synthetic',mode='semiAuto')
 def test_html_escapes_retained_rows_without_reassessment(self):
  a={'reason':s.PREFIX+json.dumps({'rows':[dict(subject='<script>bad</script>',outcome='inconclusive',reason='<img src=x>')]})}
  with patch.object(s,'assess',side_effect=AssertionError('No reassessment')):out=html.identity_values(a,html.TEXT['fr'])
  self.assertNotIn('<script>',out);self.assertNotIn('<img',out);self.assertIn('&lt;script&gt;',out)
 def test_native_sources_bound_to_adapter(self):
  self.assertTrue({'conformance/structured_identity.py','experiments/jsonld_processing.py','experiments/jsonld_processing.mjs','third_party/jsonld/jsonld-9.0.0.tgz'}<=set(captures.source_files()))
