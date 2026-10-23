from tests.lot1_history import controls_before_lot1
"""Bounded indexing/locale counterexamples, evidence boundaries and preservation."""
import base64,copy,hashlib,json,os,socket,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import tsep
from adapters import captures,replay
from conformance.evaluate import evaluate
from conformance.evidence_dossier import binding,digest
from conformance import indexing_locale as reader
from conformance.corpus import expand
ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'tests/fixtures/indexing-locale-v1.json'
def cases():return json.loads(FIXTURE.read_bytes())['cases']
def data(cid='TS21',name='complete'):return copy.deepcopy(next(c['input'] for c in cases() if c['id']=='indexing-locale-v1-'+cid+'-'+name))
def rebind(t,c):
    for r in t['evidence_checks'][c]['reviews']:r['binding_sha256']=binding(t,c)
class IndexingLocale(unittest.TestCase):
    def test_frozen_cases_offline_and_unchanged_inputs(self):
        self.assertEqual(hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),FIXTURE.with_suffix('.sha256').read_text().strip());self.assertEqual(len(cases()),53)
        with patch.object(socket,'socket',side_effect=AssertionError('Offline only')):
            for case in cases():
                with self.subTest(case=case['id']):
                    before=copy.deepcopy(case['input']);actual=evaluate(case['input'])
                    self.assertEqual([r['outcome'] for r in actual],[r['outcome'] for r in case['expected']]);self.assertEqual(case['input'],before)

    def test_all_seventy_nine_prior_rules_and_versions_preserved(self):
        baseline=tsep.read_json(ROOT/'provenance/v030-draft2-rule-baseline.json')['rules'];self.assertEqual(len(baseline),79)
        seen={r['id']:{'sha256':digest(r),'version':c['rule_version']} for c in controls_before_lot1() for r in c.get('rules',[]) if r['id'] in baseline};self.assertEqual(seen,baseline)

    def test_c_nc_nt_bundles_and_offline_replay(self):
        for cid in reader.COUNTS:
            for name,status in [('complete','C'),('review-contradiction-A01','NC'),('missing-reviews','NT')]:
                with self.subTest(cid=cid,case=name),tempfile.TemporaryDirectory() as folder:
                    root=Path(folder);source=root/'in.json';source.write_text(json.dumps(data(cid,name)));raw=source.read_bytes()
                    captures.build(source,root/'out',assessor='Fictional',label='SYNTHETIC '+cid,selection_method='Authored finite population',access='synthetic')
                    report=tsep.read_json(root/'out/report.json');self.assertEqual(report['results'][0]['status'],status);self.assertTrue(tsep.decision(report)['synthetic_evidence']);self.assertEqual((root/'out/input.json').read_bytes(),raw)
                    with patch.object(socket,'socket',side_effect=AssertionError('No collection')):result=replay.replay(root/'out',root/'replay')
                    self.assertTrue(result['same_atomic_results']);self.assertTrue(result['same_gate'])

    def test_single_html_method_needs_no_invented_sitemap(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'in.json';source.write_text(json.dumps(data('TS40','single-method-valid')))
            captures.build(source,root/'out',assessor='Fictional',label='SYNTHETIC HTML only',selection_method='Declared single method',access='synthetic')
            report=tsep.read_json(root/'out/report.json');self.assertEqual(report['results'][0]['status'],'C')
            self.assertNotIn('sitemap',{a['kind'] for a in report['artifacts']})

    def test_partial_rules_and_empty_population_never_produce_c(self):
        for cid in reader.COUNTS:
            with tempfile.TemporaryDirectory() as folder:
                root=Path(folder);value=data(cid);value['rules']=value['rules'][:1];source=root/'in.json';source.write_text(json.dumps(value))
                captures.build(source,root/'out',assessor='Fictional',label='SYNTHETIC partial',selection_method='Authored',access='synthetic')
                self.assertEqual(tsep.read_json(root/'out/report.json')['results'][0]['status'],'NT')

    def test_integrity_and_synthetic_provenance_refusals(self):
        for cid in reader.COUNTS:
            value=data(cid);value['targets'][0]['evidence_checks'][cid]['records'][0]['native']['sha256']='0'*64
            with self.assertRaises(tsep.Invalid):evaluate(value)
        for cid in reader.COUNTS:
            with tempfile.TemporaryDirectory() as folder:
                root=Path(folder);source=root/'in.json';source.write_text(json.dumps(data(cid)))
                with self.assertRaises(tsep.Invalid):captures.build(source,root/'out',assessor='Fictional',label='Cannot relabel',selection_method='Authored',access='public')
                self.assertFalse((root/'out').exists())

    def test_no_node_runtime_is_unknown_not_failure_or_pass(self):
        with patch.dict(os.environ,{'TSEP_SOURCE_NODE':'/does/not/exist/node'}):
            values=evaluate(data('TS40'))
            self.assertEqual([r['outcome'] for r in values],['inconclusive','inconclusive'])

    def test_source_failure_survives_absent_reviews_and_other_methods(self):
        for cid,name,index in [('TS21','request-contradiction-and-missing-logs',0),('TS22','destination-noindex',1),('TS40','conflict-and-missing-sitemap',1)]:
            value=data(cid,name);value['targets'][0]['evidence_checks'][cid]['reviews']=[]
            with self.subTest(cid=cid):self.assertEqual(evaluate(value)[index]['outcome'],'fail')

    def test_missing_originals_cannot_be_replaced_by_contradictory_review(self):
        for cid in reader.COUNTS:
            value=data(cid,'review-contradiction-A01');t=value['targets'][0];t['evidence_checks'][cid]['records']=[];t['evidence_checks'][cid]['documents']=[];rebind(t,cid)
            self.assertEqual(evaluate(value)[0]['outcome'],'inconclusive')

    def test_review_binding_dates_and_duplicate_identity_are_required(self):
        for mutation in ('binding','early','duplicate'):
            value=data();t=value['targets'][0];reviews=t['evidence_checks']['TS21']['reviews']
            if mutation=='binding':reviews[0]['binding_sha256']='0'*64
            elif mutation=='early':reviews[0]['reviewed_at']='2026-10-14T09:00:00Z'
            else:reviews.append(copy.deepcopy(reviews[0]))
            self.assertEqual(evaluate(value)[0]['outcome'],'inconclusive')

    def test_registered_codes_do_not_silently_migrate_or_guess(self):
        for code,outcome in [('fr-FR','pass'),('zh-Hant-TW','pass'),('EN-latn-us','pass'),('x-default','pass'),('en-UK','fail'),('es-419','fail'),('zz-FR','fail'),('iw-IL','inconclusive'),('fr-CQ','inconclusive'),('en-US-u-ca','inconclusive')]:
            with self.subTest(code=code):self.assertEqual(reader.registry_code(code)[0],outcome)
        sources=captures.source_files();self.assertIn('conformance/data/locale-code-facts-v1.json',sources)

    def test_google_robots_profile_is_explicit(self):
        value=data('TS22');t=value['targets'][0]
        for d in t['intent']['evidence_checks']['TS22']['items'][0]['destinations']:d['robots_profile']='rfc9309-bounded-v1'
        rebind(t,'TS22');self.assertEqual(evaluate(value)[1]['outcome'],'inconclusive')

    def test_24_explicit_extensions_bound_and_existing_guards(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'tests/fixtures').mkdir(parents=True);refs=[];files=[]
            for n in range(25):
                name='tests/fixtures/extra-'+str(n)+'.json';p=root/name;p.write_text(json.dumps({'synthetic':True,'cases':[{'id':str(n)}]}));files.append(name);refs.append({'path':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
            (root/'release-files.json').write_text(json.dumps({'files':files}))
            self.assertEqual(len(expand({'cases':[],'additional_case_files':refs[:24]},root=root)['cases']),24)
            with self.assertRaisesRegex(tsep.Invalid,'Excessive'):expand({'cases':[],'additional_case_files':refs},root=root)

    def test_native_binary_http_and_xml_dtd_are_not_reinterpreted(self):
        value=data('TS22');t=value['targets'][0]
        for doc in t['evidence_checks']['TS22']['documents']:
            for hop in doc['http']:
                for field in ('request','response'):
                    raw=hop[field].encode();hop[field]={'base64':base64.b64encode(raw).decode(),'sha256':hashlib.sha256(raw).hexdigest()}
        rebind(t,'TS22');self.assertEqual([r['outcome'] for r in evaluate(value)],['pass','pass'])
        value=data('TS40');t=value['targets'][0];r=t['evidence_checks']['TS40']['records'][0];raw=b'<!DOCTYPE urlset SYSTEM "https://never-fetch.invalid/dtd">'+base64.b64decode(r['native']['raw_base64']);r['native'].update(raw_base64=base64.b64encode(raw).decode(),sha256=hashlib.sha256(raw).hexdigest());rebind(t,'TS40')
        with patch.object(socket,'socket',side_effect=AssertionError('Never fetch DTD')):self.assertEqual([r['outcome'] for r in evaluate(value)],['inconclusive','inconclusive'])

if __name__=='__main__':unittest.main()
