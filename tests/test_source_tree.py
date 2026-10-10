"""Python-only integrity and failure checks; Node qualification is opt-in."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from experiments import source_tree as tree

ROOT = Path(__file__).resolve().parents[1]


class SourceTreeExperiment(unittest.TestCase):
    def test_complete_official_archives_and_licenses(self):
        files = tree.packages()
        self.assertEqual({k: len(v) for k, v in files.items()}, {'parse5': 33, 'entities': 58})
        for name in files:
            self.assertEqual(files[name]['LICENSE'], (ROOT/'licenses'/('source-tree-'+name+'.txt')).read_bytes())

    def test_tampered_archive_rejected_even_if_manifest_digest_is_updated(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            shutil.copytree(ROOT/'third_party', root/'third_party')
            base = root/'third_party/source-tree'
            archive = base/'parse5-8.0.1.tgz'
            archive.write_bytes(archive.read_bytes()+b'changed')
            path = base/'packages.json'
            manifest = json.loads(path.read_bytes())
            manifest['packages'][0]['sha256'] = tree.sha(archive.read_bytes())
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'archive changed'):
                tree.packages(root)

    def test_incomplete_inventory_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            shutil.copytree(ROOT/'third_party', root/'third_party')
            path = root/'third_party/source-tree/packages.json'
            manifest = json.loads(path.read_bytes())
            del manifest['packages'][0]['files']['LICENSE']
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'Unexpected package member'):
                tree.packages(root)

    def test_frozen_oracle_correction_is_explicit_and_single(self):
        values = []
        for version in (1, 2):
            path = ROOT/'tests/fixtures'/('source-tree-cases-v'+str(version)+'.json')
            raw = path.read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), path.with_suffix('.sha256').read_text().strip())
            values.append(json.loads(raw))
        old, new = values
        self.assertEqual(len(old['cases']), 36)
        differences = [(a['id'], m) for a, b in zip(old['cases'], new['cases'])
                       for m in ('enabled', 'disabled') if a['expected'][m] != b['expected'][m]]
        self.assertEqual(differences, [('noscript-closing-trap', 'enabled')])
        self.assertEqual(new['correction']['old'], next(c for c in old['cases']
                         if c['id'] == new['correction']['case'])['expected']['enabled'])
        self.assertEqual([c['html'] for c in old['cases']], [c['html'] for c in new['cases']])
        path = ROOT/'tests/fixtures/source-tree-groups-v1.json'
        self.assertEqual(tree.sha(path.read_bytes()), path.with_suffix('.sha256').read_text().strip())
        self.assertEqual(len(json.loads(path.read_bytes())['cases']), 12)

    def test_encoding_size_and_missing_runtime_never_fall_back(self):
        for raw, encoding, expected in [(b'html', 'latin-1', 'UTF-8'), (b'\xff', 'utf-8', 'utf-8')]:
            with self.assertRaisesRegex(ValueError, expected):
                tree.inventory(raw, encoding=encoding, node='/missing/node')
        with patch.object(tree, 'MAX_BYTES', 3):
            with self.assertRaisesRegex(ValueError, 'byte bound'):
                tree.inventory(b'1234', encoding='utf-8', node='/missing/node')
        with self.assertRaisesRegex(ValueError, 'unavailable'):
            tree.inventory(b'html', encoding='utf-8', node='/missing/node')

    def test_timeout_is_enforced_and_node_preload_environment_is_removed(self):
        with patch.object(tree.shutil, 'which', return_value='/synthetic/node'), \
             patch.object(tree.subprocess, 'run', side_effect=subprocess.TimeoutExpired('node', 30)) as run, \
             patch.dict(os.environ, {'NODE_OPTIONS': '--import=evil.mjs', 'NODE_PATH': '/foreign'}):
            with self.assertRaisesRegex(ValueError, '30-second process deadline'):
                tree.inventory(b'html', encoding='utf-8')
            self.assertEqual(run.call_args.kwargs['timeout'], 30)
            self.assertNotIn('NODE_OPTIONS', run.call_args.kwargs['env'])
            self.assertNotIn('NODE_PATH', run.call_args.kwargs['env'])

    def test_utf16_attribution_and_partial_reading_rejection(self):
        source = '🙂<a href=/>'
        record = {'context': 'body', 'source_span_utf16': [2, 13], 'raw_tag': '<a href=/>'}
        reading = {'complete': True, 'inventory': {g: ([record] if g == 'anchors' else [])
                   for g in tree.GROUPS}, 'template_signals': []}
        result = {'kind': 'unapplied-static-source-tree', 'experiment_version': '1', 'normative_effect': 'none',
                  'readings': {'enabled': copy.deepcopy(reading), 'disabled': copy.deepcopy(reading)},
                  'comparisons': {g: 'identical' for g in tree.GROUPS}}
        # UTF-16 length is 12: two units for the emoji and ten for the tag.
        for r in result['readings'].values():
            r['inventory']['anchors'][0]['source_span_utf16'][1] = 12
        tree.validate_projection(result, source)
        bad = copy.deepcopy(result)
        bad['readings']['enabled']['inventory']['anchors'][0]['source_span_utf16'][0] = 1
        with self.assertRaises(ValueError):
            tree.validate_projection(bad, source)
        bad = copy.deepcopy(result); bad['readings']['enabled']['complete'] = False
        with self.assertRaisesRegex(ValueError, 'partial reading'):
            tree.validate_projection(bad, source)
        bad = copy.deepcopy(result); bad['comparisons']['anchors'] = 'different'
        with self.assertRaisesRegex(ValueError, 'comparison differs'):
            tree.validate_projection(bad, source)

    def test_cli_missing_runtime_isolated_from_evaluator_and_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root/'source'; output = root/'output.json'
            source.write_bytes(b'<html><body>source</body></html>')
            command = [sys.executable, '-I', str(ROOT/'experiments/source_tree.py'), str(source),
                       '--encoding', 'utf-8', '--node', '/missing/node', '--output', str(output)]
            run = subprocess.run(command, capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 64)
            self.assertFalse(output.exists())
            self.assertEqual(json.loads(run.stderr)['kind'], 'experiment-unavailable')
            output.write_bytes(b'previous output')
            run = subprocess.run(command, capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 64)
            self.assertEqual(output.read_bytes(), b'previous output')


if __name__ == '__main__':
    unittest.main()
