"""Segmented GitHub logs: reversible transport, unchanged strict JSON/identity."""
import copy
import unittest
from scripts import postmerge_check as check
from tests.test_postmerge_check import fixture, log


class Transport(unittest.TestCase):
    def test_segmented_receipt(self):
        expected, receipt = fixture()
        stamp = b'2026-10-26T04:00:00.1234567Z '
        lines = log(receipt).splitlines(keepends=True)
        raw = b''.join((b'\xef\xbb\xbf' if i in (0, 6, 20) else b'') + stamp + line
                       for i, line in enumerate(lines))
        projected, proof = check.log_projection(raw)
        self.assertEqual(len(proof['removed_bom_offsets']), 3)
        self.assertEqual(check.receipt_from_log(raw)[1], receipt)
        self.assertEqual(check.receipt_from_log(projected)[1], receipt)
        check.validate_receipt(receipt, expected, '3.12')
        bad = copy.deepcopy(receipt); bad['archive_sha256'] = 'changed'
        with self.assertRaises(check.Unqualified):
            check.validate_receipt(bad, expected, '3.12')

    def test_bad_segments_rejected(self):
        for raw in (b'x\xef\xbb\xbf', b'\xef\xbb\xbf2026-10-26T00:00:00Z ',
                    b'\xef\xbb\xbf2026-10-26T00:00:00.123456Z ',
                    b'\xef\xbb\xbf{"success":true}', b'{"x":"\xef\xbb\xbf"}'):
            with self.subTest(raw=raw), self.assertRaises(check.Unqualified):
                check.log_projection(raw)

    def test_truncated_receipt_refused(self):
        _, receipt = fixture()
        with self.assertRaises((ValueError, check.Unqualified)):
            check.receipt_from_log(log(receipt)[:-20])


if __name__ == '__main__': unittest.main()
