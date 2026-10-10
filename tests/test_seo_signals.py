"""Frozen lexical observations and attribute-context counterexamples. Apache-2.0."""
import copy
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from experiments import seo_signals as signals

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT/'tests/fixtures'


def frozen(name, checksum):
    raw = (FIXTURES/name).read_bytes()
    if hashlib.sha256(raw).hexdigest() != (FIXTURES/checksum).read_text().strip():
        raise AssertionError('Frozen fixture changed: '+name)
    return json.loads(raw)


class SEOSignalInventory(unittest.TestCase):
    def test_frozen_whole_source_observations_and_explicit_expectation_change(self):
        original = frozen('seo-signals-experiment-cases.json', 'seo-signals-experiment-freeze.sha256')
        amendment = frozen('seo-signals-attribute-v2-cases.json', 'seo-signals-attribute-v2-freeze.sha256')
        self.assertEqual(amendment['base_fixture_sha256'], hashlib.sha256(
            (FIXTURES/'seo-signals-experiment-cases.json').read_bytes()).hexdigest())
        self.assertEqual(set(amendment['previous_expectation_changes']),
                         {'python-attribute-decoding-not-browser-claim'})
        self.assertEqual(len(original['cases']), 32)
        for case in original['cases']:
            with self.subTest(case=case['id']):
                expected = copy.deepcopy(case['expected'])
                if case['id'] in amendment['previous_expectation_changes']:
                    for mode in expected:
                        expected[mode]['signals'][0]['attributes']['href'] = '?a&notit;=b'
                result = signals.experiment(case['html'])
                for mode, reading in result['readings'].items():
                    self.assertEqual({k: reading[k] for k in ('complete', 'signals')}, expected[mode])
                    for signal in reading['signals']:
                        self.assertEqual(case['html'][signal['start']:signal['end']], signal['raw_tag'])
                complete = all(x['complete'] for x in expected.values())
                comparison = ('identical' if expected['enabled']['signals'] == expected['disabled']['signals']
                              else 'different') if complete else 'unavailable'
                self.assertEqual(result['inventory_comparison'], comparison)
                self.assertEqual(result['normative_effect'], 'none')
                self.assertNotIn('candidate_consensus', result)

    def test_frozen_attribute_context_and_after_head_refusal(self):
        amendment = frozen('seo-signals-attribute-v2-cases.json', 'seo-signals-attribute-v2-freeze.sha256')
        self.assertEqual(len(amendment['attribute_cases']), 25)
        for case in amendment['attribute_cases']:
            with self.subTest(raw=case['raw'][:100]):
                self.assertEqual(signals.attribute_value(case['raw']), case['expected'])
        for source in amendment['additional_refused_sources']:
            for reading in signals.experiment(source)['readings'].values():
                self.assertFalse(reading['complete'])
                self.assertEqual(reading['signals'], [])

    def test_unquoted_attributes_and_relative_href_are_not_resolved(self):
        source = ('<html><head><base href="https://example.test/">'
                  '<meta NAME=ROBOTS content=noindex><link REL=CANONICAL href=/relative>'
                  '</head><body><header>Text</header></body></html>')
        with patch.object(socket, 'socket', side_effect=AssertionError('No network')), \
                patch.object(socket, 'getaddrinfo', side_effect=AssertionError('No DNS')):
            result = signals.experiment(source)
        self.assertEqual(result['readings']['enabled']['signals'][0]['attributes'],
                         {'name': 'ROBOTS', 'content': 'noindex'})
        self.assertEqual(result['readings']['enabled']['signals'][1]['attributes']['href'], '/relative')
        self.assertEqual(result['network_requests'], 0)

    def test_cli_exact_utf8_bytes_isolated_from_normative_decision_modules(self):
        raw = ('<html><head><meta name="robots" content="index"></head>'
               '<body>é🙂\r\n<header>Text</header></body></html>').encode()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root/'source.txt'; output = root/'signals.json'
            source.write_bytes(raw)
            code = ("import runpy,sys,socket\n"
                    "def audit(event,args):\n"
                    " if event=='import' and args[0] in ('conformance.evaluate','conformance.canonical','collectors.ts01'):"
                    "raise RuntimeError('Forbidden normative import')\n"
                    "sys.addaudithook(audit)\n"
                    "def denied(*a,**k):raise RuntimeError('Forbidden networking')\n"
                    "socket.socket=denied;socket.getaddrinfo=denied\n"
                    "sys.argv=sys.argv[1:];runpy.run_path(sys.argv[0],run_name='__main__')")
            command = [sys.executable, '-I', '-c', code, str(ROOT/'experiments/seo_signals.py'),
                       str(source), '--output', str(output)]
            run = subprocess.run(command, capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 0, run.stderr)
            result = json.loads(output.read_bytes())
            self.assertEqual(result['source_utf8_sha256'], hashlib.sha256(raw).hexdigest())
            self.assertEqual(source.read_bytes(), raw)
            before = output.read_bytes()
            repeated = subprocess.run(command, capture_output=True, text=True, timeout=10)
            self.assertEqual(repeated.returncode, 64)
            self.assertEqual(output.read_bytes(), before)

    def test_input_bounds_and_changed_import_origin_fail_closed(self):
        with patch.object(signals.noscript, 'MAX_CHARS', 4):
            with self.assertRaisesRegex(ValueError, 'size limit'):
                signals.experiment('12345')
        with patch.object(signals.noscript, '__file__', '/different/experiments/noscript.py'):
            with self.assertRaisesRegex(ValueError, 'origin differs'):
                signals.experiment('<html><head></head><body></body></html>')


if __name__ == '__main__':
    unittest.main()
