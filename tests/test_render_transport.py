from tests.lot1_history import controls_before_lot1
"""Synthetic render/transport contradictions, offline replay and preservation."""
import base64,copy,hashlib,json,os,socket,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import tsep
from adapters import captures,replay
from conformance.evaluate import evaluate
from conformance.evidence_dossier import binding,digest
from conformance import render_transport as reader
ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'tests/fixtures/render-transport-v1.json'
def cases():return json.loads(FIXTURE.read_bytes())['cases']
def data(cid='TS26',name='complete'):return copy.deepcopy(next(c['input'] for c in cases() if c['id']=='render-transport-v1-'+cid+'-'+name))
def rebind(t,c):
    for r in t['evidence_checks'][c]['reviews']:r['binding_sha256']=binding(t,c)
def change(value,c,identity,fn):
    t=value['targets'][0];r=next(r for r in t['evidence_checks'][c]['records'] if r['id']==identity);v=json.loads(base64.b64decode(r['native']['raw_base64']));fn(v);raw=json.dumps(v,sort_keys=True,separators=(',',':')).encode();r['native'].update(raw_base64=base64.b64encode(raw).decode(),sha256=hashlib.sha256(raw).hexdigest());rebind(t,c)
class RenderTransport(unittest.TestCase):
    def test_frozen_cases_offline_without_input_mutation(self):
        self.assertEqual(hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),FIXTURE.with_suffix('.sha256').read_text().strip());self.assertEqual(len(cases()),71)
        with patch.object(socket,'socket',side_effect=AssertionError('No Python network')):
            for case in cases():
                with self.subTest(case=case['id']):
                    before=copy.deepcopy(case['input']);actual=evaluate(case['input']);self.assertEqual([r['outcome'] for r in actual],[r['outcome'] for r in case['expected']]);self.assertEqual(case['input'],before)

    def test_prior_eighty_five_rules_and_versions_preserved(self):
        baseline=tsep.read_json(ROOT/'provenance/v030-draft3-rule-baseline.json')['rules'];self.assertEqual(len(baseline),85)
        actual={r['id']:{'sha256':digest(r),'version':c['rule_version']} for c in controls_before_lot1() for r in c.get('rules',[]) if r['id'] in baseline};self.assertEqual(actual,baseline)
        p=tsep.read_json(tsep.PROTOCOL_PATH);self.assertEqual(len([c for c in p['controls'] if c.get('rules')]),44);self.assertEqual(sum(len(c['rules']) for c in p['controls']),98)

    def test_c_nc_nt_bundles_and_offline_replay(self):
        for cid in reader.COUNTS:
            for name,status in [('complete','C'),('review-contradiction-A01','NC'),('missing-reviews','NT')]:
                with self.subTest(cid=cid,case=name),tempfile.TemporaryDirectory() as folder:
                    root=Path(folder);source=root/'in.json';source.write_text(json.dumps(data(cid,name)));raw=source.read_bytes()
                    captures.build(source,root/'bundle',assessor='Fictional',label='SYNTHETIC '+cid,selection_method='Authored finite population',access='synthetic')
                    self.assertEqual(tsep.read_json(root/'bundle/report.json')['results'][0]['status'],status);self.assertTrue(tsep.decision(tsep.read_json(root/'bundle/report.json'))['synthetic_evidence']);self.assertEqual((root/'bundle/input.json').read_bytes(),raw)
                    with patch.object(socket,'socket',side_effect=AssertionError('No acquisition')):result=replay.replay(root/'bundle',root/'replay')
                    self.assertTrue(result['same_atomic_results']);self.assertTrue(result['same_gate'])

    def test_partial_atomic_population_never_whole_control_c(self):
        for cid in reader.COUNTS:
            with tempfile.TemporaryDirectory() as folder:
                root=Path(folder);value=data(cid);value['rules']=value['rules'][:1];source=root/'in.json';source.write_text(json.dumps(value));captures.build(source,root/'out',assessor='Fictional',label='SYNTHETIC',selection_method='Partial authored rules',access='synthetic');self.assertEqual(tsep.read_json(root/'out/report.json')['results'][0]['status'],'NT')

    def test_synthetic_cannot_be_relabelled_public_and_original_tamper_refused(self):
        for cid in reader.COUNTS:
            value=data(cid)
            if value['targets'][0]['evidence_checks'][cid]['records']:
                value['targets'][0]['evidence_checks'][cid]['records'][0]['native']['sha256']='0'*64
                with self.assertRaises(tsep.Invalid):evaluate(value)
            with tempfile.TemporaryDirectory() as folder:
                root=Path(folder);source=root/'in.json';source.write_text(json.dumps(data(cid)))
                with self.assertRaises(tsep.Invalid):captures.build(source,root/'out',assessor='Fictional',label='Cannot relabel',selection_method='Authored',access='public')
                self.assertFalse((root/'out').exists())

    def test_reviews_cannot_replace_missing_native_evidence(self):
        for cid in reader.COUNTS:
            value=data(cid,'review-contradiction-A01');t=value['targets'][0];t['evidence_checks'][cid]['records']=[];t['evidence_checks'][cid]['documents']=[];rebind(t,cid)
            self.assertEqual(evaluate(value)[0]['outcome'],'inconclusive')

    def test_independent_failures_survive_missing_reviews(self):
        for cid,name,index in [('TS26','resource-404-missing-robots',0),('TS27','wrong-route',0),('TS28','wrong-language',0),('TS29','scripts-essential-absent',0),('TS30','title-contradiction',0),('TS37','mixed-request',2)]:
            value=data(cid,name);value['targets'][0]['evidence_checks'][cid]['reviews']=[]
            with self.subTest(cid=cid):self.assertEqual(evaluate(value)[index]['outcome'],'fail')

    def test_missing_optional_runtimes_produce_nt(self):
        with patch.dict(os.environ,{'TSEP_SOURCE_NODE':'/absent/node'}):self.assertEqual(evaluate(data('TS28'))[0]['outcome'],'inconclusive')
        with patch.dict(os.environ,{'TSEP_OPENSSL':'/absent/openssl'}):self.assertEqual(evaluate(data('TS37'))[0]['outcome'],'inconclusive')

    def test_certificate_expiry_checked_at_supplied_capture_time(self):
        value=data('TS37');t=value['targets'][0];t['intent']['declared_at']='2028-01-01T09:00:00Z';t['observed_at']='2028-01-01T12:00:00Z'
        for key in ('records','documents'):
            for r in t['evidence_checks']['TS37'][key]:r['observed_at']='2028-01-01T10:00:00Z'
        for r in t['evidence_checks']['TS37']['reviews']:r['reviewed_at']='2028-01-01T11:00:00Z'
        change(value,'TS37','certificates',lambda p:p.update(captured_at='2028-01-01T10:00:00Z'));self.assertEqual(evaluate(value)[0]['outcome'],'fail')

    def test_certificate_verification_has_no_implicit_store_or_fetch_flag(self):
        value=data('TS37');calls=[];original=reader.subprocess.run
        def tracked(args,**kwargs):calls.append((args,kwargs));return original(args,**kwargs)
        with patch.object(reader.subprocess,'run',side_effect=tracked):self.assertEqual(evaluate(value)[0]['outcome'],'pass')
        args,kwargs=next((a,k) for a,k in calls if a[1]=='verify');self.assertIn('-no-CApath',args);self.assertIn('-no-CAstore',args);self.assertIn('-CAfile',args);self.assertIn('-attime',args);self.assertNotIn('-crl_download',args);self.assertNotIn('-no_check_time',args);self.assertNotIn('-ignore_critical',args);self.assertIn('OPENSSL_CONF',kwargs['env'])

    def test_browser_binding_chronology_and_incomplete_serialization(self):
        for mutation in (lambda p:p.update(captured_at='2026-10-15T10:00:00Z'),lambda p:p.update(complete=False),lambda p:p.update(failures=['timeout'])):
            value=data('TS28');change(value,'TS28','normal',mutation);self.assertEqual(evaluate(value)[0]['outcome'],'inconclusive')

    def test_csp_unsupported_tokens_nt_and_independent_denial(self):
        value=data();t=value['targets'][0];h=t['evidence_checks']['TS26']['documents'][0]['http'][0];h['response']=h['response'].replace("default-src 'self'","script-src 'nonce-fictional'");rebind(t,'TS26');self.assertEqual(evaluate(value)[0]['outcome'],'inconclusive')
        h['response']=h['response'].replace("script-src 'nonce-fictional'","default-src 'none'\r\nContent-Security-Policy: script-src 'nonce-fictional'");rebind(t,'TS26');self.assertEqual(evaluate(value)[0]['outcome'],'fail')

    def test_unknown_csp_first_and_meta_do_not_hide_header_denial(self):
        for policy in ("script-src 'nonce-fictional'\r\nContent-Security-Policy: default-src 'none'", "default-src 'none'"):
            value=data();t=value['targets'][0];h=t['evidence_checks']['TS26']['documents'][0]['http'][0];h['response']=h['response'].replace("default-src 'self'",policy)
            if 'nonce' not in policy:
                head,body=h['response'].split('\r\n\r\n',1);body=body.replace('</head>','<meta http-equiv="content-security-policy" content="script-src https:"></head>');import re;head=re.sub('Content-Length: [0-9]+','Content-Length: '+str(len(body.encode())),head);h['response']=head+'\r\n\r\n'+body
            rebind(t,'TS26');self.assertEqual(evaluate(value)[0]['outcome'],'fail')

    def test_nested_hidden_text_never_proves_visible_essential_content(self):
        for markup in ('<span hidden>{}</span>','<span style="display:none">{}</span>','<span aria-hidden="true">{}</span>'):
            value=data('TS29');change(value,'TS29','scripts',lambda p:p.update(html=p['html'].replace('Fictional essential content',markup.format('Fictional essential content'))))
            self.assertEqual([r['outcome'] for r in evaluate(value)],['inconclusive','pass'])
        value=data('TS28');change(value,'TS28','normal',lambda p:p.update(html=p['html'].replace('<h1 id="heading">Fictional page</h1>','<h1 id="heading"><span hidden>Fictional page</span></h1>')));self.assertEqual([r['outcome'] for r in evaluate(value)],['inconclusive','inconclusive'])

    def test_native_route_error_and_structure_conflict_survive_missing_dom(self):
        value=data('TS27');t=value['targets'][0];h=t['evidence_checks']['TS27']['documents'][0]['http'][0];h['response']=h['response'].replace('200 Synthetic','500 Synthetic',1);t['evidence_checks']['TS27']['records']=[];t['evidence_checks']['TS27']['reviews']=[];self.assertEqual([r['outcome'] for r in evaluate(value)],['fail','fail'])
        value=data('TS28');t=value['targets'][0];h=t['evidence_checks']['TS28']['documents'][0]['http'][0];h['response']=h['response'].replace('lang="fr"','lang="en"');t['evidence_checks']['TS28']['records']=[];t['evidence_checks']['TS28']['reviews']=[];self.assertEqual([r['outcome'] for r in evaluate(value)],['fail','fail'])

    def test_prior_tested_fallback_is_separate_from_missing_evidence(self):
        value=data('TS29','scripts-essential-absent');t=value['targets'][0];item=t['intent']['evidence_checks']['TS29']['items'][0];item['fallback']={'reason':'Synthetic selected route fallback','content':[{'id':'next','text':'Next','href':'https://synthetic.invalid/next'}]};rebind(t,'TS29');self.assertEqual(evaluate(value)[0]['outcome'],'pass')
        change(value,'TS29','scripts',lambda p:p.update(complete=False));self.assertEqual(evaluate(value)[0]['outcome'],'inconclusive')

    def test_intentional_corpus_duplicates_need_every_field_decision(self):
        value=data('TS30','corpus-duplicates-undecided');t=value['targets'][0];item=t['intent']['evidence_checks']['TS30']['items'][0];item['duplicate_decisions']=[{'field':k,'urls':[p['url'] for p in item['pages']],'value':v,'reason':'Fictional reviewed deliberate duplicate','decision':'intentional'} for k,v in item['pages'][0]['metadata'].items()];rebind(t,'TS30');self.assertEqual(evaluate(value)[0]['outcome'],'pass')
        item['duplicate_decisions'].pop();rebind(t,'TS30');self.assertEqual(evaluate(value)[0]['outcome'],'fail')

    def test_hsts_explicitly_disabled_and_preload_not_required(self):
        value=data('TS37');t=value['targets'][0];policy=t['intent']['evidence_checks']['TS37']['items'][0]['hsts'];policy.update(enabled=False,max_age=0,include_subdomains=False);change(value,'TS37','config',lambda p:p.update(hsts=policy));h=t['evidence_checks']['TS37']['documents'][0]['http'][0];h['response']=h['response'].replace('max-age=3600; includeSubDomains','max-age=0');rebind(t,'TS37');self.assertEqual(evaluate(value)[1]['outcome'],'pass')

    def test_binary_http_bodies_and_source_identity_preserved(self):
        value=data('TS30');t=value['targets'][0]
        for doc in t['evidence_checks']['TS30']['documents']:
            for hop in doc['http']:
                for field in ('request','response'):
                    raw=hop[field].encode();hop[field]={'base64':base64.b64encode(raw).decode(),'sha256':hashlib.sha256(raw).hexdigest()}
        rebind(t,'TS30');self.assertEqual([r['outcome'] for r in evaluate(value)],['pass','pass'])

if __name__=='__main__':unittest.main()
