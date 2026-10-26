"""Current-edition aggregation, applicability and exact historical inverses."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import tsep
from adapters.captures import build
from adapters.replay import replay
from tests.automation_history import ROOT, protocol_before_automation, method_before_automation
from tests.test_public_probes import target06


class AutomationIntegration(unittest.TestCase):
    def test_exact_contract_delta_and_projection(self):
        old = protocol_before_automation()
        self.assertEqual(old['version'], '0.3.0-draft.9')
        current = tsep.read_json(tsep.PROTOCOL_PATH)
        self.assertEqual(len(current['controls']), 44)
        self.assertEqual(sum(len(c['rules']) for c in current['controls']), 100)
        before = {c['id']:c for c in old['controls']}
        changed = set()
        for c in current['controls']:
            previous = before[c['id']]
            if c == previous:
                continue
            changed.add(c['id'])
            self.assertEqual(c['rule_version'], '0.3.0-draft.10')
            if c['id'] in ('TS03', 'TS06'):
                self.assertEqual(c['rules'][:-1], previous['rules'])
                self.assertEqual(c['rules'][-1]['id'], c['id']+'-A02')
                self.assertEqual(c['rules'][-1]['na_inputs'], [])
                self.assertEqual({k for k in c if c[k] != previous[k]},
                    {'acceptance','applicability','evidence','limitations','procedure','rule_version','rules'})
            else:
                self.assertEqual(c['id'], 'TS07')
                self.assertEqual({k for k in c if c[k] != previous[k]}, {'rule_version','rules'})
                self.assertEqual(c['rules'][0], previous['rules'][0])
                self.assertEqual(c['rules'][2], previous['rules'][2])
                self.assertEqual({k for k in c['rules'][1] if c['rules'][1][k] != previous['rules'][1][k]},
                                 {'procedure','limitations'})
        self.assertEqual(changed, {'TS03','TS06','TS07'})

    def test_projection_rejects_changes_inside_and_outside_automation(self):
        native_read = tsep.read_json
        for control in ('TS01', 'TS03', 'TS06', 'TS07', 'TS44'):
            with self.subTest(control=control):
                value = native_read(tsep.PROTOCOL_PATH)
                next(c for c in value['controls'] if c['id']==control)['title']['fr'] += ' tampered'
                def mutated(path):
                    return value if path == tsep.PROTOCOL_PATH else native_read(path)
                with patch.object(tsep, 'read_json', side_effect=mutated), self.assertRaisesRegex(ValueError, 'Undeclared'):
                    protocol_before_automation()

    def test_method_migration_preserves_every_previous_atom(self):
        previous = method_before_automation()
        current = tsep.read_json(ROOT/'tests/fixtures/control-cases.json')
        self.assertEqual(len(previous['cases']), 194)
        self.assertEqual(len(current['cases']), 202)
        changed = set()
        for old, new in zip(previous['cases'], current['cases']):
            self.assertEqual(old['id'], new['id'])
            self.assertEqual(old['atomic_results'], new['atomic_results'])
            self.assertEqual(old['evidence'], new['evidence'])
            if old != new:
                changed.add(old['id'])
                self.assertEqual(old['expected_status'], 'C')
                self.assertEqual(new['expected_status'], 'NT')
                self.assertEqual({k for k in old if old[k] != new[k]},
                                 {'description','expected_status','expected_gate'})
        self.assertEqual(changed, {'TS03-synthetic-matrix-complete','TS06-supplied-matrix-pass'})

    def inventory(self):
        fixture = tsep.read_json(ROOT/'tests/fixtures/ts06-access-cases.json')
        return copy.deepcopy(next(c['input'] for c in fixture['cases'] if c['id']=='ts06-dated-positive-na'))

    def bundle(self, data, root):
        source=root/'input.json';source.write_text(json.dumps(data))
        build(source, root/'bundle', assessor='Synthetic reviewer', label='Applicability counterexample',
              selection_method='Authored .invalid targets only', access='synthetic')
        return tsep.read_json(root/'bundle/report.json')

    def test_positive_inventory_retains_whole_na_export_and_replay(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);report=self.bundle(self.inventory(), root)
            self.assertEqual(report['results'][0]['status'], 'NA')
            self.assertEqual(report['results'][0]['atomic_results'], [])
            self.assertIn('every declared target', report['results'][0]['reason'])
            replay(root/'bundle', root/'replay')
            record=tsep.read_json(root/'replay/replay.json')
            self.assertTrue(record['same_report_results'])
            self.assertTrue(record['same_gate'])

    def test_missing_partial_future_or_unbound_inventory_never_becomes_na(self):
        def drop(t): t['intent'].pop('ts06_access')
        def partial(t): t['intent']['ts06_access']['inventory_review']['complete']=False
        def future(t): t['intent']['ts06_access']['inventory_review']['reviewed_at']='2099-01-01T00:00:00Z'
        def unbound(t): t['configuration']['ts06_access']['plan_sha256']='0'*64
        for mutate in (drop,partial,future,unbound):
            with self.subTest(mutation=mutate.__name__), tempfile.TemporaryDirectory() as folder:
                data=self.inventory();mutate(data['targets'][0])
                # Rebind malformed content where applicable so the specific
                # inventory condition, rather than only its hash, is exercised.
                if mutate in (partial,future):
                    from conformance.ts06_access import _hash
                    t=data['targets'][0];t['configuration']['ts06_access']['plan_sha256']=_hash(t['intent']['ts06_access'])
                self.assertNotIn(self.bundle(data, Path(folder))['results'][0]['status'], ('C','NA'))

    def test_inventory_for_one_target_does_not_exempt_another(self):
        with tempfile.TemporaryDirectory() as folder:
            data=self.inventory();other=copy.deepcopy(data['targets'][0])
            other['url']='https://other.invalid/private';other['intent'].pop('ts06_access')
            data['targets'].append(other)
            result=self.bundle(data, Path(folder))['results'][0]
            self.assertEqual(result['status'], 'NT')
            self.assertTrue(all(a['outcome']=='inconclusive' for a in result['atomic_results']))

    def test_selected_or_supplied_probe_conflicts_with_no_private_route_inventory(self):
        mutations=(
            lambda d:d['rules'].append('TS06-A02'),
            lambda d:d['targets'][0]['intent'].update(public_probe={}),
            lambda d:d['targets'][0]['configuration'].update(public_probe_sha256='0'*64),
            lambda d:d['targets'][0].update(anonymous_probe={}))
        for index,mutate in enumerate(mutations):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as folder:
                data=self.inventory();mutate(data)
                result=self.bundle(data, Path(folder))['results'][0]
                self.assertEqual(result['status'], 'NT')
                self.assertIn('conflicts', result['atomic_results'][0]['reason'])

    def test_later_private_probe_keeps_inventory_unknown_and_preserves_known_failure(self):
        for status,want in ((401,'NT'),(200,'NC')):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as folder:
                data=self.inventory();t=data['targets'][0];probe=target06(status)
                # The inventory is historical; a later explicitly private probe
                # cannot be erased by that older no-private-route declaration.
                t['url']=probe['url'];t['observed_at']=probe['observed_at']
                t['intent']['public_probe']=probe['intent']['public_probe']
                t['configuration']['public_probe_sha256']=probe['configuration']['public_probe_sha256']
                t['anonymous_probe']=probe['anonymous_probe'];data['rules'].append('TS06-A02')
                result=self.bundle(data, Path(folder))['results'][0]
                self.assertEqual(result['status'], want)
                self.assertEqual(result['atomic_results'][0]['outcome'], 'inconclusive')
                self.assertEqual(result['atomic_results'][1]['outcome'], 'pass' if status==401 else 'fail')


if __name__ == '__main__':
    unittest.main()
