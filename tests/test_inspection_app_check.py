"""Application-facing TS08 rehearsal; real subprocesses, exclusively authored inputs."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import tsep
from scripts import inspection_app_check as app


class FutureClock(datetime):
    @classmethod
    def now(cls, tz=None):
        return datetime(2040, 1, 1, tzinfo=timezone.utc).astimezone(tz)


class InspectionAppCheck(unittest.TestCase):
    def test_cli_round_trip_and_boundary_refusals(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'rehearsal'
            result = app.rehearsal(output)
            self.assertTrue(result['success'], result.get('error'))
            self.assertEqual(len(result['cases']), 13)
            self.assertEqual(result['refusals'], ['native-byte-change', 'omitted-selected-url',
                                                 'reviews-from-other-input', 'overwrite-existing-intake'])
            statuses = {row['id']: row['observed_status'] for row in result['cases']}
            self.assertEqual(statuses['negative-explained-without-cause'], 'C')
            self.assertEqual(statuses['missing-review'], 'NT')
            self.assertEqual(statuses['api-403'], 'NT')
            self.assertEqual(statuses['independent-contradiction-survives-old-crawl'], 'NC')
            self.assertEqual(statuses['future-enum'], 'NT')
            self.assertEqual(statuses['acquired-before-plan'], 'NC')
            multiple = next(row for row in result['cases'] if row['id'] == 'two-selected-urls')
            self.assertEqual(multiple['observed_status'], 'C')
            self.assertEqual(multiple['selected_url_count'], 2)
            for row in result['cases']:
                self.assertTrue(row['exact_replay'])
                self.assertTrue(row['native_bytes_retained'])
                for report in row['reports']:
                    self.assertTrue((output / report).is_file())
            self.assertEqual(tsep.read_json(output / 'rehearsal.json'), result)
            # Moving the issuance clock must not change the historical assessment.
            # This is a simulation, not a new observation of Google or future events.
            with patch.object(app.captures, 'datetime', FutureClock), patch.object(tsep, 'datetime', FutureClock):
                for name in ('qualified-positive', 'old-crawl', 'missing-review'):
                    replay_dir = output / (name + '-future-replay')
                    again = app.replay.replay(output / name / 'bundle', replay_dir)
                    self.assertTrue(again['replayed'])
                    self.assertTrue(again['same_atomic_results'])
                    self.assertTrue(again['same_report_results'])
                    self.assertTrue(again['same_source_observations'])
                    self.assertTrue(tsep.read_json(replay_dir / 'bundle/report.json')['issued_at'].startswith('2040-'))

    def test_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            (output / 'keep.txt').write_bytes(b'unchanged')
            with self.assertRaisesRegex(tsep.Invalid, 'NEW output'):
                app.rehearsal(output)
            self.assertEqual(list(output.iterdir()), [output / 'keep.txt'])
            self.assertEqual((output / 'keep.txt').read_bytes(), b'unchanged')

    def test_only_new_synthetic_examples_can_be_redated(self):
        case = app.fixture()['qualified-positive']
        before = deepcopy(case)
        anchor = datetime(2030, 1, 2, 12, tzinfo=timezone.utc)
        target = app.authored_target(case, anchor)
        self.assertEqual(case, before)
        self.assertEqual(tsep.timestamp(target['observed_at']), anchor)
        acquired = tsep.timestamp(target['inspection_records'][0]['retrieved_at'])
        self.assertEqual((anchor - acquired).total_seconds(), 7200)
        for key in ('inspection_synthetic', 'record', 'review'):
            invalid = deepcopy(case)
            item = invalid['input']['targets'][0]
            if key == 'inspection_synthetic':
                item['inspection_synthetic'] = False
            elif key == 'record':
                item['inspection_records'][0]['provenance'] = 'supplied-google-api'
            else:
                item['inspection_reviews'][0]['provenance'] = 'human'
            with self.subTest(key=key), self.assertRaises(tsep.Invalid):
                app.authored_target(invalid, anchor)


if __name__ == '__main__':
    unittest.main()
