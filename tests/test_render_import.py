"""Synthetic importer tests. Authored DOM fixtures are not browser executions."""
import copy
import json
import html
from pathlib import Path
import socket
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import tsep
from adapters import rendered
from collectors import ts01
from conformance import evaluate as evaluator
from examples import rendered_ts07_lab as lab


class RenderImport(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)
        cases = tsep.read_json(rendered.ROOT/'conformance/cases.json')['cases']
        data = copy.deepcopy(next(c['input'] for c in cases if c['id']=='render-all-states-compatible'))
        data = json.loads(json.dumps(data).replace('https://example.com','http://127.0.0.1:8765').replace('Host: example.com','Host: 127.0.0.1:8765'))
        target = data['targets'][0]; supplied = target.pop('render'); target.pop('access_review')
        ts01.save(self.root/'source.json',data)
        with patch.object(ts01,'now',return_value='2026-10-09T10:00:01Z'):
            receipt = rendered.prepare(self.root/'source.json',self.root/'receipt.json')
        supplied['browser']['user_agent'] = 'SyntheticBrowser/1'
        for state in supplied['states']:
            state['source_http_sha256'] = receipt['source_http_sha256']
            values = {'state':state['id'],'js':'executed','agent':'SyntheticBrowser/1','context':state['context_id'],
                      'errors':'[]','event-time':'2026-10-09T10:00:01Z'}
            state['dom'] = state['dom'].replace('</body>', ''.join('<span id="'+key+'">'+html.escape(value)+'</span>' for key,value in values.items())+'</body>')
        self.envelope = {'capture_version':'1','receipt_sha256':tsep.digest(self.root/'receipt.json'),
                         'method':{'name':'Authored synthetic fixture','version':'1','description':'No browser executed'},
                         'browser':supplied['browser'], 'states':[{'state':s,'navigation':{
                             'url':receipt['url'],'complete':True,'request_agent':'SyntheticBrowser/1','peer':'127.0.0.1','observed_at':'2026-10-09T10:00:01Z',
                             'response':target['http'][-1]['response']}} for s in supplied['states']]}

    def tearDown(self):
        self.temp.cleanup()

    def attach(self):
        lines=[]
        for index,item in enumerate(self.envelope['states']):
            raw=(json.dumps(item['navigation'])+'\n').encode()
            item['log_index']=index;item['log_line_sha256']=rendered.fingerprint(raw);lines.append(raw)
        journal=b''.join(lines)
        (self.root/'requests.jsonl').write_bytes(journal)
        self.envelope['server_log_sha256']=rendered.fingerprint(journal)
        ts01.save(self.root/'browser.json',self.envelope)
        with patch.object(socket,'socket',side_effect=AssertionError('network forbidden')), \
             patch.object(socket,'getaddrinfo',side_effect=AssertionError('DNS forbidden')), \
             patch.object(subprocess,'run',side_effect=AssertionError('subprocess forbidden')):
            result = rendered.attach(self.root/'source.json',self.root/'receipt.json',self.root/'browser.json',self.root/'output',server_log=self.root/'requests.jsonl')
            self.assertTrue(rendered.replay(self.root/'output')['same_results'])
        return result

    def outcome(self):
        return self.attach()['atoms'][2]['outcome']

    def test_compatible_states_preserve_originals_but_never_global_c(self):
        result = self.attach()
        self.assertEqual([a['outcome'] for a in result['atoms']],['pass','inconclusive','pass'])
        self.assertEqual(result['status'],'NT')
        for name in ('source.json','receipt.json','browser.json'):
            self.assertEqual((self.root/name).read_bytes(),(self.root/'output'/name).read_bytes())
        self.assertNotIn('access_review',tsep.read_json(self.root/'output/input.json')['targets'][0])

    def test_wrong_trace_cannot_pass(self):
        self.envelope['states'][0]['state']['source_http_sha256']='0'*64
        self.assertEqual(self.outcome(),'inconclusive')

    def test_different_navigation_response_cannot_pass_even_with_correct_claimed_trace(self):
        self.envelope['states'][0]['navigation']['response'] += 'changed'
        self.assertEqual(self.outcome(),'inconclusive')
        association=tsep.read_json(self.root/'output/association.json')
        self.assertFalse(association['states'][0]['attributed'])

    def test_missing_planned_state_is_not_filled(self):
        self.envelope['states'].pop()
        self.assertEqual(self.outcome(),'inconclusive')

    def test_attributable_failure_survives_another_wrong_binding(self):
        self.envelope['states'][0]['state']['source_http_sha256']='0'*64
        state=self.envelope['states'][1]['state']
        state['dom']=state['dom'].replace('<title>','<meta name="robots" content="noindex"><title>')
        self.assertEqual(self.outcome(),'fail')

    def test_dom_predating_receipt_is_inconclusive(self):
        self.envelope['states'][0]['state']['observed_at']='2026-10-09T10:00:00Z'
        self.assertEqual(self.outcome(),'inconclusive')

    def test_navigation_predating_receipt_is_inconclusive(self):
        self.envelope['states'][0]['navigation']['observed_at']='2026-10-09T10:00:00Z'
        self.assertEqual(self.outcome(),'inconclusive')

    def test_navigation_postdating_dom_is_inconclusive(self):
        self.envelope['states'][0]['navigation']['observed_at']='2026-10-09T10:00:03Z'
        self.assertEqual(self.outcome(),'inconclusive')

    def test_absent_browser_version_is_not_filled(self):
        self.envelope['browser'].pop('version')
        self.assertEqual(self.outcome(),'inconclusive')

    def test_script_errors_are_retained(self):
        self.envelope['states'][0]['state']['errors']=['Synthetic exception']
        self.assertEqual(self.outcome(),'inconclusive')

    def test_disabled_javascript_is_inconclusive(self):
        self.envelope['states'][0]['state']['javascript_enabled']=False
        self.assertEqual(self.outcome(),'inconclusive')

    def test_incomplete_dom_is_inconclusive(self):
        self.envelope['states'][0]['state']['complete']=False
        self.assertEqual(self.outcome(),'inconclusive')

    def test_changed_source_rejected_before_delivery(self):
        with (self.root/'source.json').open('a') as handle: handle.write(' ')
        with self.assertRaisesRegex(ValueError,'binding mismatch'): self.attach()
        self.assertFalse((self.root/'output').exists())

    def test_changed_receipt_rejected(self):
        with (self.root/'receipt.json').open('a') as handle: handle.write(' ')
        with self.assertRaisesRegex(ValueError,'binding mismatch'): self.attach()

    def test_changed_tool_rejected(self):
        with patch.object(rendered,'sources',return_value={'changed':'0'*64}),self.assertRaisesRegex(ValueError,'binding mismatch'):
            self.attach()

    def test_no_overwrite(self):
        self.attach()
        with self.assertRaisesRegex(ValueError,'NEW output'):
            rendered.attach(self.root/'source.json',self.root/'receipt.json',self.root/'browser.json',self.root/'output',server_log=self.root/'requests.jsonl')

    def test_tampered_derived_input_rejected_even_after_manifest_rehash(self):
        self.attach(); folder=self.root/'output'
        data=tsep.read_json(folder/'input.json');data['targets'][0]['render']['states'][0]['errors']=['invented']
        (folder/'input.json').write_text(json.dumps(data)); (folder/'SHA256SUMS').unlink();ts01.manifest(folder,rendered.FILES)
        with self.assertRaisesRegex(ValueError,'Replayed input.json differs'): rendered.replay(folder)

    def test_frozen_pages_have_no_external_resources_and_source_outcomes_match(self):
        plan=lab.fixture()
        self.assertEqual(len(plan['cases']),5)
        for case in plan['cases']:
            body=lab.page(case,'synthetic-test')
            self.assertNotIn(' src=',body)
            self.assertNotIn('href="http',body)
            source=tsep.read_json(self.root/'source.json'); target=source['targets'][0]
            target['http'][0]['response']=lab.wire(body).decode('utf-8')
            self.assertEqual(evaluator.evaluate(source)[0]['outcome'],case['expected'][0],case['id'])
            self.assertIn(b'Cache-Control: no-store',lab.wire(body))
            self.assertNotIn(b'Content-Encoding:',lab.wire(body))

    def test_duplicate_state_inventory_remains_inconclusive(self):
        self.envelope['states'].append(copy.deepcopy(self.envelope['states'][0]))
        self.assertEqual(self.outcome(),'inconclusive')

    def test_preclick_dom_cannot_be_labelled_as_acted(self):
        self.envelope['states'][1]['state']['dom']=self.envelope['states'][0]['state']['dom']
        self.assertEqual(self.outcome(),'inconclusive')

    def test_copied_collector_response_is_not_browser_navigation(self):
        self.envelope['states'][0]['navigation']['request_agent']='googlebot'
        self.assertEqual(self.outcome(),'inconclusive')

    def test_wrong_recorded_peer_is_not_attributed(self):
        self.envelope['states'][0]['navigation']['peer']='192.0.2.1'
        self.assertEqual(self.outcome(),'inconclusive')

    def test_changed_journal_rejected_even_with_outer_manifest_rehashed(self):
        self.attach();folder=self.root/'output'
        with (folder/'requests.jsonl').open('a') as handle:handle.write(' ')
        (folder/'SHA256SUMS').unlink();ts01.manifest(folder,rendered.FILES)
        with self.assertRaisesRegex(ValueError,'log fingerprint'):rendered.replay(folder)

    def test_browser_log_line_must_equal_the_cited_record(self):
        self.attach();folder=self.root/'output'
        data=tsep.read_json(folder/'browser.json');data['states'][0]['log_line_sha256']='0'*64
        source_raw=(folder/'source.json').read_bytes();receipt_raw=(folder/'receipt.json').read_bytes()
        _,association=rendered.derive(source_raw,receipt_raw,data,(folder/'requests.jsonl').read_bytes())
        self.assertFalse(association['states'][0]['attributed'])
