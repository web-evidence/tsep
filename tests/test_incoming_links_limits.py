"""Authored TS16 counterexample for an explicitly disclosed semantic boundary."""
import hashlib
import json
import copy
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

import tsep
from adapters import captures, replay
from conformance import incoming_links
from reports import html

ROOT = Path(__file__).resolve().parents[1]

class IncomingLinksSemanticLimits(unittest.TestCase):
    def test_nested_evidence_retains_other_supplied_http_and_render(self):
        case = json.loads((ROOT/'tests/fixtures/incoming-links-cases-v1.json').read_text())['cases'][0]
        data = copy.deepcopy(case['input']); target = data['targets'][0]
        target['http'] = copy.deepcopy(target['incoming_links']['documents'][0]['http'])
        target['render'] = {'retained_top_level': 'authored separate diagnostic'}
        other = copy.deepcopy(target); other.pop('incoming_links')
        originals = captures.pieces(other)
        extracted = captures.pieces(target)
        for kind in ('http','html','render'):
            self.assertEqual(extracted[kind]['other_supplied_evidence'], originals[kind])
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);raw=(json.dumps(data,ensure_ascii=False)+'\n').encode()
            (root/'input.json').write_bytes(raw)
            captures.build(root/'input.json',root/'bundle',assessor='Authored synthetic coexistence',
                           label='Synthetic TS16 originals',selection_method='Prior authored population',access='synthetic')
            self.assertEqual((root/'bundle/input.json').read_bytes(),raw)
            for kind in ('http','html','render'):
                self.assertEqual(tsep.read_json(root/'bundle/evidence'/('target-1-'+kind+'.json'))['record'],
                                 extracted[kind])

    def test_http200_error_navigation_does_not_authenticate_source_content(self):
        raw = (ROOT/'tests/fixtures/incoming-links-source-identity-v1.json').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         '8bacb3836d6f9be8036e00f530a2a10c524a66af73f4cb391fca1eef9a786343')
        case = json.loads(raw)['cases'][0]
        with tempfile.TemporaryDirectory() as folder, patch.object(socket, 'socket', side_effect=AssertionError('Offline')):
            root = Path(folder)
            input_bytes = (json.dumps(case['input'], ensure_ascii=False)+'\n').encode()
            (root/'input.json').write_bytes(input_bytes)
            diagnostic = incoming_links.assess_target(case['input']['targets'][0])
            self.assertEqual(diagnostic['outcome'], case['expected'])
            self.assertIn('HTTP200 error template', diagnostic['source_content_identity'])
            captures.build(root/'input.json',root/'bundle',assessor='Authored synthetic case',
                           label='Synthetic source identity boundary',selection_method='Prior authored population',access='synthetic')
            report = tsep.read_json(root/'bundle/report.json')
            self.assertEqual(report['results'][0]['status'], 'C')
            self.assertEqual((root/'bundle/input.json').read_bytes(),input_bytes)
            for lang, text in [('fr','les soft404 ne sont pas détectées'),('en','soft404s are not detected')]:
                rendered = html.render(root/'bundle/report.json',language=lang)
                self.assertIn(text, rendered)
                self.assertIn('HTTP200 error template',rendered)
            result = replay.replay(root/'bundle',root/'replayed')
            self.assertTrue(result['same_atomic_results']);self.assertTrue(result['same_gate'])
