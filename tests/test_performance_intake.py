"""Acceptance of the offline operator workflow, with synthetic native records."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import tsep
from adapters import performance_intake as intake, package, replay

ROOT = Path(__file__).resolve().parents[1]
PLAN = '2026-10-10T11:00:00Z'
RECORD = '2026-10-10T12:00:00Z'
FINAL = '2026-10-10T12:10:00Z'
REVIEW = '2026-10-10T12:30:00Z'
IMPORT = '2026-10-10T12:40:00Z'
TARGET = 'https://example.com/product'


def base(kind):
    path = ROOT/'tests/fixtures/performance-v2.json'
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != path.with_suffix('.sha256').read_text().strip():
        raise ValueError('Frozen native fixture changed')
    name = 'performance-'+('field-poor-correctly-documented' if kind == 'field' else 'lab-context-and-supplied-review')
    return copy.deepcopy(next(c['input']['targets'][0] for c in json.loads(raw)['cases'] if c['id'] == name))


class PerformanceIntake(unittest.TestCase):
    # One authored scenario can exercise several assertions, not just a count.
    COVERAGE = {
        'field-byte-preservation': 'test_field_bytes',
        'lab-complete-no-review': 'test_lab_without_review',
        'field-complete-synthetic-review': 'test_field_supplied_review',
        'lab-complete-synthetic-review': 'test_lab_supplied_review',
        'field-wrong-classification': 'test_field_contradictory_review',
        'lab-false-field-claim': 'test_lab_contradictory_review',
        'blank-review': 'test_blank_review',
        'wrong-review-binding': 'test_wrong_request_binding',
        'wrong-evidence-binding': 'test_wrong_evidence_binding',
        'real-synthetic-mismatch': 'test_false_human_provenance',
        'review-before-request': 'test_review_before_request',
        'missing-field': 'test_missing_field',
        'missing-lab-slot': 'test_missing_lab_slot',
        'unrecorded-lab-slot': 'test_unrecorded_lab_slot',
        'runtime-error': 'test_runtime_error',
        'wrong-url': 'test_wrong_url',
        'changed-settings': 'test_changed_settings',
        'calibration-reuse': 'test_calibration_reuse',
        'invalid-native-json': 'test_invalid_json',
        'non-utf8': 'test_non_utf8',
        'oversize': 'test_oversize',
        'out-of-order-slot': 'test_skip_slot',
        'replace-slot': 'test_replace_slot',
        'extra-slot': 'test_extra_slot',
        'manifest-tamper': 'test_manifest_tamper',
        'rehashed-receipt-tamper': 'test_rehashed_receipt_tamper',
        'plan-tamper': 'test_plan_tamper',
        'source-change': 'test_source_change',
        'output-existing': 'test_existing_output',
        'network-free': 'test_offline',
        'portable': 'test_portable',
    }

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.counter = 0

    def path(self, prefix='p'):
        self.counter += 1
        return self.root/(prefix+str(self.counter))

    def write(self, data):
        path = self.path('file')
        path.write_bytes(data if isinstance(data, bytes) else package.json_bytes(data))
        return path

    def plan(self, kind='field'):
        b = base(kind)
        options = dict(kind=kind, target=TARGET, operator='Synthetic operator', access='synthetic',
                       selection_reason='Authored acceptance exercise only', max_age_days=7)
        if kind == 'field':
            options.update(request_file=self.write(b['field']['request']), granularity='url', form_factor='PHONE')
        else:
            calibration = json.loads(b['lab']['runs'][0]['raw_json'])
            calibration['fetchTime'] = '2026-10-10T10:00:00Z'
            calibration['environment']['benchmarkIndex'] = 123
            options.update(calibration=self.write(calibration), final_url=TARGET, run_count=3)
        output = self.path('plan')
        with patch.object(intake, 'now', return_value=PLAN):
            intake.plan(output, **options)
        return output

    def append(self, session, slot=1, raw=None, missing=False):
        output = self.path('session')
        options = {'missing_reason': 'Synthetic unavailable attempt', 'error_file': self.write(b'Synthetic failure\r\n')} if missing else {
            'file': self.write(raw if raw is not None else base('field')['field']['raw_json'].encode()), 'source_url': TARGET}
        with patch.object(intake, 'now', return_value=RECORD):
            intake.record(session, output, slot=slot, **options)
        return output

    def ready(self, kind='field', mutate=None):
        session = self.plan(kind)
        raws = [base('field')['field']['raw_json'].encode()] if kind == 'field' else [r['raw_json'].encode() for r in base('lab')['lab']['runs']]
        if mutate:
            raws = mutate(raws, session)
        for i, raw in enumerate(raws, 1):
            session = self.append(session, i, raw, missing=raw is None)
        return session

    def finalize(self, session, expected='NT'):
        output = self.path('intake')
        with patch.object(intake, 'now', return_value=FINAL):
            result = intake.finalize(session, output)
        self.assertEqual(result['status'], expected)
        package.inventory(output)
        return output

    def answer(self, root, kind='field'):
        data = tsep.read_json(root/'response-template.json')
        data.update(reviewer='Authored synthetic reviewer', observed_at=REVIEW,
                    provenance='synthetic-exercise', assistance='Authored fixture, no real person or site assessment',
                    examined_evidence=tsep.read_json(root/'request.json')['evidence'])
        original = base(kind)[kind+'_review']
        keys = ('metrics',) if kind == 'field' else ('metrics', 'hypothesis', 'next_measurement', 'claims_field_cwv', 'claims_inp_from_tbt')
        data.update({key: original[key] for key in keys})
        return data

    def review(self, root, answer, expected='C'):
        output = self.path('reviewed')
        with patch.object(intake, 'now', return_value=IMPORT):
            result = intake.review(root, self.write(answer), output)
        self.assertEqual(result['status'], expected)
        self.assertFalse(result['review_authenticated'])
        return output

    def rejected_review(self, mutate):
        root = self.finalize(self.ready())
        answer = self.answer(root)
        mutate(answer)
        output = self.path('rejected')
        with patch.object(intake, 'now', return_value=IMPORT), self.assertRaises(ValueError):
            intake.review(root, self.write(answer), output)
        self.assertFalse(output.exists())
        package.inventory(root)

    def test_frozen_acceptance_matrix(self):
        path = ROOT/'tests/fixtures/performance-intake-v1.json'
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), '1c1bc01b8cdf89bcb881899dca75d2631682492360479415e99b725110307ae6')
        cases = tsep.read_json(path)['scenarios']
        self.assertEqual({c['id'] for c in cases}, set(self.COVERAGE))
        self.assertTrue(all(callable(getattr(self, method)) for method in self.COVERAGE.values()))

    def test_field_bytes(self):
        value = json.loads(base('field')['field']['raw_json'])
        value['unknownProperty'] = {'message': 'épreuve conservée'}
        raw = ('\ufeff'+json.dumps(value, ensure_ascii=False, indent=2).replace('\n', '\r\n')+'\r\n').encode()
        root = self.finalize(self.ready(mutate=lambda runs, session: [raw]))
        data = tsep.read_json(root/'bundle/input.json')
        self.assertEqual(data['targets'][0]['field']['raw_json'].encode(), raw)
        self.assertEqual((root/'session/originals/01.json').read_bytes(), raw)
        self.assertNotIn('field_review', data['targets'][0])

    def test_lab_without_review(self):
        root = self.finalize(self.ready('lab'))
        target = tsep.read_json(root/'bundle/input.json')['targets'][0]
        self.assertEqual(len(target['lab']['runs']), 3)
        self.assertNotIn('lab_review', target)
        atoms = tsep.read_json(root/'bundle/report.json')['results'][0]['atomic_results']
        self.assertEqual([a['outcome'] for a in atoms], ['pass', 'inconclusive'])
        self.assertIsNone(tsep.read_json(root/'response-template.json')['claims_field_cwv'])
        self.assertIn('native_environment', tsep.read_json(root/'overview.json')['slots'][0])

    def test_field_supplied_review(self):
        root = self.finalize(self.ready())
        reviewed = self.review(root, self.answer(root))
        target = tsep.read_json(reviewed/'bundle/input.json')['targets'][0]
        self.assertEqual(target['observed_at'], IMPORT)
        self.assertEqual(target['intent']['declared_at'], PLAN)
        self.assertIn('4200', (reviewed/'bundle/gate.json').read_text())
        self.assertEqual((root/'input.json').read_bytes(), (reviewed/'intake/input.json').read_bytes())
        self.assertEqual(tsep.read_json(reviewed/'review-import.json')['original_assessed_at'], FINAL)

    def test_lab_supplied_review(self):
        root = self.finalize(self.ready('lab'))
        self.review(root, self.answer(root, 'lab'))

    def test_field_contradictory_review(self):
        root = self.finalize(self.ready())
        answer = self.answer(root); answer['metrics']['LCP']['classification'] = 'good'
        reviewed = self.review(root, answer, 'NC')
        self.assertEqual(tsep.read_json(reviewed/'response.json')['metrics']['LCP']['classification'], 'good')

    def test_lab_contradictory_review(self):
        root = self.finalize(self.ready('lab'))
        answer = self.answer(root, 'lab'); answer['claims_inp_from_tbt'] = True
        self.review(root, answer, 'NC')

    def test_blank_review(self):
        root = self.finalize(self.ready())
        with self.assertRaises(ValueError):
            self.review(root, tsep.read_json(root/'response-template.json'))

    def test_wrong_request_binding(self):
        self.rejected_review(lambda a: a.update(request_sha256='0'*64))

    def test_wrong_evidence_binding(self):
        self.rejected_review(lambda a: a.update(examined_evidence=[]))

    def test_false_human_provenance(self):
        self.rejected_review(lambda a: a.update(provenance='human'))

    def test_review_before_request(self):
        self.rejected_review(lambda a: a.update(observed_at=PLAN))

    def test_missing_field(self):
        root = self.finalize(self.append(self.plan(), missing=True))
        field = tsep.read_json(root/'input.json')['targets'][0]['field']
        self.assertNotIn('raw_json', field)
        self.assertEqual(field['slots'][0]['status'], 'unavailable')
        self.assertEqual((root/'session/errors/01.txt').read_bytes(), b'Synthetic failure\r\n')

    def test_missing_lab_slot(self):
        root = self.finalize(self.ready('lab', lambda raws, s: [raws[0], None, raws[2]]))
        lab = tsep.read_json(root/'input.json')['targets'][0]['lab']
        self.assertEqual(len(lab['runs']), 2)
        self.assertEqual([s['status'] for s in lab['slots']], ['supplied', 'unavailable', 'supplied'])
        self.review(root, self.answer(root, 'lab'), 'NT')
        self.assertNotIn('median', (root/'bundle/assessment.json').read_text())

    def test_unrecorded_lab_slot(self):
        root = self.finalize(self.ready('lab', lambda raws, s: raws[:1]))
        lab = tsep.read_json(root/'input.json')['targets'][0]['lab']
        self.assertEqual(lab['slots'][1], {'slot': 2, 'status': 'unrecorded'})

    def changed_lab(self, transform, expected='NT'):
        def alter(raws, session):
            value = json.loads(raws[1]); transform(value); raws[1] = package.json_bytes(value)
            return raws
        root = self.finalize(self.ready('lab', alter), expected)
        return root

    def test_runtime_error(self):
        root = self.changed_lab(lambda v: v.update(runtimeError={'code': 'SYNTHETIC_FAILURE'}))
        self.assertIn('SYNTHETIC_FAILURE', (root/'session/originals/02.json').read_text())

    def test_wrong_url(self):
        self.changed_lab(lambda v: v.update(finalUrl='https://example.com/elsewhere'), 'NC')

    def test_changed_settings(self):
        self.changed_lab(lambda v: v['configSettings'].update(disableStorageReset=True))

    def test_calibration_reuse(self):
        root = self.finalize(self.ready('lab', lambda raws, s: [(s/'reference/calibration.json').read_bytes(), *raws[1:]]))
        self.assertTrue(tsep.read_json(root/'overview.json')['slots'][0]['calibration_reused'])

    def test_invalid_json(self):
        raw = b'{ invalid json\r\n'
        root = self.finalize(self.ready(mutate=lambda runs, s: [raw]))
        self.assertEqual((root/'session/originals/01.json').read_bytes(), raw)

    def test_non_utf8(self):
        session = self.plan(); original = self.write(b'\xff\x80')
        out = self.path()
        with self.assertRaises(ValueError):
            intake.record(session, out, slot=1, file=original, source_url=TARGET)
        self.assertFalse(out.exists()); self.assertEqual(original.read_bytes(), b'\xff\x80')

    def test_oversize(self):
        session = self.plan(); out = self.path()
        with self.assertRaises(ValueError):
            intake.record(session, out, slot=1, file=self.write(b'x'*(intake.NATIVE_LIMIT+1)), source_url=TARGET)
        self.assertFalse(out.exists())
        def pad(raws, session):
            result = []
            for raw in raws:
                value = json.loads(raw); value['padding'] = 'x'*(3*1024*1024)
                result.append(package.json_bytes(value))
            return result
        session = self.ready('lab', pad); out = self.path()
        with patch.object(intake, 'now', return_value=FINAL), self.assertRaises(ValueError):
            intake.finalize(session, out)
        self.assertFalse(out.exists()); package.inventory(session)

    def test_skip_slot(self):
        session = self.plan('lab')
        with self.assertRaises(ValueError):
            self.append(session, 2)

    def test_replace_slot(self):
        session = self.ready()
        old = package.inventory(session)
        with self.assertRaises(ValueError):
            self.append(session, 1)
        self.assertEqual(old, package.inventory(session))

    def test_extra_slot(self):
        with self.assertRaises(ValueError):
            self.append(self.ready(), 2)

    def test_manifest_tamper(self):
        session = self.ready(); (session/'originals/01.json').write_bytes(b'{}')
        with self.assertRaises(ValueError):
            intake.session(session)

    def test_rehashed_receipt_tamper(self):
        session = self.ready(); (session/'originals/01.json').write_bytes(b'{}'); package.seal(session)
        with self.assertRaises(ValueError):
            intake.session(session)

    def test_plan_tamper(self):
        session = self.ready(); p = tsep.read_json(session/'plan.json'); p['target'] = 'https://example.com/other'
        (session/'plan.json').write_bytes(package.json_bytes(p)); package.seal(session)
        with self.assertRaises(ValueError):
            intake.session(session)

    def test_source_change(self):
        session = self.ready()
        with patch.object(intake, 'source_files', return_value={}), self.assertRaises(ValueError):
            intake.session(session)

    def test_existing_output(self):
        session = self.plan(); before = package.inventory(session)
        with self.assertRaises(ValueError):
            intake.record(session, session, slot=1, file=self.write(b'{}'), source_url=TARGET)
        self.assertEqual(package.inventory(session), before)

    def test_offline(self):
        with patch.object(socket, 'socket', side_effect=AssertionError('Network forbidden')):
            root = self.finalize(self.ready('lab'))
            reviewed = self.review(root, self.answer(root, 'lab'))
            result = replay.replay(reviewed/'bundle', self.path('replay'))
            self.assertTrue(result['replayed']); self.assertTrue(result['same_source_observations'])

    def test_portable(self):
        session = self.ready('lab')
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder); copied = dest/'copied'; shutil.copytree(session, copied)
            # Remove every original local source and previous package; copies alone suffice.
            for path in list(self.root.iterdir()):
                if path.is_dir(): shutil.rmtree(path)
                else: path.unlink()
            result = subprocess.run([sys.executable, '-B', str(ROOT/'adapters/performance_intake.py'),
                'finalize', str(copied), '--output', str(dest/'delivered')], cwd=folder, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(replay.replay(dest/'delivered/bundle', dest/'replay')['replayed'])
            self.assertNotIn(str(self.root), (dest/'delivered/input.json').read_text())


if __name__ == '__main__':
    unittest.main()
