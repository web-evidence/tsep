"""Explicit conservative date limitation and declared expectation revisions."""
import hashlib,json,unittest
from pathlib import Path
from conformance import google_directives as g
from conformance.evaluate import evaluate
ROOT=Path(__file__).resolve().parents[1]
NOW='2026-10-25T05:00:00Z'

class TwoDigitYearLimit(unittest.TestCase):
    def test_all_two_digit_years_unsupported_before_calendar_or_capture(self):
        for year in range(100):
            for day in ('21 Oct','31 Feb'):
                for capture in (NOW,None):
                    self.assertEqual(g.expiry_v2(day+' '+str(year).zfill(2)+' 00:00:00 GMT',capture),'unsupported')
        self.assertEqual(g.expiry_v2('Wed, 21 Oct 2020 00:00:00 GMT',NOW),'expired')
        self.assertEqual(g.expiry_v2('Sat, 21 Oct 2020 00:00:00 GMT',NOW),'unsupported')
        self.assertEqual(g.expiry_v2('31 Feb 2050 00:00:00 GMT',NOW),'invalid')

    def test_authored_independent_noindex_corpus(self):
        corpus=json.loads((ROOT/'tests/fixtures/ts07-google-dates-review3-v2.json').read_text())
        self.assertTrue(corpus['synthetic']);self.assertEqual(len(corpus['cases']),24)
        for c in corpus['cases']:
            with self.subTest(case=c['id']):
                self.assertEqual([{k:r[k] for k in ('rule_id','target','outcome')} for r in evaluate(c['input'])],c['expected'])

    def test_expectation_revisions_are_explicit_and_input_bound(self):
        delta=json.loads((ROOT/'provenance/ts07-draft9-review3-expectation-delta.json').read_text())
        self.assertEqual(delta['revised_expectation_count'],15);seen=[]
        for file in delta['files']:
            path=ROOT/file['path'];self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),file['after_sha256'])
            cases={c['id']:c for c in json.loads(path.read_text())['cases']}
            for change in file['revisions']:
                case=cases[change['case']];self.assertEqual(case['expected'],change['after']);self.assertNotEqual(change['before'],change['after'])
                self.assertEqual(hashlib.sha256(json.dumps(case['input'],sort_keys=True,separators=(',',':')).encode()).hexdigest(),change['input_sha256'])
                self.assertTrue(all(r['outcome']=='inconclusive' for r in change['after']));seen.append(case['id'])
        self.assertEqual(len(seen),15);self.assertEqual(len(set(seen)),15)

if __name__=='__main__':unittest.main()
