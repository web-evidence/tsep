import copy
import json
from pathlib import Path
import shutil
import socket
import tempfile
import unittest
from unittest.mock import patch

import tsep
from collectors import ts01
from examples.prospective_ts01 import run
from experiments import prospective

ROOT = Path(__file__).resolve().parents[1]


class ProspectiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.lab = Path(cls.temp.name)/'laboratory'
        cls.result = run(cls.lab)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.temp_case = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_case.name)/'copy'
        shutil.copytree(self.lab, self.root)

    def tearDown(self):
        self.temp_case.cleanup()

    def compare(self):
        with patch.object(socket, 'socket', side_effect=AssertionError('Network forbidden')), \
                patch.object(socket, 'getaddrinfo', side_effect=AssertionError('DNS forbidden')):
            return prospective.compare(self.root/'first/reference', self.root/'assessment', self.root/'receipt.json')

    def modify(self, name, change, rehash=False):
        path = self.root/name
        data = tsep.read_json(path)
        change(data)
        path.write_text(json.dumps(data), encoding='utf-8')
        if rehash:
            self.rehash(path.parent)

    def rehash(self, root):
        manifest = root/'SHA256SUMS'
        names = [line.split('  ', 1)[1] for line in manifest.read_text().splitlines()]
        manifest.unlink()
        ts01.manifest(root, names)

    def test_frozen_nine_outcomes_and_exact_request_scope(self):
        fixture_path = ROOT/'tests/fixtures/prospective-ts01-cases.json'
        self.assertEqual(tsep.digest(fixture_path), (fixture_path.parent/'prospective-ts01-freeze.sha256').read_text().strip())
        fixture = tsep.read_json(fixture_path)
        for row, expected in zip(self.result['targets'], fixture['cases']):
            with self.subTest(case=expected['id']):
                self.assertTrue(row['url'].endswith('/'+expected['id']))
                self.assertEqual([a['outcome'] for a in row['active_observations']], [expected['active_a01'], expected['active_a02']])
                probe = row['marker_experiment']
                self.assertEqual(probe['candidate_consensus'] if probe else row['eligibility'], expected['experiment'])
                if probe:
                    self.assertTrue(row['same_decoded_body_bytes'])
                    self.assertEqual(probe['source_utf8_sha256'], row['decoded_body_sha256'])
        requests = tsep.read_json(self.lab/'laboratory.json')['requests']
        self.assertEqual(len(requests), 19)
        self.assertEqual(sum(r['phase'] == 'reference' for r in requests), 9)
        self.assertEqual(len(self.result['targets']), len(fixture['cases']))

    def test_portable_offline_replay_keeps_normative_and_experiment_separate(self):
        self.assertEqual(self.compare(), self.result)
        self.assertEqual(self.result['normative_effect'], 'none')
        self.assertTrue(self.result['active_report_replayed']['same_atomic_observations_and_gate'])
        self.assertIn('no trusted timestamp', self.result['chronology'])

    def test_changed_intent_after_receipt_is_rejected_even_with_new_manifest(self):
        self.modify('assessment/intent.json', lambda d: d.update(label='Changed'), True)
        with self.assertRaisesRegex(ValueError, 'Frozen reference/intent/probe changed'):
            self.compare()

    def test_receipt_after_measurement_is_rejected(self):
        self.modify('receipt.json', lambda d: d.update(prepared_at='2999-01-01T00:00:00Z'))
        with self.assertRaisesRegex(ValueError, 'Receipt must precede'):
            self.compare()

    def test_changed_experimental_source_is_rejected(self):
        changed = dict(prospective.sources(), **{'experiments/noscript.py': '0'*64})
        with patch.object(prospective, 'sources', return_value=changed), \
                self.assertRaisesRegex(ValueError, 'Trial source/receipt mismatch'):
            self.compare()

    def test_raw_capture_sidecar_disagreement_is_rejected_after_rehash(self):
        path = self.root/'first/reference/target-1-hop-1-response.bin'
        path.write_bytes(path.read_bytes().replace(b'Expected', b'Modified'))
        self.rehash(path.parent)
        with self.assertRaisesRegex(ValueError, 'sidecar mismatch'):
            self.compare()

    def test_input_reference_evaluation_and_context_cannot_be_rebound(self):
        path = self.root/'assessment/input.json'
        original = path.read_bytes()
        changes = [lambda d: d['targets'][0]['reference'].update(observed_at='2000-01-01T00:00:00Z'),
                   lambda d: d['targets'][0].update(observed_at='2000-01-01T00:00:00Z'),
                   lambda d: d['targets'][0]['context'].update(network='Other'),
                   lambda d: d['targets'][0]['context'].update(intent_file_sha256='0'*64)]
        for change in changes:
            path.write_bytes(original)
            self.modify('assessment/input.json', change, True)
            with self.assertRaisesRegex(ValueError, 'binding mismatch|context mismatch'):
                self.compare()

    def test_fabricated_experimental_reference_check_is_rejected(self):
        def change(d):
            d['checked_reference']['targets'][0]['experimental_reference']['candidate_consensus'] = 'fail'
        self.modify('receipt.json', change)
        with self.assertRaisesRegex(ValueError, 'Frozen reference/intent/probe changed'):
            self.compare()

    def test_contradictory_reference_never_gets_a_receipt(self):
        def change(d):
            d['targets'][0]['intent']['required_markers'] = ['Absent']
        self.modify('intent.json', change)
        with self.assertRaisesRegex(ValueError, 'Reference does not satisfy'):
            prospective.prepare(self.root/'first/reference', self.root/'intent.json', self.root/'invalid.json')
        self.assertFalse((self.root/'invalid.json').exists())

    def test_runtime_difference_is_disclosed_with_same_outcomes(self):
        runtime = copy.deepcopy(tsep.read_json(self.root/'assessment/bundle/import.json')['runtime'])
        runtime['build'] += ' synthetic different runtime'
        with patch('adapters.captures.runtime_identity', return_value=runtime):
            result = self.compare()
        self.assertFalse(result['active_report_replayed']['same_recorded_runtime'])
        self.assertTrue(result['active_report_replayed']['same_atomic_observations_and_gate'])
        self.assertEqual(result['targets'], self.result['targets'])

    def test_prepare_never_overwrites_a_receipt(self):
        old = (self.root/'receipt.json').read_bytes()
        with self.assertRaises(FileExistsError):
            prospective.prepare(self.root/'first/reference', self.root/'intent.json', self.root/'receipt.json')
        self.assertEqual(old, (self.root/'receipt.json').read_bytes())

    def test_parsed_profile_cannot_be_silently_compared_as_lexical_experiment(self):
        def change(d):
            d['targets'][0]['intent']['identity_reader'] = 'html-tree-markers-v1'
            d['targets'][0]['identity_basis']['identity_reader'] = 'html-tree-markers-v1'
        self.modify('intent.json', change)
        with self.assertRaisesRegex(ValueError, 'Lexical experiment requires the historical'):
            prospective.prepare(self.root/'first/reference', self.root/'intent.json', self.root/'invalid.json')
        self.assertFalse((self.root/'invalid.json').exists())

    def test_old_intent_version_requires_its_historical_tool_archive(self):
        self.modify('intent.json', lambda d: d.update(intent_version='3'))
        with self.assertRaisesRegex(ValueError, 'Intent/reference settings mismatch'):
            prospective.prepare(self.root/'first/reference', self.root/'intent.json', self.root/'invalid.json')


if __name__ == '__main__':
    unittest.main()
