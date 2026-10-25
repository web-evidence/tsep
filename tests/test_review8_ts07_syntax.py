"""R-077: independently authored syntax traps; no live observation or Google call."""
import hashlib
import json
from pathlib import Path
import unittest
from conformance.evaluate import evaluate, directive_result
from conformance.google_directives import PROFILE, LEGACY_PROFILE, result, tokens

ROOT=Path(__file__).resolve().parents[1]
NOW='2026-10-25T05:00:00Z'

class GoogleSyntaxV2(unittest.TestCase):
    def test_authored_conformance_matrix(self):
        corpus=json.loads((ROOT/'tests/fixtures/ts07-google-syntax-v2.json').read_text())
        self.assertTrue(corpus['synthetic']);self.assertEqual(len(corpus['cases']),35)
        for case in corpus['cases']:
            with self.subTest(case=case['id']):
                actual=evaluate(case['input'])
                self.assertEqual([{k:r[k] for k in ('rule_id','target','outcome')} for r in actual],case['expected'])

    def test_undocumented_syntax_is_attributed_without_invented_tokens(self):
        notes=[]
        state,reason=result({'x-robots-tag':['googlebot: noindex nofollow']},[],
            {'directive_policy':PROFILE,'crawler':'googlebot','indexing':'exclude'},NOW,notes)
        self.assertEqual(state,'inconclusive');self.assertIn('undocumented or unsupported syntax',reason)
        self.assertEqual(notes[0]['unsupported_syntax'],['googlebot: noindex nofollow'])
        self.assertEqual(notes[0]['tokens'],[])

    def test_legacy_profile_is_explicit_not_reinterpreted(self):
        for profile,expected in [(LEGACY_PROFILE,'pass'),(PROFILE,'inconclusive')]:
            got=result({},['noindex nofollow'],{'directive_policy':profile,'crawler':'googlebot','indexing':'exclude'},NOW)
            self.assertEqual(got[0],expected)

    def test_date_comma_is_scoped_to_a_date_directive(self):
        self.assertEqual(list(tokens('noindex, 21 Oct 2026 00:00:00 GMT',PROFILE)),['noindex','21 Oct 2026 00:00:00 GMT'])
        self.assertEqual(list(tokens('googlebot: unavailable_after: Wednesday, 21-Oct-26 00:00:00 GMT, nofollow',PROFILE)),
            ['googlebot: unavailable_after: Wednesday, 21-Oct-26 00:00:00 GMT','nofollow'])

    def test_both_static_html_readings_preserve_independent_failure(self):
        body='<!doctype html><html><head><meta name="robots" content="index follow"></head><body>Fictional</body></html>'
        intent={'directive_policy':PROFILE,'source_reader':'html-tree-directives-v1','crawler':'googlebot','indexing':'allow'}
        headers={'content-type':['text/html; charset=utf-8']}
        self.assertEqual(directive_result(headers,body,intent,source=True,observed_at=NOW)[0],'inconclusive')
        self.assertEqual(directive_result(dict(headers,**{'x-robots-tag':['noindex']}),body,intent,source=True,observed_at=NOW)[0],'fail')

    def test_normative_delta_is_only_ts07_a01(self):
        baseline=json.loads((ROOT/'provenance/v030-draft8-r077-baseline.json').read_text())
        protocol=json.loads((ROOT/'spec/protocol.json').read_text())
        self.assertEqual(protocol['version'],'0.3.0-draft.9')
        for control in protocol['controls']:
            if control['id']!='TS07':
                digest=hashlib.sha256(json.dumps(control,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
                self.assertEqual(digest,baseline['controls_sha256'][control['id']])
            else:
                old=baseline['TS07'];self.assertEqual(control['rule_version'],'0.3.0-draft.9')
                self.assertEqual({k for k in control if control[k]!=old[k]},{'rule_version','acceptance_note','rules'})
                self.assertEqual({k for k in control['rules'][0] if control['rules'][0][k]!=old['rules'][0][k]},{'procedure'})
                self.assertEqual(control['rules'][1:],old['rules'][1:])

if __name__=='__main__':unittest.main()
