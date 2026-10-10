"""Authored sequence and HTTP client tests; no browser execution claimed."""
import copy
import json
from pathlib import Path
import shutil
import socket
import tempfile
import unittest
from unittest.mock import patch
from urllib.request import Request, urlopen
import tsep
from collectors import ts01
from experiments import canonical_sequence as seq
from experiments import rendered_canonical as core
from experiments import rendered_metadata as metadata
from examples import canonical_sequence_lab as lab

FIXTURES = tsep.read_json(core.ROOT/'tests/fixtures/rendered-canonical-v1-cases.json')['cases']


def fixture(name='exact'):
    return copy.deepcopy(next(c for c in FIXTURES if c['id'] == name))


def authored_tree(url, state, preferred):
    tree = fixture()['record']['tree']; tree['document_url'] = url
    tree['nodes'][3]['attributes'][1]['value'] = preferred; tree['nodes'][3]['resolved_href'] = preferred
    tree['nodes'][3]['attributes'].append({'name': 'id', 'local_name': 'id', 'namespace': None, 'value': 'primary'})
    tree['nodes'][4]['child_count'] = 1
    node = copy.deepcopy(tree['nodes'][4]); node.update(id=5, parent=4, index=0, name='code', child_count=1,
        attributes=[{'name': 'id', 'local_name': 'id', 'namespace': None, 'value': 'lab-state'}])
    text = dict(node, id=6, parent=5, name='#text', type=3, namespace=None, attributes=[], data=state, child_count=0, shadow='not-element')
    tree['nodes'] += [node, text]; tree['reported_node_count'] = len(tree['nodes']); return tree


class SequenceComparison(unittest.TestCase):
    def prepare(self, names):
        cases, pages, tasks, _ = lab.scope('http://127.0.0.1:1234/0123456789abcdef', '0123456789abcdef')
        page = pages[0]; tasks = [t for t in tasks if t['page_id'] == page['id']]
        records = {}
        for task, name in zip(tasks, names):
            if name is None: records[task['id']] = {'snapshot': None, 'missing_reason': 'AUTHORED missing state'}; continue
            x = fixture(name); task['url'] = x['intent']['document_url']; page['url'] = task['url']
            task['intent'] = {k: x['intent'][k] for k in ('preferred_url', 'state_label', 'html_canonical_required', 'known_integrity_issues')}
            records[task['id']] = {'snapshot': x['record'], 'missing_reason': None}
        # Missing tasks use the same declared URL as received tasks.
        for task in tasks: task['url'] = page['url']
        reg = {'kind': 'predeclared-canonical-laboratory', 'version': '1', 'method': seq.METHOD, 'pages': [page], 'tasks': tasks}
        return reg, page['id'], records

    def test_final_agreement_does_not_erase_previous_contradiction(self):
        args = self.prepare(['exact', 'query-difference', 'exact']); before = copy.deepcopy(args)
        result = seq.assess(*args)
        self.assertEqual(result['contradiction_state_ids'], ['after-action-1'])
        self.assertTrue(result['at_least_one_observed_contradiction'])
        self.assertEqual(result['last_planned_state']['outcome'], 'agreement-in-record')
        self.assertNotIn('outcome', result); self.assertEqual(result['continuous_stability'], 'not-assessed')
        self.assertEqual(args, before)

    def test_unknown_and_missing_states_remain_visible_with_prior_conflict(self):
        result = seq.assess(*self.prepare(['query-difference', 'same-value-body', None]))
        self.assertEqual(result['contradiction_state_ids'], ['initial'])
        self.assertEqual(result['undetermined_state_ids'], ['after-action-1'])
        self.assertEqual(result['missing_state_ids'], ['after-action-2'])
        self.assertEqual(result['last_planned_state'], {'id': 'after-action-2', 'availability': 'not-received', 'outcome': None})
        self.assertFalse(result['all_planned_states_received'])

    def test_all_agreements_are_not_continuous_stability(self):
        r = seq.assess(*self.prepare(['exact', 'exact', 'exact']))
        self.assertFalse(r['at_least_one_observed_contradiction']); self.assertEqual(r['continuous_stability'], 'not-assessed')
        self.assertEqual(len(r['states']), 3)

    def test_missing_unknown_duplicate_task_and_bad_snapshot_rejected(self):
        for change in ('omit', 'extra', 'duplicate', 'wrong-page', 'invalid-tree', 'no-reason'):
            reg, page, records = self.prepare(['exact', 'exact', 'exact']); key = next(iter(records))
            if change == 'omit': del records[key]
            elif change == 'extra': records['extra'] = records[key]
            elif change == 'duplicate': reg['tasks'].append(reg['tasks'][0])
            elif change == 'wrong-page': reg['tasks'][0]['page_id'] = 'other'
            elif change == 'invalid-tree': records[key]['snapshot']['tree']['reported_node_count'] = 0
            else: records[key] = {'snapshot': None, 'missing_reason': ''}
            with self.subTest(change=change), self.assertRaises(ValueError): seq.assess(reg, page, records)

    def test_plan_frozen_before_implementation_and_all_state_actions_explicit(self):
        self.assertEqual(tsep.digest(lab.ROOT/lab.RECIPE), 'c015f3cebc4502c0bd9cfbdb8f7bb08807303d63fbe46b469a118e032d21fdb7')
        self.assertEqual(len(lab.recipes()['cases']), 4)
        for case in lab.recipes()['cases']:
            self.assertEqual([s['action'] for s in case['states']], ['load', 'click #advance 1', 'click #advance 2'])
            self.assertEqual(len(case['actions']), 2)


class SequenceTransport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(); cls.root = Path(cls.temp.name); cls.source = cls.root/'source'
        servers, threads, reg = lab.start(cls.source); cls.records = {}; cls.reg = reg
        try:
            for env in reg['environments']:
                pages = {}; ua = 'AUTHORED-UNIT-CLIENT/'+env
                for page in [p for p in reg['pages'] if p['environment'] == env]:
                    nav = ts01.now()
                    with urlopen(Request(page['url'], headers={'User-Agent': ua}), timeout=3) as response: response.read()
                    states = {}; previous = None
                    for task in [t for t in reg['tasks'] if t['page_id'] == page['id']]:
                        action_at = ts01.now()
                        payload = {'kind': 'laboratory-page-inventory', 'version': '1', 'script_sha256': metadata.script_digest(),
                            'tree': authored_tree(page['url'], task['state_id'], task['intent']['preferred_url']),
                            'context': reg['token'], 'url': page['url'], 'state': task['state_id'], 'sequence_index': task['sequence_index'],
                            'action': task['action'], 'previous_receipt': previous, 'user_agent': ua, 'errors': [],
                            'capture_started_at': ts01.now(), 'captured_at': ts01.now()}
                        text = json.dumps(payload); raw = json.dumps({'payload': text, 'sha256': metadata.sha(text.encode())}).encode()
                        with urlopen(Request(reg['capture_endpoint'], data=raw, headers={'User-Agent': ua}), timeout=3) as response:
                            previous = json.loads(response.read())['receipt']
                        states[task['state_id']] = {k: payload[k] for k in lab.FIELDS}
                        states[task['state_id']].update(action_started_at=action_at, observed_at=ts01.now(), page_receipt=previous, devLogs=[])
                    pages[page['case']] = {'navigation_started_at': nav, 'observed_at': ts01.now(), 'states': states,
                        'browser': {'name': 'AUTHORED UNIT CLIENT, NOT BROWSER', 'version': 'unit', 'user_agent': ua}}
                cls.records[env] = {'status': 'collected', 'pages': pages}
        finally: lab.transport.stop(servers, threads)
        cls.observations = cls.root/'observations.json'; ts01.save(cls.observations, cls.records)

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def source_copy(self, name):
        dest = self.root/name; shutil.copytree(self.source, dest); return dest

    def test_actual_transport_of_authored_records_replays_without_network(self):
        out = self.root/'delivery'; result = lab.finish(self.source, self.observations, out)
        self.assertEqual(result['observations'], 24); self.assertEqual(result['server_requests'], 40)
        self.assertEqual(result['recipe_checks'], 192); self.assertFalse(result['all_collected_checks_matched'])
        self.assertTrue(result['all_planned_states_received'])
        with patch.object(socket, 'socket', side_effect=AssertionError('Network forbidden')), patch.object(socket, 'getaddrinfo', side_effect=AssertionError('DNS forbidden')):
            self.assertTrue(lab.replay(out)['same_results'])
        with self.assertRaisesRegex(ValueError, 'NEW output'): lab.finish(self.source, self.observations, out)
        (out/'extra').write_text('unexpected')
        with self.assertRaisesRegex(ValueError, 'Unexpected file'): lab.replay(out)

    def test_duplicate_navigation_and_missing_duplicate_post_rejected(self):
        rows = [json.loads(x) for x in (self.source/'requests.jsonl').read_text().splitlines()]
        post = next(r for r in rows if r.get('method') == 'POST'); get = next(r for r in rows if r['agent'] != lab.AGENT and r.get('method') != 'POST')
        for name, changed in [('duplicate-post', rows+[post]), ('duplicate-get', rows+[get]), ('missing-post', [r for r in rows if r is not post])]:
            source = self.source_copy(name); (source/'requests.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in changed))
            with self.assertRaises(ValueError): lab.analyze(source, self.records)

    def test_changed_state_order_receipt_or_operator_chronology_rejected(self):
        for key, value in [('previous_receipt', '0'*64), ('sequence_index', 0), ('action', 'other action'),
                           ('action_started_at', '2000-01-01T00:00:00Z'), ('page_receipt', '../bad')]:
            records = copy.deepcopy(self.records); records['integrated']['pages']['unchanged']['states']['after-action-1'][key] = value
            with self.assertRaises(ValueError): lab.analyze(self.source, records)

    def test_missing_final_state_preserved_without_reclassifying_as_agreement(self):
        source = self.source_copy('missing-final'); records = copy.deepcopy(self.records)
        page = records['integrated']['pages']['unchanged']; removed = page['states']['after-action-2']['page_receipt']
        page['states']['after-action-2'] = {'missing_reason': 'AUTHORED interruption, no retry'}
        rows = [json.loads(x) for x in (source/'requests.jsonl').read_text().splitlines()]
        (source/'requests.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows if r.get('receipt') != removed))
        result = lab.analyze(source, records)
        self.assertEqual(result['observations'], 23); self.assertFalse(result['all_planned_states_received'])
        page_result = result['environments']['integrated']['pages'][0]
        self.assertFalse(page_result['receipt_chain_complete'])
        self.assertEqual(page_result['ledger']['last_planned_state']['availability'], 'not-received')

    def test_missing_state_cannot_hide_attempt_or_allow_later_capture(self):
        for state in ('after-action-1', 'after-action-2'):
            records = copy.deepcopy(self.records)
            records['integrated']['pages']['unchanged']['states'][state] = {'missing_reason': 'AUTHORED gap'}
            with self.assertRaises(ValueError): lab.analyze(self.source, records)

    def test_recipe_and_page_hash_cannot_be_rebound(self):
        source = self.source_copy('rebound'); reg = tsep.read_json(source/'registration.json')
        reg['pages'][0]['response_sha256'] = '0'*64
        (source/'registration.json').write_text(json.dumps(reg)); receipt = tsep.read_json(source/'receipt.json')
        receipt['registration_sha256'] = tsep.digest(source/'registration.json'); (source/'receipt.json').write_text(json.dumps(receipt))
        with self.assertRaisesRegex(ValueError, 'scope'): lab.analyze(source, self.records)

    def test_not_collected_environment_cannot_hide_requests(self):
        records = copy.deepcopy(self.records); records['chrome'] = {'status': 'not-collected', 'reason': 'AUTHORED unavailability'}
        with self.assertRaisesRegex(ValueError, 'Extra/unmatched'): lab.analyze(self.source, records)
        source = self.source_copy('unavailable'); rows = [json.loads(x) for x in (source/'requests.jsonl').read_text().splitlines()]
        (source/'requests.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows if r['agent'] != 'AUTHORED-UNIT-CLIENT/chrome'))
        result = lab.analyze(source, records)
        self.assertEqual(result['observations'], 12); self.assertFalse(result['all_planned_states_received'])

    def rewrite_last_post(self, source, records, changes):
        record = records['integrated']['pages']['unchanged']['states']['after-action-2']
        old = record['page_receipt']; envelope = json.loads((source/'posts'/(old+'.json')).read_bytes())
        payload = json.loads(envelope['payload']); payload.update(changes)
        text = json.dumps(payload); raw = json.dumps({'payload': text, 'sha256': metadata.sha(text.encode())}).encode()
        receipt = metadata.sha(raw); response = lab.response_bytes(receipt)
        (source/'posts'/(receipt+'.json')).write_bytes(raw); (source/'posts'/(receipt+'.response.bin')).write_bytes(response)
        rows = [json.loads(x) for x in (source/'requests.jsonl').read_text().splitlines()]
        row = next(r for r in rows if r.get('receipt') == old); row.update(receipt=receipt, response_sha256=metadata.sha(response))
        (source/'requests.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
        record.update(changes); record['page_receipt'] = receipt

    def test_coherently_rehashed_chain_action_and_index_still_rejected(self):
        for key, value in [('previous_receipt', '0'*64), ('sequence_index', 1), ('action', 'click #advance 99'),
                           ('capture_started_at', '2000-01-01T00:00:00Z')]:
            source = self.source_copy('coherent-'+key); records = copy.deepcopy(self.records)
            self.rewrite_last_post(source, records, {key: value})
            with self.assertRaises(ValueError): lab.analyze(source, records)

    def test_marker_mismatch_is_retained_as_recipe_deviation(self):
        source = self.source_copy('marker'); records = copy.deepcopy(self.records)
        tree = copy.deepcopy(records['integrated']['pages']['unchanged']['states']['after-action-2']['tree'])
        tree['nodes'][6]['data'] = 'wrong-state'
        self.rewrite_last_post(source, records, {'tree': tree})
        result = lab.analyze(source, records)
        check = result['environments']['integrated']['pages'][0]['checks'][-1]['checks'][-1]
        self.assertEqual(check['check'], 'captured-state-marker'); self.assertFalse(check['matches'])

    def test_rehashed_receiver_response_cannot_claim_another_receipt(self):
        source = self.source_copy('receiver'); rows = [json.loads(x) for x in (source/'requests.jsonl').read_text().splitlines()]
        row = next(r for r in rows if r.get('method') == 'POST'); raw = lab.response_bytes('0'*64)
        (source/'posts'/(row['receipt']+'.response.bin')).write_bytes(raw); row['response_sha256'] = metadata.sha(raw)
        (source/'requests.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
        with self.assertRaisesRegex(ValueError, 'receiver response'): lab.analyze(source, self.records)
