"""TS44 evidence boundaries; Node qualification is an explicit separate command."""
import copy
import hashlib
import json
import os
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from conformance import critical_content as content
from conformance.evaluate import evaluate
from conformance.run import compare
from adapters import captures,replay
from reports import html
import tsep

ROOT=Path(__file__).resolve().parents[1]
NAMES=('critical-content-v1.json','critical-content-boundaries-v1.json')


def cases():
    rows=[]
    for name in NAMES:
        p=ROOT/'tests/fixtures'/name;raw=p.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=p.with_suffix('.sha256').read_text().strip():raise ValueError('Frozen critical fixture changed')
        rows+=json.loads(raw)['cases']
    return rows


class CriticalContent(unittest.TestCase):
    def data(self,name='server-html'):
        return copy.deepcopy(next(c['input'] for c in cases() if c['id']=='critical-content-'+name))

    def test_frozen_cases_exact_in_corpus_and_no_silent_runtime_pass(self):
        rows=cases();self.assertEqual(len(rows),71)
        corpus=tsep.read_json(ROOT/'conformance/cases.json')['cases'];self.assertEqual(corpus[980:1051],rows)
        with patch.dict(os.environ,{'TSEP_SOURCE_NODE':'/unavailable/node24'}):
            for c in rows:
                with self.subTest(case=c['id']):
                    _,disagreements,_=compare(c['expected'],evaluate(c['input']))
                    self.assertEqual(disagreements,[])

    def test_json_pointer_order_unicode_arrays_and_missing_values(self):
        document={'a/b':'slash','~1':'tilde-one','é':'unicode','list':['zero']}
        for p,value in [('/a~1b','slash'),('/~01','tilde-one'),('/é','unicode'),('/list/0','zero')]:
            self.assertEqual(content.pointer(document,p),value)
        self.assertIsNone(content.pointer(document,'/missing'));self.assertIsNone(content.pointer(document,'/list/4'))
        for p in ('/list/00','/list/-','/a~2b','/list/0/more'):
            with self.subTest(pointer=p),self.assertRaises(ValueError):content.pointer(document,p)
        for value in (None,1,False,{},[]):
            with self.assertRaises(ValueError):content.pointer({'value':value},'/value')
        self.assertEqual(content.pointer('root',''),'root')

    def test_text_convention_does_not_fold_unicode_case_or_add_spaces(self):
        self.assertEqual(content.text(' A\tB\r\nC\f '),'A B C')
        self.assertEqual(content.text('A\u00a0B'),'A\u00a0B')
        self.assertNotEqual(content.text('É'),content.text('é'))

    def test_plan_review_must_predate_capture_and_bind_whole_intent(self):
        t=self.data()['targets'][0]
        self.assertEqual(content.assess(t,'TS44-A01')[0],'pass')
        t['intent']['critical_content']['items'][0]['expected']='Changed'
        self.assertEqual(content.assess(t,'TS44-A01')[0],'inconclusive')
        t['critical_plan_review']['binding_sha256']=content.plan_binding(t)
        self.assertEqual(content.assess(t,'TS44-A01')[0],'pass')
        t['critical_plan_review']['observed_at']='2026-10-10T10:01:00Z'
        self.assertEqual(content.assess(t,'TS44-A01')[0],'inconclusive')

    def test_semantic_review_binds_exact_source_resource_or_state(self):
        t=self.data('linked-json')['targets'][0]
        for subject in ('resource','render:loaded'):
            before=content.content_binding(t,subject)
            t['intent']['critical_content']['consumers'][0]['reason']+=' changed'
            self.assertNotEqual(content.content_binding(t,subject),before)

    def test_missing_node_failure_cached_only_within_one_rule_evaluation(self):
        t=self.data()['targets'][0];p,at=content.header(t);e=content.Evidence(t,p,at,{})
        with patch.object(content.source_content,'inventory',side_effect=ValueError('unavailable')) as inv:
            for _ in range(3):
                with self.assertRaises(ValueError):e.source('page')
            self.assertEqual(inv.call_count,1)
            e2=content.Evidence(t,p,at,{})
            with self.assertRaises(ValueError):e2.source('page')
            self.assertEqual(inv.call_count,2)

    def test_json_conflict_survives_missing_node_and_missing_render(self):
        t=self.data('json-resource-stale')['targets'][0];t.pop('render');notes=[]
        with patch.dict(os.environ,{'TSEP_SOURCE_NODE':'/unavailable/node24'}):
            self.assertEqual(content.assess(t,'TS44-A03',diagnostics=notes)[0],'fail')
        self.assertTrue(any(r['outcome']=='inconclusive' for r in notes[0]['rows']))
        self.assertTrue(any(r.get('actual')=='r1' and r.get('expected')=='r2' for r in notes[0]['rows']))

    def test_malformed_inputs_do_not_crash_or_invent_pass(self):
        for field in ('intent','critical_plan_review','critical_reviews','render','http','documents'):
            for value in (None,[],{},False,'bad'):
                t=self.data('linked-json')['targets'][0];t[field]=value
                for rule in ('TS44-A01','TS44-A02','TS44-A03'):
                    with self.subTest(field=field,value=value,rule=rule):
                        self.assertIn(content.assess(t,rule)[0],('pass','inconclusive'))

    def test_import_retains_content_evidence_and_replays_without_network(self):
        data=self.data('json-resource-stale')
        with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{'TSEP_SOURCE_NODE':'/unavailable/node24'}):
            root=Path(d);p=root/'input.json';p.write_text(json.dumps(data))
            with patch.object(socket,'socket',side_effect=AssertionError('No network')):
                captures.build(p,root/'bundle',assessor='Synthetic importer',label='Authored critical-content exercise',selection_method='One authored case',access='synthetic',mode='semiAuto')
                result=replay.replay(root/'bundle',root/'replay')
            self.assertTrue(result['replayed']);self.assertTrue(result['same_source_observations'])
            report=tsep.read_json(root/'bundle/report.json');self.assertEqual(report['results'][0]['status'],'NC')
            self.assertTrue({'http','html','content','intent','render'} <= {a['kind'] for a in report['artifacts']})
            for lang in ('fr','en'):
                output=html.render(root/'bundle/report.json',language=lang)
                self.assertIn(html.TEXT[lang]['critical_content_note'],output);self.assertNotIn('<script',output)

    def test_synthetic_reviews_cannot_be_relabelled_public_without_dom(self):
        for field in ('critical_plan_review','critical_reviews'):
            data=self.data();t=data['targets'][0];t.pop('render')
            for other in ('critical_plan_review','critical_reviews'):
                if other!=field:t.pop(other)
            with tempfile.TemporaryDirectory() as d:
                p=Path(d)/'input.json';p.write_text(json.dumps(data))
                with self.assertRaisesRegex(tsep.Invalid,'provenance'):
                    captures.build(p,Path(d)/'out',assessor='Importer',label='No laundering',selection_method='One case',access='public')

    def test_partial_scope_cannot_close_control(self):
        data=self.data();data['rules']=['TS44-A01']
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'input.json';p.write_text(json.dumps(data))
            captures.build(p,Path(d)/'out',assessor='Synthetic',label='Partial',selection_method='One case',access='synthetic')
            self.assertEqual(tsep.read_json(Path(d)/'out/report.json')['results'][0]['status'],'NT')

    def test_diagnostic_html_escapes_critical_values(self):
        reason='Critical content evidence / preuves contenu critique: '+json.dumps({'rows':[{'subject':'fact','actual':'<script>bad</script>','outcome':'fail','reason':'<img>'}]})
        output=html.agent_values({'reason':reason},html.TEXT['fr']);self.assertIn('&lt;script&gt;',output);self.assertNotIn('<script>',output)


if __name__=='__main__':unittest.main()
