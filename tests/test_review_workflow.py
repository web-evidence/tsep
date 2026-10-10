"""Evidence-bound review workflow, never an actual human review. Apache-2.0."""
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from adapters.captures import build
from adapters.package import inventory, json_bytes, seal
from adapters.review import prepare, apply_review
from adapters.replay import replay

CASES = {c['id']: c['input'] for c in tsep.read_json(ROOT/'conformance/cases.json')['cases']}


class EvidenceWorkflow(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root/'source.json'
        self.bundle = self.root/'bundle'
        self.request = self.root/'request'
        self.answer = self.root/'completed.json'
        self.output = self.root/'reviewed'

    def tearDown(self):
        self.temp.cleanup()

    def build(self, case='canonical-content-review-missing', access='synthetic'):
        data = copy.deepcopy(CASES[case])
        self.source.write_bytes(json_bytes(data))
        build(self.source, self.bundle, assessor='Synthetic fixture author', label='Synthetic test case',
              selection_method='Authored fixture only; no collection', access=access, mode='manual')
        return data

    def prepare(self, case='canonical-content-review-missing', access='synthetic'):
        data = self.build(case, access)
        prepare(self.bundle, self.request)
        return data

    def fill(self, choice=None):
        request = tsep.read_json(self.request/'request.json')
        answer = tsep.read_json(self.request/'response-template.json')
        for task, row in zip(request['tasks'], answer['responses']):
            row.update(reviewer='Fictional reviewer in automated synthetic test',
                       observed_at=datetime.now(timezone.utc).isoformat(), provenance='synthetic-exercise',
                       assistance='Authored automated exercise; no human review occurred',
                       reason='Synthetic judgment supplied to exercise the evidence workflow',
                       examined_evidence=task['evidence'])
            for item in row['comparisons']:
                item.update(outcome=choice or task['choices'][0], reason='Authored synthetic comparison, not an observed human opinion')
        return answer

    def apply(self, answer):
        self.answer.write_bytes(json_bytes(answer))
        return apply_review(self.request, self.answer, self.output)

    def test_blank_template_has_no_conclusion_and_original_bytes_are_retained(self):
        self.prepare()
        self.assertEqual((self.request/'input.json').read_bytes(), self.source.read_bytes())
        answer = tsep.read_json(self.request/'response-template.json')
        for row in answer['responses']:
            self.assertIsNone(row['provenance'])
            for field in ('reviewer', 'observed_at', 'reason', 'assistance'):
                self.assertEqual(row[field], '')
            self.assertEqual(row['examined_evidence'], [])
            self.assertTrue(all(c['outcome'] is None and c['reason'] == '' for c in row['comparisons']))
        with self.assertRaisesRegex(ValueError, 'Missing human response'):
            self.apply(answer)
        self.assertFalse(self.output.exists())

    def test_synthetic_content_review_creates_new_input_and_replayable_bundle(self):
        before = self.prepare()
        original_bytes = self.source.read_bytes()
        with patch('socket.socket', side_effect=AssertionError('network forbidden')), patch('socket.getaddrinfo', side_effect=AssertionError('DNS forbidden')):
            receipt = self.apply(self.fill())
            replayed = replay(self.output/'bundle', self.root/'replayed')
        self.assertEqual(receipt['provenance'], ['synthetic-exercise'])
        self.assertTrue(replayed['replayed'])
        self.assertEqual((self.output/'original-input.json').read_bytes(), original_bytes)
        data = tsep.read_json(self.output/'reviewed-input.json')
        for old, new in zip(before['targets'], data['targets']):
            self.assertEqual(old['documents'], new['documents'])
            self.assertEqual(old['intent'], new['intent'])
            self.assertEqual(old['context'], new['context'])
            self.assertEqual(new['content_review']['previous_assessment_end'], old['observed_at'])
        self.assertEqual(tsep.read_json(self.output/'bundle/gate.json')['counts']['C'], 1)
        self.assertTrue(tsep.read_json(self.output/'bundle/gate.json')['synthetic_evidence'])
        self.assertEqual(inventory(self.output)['original-input.json'], tsep.digest(self.source))
        for task in tsep.read_json(self.request/'request.json')['tasks']:
            for proof in task['evidence']:
                self.assertEqual(tsep.digest(self.output/proof['path']), proof['sha256'])

    def test_incompatible_content_survives_as_failure(self):
        self.prepare()
        self.apply(self.fill('incompatible'))
        gate = tsep.read_json(self.output/'bundle/gate.json')
        self.assertEqual(gate['counts']['NC'], 1)
        self.assertEqual(gate['decision'], 'REVIEW')

    def test_access_review_cannot_invent_required_render(self):
        self.prepare('unresolved-access-review')
        self.apply(self.fill())
        atoms = tsep.read_json(self.output/'bundle/assessment.json')
        access = [a for a in atoms if a['rule_id'] == 'TS07-A02']
        self.assertTrue(access and all(a['outcome'] == 'pass' for a in access))
        self.assertFalse(any(a['rule_id'] == 'TS07-A03' and a['outcome'] == 'pass' for a in atoms))
        self.assertEqual(tsep.read_json(self.output/'bundle/gate.json')['counts']['NT'], 1)

    def test_positive_review_cannot_erase_source_directive_failure(self):
        self.prepare('unexpected-noindex')
        self.apply(self.fill())
        gate = tsep.read_json(self.output/'bundle/gate.json')
        self.assertEqual(gate['counts']['NC'], 1)
        self.assertEqual(gate['decision'], 'NO_GO')

    def test_review_missing_evidence_decision_reason_identity_or_assistance_is_rejected(self):
        self.prepare()
        mutations = [lambda a:a['responses'][0].update(reviewer=''),
                     lambda a:a['responses'][0].update(assistance=' '),
                     lambda a:a['responses'][0].update(examined_evidence=[]),
                     lambda a:a['responses'][0]['comparisons'][0].update(outcome=None),
                     lambda a:a['responses'][0]['comparisons'][0].update(reason=''),
                     lambda a:a['responses'][0]['comparisons'][0].update(url='https://example.com/unrelated'),
                     lambda a:a['responses'][0].update(provenance='human'),
                     lambda a:a.update(request_sha256='0'*64),
                     lambda a:a['responses'][0].update(observed_at='2000-01-01T00:00:00Z'),
                     lambda a:a['responses'][0].update(observed_at='2999-01-01T00:00:00Z')]
        for change in mutations:
            answer = self.fill(); change(answer)
            with self.subTest(change=mutations.index(change)), self.assertRaises(ValueError):
                self.apply(answer)
            self.assertFalse(self.output.exists())

    def test_public_input_cannot_accept_synthetic_review_as_human(self):
        self.prepare(access='public')
        with self.assertRaisesRegex(ValueError, 'provenance'):
            self.apply(self.fill())
        self.assertFalse(self.output.exists())

    def test_rehashed_changed_request_or_evidence_cannot_change_questions(self):
        self.prepare()
        answer = self.fill()
        request = tsep.read_json(self.request/'request.json')
        request['tasks'][0]['choices'].append('automatic-pass')
        (self.request/'request.json').write_bytes(json_bytes(request))
        seal(self.request)
        answer['request_sha256'] = tsep.digest(self.request/'request.json')
        with self.assertRaisesRegex(ValueError, 'questions/population'):
            self.apply(answer)

    def test_changed_tool_sources_refuse_historical_replay_before_writing(self):
        self.build()
        meta = tsep.read_json(self.bundle/'import.json')
        meta['source_files']['conformance/evaluate.py'] = '0'*64
        (self.bundle/'import.json').write_bytes(json_bytes(meta))
        # Update the report's evidence hash too, so report validation still passes.
        report = tsep.read_json(self.bundle/'report.json')
        next(a for a in report['artifacts'] if a['path']=='import.json')['sha256'] = tsep.digest(self.bundle/'import.json')
        (self.bundle/'report.json').write_bytes(json_bytes(report))
        seal(self.bundle)
        with self.assertRaisesRegex(ValueError, 'Tool sources differ'):
            replay(self.bundle, self.output)
        self.assertFalse(self.output.exists())

    def test_replay_retains_a_coherently_rehashed_wrong_report(self):
        self.build()
        report = tsep.read_json(self.bundle/'report.json')
        report['results'][0]['reason'] = 'Changed report claim without changing raw input'
        (self.bundle/'report.json').write_bytes(json_bytes(report))
        # EARL may include reason text; recompute it so consistency checks alone pass.
        gate = tsep.validate(report, self.bundle)
        (self.bundle/'earl.jsonld').write_bytes(json_bytes(tsep.earl(report, gate)))
        seal(self.bundle)
        with self.assertRaisesRegex(ValueError, 'Replay differs'):
            replay(self.bundle, self.output)
        receipt = tsep.read_json(self.output/'replay.json')
        self.assertFalse(receipt['replayed'])
        self.assertFalse(receipt['same_report_results'])
        self.assertTrue(receipt['same_atomic_results'])

    def test_manifest_extra_files_symlinks_and_existing_output_are_rejected(self):
        self.prepare()
        before = inventory(self.request)
        with self.assertRaises(ValueError):prepare(self.bundle, self.request)
        self.assertEqual(before, inventory(self.request))
        (self.request/'unexpected.txt').write_text('extra')
        with self.assertRaisesRegex(ValueError, 'Unlisted'):
            inventory(self.request)
        (self.request/'unexpected.txt').unlink()
        (self.request/'linked').symlink_to(self.bundle, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            inventory(self.request)

    def test_cli_blank_review_rejection_and_replay_run_outside_checkout(self):
        self.prepare()
        answer = self.root/'blank.json'
        answer.write_bytes((self.request/'response-template.json').read_bytes())
        args = [sys.executable, str(ROOT/'adapters/review.py'), 'import', str(self.request),
                '--response', str(answer), '--output', str(self.output)]
        run = subprocess.run(args, cwd=self.root, capture_output=True, text=True)
        self.assertEqual(run.returncode, 64)
        self.assertFalse(self.output.exists())
        run = subprocess.run([sys.executable, str(ROOT/'adapters/replay.py'), str(self.bundle),
                              '--output', str(self.output)], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertTrue(json.loads(run.stdout)['replayed'])


if __name__ == '__main__':
    unittest.main()
