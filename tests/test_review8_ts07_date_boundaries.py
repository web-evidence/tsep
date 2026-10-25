"""Bounded synthetic date interpretations from the f3 exact-candidate review."""
import json
from contextlib import nullcontext
from pathlib import Path
import unittest
from unittest.mock import patch
from conformance import google_directives as g, source_directives
from conformance.evaluate import evaluate, directive_result
NOW='2026-10-25T05:00:00Z'
ROOT=Path(__file__).resolve().parents[1]

class ReviewedDateBoundaries(unittest.TestCase):
    def test_authored_review_matrix(self):
        corpus=json.loads((ROOT/'tests/fixtures/ts07-google-dates-review2-v2.json').read_text())
        self.assertEqual(len(corpus['cases']),68);self.assertTrue(corpus['synthetic'])
        for case in corpus['cases']:
            with self.subTest(case=case['id']):
                self.assertEqual([{k:r[k] for k in ('rule_id','target','outcome')} for r in evaluate(case['input'])],case['expected'])

    def test_month_grammar_is_closed(self):
        for month in ('Okt','Mai','Dic','Foo'):
            self.assertEqual(g.expiry_v2('21 '+month+' 2020 00:00:00 GMT',NOW),'unsupported')
        for month in ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'):
            self.assertEqual(g.expiry_v2('21 '+month+' 2020 00:00:00 GMT',NOW),'expired')
        self.assertEqual(g.expiry_v2('31 Feb 2020 00:00:00 GMT',NOW),'invalid')

    def test_two_digit_years_require_agreement_without_google_pivot(self):
        for year in ('49','50','76','99'):
            self.assertEqual(g.expiry_v2('21 Oct '+year+' 00:00:00 GMT',NOW),'unresolved')
        self.assertEqual(g.expiry_v2('21 Oct 20 00:00:00 GMT',NOW),'expired')
        self.assertEqual(g.expiry_v2('21 Oct 50 00:00:00 GMT','1800-01-01T00:00:00Z'),'future')
        self.assertEqual(g.expiry_v2('21 Oct 50 00:00:00 GMT','2100-01-01T00:00:00Z'),'expired')
        self.assertEqual(g.expiry_v2('Sat, 21 Oct 50 00:00:00 GMT',NOW),'expired')
        self.assertEqual(g.expiry_v2('Friday, 21-Oct-50 00:00:00 GMT',NOW),'future')
        self.assertEqual(g.expiry_v2('Mon, 21 Oct 50 00:00:00 GMT',NOW),'unsupported')

    def test_negative_zero_offsets_represent_known_utc_instant(self):
        for value in ('25 Oct 2026 05:01:00 -0000','2026-10-25T05:01:00-00:00'):
            self.assertEqual(g.expiry_v2(value,NOW),'future')
        for value in ('25 Oct 2026 04:59:00 -0000','2026-10-25T04:59:00-00:00'):
            self.assertEqual(g.expiry_v2(value,NOW),'expired')
        self.assertEqual(g.expiry_v2('2026-10-25T05:01:00',NOW),'unresolved')

    def test_exact_expiry_instant_is_not_yet_after(self):
        self.assertEqual(g.expiry_v2(NOW,NOW),'future')
        self.assertEqual(g.expiry_v2('2026-10-25T04:59:59.999999Z',NOW),'expired')
        self.assertEqual(g.expiry_v2('2026-10-25T05:00:00.000001Z',NOW),'future')
        self.assertEqual(g.expiry(NOW,NOW),'expired') # Explicit historical v1 unchanged.

    def test_unknown_profile_does_not_escape_http_shortcut(self):
        for profile in ('unknown-profile',None,[],{}):
            for unavailable in (False,True):
                with self.subTest(profile=profile,unavailable=unavailable):
                    with patch.object(source_directives.source_http,'inventory',side_effect=OSError('synthetic unavailable')) if unavailable else nullcontext():
                        outcome=directive_result({'content-type':['text/html; charset=utf-8'],'x-robots-tag':['noindex']},
                            b'<html><head></head><body>Synthetic</body></html>',
                            {'directive_policy':profile,'crawler':'googlebot','indexing':'allow','source_reader':source_directives.READER},source=True,observed_at=NOW)
                    self.assertEqual(outcome[0],'inconclusive')

if __name__=='__main__':unittest.main()
