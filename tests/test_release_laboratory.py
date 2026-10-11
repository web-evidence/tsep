"""Actual local TS41 execution and adversarial offline attribution checks."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import tsep
from collectors import ts01
from examples import release_laboratory as lab


class ReleaseLaboratory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.temp.cleanup)
        cls.original=Path(cls.temp.name)/'experiment'
        with patch.object(socket,'getaddrinfo',side_effect=AssertionError('DNS forbidden')), \
             patch.object(socket,'getfqdn',side_effect=AssertionError('DNS forbidden')):
            cls.result=lab.run(cls.original)

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'copy';shutil.copytree(self.original,self.root)

    def rehash(self,root=None):
        root=root or self.root
        names=[line.split('  ',1)[1] for line in (root/'SHA256SUMS').read_text().splitlines()]
        (root/'SHA256SUMS').unlink();ts01.manifest(root,names)

    def change(self,name,fn):
        p=self.root/name;value=tsep.read_json(p);fn(value)
        p.write_text(json.dumps(value,ensure_ascii=False)+'\n');self.rehash()

    def offline(self):
        with patch.object(socket,'socket',side_effect=AssertionError('No network')), \
             patch.object(socket,'getaddrinfo',side_effect=AssertionError('No DNS')), \
             patch.object(subprocess,'Popen',side_effect=AssertionError('No child processes')), \
             patch.object(lab,'replace_active',side_effect=AssertionError('No artifact application')):
            return lab.replay(self.root)

    def test_six_prefrozen_scenarios_sixteen_actual_requests_and_processes(self):
        result=self.result
        self.assertEqual((result['actual_http_requests'],result['actual_processes']),(16,16))
        self.assertTrue(result['all_expectations_matched'])
        self.assertEqual([r['actual']['control_status'] for r in result['cases']],['C','C','C','NC','NC','C'])
        self.assertFalse(result['human_review_performed']);self.assertFalse(result['production_deployed']);self.assertFalse(result['edikka_assessed'])
        records=lab.read_lines(self.root/'requests.jsonl');self.assertEqual(len(records),16)
        self.assertEqual({r['status'] for r in records},{200});self.assertEqual({r['peer_ip'] for r in records},{'127.0.0.1'})
        incomplete=[r for r in records if r['actual_body_bytes']!=r['declared_content_length']]
        self.assertEqual(len(incomplete),3)

    def test_frozen_recipe_precedes_implementation_and_is_exact(self):
        self.assertEqual(tsep.digest(lab.ROOT/lab.FIXTURE),'1eb18ebfabaa2ed0a9ab92dcc2870f9936efcd349d2d8cc0a182e02faad61f0a')
        self.assertIn('before laboratory implementation',lab.fixture()['expected_origin'])
        registration=tsep.read_json(self.root/'registration.json')
        self.assertLessEqual(tsep.timestamp(registration['registered_at']),tsep.timestamp(registration['window_start']))
        for p in registration['plans'].values():
            self.assertEqual(p['target']['release_plan_review']['provenance'],'synthetic-exercise')
        for case in lab.fixture()['cases']:
            t=tsep.read_json(self.root/case['id']/'input.json')['targets'][0]
            self.assertEqual(t['release_review']['provenance'],'synthetic-exercise')

    def test_actual_block_keeps_positive_before_after_file_evidence(self):
        for name in ('noindex-blocked','unknown-blocked'):
            effects=lab.read_lines(self.root/name/'effects.jsonl')
            self.assertEqual(effects[-1]['action'],'blocked')
            self.assertEqual(effects[-1]['operation'],'explicit-hold-no-write')
            self.assertEqual(effects[-1]['before_json'],lab.baseline())
            self.assertEqual(effects[-1]['after_json'],lab.baseline())
            self.assertEqual((self.root/name/'active.json').read_text(),lab.baseline())
            self.assertEqual(len(tsep.read_json(self.root/name/'runs.json')),2)
        actions=lab.read_lines(self.root/'red-test-ignored/effects.jsonl')
        self.assertEqual(actions[1]['operation'],'atomic-replace')
        self.assertNotEqual(actions[1]['before_sha256'],actions[1]['after_sha256'])

    def test_replay_runs_no_network_no_process_and_no_deployment(self):
        result=self.offline()
        self.assertTrue(result['same_observations_and_results']);self.assertTrue(result['all_expectations_matched'])
        self.assertEqual((result['network_requests'],result['processes_executed'],result['artifact_applications']),(0,0,0))

    def test_unknown_mask_preserves_native_unknown_and_actual_zero_exit(self):
        r=tsep.read_json(self.root/'unknown-masked/unknown-masked-pre/receipt.json')
        self.assertEqual(r['exit_code'],0)
        self.assertEqual({v['outcome'] for v in json.loads(r['stdout_json'])},{'inconclusive'})
        actual=tsep.read_json(self.root/'unknown-masked/unknown-masked-pre/process.json')
        worker=tsep.read_json(self.root/'unknown-masked/unknown-masked-pre/worker.json')
        self.assertEqual(actual['pid'],worker['pid']);self.assertEqual(actual['exit_code'],0)

    def test_changed_registration_rejected_even_after_rehash(self):
        self.change('registration.json',lambda d:d['plans']['clean-cycle']['native']['intent'].update(indexing='disallow'))
        with self.assertRaisesRegex(ValueError,'Registered native'):self.offline()

    def test_changed_http_evidence_rejected_after_rehash(self):
        self.change('clean-cycle/clean-cycle-pre/exchange.json',lambda d:d.update(response=d['response'].replace('Expected public content','Changed public content')))
        with self.assertRaisesRegex(ValueError,'Native input scope|Observed HTTP'):self.offline()

    def test_changed_process_stdout_cannot_be_hidden_by_consistent_hashes(self):
        name='noindex-blocked';run_id=name+'-pre';folder=self.root/name/run_id
        rows=tsep.read_json(folder/'stdout.json');rows[1]['outcome']='pass';raw=json.dumps(rows)+'\n'
        (folder/'stdout.json').write_text(raw)
        for relative in ('receipt.json','process.json'):
            p=folder/relative;x=tsep.read_json(p);x['stdout_sha256']=lab.sha(raw)
            if relative=='receipt.json':x['stdout_json']=raw
            p.write_text(json.dumps(x)+'\n')
        p=self.root/name/'runs.json';runs=tsep.read_json(p)
        next(r for r in runs if r['id']==run_id).update(stdout_json=raw,stdout_sha256=lab.sha(raw));p.write_text(json.dumps(runs)+'\n');self.rehash()
        with self.assertRaisesRegex(ValueError,'Worker result/exit'):self.offline()

    def test_changed_exit_cannot_be_laundered_by_receipt_hashes(self):
        name='noindex-blocked';run_id=name+'-pre';folder=self.root/name/run_id
        for relative in ('receipt.json','process.json'):
            p=folder/relative;x=tsep.read_json(p);x['exit_code']=0;p.write_text(json.dumps(x)+'\n')
        p=self.root/name/'runs.json';runs=tsep.read_json(p)
        next(r for r in runs if r['id']==run_id)['exit_code']=0;p.write_text(json.dumps(runs)+'\n');self.rehash()
        with self.assertRaisesRegex(ValueError,'Worker result/exit'):self.offline()

    def test_changed_effect_bytes_rejected_even_after_rehash(self):
        p=self.root/'noindex-blocked/effects.jsonl';rows=lab.read_lines(p)
        rows[-1].update(after_json=lab.artifact('noindex'),after_sha256=lab.sha(lab.artifact('noindex')))
        p.write_text(''.join(lab.compact(r)+'\n' for r in rows));self.rehash()
        with self.assertRaisesRegex(ValueError,'artifact action or snapshot'):self.offline()

    def test_changed_final_active_file_rejected(self):
        (self.root/'clean-cycle/active.json').write_text(lab.baseline());self.rehash()
        with self.assertRaisesRegex(ValueError,'Final active artifact'):self.offline()

    def test_missing_server_log_is_a_clean_refusal(self):
        p=self.root/'requests.jsonl';rows=lab.read_lines(p);rows.pop();p.write_text(''.join(lab.compact(r)+'\n' for r in rows));self.rehash()
        with self.assertRaisesRegex(ValueError,'missing server requests'):self.offline()

    def test_wrong_server_identity_and_timing_rejected(self):
        p=self.root/'requests.jsonl';rows=lab.read_lines(p);rows[0]['peer_ip']='192.0.2.1'
        p.write_text(''.join(lab.compact(r)+'\n' for r in rows));self.rehash()
        with self.assertRaisesRegex(ValueError,'server-log binding'):self.offline()

    def test_human_assessor_and_review_claim_rejected(self):
        p=self.root/'clean-cycle/bundle/report.json';r=tsep.read_json(p);r['assessor']['name']='Invented human approver'
        p.write_text(json.dumps(r)+'\n');self.rehash(p.parent);self.rehash()
        with self.assertRaisesRegex(ValueError,'Synthetic laboratory report identity'):self.offline()

    def test_unlisted_file_and_empty_directory_are_refused(self):
        extra=self.root/'unlisted.txt';extra.write_text('unlisted')
        with self.assertRaisesRegex(ValueError,'Unlisted'):self.offline()
        extra.unlink();(self.root/'unlisted-directory').mkdir()
        with self.assertRaisesRegex(ValueError,'Unlisted'):self.offline()

    def test_source_identity_and_future_review_cannot_be_replaced(self):
        changed=dict(lab.sources(),**{'examples/release_laboratory.py':'0'*64})
        with patch.object(lab,'sources',return_value=changed),self.assertRaisesRegex(ValueError,'source identity'):
            self.offline()
        self.change('receipt.json',lambda d:d.update(synthetic_review_at='2099-01-01T00:00:00Z'))
        with self.assertRaisesRegex(ValueError,'receipt chronology'):self.offline()

    def test_only_prefrozen_numeric_loopback_before_socket(self):
        with patch.object(socket,'socket',side_effect=AssertionError('Must not connect')):
            for base,case in [('https://example.test','clean-cycle'),('http://127.0.0.1:8@evil.example','clean-cycle'),
                              ('http://127.0.0.1:8','unplanned')]:
                with self.subTest(base=base,case=case),self.assertRaises(ValueError):
                    lab.fetch(base,case,case+'-pre')

    def test_interrupted_second_process_keeps_first_http_and_exit(self):
        original=lab.run_process;calls=[]
        def stop(folder,command,config,timeout=6):
            calls.append(config['run_id'])
            if len(calls)==2:raise OSError('Injected second process interruption')
            return original(folder,command,config,timeout)
        output=Path(self.tmp.name)/'interrupted'
        with patch.object(lab,'run_process',side_effect=stop),self.assertRaisesRegex(OSError,'Injected second'):
            lab.run(output)
        failure=tsep.read_json(output/'failure.json');self.assertFalse(failure['collection_complete'])
        self.assertEqual(len(lab.read_lines(output/'requests.jsonl')),1)
        self.assertEqual(tsep.read_json(output/'clean-cycle/clean-cycle-negative/process.json')['exit_code'],1)
        self.assertFalse((output/'SHA256SUMS').exists())


if __name__=='__main__':unittest.main()
