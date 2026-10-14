"""Frozen TS17 transport-corruption versus evidence-qualification boundaries."""
import copy
import hashlib
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch
import tsep
from adapters import captures
from conformance import essential_links

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_SHA = '0db8e603262ac38ce60f56d2ebbc647a46a1ad26f638c17e890058ab8506cd92'

def cases():
    raw = (ROOT/'tests/fixtures/essential-links-dom-intake-v1.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != FIXTURE_SHA:
        raise ValueError('Changed prefrozen TS17 intake expectations')
    return json.loads(raw)['cases']

class EssentialLinksIntake(unittest.TestCase):
    def test_frozen_transport_refusals_and_missing_evidence(self):
        rows = cases()
        self.assertEqual(len(rows), 22)
        for row in rows:
            with self.subTest(case=row['id']), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                original = root/'input.json'
                raw = (json.dumps(row['input'], ensure_ascii=False, indent=2)+'\n').encode()
                original.write_bytes(raw)
                args = dict(assessor='Authored synthetic test; no human review', label='Synthetic TS17 intake',
                            selection_method='Prefrozen contradictory case', access='synthetic')
                with patch.object(socket, 'socket', side_effect=AssertionError('Offline synthetic import only')):
                    if row['expected_intake'] == 'technical-refusal':
                        with self.assertRaisesRegex(tsep.Invalid, 'TS17 DOM integrity|HTTP evidence integrity'):
                            captures.build(original, root/'bundle', **args)
                        self.assertFalse((root/'bundle').exists())
                    else:
                        captures.build(original, root/'bundle', **args)
                        self.assertEqual(tsep.read_json(root/'bundle/report.json')['results'][0]['status'], row['expected_intake'])
                        self.assertEqual((root/'bundle/input.json').read_bytes(), raw)
                self.assertEqual(original.read_bytes(), raw)

    def test_standalone_reader_retains_qualification_behavior(self):
        # Transport tightening does not silently migrate historical native rules.
        selected = {'snapshot-false-self-hash', 'support-false-self-hash',
                    'association-different-only', 'snapshot-hash-missing'}
        for row in cases():
            if row['id'] not in selected:
                continue
            with self.subTest(case=row['id']):
                target = copy.deepcopy(row['input']['targets'][0])
                result = essential_links.assess_target(target)
                self.assertEqual([result[x]['outcome'] for x in ('source', 'rendered')], ['pass', 'inconclusive'])
                self.assertEqual(target, row['input']['targets'][0])

if __name__ == '__main__':
    unittest.main()
