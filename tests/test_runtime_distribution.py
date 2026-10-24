"""Closed-profile contradictory cases. No collection, network or private source paths."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/runtime_distribution.py'
if not SCRIPT.exists():
    SCRIPT = Path(__file__).with_name('runtime_distribution.py')
spec = importlib.util.spec_from_file_location('runtime_distribution', SCRIPT)
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


class RuntimeDistributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.profile = runtime.definitions()[1][0]

    def fake_tree(self, files):
        tree = self.folder/'source'
        tree.mkdir()
        for name, data in files.items():
            p = tree/name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        return tree, {n: runtime.digest(b) for n,b in files.items()}

    def test_two_closed_descriptors(self):
        profiles = runtime.definitions()[1]
        self.assertEqual(len(profiles), 2)
        for profile in profiles:
            p, retained, payload, descriptor = runtime.package_metadata(profile['id'])
            self.assertEqual(len(p['full_source_files']) - len(retained), 1)
            self.assertEqual(set(p['excluded']), {'provenance/source-canonical-signal-correction.json'})
            for n, excluded in p['excluded'].items():
                self.assertEqual(excluded['sha256'], p['full_source_files'][n])
                self.assertTrue(excluded['reason_en'] and excluded['reason_fr'])
                self.assertNotIn('runtime/'+n, descriptor['files'])
            self.assertEqual('runtime/SHA256SUMS' in descriptor['files'], 'SHA256SUMS' in p['full_source_files'])
            self.assertEqual(runtime.encode(descriptor), payload['distribution.json'])

    def test_unknown_profile(self):
        for value in ('', 'draft33', None, ['draft31']):
            with self.subTest(value=value), self.assertRaises(runtime.Invalid):
                runtime.select_profile(value)

    def test_coherent_snapshot(self):
        root, inventory = self.fake_tree({'a/a.py': b'x', '.gitattributes': b''})
        self.assertEqual(runtime.snapshot(root, inventory)['a/a.py'], b'x')

    def test_extra_file(self):
        root, inventory = self.fake_tree({'a.py':b'a'})
        (root/'extra.py').write_bytes(b'x')
        with self.assertRaises(runtime.Invalid): runtime.snapshot(root, inventory)

    def test_missing_file(self):
        root, inventory = self.fake_tree({'a.py':b'a'})
        (root/'a.py').unlink()
        with self.assertRaises(runtime.Invalid): runtime.snapshot(root, inventory)

    def test_changed_bytes(self):
        root, inventory = self.fake_tree({'a.py':b'a'})
        (root/'a.py').write_bytes(b'b')
        with self.assertRaises(runtime.Invalid): runtime.snapshot(root, inventory)

    def test_symlink_file(self):
        root, inventory = self.fake_tree({'a.py':b'a'})
        other=self.folder/'outside'; other.write_bytes(b'a')
        (root/'a.py').unlink(); (root/'a.py').symlink_to(other)
        with self.assertRaises(runtime.Invalid): runtime.snapshot(root, inventory)

    def test_symlink_directory(self):
        root, inventory = self.fake_tree({'sub/a.py':b'a'})
        shutil.move(root/'sub', self.folder/'outside')
        (root/'sub').symlink_to(self.folder/'outside', target_is_directory=True)
        with self.assertRaises(runtime.Invalid): runtime.snapshot(root, inventory)

    def test_symlink_root(self):
        root, inventory = self.fake_tree({'a.py':b'a'})
        alias=self.folder/'alias'; alias.symlink_to(root, target_is_directory=True)
        with self.assertRaises(runtime.Invalid): runtime.snapshot(alias, inventory)

    def test_extra_empty_directory(self):
        root, inventory = self.fake_tree({'a.py':b'a'})
        (root/'private').mkdir()
        with self.assertRaises(runtime.Invalid): runtime.snapshot(root, inventory)

    def test_alias_and_unsafe_paths(self):
        for name in ('/x', 'a/../b', './a', 'a//b', 'a\\b', 'a\x00', 'a/é', '', 'a:ads'):
            with self.subTest(name=name), self.assertRaises(runtime.Invalid): runtime.safe_name(name)

    def test_modified_closed_definitions_refused(self):
        copied=self.folder/'tool'; copied.mkdir()
        shutil.copyfile(SCRIPT, copied/'runtime_distribution.py')
        raw, _=runtime.definitions()
        altered=json.loads(raw); altered['closed_profiles'][0]['excluded']['another.txt']={'sha256':'0'*64}
        (copied/'runtime-profiles.json').write_text(json.dumps(altered))
        source=self.folder/'source'; source.mkdir()
        result=subprocess.run([sys.executable,'-I','-B',str(copied/'runtime_distribution.py'),'build','--source',str(source),'--output',str(self.folder/'out.zip'),'--profile',self.profile['id']],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertIn('Closed profile definitions changed',result.stderr)
        self.assertFalse((self.folder/'out.zip').exists())
        self.assertNotIn(str(self.folder),result.stderr)

    def test_bad_source_no_output(self):
        root, _ = self.fake_tree({'a.py':b'a'})
        out=self.folder/'output.zip'
        with self.assertRaises(runtime.Invalid): runtime.build(root,out,self.profile['id'])
        self.assertFalse(out.exists())

    def test_output_inside_source_refused(self):
        root, _ = self.fake_tree({'a.py':b'a'})
        with self.assertRaisesRegex(runtime.Invalid, 'outside source'):
            runtime.build(root,root/'out.zip',self.profile['id'])
        self.assertFalse((root/'out.zip').exists())

    def test_unknown_descriptor_no_acceptance(self):
        (self.folder/'distribution.json').write_text('{"profile_id":"unknown"}')
        with self.assertRaises(runtime.Invalid): runtime.check(self.folder)


if __name__ == '__main__':
    unittest.main()
