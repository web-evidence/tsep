"""TS41 authored expectations and adversarial process-evidence boundaries."""
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
from adapters import captures,replay
from conformance import release_invariants as release
from conformance.evaluate import evaluate
from conformance.run import compare
from reports import html

ROOT=Path(__file__).resolve().parents[1]
NAMES=('release-invariants-v1.json','release-invariants-boundaries-v1.json','release-invariants-uncertain-output-v1.json')


def cases():
    result=[]
    for name in NAMES:
        p=ROOT/'tests/fixtures'/name;raw=p.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=p.with_suffix('.sha256').read_text().strip():
            raise ValueError('Frozen release fixture changed')
        result+=json.loads(raw)['cases']
    return result


class AuthoredClock(datetime):
    """Synthetic case dates are not observations of the actual test clock."""
    @classmethod
    def now(cls,tz=None):return cls(2026,10,12,12,tzinfo=timezone.utc)


class ReleaseInvariants(unittest.TestCase):
    def data(self,name='complete-cycle'):
        return copy.deepcopy(next(c['input'] for c in cases() if c['id']=='release-invariants-'+name))

    def test_frozen_cases_preserved_and_match_without_network_or_processes(self):
        rows=cases();self.assertEqual(len(rows),53)
        self.assertEqual(tsep.read_json(ROOT/'conformance/cases.json')['cases'][1051:1104],rows)
        with patch.object(socket,'socket',side_effect=AssertionError('No network')),patch.object(subprocess,'Popen',side_effect=AssertionError('No process')):
            for c in rows:
                with self.subTest(case=c['id']):
                    _,different,_=compare(c['expected'],evaluate(c['input']))
                    self.assertEqual(different,[])

    def test_process_pass_retains_underlying_failure_or_unknown(self):
        for case,expected in [('defect-detected-blocked','fail'),('unknown-held','inconclusive')]:
            t=self.data(case)['targets'][0];notes=[]
            self.assertEqual(release.assess(t,'TS41-A03',diagnostics=notes)[0],'pass')
            run=next(r for r in notes[0]['executions'] if r.get('phase')=='pre')
            self.assertEqual(run['underlying_decision'],expected)
            self.assertIn(expected,{r['outcome'] for r in run['recalculated_results']})

    def test_unavailable_recalculation_cannot_accuse_old_success(self):
        t=self.data()['targets'][0]
        def unknown(data):
            return [{'rule_id':r,'target':x['url'],'outcome':'inconclusive','reason':'Unavailable optional runtime'} for r in data['rules'] for x in data['targets']]
        with patch('conformance.evaluate.evaluate',side_effect=unknown):
            for rule in ('TS41-A02','TS41-A03'):
                self.assertEqual(release.assess(t,rule)[0],'inconclusive')

    def test_malformed_objects_do_not_crash_or_fabricate_a_contradiction(self):
        for field in ('intent','context','release_runs','release_events','release_review','release_plan_review'):
            for value in (None,[],{},False,'bad'):
                t=self.data()['targets'][0];t[field]=value
                for rule in ('TS41-A01','TS41-A02','TS41-A03'):
                    with self.subTest(field=field,value=value,rule=rule):
                        self.assertIn(release.assess(t,rule)[0],('pass','inconclusive'))

    def test_command_strings_are_only_compared_never_executed(self):
        t=self.data()['targets'][0];command=t['intent']['release']['command']
        command['argv']=['not-an-executable','$(do-not-run)','<script>alert(1)</script>']
        for r in t['release_runs']:r['command']=copy.deepcopy(command)
        t['release_plan_review']['binding_sha256']=release.plan_binding(t)
        t['release_review']['binding_sha256']=release.review_binding(t)
        with patch.object(subprocess,'Popen',side_effect=AssertionError('No process')):
            self.assertEqual(release.assess(t,'TS41-A03')[0],'pass')

    def test_plan_and_journal_reviews_bind_exact_evidence(self):
        t=self.data()['targets'][0]
        t['intent']['release']['population'][0]['before_artifact']='f'*64
        self.assertEqual(release.assess(t,'TS41-A01')[0],'inconclusive')
        self.assertEqual(release.assess(t,'TS41-A02')[0],'inconclusive')
        t=self.data()['targets'][0];t['release_runs'][1]['exit_code']=1
        self.assertEqual(release.assess(t,'TS41-A02')[0],'inconclusive')
        self.assertEqual(release.assess(t,'TS41-A03')[0],'fail')

    def test_import_replay_report_keep_process_and_native_results_distinct(self):
        for case,status in [('defect-detected-blocked','C'),('unknown-green','NC'),('post-missing','NT')]:
            with self.subTest(case=case),tempfile.TemporaryDirectory() as d,patch.object(captures,'datetime',AuthoredClock):
                root=Path(d);p=root/'input.json';p.write_text(json.dumps(self.data(case)))
                with patch.object(socket,'socket',side_effect=AssertionError('No network')):
                    captures.build(p,root/'bundle',assessor='Synthetic importer',label='Authored TS41 exercise',selection_method='One authored case',access='synthetic',mode='semiAuto')
                    result=replay.replay(root/'bundle',root/'replay')
                self.assertTrue(result['replayed']);self.assertTrue(result['same_source_observations'])
                report=tsep.read_json(root/'bundle/report.json');self.assertEqual(report['results'][0]['status'],status)
                self.assertTrue({'configuration','ci-output','change-history','intent'} <= {a['kind'] for a in report['artifacts']})
                for lang in ('fr','en'):
                    text=html.render(root/'bundle/report.json',language=lang)
                    self.assertIn(html.TEXT[lang]['release_note'],text)
                    self.assertIn(html.TEXT[lang]['release_native'],text)
                    self.assertNotIn('<script',text)

    def test_partial_rule_cannot_make_whole_control_conform(self):
        data=self.data();data['rules']=['TS41-A01']
        with tempfile.TemporaryDirectory() as d,patch.object(captures,'datetime',AuthoredClock):
            root=Path(d);p=root/'input.json';p.write_text(json.dumps(data))
            captures.build(p,root/'bundle',assessor='Synthetic importer',label='Partial authored TS41',selection_method='Only one rule',access='synthetic',mode='semiAuto')
            self.assertEqual(tsep.read_json(root/'bundle/report.json')['results'][0]['status'],'NT')

    def test_top_and_nested_synthetic_reviews_cannot_be_relabelled_public(self):
        for field in ('release_plan_review','release_review','nested'):
            data=self.data();t=data['targets'][0]
            for review in ('release_plan_review','release_review'):
                t[review]['provenance']='human'
            if field=='nested':
                r=t['release_runs'][0];native=json.loads(r['input_json'])
                native['targets'][0]['critical_plan_review']={'provenance':'synthetic-exercise'}
                r['input_json']=json.dumps(native);r['input_sha256']=hashlib.sha256(r['input_json'].encode()).hexdigest()
            else:t[field]['provenance']='synthetic-exercise'
            with self.subTest(field=field),tempfile.TemporaryDirectory() as d,patch.object(captures,'datetime',AuthoredClock):
                p=Path(d)/'input.json';p.write_text(json.dumps(data))
                with self.assertRaisesRegex(tsep.Invalid,'provenance differs'):
                    captures.build(p,Path(d)/'out',assessor='Importer',label='Unqualified relabelling',selection_method='Authored test',access='public',mode='semiAuto')

    def test_renderer_escapes_saved_text_and_does_not_evaluate(self):
        note={'rows':[{'subject':'<script>','outcome':'fail','reason':'<img onerror=x>'}], 'executions':[]}
        atom={'reason':'Release process / dispositif de déploiement: '+json.dumps(note)}
        with patch('conformance.release_invariants.assess',side_effect=AssertionError('No reevaluation')):
            text=html.release_values(atom,html.TEXT['fr'])
        self.assertIn('&lt;script&gt;',text);self.assertNotIn('<img',text)


if __name__=='__main__':unittest.main()
