"""TS08 native inspection, supplied decisions, adverse boundaries and exact replay."""
from datetime import datetime, timezone
import copy
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import tsep
from adapters import captures, replay, inspection_intake
from conformance import inspection
from conformance.evaluate import evaluate
from reports import html

ROOT=Path(__file__).resolve().parents[1]


def fixture(version=2):
    p=ROOT/('tests/fixtures/inspection-evidence-v%d.json'%version)
    raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=p.with_suffix('.sha256').read_text().strip():raise ValueError('Changed frozen TS08 cases')
    return json.loads(raw)['cases']


class AuthoredClock(datetime):
    @classmethod
    def now(cls,tz=None):return cls(2026,10,10,12,tzinfo=timezone.utc)


class InspectionEvidence(unittest.TestCase):
    def data(self,name='qualified-positive'):
        return copy.deepcopy(next(c['input'] for c in fixture() if c['id']=='inspection-v1-'+name))

    def test_frozen_cases_without_network_or_processes(self):
        rows=fixture();self.assertEqual(len(rows),47)
        self.assertEqual(tsep.read_json(ROOT/'conformance/cases.json')['cases'][1257:1304],rows)
        with patch.object(socket,'socket',side_effect=AssertionError('No network')),patch.object(subprocess,'Popen',side_effect=AssertionError('No process')):
            for c in rows:
                with self.subTest(case=c['id']):
                    self.assertEqual([(r['rule_id'],r['target'],r['outcome']) for r in evaluate(c['input'])],
                                     [(r['rule_id'],r['target'],r['outcome']) for r in c['expected']])

    def test_initial_fixture_error_retained(self):
        old=fixture(1);new=fixture(2)
        self.assertEqual([c['expected'] for c in old],[c['expected'] for c in new])
        differences=[]
        for c in old:
            for want,got in zip(c['expected'],evaluate(c['input'])):
                if want['outcome']!=got['outcome']:differences.append((c['id'],got['rule_id'],got['outcome']))
        self.assertEqual(differences,[('inspection-v1-unknown-url-no-fields','TS08-A03','fail')])

    def test_independent_contradiction_survives_missing_age_evidence(self):
        rows=evaluate(self.data('independent-contradiction-survives-old-crawl'))
        self.assertEqual([r['outcome'] for r in rows],['pass','inconclusive','fail'])

    def test_malformed_inputs_never_crash_or_become_exempt(self):
        for key in ('intent','inspection_plan_review','inspection_records','inspection_reviews'):
            for value in (None,True,[],'bad',{}):
                t=self.data()['targets'][0];t[key]=value
                for rule in inspection_intake.RULES:
                    with self.subTest(key=key,value=value,rule=rule):
                        self.assertIn(inspection.assess(t,rule)[0],('pass','inconclusive'))

    def test_bundles_C_NC_NT_replay_and_bilingual_reports(self):
        for name,status in [('qualified-positive','C'),('negative-explained-without-cause','C'),('claimed-wrong-verdict','NC'),('missing-review','NT')]:
            with self.subTest(name=name),tempfile.TemporaryDirectory() as d:
                root=Path(d);p=root/'input.json';p.write_text(json.dumps(self.data(name)))
                with patch.object(socket,'socket',side_effect=AssertionError('No network')),patch.object(subprocess,'Popen',side_effect=AssertionError('No process')):
                    captures.build(p,root/'bundle',assessor='Fictional author',label='Synthetic TS08',selection_method='Frozen fictional singleton',access='synthetic',mode='semiAuto')
                    result=replay.replay(root/'bundle',root/'replay')
                self.assertTrue(result['replayed']);self.assertTrue(result['same_source_observations'])
                report=tsep.read_json(root/'bundle/report.json');self.assertEqual(report['results'][0]['status'],status)
                self.assertTrue({'search-console','intent'}<={a['kind'] for a in report['artifacts']})
                for language in ('fr','en'):
                    rendered=html.render(root/'bundle/report.json',language=language)
                    self.assertIn(html.TEXT[language]['inspection_note'],rendered)
                    self.assertIn('pageFetchState',rendered)

    def test_partial_rule_cannot_close_control_and_synthetic_cannot_be_public(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);data=self.data();data['rules']=['TS08-A02'];p=root/'input.json';p.write_text(json.dumps(data))
            captures.build(p,root/'partial',assessor='Fictional author',label='Partial',selection_method='One rule',access='synthetic',mode='semiAuto')
            self.assertEqual(tsep.read_json(root/'partial/report.json')['results'][0]['status'],'NT')
            with self.assertRaises(tsep.Invalid):captures.build(p,root/'invalid',assessor='A',label='Bad access',selection_method='Authored',access='public',mode='semiAuto')

    def test_intake_blank_reviews_and_tamper_refusal(self):
        with tempfile.TemporaryDirectory() as d, patch.object(inspection_intake,'datetime',AuthoredClock), patch.object(captures,'datetime',AuthoredClock):
            root=Path(d);target=self.data()['targets'][0];record=target.pop('inspection_records')[0];authored_review=target.pop('inspection_reviews')[0]
            p=root/'plan.json';p.write_text(json.dumps(target));obs=root/'observation';obs.mkdir()
            for key in ('request','response'):(obs/(key+'.json')).write_text(record[key]['raw_text'])
            meta={'kind':'tsep-url-inspection-observation','format_version':'1','provenance':'synthetic-exercise','description':'Authored native API files','retrieved_at':record['retrieved_at'],'http_status':record['http_status'],'change':None,
                  'request_sha256':record['request']['sha256'],'response_sha256':record['response']['sha256']}
            (obs/'manifest.json').write_text(json.dumps(meta))
            inspection_intake.prepare(p,[obs],root/'prepared')
            request=tsep.read_json(root/'prepared/review-request.json')
            self.assertFalse(request['reviews'][0]['complete']);self.assertIsNone(request['reviews'][0]['reviewer'])
            inspection_intake.build(root/'prepared',root/'prepared/review-request.json',root/'blank-bundle','Fictional author')
            self.assertEqual(tsep.read_json(root/'blank-bundle/report.json')['results'][0]['status'],'NT')
            authored_review['binding_sha256']=request['reviews'][0]['binding_sha256']
            request['reviews']=[authored_review];supplied=root/'supplied-reviews.json';supplied.write_text(json.dumps(request))
            inspection_intake.build(root/'prepared',supplied,root/'complete-bundle','Fictional author')
            self.assertEqual(tsep.read_json(root/'complete-bundle/report.json')['results'][0]['status'],'C')
            self.assertTrue(replay.replay(root/'complete-bundle',root/'complete-replay')['replayed'])
            (root/'prepared/originals/1/response.json').write_text('{}')
            with self.assertRaisesRegex(tsep.Invalid,'Changed intake file'):
                inspection_intake.build(root/'prepared',root/'prepared/review-request.json',root/'tampered','Fictional author')

    def test_renderer_escapes_and_does_not_reassess(self):
        atom={'reason':inspection.PREFIX+json.dumps({'rows':[{'subject':'<script>','outcome':'fail','reason':'<img onerror=x>'}]})}
        with patch.object(inspection,'assess',side_effect=AssertionError('No reassessment')):
            rendered=html.inspection_values(atom,html.TEXT['fr'])
        self.assertIn('&lt;script&gt;',rendered);self.assertNotIn('<img',rendered)

    def test_unplanned_review_is_not_silently_ignored(self):
        t=self.data()['targets'][0]
        t['inspection_reviews'].append(dict(t['inspection_reviews'][0],url='https://example.com/unplanned'))
        self.assertEqual(inspection.assess(t,'TS08-A03')[0],'inconclusive')

    def test_member_failure_survives_another_missing_member(self):
        t=self.data('claimed-wrong-verdict')['targets'][0]
        t['intent']['inspection']['members'].append(dict(t['intent']['inspection']['members'][0],url='https://example.com/missing'))
        from conformance.agent_policy import digest
        t['inspection_reviews'][0]['binding_sha256']=digest({'url':t['url'],'intent':t['intent'],'record':t['inspection_records'][0]})
        self.assertEqual(inspection.assess(t,'TS08-A03')[0],'fail')

    def test_cli_evaluation_and_review_deadline_failures(self):
        import sys
        result=subprocess.run([sys.executable,str(ROOT/'conformance/evaluate.py')],input=json.dumps(self.data()),
                              text=True,capture_output=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)
        # The CLI response has the same typed outcomes as the direct reader.
        self.assertEqual(json.loads(result.stdout),evaluate(self.data()))
        for decision in ({'kind':'correct','reason':'Action pending','owner':'Fictional owner'},
                         {'kind':'revise-objective','reason':'Change pending','owner':'Fictional owner'},
                         {'kind':'monitor','reason':'Monitor','owner':'Fictional owner','criterion':'Inspect again','due_at':'2026-10-09T00:00:00Z'}):
            t=self.data()['targets'][0];t['inspection_reviews'][0]['decision']=decision
            self.assertEqual(inspection.assess(t,'TS08-A03')[0],'inconclusive')


if __name__=='__main__':unittest.main()
