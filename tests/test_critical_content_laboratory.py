"""Controlled TS44 transport and provenance boundaries; full Node run is separate."""
import json
import os
from pathlib import Path
import shutil
import socket
import tempfile
import unittest
from unittest.mock import patch

import tsep
from collectors import ts01
from examples import critical_content_laboratory as lab

NO_NODE = {'TSEP_SOURCE_NODE':'/unavailable/node24'}


class CriticalContentLaboratory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.original = Path(cls.temp.name)/'experiment'
        with patch.dict(os.environ, NO_NODE), \
                patch.object(socket, 'getaddrinfo', side_effect=AssertionError('DNS forbidden')), \
                patch.object(socket, 'getfqdn', side_effect=AssertionError('DNS forbidden')):
            cls.result = lab.run(cls.original)

    def setUp(self):
        self.temp_case = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_case.cleanup)
        self.root = Path(self.temp_case.name)/'copy'
        shutil.copytree(self.original, self.root)

    def rehash(self, root=None):
        root = root or self.root
        names = [line.split('  ',1)[1] for line in (root/'SHA256SUMS').read_text().splitlines()]
        (root/'SHA256SUMS').unlink(); ts01.manifest(root,names)

    def change(self, name, mutate):
        p = self.root/name; data = tsep.read_json(p); mutate(data)
        p.write_text(json.dumps(data,ensure_ascii=False)+'\n'); self.rehash()

    def offline(self):
        with patch.dict(os.environ,NO_NODE), \
                patch.object(socket,'socket',side_effect=AssertionError('Network forbidden')), \
                patch.object(socket,'getaddrinfo',side_effect=AssertionError('DNS forbidden')):
            return lab.replay(self.root)

    def test_six_actual_requests_and_optional_runtime_limits_stay_visible(self):
        self.assertEqual(self.result['actual_http_requests'],6)
        self.assertFalse(self.result['all_expectations_matched'])
        self.assertEqual([r['actual']['control_status'] for r in self.result['cases']],['NT','NT','NT','NC'])
        self.assertEqual([r['expected']['control_status'] for r in self.result['cases']],['C','NC','C','NC'])
        records=[json.loads(line) for line in (self.root/'requests.jsonl').read_text().splitlines()]
        self.assertEqual(len(records),6)
        self.assertEqual({r['peer_ip'] for r in records},{'127.0.0.1'})
        self.assertFalse(self.result['human_review_performed'])
        self.assertFalse(self.result['browser_observed'])
        self.assertFalse(self.result['actual_agent_visit_established'])

    def test_prior_registration_is_separate_from_authored_dom_and_reviews(self):
        registration=tsep.read_json(self.root/'registration.json')
        exchanges=tsep.read_json(self.root/'exchanges.json')
        for case,phase in zip(lab.fixture()['cases'],exchanges['phases']):
            t=tsep.read_json(self.root/case['id']/'input.json')['targets'][0]
            self.assertLessEqual(tsep.timestamp(t['critical_plan_review']['observed_at']),
                                 tsep.timestamp(phase['http'][0]['sent_at']))
            self.assertEqual(t['critical_plan_review']['provenance'],'synthetic-exercise')
            acquisition=t['render']['states'][0]['structured_dom']['acquisition']
            self.assertEqual(acquisition['kind'],'authored-synthetic')
            self.assertIn('DOM rédigé, non observé dans un navigateur',acquisition['support'][0]['content'])
            self.assertEqual(registration['plans'][case['id']]['intent'],t['intent'])

    def test_replay_is_offline_and_keeps_unmet_runtime_expectations(self):
        result=self.offline()
        self.assertTrue(result['same_observations_and_results'])
        self.assertEqual(result['network_requests'],0)
        self.assertFalse(result['all_expectations_matched'])

    def test_changed_plan_is_rejected_even_after_rehash(self):
        self.change('registration.json',lambda d:d['plans']['server-html']['intent']['critical_content'].update(delivery='resource'))
        with self.assertRaisesRegex(ValueError,'Registered plans'): self.offline()

    def test_changed_http_body_cannot_be_qualified_by_rehash(self):
        self.change('exchanges.json',lambda d:d['phases'][0]['http'][0].update(
            response=d['phases'][0]['http'][0]['response'].replace('1.8 s','8.1 s')))
        with self.assertRaisesRegex(ValueError,'Observed response differs'): self.offline()

    def test_wrong_native_log_rejected(self):
        p=self.root/'requests.jsonl';rows=[json.loads(line) for line in p.read_text().splitlines()]
        rows[0]['peer_ip']='192.0.2.1';p.write_text(''.join(json.dumps(r)+'\n' for r in rows));self.rehash()
        with self.assertRaisesRegex(ValueError,'Native request log mismatch'): self.offline()

    def test_authored_dom_cannot_be_relabelled_as_browser_capture(self):
        self.change('exchanges.json',lambda d:d['phases'][0]['authored_state']['structured_dom']['acquisition'].update(kind='same-navigation'))
        with self.assertRaisesRegex(ValueError,'Authored DOM attribution'): self.offline()

    def test_missing_exchange_is_rejected(self):
        self.change('exchanges.json',lambda d:d['phases'].pop())
        with self.assertRaisesRegex(ValueError,'request count mismatch'): self.offline()

    def test_future_synthetic_review_cannot_pass_receipt_check(self):
        self.change('receipt.json',lambda d:d.update(synthetic_review_at='2099-01-01T00:00:00Z'))
        with self.assertRaisesRegex(ValueError,'Receipt chronology'): self.offline()

    def test_changed_input_is_not_trusted(self):
        self.change('server-html/input.json',lambda d:d['targets'][0]['critical_plan_review'].update(provenance='human'))
        with self.assertRaisesRegex(ValueError,'Capture/input binding mismatch'): self.offline()

    def test_human_assessor_claim_rejected_even_after_rehash(self):
        p=self.root/'server-html/bundle/report.json';d=tsep.read_json(p)
        d['assessor']['name']='Invented human reviewer';p.write_text(json.dumps(d)+'\n')
        self.rehash(p.parent);self.rehash()
        with self.assertRaisesRegex(ValueError,'Synthetic report identity'): self.offline()

    def test_source_mismatch_rejected_before_replay(self):
        changed=dict(lab.sources(), **{'examples/critical_content_laboratory.py':'0'*64})
        with patch.object(lab,'sources',return_value=changed), self.assertRaisesRegex(ValueError,'source/recipe mismatch'):
            self.offline()

    def test_unplanned_destination_rejected_before_socket(self):
        with patch.object(socket,'socket',side_effect=AssertionError('Must not connect')):
            for base,path in [('https://example.test','/server-html'),('http://127.0.0.1:8','/unplanned'),
                              ('http://127.0.0.1:8@evil.example','/server-html')]:
                with self.subTest(base=base,path=path),self.assertRaises(ValueError): lab.fetch(base,path)

    def test_partial_transport_failure_retains_the_actual_first_exchange(self):
        original=lab.fetch;calls=[]
        def interrupted(base,path):
            calls.append(path)
            if len(calls)==2:raise OSError('Injected second-request interruption')
            return original(base,path)
        output=Path(self.temp_case.name)/'interrupted'
        with patch.object(lab,'fetch',side_effect=interrupted),self.assertRaisesRegex(OSError,'Injected'):
            lab.run(output)
        failure=tsep.read_json(output/'failure.json')
        self.assertFalse(failure['collection_complete'])
        self.assertEqual(len((output/'requests.jsonl').read_text().splitlines()),1)
        self.assertEqual(len(tsep.read_json(output/'exchanges.json')['phases'][0]['http']),1)
        self.assertFalse((output/'SHA256SUMS').exists())


if __name__ == '__main__': unittest.main()
