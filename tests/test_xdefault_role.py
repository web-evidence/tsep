"""TS24 documentary boundaries, exact originals and independent offline replay."""
import copy
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import tsep
from adapters import captures,replay
from conformance import xdefault_role as native
from conformance.evaluate import evaluate
from reports import html

ROOT=Path(__file__).resolve().parents[1]

def cases():
    path=ROOT/'tests/fixtures/xdefault-role-cases-v2.json'
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=path.with_suffix('.sha256').read_text().strip():
        raise ValueError('Changed authored x-default counter-cases')
    return json.loads(raw)['cases']

def data(name='complete-default-variant'):
    return copy.deepcopy(next(c['input'] for c in cases() if c['id']==name))

def build(root,value,access='synthetic'):
    raw=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
    (root/'input.json').write_bytes(raw)
    captures.build(root/'input.json',root/'bundle',assessor='Authored synthetic exercise',
                   label='Synthetic x-default role',selection_method='Prior authored bounded group/context',access=access)
    return raw

class XDefaultRole(unittest.TestCase):
    def test_prefrozen_native_cases_and_retained_uncertainty(self):
        for c in cases():
            with self.subTest(case=c['id']),patch.object(socket,'socket',side_effect=AssertionError('No collection')):
                before=copy.deepcopy(c['input'])
                if c['expected']=='technical-refusal':
                    with self.assertRaises(tsep.Invalid):evaluate(c['input'])
                else:
                    result=evaluate(c['input'])[0]
                    self.assertEqual(result['outcome'],{'C':'pass','NC':'fail','NT':'inconclusive'}[c['expected']])
                    note=json.loads(result['reason'][len(native.PREFIX):])['measurement']
                    requirement=c.get('required_diagnostic',{})
                    if 'first_primary_complete' in requirement:
                        self.assertEqual(note['pages'][0]['primary_complete'],requirement['first_primary_complete'])
                    if requirement.get('soft404_limit'):self.assertIn('soft404',json.dumps(note['semantic_limit']))
                self.assertEqual(c['input'],before)
        self.assertEqual(len(cases()),79)

    def test_corrupt_intake_refuses_before_publishing_preserves_input(self):
        for c in cases():
            if c['expected']!='technical-refusal':continue
            with self.subTest(case=c['id']),tempfile.TemporaryDirectory()as folder:
                root=Path(folder)
                with self.assertRaises(tsep.Invalid):build(root,c['input'])
                self.assertFalse((root/'bundle').exists())
                self.assertEqual(tsep.read_json(root/'input.json'),c['input'])

    def test_real_bundles_bilingual_report_and_exact_offline_replay(self):
        for name,status in [('complete-default-variant','C'),('destination-status-404','NC'),
                            ('contested-defect-not-latest-wins','NT'),('missing-context-reason','NT')]:
            with self.subTest(case=name),tempfile.TemporaryDirectory()as folder,patch.object(socket,'socket',side_effect=AssertionError('No acquisition')):
                root=Path(folder);d=data(name);raw=build(root,d)
                report=tsep.read_json(root/'bundle/report.json')
                self.assertEqual(report['results'][0]['status'],status)
                self.assertTrue(tsep.decision(report)['synthetic_evidence'])
                self.assertIn('xdefault_interpretation',tsep.decision(report))
                self.assertEqual((root/'bundle/input.json').read_bytes(),raw)
                repeated=replay.replay(root/'bundle',root/'replay')
                self.assertTrue(repeated['same_atomic_results']);self.assertTrue(repeated['same_gate'])
                for lang in ('fr','en'):
                    rendered=html.render(root/'bundle/report.json',language=lang)
                    self.assertIn(html.TEXT[lang]['xdefault_title'],rendered)
                    self.assertIn(html.TEXT[lang]['xdefault_note'],rendered)
                    if name=='contested-defect-not-latest-wins':
                        self.assertIn(html.TEXT[lang]['xdefault_contested'],rendered)
                        self.assertIn('defect',rendered);self.assertIn('consistent',rendered)

    def test_native_originals_and_actual_supplied_reviews_retained(self):
        d=data();t=d['targets'][0];t['http']=copy.deepcopy(t['hreflang_documents'][0]['http'])
        t['hreflang']={'legacy':'Uninterpreted supplied older annotation'}
        result=captures.pieces(t)
        self.assertEqual(result['http']['hreflang_documents'],t['hreflang_documents'])
        self.assertEqual(result['http']['other_supplied_evidence']['http'],t['http'])
        self.assertIn('xdefault_reviews',json.dumps(result['intent']))
        self.assertIn('native_hreflang_sources',json.dumps(result['hreflang']))

    def test_provenance_runtime_and_existing_destination(self):
        for flag,access in [(True,'public'),(False,'synthetic'),('yes','synthetic')]:
            for absent_policy in (False,True):
                with self.subTest(flag=flag,absent_policy=absent_policy),tempfile.TemporaryDirectory()as folder:
                    d=data();d['targets'][0]['xdefault_synthetic']=flag
                    if absent_policy:d['targets'][0]['intent'].pop('xdefault')
                    root=Path(folder)
                    with self.assertRaises(tsep.Invalid):build(root,d,access)
                    self.assertFalse((root/'bundle').exists())
        with patch.dict(os.environ,{},clear=True):self.assertEqual(evaluate(data())[0]['outcome'],'inconclusive')
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder);(root/'bundle').mkdir();(root/'bundle/original').write_bytes(b'keep')
            with self.assertRaises(tsep.Invalid):build(root,data())
            self.assertEqual((root/'bundle/original').read_bytes(),b'keep')

    def test_ts23_and_ts24_have_separate_outcomes_in_one_dossier(self):
        d=data('unrelated-TS23-missing-en');d['rules']=['TS23-A01','TS24-A01']
        result={r['rule_id']:r['outcome']for r in evaluate(d)}
        self.assertEqual(result,{'TS23-A01':'fail','TS24-A01':'pass'})
        d=data('missing-destination-hash');d['rules']=['TS23-A01','TS24-A01']
        self.assertEqual([r['outcome']for r in evaluate(d)],['inconclusive','inconclusive'])

    def test_distinct_dossiers_do_not_share_supplied_judgments(self):
        d=data();other=data('review-defect')['targets'][0]
        # The scope target is not part of the documentary review material.
        other['url']='https://example.test/second-scope';d['targets'].append(other)
        self.assertEqual([r['outcome']for r in evaluate(d)],['pass','fail'])

    def test_large_diagnostics_never_truncate_a_positive_result(self):
        with patch.object(native,'qualify',return_value={'outcome':'C','diagnostic':'x'*(4*1024*1024)}):
            self.assertEqual(native.assess({},'TS24-A01')[0],'inconclusive')

    def test_renderer_preserves_contested_reviews_escapes_without_rejudging(self):
        review={'supplied':[{'disposition':'defect','rationale':'<script>bad</script>'},{'disposition':'consistent'}]}
        note={'measurement':{'review':review,'pages':[{'url':'<img src=x onerror=bad>','primary':'html'}]}}
        for lang in ('fr','en'):
            with patch.object(native,'qualify',side_effect=AssertionError('No rejudgment')):
                text=html.xdefault_values({'reason':native.PREFIX+json.dumps(note)},html.TEXT[lang])
            self.assertNotIn('<img ',text);self.assertNotIn('<script>',text)
            self.assertIn('&lt;img ',text);self.assertIn('&lt;script&gt;',text)
            self.assertIn(html.TEXT[lang]['xdefault_contested'],text)
            self.assertIn('defect',text);self.assertIn('consistent',text)

    def test_public_raw_cli_is_not_report_intake(self):
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder);value=data('synthetic-provenance-mismatch')
            source=root/'input.json';source.write_text(json.dumps(value)+'\n');before=source.read_bytes()
            raw=subprocess.run([sys.executable,'-B','-m','conformance.evaluate'],cwd=ROOT,
                               input=before,capture_output=True)
            self.assertEqual(raw.returncode,0,raw.stderr)
            self.assertEqual(json.loads(raw.stdout)[0]['outcome'],'inconclusive')
            destination=root/'bundle'
            report=subprocess.run([sys.executable,'-B','-m','adapters.captures',str(source),
                '--output-dir',str(destination),'--assessor','Synthetic author','--label','Synthetic boundary',
                '--selection-method','Authored prior fixture','--access','synthetic','--controls','TS24','--json'],
                cwd=ROOT,capture_output=True)
            self.assertEqual(report.returncode,64)
            self.assertIn(b'Explicit provenance differs from evidence access: xdefault_synthetic',report.stderr)
            self.assertFalse(destination.exists())
            self.assertEqual(source.read_bytes(),before)

    def test_source_identity_and_authored_corpus(self):
        for name in ('conformance/xdefault_role.py','conformance/hreflang_native.py','conformance/hreflang_reciprocity.py','adapters/hreflang_intake.py'):
            self.assertIn(name,captures.source_files())
        from conformance.corpus import expand
        corpus=[c for c in expand(tsep.read_json(ROOT/'conformance/cases.json'))['cases']if c['id'].startswith('xdefault-role-v1-')]
        authored=[c for c in cases()if c['expected']!='technical-refusal']
        self.assertEqual(len(corpus),len(authored))
        for row,c in zip(corpus,authored):
            self.assertEqual(row['input'],c['input'])
            self.assertEqual(row['expected'][0]['outcome'],{'C':'pass','NC':'fail','NT':'inconclusive'}[c['expected']])

if __name__=='__main__':unittest.main()
