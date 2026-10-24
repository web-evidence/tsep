"""Retained actual parsing, contradictory source segments and unapplied boundaries."""
import copy
import unittest
from unittest.mock import patch

from experiments import source_markers as reader
from scripts.source_markers_check import fixture


class SourceMarkers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases={c['id']:c for f in ('source-markers-v1.json','source-markers-contexts-v1.json') for c in fixture(f)['cases']}
        cls.observed={c['id']:c['inventory'] for c in fixture('source-markers-observations-v1.json')['observations']}

    def reading(self,id,mode='enabled'):
        return copy.deepcopy(self.observed[id]['readings'][mode])

    def test_frozen_cases_with_explicit_corrections(self):
        corrections={c['case_id']:c for c in [fixture('source-markers-v1-amendment.json'),fixture('source-markers-contexts-v1-amendment.json')]}
        self.assertEqual(set(self.cases),set(self.observed));self.assertEqual(len(self.cases),52)
        for id,case in self.cases.items():
            with self.subTest(id=id):
                readings,consensus=reader.hypotheses(self.observed[id],case['criteria'])
                expected=corrections.get(id,case)
                self.assertEqual(consensus,expected['candidate_consensus'])
                for mode,r in readings.items():
                    self.assertEqual({'complete':r['complete'],'segments':None if r['segments'] is None else [s['data'] for s in r['segments']],
                                      'candidate_outcome':r['candidate_outcome']},expected['expected'][mode])

    def test_source_intervals_match_original_bytes_including_unicode(self):
        for id in ('unicode-nbsp','entity-contiguous','raw-crlf-normalized','noscript-forbidden-attribute'):
            raw=self.cases[id]['html'].encode()
            for mode in reader.MODES:
                segments,_=reader.project(self.reading(id,mode),mode)
                for s in segments:
                    a,b=s['body_span_bytes'];self.assertEqual(raw[a:b].decode(),s['raw_source'])

    def test_attribute_inside_noscript_is_not_silently_dropped(self):
        r,consensus=reader.hypotheses(self.observed['noscript-forbidden-attribute'],self.cases['noscript-forbidden-attribute']['criteria'])
        self.assertEqual([r[m]['candidate_outcome'] for m in reader.MODES],['fail','pass'])
        self.assertEqual(consensus,'inconclusive')

    def test_independent_marker_failures_do_not_union_modes(self):
        r,c=reader.hypotheses(self.observed['noscript-two-no-union'],self.cases['noscript-two-no-union']['criteria'])
        self.assertEqual(c,'inconclusive')
        self.assertEqual(r['enabled']['candidate_outcome'],'pass')
        self.assertEqual(r['disabled']['candidate_outcome'],'fail')

    def test_source_split_forbidden_is_not_a_visibility_claim(self):
        r,c=reader.hypotheses(self.observed['forbidden-split-is-not-found'],self.cases['forbidden-split-is-not-found']['criteria'])
        self.assertEqual(c,'pass');self.assertEqual(r['enabled']['present_forbidden'],[])

    def test_reported_error_refuses_whole_reading_even_after_contradiction(self):
        r=self.reading('forbidden-after-good');r['parse_errors']=[{'code':'synthetic-error'}]
        inv=copy.deepcopy(self.observed['forbidden-after-good']);inv['readings']['enabled']=r
        rows,c=reader.hypotheses(inv,self.cases['forbidden-after-good']['criteria'])
        self.assertEqual(rows['disabled']['candidate_outcome'],'fail');self.assertEqual(c,'inconclusive')
        self.assertIsNone(rows['enabled']['segments'])

    def test_missing_tree_cannot_be_empty_success(self):
        inv=copy.deepcopy(self.observed['ordinary']);inv['readings']['enabled']={'complete':False,'reason':'synthetic bound','nodes':[],'parse_errors':[]}
        rows,c=reader.hypotheses(inv,self.cases['ordinary']['criteria']);self.assertEqual(c,'inconclusive');self.assertIsNone(rows['enabled']['segments'])

    def test_fused_or_overlapping_text_cannot_create_marker(self):
        r=self.reading('ordinary');n=next(n for n in r['nodes'] if n['kind']=='text');n['raw_source']='Ex</x>pected'
        with self.assertRaisesRegex(ValueError,'Non-contiguous'):reader.project(r,'enabled')
        r=self.reading('forbidden-after-good');texts=[n for n in r['nodes'] if n['kind']=='text'];texts[1]['body_span_bytes']=texts[0]['body_span_bytes']
        with self.assertRaisesRegex(ValueError,'Overlapping'):reader.project(r,'enabled')

    def test_numeric_cr_stays_in_raw_tree_but_reported_error_is_not_ignored(self):
        r=self.reading('entity-cr-retained')
        self.assertIn('Expected\rvalue',[n['data'] for n in r['nodes'] if n['kind']=='text'])
        self.assertIn('control-character-reference',[e['code'] for e in r['parse_errors']])
        reader.criteria({'required_markers':['Expected\rvalue'],'forbidden_markers':[]})
        with self.assertRaisesRegex(ValueError,'Reported parse5'):reader.project(r,'enabled')

    def test_svg_styles_excluded_without_excluding_html_breakout(self):
        for id,want in [('svg-style-excluded','pass'),('svg-style-breakout','fail')]:
            rows,c=reader.hypotheses(self.observed[id],self.cases[id]['criteria']);self.assertEqual(c,want)
        r=self.reading('svg-style-breakout');self.assertEqual(r['parse_errors'],[])
        forbidden=next(n for n in r['nodes'] if n['kind']=='text' and n['data']=='Forbidden')
        self.assertEqual(r['nodes'][forbidden['parent']]['namespace'],reader.HTML)

    def test_no_objective_never_emits_a_candidate_outcome(self):
        for id in ('ordinary','foreign-text-outside'):
            r,c=reader.hypotheses(self.observed[id],None);self.assertIsNone(c)
            self.assertTrue(all(x['candidate_outcome'] is None for x in r.values()))

    def test_marker_and_match_bounds_preserve_unknown(self):
        for objective in (None,{}, {'required_markers':['x']*2,'forbidden_markers':[]},
                          {'required_markers':['x'*4097],'forbidden_markers':[]},
                          {'required_markers':[str(i) for i in range(65)],'forbidden_markers':[]},
                          {'required_markers':['Expected'],'forbidden_markers':['Expected']}):
            with self.assertRaises(ValueError):reader.criteria(objective)
        with patch.object(reader,'MAX_MATCHES',1):
            r,c=reader.hypotheses(self.observed['ordinary'],{'required_markers':['Expected','xpected'],'forbidden_markers':[]})
        self.assertEqual(c,'inconclusive');self.assertTrue(all(x['segments'] is None for x in r.values()))
        with patch.object(reader,'MAX_SEGMENTS',0),self.assertRaisesRegex(ValueError,'segment bound'):
            reader.project(self.reading('ordinary'),'enabled')

    def test_runtime_and_encoding_failure_have_no_lexical_fallback(self):
        raw=self.cases['ordinary']['html'].encode()
        with self.assertRaisesRegex(ValueError,'unavailable'):reader.observe(raw,content_types=['text/html; charset=utf-8'],node='/missing/node24')
        with self.assertRaises(ValueError):reader.observe(b'\xff',content_types=['text/html; charset=utf-8'])

    def test_exact_replay_rejects_different_inputs_tools_or_result(self):
        raw=b'synthetic';saved={'kind':'unapplied-source-marker-readings','experiment_version':reader.VERSION,'normative_effect':'none',
                             'body_sha256':reader.sha(raw),'source_sha256':reader.identity(),'content_types':['text/html; charset=utf-8'],'criteria':None}
        with self.assertRaisesRegex(ValueError,'body identity'):reader.replay(saved,b'changed',node='/unused')
        changed=dict(saved,source_sha256={})
        with self.assertRaisesRegex(ValueError,'Exact source-marker tool'):reader.replay(changed,raw,node='/unused')
        with patch.object(reader,'observe',return_value=dict(saved,unexpected=True)),self.assertRaisesRegex(ValueError,'replay differs'):
            reader.replay(saved,raw,node='/unused')


if __name__=='__main__':unittest.main()
