"""Authored method fixtures + adversarial evidence/aggregation checks, not an SEO parser."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep

CORPUS = tsep.read_json(ROOT/'tests/fixtures/control-cases.json')
CASES = {c['id']: c for c in CORPUS['cases']}
TARGET = 'urn:tsep:synthetic:declared-population'
DATE = '2026-10-09T10:00:00Z'


def materialize(case, root):
    """Bundle supplied fictional inputs and authored verdicts; no network/SEO inference."""
    report = tsep.initialize([TARGET], [case['control_id']], 'custom',
                             'Synthetic reference author', 'Synthetic declared population',
                             'Fixture-only URL/family inventory in intent; no live site')
    report['issued_at'] = DATE
    report['scope']['exclusions'] = ['All real sites and unselected controls']
    for kind, content in case['evidence'].items():
        path = root/(kind+'.txt')
        path.write_text('SYNTHETIC / SYNTHÉTIQUE\n'+content+'\n', encoding='utf-8')
        report['artifacts'].append({'id':kind, 'path':path.name, 'sha256':tsep.digest(path),
                                   'kind':kind, 'observed_at':DATE, 'targets':[TARGET],
                                   'access':'synthetic', 'description':'Authored fixture, not collected evidence'})
    result = report['results'][0]
    result.update(status=case['expected_status'], evaluation_state=(
        'inconclusive' if case['expected_status']=='NT' else 'complete'),
        reason=case['description']['en']+' / '+case['description']['fr'],
        procedure='Review authored rule judgments against supplied synthetic inputs; no automatic SEO interpretation.',
        evaluated_targets=[TARGET], evidence_ids=list(case['evidence']), atomic_results=[])
    for entry in case['atomic_results']:
        atom = copy.deepcopy(entry)
        atom.update(target=TARGET, reason=entry['reason']['en']+' / '+entry['reason']['fr'])
        result['atomic_results'].append(atom)
    return report


class AtomicRules(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def rejected(self, report, message):
        with self.assertRaisesRegex(tsep.Invalid, message):
            tsep.validate(report, self.root)

    def test_method_case_reports(self):
        self.assertTrue(CORPUS['synthetic'])
        self.assertEqual(len(CASES), len(CORPUS['cases']))
        self.assertEqual(CORPUS['protocol_version'], tsep.read_json(tsep.PROTOCOL_PATH)['version'])
        for case in CASES.values():
            with self.subTest(case=case['id']):
                self.assertEqual(set(case['description']), {'fr','en'})
                summary = tsep.validate(materialize(case, self.root), self.root)
                self.assertEqual(summary['decision'], case['expected_gate'])
                self.assertTrue(summary['synthetic_evidence'])
                self.assertEqual(len(summary['unevaluated_controls']),43)

    def test_each_rule_has_pass_fail_and_inconclusive_reference_cases(self):
        outcomes = {}
        for case in CASES.values():
            for atom in case['atomic_results']:
                self.assertEqual(set(atom['reason']), {'fr','en'})
                outcomes.setdefault(atom['rule_id'],set()).add(atom['outcome'])
        rules=[r for c in tsep.read_json(tsep.PROTOCOL_PATH)['controls'] for r in c.get('rules',[])]
        self.assertEqual(set(outcomes), {r['id'] for r in rules})
        for rule in rules:
            with self.subTest(rule=rule['id']):
                self.assertTrue({'pass','fail','inconclusive'} <= outcomes[rule['id']])
                if rule['na_inputs']:
                    self.assertIn('not-applicable',outcomes[rule['id']])

    def test_missing_rule_cannot_be_hidden_by_complete_input_kinds(self):
        for key in ('TS01-ok','TS07-allow','TS10-aligned'):
            report = materialize(CASES[key], self.root)
            report['results'][0]['atomic_results'].pop()
            self.rejected(report, 'every atomic rule')

    def test_missing_matrix_cannot_claim_c(self):
        report=materialize(CASES['TS01-ok'],self.root)
        del report['results'][0]['atomic_results']
        self.rejected(report,'every atomic rule')

    def test_one_target_cannot_cover_another_even_with_declared_control_inputs(self):
        report=materialize(CASES['TS10-aligned'],self.root)
        second='urn:tsep:synthetic:other-family'
        report['scope']['targets'].append(second)
        report['results'][0]['evaluated_targets'].append(second)
        for artifact in report['artifacts']: artifact['targets'].append(second)
        self.rejected(report,'every atomic rule')

    def test_unknown_duplicate_and_foreign_rules_rejected(self):
        for rid in ('TS01-A99','TS07-A01','TS01-A01'):
            report=materialize(CASES['TS01-ok'],self.root)
            atom=copy.deepcopy(report['results'][0]['atomic_results'][0]); atom['rule_id']=rid
            report['results'][0]['atomic_results'].append(atom)
            self.rejected(report,'Unknown or foreign|Duplicate')

    def test_rule_evidence_must_be_linked_and_targeted(self):
        report=materialize(CASES['TS01-ok'],self.root)
        report['results'][0]['atomic_results'][0]['evidence_ids'].append('unlinked')
        self.rejected(report,'not linked')
        report=materialize(CASES['TS01-ok'],self.root)
        second='urn:tsep:synthetic:other'
        report['scope']['targets'].append(second)
        report['results'][0].update(status='NC')
        report['results'][0]['atomic_results'][0]['outcome']='fail'
        report['artifacts'][0]['targets']=[second]
        self.rejected(report,'does not cover its target')

    def test_conclusive_atomic_outcomes_need_evidence(self):
        report=materialize(CASES['TS01-login'],self.root)
        report['results'][0]['atomic_results'][1]['evidence_ids']=[]
        self.rejected(report,'requires evidence')

    def test_rule_pass_needs_its_own_input_coverage(self):
        report=materialize(CASES['TS10-aligned'],self.root)
        report['results'][0]['atomic_results'][3]['evidence_ids']=['intent']
        self.rejected(report,'Missing atomic input')

    def test_render_pass_requires_render_artifact(self):
        report=materialize(CASES['TS07-allow'],self.root)
        report['results'][0]['atomic_results'][2]['outcome']='pass'
        self.rejected(report,'Missing atomic input')

    def test_atomic_exemptions_need_positive_inputs_and_permission(self):
        report=materialize(CASES['TS01-ok'],self.root)
        report['results'][0]['atomic_results'][0]['outcome']='not-applicable'
        self.rejected(report,'exemption is not allowed')
        report=materialize(CASES['TS10-no-sitemap'],self.root)
        report['results'][0]['atomic_results'][2]['evidence_ids']=['intent']
        self.rejected(report,'Missing atomic input')

    def test_fail_cannot_be_laundered_as_unknown_or_success(self):
        for status,state in [('C','complete'),('NT','inconclusive')]:
            report=materialize(CASES['TS01-login'],self.root)
            report['results'][0].update(status=status,evaluation_state=state)
            self.rejected(report,'cannot yield C|must remain NC')

    def test_inconclusive_cannot_be_promoted_to_c(self):
        report=materialize(CASES['TS01-timeout'],self.root)
        report['results'][0].update(status='C',evaluation_state='complete')
        self.rejected(report,'cannot yield C')

    def test_nc_needs_a_contradiction_but_can_preserve_gaps(self):
        report=materialize(CASES['TS01-ok'],self.root)
        report['results'][0]['status']='NC'
        self.rejected(report,'requires an evidenced atomic contradiction')
        report=materialize(CASES['TS01-login'],self.root)
        report['scope']['targets'].append('urn:tsep:synthetic:unobserved')
        self.assertEqual(tsep.validate(report,self.root)['decision'],'NO_GO')

    def test_whole_na_is_separate_from_atomic_exemptions(self):
        report=materialize(CASES['TS07-allow'],self.root)
        report['results'][0]['status']='NA'
        self.rejected(report,'cannot contain applicable atomic')
        report=materialize(CASES['TS10-not-applicable'],self.root)
        report['artifacts'][0]['kind']='http'
        self.rejected(report,'requires applicability evidence')

    def test_old_format_is_rejected_even_with_new_protocol_hash(self):
        report=materialize(CASES['TS01-ok'],self.root)
        report['format_version']='1'
        self.rejected(report,'Wrong constant')

    def test_probe_success_cannot_claim_selected_three_controls_conform(self):
        report=materialize(CASES['TS01-ok'],self.root)
        untested=tsep.initialize([TARGET],['TS07','TS10'],'custom','author','scope','fixture')
        report['controls']+=['TS07','TS10']
        report['results']+=untested['results']
        summary=tsep.validate(report,self.root)
        self.assertEqual(summary['decision'],'NO_GO')
        self.assertEqual(summary['counts']['NT'],2)


if __name__ == '__main__':
    unittest.main()
