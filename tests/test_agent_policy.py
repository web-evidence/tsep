"""Frozen governance cases, authority boundaries and offline report/replay delivery."""
import copy
import hashlib
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch
from adapters import captures, replay
from conformance import agent_policy
from conformance.evaluate import evaluate
from reports import html
import tsep

ROOT = Path(__file__).resolve().parents[1]

def fixture():
    p = ROOT/'tests/fixtures/agent-policy-v1.json'
    raw = p.read_bytes()
    if hashlib.sha256(raw).hexdigest() != p.with_suffix('.sha256').read_text().strip():
        raise ValueError('Frozen agent fixture changed')
    return json.loads(raw)['cases']

class AgentPolicy(unittest.TestCase):
    def data(self, name='documented-search'):
        return copy.deepcopy(next(c['input'] for c in fixture() if c['id'] == 'agents-'+name))

    def test_frozen_cases_and_exact_corpus(self):
        cases = fixture()
        self.assertEqual(len(cases), 52)
        self.assertEqual(sum(len(c['expected']) for c in cases), 156)
        corpus = tsep.read_json(ROOT/'conformance/cases.json')['cases']
        for case in cases:
            with self.subTest(case=case['id']):
                self.assertIn(case, corpus)
                self.assertEqual([{k:r[k] for k in ('rule_id','target','outcome')}
                                  for r in evaluate(case['input'])], case['expected'])

    def test_previous_corpus_is_preserved_in_order(self):
        # Preserve the independent previous performance freeze in the extended corpus.
        old = tsep.read_json(ROOT/'tests/fixtures/performance-v2.json')['cases']
        corpus = tsep.read_json(ROOT/'conformance/cases.json')['cases']
        self.assertEqual(corpus[775:857], old)

    def test_same_token_alias_cannot_split_coupled_wishes(self):
        data = self.data('separate-ids-same-token-coupled')
        self.assertEqual([r['outcome'] for r in evaluate(data)], ['pass','pass','inconclusive'])
        t=data['targets'][0]
        t['intent']['agent_policy']['mechanisms'][1]['operator']='Different label'
        t['agent_decision']['binding_sha256']=agent_policy.owner_binding(t)
        self.assertEqual(agent_policy.assess(t,'TS42-A03')[0],'inconclusive')

    def test_arbitration_does_not_rewrite_initial_wishes(self):
        data = self.data('coupled-arbitrated-match');before=copy.deepcopy(data)
        notes=[];t=data['targets'][0]
        self.assertEqual(agent_policy.assess(t,'TS42-A03',diagnostics=notes)[0],'pass')
        self.assertEqual(data,before)
        row=notes[0]['rows'][0]
        self.assertEqual({d['choice'] for d in row['decisions']},{'allow','deny'})
        self.assertEqual(row['effective_choice'],'deny')
        self.assertEqual(row['arbitration']['choice'],'deny')

    def test_source_binding_cannot_be_reused_after_url_change(self):
        t=self.data()['targets'][0];t['agent_documents'][0]['source_url']='https://different.example/source'
        self.assertEqual(agent_policy.assess(t,'TS42-A01')[0],'inconclusive')

    def test_reviewer_cannot_take_owner_decision(self):
        t=self.data()['targets'][0];t['agent_decision']['author']=t['agent_reviews'][0]['reviewer']
        self.assertEqual(agent_policy.assess(t,'TS42-A02')[0],'inconclusive')
        self.assertEqual(agent_policy.assess(t,'TS42-A03')[0],'inconclusive')

    def test_invalid_source_port_cannot_be_qualified_even_after_rebinding(self):
        for port in ('invalid','0','99999'):
            t=self.data()['targets'][0]
            t['agent_documents'][0]['source_url']='https://provider.example:'+port+'/bots'
            t['agent_reviews'][0]['binding_sha256']=agent_policy.mapping_binding(t['intent']['agent_policy']['mechanisms'][0],t['agent_documents'])
            self.assertEqual(agent_policy.assess(t,'TS42-A01')[0],'inconclusive')

    def test_explicit_target_port_is_preserved_in_policy_origin(self):
        t=self.data()['targets'][0];t['url']='https://example.com:8890/page'
        hop=t['robots']['http'][0];hop['url']='https://example.com:8890/robots.txt'
        hop['request']=hop['request'].replace('Host: example.com','Host: example.com:8890')
        t['agent_decision']['binding_sha256']=agent_policy.owner_binding(t)
        self.assertEqual(agent_policy.assess(t,'TS42-A03')[0],'pass')

    def test_policy_change_does_not_change_source_or_owner_judgment(self):
        data=self.data();data['targets'][0]['robots']['http'][0]['response']=data['targets'][0]['robots']['http'][0]['response'].replace('Allow: /','Disallow: /')
        self.assertEqual([r['outcome'] for r in evaluate(data)],['pass','pass','fail'])

    def test_unqualified_lines_are_not_silently_discarded(self):
        for field in ('Sitemap: https://example.com/map.xml','Crawl-delay: 2','Host: example.com','Content-Signal: ai-train=no'):
            t=self.data()['targets'][0];t['robots']['http'][0]['response']+=field+'\n'
            self.assertEqual(agent_policy.assess(t,'TS42-A03')[0],'inconclusive')

    def test_malformed_governance_never_crashes(self):
        for field in ('agent_documents','agent_reviews','agent_decision','robots','intent'):
            for value in (None, [], False, 'invalid', {}):
                t=self.data()['targets'][0];t[field]=value
                for rule in ('TS42-A01','TS42-A02','TS42-A03'):
                    with self.subTest(field=field,value=value,rule=rule):
                        self.assertIn(agent_policy.assess(t,rule)[0],('pass','inconclusive'))

    def test_failure_keeps_unrelated_unknown(self):
        t=self.data('failure-survives-unrelated-source-gap')['targets'][0];notes=[]
        self.assertEqual(agent_policy.assess(t,'TS42-A03',diagnostics=notes)[0],'fail')
        self.assertEqual([r['outcome'] for r in notes[0]['rows']],['fail','inconclusive'])

    def test_frozen_delivery_replays_without_network(self):
        for name,status in (('coupled-arbitrated-match','C'),('coupled-arbitrated-conflict','NC'),('coupled-no-arbitration','NT'),('owner-decision-missing','NT')):
            with self.subTest(case=name), tempfile.TemporaryDirectory() as directory:
                root=Path(directory);data=self.data(name);src=root/'input.json';src.write_text(json.dumps(data))
                with patch.object(socket,'socket',side_effect=AssertionError('Network forbidden')):
                    captures.build(src,root/'bundle',assessor='Synthetic importer',label='Synthetic agent policy',selection_method='One authored case',access='synthetic')
                    rerun=replay.replay(root/'bundle',root/'replay')
                    self.assertTrue(rerun['replayed']);self.assertTrue(rerun['same_source_observations'])
                report=tsep.read_json(root/'bundle/report.json')
                self.assertEqual(report['results'][0]['status'],status)
                self.assertEqual(tsep.read_json(root/'bundle/input.json'),data)
                kinds={a['kind'] for a in report['artifacts']}
                self.assertTrue({'intent','configuration','operator-docs'}<=kinds)
                for lang in ('fr','en'):
                    rendered=html.render(root/'bundle/report.json',language=lang)
                    self.assertIn(html.TEXT[lang]['agent_note'],rendered)
                    self.assertIn(html.TEXT[lang]['agent_values'],rendered)
                    self.assertNotIn('<script',rendered)

    def test_partial_rule_cannot_establish_whole_control(self):
        data=self.data();data['rules']=['TS42-A01']
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);src=root/'input.json';src.write_text(json.dumps(data))
            captures.build(src,root/'bundle',assessor='Synthetic importer',label='Partial',selection_method='One authored case',access='synthetic')
            self.assertEqual(tsep.read_json(root/'bundle/report.json')['results'][0]['status'],'NT')

    def test_synthetic_decision_and_review_cannot_be_imported_as_real(self):
        for field in ('agent_reviews','agent_decision'):
            data=self.data();t=data['targets'][0]
            other='agent_decision' if field=='agent_reviews' else 'agent_reviews'
            if other=='agent_reviews':t[other]=[]
            else:t.pop(other)
            with tempfile.TemporaryDirectory() as directory:
                root=Path(directory);src=root/'input.json';src.write_text(json.dumps(data))
                with self.assertRaisesRegex(tsep.Invalid,'provenance'):
                    captures.build(src,root/'bundle',assessor='Importer',label='Provenance',selection_method='One case',access='public')
                self.assertFalse((root/'bundle').exists())

    def test_html_escapes_untrusted_diagnostic_text(self):
        reason='Agent usage governance / gouvernance des usages agents: '+json.dumps({'rows':[{'subject':'<script>','decisions':[{'reason':'<img src=x onerror=x>'}],'reason':'<bad>','outcome':'pass'}]})
        text=html.agent_values({'reason':reason},html.TEXT['fr'])
        self.assertIn('&lt;script&gt;',text);self.assertNotIn('<script>',text);self.assertNotIn('<img src=x',text)

if __name__=='__main__':unittest.main()
