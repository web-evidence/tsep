"""The runtime preflight must agree with PATH discovery and reject substitutions."""
import os
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch
from scripts.runtime import node24,source_runtime_available


class RuntimeSelection(unittest.TestCase):
    def test_path_only_and_explicit_runtime_have_the_same_identity(self):
        explicit=node24(os.environ)
        env=dict(os.environ,PATH=str(Path(explicit['path']).parent));env.pop('TSEP_SOURCE_NODE',None)
        self.assertEqual(node24(env),explicit)
        self.assertTrue(source_runtime_available(env))

    def test_invalid_explicit_runtime_does_not_fall_back_to_path(self):
        env=dict(os.environ,TSEP_SOURCE_NODE='/nonexistent/tsep-node24')
        self.assertFalse(source_runtime_available(env))
        with self.assertRaisesRegex(ValueError,'unavailable'):node24(env)

    def test_missing_or_wrong_major_runtime_is_not_qualification(self):
        self.assertFalse(source_runtime_available({'PATH':'/nonexistent'}))
        with patch('scripts.runtime.subprocess.run',return_value=subprocess.CompletedProcess([],0,'v22.1.0\n','')):
            with self.assertRaisesRegex(ValueError,'Node24 required'):node24(os.environ)


if __name__=='__main__':unittest.main()
