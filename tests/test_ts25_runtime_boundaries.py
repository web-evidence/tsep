"""Synthetic, exact serialized public boundaries on the actual runtime."""
import hashlib
import json
import platform
import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import tsep
from adapters import captures, replay
from conformance.evaluate import evaluate
from test_critical_presence_budgets import materialize
from ts25_runtime_fixtures import ROOT, fixture, calibrated, public_bytes, historical_expectation

class RuntimeBoundaries(unittest.TestCase):
    def test_actual_runtime_literal_byte_boundaries(self):
        fixtures=json.loads((ROOT/'tests/fixtures/critical-presence-cases-v1.json').read_text())['cases']
        for row in fixture()['cases']:
            with self.subTest(case=row['id']), tempfile.TemporaryDirectory() as folder, patch.object(socket, 'socket', side_effect=AssertionError('Offline only')):
                data=calibrated(row, fixtures, materialize, evaluate)
                notes=[]; values=evaluate(data,source_observations=notes)
                self.assertEqual([v['outcome'] for v in values],row['expected_native'])
                self.assertEqual(public_bytes(notes),row['bytes'])
                identities=[inv['supervisor']['python'] for n in notes for o in n['observations'] for inv in o.get('inventories',{}).values() if 'supervisor' in inv]
                self.assertEqual(identities,[platform.python_version()]*2)
                root=Path(folder); source=root/'input.json'; raw=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode();source.write_bytes(raw)
                args=dict(assessor='Fictional operator',label='SYNTHETIC actual-runtime TS25 boundary',selection_method='Authored boundary recipe',access='synthetic')
                if row['expected_public']=='technical-refusal':
                    with self.assertRaisesRegex(tsep.Invalid,'TS25'):captures.build(source,root/'out',**args)
                    self.assertFalse((root/'out').exists())
                else:
                    captures.build(source,root/'out',**args)
                    self.assertEqual(tsep.read_json(root/'out/report.json')['results'][0]['status'],'C')
                    self.assertEqual(sum(p.stat().st_size for p in (root/'out/observations').glob('*.json')),row['bytes'])
                    result=replay.replay(root/'out',root/'replay')
                    self.assertTrue(result['same_atomic_results']);self.assertTrue(result['same_gate'])
                self.assertEqual(source.read_bytes(),raw)

    def test_runtime_normalization_cannot_hide_changed_observation(self):
        fixtures=json.loads((ROOT/'tests/fixtures/critical-presence-cases-v1.json').read_text())['cases']
        rows=tsep.read_json(ROOT/'tests/fixtures/critical-presence-budget-v3.json')['cases']
        row=next(r for r in rows if r['id']=='public-diagnostics-exact4MiB')
        notes=[];evaluate(materialize(row,fixtures),source_observations=notes)
        historical_expectation(row,notes)
        notes[0]['target']='https://other.synthetic.invalid/'
        with self.assertRaises(AssertionError):historical_expectation(row,notes)

if __name__=='__main__':unittest.main()
