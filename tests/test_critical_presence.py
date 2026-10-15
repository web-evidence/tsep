"""TS25 closed native scope, refusal boundary, exact export/replay, no collection."""
import copy,hashlib,json,os,socket,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import tsep
from adapters import captures,replay
from conformance import critical_presence as native
from conformance.evaluate import evaluate
from reports import html
ROOT=Path(__file__).resolve().parents[1]
def cases():
    p=ROOT/'tests/fixtures/critical-presence-cases-v1.json';raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=p.with_suffix('.sha256').read_text().strip():raise ValueError('Changed authored TS25 cases')
    extra=ROOT/'tests/fixtures/critical-presence-boundary-cases-v2.json';other=extra.read_bytes()
    if hashlib.sha256(other).hexdigest()!=extra.with_suffix('.sha256').read_text().strip():raise ValueError('Changed authored TS25 boundary cases')
    return json.loads(raw)['cases']+json.loads(other)['cases']
def data(name='five-roles-complete'):
    return copy.deepcopy(next(r['input'] for r in cases() if r['id']==name))
def build(root,value,access='synthetic'):
    raw=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode();(root/'input.json').write_bytes(raw)
    captures.build(root/'input.json',root/'bundle',assessor='Authored synthetic exercise',label='Synthetic critical presence',selection_method='Prior finite five-role population',access=access)
    return raw
class CriticalPresence(unittest.TestCase):
    def test_authored_native_cases_do_not_mutate_or_collect(self):
        self.assertEqual(len(cases()),183)
        for r in cases():
            with self.subTest(case=r['id']),patch.object(socket,'socket',side_effect=AssertionError('No network')):
                before=copy.deepcopy(r['input']);result=evaluate(r['input']);ex=r['expected'] if type(r['expected']) is list else [r['expected']]
                self.assertEqual([v['outcome'] for v in result],ex);self.assertEqual(before,r['input'])
    def test_bundles_originals_and_replay(self):
        for name,status in [('five-roles-complete','C'),('five-roles-source-only-without-dom','C'),('five-roles-mixed-failure-unknown','NC'),('five-roles-no-plan-review','NT')]:
            with self.subTest(case=name),tempfile.TemporaryDirectory() as td,patch.object(socket,'socket',side_effect=AssertionError('No collection')):
                root=Path(td);d=data(name);raw=build(root,d);report=tsep.read_json(root/'bundle/report.json')
                self.assertEqual(report['results'][0]['status'],status);self.assertTrue(tsep.decision(report)['synthetic_evidence']);self.assertIn('critical_presence_interpretation',tsep.decision(report))
                self.assertEqual((root/'bundle/input.json').read_bytes(),raw)
                repeated=replay.replay(root/'bundle',root/'replay');self.assertTrue(repeated['same_atomic_results']);self.assertTrue(repeated['same_gate'])
                for lang in ('fr','en'):
                    page=html.render(root/'bundle/report.json',language=lang);self.assertIn(html.TEXT[lang]['presence_title'],page);self.assertIn(html.TEXT[lang]['presence_note'],page)
    def test_unqualified_render_preserves_independent_source_failure_and_replay(self):
        for name,status in [('malformed-render-null-source-only-absent','NC'),('malformed-render-list-source-and-render-absent','NC'),('malformed-render-scalar-source-only-present','NT'),('malformed-render-null-render-only-absent','NT')]:
            with self.subTest(case=name),tempfile.TemporaryDirectory() as td,patch.object(socket,'socket',side_effect=AssertionError('No collection')):
                root=Path(td);d=data(name);raw=build(root,d)
                self.assertEqual(tsep.read_json(root/'bundle/report.json')['results'][0]['status'],status)
                self.assertEqual((root/'bundle/input.json').read_bytes(),raw)
                repeated=replay.replay(root/'bundle',root/'replay');self.assertTrue(repeated['same_atomic_results']);self.assertTrue(repeated['same_gate'])
    def test_original_reviews_not_replaced(self):
        d=data('five-roles-contested-body');t=d['targets'][0];pieces=captures.pieces(t);self.assertIn('presence_plan_review',json.dumps(pieces['intent']));self.assertIn('presence_context_reviews',json.dumps(pieces['intent']))
        self.assertEqual(pieces['intent']['presence_context_reviews'],t['presence_context_reviews'])
    def test_corrupt_self_digests_refused_even_unplanned_or_without_plan(self):
        for kind in ('snapshot','support'):
            for unplanned in (False,True):
                for no_plan in (False,True):
                    with self.subTest(kind=kind,unplanned=unplanned,no_plan=no_plan),tempfile.TemporaryDirectory() as td:
                        root=Path(td);d=data();t=d['targets'][0];s=t['render']['states'][0]
                        if unplanned:s['id']='extra'
                        if no_plan:t['intent'].pop('critical_presence')
                        if kind=='snapshot':s['structured_dom']['snapshot_sha256']='0'*64
                        else:s['structured_dom']['acquisition']['support'][0]['sha256']='0'*64
                        with self.assertRaisesRegex(tsep.Invalid,'self-integrity'):build(root,d)
                        self.assertFalse((root/'bundle').exists());self.assertEqual(tsep.read_json(root/'input.json'),d)
    def test_provenance_mismatch_is_refusal_not_nt(self):
        for flag,access in [(True,'public'),(False,'synthetic'),('yes','synthetic')]:
            with self.subTest(flag=flag,access=access),tempfile.TemporaryDirectory() as td:
                d=data();d['targets'][0]['presence_synthetic']=flag;root=Path(td)
                with self.assertRaises(tsep.Invalid):build(root,d,access)
                self.assertFalse((root/'bundle').exists())
        with tempfile.TemporaryDirectory() as td:
            d=data();d['targets'][0]['presence_plan_review']['provenance']='human';root=Path(td)
            with self.assertRaises(tsep.Invalid):build(root,d)
            self.assertFalse((root/'bundle').exists())
    def test_no_review_generation_or_global_claim(self):
        d=data('five-roles-no-plan-review');before=copy.deepcopy(d);values=evaluate(d);self.assertEqual(values[0]['outcome'],'inconclusive');self.assertEqual(d,before)
        n=json.loads(values[0]['reason'][len(native.PREFIX):]);self.assertEqual(len(n['declared_roles']),5);self.assertIn('No execution',n['scope'])
    def test_identical_snapshot_not_interchangeable_review(self):
        result=evaluate(data('review-identical-dom-state-not-interchangeable'));self.assertEqual(result[1]['outcome'],'inconclusive')
        note=json.loads(result[1]['reason'][len(native.PREFIX):]);self.assertEqual(len(note['state_population']['shared_snapshots']),1)
    def test_independent_failure_survives_scope_unknown_and_contested(self):
        for name in ('five-roles-false-scope-native-failure','review-native-failure-contested-elsewhere','five-roles-unplanned-native-failure'):
            with self.subTest(case=name):self.assertEqual(evaluate(data(name))[1]['outcome'],'fail')
    def test_invalid_nested_containers_never_raise_or_pass(self):
        for field in ('intent','render','presence_context_reviews','http'):
            for bad in (None,[],42,'wrong'):
                with self.subTest(field=field,bad=bad):
                    t=data()['targets'][0];t[field]=bad
                    outcome,reason=native.assess(t,'TS25-A02');self.assertIn(outcome,('inconclusive','fail'))
        for field in ('items','states','roles','origins'):
            for bad in (None,42,'wrong'):
                with self.subTest(field=field,bad=bad):
                    t=data()['targets'][0];t['intent']['critical_presence'][field]=bad
                    outcome,reason=native.assess(t,'TS25-A01');self.assertEqual(outcome,'inconclusive')
    def test_maximum_population_and_missing_runtime(self):
        d=data('maximum-32-items-16-states');result=evaluate(d);self.assertEqual(result[0]['outcome'],'pass');n=json.loads(result[0]['reason'][len(native.PREFIX):]);self.assertEqual(len(n['items']),32);self.assertTrue(all(len(i['rendered']['states'])==16 for i in n['items']))
        with patch.dict(os.environ,{'TSEP_SOURCE_NODE':'/missing/explicit-node24'}):self.assertEqual(evaluate(data())[1]['outcome'],'inconclusive')
    def test_html_escapes_literal_values_and_preserves_all_items(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);build(root,data('five-roles-literal-html-escaped'));page=html.render(root/'bundle/report.json',language='en');self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;',page);self.assertNotIn('<script>alert(1)</script>',page)
    def test_cli_refusal_has_no_bundle(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);d=data();d['targets'][0]['render']['states'][0]['structured_dom']['snapshot_sha256']='0'*64;(root/'input.json').write_text(json.dumps(d))
            r=subprocess.run([sys.executable,'adapters/captures.py',str(root/'input.json'),'--output-dir',str(root/'bundle'),'--assessor','Synthetic','--label','Synthetic','--selection-method','Authored','--access','synthetic'],cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(r.returncode,64,r.stderr);self.assertFalse((root/'bundle').exists())
if __name__=='__main__':unittest.main()
