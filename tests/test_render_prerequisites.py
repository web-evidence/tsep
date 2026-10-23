from tests.lot1_history import controls_before_lot1
"""Frozen synthetic countercases; no real browser, site or human audit."""
import copy
import hashlib
import json
import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tsep
from adapters import captures, replay
from conformance.evidence_dossier import digest
from conformance.evaluate import evaluate

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT/'tests/fixtures/render-prerequisites-v2.json'

def cases():
    return tsep.read_json(FIXTURE)['cases']

class RenderPrerequisites(unittest.TestCase):
    def test_prefrozen_countercases_and_unchanged_inputs(self):
        self.assertEqual(hashlib.sha256(FIXTURE.read_bytes()).hexdigest(), FIXTURE.with_suffix('.sha256').read_text().strip())
        self.assertEqual(len(cases()), 21)
        with patch.object(socket, 'socket', side_effect=AssertionError('No acquisition')):
            for case in cases():
                with self.subTest(case=case['id']):
                    before = copy.deepcopy(case['input'])
                    actual = evaluate(case['input'])
                    self.assertEqual([{k:r[k] for k in ('rule_id','target','outcome')} for r in actual], case['expected'])
                    self.assertEqual(case['input'], before)

    def test_other_ninety_five_rule_definitions_preserved(self):
        baseline = tsep.read_json(ROOT/'provenance/v030-draft4-rule-baseline.json')['rules']
        changed = {'TS30-A01','TS30-A02','TS37-A03'}
        protocol = dict(tsep.read_json(tsep.PROTOCOL_PATH),controls=controls_before_lot1())
        actual = {r['id']:digest(r) for c in protocol['controls'] for r in c['rules']}
        self.assertEqual(len(actual), 98)
        self.assertEqual({key for key in actual if actual[key] != baseline[key]['sha256']}, changed)
        for control in protocol['controls']:
            for rule in control['rules']:
                self.assertEqual(control['rule_version'], '0.3.0-draft.5' if control['id'] in ('TS30','TS37') else baseline[rule['id']]['version'])

    def test_nt_nc_packages_and_offline_replay(self):
        selected = {'h1-hidden':'NT', 'h1-hidden-title-conflict':'NC', 'css-before-http':'NC'}
        for name, status in selected.items():
            case = next(c for c in cases() if c['id']=='render-prerequisites-v2-'+name)
            with self.subTest(case=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory);source=root/'input.json';source.write_text(json.dumps(case['input']))
                captures.build(source,root/'bundle',assessor='Fictional',label='SYNTHETIC prerequisites',selection_method='Authored finite countercase',access='synthetic')
                report=tsep.read_json(root/'bundle/report.json')
                self.assertEqual(report['results'][0]['status'],status)
                self.assertTrue(tsep.decision(report)['synthetic_evidence'])
                with patch.object(socket,'socket',side_effect=AssertionError('No acquisition')):
                    result=replay.replay(root/'bundle',root/'replay')
                self.assertTrue(result['same_atomic_results']);self.assertTrue(result['same_gate'])

if __name__=='__main__':
    unittest.main()
