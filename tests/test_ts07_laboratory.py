"""Replayed TS07 laboratory evidence, independent frozen expectations and tamper checks."""
import copy
import io
import json
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import tsep
from collectors import ts01
from examples import ts07_laboratory as lab


class TS07Laboratory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.original = Path(cls.temp.name)/'laboratory'
        cls.result = lab.run(cls.original)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.temp_case = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_case.name)/'copy'
        shutil.copytree(self.original, self.root)

    def tearDown(self):
        self.temp_case.cleanup()

    def offline(self):
        with patch.object(socket, 'socket', side_effect=AssertionError('Network forbidden')), \
             patch.object(socket, 'getaddrinfo', side_effect=AssertionError('DNS forbidden')), \
             patch.object(subprocess, 'run', side_effect=AssertionError('Subprocess forbidden')):
            return lab.replay(self.root)

    def rehash(self, root):
        path = root/'SHA256SUMS'
        names = [line.split('  ', 1)[1] for line in path.read_text().splitlines()]
        path.unlink()
        ts01.manifest(root, names)

    def change_json(self, name, mutate):
        path = self.root/name
        data = tsep.read_json(path)
        mutate(data)
        path.write_text(json.dumps(data, ensure_ascii=False)+'\n')

    def test_prefrozen_fifteen_cases_and_thirty_actual_requests(self):
        plan = lab.fixture()
        self.assertEqual(len(plan['cases']), 15)
        self.assertEqual([r['id'] for r in self.result['cases']], [c['id'] for c in plan['cases']])
        for case, row in zip(plan['cases'], self.result['cases']):
            with self.subTest(case=case['id']):
                self.assertEqual(row['actual'], case['expected'])
                self.assertNotIn(row['actual']['control_status'], ('C', 'NA'))
                data = tsep.read_json(self.root/case['id']/'input.json')
                self.assertNotIn('expected', data)
                self.assertNotIn('render', data['targets'][0])
                self.assertNotIn('access_review', data['targets'][0])
                report = tsep.read_json(self.root/case['id']/'bundle/report.json')
                self.assertTrue(all(a['access'] == 'synthetic' for a in report['artifacts']))
        requests = tsep.read_json(self.root/'requests.json')
        self.assertEqual(len(requests), 30)
        self.assertEqual({r['agent'] for r in requests}, {'googlebot'})
        self.assertEqual({r['path'] for r in requests}, {'/page', '/robots.txt'})
        self.assertTrue(self.result['all_expectations_matched'])

    def test_header_defect_correction_and_experimental_disagreement_remain_distinct(self):
        rows = {r['id']:r for r in self.result['cases']}
        reference = rows['initial']['observation']
        for key in ('header-noindex', 'header-corrected'):
            observed = rows[key]['observation']
            self.assertEqual(observed['decoded_body_sha256'], reference['decoded_body_sha256'])
            self.assertEqual(observed['lexical_inventory'], reference['lexical_inventory'])
        self.assertEqual(rows['header-noindex']['observation']['x_robots_tag'], ['noindex'])
        self.assertEqual(rows['header-noindex']['actual']['atomic_outcomes'][0], 'fail')
        self.assertEqual(rows['header-corrected']['actual']['control_status'], 'NT')
        for key in ('unsupported-source', 'blocked-unsupported'):
            self.assertEqual(rows[key]['actual']['atomic_outcomes'][0], 'inconclusive')
            self.assertEqual(rows[key]['actual']['inventory_comparison'], 'different')
        self.assertEqual(rows['blocked-unsupported']['actual']['control_status'], 'NC')
        self.assertEqual(rows['exclude-blocked']['actual']['atomic_outcomes'], ['pass', 'fail', 'inconclusive'])

    def test_full_replay_forbids_network_dns_and_subprocess(self):
        result = self.offline()
        self.assertTrue(result['same_observations_and_results'])
        self.assertEqual(result['network_requests'], 0)
        self.assertEqual(result['cases'], 15)

    def test_changed_raw_response_is_rejected_even_with_all_manifests_recomputed(self):
        folder = self.root/'header-noindex'
        raw = folder/'capture/target-2-hop-1-response.bin'
        raw.write_bytes(raw.read_bytes().replace(b'noindex', b'indexxx'))
        for path in (folder/'capture', folder, self.root):
            self.rehash(path)
        with self.assertRaisesRegex(ValueError, 'sidecar mismatch'):
            self.offline()

    def test_changed_input_cannot_invent_review_or_render(self):
        for field in ('access_review', 'render'):
            with self.subTest(field=field):
                self.change_json('initial/input.json', lambda d: d['targets'][0].update({field: {'fabricated': True}}))
                self.rehash(self.root/'initial'); self.rehash(self.root)
                with self.assertRaisesRegex(ValueError, 'Capture/input binding mismatch'):
                    self.offline()

    def test_changed_intent_or_registered_scope_is_rejected_after_rehash(self):
        original = (self.root/'registration.json').read_bytes()
        changes = [lambda d:d['intents']['allow'].update(indexing='exclude'),
                   lambda d:d['settings'].update(agent='otherbot'),
                   lambda d:d.update(registered_at='2999-01-01T00:00:00Z')]
        for change in changes:
            (self.root/'registration.json').write_bytes(original)
            self.change_json('registration.json', change); self.rehash(self.root)
            with self.assertRaises(ValueError):
                self.offline()

    def test_missing_scenario_manifest_and_changed_request_log_are_rejected(self):
        path = self.root/'SHA256SUMS'
        original = path.read_bytes()
        path.write_text('\n'.join(line for line in path.read_text().splitlines() if 'initial/SHA256SUMS' not in line)+'\n')
        with self.assertRaisesRegex(ValueError, 'Incomplete laboratory manifest'):
            self.offline()
        path.write_bytes(original)
        self.change_json('requests.json', lambda d:d.pop())
        self.rehash(self.root)
        with self.assertRaisesRegex(ValueError, 'request scope mismatch'):
            self.offline()

    def test_tampered_results_or_inventory_are_not_trusted(self):
        self.change_json('initial/observations.json', lambda d:d.update(x_robots_tag=['invented']))
        self.rehash(self.root/'initial'); self.rehash(self.root)
        with self.assertRaisesRegex(ValueError, 'Replayed lexical observations differ'):
            self.offline()

    def test_changed_tool_source_prevents_replay(self):
        changed = dict(lab.sources(), **{'examples/ts07_laboratory.py':'0'*64})
        with patch.object(lab, 'sources', return_value=changed), self.assertRaisesRegex(ValueError, 'source/plan mismatch'):
            self.offline()

    def test_report_cannot_claim_an_actual_reviewer_after_rehash(self):
        folder = self.root/'initial'
        self.change_json('initial/bundle/report.json', lambda d:d['assessor'].update(name='Invented human review'))
        for path in (folder/'bundle', folder, self.root):
            self.rehash(path)
        with self.assertRaisesRegex(ValueError, 'Synthetic report identity mismatch'):
            self.offline()

    def test_recorded_non_loopback_peer_is_rejected_after_rehash(self):
        folder = self.root/'initial'
        self.change_json('initial/capture/capture.json',
                         lambda d:d['targets'][0]['http'][0].update(peer_address='192.0.2.1'))
        for path in (folder/'capture', folder, self.root):
            self.rehash(path)
        with self.assertRaisesRegex(ValueError, 'Recorded peer'):
            self.offline()

    def test_extra_server_request_keeps_log_without_success_summary(self):
        original = lab.Handler.do_GET
        injected = []
        def extra(handler):
            if not injected:
                handler.server.requests.append({'case':'unexpected', 'path':'/foreign', 'agent':'other-client'})
                injected.append(True)
            return original(handler)
        output = Path(self.temp_case.name)/'extra-request'
        with patch.object(lab.Handler, 'do_GET', extra), self.assertRaisesRegex(ValueError, 'request scope mismatch'):
            lab.run(output)
        self.assertEqual(len(tsep.read_json(output/'requests.json')), 31)
        self.assertFalse((output/'results.json').exists())
        self.assertTrue((output/'initial/capture/SHA256SUMS').is_file())

    def test_runtime_difference_is_disclosed_not_confused_with_result_change(self):
        runtime = copy.deepcopy(lab.runtime_identity()); runtime['build'] += ' alternate test runtime'
        with patch.object(lab, 'runtime_identity', return_value=runtime):
            result = self.offline()
        self.assertFalse(result['same_recorded_runtime'])
        self.assertTrue(result['same_observations_and_results'])

    def test_cli_refuses_existing_output_without_network(self):
        target = self.root/'existing.json'; target.write_text('Preserve this')
        with patch.object(sys, 'argv', ['lab', 'replay', str(self.root), '--output', str(target)]), \
             patch.object(socket, 'socket', side_effect=AssertionError('No network')), \
             patch('sys.stderr', new_callable=io.StringIO):
            self.assertEqual(lab.main(), 64)
        self.assertEqual(target.read_text(), 'Preserve this')
        with patch.object(socket, 'socket', side_effect=AssertionError('No listener')), \
             self.assertRaisesRegex(ValueError, 'NEW output'):
            lab.run(self.root)


if __name__ == '__main__':
    unittest.main()
