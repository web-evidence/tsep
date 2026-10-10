"""Reject mixed module origins before collection or offline assessment. Apache-2.0."""
import importlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from adapters.captures import source_files, build
from collectors.ts01 import collection_sources, reference
import tsep

ROOT = Path(__file__).resolve().parents[1]


class RuntimeProvenance(unittest.TestCase):
    def test_actual_loaded_origins_are_hashed(self):
        for files in (source_files(), collection_sources()):
            for name, fingerprint in files.items():
                self.assertEqual(fingerprint, tsep.digest(ROOT/name))
            self.assertIn('provenance/runtime.py', files)

    def test_foreign_module_file_or_spec_is_rejected_before_bundle(self):
        module = importlib.import_module('conformance.http')
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)/'bundle'
            for obj, field in ((module, '__file__'), (module.__spec__, 'origin')):
                with self.subTest(field=field), patch.object(obj, field, str(Path(folder)/'http.py')):
                    with self.assertRaisesRegex(ValueError, 'Loaded module origin differs'):
                        build(ROOT/'examples/captures/ts01-markers.json', output,
                              assessor='Test', label='Test', selection_method='Synthetic', access='synthetic')
            self.assertFalse(output.exists())

    def test_foreign_worker_import_cannot_start_collection(self):
        module = importlib.import_module('collectors.http')
        with patch.object(module, '__file__', '/some/other/collectors/http.py'), \
                patch('collectors.ts01.subprocess.run', side_effect=AssertionError('No network')):
            with self.assertRaisesRegex(ValueError, 'Loaded module origin differs'):
                collection_sources()
