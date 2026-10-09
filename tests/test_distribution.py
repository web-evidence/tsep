"""Distribution boundaries and portability; Apache-2.0."""
import json
from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import maintain
import tsep


class Distribution(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root/'public.txt').write_text('public fixture')
        self.names = ['public.txt', 'release-files.json']
        self.save()

    def tearDown(self):
        self.temp.cleanup()

    def save(self):
        (self.root/'release-files.json').write_text(json.dumps({'format_version': 1, 'files': self.names}))

    def test_unlisted_private_files_cannot_enter_release(self):
        (self.root/'.env').write_text('SYNTHETIC_LOCAL_SETTING=example')
        (self.root/'private-notes.txt').write_text('private fixture')
        (self.root/'.tsep-local.json').write_text('{}')
        self.assertEqual([p.name for p in maintain.release_sources(self.root)], sorted(self.names))

    def test_explicit_private_files_are_rejected(self):
        for name in ['.env', '.env.production', '.tsep-local.json', '.ssh/config', '.git/config', 'backup.sql']:
            with self.subTest(name=name):
                path = self.root/name
                path.parent.mkdir(exist_ok=True)
                path.write_text('synthetic fixture')
                self.names = ['release-files.json', name]
                self.save()
                with self.assertRaises(tsep.Invalid):
                    maintain.release_sources(self.root)

    def test_missing_files_block_release(self):
        self.names.append('missing.json')
        self.save()
        with self.assertRaises(tsep.Invalid):
            maintain.release_sources(self.root)

    def test_duplicates_block_release(self):
        self.names.append('public.txt')
        self.save()
        with self.assertRaises(tsep.Invalid):
            maintain.release_sources(self.root)

    def test_path_traversal_and_absolute_paths_block_release(self):
        for name in ['../outside', '/outside', 'a/../../outside', 'C:\\outside']:
            with self.subTest(name=name):
                self.names = ['release-files.json', name]
                self.save()
                with self.assertRaises(tsep.Invalid):
                    maintain.release_sources(self.root)

    def test_file_symlink_blocks_release(self):
        (self.root/'alias.txt').symlink_to(self.root/'public.txt')
        self.names.append('alias.txt')
        self.save()
        with self.assertRaises(tsep.Invalid):
            maintain.release_sources(self.root)

    def test_directory_symlink_blocks_release(self):
        (self.root/'directory').mkdir()
        (self.root/'directory/file.txt').write_text('fixture')
        (self.root/'alias').symlink_to(self.root/'directory', target_is_directory=True)
        self.names.append('alias/file.txt')
        self.save()
        with self.assertRaises(tsep.Invalid):
            maintain.release_sources(self.root)

    def test_manifest_is_distributed(self):
        self.names = ['public.txt']
        self.save()
        with self.assertRaises(tsep.Invalid):
            maintain.release_sources(self.root)


if __name__ == '__main__':
    unittest.main()
