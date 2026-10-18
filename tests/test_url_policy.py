"""Frozen synthetic URL-policy cases and independent transport/preservation checks."""
import base64
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
from adapters import captures,replay
from conformance.evaluate import evaluate
from conformance import evidence_dossier as native,url_policy

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'tests/fixtures/url-policy-v1.json'
def cases():return json.loads(FIXTURE.read_bytes())['cases']
def data(cid='TS09',name='complete'):
    return copy.deepcopy(next(c['input'] for c in cases() if c['id']=='url-policy-v1-'+cid+'-'+name))
def rebind(target,cid):
    for review in target['evidence_checks'][cid]['reviews']:review['binding_sha256']=native.binding(target,cid)
def record_payload(record,value):
    raw=json.dumps(value,ensure_ascii=False).encode();record['native'].update(raw_base64=base64.b64encode(raw).decode(),sha256=hashlib.sha256(raw).hexdigest())

class URLPolicy(unittest.TestCase):
    def test_frozen_cases_offline_and_input_immutability(self):
        self.assertEqual(len(cases()),64)
        self.assertEqual(hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),FIXTURE.with_suffix('.sha256').read_text().strip())
        with patch.object(socket,'socket',side_effect=AssertionError('No network')):
            for case in cases():
                with self.subTest(case=case['id']):
                    original=copy.deepcopy(case['input']);actual=evaluate(case['input'])
                    self.assertEqual([x['outcome'] for x in actual],[x['outcome'] for x in case['expected']])
                    self.assertEqual(case['input'],original)

    def test_seventy_prior_rule_objects_and_versions_preserved(self):
        baseline=tsep.read_json(ROOT/'provenance/v030-draft1-rule-baseline.json')['rules'];self.assertEqual(len(baseline),70)
        protocol=tsep.read_json(tsep.PROTOCOL_PATH);seen={}
        for c in protocol['controls']:
            for r in c.get('rules',[]):
                if r['id'] in baseline:seen[r['id']]={'sha256':native.digest(r),'version':c['rule_version']}
        self.assertEqual(seen,baseline)

    def test_fifteen_c_nc_nt_bundles_export_and_exact_replay(self):
        for cid in url_policy.COUNTS:
            for name,status in [('complete','C'),('review-contradiction-A01','NC'),('missing-reviews','NT')]:
                with self.subTest(control=cid,case=name),tempfile.TemporaryDirectory() as folder:
                    root=Path(folder);source=root/'input.json';source.write_text(json.dumps(data(cid,name)))
                    original=source.read_bytes()
                    captures.build(source,root/'out',assessor='Fictional reviewer',label='SYNTHETIC '+cid,selection_method='Authored finite scope',access='synthetic')
                    report=tsep.read_json(root/'out/report.json')
                    self.assertEqual(report['results'][0]['status'],status);self.assertTrue(tsep.decision(report)['synthetic_evidence'])
                    self.assertEqual((root/'out/input.json').read_bytes(),original)
                    with patch.object(socket,'socket',side_effect=AssertionError('Offline replay')):
                        result=replay.replay(root/'out',root/'replayed')
                    self.assertTrue(result['same_atomic_results']);self.assertTrue(result['same_gate'])
                    self.assertEqual(source.read_bytes(),original)

    def test_partial_rules_never_close_control(self):
        for cid in ('TS11','TS19','TS20','TS38'):
            with self.subTest(control=cid),tempfile.TemporaryDirectory() as folder:
                root=Path(folder);value=data(cid);value['rules']=value['rules'][:1];source=root/'in.json';source.write_text(json.dumps(value))
                captures.build(source,root/'out',assessor='Fictional',label='Synthetic partial',selection_method='Authored',access='synthetic')
                self.assertEqual(tsep.read_json(root/'out/report.json')['results'][0]['status'],'NT')

    def test_corrupt_original_and_synthetic_relabeling_refused(self):
        for broken in ('hash','provenance'):
            with self.subTest(kind=broken),tempfile.TemporaryDirectory() as folder:
                root=Path(folder);value=data()
                if broken=='hash':value['targets'][0]['evidence_checks']['TS09']['records'][0]['native']['sha256']='0'*64
                source=root/'in.json';source.write_text(json.dumps(value))
                with self.assertRaises(tsep.Invalid):captures.build(source,root/'out',assessor='Fictional',label='Synthetic',selection_method='Authored',access='public' if broken=='provenance' else 'synthetic')
                self.assertFalse((root/'out').exists())

    def test_unbound_early_duplicate_or_unknown_review_cannot_pass(self):
        for mutation in ('binding','early','duplicate','unknown','oversize','real'):
            value=data();t=value['targets'][0];reviews=t['evidence_checks']['TS09']['reviews'];r=reviews[0]
            if mutation=='binding':r['binding_sha256']='0'*64
            elif mutation=='early':r['reviewed_at']='2026-10-14T09:00:00Z'
            elif mutation=='duplicate':reviews.append(copy.deepcopy(r))
            elif mutation=='unknown':r['judgment']='unknown'
            elif mutation=='oversize':r['reason']='é'*4097
            elif mutation=='real':r['provenance']='human'
            with self.subTest(mutation=mutation):self.assertEqual(evaluate(value)[0]['outcome'],'inconclusive')

    def test_contradictory_review_does_not_replace_missing_original(self):
        for cid in url_policy.COUNTS:
            value=data(cid,'review-contradiction-A01');t=value['targets'][0];d=t['evidence_checks'][cid];d['records']=[];d['documents']=[];rebind(t,cid)
            with self.subTest(control=cid):self.assertEqual(evaluate(value)[0]['outcome'],'inconclusive')

    def test_native_failure_survives_missing_review(self):
        for cid,name,index in [('TS09','wrong-mechanism',0),('TS11','wrong-canonical',1),('TS19','outside-finite-population',1),('TS20','bad-encoding',0),('TS38','sitemap-divergence',1)]:
            value=data(cid,name);value['targets'][0]['evidence_checks'][cid]['reviews']=[]
            with self.subTest(control=cid):self.assertEqual(evaluate(value)[index]['outcome'],'fail')

    def test_unsupported_or_malformed_containers_stay_unknown(self):
        for cid in url_policy.COUNTS:
            for key in ('records','documents','reviews'):
                for bad in (None,False,{},'pass'):
                    value=data(cid);value['targets'][0]['evidence_checks'][cid][key]=bad
                    with self.subTest(control=cid,key=key,bad=bad):self.assertEqual({r['outcome'] for r in evaluate(value)},{'inconclusive'})

    def test_original_json_duplicate_and_nonfinite_values_are_unknown(self):
        for raw in (b'{"format":"exclusion-register-v1","families":[],"families":[]}',b'{"format":"exclusion-register-v1","families":NaN}',b'[]',b'\xff'):
            value=data();t=value['targets'][0];r=t['evidence_checks']['TS09']['records'][0];r['native'].update(raw_base64=base64.b64encode(raw).decode(),sha256=hashlib.sha256(raw).hexdigest());rebind(t,'TS09')
            self.assertEqual(evaluate(value)[0]['outcome'],'inconclusive')

    def test_context_completeness_and_window_are_required(self):
        for field,value in [('context_id','other'),('observed_at','2026-10-14T08:00:00Z')]:
            payload=data();t=payload['targets'][0];t['evidence_checks']['TS09']['records'][0][field]=value;rebind(t,'TS09')
            self.assertEqual(evaluate(payload)[0]['outcome'],'inconclusive')
        payload=data();t=payload['targets'][0];t['evidence_checks']['TS09']['records'][0]['native']['complete']=False;rebind(t,'TS09')
        self.assertEqual(evaluate(payload)[0]['outcome'],'inconclusive')

    def test_changed_url_encoding_and_temporal_scope(self):
        for suffix in ('/%FF','/%00'):
            payload=data('TS20');t=payload['targets'][0];r=t['evidence_checks']['TS20']['records'][1];value=json.loads(base64.b64decode(r['native']['raw_base64']));value['rows'][0]['url']='https://synthetic.invalid'+suffix;record_payload(r,value);rebind(t,'TS20')
            self.assertEqual(evaluate(payload)[0]['outcome'],'inconclusive')
        payload=data('TS20');t=payload['targets'][0];t['evidence_checks']['TS20']['records'][0]['observed_at']=t['evidence_checks']['TS20']['records'][1]['observed_at'];rebind(t,'TS20')
        self.assertEqual(evaluate(payload)[1]['outcome'],'inconclusive')

    def test_limits_do_not_truncate_to_success(self):
        payload=data();t=payload['targets'][0];items=t['intent']['evidence_checks']['TS09']['items'];items[:]=[dict(items[0],id=str(n)) for n in range(33)];rebind(t,'TS09')
        self.assertEqual(evaluate(payload)[0]['outcome'],'inconclusive')
        payload=data();t=payload['targets'][0];r=t['evidence_checks']['TS09']['records'][0];raw=b' '*(native.LIMIT+1);r['native'].update(raw_base64=base64.b64encode(raw).decode(),sha256=hashlib.sha256(raw).hexdigest());rebind(t,'TS09')
        self.assertEqual(evaluate(payload)[0]['outcome'],'inconclusive')

    def test_original_binary_http_is_supported_without_rewriting(self):
        for cid in ('TS11','TS38'):
            value=data(cid);t=value['targets'][0]
            for document in t['evidence_checks'][cid]['documents']:
                for hop in document['http']:
                    for field in ('request','response'):
                        raw=hop[field].encode('utf-8')
                        hop[field]={'base64':base64.b64encode(raw).decode(),'sha256':hashlib.sha256(raw).hexdigest()}
            rebind(t,cid)
            with self.subTest(control=cid):self.assertEqual([r['outcome'] for r in evaluate(value)],['pass','pass'])

    def test_source_dependencies_are_bound(self):
        sources=captures.source_files()
        self.assertIn('conformance/evidence_dossier.py',sources);self.assertIn('conformance/url_policy.py',sources)

if __name__=='__main__':unittest.main()
