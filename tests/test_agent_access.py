"""Prefrozen TS43 expectations, independent failures and retained attribution limits."""
import copy
import hashlib
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from adapters import captures, replay
from conformance import agent_access as access
from conformance.evaluate import evaluate
from reports import html
import tsep

ROOT = Path(__file__).resolve().parents[1]
RULES = ['TS43-A01', 'TS43-A02', 'TS43-A03']


def fixture():
    path = ROOT/'tests/fixtures/agent-access-v1.json'
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != path.with_suffix('.sha256').read_text().strip():
        raise ValueError('Frozen agent access fixture changed')
    return json.loads(raw)['cases']


class AgentAccess(unittest.TestCase):
    def data(self, name='ua-only-allows-test'):
        return copy.deepcopy(next(c['input'] for c in fixture() if c['id'] == 'agent-access-'+name))

    def test_all_frozen_expectations_and_exact_corpus(self):
        cases = fixture()
        self.assertEqual(len(cases), 71)
        self.assertEqual(sum(len(c['expected']) for c in cases), 213)
        corpus = tsep.read_json(ROOT/'conformance/cases.json')['cases']
        self.assertEqual(corpus[909:], cases)
        for case in cases:
            with self.subTest(case=case['id']):
                self.assertEqual([{k:r[k] for k in ('rule_id','target','outcome')}
                                  for r in evaluate(case['input'])], case['expected'])

    def test_previous_agent_governance_corpus_preserved_in_order(self):
        old = tsep.read_json(ROOT/'tests/fixtures/agent-policy-v1.json')['cases']
        corpus = tsep.read_json(ROOT/'conformance/cases.json')['cases']
        self.assertEqual(corpus[857:909], old)

    def test_expected_denial_and_allowed_impersonation_do_not_establish_operator_access(self):
        for name in ('ua-only-allows-test', 'identity-gated-refuses-test'):
            t = self.data(name)['targets'][0]; before = copy.deepcopy(t); notes = []
            self.assertEqual(access.assess(t, RULES[0], diagnostics=notes)[0], 'pass')
            self.assertEqual(notes[0]['rows'][1]['operator_access'], 'not-established')
            self.assertEqual(notes[0]['rows'][1]['scope'], 'test-client-only')
            self.assertEqual(t, before)

    def test_cached_old_id_is_unknown_before_client_mismatch_is_compared(self):
        t = self.data('cached-old-id-other-client')['targets'][0]; notes = []
        self.assertEqual(access.assess(t, RULES[1], diagnostics=notes)[0], 'inconclusive')
        self.assertIn('outside request clock window', notes[0]['rows'][0]['reason'])
        self.assertNotIn('differences', notes[0]['rows'][0])

    def test_attributed_log_failure_preserves_other_missing_hop(self):
        t = self.data('log-failure-keeps-missing-hop')['targets'][0]; notes = []
        self.assertEqual(access.assess(t, RULES[1], diagnostics=notes)[0], 'fail')
        self.assertEqual({r['outcome'] for r in notes[0]['rows']}, {'fail','inconclusive'})

    def test_invalid_origin_and_undeclared_redirect_never_pass(self):
        for origin in ('https://example.com', 'https://example.com:bad/', 'https://example.com:0/',
                       'https://user:password@example.com/', 'https://different.example/'):
            t = self.data()['targets'][0]; t['intent']['agent_access']['origins'] = [origin]
            for rule in RULES:
                with self.subTest(origin=origin, rule=rule):
                    self.assertEqual(access.assess(t, rule)[0], 'inconclusive')

    def test_url_or_execution_change_invalidates_supplied_bindings(self):
        t = self.data()['targets'][0]; t['execution']['initiator'] = 'Another initiator'
        self.assertEqual(access.assess(t, RULES[2])[0], 'inconclusive')
        t = self.data()['targets'][0]; t['client_documents'][0]['source_url'] = 'https://other.example/bots'
        self.assertEqual(access.assess(t, RULES[0])[0], 'inconclusive')

    def test_json_duplicate_keys_and_nonfinite_values_are_unknown(self):
        for raw in ('{"request_id":"one","request_id":"two"}\n', '{"status":NaN}\n', '\n'):
            t = self.data()['targets'][0]; t['logs']['raw_jsonl'] = raw
            t['logs']['sha256'] = hashlib.sha256(raw.encode()).hexdigest()
            t['log_review']['binding_sha256'] = access.correlation_binding(t)
            self.assertEqual(access.assess(t, RULES[1])[0], 'inconclusive')

    def test_bad_structures_never_invent_a_pass_or_crash(self):
        for field in ('intent','http','logs','execution','client_documents','client_review','log_review','attribution'):
            for value in (None, [], {}, False, 'invalid'):
                t = self.data()['targets'][0]; t[field] = value
                for rule in RULES:
                    with self.subTest(field=field, value=value, rule=rule):
                        self.assertIn(access.assess(t, rule)[0], ('pass','inconclusive'))

    def test_supplied_command_is_never_executed(self):
        t = self.data()['targets'][0]
        t['execution']['command'] = ['$(touch SHOULD_NOT_EXIST)', '`exit 1`']
        t['attribution']['binding_sha256'] = access.attribution_binding(t)
        self.assertEqual(access.assess(t, RULES[2])[0], 'pass')

    def test_three_control_outcomes_replay_offline_and_keep_raw_evidence(self):
        for name,status in (('identity-gated-refuses-test','C'),('200-challenge-body','NC'),
                            ('cached-old-id-other-client','NT')):
            with self.subTest(case=name), tempfile.TemporaryDirectory() as directory:
                root=Path(directory); data=self.data(name); src=root/'input.json'
                src.write_text(json.dumps(data))
                with patch.object(socket,'socket',side_effect=AssertionError('Network forbidden')):
                    captures.build(src,root/'bundle',assessor='Synthetic importer',label='Synthetic agent access',
                                   selection_method='One authored case',access='synthetic')
                    rerun=replay.replay(root/'bundle',root/'replay')
                    self.assertTrue(rerun['replayed']); self.assertTrue(rerun['same_source_observations'])
                report=tsep.read_json(root/'bundle/report.json')
                self.assertEqual(report['results'][0]['status'],status)
                self.assertEqual(tsep.read_json(root/'bundle/input.json'),data)
                self.assertTrue({'intent','logs','http','operator-docs'} <= {a['kind'] for a in report['artifacts']})
                for lang in ('fr','en'):
                    rendered=html.render(root/'bundle/report.json',language=lang)
                    self.assertIn(html.TEXT[lang]['agent_access_note'],rendered)
                    self.assertIn('test-client-only',rendered)
                    self.assertNotIn('<script',rendered)

    def test_partial_method_does_not_close_whole_control(self):
        data=self.data(); data['rules']=RULES[:1]
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); src=root/'input.json'; src.write_text(json.dumps(data))
            captures.build(src,root/'bundle',assessor='Synthetic importer',label='Partial',
                           selection_method='One case',access='synthetic')
            self.assertEqual(tsep.read_json(root/'bundle/report.json')['results'][0]['status'],'NT')

    def test_synthetic_review_cannot_be_labeled_real(self):
        for field in ('client_review','log_review','attribution'):
            data=self.data(); t=data['targets'][0]
            for other in ('client_review','log_review','attribution'):
                if field != other: t.pop(other)
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                root=Path(directory); src=root/'input.json'; src.write_text(json.dumps(data))
                with self.assertRaisesRegex(tsep.Invalid,'provenance'):
                    captures.build(src,root/'bundle',assessor='Importer',label='Provenance',
                                   selection_method='One case',access='public')
                self.assertFalse((root/'bundle').exists())

    def test_html_escapes_untrusted_log_values(self):
        reason='Agent access evidence / preuves accès agents: '+json.dumps({'rows':[
            {'subject':'<script>','log_record':{'user_agent':'<img src=x onerror=x>'},
             'reason':'<bad>','outcome':'pass'}]})
        rendered=html.agent_values({'reason':reason},html.TEXT['fr'])
        self.assertIn('&lt;script&gt;',rendered); self.assertNotIn('<script>',rendered)
        self.assertIn('&lt;img',rendered)


if __name__ == '__main__': unittest.main()
