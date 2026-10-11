"""HTTP context/destination separation, attribution, bounds and retained unknowns."""
import copy
import hashlib
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from adapters import captures, replay
from conformance import http_canonical as policy
from conformance.evaluate import binding_digest, evaluate
from reports.html import render
import tsep

ROOT = Path(__file__).resolve().parents[1]
P = 'https://example.com/product'
O = 'https://example.com/other'


def fixture():
    p = ROOT/'tests/fixtures/http-canonical-context-v1.json'
    raw = p.read_bytes()
    if hashlib.sha256(raw).hexdigest() != p.with_suffix('.sha256').read_text().strip():
        raise ValueError('Changed prefrozen HTTP Link expectations')
    return json.loads(raw)


class HTTPCanonical(unittest.TestCase):
    def data(self, name):
        return copy.deepcopy(next(c['input'] for c in fixture()['cases'] if c['id'] == 'http-canonical-'+name))

    def reading(self, fields, required=False, final=P):
        notes = []
        outcome = policy.assess({'link': fields}, final, P, required, policy.READER,
                               document_url=final, source_sha256='0'*64,
                               observed_at='2026-10-11T00:00:00Z', diagnostics=notes)
        return outcome, notes[0]

    def test_all_prefrozen_expectations_and_corpus_inclusion(self):
        rows = fixture()['cases']; self.assertEqual(len(rows), 61)
        corpus = {c['id']: c for c in tsep.read_json(ROOT/'conformance/cases.json')['cases']}
        for c in rows:
            with self.subTest(case=c['id']):
                self.assertEqual(corpus[c['id']], c)
                expected = [{k: e[k] for k in ('rule_id', 'target', 'outcome')} for e in c['expected']]
                actual = [{k: e[k] for k in ('rule_id', 'target', 'outcome')} for e in evaluate(c['input'])]
                self.assertEqual(actual, expected)

    def test_attribution_first_rel_and_repetitions_are_retained(self):
        notes = []; d = self.data('first-rel-retained'); evaluate(d, source_observations=notes)
        r = notes[0]['observations'][0]; item = r['items'][0]
        self.assertEqual(item['ignored_later_rel'], ['alternate'])
        self.assertEqual(item['parameters'], [{'name':'rel', 'value':'canonical'}, {'name':'rel', 'value':'alternate'}])
        self.assertEqual(r['source_http_sha256'], binding_digest(d['targets'][0]['documents'][0]['http']))
        self.assertEqual((r['document_url'], r['final_url']), (P, P))
        _, r = self.reading([f'<{P}>; rel=canonical, <{P}>; rel=canonical', f'<{P}>; rel=canonical'])
        self.assertEqual([(i['field_index'], i['item_index']) for i in r['items']], [(0,0),(0,1),(1,0)])
        self.assertEqual(r['counts']['compatible'], 3)

    def test_context_does_not_supply_a_different_member(self):
        notes=[];evaluate(self.data('anchor-other-member-not-transferred'),source_observations=notes)
        records=notes[0]['observations']
        self.assertEqual(records[0]['items'][0]['classification'],'other-context')
        self.assertEqual(records[1]['counts']['compatible'],0)

    def test_relative_resolution_preserves_components(self):
        base='https://example.com/a/b?old'
        expected={
            '':'https://example.com/a/b?old', '?':'https://example.com/a/b?',
            '#':'https://example.com/a/b?old#', '?new#part':'https://example.com/a/b?new#part',
            'c':'https://example.com/a/c', './c':'https://example.com/a/c', '../c':'https://example.com/c',
            '../../c':'https://example.com/c', '/a//c':'https://example.com/a//c',
            'c//d':'https://example.com/a/c//d', './':'https://example.com/a/',
            '.':'https://example.com/a/', '..':'https://example.com/',
            '/c/.':'https://example.com/c/', '/c/..':'https://example.com/',
            '/c/./d/../e':'https://example.com/c/e',
            '?q=/../x':'https://example.com/a/b?q=/../x',
            '#/../x':'https://example.com/a/b?old#/../x',
            '//other.example/a':'https://other.example/a',
            'https://other.example/x/../y':'https://other.example/y',
            '%2e%2e/c':'https://example.com/a/%2e%2e/c',
            'a;b?c,d#e':'https://example.com/a/a;b?c,d#e',
        }
        for ref, result in expected.items():
            with self.subTest(ref=ref):self.assertEqual(policy.resolve(ref,base),result)
        self.assertEqual(policy.resolve('x','https://example.com'),'https://example.com/x')

    def test_equivalent_or_unqualified_context_never_becomes_foreign(self):
        for anchor in ('https://EXAMPLE.com/product','https://example.com:443/product',
                       'https://example.com./product','/%70roduct','https://[::1]/product','#','?'):
            with self.subTest(anchor=anchor):
                outcome,r=self.reading([f'<{O}>; rel=canonical; anchor="{anchor}"'])
                self.assertEqual(outcome[0],'inconclusive');self.assertEqual(r['counts']['other-context'],0)
        self.assertEqual(self.reading([f'<{O}>; rel=canonical; anchor="/product"'],
                                     final='https://example.com/x/../product')[0][0],'inconclusive')

    def test_all_literal_destinations_are_still_compared(self):
        for dest in ('/product',P+'#',P+'#part','https://EXAMPLE.com/product',P+'?',''):
            with self.subTest(dest=dest):
                self.assertEqual(self.reading([f'<{dest}>; rel=canonical'])[0][0],'fail')

    def test_quoted_pairs_and_delimiters_do_not_fabricate_links(self):
        for value in (f'<{P}>; rel="canonical  alternate"', f'<{P}>; rel="cano\\nical"'):
            self.assertEqual(self.reading([value],True)[0][0],'pass')
        for tail in ('title="one,two;three"', 'title="quote\\\";comma,here"'):
            _,r=self.reading([f'<{P}>; rel=canonical; '+tail])
            self.assertEqual(len(r['items']),1);self.assertEqual(r['items'][0]['classification'],'unknown')
        self.assertEqual(self.reading([f'<{P}>; rel=canonical; title*=UTF-8\'en\'Example'])[0][0],'inconclusive')
        _,r=self.reading([f'<{O},part>; rel=canonical'])
        self.assertEqual(len(r['items']),1);self.assertEqual(r['items'][0]['target'],O+',part')

    def test_bad_uri_or_parameter_never_becomes_conclusive(self):
        for value in (f'<{P}%ZZ>; rel=canonical', '<https://[bad]>; rel=canonical',
                      '<https://example.com:bad/x>; rel=canonical', f'<{P}>; rel',
                      f'<{P}>; rel=""; rel=canonical', f'<{P}>; rel=canonical; anchor',
                      f'<{P}>; rel=canonical; anchor="/one"; anchor="/one"',
                      f'<{P}>; rel="canonical\r\n alternate"',f'<{P}>; rel="canonicál"'):
            with self.subTest(value=value):self.assertEqual(self.reading([value],True)[0][0],'inconclusive')

    def test_conflict_is_preserved_only_with_clear_item_boundaries(self):
        conflict=f'<{O}>; rel=canonical'; unclosed=f'<{P}>; rel="canonical'
        self.assertEqual(self.reading([conflict+', '+unclosed])[0][0],'fail')
        self.assertEqual(self.reading([unclosed+', '+conflict])[0][0],'inconclusive')
        self.assertEqual(self.reading([unclosed,conflict])[0][0],'fail')

    def test_completed_conflict_survives_nonascii_in_later_item(self):
        # Found during review after the 61-case freeze; keep it as an added regression.
        field=f'<{O}>; rel=canonical, <{P}>; rel="canonicál"'
        result,reading=self.reading([field])
        self.assertEqual(result[0],'fail')
        self.assertEqual([i['classification'] for i in reading['items']],['conflict','unknown'])
        d=self.data('conflict-before-unclosed');doc=d['targets'][0]['documents'][0]
        doc['http'][0]['response']=doc['http'][0]['response'].replace('rel="canonical\r\n\r\n','rel="canonicál"\r\n\r\n')
        doc['exemption_review']['source_http_sha256']=binding_digest(doc['http'])
        self.assertEqual(evaluate(d)[0]['outcome'],'fail')

    def test_population_and_diagnostic_bounds_refuse_whole_reader(self):
        conflict=f'<{O}>; rel=canonical'
        for limit in ('MAX_FIELDS','MAX_LINKS','MAX_BYTES','MAX_DIAGNOSTIC_BYTES'):
            with self.subTest(limit=limit),patch.object(policy,limit,0):
                outcome,r=self.reading([conflict])
                self.assertEqual(outcome[0],'inconclusive');self.assertNotIn('counts',r)
        outcome,r=self.reading([conflict]);size=len(json.dumps(r,ensure_ascii=False,indent=2).encode())
        with patch.object(policy,'MAX_DIAGNOSTIC_BYTES',size):self.assertEqual(self.reading([conflict])[0][0],'fail')
        with patch.object(policy,'MAX_DIAGNOSTIC_BYTES',size-1):self.assertEqual(self.reading([conflict])[0][0],'inconclusive')

    def test_missing_or_unknown_selector_does_not_migrate(self):
        d=self.data('first-rel-retained');del d['targets'][0]['intent']['canonical']['http_reader']
        self.assertEqual(evaluate(d)[0]['outcome'],'inconclusive')
        for value in (None,'unknown',''):
            d['targets'][0]['intent']['canonical']['http_reader']=value
            self.assertEqual(evaluate(d)[0]['outcome'],'inconclusive')

    def test_stale_review_is_not_repaired_by_header_success(self):
        d=self.data('destination-good-review');d['targets'][0]['content_review']['source_sha256']='0'*64
        self.assertEqual(evaluate(d)[0]['outcome'],'inconclusive')

    def test_intermediate_headers_are_not_final_declarations(self):
        d=self.data('intermediate-link-not-final');notes=[];result=evaluate(d,source_observations=notes)
        self.assertEqual(result[0]['outcome'],'pass')
        last=notes[0]['observations'][-1]
        self.assertEqual(last['document_url'],P+'-old');self.assertEqual(last['final_url'],P)
        self.assertNotIn(O,json.dumps(last['items']))
        self.assertIn(O,d['targets'][0]['documents'][-1]['http'][0]['response'])

    def test_report_html_earl_gate_and_offline_replay_keep_http_observations(self):
        for name,status in [('plain','C'),('missing-render-not-pass','NT'),('unknown-plus-conflict','NC')]:
            with self.subTest(case=name),tempfile.TemporaryDirectory() as folder:
                d=self.data(name);d['rules']=['TS10-A01','TS10-A02','TS10-A03','TS10-A04']
                root=Path(folder);inp=root/'input.json';inp.write_text(json.dumps(d))
                with patch.object(socket,'socket',side_effect=AssertionError('No network')),patch.object(socket,'getaddrinfo',side_effect=AssertionError('No DNS')):
                    captures.build(inp,root/'bundle',assessor='Synthetic supplied review',label='SYNTHETIC HTTP canonical',
                                   selection_method='Authored family; no actual human review',access='synthetic')
                    report=tsep.read_json(root/'bundle/report.json')
                    self.assertEqual(report['results'][0]['status'],status)
                    self.assertTrue(tsep.read_json(root/'bundle/gate.json')['synthetic_evidence'])
                    for content in (render(root/'bundle/report.json',language='fr'),
                                    render(root/'bundle/report.json',language='en'),
                                    (root/'bundle/earl.jsonld').read_text()):self.assertIn(policy.READER,content)
                    r=replay.replay(root/'bundle',root/'replay');self.assertTrue(r['same_source_observations'])
                    evidence=root/'bundle/observations/source-observation-1.json'
                    value=json.loads(evidence.read_text());self.assertEqual(value['observations'][0]['reader'],policy.READER)


if __name__ == '__main__':unittest.main()
