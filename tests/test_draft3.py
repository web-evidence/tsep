"""Behavioral conformance, mutation safety, automatic claims and atomic EARL; Apache-2.0."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from conformance.evaluate import evaluate
from conformance.run import run
from test_atomic_rules import CASES, materialize


class Draft3(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for name in ('http.txt', 'intent.txt'):
            shutil.copyfile(ROOT/'examples/pass'/name, self.root/name)
        self.report = tsep.read_json(ROOT/'examples/pass/report.json')
        self.path = self.root/'report.json'

    def tearDown(self):
        self.temp.cleanup()

    def automatic(self):
        self.report['assessor'].update(mode='automatic', tool={'name': 'Synthetic test interpreter', 'version': '1'})

    def test_automatic_c_allowed_with_every_rule_and_tool(self):
        self.automatic()
        self.assertEqual(tsep.validate(self.report, self.root)['counts']['C'], 1)

    def test_automatic_c_rejects_missing_or_blank_tool_metadata(self):
        self.automatic()
        for tool in (None, {}, {'name': 'X'}, {'version': '1'}, {'name': ' ', 'version': '1'}, {'name': 'X', 'version': ''}):
            with self.subTest(tool=tool):
                report = copy.deepcopy(self.report)
                if tool is None:
                    del report['assessor']['tool']
                else:
                    report['assessor']['tool'] = tool
                with self.assertRaises(tsep.Invalid):
                    tsep.validate(report, self.root)

    def test_automatic_c_rejects_semi_auto_and_manual_rules(self):
        for case in ('TS07-allow', 'TS10-aligned'):
            with self.subTest(case=case):
                report = materialize(CASES[case], self.root)
                report['assessor'].update(mode='automatic', tool={'name': 'X', 'version': '1'})
                with self.assertRaisesRegex(tsep.Invalid, 'every control rule'):
                    tsep.validate(report, self.root)

    def test_automatic_c_rejects_control_without_atomic_rules(self):
        report = copy.deepcopy(self.report)
        report['controls'] = ['TS08']
        report['results'][0]['control_id'] = 'TS08'
        del report['results'][0]['atomic_results']
        report['assessor'].update(mode='automatic', tool={'name': 'X', 'version': '1'})
        with self.assertRaisesRegex(tsep.Invalid, 'every control rule'):
            tsep.validate(report, self.root)

    def test_automatic_metadata_does_not_bypass_incomplete_matrix(self):
        self.automatic()
        self.report['results'][0]['atomic_results'].pop()
        with self.assertRaisesRegex(tsep.Invalid, 'every atomic rule'):
            tsep.validate(self.report, self.root)

    def test_earl_each_atomic_outcome_and_parent_link(self):
        seen = set()
        mapping = {'pass': 'passed', 'fail': 'failed', 'inconclusive': 'cantTell', 'not-applicable': 'inapplicable'}
        for case in CASES.values():
            report = materialize(case, self.root)
            summary = tsep.validate(report, self.root)
            graph = tsep.earl(report, summary)['@graph']
            atoms = report['results'][0]['atomic_results']
            exported = [x for x in graph if 'dct:isPartOf' in x]
            self.assertEqual(len(exported), len(atoms))
            for atom, assertion in zip(atoms, exported):
                seen.add(atom['outcome'])
                self.assertEqual(assertion['earl:subject']['@id'], atom['target'])
                self.assertEqual(assertion['earl:test']['@id'], 'urn:tsep:'+report['protocol']['version']+':'+atom['rule_id'])
                self.assertEqual(assertion['earl:result']['earl:outcome']['@id'], 'earl:'+mapping[atom['outcome']])
                self.assertEqual(assertion['dct:isPartOf']['@id'], graph[2]['@id'])
        self.assertEqual(seen, set(mapping))

    def test_earl_two_targets_are_not_collapsed(self):
        target = 'https://example.com/other'
        self.report['scope']['targets'].append(target)
        result = self.report['results'][0]
        result['evaluated_targets'].append(target)
        for artifact in self.report['artifacts']:
            artifact['targets'].append(target)
        result['atomic_results'] += [dict(atom, target=target) for atom in list(result['atomic_results'])]
        graph = tsep.earl(self.report, tsep.validate(self.report, self.root))['@graph']
        atoms = [a for a in graph if 'dct:isPartOf' in a]
        self.assertEqual(len(atoms), 4)
        self.assertEqual(len({a['@id'] for a in atoms}), 4)
        self.assertEqual({a['earl:subject']['@id'] for a in atoms}, set(self.report['scope']['targets']))

    def cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT/'tsep.py'), *map(str, args)],
                              text=True, encoding='utf-8', capture_output=True, timeout=15)

    def init_cli(self):
        result = self.cli('init', '--target', self.report['scope']['targets'][0], '--controls', 'TS01',
                          '--assessor', 'Synthetic author', '--label', 'Synthetic workflow',
                          '--selection-method', 'One fictional target')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.path.write_text(result.stdout)

    def add_cli(self, kind):
        return self.cli('add-evidence', self.path, '--id', kind, '--path', kind+'.txt', '--kind', kind,
                        '--target', self.report['scope']['targets'][0], '--observed-at', '2026-10-09T10:00:00Z',
                        '--access', 'synthetic', '--description', 'Synthetic fixture')

    def record_cli(self):
        return self.cli('record', self.path, '--control', 'TS01', '--status', 'C',
                        '--reason', 'Two authored passing judgments', '--procedure', 'Fixture replay',
                        '--target', self.report['scope']['targets'][0], '--evidence', 'http',
                        '--evidence', 'intent', '--atomic-results', self.root/'atoms.json')

    def test_init_add_evidence_record_gate_workflow(self):
        self.init_cli()
        self.assertEqual(self.cli('gate', self.path).returncode, 1)
        for kind in ('http', 'intent'):
            added = self.add_cli(kind)
            self.assertEqual(added.returncode, 0, added.stderr)
        atoms = self.report['results'][0]['atomic_results']
        (self.root/'atoms.json').write_text(json.dumps(atoms))
        recorded = self.record_cli()
        self.assertEqual(recorded.returncode, 0, recorded.stderr)
        report = tsep.read_json(self.path)
        self.assertEqual(report['artifacts'][0]['sha256'], tsep.digest(self.root/'http.txt'))
        self.assertEqual(report['results'][0]['atomic_results'], atoms)
        gated = self.cli('gate', self.path, '--summary', '--lang', 'fr')
        self.assertEqual(gated.returncode, 0, gated.stderr)
        self.assertIn('1/44', gated.stdout)
        self.assertIn('C=1', gated.stdout)
        self.assertIn('aucune conformité globale', gated.stdout)
        self.assertIn('synthétiques : oui', gated.stdout)
        # Rejected partial rewrite leaves the established file byte-for-byte unchanged.
        before = self.path.read_bytes()
        (self.root/'atoms.json').write_text(json.dumps(atoms[:1]))
        self.assertEqual(self.record_cli().returncode, 64)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(self.add_cli('http').returncode, 64)
        self.assertEqual(self.path.read_bytes(), before)

    def test_evidence_future_date_and_self_reference_preserve_report(self):
        self.init_cli()
        before = self.path.read_bytes()
        for path, date in [('http.txt', '2999-01-01T00:00:00Z'), ('report.json', '2020-01-01T00:00:00Z')]:
            bad = self.cli('add-evidence', self.path, '--id', 'bad', '--path', path, '--kind', 'http',
                           '--target', self.report['scope']['targets'][0], '--observed-at', date,
                           '--access', 'synthetic', '--description', 'invalid fixture')
            self.assertEqual(bad.returncode, 64, bad.stdout)
            self.assertEqual(self.path.read_bytes(), before)

    def test_webmaster_engine_is_required_and_google_series_is_not_generic(self):
        target = self.report['scope']['targets'][0]
        report = tsep.initialize([target], ['TS08'], 'custom', 'Author', 'Synthetic', 'Fixture')
        control = next(c for c in tsep.read_json(tsep.PROTOCOL_PATH)['controls'] if c['id']=='TS08')
        # Supply each required kind, replacing Search Console with typed engine evidence.
        for kind in control['required_inputs']:
            path = self.root/(kind+'.txt');path.write_text('Synthetic engine observation')
            report['artifacts'].append({'id':kind, 'path':path.name, 'sha256':tsep.digest(path),
                'kind':'webmaster-tools' if kind=='search-console' else kind, 'observed_at':'2020-01-01T00:00:00Z',
                'targets':[target], 'description':'Synthetic', 'access':'synthetic'})
        engine = next(a for a in report['artifacts'] if a['kind']=='webmaster-tools')
        report['results'][0].update(status='C', evaluation_state='complete', reason='Authored engine finding',
            procedure='Fixture only', evaluated_targets=[target], evidence_ids=[a['id'] for a in report['artifacts']])
        with self.assertRaisesRegex(tsep.Invalid, 'requires its engine'):
            tsep.validate(report, self.root)
        engine['engine']='bing'
        with self.assertRaisesRegex(tsep.Invalid, 'Missing input coverage search-console'):
            tsep.validate(report, self.root)
        engine['engine']='google'
        self.assertEqual(tsep.validate(report, self.root)['counts']['C'], 1)
        engine.update(kind='search-console', engine='bing')
        with self.assertRaisesRegex(tsep.Invalid, 'Google-specific'):
            tsep.validate(report, self.root)

    def test_raw_conformance_and_contradictory_expected_outcome(self):
        corpus = tsep.read_json(ROOT/'conformance/cases.json')
        self.assertTrue(run(corpus)['success'])
        corpus['cases'][0]['expected'][0]['outcome']='fail'
        result = run(corpus)
        self.assertFalse(result['success'])
        self.assertEqual(result['failures'][0]['case'], 'complete-reference')

    def test_external_adapter_receives_inputs_only_and_cannot_omit_results(self):
        script = self.root/'adapter.py'
        script.write_text('import json,sys\ndata=json.load(sys.stdin)\nassert "expected" not in data\nprint("[]")\n')
        import shlex
        result = run(tsep.read_json(ROOT/'conformance/cases.json'),
                     shlex.join([sys.executable,str(script)]))
        self.assertFalse(result['success'])
        self.assertEqual(len(result['failures']), result['cases'])

    def test_raw_interpretation_changes_when_body_changes_not_expected(self):
        data = tsep.read_json(ROOT/'conformance/cases.json')['cases'][0]['input']
        data['targets'][0]['http'][0]['response'] = data['targets'][0]['http'][0]['response'].replace('Expected content','Different content')
        result = {a['rule_id']:a['outcome'] for a in evaluate(data)}
        self.assertEqual(result['TS01-A01'], 'pass')
        self.assertEqual(result['TS01-A02'], 'fail')

    def test_distribution_excludes_agent_instructions(self):
        self.assertNotIn('AGENTS.md', tsep.read_json(ROOT/'release-files.json')['files'])


if __name__ == '__main__':
    unittest.main()
