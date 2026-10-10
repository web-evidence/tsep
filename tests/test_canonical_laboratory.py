"""Synthetic authored DOM fixtures plus actual loopback HTTP. No browser execution."""
import copy
import json
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from urllib.request import Request, urlopen

import tsep
from collectors import ts01
from examples import canonical_laboratory as lab


def authored_observations(server, registration, tasks):
    """Author synthetic loaded states explicitly; never execute JS or call them real."""
    result={};agent='AuthoredFixture/1'
    for task in tasks:
        with urlopen(Request(task['url'],headers={'User-Agent':agent}),timeout=3) as response:
            dom=response.read().decode('utf-8')
        record=registration['scenarios'][task['case']]
        if task['case']=='js-canonical' and task['role']=='variant':
            dom=dom.replace('<link rel="canonical" href="'+record['urls']['product']+'">',
                            '<link rel="canonical" href="'+record['urls']['variant']+'">')
        event=ts01.now()
        for key,value in [('state','loaded'),('js','executed'),('agent',agent),('event-time',event),('document-url',task['url'])]:
            old='waiting' if key=='state' else 'pending'
            dom=dom.replace('<span id="'+key+'">'+old+'</span>','<span id="'+key+'">'+value+'</span>')
        result[task['id']]={'url':task['url'],'dom':dom,'state':'loaded','js':'executed','agent':agent,'context':task['context_id'],
                           'errors':[],'readyState':'complete','observed_at':ts01.now(),'devLogs':[],
                           'browser':{'name':'Authored synthetic fixture, no browser','version':'1','user_agent':agent}}
    return result


class CanonicalLaboratory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.base=Path(cls.temp.name)
        cls.source=cls.base/'source'
        server,thread,registration,tasks=lab.start(cls.source)
        try:observations=authored_observations(server,registration,tasks)
        finally:lab.stop(server,thread)
        ts01.save(cls.base/'observations.json',observations)
        cls.original=cls.base/'delivery'
        cls.result=lab.finish(cls.source,cls.base/'observations.json',cls.original,'authored-fixture')

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory();self.root=Path(self.temporary.name)/'delivery'
        shutil.copytree(self.original,self.root)

    def tearDown(self):self.temporary.cleanup()

    def offline(self):
        with patch.object(socket,'socket',side_effect=AssertionError('Network forbidden')), \
             patch.object(socket,'getaddrinfo',side_effect=AssertionError('DNS forbidden')), \
             patch.object(subprocess,'run',side_effect=AssertionError('Subprocess forbidden')):
            return lab.replay(self.root)

    def change(self,name,fn):
        p=self.root/name;d=tsep.read_json(p);fn(d);p.write_text(json.dumps(d,ensure_ascii=False)+'\n')

    def rehash(self,root=None):
        root=root or self.root;names=[line.split('  ',1)[1] for line in (root/'SHA256SUMS').read_text().splitlines()]
        (root/'SHA256SUMS').unlink();ts01.manifest(root,names)

    def test_twelve_prefrozen_cases_match_and_remain_nc_or_nt(self):
        self.assertEqual(len(self.result['cases']),12)
        self.assertTrue(self.result['all_expectations_matched'])
        self.assertEqual(self.result['browser_evidence_origin'],'authored-fixture')
        self.assertEqual(self.result['counts'],{'source_requests':51,'browser_requests':35,'total_requests':86})
        for row in self.result['cases']:
            self.assertEqual(row['actual'],row['expected'],row['id']);self.assertIn(row['status'],('NC','NT'))
            data=tsep.read_json(self.root/row['id']/'input.json')
            self.assertNotIn('expected',data);self.assertNotIn('content_review',data['targets'][0])
            self.assertFalse(any('exemption_review' in doc for doc in data['targets'][0]['documents']))

    def test_complete_omission_vs_missing_branch_and_contradiction_survives_gap(self):
        rows={r['id']:r for r in self.result['cases']}
        self.assertEqual(rows['sitemap-omission']['actual'][2],'fail')
        self.assertEqual(rows['missing-child']['actual'][2],'inconclusive')
        self.assertEqual(rows['contradiction-with-gap']['actual'][2],'fail')
        reason=rows['contradiction-with-gap']['atomic_results'][2]['reason']
        self.assertIn('Missing/duplicate capture',reason);self.assertIn('Competing family URL',reason)
        for key in ('missing-child','contradiction-with-gap'):
            captured=tsep.read_json(self.root/key/'input.json')['targets'][0]['sitemaps']['documents']
            self.assertFalse(any(d['url'].endswith('two.xml') for d in captured))

    def test_http_conflict_and_javascript_contradiction_are_independent(self):
        rows={r['id']:r for r in self.result['cases']}
        self.assertIn('HTTP Link',rows['http-conflict']['atomic_results'][0]['reason'])
        self.assertIn('dom canonical',rows['js-canonical']['atomic_results'][0]['reason'])
        self.assertEqual(rows['reference']['actual'],rows['corrected']['actual'])
        self.assertEqual(rows['relative-canonical']['actual'][0],'fail')

    def test_replay_forbids_network_dns_and_subprocess(self):
        self.assertTrue(self.offline()['same_results'])

    def test_source_response_tamper_even_after_rehash_is_rejected(self):
        folder=self.root/'source/reference/capture'
        path=folder/'target-1-hop-1-response.bin';path.write_bytes(path.read_bytes()+b'changed')
        self.rehash(folder);self.rehash(self.root/'source');self.rehash()
        with self.assertRaisesRegex(ValueError,'sidecar mismatch'):self.offline()

    def test_family_intent_cannot_change_after_capture(self):
        self.change('source/registration.json',lambda d:d['scenarios']['reference']['intent']['canonical'].update(preferred_url='http://127.0.0.1:1/other'))
        self.rehash(self.root/'source');self.rehash()
        with self.assertRaisesRegex(ValueError,'family/intent mismatch'):self.offline()

    def test_human_review_cannot_be_injected_into_input(self):
        self.change('reference/input.json',lambda d:d['targets'][0].update(content_review={'reviewer':'Invented reviewer'}));self.rehash()
        with self.assertRaisesRegex(ValueError,'Family/capture input mismatch'):self.offline()

    def test_binding_wrapper_cannot_change_canonical_plan(self):
        self.change('source/reference/bindings/product/source.json',lambda d:d['targets'][0]['context'].update(canonical_plan_sha256='0'*64))
        self.rehash(self.root/'source');self.rehash()
        with self.assertRaisesRegex(ValueError,'receipt binding mismatch'):self.offline()

    def test_extra_server_request_rejected_before_successful_summary(self):
        p=self.root/'source/requests.jsonl';p.write_bytes(p.read_bytes()+p.read_bytes().splitlines(keepends=True)[0]);self.rehash()
        with self.assertRaisesRegex(ValueError,'Source request scope mismatch'):self.offline()

    def test_wrong_peer_rejected(self):
        p=self.root/'source/requests.jsonl';rows=[json.loads(x) for x in p.read_text().splitlines()];rows[-1]['peer']='192.0.2.1'
        p.write_text(''.join(json.dumps(r)+'\n' for r in rows));self.rehash()
        with self.assertRaisesRegex(ValueError,'Unexpected/incomplete server request'):self.offline()

    def test_browser_agent_cannot_contain_googlebot(self):
        self.change('observations.json',lambda d:d['reference/product'].update(agent='Mozilla Googlebot/2.1'));self.rehash()
        with self.assertRaisesRegex(ValueError,'Googlebot'):self.offline()

    def test_dom_association_cannot_be_rewritten_after_import(self):
        self.change('reference/product-binding.json',lambda d:d['association']['states'][0].update(attributed=False));self.rehash()
        with self.assertRaisesRegex(ValueError,'association differs'):self.offline()

    def test_snapshot_before_js_witness_cannot_pass(self):
        observations=tsep.read_json(self.root/'observations.json')
        observations['reference/product']['dom']=observations['reference/product']['dom'].replace('<span id="js">executed</span>','<span id="js">pending</span>')
        retained=tsep.read_json(self.root/'results.json')
        reg,inputs,bindings,counts=lab.assemble(self.root/'source',observations,retained['assessment_end'],'authored-fixture')
        calculated=lab.summarize(reg,inputs,counts,'authored-fixture',retained['assessment_end'])
        self.assertEqual(calculated['cases'][0]['actual'][0],'inconclusive')
        self.assertFalse(calculated['all_expectations_matched'])

    def test_source_changes_block_replay(self):
        with patch.object(lab,'sources',return_value={'changed':'0'*64}),self.assertRaisesRegex(ValueError,'source/plan mismatch'):self.offline()

    def test_report_cannot_claim_human_validation(self):
        self.change('reference/bundle/report.json',lambda d:d['assessor'].update(name='Invented human'))
        self.rehash(self.root/'reference/bundle');self.rehash()
        with self.assertRaisesRegex(ValueError,'Synthetic report identity'):self.offline()

    def test_no_overwrite_and_registration_precedes_captures(self):
        with self.assertRaisesRegex(ValueError,'NEW output'):
            lab.finish(self.source,self.base/'observations.json',self.original,'authored-fixture')
        self.assertTrue(self.offline()['same_results'])

    def test_transport_wrappers_do_not_declare_indexing_and_share_exact_ts10_plan(self):
        registration=tsep.read_json(self.root/'source/registration.json')
        for case in registration['plan']['cases']:
            key=case['id'];record=registration['scenarios'][key]
            for role in record['browser_roles']:
                source=tsep.read_json(self.root/'source'/key/'bindings'/role/'source.json')['targets'][0]
                self.assertEqual(source['intent']['indexing'],'transport-not-declared')
                self.assertFalse(source['intent']['public_canonical'])
                self.assertIn('DO NOT EVALUATE',source['context']['transport_only'])
                self.assertEqual(source['intent']['rendering']['required_states'],registration['plan']['required_states'])

    def test_unlisted_ts07_report_is_rejected(self):
        (self.root/'TS07-report.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'transport wrappers must remain inert'):self.offline()

    def test_swapped_document_dom_cannot_pass(self):
        observations=tsep.read_json(self.root/'observations.json')
        observations['reference/product']['dom']=observations['reference/variant']['dom']
        # Dates would otherwise be valid; only the DOM URL/role witness prevents attribution.
        observations['reference/product']['observed_at']=observations['reference/variant']['observed_at']
        retained=tsep.read_json(self.root/'results.json')
        reg,inputs,bindings,counts=lab.assemble(self.root/'source',observations,retained['assessment_end'],'authored-fixture')
        self.assertFalse(bindings['reference/product']['association']['states'][0]['attributed'])
        calculated=lab.summarize(reg,inputs,counts,'authored-fixture',retained['assessment_end'])
        self.assertEqual(calculated['cases'][0]['actual'][0],'inconclusive')

    def test_transport_policy_never_produces_a_pass_in_generic_evaluator(self):
        data=tsep.read_json(self.root/'source/reference/bindings/product/source.json')
        self.assertEqual([r['outcome'] for r in lab.evaluator.evaluate(data)],['inconclusive']*3)

    def test_auxiliary_root_node_is_preserved_and_inconclusive(self):
        observations=tsep.read_json(self.root/'observations.json')
        item=observations['reference/product']
        original=item['dom']
        item['dom']=original.replace('</html>','<div id="codex-browser-sidebar-comments-root"></div></html>')
        retained=tsep.read_json(self.root/'results.json')
        reg,inputs,bindings,counts=lab.assemble(self.root/'source',observations,retained['assessment_end'],'authored-fixture')
        rendered=inputs['reference']['targets'][0]['documents'][0]['render']['states'][0]
        self.assertEqual(rendered['dom'],item['dom'])
        self.assertTrue(bindings['reference/product']['association']['states'][0]['attributed'])
        calculated=lab.summarize(reg,inputs,counts,'authored-fixture',retained['assessment_end'])
        self.assertEqual(calculated['cases'][0]['actual'][0],'inconclusive')
        self.assertIn('Unsupported HTML root child',calculated['cases'][0]['atomic_results'][0]['reason'])
