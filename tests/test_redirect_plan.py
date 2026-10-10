"""Synthetic prior-owner workflow exercises; no actual human review. Apache-2.0."""
import copy
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
from adapters import redirect_plan as workflow
from adapters.package import json_bytes, seal, inventory
from adapters.replay import replay

CASES = {c['id']: c['input'] for c in tsep.read_json(ROOT/'tests/fixtures/redirect-cases-v1.json')['cases']}
PREPARED = '2026-10-10T09:10:00Z'
REVIEWED = '2026-10-10T09:20:00Z'
IMPORTED = '2026-10-10T09:30:00Z'


class RedirectPlanWorkflow(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.plan = copy.deepcopy(CASES['redirect-direct']['targets'][0])
        self.plan.pop('http'); self.plan.pop('observed_at')
        self.plan['intent'].pop('redirect_review')
        self.data = {'kind': 'tsep-redirect-plan', 'access': 'synthetic',
                     'selection_reason': 'Authored fixture, not a site assessment', 'targets': [self.plan]}
        self.source = self.root/'plan.json'
        self.request = self.root/'request'
        self.reviewed = self.root/'reviewed'
        self.output = self.root/'output'

    def tearDown(self):
        self.temp.cleanup()

    def prepare(self):
        self.source.write_bytes(json_bytes(self.data))
        with patch.object(workflow, 'now', return_value=PREPARED):
            return workflow.prepare(self.source, self.request)

    def answer(self, outcome='approved'):
        answer = tsep.read_json(self.request/'response-template.json')
        for row in answer['responses']:
            row.update(reviewer='Fictional owner in automated exercise', observed_at=REVIEWED,
                       outcome=outcome, reason='Authored synthetic decision for workflow verification',
                       assistance='Automated test; no actual human judgment', provenance='synthetic-exercise')
        return answer

    def apply(self, answer):
        path = self.root/'answer.json'; path.write_bytes(json_bytes(answer))
        with patch.object(workflow, 'now', return_value=IMPORTED):
            return workflow.import_response(self.request, path, self.reviewed)

    def supplied(self, case='redirect-direct'):
        data = copy.deepcopy(CASES[case])
        data['targets'][0]['intent'] = copy.deepcopy(self.plan['intent'])
        data['targets'][0]['context'] = copy.deepcopy(self.plan['context'])
        return data

    def attach(self, data):
        path = self.root/'captures.json'; path.write_bytes(json_bytes(data))
        return workflow.attach(self.reviewed, path, self.output)

    def test_blank_plan_template_does_not_approve_or_claim_a_capture(self):
        result = self.prepare()
        self.assertEqual(result['human_decisions_created'], 0)
        self.assertEqual((self.request/'plan.json').read_bytes(), self.source.read_bytes())
        template = tsep.read_json(self.request/'response-template.json')
        row = template['responses'][0]
        self.assertIsNone(row['outcome']); self.assertIsNone(row['provenance'])
        for field in ('reviewer', 'observed_at', 'reason', 'assistance'):
            self.assertEqual(row[field], '')
        self.assertNotIn('observed_at', tsep.read_json(self.request/'plan.json')['targets'][0])
        with self.assertRaisesRegex(ValueError, 'Missing reasoned'):
            self.apply(template)
        self.assertFalse(self.reviewed.exists())

    def test_offline_workflow_preserves_capture_and_replays_native_report(self):
        with patch('socket.socket', side_effect=AssertionError('Network forbidden')):
            self.prepare(); self.apply(self.answer())
            original = self.supplied()
            self.attach(original)
            result = replay(self.output/'bundle', self.root/'replay')
        self.assertTrue(result['replayed']); self.assertEqual(result['network_requests'], 0)
        self.assertEqual(tsep.read_json(self.output/'original-captures.json'), original)
        reviewed = tsep.read_json(self.output/'reviewed-captures.json')['targets'][0]
        self.assertEqual(reviewed['http'], original['targets'][0]['http'])
        self.assertEqual(reviewed['observed_at'], original['targets'][0]['observed_at'])
        self.assertEqual(tsep.read_json(self.output/'bundle/gate.json')['counts']['C'], 1)
        inventory(self.output)

    def test_refusal_failure_and_incomplete_capture_are_not_hidden(self):
        for decision, case, expected in [('rejected', 'redirect-direct', 'NC'),
                                         ('approved', 'redirect-wrong-destination', 'NC'),
                                         ('approved', 'redirect-unfinished', 'NT')]:
            with self.subTest(decision=decision, case=case), tempfile.TemporaryDirectory(dir=self.root) as directory:
                base = Path(directory)
                self.request = base/'request'; self.reviewed = base/'reviewed'; self.output = base/'output'
                self.prepare(); self.apply(self.answer(decision)); self.attach(self.supplied(case))
                self.assertEqual(tsep.read_json(self.output/'bundle/gate.json')['counts'][expected], 1)

    def test_response_rejects_wrong_binding_dates_provenance_and_incomplete_population(self):
        self.prepare()
        changes = [lambda a: a.update(request_sha256='0'*64),
                   lambda a: a['responses'][0].update(plan_sha256='0'*64),
                   lambda a: a['responses'][0].update(observed_at='2026-10-10T09:00:00Z'),
                   lambda a: a['responses'][0].update(observed_at='2026-10-10T11:00:00Z'),
                   lambda a: a['responses'][0].update(provenance='human'),
                   lambda a: a['responses'][0].update(role='assistant'),
                   lambda a: a.update(responses=[])]
        for change in changes:
            answer = self.answer(); change(answer)
            with self.assertRaises(ValueError):
                self.apply(answer)
            self.assertFalse(self.reviewed.exists())

    def test_public_plan_refuses_synthetic_approval(self):
        self.data['access'] = 'public'; self.prepare()
        with self.assertRaisesRegex(ValueError, 'provenance'):
            self.apply(self.answer())

    def test_capture_rejects_changed_context_intent_population_and_backdating(self):
        self.prepare(); self.apply(self.answer())
        changes = [lambda d: d['targets'][0]['context'].update(tool_version='other'),
                   lambda d: d['targets'][0]['intent']['redirect_plan'].update(expected_final_url='https://example.com/else'),
                   lambda d: d['targets'][0]['intent'].update(redirect_review={}),
                   lambda d: d['targets'][0].update(observed_at='2026-10-10T09:25:00Z'),
                   lambda d: d['targets'][0].update(observed_at='2099-10-10T10:00:00Z'),
                   lambda d: d.update(targets=[]),
                   lambda d: d.update(rules=['TS02-A02'])]
        for change in changes:
            data = self.supplied(); change(data)
            with self.assertRaises(ValueError):
                self.attach(data)
            self.assertFalse(self.output.exists())

    def test_rehashed_readable_plan_or_review_payload_still_rejected(self):
        self.prepare(); self.apply(self.answer())
        view = self.reviewed/'plan.html'; old = view.read_bytes()
        view.write_bytes(old.replace(b'example.com/new', b'example.com/else')); seal(self.reviewed)
        with self.assertRaisesRegex(ValueError, 'Readable plan differs'):
            self.attach(self.supplied())
        view.write_bytes(old)
        reviewed = tsep.read_json(self.reviewed/'reviewed-plan.json')
        reviewed['targets'][0]['intent']['redirect_review']['outcome'] = 'rejected'
        (self.reviewed/'reviewed-plan.json').write_bytes(json_bytes(reviewed))
        receipt = tsep.read_json(self.reviewed/'receipt.json')
        receipt['reviewed_plan_sha256'] = tsep.digest(self.reviewed/'reviewed-plan.json')
        (self.reviewed/'receipt.json').write_bytes(json_bytes(receipt)); seal(self.reviewed)
        with self.assertRaisesRegex(ValueError, 'differs from supplied response'):
            self.attach(self.supplied())

    def test_plan_rejects_existing_review_captures_duplicates_and_future_intent(self):
        for field, value in [('http', []), ('observed_at', PREPARED)]:
            data = copy.deepcopy(self.data); data['targets'][0][field] = value
            with self.assertRaises(ValueError):
                workflow.validate_plan(data, PREPARED)
        data = copy.deepcopy(self.data); data['targets'] *= 2
        with self.assertRaises(ValueError):
            workflow.validate_plan(data, PREPARED)
        data = copy.deepcopy(self.data); data['targets'][0]['intent']['declared_at'] = '2099-01-01T00:00:00Z'
        with self.assertRaises(ValueError):
            workflow.validate_plan(data, PREPARED)
        data = copy.deepcopy(self.data); data['targets'][0]['intent']['redirect_review'] = {}
        with self.assertRaises(ValueError):
            workflow.validate_plan(data, PREPARED)

    def test_html_is_escaped_and_no_external_resource_or_script(self):
        self.data['selection_reason'] = '<script>alert(1)</script>'
        self.prepare()
        html = (self.request/'plan.html').read_text()
        self.assertIn('&lt;script&gt;', html)
        self.assertNotIn('<script', html); self.assertNotIn(' src=', html)

    def test_cli_runs_outside_repository_and_refuses_overwrite(self):
        self.source.write_bytes(json_bytes(self.data))
        args = [sys.executable, str(ROOT/'adapters/redirect_plan.py'), 'prepare', str(self.source), '--output', str(self.request)]
        result = subprocess.run(args, cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)['prepared'])
        result = subprocess.run(args, cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 64)


if __name__ == '__main__':
    unittest.main()
