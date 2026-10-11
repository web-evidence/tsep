"""Real bounded loopback exchanges under a prefrozen synthetic TS43 recipe."""
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
from examples import agent_access_laboratory as lab


class AgentAccessLaboratory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(); cls.original=Path(cls.temp.name)/'experiment'
        cls.result=lab.run(cls.original)

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def setUp(self):
        self.temp_case=tempfile.TemporaryDirectory(); self.root=Path(self.temp_case.name)/'copy'
        shutil.copytree(self.original,self.root)

    def tearDown(self): self.temp_case.cleanup()

    def rehash(self):
        names=[line.split('  ',1)[1] for line in (self.root/'SHA256SUMS').read_text().splitlines()]
        (self.root/'SHA256SUMS').unlink(); ts01.manifest(self.root,names)

    def change(self,name,mutate):
        path=self.root/name; data=tsep.read_json(path); mutate(data)
        path.write_text(json.dumps(data,ensure_ascii=False)+'\n'); self.rehash()

    def offline(self):
        with patch.object(socket,'socket',side_effect=AssertionError('Network forbidden')), \
             patch.object(socket,'getaddrinfo',side_effect=AssertionError('DNS forbidden')), \
             patch.object(subprocess,'run',side_effect=AssertionError('Subprocess forbidden')):
            return lab.replay(self.root)

    def test_six_prefrozen_cases_eight_actual_requests_and_no_real_identity(self):
        self.assertTrue(self.result['all_expectations_matched'])
        self.assertEqual([r['actual']['control_status'] for r in self.result['cases']],['C','C','C','NC','NT','C'])
        records=[json.loads(line) for line in (self.root/'requests.jsonl').read_text().splitlines()]
        self.assertEqual(len(records),8); self.assertEqual({r['peer_ip'] for r in records},{'127.0.0.1'})
        self.assertTrue(all(r['fictional_allowlist_match'] is False for r in records))
        self.assertEqual(records[3]['forwarded_for'],'192.0.2.5')
        self.assertEqual(records[3]['status'],403); self.assertEqual(records[4]['status'],200)
        for case in lab.fixture()['cases']:
            data=tsep.read_json(self.root/case['id']/'input.json')
            self.assertNotIn('atomic_outcomes',data); self.assertNotIn('expected',data)
            t=data['targets'][0]
            self.assertFalse(t['attribution']['claims_operator_visit'])
            self.assertEqual(t['attribution']['operator_identity'],'not-verified')
            self.assertEqual(t['log_review']['provenance'],'synthetic-exercise')

    def test_cached_response_id_is_from_primer_not_current_request(self):
        evidence=tsep.read_json(self.root/'exchanges.json')
        primer=lab.message(evidence['primer']['response'])[1]['x-request-id']
        cached=next(p for p in evidence['phases'] if p['id']=='cached-id')['http'][0]
        self.assertEqual(lab.message(cached['response'])[1]['x-request-id'],primer)
        atoms=tsep.read_json(self.root/'cached-id/bundle/assessment.json')
        self.assertEqual(atoms[1]['outcome'],'inconclusive')
        self.assertIn('outside request clock window',atoms[1]['reason'])
        self.assertIn('erroneous fixture judgment',tsep.read_json(self.root/'cached-id/input.json')['targets'][0]['log_review']['reason'])

    def test_replay_has_no_network_dns_or_subprocess(self):
        result=self.offline()
        self.assertTrue(result['same_observations_and_results']); self.assertEqual(result['network_requests'],0)

    def test_changed_registered_expectation_is_rejected_even_after_rehash(self):
        self.change('registration.json',lambda d:d['plans']['identity-gated']['agent_access']['test_access'].update(action='allow'))
        with self.assertRaisesRegex(ValueError,'Registered test plans differ'): self.offline()

    def test_changed_input_cannot_invent_operator_visit(self):
        self.change('ua-only/input.json',lambda d:d['targets'][0]['attribution'].update(claims_operator_visit=True))
        with self.assertRaisesRegex(ValueError,'Capture/input binding mismatch'): self.offline()

    def test_changed_log_cannot_be_qualified_by_rehash(self):
        path=self.root/'requests.jsonl'; rows=[json.loads(line) for line in path.read_text().splitlines()]
        rows[1]['peer_ip']='192.0.2.1'; path.write_text(''.join(json.dumps(r)+'\n' for r in rows)); self.rehash()
        with self.assertRaisesRegex(ValueError,'Native request log scope/clock mismatch'): self.offline()

    def test_incomplete_experiment_is_rejected(self):
        self.change('exchanges.json',lambda d:d['phases'].pop())
        with self.assertRaisesRegex(ValueError,'request count mismatch'): self.offline()

    def test_changed_sources_prevent_replay(self):
        changed=dict(lab.sources(), **{'examples/agent_access_laboratory.py':'0'*64})
        with patch.object(lab,'sources',return_value=changed), self.assertRaisesRegex(ValueError,'source/plan mismatch'):
            self.offline()

    def test_real_reviewer_claim_is_rejected(self):
        path=self.root/'ua-only/bundle/report.json'; data=tsep.read_json(path)
        data['assessor']['name']='Invented human'; path.write_text(json.dumps(data)+'\n')
        folder=path.parent; names=[line.split('  ',1)[1] for line in (folder/'SHA256SUMS').read_text().splitlines()]
        (folder/'SHA256SUMS').unlink(); ts01.manifest(folder,names); self.rehash()
        with self.assertRaisesRegex(ValueError,'Synthetic report identity mismatch'): self.offline()

    def test_changed_results_are_not_trusted(self):
        self.change('results.json',lambda d:d.update(actual_operator_visits_established=True))
        with self.assertRaisesRegex(ValueError,'Replayed summary differs'): self.offline()


if __name__ == '__main__': unittest.main()
