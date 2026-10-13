"""Explicit fixture extensions cannot expand access or silently change expectations."""
import hashlib,json,tempfile,unittest
from pathlib import Path
import tsep
from unittest.mock import patch
from conformance.corpus import expand


class CorpusExtensions(unittest.TestCase):
    def setup_corpus(self,root,payload=None):
        p=root/'tests/fixtures/extra.json';p.parent.mkdir(parents=True);raw=(json.dumps(payload or {'synthetic':True,'cases':[{'id':'extra'}]})+'\n').encode();p.write_bytes(raw)
        (root/'release-files.json').write_text(json.dumps({'files':['tests/fixtures/extra.json']}))
        return {'cases':[{'id':'base'}],'additional_case_files':[{'path':'tests/fixtures/extra.json','sha256':hashlib.sha256(raw).hexdigest()}]}

    def test_exact_extension_preserves_original_and_base(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);c=self.setup_corpus(root);before=json.dumps(c,sort_keys=True)
            self.assertEqual([x['id'] for x in expand(c,root=root)['cases']],['base','extra']);self.assertEqual(json.dumps(c,sort_keys=True),before)

    def test_changed_fingerprint_and_unlisted_paths_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);c=self.setup_corpus(root)
            for path in ('../secret.json','/tmp/secret.json','tests/fixtures/missing.json','tests/fixtures/../extra.json'):
                broken=dict(c,additional_case_files=[dict(c['additional_case_files'][0],path=path)])
                with self.subTest(path=path),self.assertRaises(tsep.Invalid):expand(broken,root=root)
            (root/'tests/fixtures/extra.json').write_text('{"synthetic":true,"cases":[]}')
            with self.assertRaisesRegex(tsep.Invalid,'fingerprint'):expand(c,root=root)

    def test_symlink_duplicate_and_recursive_inputs_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);c=self.setup_corpus(root);p=root/'tests/fixtures/extra.json';saved=root/'saved.json';p.rename(saved);p.symlink_to(saved)
            with self.assertRaisesRegex(tsep.Invalid,'Symlink'):expand(c,root=root)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);c=self.setup_corpus(root);c['additional_case_files']*=2
            with self.assertRaisesRegex(tsep.Invalid,'duplicate'):expand(c,root=root)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);c=self.setup_corpus(root,{'synthetic':True,'cases':[],'additional_case_files':[]})
            with self.assertRaisesRegex(tsep.Invalid,'recursive'):expand(c,root=root)

    def test_no_extension_requires_no_file_access(self):
        self.assertEqual(expand({'cases':[]},root=Path('/nonexistent')),{'cases':[]})

    def test_expansion_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);expanded=expand(self.setup_corpus(root),root=root)
            self.assertEqual(expand(expanded,root=Path('/nonexistent')),expanded)

    def test_aggregate_size_bound_is_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);c=self.setup_corpus(root)
            with patch('conformance.corpus.MAX_TOTAL_BYTES',1),self.assertRaisesRegex(tsep.Invalid,'Aggregate corpus size'):
                expand(c,root=root)
