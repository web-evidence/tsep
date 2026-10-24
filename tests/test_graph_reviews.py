import copy
import hashlib
import json
from pathlib import Path
import unittest
from conformance.graph_reviews import read
P=Path(__file__).resolve().parent/'fixtures'
class GraphReviews(unittest.TestCase):
    def test_27_prefrozen_review_cases(self):
        raw=(P/'ts18-review-component-cases-r1.json').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),'4227ccf2bf0d3866cead0aa1c1a922e6c89c9347f115d0056522bd21a6a946e3')
        cases=json.loads(raw)['cases'];self.assertEqual(len(cases),27)
        for case in cases:
            with self.subTest(case=case['id']):
                before=copy.deepcopy(case['input']);value=read(**case['input'])
                self.assertEqual(value['outcome'],case['expected'],value)
                for subject,want in case['subject_outcomes'].items():
                    self.assertEqual(next(s['outcome'] for s in value['subjects'] if s['subject']==subject),want)
                self.assertFalse(value['authenticates_reviewer']);self.assertFalse(value['adjudicates_rationale'])
                self.assertEqual(before,case['input'])
if __name__=='__main__':unittest.main()
