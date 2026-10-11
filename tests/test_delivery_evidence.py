"""TS39 contradictory delivery policies, attribution and complete offline bundles."""
import copy
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import tsep
from conformance import delivery
from conformance.evaluate import evaluate
from adapters import captures,replay
from reports import html

ROOT=Path(__file__).resolve().parents[1]
ACTIVE=('delivery-evidence-v2.json','delivery-evidence-boundaries-v1.json')


def fixture(name):
    p=ROOT/'tests/fixtures'/name;raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=p.with_suffix('.sha256').read_text().strip():raise ValueError('Frozen TS39 fixture changed')
    return json.loads(raw)['cases']


class AuthoredClock(datetime):
    @classmethod
    def now(cls,tz=None):return cls(2026,10,12,12,tzinfo=timezone.utc)


class DeliveryEvidence(unittest.TestCase):
    def data(self,name='qualified-negotiation'):
        all_cases=sum((fixture(n) for n in ACTIVE),[])
        return copy.deepcopy(next(c['input'] for c in all_cases if c['id'].endswith('-'+name)))

    def test_all_frozen_cases_and_history_preserved_without_network_or_processes(self):
        rows=sum((fixture(n) for n in ACTIVE),[]);self.assertEqual(len(rows),77)
        corpus=tsep.read_json(ROOT/'conformance/cases.json')['cases']
        self.assertEqual(corpus[1104:1181],rows)
        with patch.object(socket,'socket',side_effect=AssertionError('No network')),patch.object(subprocess,'Popen',side_effect=AssertionError('No process')):
            for c in rows:
                with self.subTest(case=c['id']):
                    got=evaluate(c['input'])
                    self.assertEqual([(r['rule_id'],r['target'],r['outcome']) for r in got],[(r['rule_id'],r['target'],r['outcome']) for r in c['expected']])

    def test_initial_fixture_error_remains_visible_not_reader_relaxation(self):
        old=fixture('delivery-evidence-v1.json');new=fixture('delivery-evidence-v2.json');self.assertEqual(len(old),60)
        self.assertEqual([c['expected'] for c in old],[c['expected'] for c in new])
        different=[]
        for c in old:
            for want,got in zip(c['expected'],evaluate(c['input'])):
                if want['outcome']!=got['outcome']:different.append((got['rule_id'],want['outcome'],got['outcome']))
        self.assertEqual(different,[('TS39-A02','pass','inconclusive')]*34)

    def test_header_failure_survives_partial_body_without_closing_native_tests(self):
        notes=[];t=self.data('truncated-noindex')['targets'][0]
        self.assertEqual(delivery.assess(t,'TS39-A02',diagnostics=notes)[0],'fail')
        self.assertTrue(any(r['subject']=='b:http-directives' and r['outcome']=='fail' for r in notes[0]['rows']))
        self.assertTrue(any(r['subject']=='b:TS10-A01' and r['outcome']=='inconclusive' for r in notes[0]['rows']))

    def test_header_preview_cannot_ignore_valid_html_meta(self):
        t=self.data('meta-preview-not-header-failure')['targets'][0]
        self.assertEqual(delivery.assess(t,'TS39-A02')[0],'pass')

    def test_missing_cache_attribution_prevents_cause_claim(self):
        t=self.data('cache-unknown-link-mismatch-not-attributed')['targets'][0];notes=[]
        self.assertEqual(delivery.assess(t,'TS39-A03',diagnostics=notes)[0],'inconclusive')
        self.assertFalse(any(r['outcome']=='fail' for r in notes[0]['rows']))

    def test_raw_fingerprint_mutation_invalidates_reviews(self):
        t=self.data()['targets'][0]
        t['delivery_observations'][1]['http'][0]['response']+='x'
        self.assertEqual(delivery.assess(t,'TS39-A02')[0],'inconclusive')
        self.assertEqual(delivery.assess(t,'TS39-A03')[0],'inconclusive')

    def test_malformed_evidence_retained_as_unknown_without_crashing(self):
        for field in ('intent','delivery_observations','delivery_configuration','delivery_sources','delivery_context_reviews','delivery_semantic_reviews','delivery_cache_records'):
            for value in (None,True,[],'bad'):
                t=self.data()['targets'][0];t[field]=value
                for rule in ('TS39-A01','TS39-A02','TS39-A03'):
                    with self.subTest(field=field,value=value,rule=rule):
                        self.assertIn(delivery.assess(t,rule)[0],('pass','inconclusive'))

    def test_import_replay_and_bilingual_reports_retain_C_NC_NT_and_native_results(self):
        for name,status in [('qualified-cache','C'),('canonical-contradiction','NC'),('cache-vary-mismatch','NC'),('missing-cell','NT')]:
            with self.subTest(case=name),tempfile.TemporaryDirectory() as d,patch.object(captures,'datetime',AuthoredClock):
                root=Path(d);p=root/'input.json';p.write_text(json.dumps(self.data(name)))
                with patch.object(socket,'socket',side_effect=AssertionError('No network')),patch.object(subprocess,'Popen',side_effect=AssertionError('No process')):
                    captures.build(p,root/'bundle',assessor='Fictional assessor',label='Authored TS39 exercise',selection_method='Authored fixture, not Edikka',access='synthetic',mode='semiAuto')
                    result=replay.replay(root/'bundle',root/'replay')
                report=tsep.read_json(root/'bundle/report.json');self.assertEqual(report['results'][0]['status'],status)
                self.assertTrue(result['replayed']);self.assertTrue(result['same_source_observations'])
                self.assertTrue({'configuration','http','content','logs','intent'}<={a['kind'] for a in report['artifacts']})
                for language in ('fr','en'):
                    rendered=html.render(root/'bundle/report.json',language=language)
                    self.assertIn(html.TEXT[language]['delivery_note'],rendered)
                    self.assertIn(html.TEXT[language]['delivery_native'],rendered)

    def test_partial_rules_do_not_close_TS39(self):
        data=self.data();data['rules']=['TS39-A01']
        with tempfile.TemporaryDirectory() as d,patch.object(captures,'datetime',AuthoredClock):
            root=Path(d);p=root/'in.json';p.write_text(json.dumps(data))
            captures.build(p,root/'bundle',assessor='Fictional author',label='Partial TS39',selection_method='One rule only',access='synthetic',mode='semiAuto')
            self.assertEqual(tsep.read_json(root/'bundle/report.json')['results'][0]['status'],'NT')

    def test_synthetic_top_nested_and_cache_reviews_cannot_be_relabelled_public(self):
        for field in ('marker','semantic','context','cache','native'):
            data=self.data('qualified-cache');t=data['targets'][0]
            def human(x):
                if isinstance(x,dict):
                    if x.get('provenance')=='synthetic-exercise':x['provenance']='human'
                    for v in x.values():human(v)
                elif isinstance(x,list):
                    for v in x:human(v)
            human(t);t['delivery_synthetic']=False
            if field=='marker':t['delivery_synthetic']=True
            elif field=='semantic':t['delivery_semantic_reviews'][0]['provenance']='synthetic-exercise'
            elif field=='context':t['delivery_context_reviews'][0]['provenance']='synthetic-exercise'
            elif field=='cache':t['delivery_cache_records'][0]['review']['provenance']='synthetic-exercise'
            else:t['delivery_observations'][0]['native']['exemption_review']['provenance']='synthetic-exercise'
            with self.subTest(field=field),tempfile.TemporaryDirectory() as d,patch.object(captures,'datetime',AuthoredClock):
                root=Path(d);p=root/'in.json';p.write_text(json.dumps(data))
                with self.assertRaisesRegex(tsep.Invalid,'provenance differs'):
                    captures.build(p,root/'out',assessor='Author',label='Invalid relabelling',selection_method='Authored fixture',access='public',mode='semiAuto')

    def test_renderer_escapes_and_never_reassesses(self):
        atom={'reason':'Delivery evidence / preuves de diffusion: '+json.dumps({'rows':[{'subject':'<script>','reason':'<img onerror=x>','outcome':'fail'}],'native_results':[{'reason':'<script>'}]})}
        with patch.object(delivery,'assess',side_effect=AssertionError('No reassessment')):
            rendered=html.delivery_values(atom,html.TEXT['fr'])
        self.assertIn('&lt;script&gt;',rendered);self.assertNotIn('<img',rendered)


if __name__=='__main__':unittest.main()
