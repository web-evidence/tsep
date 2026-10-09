"""Adversarial report-interchange cases, not an SEO conformance suite. Apache-2.0."""
import copy
import hashlib
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
import maintain


class Reports(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / 'examples/pass', self.root, dirs_exist_ok=True)
        self.report = tsep.read_json(self.root / 'report.json')

    def tearDown(self):
        self.temp.cleanup()

    def check(self, report=None):
        return tsep.validate(report or self.report, self.root)

    def rejected(self):
        with self.assertRaises((tsep.Invalid, ValueError, OSError)):
            self.check()

    def test_complete_single_control_remains_explicitly_partial(self):
        result = self.check()
        self.assertEqual(result['decision'], 'GO_WITH_RESERVATIONS')
        self.assertEqual(result['selected_controls'], 1)
        self.assertEqual(len(result['unevaluated_controls']), 43)

    def test_artifact_tampering(self):
        (self.root / 'http.txt').write_text('tampered')
        self.rejected()

    def test_missing_artifact(self):
        (self.root / 'http.txt').unlink()
        self.rejected()

    def test_path_traversal(self):
        self.report['artifacts'][0]['path'] = '../outside.txt'
        self.rejected()

    def test_absolute_path(self):
        self.report['artifacts'][0]['path'] = str(self.root / 'intent.txt')
        self.rejected()

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as other:
            outside = Path(other) / 'outside'
            outside.write_text('external')
            (self.root / 'link').symlink_to(outside)
            self.report['artifacts'][0].update(path='link', sha256=tsep.digest(outside))
            self.rejected()

    def test_protocol_fingerprint(self):
        self.report['protocol']['sha256'] = '0' * 64
        self.rejected()

    def test_protocol_version(self):
        self.report['protocol']['version'] = '1.0.0'
        self.rejected()

    def test_duplicate_result(self):
        self.report['results'].append(copy.deepcopy(self.report['results'][0]))
        self.rejected()

    def test_missing_result(self):
        self.report['controls'].append('TS07')
        self.rejected()

    def test_unknown_control(self):
        self.report['controls'][0] = 'TS99'
        self.rejected()

    def test_unknown_status(self):
        self.report['results'][0]['status'] = 'PASS'
        self.rejected()

    def test_status_cannot_downgrade_severity(self):
        self.report['results'][0]['severity'] = 'informational'
        self.rejected()

    def test_no_arbitrary_score(self):
        self.report['score'] = 100
        self.rejected()

    def test_no_sitewide_claim(self):
        self.report['claim'] = 'all-pages-certified'
        self.rejected()

    def test_no_evidenceless_pass(self):
        self.report['results'][0]['evidence_ids'] = []
        self.rejected()

    def test_no_unsupported_na(self):
        self.report['results'][0].update(status='NA', evidence_ids=[])
        self.rejected()

    def test_no_whitespace_reason(self):
        self.report['results'][0]['reason'] = '  '
        self.rejected()

    def test_required_input_is_not_an_optional_footnote(self):
        self.report['results'][0]['evidence_ids'] = ['intent']
        self.rejected()

    def test_one_url_cannot_satisfy_two_url_scope(self):
        self.report['scope']['targets'].append('https://example.com/other')
        self.rejected()

    def test_no_declared_coverage_without_input_coverage(self):
        second = 'https://example.com/other'
        self.report['scope']['targets'].append(second)
        self.report['results'][0]['evaluated_targets'].append(second)
        self.report['artifacts'][0]['targets'].append(second)
        self.rejected()

    def test_outside_scope_evidence(self):
        self.report['artifacts'][0]['targets'] = ['https://outside.example/']
        self.rejected()

    def test_missing_reference(self):
        self.report['results'][0]['evidence_ids'].append('missing')
        self.rejected()

    def test_duplicate_artifact(self):
        self.report['artifacts'].append(copy.deepcopy(self.report['artifacts'][0]))
        self.rejected()

    def test_no_fake_profile_badge(self):
        self.report['profile'] = 'TSEP-1'
        self.rejected()

    def test_profiles_start_untested_and_block_gate(self):
        for profile, expected in [('TSEP-1', 27), ('TSEP-2', 29), ('TSEP-3', 44)]:
            with self.subTest(profile=profile):
                report = tsep.initialize(['target'], None, profile, 'author', 'scope', 'declared')
                result = self.check(report)
                self.assertEqual(len(report['results']), expected)
                self.assertEqual(result['counts']['NT'], expected)
                self.assertEqual(result['decision'], 'NO_GO')

    def test_cannot_narrow_profile(self):
        with self.assertRaises(tsep.Invalid):
            tsep.initialize(['target'], ['TS01'], 'TSEP-1', 'author', 'scope', 'declared')

    def test_private_measurement_cannot_claim_public_profile(self):
        report = tsep.initialize(self.report['scope']['targets'], None, 'TSEP-1', 'author', 'scope', 'declared')
        report['artifacts'] = [copy.deepcopy(self.report['artifacts'][1])]
        report['artifacts'][0].update(kind='field-data', access='restricted')
        self.report = report
        self.rejected()

    def test_no_automated_whole_control_pass_claim(self):
        self.report['assessor']['mode'] = 'automatic'
        self.rejected()

    def test_incomplete_cannot_be_passed(self):
        self.report['results'][0]['evaluation_state'] = 'inconclusive'
        self.rejected()

    def test_untested_cannot_be_complete(self):
        self.report['results'][0]['status'] = 'NT'
        self.rejected()

    def test_unstarted_cannot_contain_observations(self):
        self.report['results'][0].update(status='NT', evaluation_state='not-started')
        self.rejected()

    def test_after_issuance_evidence(self):
        self.report['artifacts'][0]['observed_at'] = '2027-10-09T10:00:00Z'
        self.rejected()

    def test_ambiguous_time(self):
        self.report['issued_at'] = '2026-10-09T10:00:00'
        self.rejected()

    def test_impossible_date(self):
        self.report['issued_at'] = '2026-02-30T10:00:00Z'
        self.rejected()

    def test_duplicate_json_key(self):
        file = self.root / 'duplicate.json'
        file.write_text('{"status":"C","status":"NC"}')
        with self.assertRaises(tsep.Invalid):
            tsep.read_json(file)

    def test_non_finite_json(self):
        file = self.root / 'nonfinite.json'
        file.write_text('{"score":NaN}')
        with self.assertRaises(tsep.Invalid):
            tsep.read_json(file)

    def test_nonblocking_unknown_prevents_go(self):
        report = tsep.initialize(['target'], ['TS02'], 'custom', 'author', 'scope', 'declared')
        self.assertEqual(self.check(report)['decision'], 'INCOMPLETE')

    def test_major_failure_requires_review(self):
        self.report['controls'] = ['TS02']
        self.report['results'][0].update(control_id='TS02', status='NC')
        self.assertEqual(self.check()['decision'], 'REVIEW')

    def test_minor_failure_preserved_in_go_reservations(self):
        self.report['controls'] = ['TS09']
        self.report['results'][0].update(control_id='TS09', status='NC')
        result = self.check()
        self.assertEqual(result['decision'], 'GO_WITH_RESERVATIONS')
        self.assertEqual(result['counts']['NC'], 1)

    def test_all_na_is_not_success(self):
        self.report['results'][0].update(status='NA', reason='Declared no public canonical target; synthetic status test only.')
        self.assertEqual(self.check()['decision'], 'INCOMPLETE')

    def test_failing_counterexample_can_cover_subset(self):
        self.report['scope']['targets'].append('https://example.com/other')
        self.report['results'][0].update(status='NC', reason='One observed contradiction is enough to fail the whole declared set.')
        self.assertEqual(self.check()['decision'], 'NO_GO')

    def test_five_earl_outcomes_are_distinct(self):
        expected = [('C','complete','passed'), ('NC','complete','failed'),
                    ('NA','complete','inapplicable'), ('NT','not-started','untested'),
                    ('NT','inconclusive','cantTell')]
        for status, state, outcome in expected:
            with self.subTest(status=status, state=state):
                report = copy.deepcopy(self.report)
                report['results'][0].update(status=status, evaluation_state=state)
                if state == 'not-started':
                    report['results'][0].update(evaluated_targets=[], evidence_ids=[])
                summary = self.check(report)
                earl = tsep.earl(report, summary)
                self.assertEqual(earl['@graph'][2]['earl:result']['earl:outcome']['@id'], 'earl:'+outcome)
                self.assertEqual(earl['@graph'][2]['earl:subject']['@id'], '_:scope')

    def test_exit_codes_validate_vs_gate(self):
        cases = [('pass', 'validate', 0), ('pass', 'gate', 0),
                 ('fail', 'validate', 0), ('fail', 'gate', 1), ('partial', 'gate', 1)]
        for case, command, code in cases:
            with self.subTest(case=case, command=command):
                result = subprocess.run([sys.executable, str(ROOT/'tsep.py'), command,
                                         str(ROOT/'examples'/case/'report.json')], capture_output=True)
                self.assertEqual(result.returncode, code, result.stderr)

    def test_invalid_exit_code(self):
        (self.root / 'http.txt').write_text('tampered')
        result = subprocess.run([sys.executable, str(ROOT/'tsep.py'), 'gate',
                                 str(self.root/'report.json')], capture_output=True)
        self.assertEqual(result.returncode, 64)

    def test_deterministic_example_regeneration(self):
        expected = {p.relative_to(ROOT/'examples'): p.read_bytes()
                    for case in ('pass', 'fail', 'partial')
                    for p in (ROOT/'examples'/case).rglob('*') if p.is_file()}
        destination = self.root / 'regenerated'
        subprocess.run([sys.executable, str(ROOT/'examples/replay.py'),
                        '--output-dir', str(destination)], check=True, capture_output=True)
        actual = {p.relative_to(destination): p.read_bytes() for p in destination.rglob('*') if p.is_file()}
        self.assertEqual(expected, actual)

    def test_bilingual_generation_and_frozen_provenance(self):
        maintain.check()


if __name__ == '__main__':
    unittest.main()
