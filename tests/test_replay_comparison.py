"""Frozen synthetic comparisons and offline workflow adversarial cases."""
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import tsep
from adapters import captures, replay, replay_comparison as comparison
from adapters.package import inventory, json_bytes, seal
from scripts.source_directives_check import fixture

ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT/'tests/fixtures/replay-python-supervisor-v1.json'
CASES_HASH = 'ffe3152329afd039c1a564281a116282145c03459a9073bdef93cc0e3e0464df'
CASES = json.loads(CASES_PATH.read_text())['cases']


class ReplayComparison(unittest.TestCase):
    def test_frozen_synthetic_expectations(self):
        self.assertEqual(hashlib.sha256(CASES_PATH.read_bytes()).hexdigest(), CASES_HASH)
        self.assertEqual(len(CASES), 37)
        for case in CASES:
            with self.subTest(case=case['id']):
                before = copy.deepcopy(case)
                result = comparison.compare(case['original'], case['current'], case['original_runtime'],
                                            case['current_runtime'], 'python-supervisor-v1')
                self.assertEqual(result['match'], case['expected_match'])
                strict = comparison.compare(case['original'], case['current'], case['original_runtime'],
                                            case['current_runtime'])
                self.assertEqual(strict['match'], result['exact'])
                self.assertFalse(any(d['allowed_python_supervisor_difference'] for d in strict['differences']))
                self.assertEqual(before, case)
                for difference in result['differences']:
                    if difference['allowed_python_supervisor_difference']:
                        self.assertEqual(difference['original_value'], case['original_runtime']['python'])
                        self.assertEqual(difference['current_value'], case['current_runtime']['python'])

    def test_reversal_supported_range_and_difference_budget(self):
        case = CASES[1]
        result = comparison.compare(case['current'], case['original'], case['current_runtime'],
                                    case['original_runtime'], 'python-supervisor-v1')
        self.assertTrue(result['match'])
        self.assertEqual(len(result['differences']), 3)
        # Supported range is not an allowlist of the two locally tested versions.
        for version in ('3.10.2', '3.11.9', '3.13.1'):
            current = copy.deepcopy(case['current'])
            for worker, field in ((current['observations'][0]['inventory'], 'python'),
                                  (current['observations'][0]['base_policy_metadata'], 'python_version'),
                                  (current['observations'][0]['url_runs'][0], 'python')):
                worker['supervisor'][field] = version
            runtime = dict(case['current_runtime'], python=version)
            self.assertTrue(comparison.compare(case['original'], current, case['original_runtime'],
                                               runtime, 'python-supervisor-v1')['match'])
        with patch.object(comparison, 'MAX_DIFFERENCES', 2):
            result = comparison.compare(case['original'], case['current'], case['original_runtime'],
                                        case['current_runtime'], 'python-supervisor-v1')
        self.assertFalse(result['complete'])
        self.assertFalse(result['match'])
        self.assertEqual(len(result['differences']), 2)

    def test_object_key_order_and_pointer_escaping(self):
        self.assertTrue(comparison.compare({'a': 1, 'b': 2}, {'b': 2, 'a': 1}, None, None)['exact'])
        result = comparison.compare({'a/b~c': None}, {}, None, None)
        self.assertEqual(result['differences'][0]['pointer'], '/a~1b~0c')
        self.assertFalse(result['differences'][0]['current']['present'])
        with self.assertRaisesRegex(ValueError, 'Unknown'):
            comparison.compare({}, {}, None, None, 'guess')

    def test_offline_replay_profiles_preserve_both_raw_sides_and_reject_changed_facts(self):
        # Inject authored diagnostics around a real adapter bundle. This tests
        # workflow wiring without pretending that these are observed Node outputs.
        case = CASES[1]
        actual_build = captures.build
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {'TSEP_SOURCE_NODE': '/missing'}):
            root = Path(folder)
            source = root/'input.json'
            source.write_bytes(json_bytes(fixture()['cases'][0]['input']))
            bundle = root/'source'
            captures.build(source, bundle, assessor='Synthetic fixture author', label='Synthetic replay diagnostic',
                           selection_method='Authored workflow test', access='synthetic')
            observation_name = 'observations/source-observation-1.json'

            def inject(destination, observation, runtime=None):
                (destination/observation_name).write_bytes(json_bytes(observation))
                if runtime is not None:
                    meta = tsep.read_json(destination/'import.json')
                    meta['runtime'] = runtime
                    (destination/'import.json').write_bytes(json_bytes(meta))
                report = tsep.read_json(destination/'report.json')
                for artifact in report['artifacts']:
                    if artifact['path'] in (observation_name, 'import.json'):
                        artifact['sha256'] = tsep.digest(destination/artifact['path'])
                (destination/'report.json').write_bytes(json_bytes(report))
                seal(destination)

            inject(bundle, case['original'], case['original_runtime'])
            before = inventory(bundle)

            def rebuilt(input_path, output, **kwargs):
                result = actual_build(input_path, output, **kwargs)
                inject(output, case['current'], case['current_runtime'])
                return result

            with patch.object(captures, 'build', side_effect=rebuilt), \
                    patch.object(replay, 'runtime_identity', return_value=case['current_runtime']), \
                    patch('socket.socket', side_effect=AssertionError('Network forbidden')), \
                    patch('socket.getaddrinfo', side_effect=AssertionError('DNS forbidden')):
                with self.assertRaisesRegex(ValueError, 'Replay differs'):
                    replay.replay(bundle, root/'strict')
                result = replay.replay(bundle, root/'profile', comparison='python-supervisor-v1')
                self.assertTrue(result['replayed'])
                self.assertFalse(result['same_source_observations'])
                self.assertFalse(result['same_recorded_runtime'])
                self.assertTrue(result['source_observations_match'])
                self.assertEqual(result['workflow_version'], '3')
                self.assertIsNone(result['original_unicode_data_version'])
                self.assertEqual((root/'profile/original-evidence'/observation_name).read_bytes(),
                                 (bundle/observation_name).read_bytes())
                self.assertEqual(tsep.read_json(root/'profile/bundle'/observation_name), case['current'])
                self.assertEqual(result['original_runtime'], case['original_runtime'])
                self.assertEqual(result['current_runtime'], case['current_runtime'])
                self.assertEqual(before, inventory(bundle))
                inventory(root/'profile')
                with self.assertRaises(ValueError):
                    replay.replay(bundle, root/'profile', comparison='python-supervisor-v1')
                changed = copy.deepcopy(case['original'])
                changed['observations'][0]['inventory']['readings']['enabled']['href'] = 'https://example.com/other'
                inject(bundle, changed)
                with self.assertRaisesRegex(ValueError, 'Replay differs'):
                    replay.replay(bundle, root/'wrong-fact', comparison='python-supervisor-v1')
                self.assertFalse(tsep.read_json(root/'wrong-fact/replay.json')['source_observations_match'])
                # A missing source observation cannot disappear from comparison.
                report = tsep.read_json(bundle/'report.json')
                extra = bundle/'observations/source-observation-extra.json'
                extra.write_bytes(json_bytes(case['original']))
                seal(bundle)
                with self.assertRaisesRegex(ValueError, 'Replay differs'):
                    replay.replay(bundle, root/'extra-file', comparison='python-supervisor-v1')
                self.assertEqual(tsep.read_json(root/'extra-file/replay.json')['original_only_observations'],
                                 ['observations/source-observation-extra.json'])


if __name__ == '__main__':
    unittest.main()
