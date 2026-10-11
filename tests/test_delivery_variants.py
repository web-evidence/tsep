"""Delivery observations, partial evidence and conservative Vary boundaries."""
import copy
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from experiments import delivery_variants as dv

ROOT=Path(__file__).resolve().parents[1]
FIXTURES=('delivery-variants-v1.json','delivery-variants-boundaries-v1.json')

def cases():
    result=[]
    for name in FIXTURES:
        p=ROOT/'tests/fixtures'/name;raw=p.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=p.with_suffix('.sha256').read_text().strip():raise ValueError('Frozen delivery cases changed')
        result.extend(json.loads(raw)['cases'])
    return result


class DeliveryVariants(unittest.TestCase):
    def data(self,name='identical'):return copy.deepcopy(next(c['input'] for c in cases() if c['id']==name))

    def test_all_frozen_expectations_without_network_processes_or_native_verdicts(self):
        fixture=cases();self.assertEqual(len(fixture),49)
        with patch.object(socket,'socket',side_effect=AssertionError('No HTTP')),patch.object(socket,'getaddrinfo',side_effect=AssertionError('No DNS')),patch.object(subprocess,'Popen',side_effect=AssertionError('No process')),patch('conformance.evaluate.evaluate',side_effect=AssertionError('No normative outcomes')):
            for c in fixture:
                with self.subTest(case=c['id']):
                    if 'expected_error' in c:
                        with self.assertRaisesRegex(ValueError,c['expected_error']):dv.observe(c['input'])
                        continue
                    result=dv.observe(c['input'])
                    self.assertEqual(result['normative_effect'],'none')
                    for path,want in c['expected'].items():
                        got=result
                        for k in path.split('.'):got=got[int(k)] if isinstance(got,list) else got[k]
                        self.assertEqual(got,want,path)

    def test_normative_rule_and_corpus_inventory_unchanged(self):
        from conformance.evaluate import RULES
        self.assertFalse(any(r.startswith('TS39-') for r in RULES))
        p=json.loads((ROOT/'conformance/cases.json').read_text());self.assertEqual(len(p['cases']),1104)

    def test_same_observations_not_same_authenticity_or_semantics(self):
        r=dv.observe(self.data('context-claims-unverified'))
        self.assertEqual(r['pairs'][0]['body'],'equal');self.assertEqual(r['operator_access'],'not-established')
        self.assertEqual(r['cells'][1]['context_claims']['region'],'AU')
        self.assertEqual(r['cells'][1]['context_authentication'],'not-established')
        self.assertNotIn('outcome',r);self.assertNotIn('control_status',r)

    def test_missing_observation_remains_in_declared_order(self):
        r=dv.observe(self.data('missing-cell'))
        self.assertEqual([c['id'] for c in r['cells']],['a','b']);self.assertFalse(r['cells'][1]['observed'])
        self.assertFalse(r['pairs'][0]['all_planned_observations_complete'])

    def test_incomplete_body_keeps_independent_header_contradiction(self):
        data=self.data('incomplete-body-keeps-headers')
        data['observations'][1]['http'][0]['response']=data['observations'][1]['http'][0]['response'].replace('Vary: Accept-Language','Vary: Accept-Language\r\nX-Robots-Tag: noindex')
        r=dv.observe(data);self.assertEqual(r['pairs'][0]['header_changes']['x-robots-tag'],'different')
        self.assertEqual(r['pairs'][0]['body'],'unavailable');self.assertFalse(r['cells'][1]['hops'][0]['body_complete'])

    def test_vary_matching_uses_stored_side_and_is_directional(self):
        data=self.data('vary-left-only');data['plan']['pairs'].append({'id':'ba','left':'b','right':'a'})
        r=dv.observe(data);self.assertEqual(r['pairs'][0]['vary']['match'],'nonmatching');self.assertEqual(r['pairs'][1]['vary']['match'],'unconstrained')

    def test_wildcard_mixed_members_and_empty_elements_are_explicit(self):
        v=dv.vary({'vary':[' , Accept-Language, *', 'accept-language,']})
        self.assertTrue(v['valid']);self.assertTrue(v['wildcard']);self.assertEqual(v['fields'],['accept-language'])
        self.assertFalse(dv.vary({'vary':[','.join(['a']*129)]})['valid'])

    def test_absence_is_distinct_from_present_empty(self):
        self.assertEqual(dv.field_match('accept-language',None,['']),'different')
        self.assertEqual(dv.field_match('x-custom',[''],['']),'equal')
        self.assertEqual(dv.field_match('x-custom',['a, b'],['a','b']),'undetermined')

    def test_malformed_rows_stay_unknown_and_malformed_plans_refuse(self):
        for value in (None,True,{},'bad',[],-1):
            data=self.data();data['observations'][1]['http']=[value]
            self.assertFalse(dv.observe(data)['cells'][1]['complete'])
            for field in ('plan','observations'):
                data=self.data();data[field]=value
                if field=='observations' and value==[]:
                    self.assertTrue(all(not c['observed'] for c in dv.observe(data)['cells']))
                else:
                    with self.assertRaises(ValueError):dv.observe(data)

    def test_future_out_of_order_hops_and_redirect_loops_not_closed(self):
        data=self.data('complete-redirect');data['observations'][1]['http'][1]['sent_at']='2026-10-11T09:00:01Z'
        r=dv.observe(data);self.assertFalse(r['cells'][1]['complete']);self.assertIsNone(r['cells'][1]['terminal'])
        data=self.data('complete-redirect');data['observations'][1]['http'][0]['response']=data['observations'][1]['http'][0]['response'].replace('Location: /fr','Location: /page')
        data['observations'][1]['http'][1]=copy.deepcopy(data['observations'][1]['http'][0])
        self.assertFalse(dv.observe(data)['cells'][1]['complete'])

    def test_input_bounds_and_blank_client_refuse(self):
        data=self.data();data['plan']['cells']*=40
        with self.assertRaisesRegex(ValueError,'Cell population'):dv.observe(data)
        data=self.data();data['plan']['cells'][0]['user_agent']='   '
        with self.assertRaisesRegex(ValueError,'User-Agent'):dv.observe(data)
        data=self.data();data['expected']={'outcome':'pass'}
        with self.assertRaisesRegex(ValueError,'expected outcomes'):dv.observe(data)

    def test_raw_input_immutable_and_fingerprints_change_with_context(self):
        data=self.data();before=copy.deepcopy(data);first=dv.observe(data);self.assertEqual(data,before)
        data['plan']['cells'][0]['context_claims']['region']='US';second=dv.observe(data)
        self.assertNotEqual(first['input_sha256'],second['input_sha256'])
        self.assertEqual(first['pairs'][0]['body'],second['pairs'][0]['body'])

    def test_binary_response_fingerprint_and_decoded_comparison(self):
        data=self.data('gzip-same-content');r=dv.observe(data)
        a,b=[c['hops'][0] for c in r['cells']]
        self.assertNotEqual(a['response_sha256'],b['response_sha256']);self.assertEqual(a['body_sha256'],b['body_sha256'])
        data['observations'][1]['http'][0]['response']['sha256']='0'*64
        r=dv.observe(data);self.assertFalse(r['cells'][1]['complete']);self.assertEqual(r['pairs'][0]['body'],'unavailable')

    def test_cli_exclusive_output_and_exact_input_file_identity(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'in.json';out=root/'out.json';raw=json.dumps(self.data(),indent=4).encode();source.write_bytes(raw)
            cmd=[sys.executable,str(ROOT/'experiments/delivery_variants.py'),str(source),'--output',str(out)]
            one=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(one.returncode,0,one.stderr)
            original=out.read_bytes();self.assertEqual(json.loads(original)['input_file_sha256'],hashlib.sha256(raw).hexdigest())
            two=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(two.returncode,64);self.assertEqual(out.read_bytes(),original)

    def test_runtime_result_does_not_read_expected_fixture_values(self):
        original=dv.observe(self.data('language-diff-same-body'))
        with patch.object(Path,'read_bytes',side_effect=AssertionError('No fixture access')):
            # Source identity reads files through the loaded-source helper, not this method.
            with patch.object(dv,'identity',return_value=original['source_files']):result=dv.observe(self.data_from(original))
        self.assertEqual(result['pairs'][0]['vary']['match'],'nonmatching')

    @staticmethod
    def data_from(result):
        # Fully independent handcrafted input, not an expected-outcome report.
        cells=[];obs=[]
        for cid,language in [('a','fr'),('b','en')]:
            cells.append({'id':cid,'url':'https://example.test/page','user_agent':'ExampleTest/1','request_fields':{'accept-language':[language]},'context_claims':{}})
            obs.append({'cell_id':cid,'http':[{'url':'https://example.test/page','complete':True,'sent_at':'2026-10-11T09:00:01Z','received_at':'2026-10-11T09:00:02Z','request':'GET /page HTTP/1.1\r\nHost: example.test\r\nUser-Agent: ExampleTest/1\r\nAccept-Language: '+language+'\r\n\r\n','response':'HTTP/1.1 200 OK\r\nContent-Length: 1\r\nVary: Accept-Language\r\n\r\nx'}]})
        return {'kind':'delivery-variants-input','version':'1','synthetic':True,'plan':{'declared_at':'2026-10-11T08:59:00Z','window_start':'2026-10-11T09:00:00Z','window_end':'2026-10-11T09:01:00Z','cells':cells,'pairs':[{'id':'ab','left':'a','right':'b'}]},'observations':obs}


if __name__=='__main__':unittest.main()
