"""Authored date/scope regressions from exact-candidate Claude review; synthetic."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from conformance import google_directives as google
from conformance.evaluate import evaluate, directive_result
from tests.test_review7_priority1 import observed_case
from tests.test_url_policy import rebind

ROOT=Path(__file__).resolve().parents[1]
NOW='2026-10-25T05:00:00Z'


class ReviewedGoogleDates(unittest.TestCase):
    def test_authored_date_and_scope_matrix(self):
        corpus=json.loads((ROOT/'tests/fixtures/ts07-google-dates-v2.json').read_text())
        self.assertTrue(corpus['synthetic']);self.assertEqual(len(corpus['cases']),78)
        for case in corpus['cases']:
            with self.subTest(case=case['id']):
                actual=evaluate(case['input'])
                self.assertEqual([{k:r[k] for k in ('rule_id','target','outcome')} for r in actual],case['expected'])

    def test_partial_date_parse_cannot_produce_exclusion(self):
        for value in ('21 Oct 2020 00:00:00 GMT max-snippet:0','21 Oct 2020 00:00:00 GMT foo',
                      'Wed, 21 Oct 2020 00:00:00 GMT foo','21 Oct 2020\n00:00:00 GMT'):
            notes=[]
            outcome,_=google.result({},['unavailable_after: '+value],
                {'directive_policy':google.PROFILE,'crawler':'googlebot','indexing':'allow'},NOW,notes)
            self.assertEqual(outcome,'inconclusive');self.assertFalse(notes[0]['excluded'])
            self.assertTrue(notes[0]['unsupported_syntax'])

    def test_valid_but_unimplemented_iso_forms_are_not_called_invalid(self):
        for value in ('20201021','2020-10-21T00:00:00+0000','2020-W43-3','2020-295'):
            self.assertEqual(google.expiry_v2(value,NOW),'unsupported')

    def test_date_zones_and_boundary_use_capture_time(self):
        for value,expected in [('2026-10-25T05:00:00Z','expired'),
                               ('2026-10-25T05:00:00.000001Z','future'),
                               ('2026-10-25T06:00:00+02:00','expired'),
                               ('2026-10-25T04:00:00-02:00','future'),
                               ('2026-10-25T06:00:00','unresolved'),
                               ('2020-10-21','expired'),('2020-02-31','invalid'),
                               ('21 Oct 49 00:00:00 GMT','future'),
                               ('21 Oct 50 00:00:00 GMT','expired'),
                               ('2026-10-25T05:01:00-00:00','unresolved'),
                               ('25 Oct 2026 05:01:00 -0000','unresolved')]:
            with self.subTest(value=value):self.assertEqual(google.expiry_v2(value,NOW),expected)
        self.assertEqual(google.expiry_v2('2020-10-21T00:00:00Z',None),'unresolved')

    def test_profile_is_mandatory_for_internal_facts_and_tokens(self):
        with self.assertRaises(TypeError):google.tokens('noindex')
        with self.assertRaises(TypeError):google.facts({},[],NOW)

    def test_explicit_v1_header_shortcut_keeps_its_own_grammar(self):
        from conformance import source_directives
        headers={'x-robots-tag':['noindex nofollow']}
        for profile,expected in [(google.LEGACY_PROFILE,'fail'),(google.PROFILE,'inconclusive')]:
            with patch.object(source_directives.source_http,'inventory',side_effect=OSError('synthetic unavailability')):
                actual=directive_result(headers,b'unreadable',{'directive_policy':profile,
                    'crawler':'googlebot','indexing':'allow','source_reader':source_directives.READER},
                    source=True,observed_at=NOW)
            self.assertEqual(actual[0],expected)

    def test_ts09_header_mechanism_remains_explicitly_v1(self):
        value=observed_case(meta='index',mechanism='x-robots-tag-noindex',reviewed=True)
        target=value['targets'][0];doc=target['evidence_checks']['TS09']['documents'][0]
        doc['http'][0]['response']=doc['http'][0]['response'].replace('Content-Type:',
            'X-Robots-Tag: noindex nofollow\r\nContent-Type:')
        rebind(target,'TS09')
        with patch.object(google,'facts',wraps=google.facts) as reader:
            self.assertEqual(evaluate(value)[0]['outcome'],'pass')
        self.assertTrue(reader.call_args_list)
        self.assertTrue(all(call.args[3]==google.LEGACY_PROFILE for call in reader.call_args_list))

    def test_v1_lenient_dates_unchanged_but_v2_does_not_reuse_them(self):
        value='21 Oct 2020 00:00:00 GMT foo'
        self.assertEqual(google.expiry(value,NOW),'expired')
        self.assertEqual(google.expiry_v2(value,NOW),'unsupported')


if __name__=='__main__':unittest.main()
