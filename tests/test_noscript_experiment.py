"""Unapplied candidate semantics, retained offsets, refusal and isolation. Apache-2.0."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments import noscript
from conformance.http import Unknown
from conformance.source_text import extract


class NoscriptExperiment(unittest.TestCase):
    def test_frozen_whole_document_expectations_and_per_reading_candidates(self):
        path = ROOT/'tests/fixtures/noscript-experiment-cases.json'
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                         (ROOT/'tests/fixtures/noscript-experiment-freeze.sha256').read_text().strip())
        cases = json.loads(path.read_text())['cases']
        self.assertEqual(len(cases), 68)
        self.assertEqual(len({c['id'] for c in cases}), len(cases))
        with patch('socket.socket', side_effect=AssertionError('network forbidden')), patch('socket.getaddrinfo', side_effect=AssertionError('DNS forbidden')):
            for case in cases:
                with self.subTest(case=case['id']):
                    result = noscript.experiment(case['html'], {k: case[k] for k in ('required_markers', 'forbidden_markers')})
                    for mode in ('enabled', 'disabled'):
                        reading = result['readings'][mode]
                        actual = [s['text'] for s in reading['segments']] if reading['complete'] else None
                        self.assertEqual(actual, case[mode+'_segments'])
                        self.assertEqual(reading['markers']['candidate'], case[mode+'_candidate'])
                        if not reading['complete']:
                            self.assertEqual(reading['segments'], [])
                    self.assertEqual(result['candidate_consensus'], case['candidate_consensus'])
                    self.assertEqual(result['normative_effect'], 'none')

    def test_offsets_bind_original_unicode_slices_and_decoded_marker_positions(self):
        source = '<html><head></head><body>😀 &amp;<noscript>&amp;</noscript>\r\n</body></html>'
        result = noscript.experiment(source, {'required_markers':['😀 &'], 'forbidden_markers':[]})
        first = result['readings']['disabled']['segments'][0]
        start = source.index('😀')
        self.assertEqual(first, {'start':start, 'end':start+len('😀 &amp;'), 'text':'😀 &', 'decoding':'character-references'})
        raw = result['readings']['enabled']['segments'][1]
        self.assertEqual(source[raw['start']:raw['end']], '&amp;')
        self.assertEqual(raw['text'], '&amp;')
        hit = result['readings']['disabled']['markers']['evidence']['required_markers'][0]['matches'][0]
        self.assertEqual(hit, {'segment':0, 'text_start':0, 'text_end':3})
        self.assertEqual(result['readings']['disabled']['segments'][-1]['text'], '\r\n')
        self.assertEqual(result['source_utf8_sha256'], hashlib.sha256(source.encode()).hexdigest())

    def test_both_fail_retains_distinct_reasons_without_marker_union(self):
        source = '<html><head></head><body><noscript><img alt="A">&#66;</noscript></body></html>'
        result = noscript.experiment(source, {'required_markers':['A','B'], 'forbidden_markers':[]})
        self.assertEqual(result['candidate_consensus'], 'fail')
        self.assertEqual(result['readings']['enabled']['markers']['missing'], ['B'])
        self.assertEqual(result['readings']['disabled']['markers']['missing'], ['A'])

    def test_refusal_after_known_failure_never_uses_prefix(self):
        source = '<html><head></head><body>Forbidden<noscript><iframe></iframe></noscript></body></html>'
        result = noscript.experiment(source, {'required_markers':['Expected'], 'forbidden_markers':['Forbidden']})
        self.assertEqual(result['readings']['enabled']['markers']['candidate'], 'fail')
        self.assertFalse(result['readings']['disabled']['complete'])
        self.assertEqual(result['readings']['disabled']['segments'], [])
        self.assertEqual(result['candidate_consensus'], 'inconclusive')

    def test_no_criteria_means_no_candidate_not_implicit_success(self):
        result = noscript.experiment('<html><head></head><body><noscript>Expected</noscript></body></html>')
        self.assertIsNone(result['candidate_consensus'])
        self.assertIsNone(result['criteria'])
        self.assertTrue(all('markers' not in x for x in result['readings'].values()))

    def test_documented_lexical_differences_are_not_dom_claims(self):
        for body, expected in [('<pre>\nExpected</pre>', ['\nExpected']),
                               ('<p>A<li>B</li></p>', ['A','B']),
                               ('<p>A<summary>B</summary></p>', ['A','B'])]:
            source = '<html><head></head><body>'+body+'</body></html>'
            for mode in ('enabled', 'disabled'):
                with self.subTest(body=body, mode=mode):
                    result = noscript.reading(source, mode)
                    self.assertTrue(result['complete'])
                    self.assertEqual([s['text'] for s in result['segments']], expected)
                    self.assertIn('not HTML5', result['completeness_scope'])

    def test_limits_and_unsupported_contexts_keep_whole_reading_unavailable(self):
        source = '<html><head></head><body>Expected<noscript>Other</noscript></body></html>'
        for field, limit in [('MAX_CHARS',10), ('MAX_TOKENS',3), ('MAX_DEPTH',2)]:
            with self.subTest(field=field), patch.object(noscript, field, limit):
                result = noscript.reading(source, 'enabled')
                self.assertFalse(result['complete'])
                self.assertEqual(result['segments'], [])
        for bad in ('textarea', 'template', 'iframe', 'select', 'table', 'math', 'xmp', 'custom-element'):
            with self.subTest(tag=bad):
                result = noscript.reading('<html><head></head><body>Expected<'+bad+'></'+bad+'></body></html>', 'disabled')
                self.assertFalse(result['complete'])
        with self.assertRaises(Unknown):
            noscript.reading(source, 'per-element-vote')

    def test_invalid_or_contradictory_markers_are_not_candidates(self):
        for criteria in (None, {}, {'required_markers':[], 'forbidden_markers':[]},
                         {'required_markers':[' '], 'forbidden_markers':[]},
                         {'required_markers':['Expected','Expected'], 'forbidden_markers':[]},
                         {'required_markers':['Expected'], 'forbidden_markers':['pect']},
                         {'required_markers':['x'*4097], 'forbidden_markers':[]},
                         {'required_markers':[], 'forbidden_markers':[], 'policy':'stable'}):
            with self.subTest(criteria=criteria), self.assertRaises(Unknown):
                noscript.validate_criteria(criteria)

    def test_active_extractor_still_refuses_nonempty_noscript(self):
        source = '<html><head></head><body>Expected<noscript><img src="x"></noscript></body></html>'
        with self.assertRaises(Unknown):
            extract(source)
        result = noscript.experiment(source, {'required_markers':['Expected'], 'forbidden_markers':[]})
        self.assertEqual(result['candidate_consensus'], 'pass')
        self.assertEqual(json.loads((ROOT/'spec/protocol.json').read_text())['version'], '0.1.0-draft.7')

    def test_isolated_cli_needs_no_evaluator_collector_or_private_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in noscript.SOURCE_FILES:
                target = root/name
                target.parent.mkdir(exist_ok=True, parents=True)
                shutil.copyfile(ROOT/name, target)
            source = root/'source.html'
            source.write_bytes(b'<html><head></head><body>Expected\r\n<noscript><img src="x"></noscript></body></html>')
            criteria = root/'criteria.json'
            criteria.write_text(json.dumps({'required_markers':['Expected\r\n'], 'forbidden_markers':[]}))
            output = root/'result.json'
            command = [sys.executable, '-I', str(root/'experiments/noscript.py'), str(source), '--criteria', str(criteria), '--output', str(output)]
            run = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 0, run.stderr)
            result = json.loads(output.read_text())
            self.assertEqual(result['candidate_consensus'], 'pass')
            self.assertEqual(result['source_utf8_sha256'], hashlib.sha256(source.read_bytes()).hexdigest())
            before = output.read_bytes()
            again = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=10)
            self.assertEqual(again.returncode, 64)
            self.assertEqual(output.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
