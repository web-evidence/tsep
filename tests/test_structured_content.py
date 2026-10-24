"""TS31 prefrozen contradictions, authentic input replay and honest missing evidence."""
import copy
import hashlib
import json
import os
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

import tsep
from adapters import captures, replay, structured_intake as intake
from conformance import structured_content as s
from conformance.evaluate import evaluate
from reports import html

ROOT = Path(__file__).resolve().parents[1]
FROZEN = 'f7abbe706ab165e55a514ae6fa07ddadf992a302fa442e62c6d8cde774afa97a'
NODE = os.environ.get('TSEP_SOURCE_NODE')


def cases():
    rows=[]
    for name,want in [('structured-content-v1.json',FROZEN),('structured-content-boundaries-v1.json','7f2115d8ba8edee2c414b65954b7fc13bb83f1e4e9790a64b3733bb00f8e111a')]:
        p = ROOT/'tests/fixtures'/name; raw=p.read_bytes()
        if hashlib.sha256(raw).hexdigest() != want or p.with_suffix('.sha256').read_text().strip() != want:
            raise ValueError('Changed prefrozen TS31 oracle')
        rows.extend(json.loads(raw)['cases'])
    correction=tsep.read_json(ROOT/'tests/fixtures/structured-content-reference-limits-v1.json')
    for case in rows:
        for row in case['expected']:
            if row.get('reference_limit'):row['basis']=correction['basis']
    return rows


def data(name='complete'):
    return copy.deepcopy(next(c['input'] for c in cases() if c['id']=='structured-content-v1-'+name))


class StructuredContent(unittest.TestCase):
    def test_prefrozen_oracle_is_distributed_unchanged(self):
        rows=cases();self.assertEqual(len(rows),59)
        self.assertEqual(tsep.read_json(ROOT/'conformance/cases.json')['cases'][1435:1494],rows)

    @unittest.skipUnless(NODE,'Explicit Node 24 required for full native TS31 observations')
    def test_all_prefrozen_cases_offline(self):
        with patch.object(socket,'socket',side_effect=AssertionError('No network collection')):
            for c in cases():
                before=copy.deepcopy(c['input'])
                with self.subTest(case=c['id']):
                    self.assertEqual([r['outcome'] for r in evaluate(c['input'])],[r['outcome'] for r in c['expected']])
                    self.assertEqual(c['input'],before)

    def test_missing_runtime_is_explicit_unknown(self):
        with patch.dict(os.environ,{},clear=True):
            rows=evaluate(data());self.assertEqual([r['outcome'] for r in rows],['pass','inconclusive','inconclusive'])
            self.assertIn('TSEP_SOURCE_NODE',rows[1]['reason'])

    def test_bad_nested_values_are_not_exceptions_or_green(self):
        for key in ('jsonld','intent','context'):
            for value in (None,False,[],{},'broken'):
                t=data()['targets'][0];t[key]=value
                for rule in s.RULES:
                    with self.subTest(key=key,value=value,rule=rule):self.assertEqual(s.assess(t,rule)[0],'inconclusive')

    @unittest.skipUnless(NODE,'Explicit Node 24 required for native TS31 bundle/replay')
    def test_reports_replay_and_synthetic_provenance(self):
        for name,status in [('complete','C'),('known-fabrication-missing-state','NC'),('missing-surface-review','NT'),('source-invalid-json','NC')]:
            with self.subTest(name=name),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);p=root/'input.json';p.write_text(json.dumps(data(name)))
                captures.build(p,root/'bundle',assessor='Fictional reviewer',label='Authored TS31',selection_method='One fictional page',access='synthetic',mode='semiAuto')
                report=tsep.read_json(root/'bundle/report.json');self.assertEqual(report['results'][0]['status'],status)
                self.assertTrue({'structured-data','content','intent'} <= {a['kind'] for a in report['artifacts']})
                self.assertIn('structured_content_interpretation',tsep.decision(report))
                result=replay.replay(root/'bundle',root/'replay');self.assertTrue(result['same_atomic_results']);self.assertTrue(result['same_gate'])
                for language in ('fr','en'):
                    rendered=html.render(root/'bundle/report.json',language=language)
                    self.assertIn(html.TEXT[language]['structured_note'],rendered)
                    self.assertIn(html.TEXT[language]['structured_values'],rendered)

    def test_partial_scope_cannot_be_complete_control(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);d=data();d['rules']=['TS31-A01'];p=root/'input.json';p.write_text(json.dumps(d))
            captures.build(p,root/'bundle',assessor='Fictional reviewer',label='Partial TS31',selection_method='Authored',access='synthetic',mode='semiAuto')
            self.assertEqual(tsep.read_json(root/'bundle/report.json')['results'][0]['status'],'NT')
            with self.assertRaises(tsep.Invalid):
                captures.build(p,root/'public',assessor='Fictional',label='False public',selection_method='Authored',access='public',mode='semiAuto')

    def test_escaped_report_never_invokes_reader(self):
        atom={'reason':s.PREFIX+json.dumps({'rows':[dict(subject='<script>bad</script>',outcome='inconclusive',reason='<img src=x>')]})}
        with patch.object(s,'assess',side_effect=AssertionError('No reassessment')):
            out=html.structured_values(atom,html.TEXT['fr'])
        self.assertNotIn('<script>',out);self.assertNotIn('<img',out);self.assertIn('&lt;script&gt;',out)

    def test_native_and_processor_sources_bound_to_adapter(self):
        sources=captures.source_files()
        self.assertTrue({'conformance/structured_content.py','experiments/jsonld_rendered.py','experiments/jsonld_html.py','experiments/jsonld_processing.py','experiments/jsonld_processing.mjs','third_party/jsonld/jsonld-9.0.0.tgz'} <= set(sources))

    @unittest.skipUnless(NODE,'Explicit Node 24 required for TS31 intake')
    def test_intake_blank_reviews_and_immutable_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);t=data()['targets'][0];full=copy.deepcopy(t['structured_reviews'])
            t['structured_reviews']=[{k:r[k] for k in ('surface_id','content')} for r in full]
            p=root/'target.json';p.write_text(json.dumps(t))
            intake.plan_request(p,root/'plan')
            prior=tsep.read_json(root/'plan/plan-review-request.json')['review']
            self.assertFalse(prior['complete']);self.assertIsNone(prior['reviewer']);self.assertEqual(prior['scope'],'unknown')
            intake.prepare(p,root/'prepared');rp=root/'prepared/review-request.json';request=tsep.read_json(rp)
            self.assertEqual(len(request['reviews']),3)
            self.assertTrue(all(not r['review']['complete'] and r['review']['reviewer'] is None for r in request['reviews']))
            self.assertTrue(all(e[k]['value']=='unknown' and e[k]['reason'] is None for r in request['reviews'] for e in r['entities'] for k in s.JUDGMENTS))
            intake.build(root/'prepared',rp,root/'blank','Fictional reviewer')
            self.assertEqual(tsep.read_json(root/'blank/report.json')['results'][0]['status'],'NT')
            request['reviews']=full;review=root/'reviews.json';review.write_text(json.dumps(request))
            intake.build(root/'prepared',review,root/'complete','Fictional reviewer')
            self.assertEqual(tsep.read_json(root/'complete/report.json')['results'][0]['status'],'C')
            request['reviews'][0]['content']['raw_text']+=' changed';review.write_text(json.dumps(request))
            with self.assertRaisesRegex(tsep.Invalid,'Content changed'):intake.build(root/'prepared',review,root/'changed','Fictional')
            (root/'prepared/originals/target.json').write_text('{}')
            with self.assertRaisesRegex(tsep.Invalid,'Changed intake file'):intake.build(root/'prepared',rp,root/'tampered','Fictional')


if __name__=='__main__':unittest.main()
