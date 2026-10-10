"""Real loopback collection, synthetic defects, exact offline reinterpretation. Apache-2.0."""
import hashlib
import json
from pathlib import Path
import socket
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments.robots_laboratory import run
from experiments.robots_policy import inspect_capture


class RobotsLaboratory(unittest.TestCase):
    def test_before_after_evidence_and_network_forbidden_reinterpretation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)/'lab'
            summary = run(root)
            self.assertEqual(summary['network_requests'], 18)
            self.assertEqual(summary['external_requests'], 0)
            self.assertEqual([r['observed_model'] for r in summary['rows']],
                             ['disallow', 'allow', 'allow', 'disallow', 'allow', 'allow', 'disallow', 'allow', 'allow', 'allow'])
            self.assertTrue(all(r['synthetic'] and r['resource_http_status'] == 200 for r in summary['rows']))
            noindex = [r for r in summary['rows'] if r['scenario'] == 'noindex-disallow']
            self.assertEqual([[a['outcome'] for a in r['active_ts07']] for r in noindex],
                             [['pass', 'fail'], ['pass', 'inconclusive']])
            for line in (root/'SHA256SUMS').read_text().splitlines():
                digest, name = line.split('  ', 1)
                self.assertEqual(hashlib.sha256((root/name).read_bytes()).hexdigest(), digest)
            with patch.object(socket, 'socket', side_effect=AssertionError('Network forbidden')):
                for source in root.rglob('input-*.json'):
                    number = source.stem.split('-')[1]
                    data = json.loads(source.read_text())
                    expected = json.loads((source.parent/('observation-'+number+'.json')).read_text())
                    self.assertEqual(inspect_capture(data), expected)
            with self.assertRaises(FileExistsError):
                run(root)


if __name__ == '__main__':
    unittest.main()
