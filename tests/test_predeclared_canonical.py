"""Authored inputs and loopback clients, explicitly not real browser observations."""
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
from examples import predeclared_canonical_lab as lab
from experiments import rendered_canonical_v2 as v2
from experiments import rendered_canonical as core
from experiments import rendered_metadata as metadata


class IntentAdapter(unittest.TestCase):
    def test_shared_core_all_69_frozen_cases_and_two_preference_cases(self):
        cases = []
        for name in ('cases', 'review-cases', 'url-prefix-cases'):
            cases += tsep.read_json(core.ROOT/('tests/fixtures/rendered-canonical-v1-'+name+'.json'))['cases']
        self.assertEqual(len(cases), 69)
        exact = copy.deepcopy(cases[0]); exact['intent']['preferred_url'] = 'https://EXAMPLE.test/product'
        cases.append(exact); other = copy.deepcopy(exact)
        other['record']['tree']['nodes'][3]['attributes'][1]['value'] = 'https://EXAMPLE.test/product'
        other['intent']['record_sha256'] = core.digest(other['record']); cases.append(other)
        for case in cases:
            before = copy.deepcopy(case); original = core.assess(case['record'], case['intent'])
            adapted = v2.upgrade_intent_v1(case['intent']); result = v2.assess(case['record'], adapted)
            for key in original:
                if key not in ('version', 'intent'): self.assertEqual(result[key], original[key], (case['id'], key))
            self.assertEqual(case, before)
        with self.assertRaisesRegex(ValueError, 'v2 intent'): v2.assess(cases[0]['record'], cases[0]['intent'])

    def test_predeclared_binding_and_explicit_mode(self):
        case = tsep.read_json(core.ROOT/'tests/fixtures/rendered-canonical-v1-cases.json')['cases'][0]
        intent = v2.upgrade_intent_v1(case['intent']); intent.update(mode=v2.MODE, case_id='integrated/test')
        reg = {'kind': 'predeclared-canonical-laboratory', 'version': '1', 'tasks': [
            {'id': intent['case_id'], 'url': intent['document_url'], 'intent': {k: intent[k] for k in
                ('preferred_url', 'html_canonical_required', 'known_integrity_issues', 'state_label')}}]}
        intent['registration_sha256'] = core.digest(reg)
        r = v2.assess(case['record'], intent, reg)
        self.assertEqual(r['mode'], v2.MODE); self.assertEqual(r['collection_validation'], 'not-performed-by-comparison-adapter')
        for key, value in [('preferred_url', 'https://example.test/other'), ('case_id', 'unknown'), ('registration_sha256', '0'*64)]:
            bad = dict(intent); bad[key] = value
            with self.assertRaises(ValueError): v2.assess(case['record'], bad, reg)
        with self.assertRaises(ValueError): v2.assess(case['record'], intent)
        intent['mode'] = 'retrospective'
        with self.assertRaises(ValueError): v2.assess(case['record'], intent, reg)

    def test_frozen_recipes_and_inline_capture_position(self):
        self.assertEqual(tsep.digest(lab.ROOT/lab.RECIPE), '9fe2c2a7e967026c3c8925944200e97d8aa7208ea163cf44958963933a3bba9d')
        cases, tasks, raw = lab.scope('http://127.0.0.1:1234/0123456789abcdef', '0123456789abcdef')
        self.assertEqual(len(cases), 9); self.assertEqual(len(set(t['url'] for t in tasks)), 18)
        body = lab.page(cases[-1], '0123456789abcdef', '/capture')
        self.assertLess(body.index('const tree = '), body.index('id="trailing-conflict"'))
        self.assertIn("if (\"during-parsing\" === 'during-parsing') capture()", body)
        for task in tasks: self.assertEqual(task['response_sha256'], metadata.sha(raw[task['url']]))


class PredeclaredTransport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(); cls.root = Path(cls.temp.name); cls.source = cls.root/'source'
        servers, threads, reg = lab.start(cls.source); cls.records = {}
        cls.reg = reg
        try:
            for env in reg['environments']:
                records = {}; agent = 'AUTHORED-UNIT-CLIENT/'+env
                for task in [t for t in reg['tasks'] if t['environment'] == env]:
                    started = ts01.now()
                    with urlopen(Request(task['url'], headers={'User-Agent': agent}), timeout=3) as response: response.read()
                    case = tsep.read_json(core.ROOT/'tests/fixtures/rendered-canonical-v1-cases.json')['cases'][0]
                    tree = case['record']['tree']; tree['document_url'] = task['url']
                    payload = {'kind': 'laboratory-page-inventory', 'version': '1', 'script_sha256': metadata.script_digest(),
                        'tree': tree, 'context': reg['token'], 'url': task['url'], 'state': task['trigger'],
                        'user_agent': agent, 'errors': [], 'capture_started_at': ts01.now(), 'captured_at': ts01.now()}
                    text = json.dumps(payload); raw = json.dumps({'payload': text, 'sha256': metadata.sha(text.encode())}).encode()
                    with urlopen(Request(reg['capture_endpoint'], data=raw, headers={'User-Agent': agent}), timeout=3) as response:
                        receipt = json.loads(response.read())['receipt']
                    record = {k: v for k, v in payload.items() if k not in ('kind', 'version', 'user_agent')}
                    record.update(navigation_started_at=started, observed_at=ts01.now(), page_receipt=receipt, devLogs=[],
                                  browser={'name': 'AUTHORED UNIT CLIENT, NOT BROWSER', 'version': 'unit', 'user_agent': agent})
                    records[task['case']] = record
                cls.records[env] = {'status': 'collected', 'records': records}
        finally: lab.transport.stop(servers, threads)
        cls.observations = cls.root/'observations.json'; ts01.save(cls.observations, cls.records)

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def test_offline_replay_preserves_mismatches_and_refuses_overwrite(self):
        output = self.root/'delivery'; result = lab.finish(self.source, self.observations, output)
        self.assertEqual(result['observations'], 18); self.assertEqual(result['server_requests'], 54)
        self.assertFalse(result['all_collected_checks_matched']); self.assertTrue(result['all_environments_collected'])
        with patch.object(socket, 'socket', side_effect=AssertionError('network forbidden')), \
             patch.object(socket, 'getaddrinfo', side_effect=AssertionError('DNS forbidden')):
            self.assertTrue(lab.replay(output)['same_results'])
        with self.assertRaisesRegex(ValueError, 'NEW output'): lab.finish(self.source, self.observations, output)
        (output/'extra').write_text('unexpected')
        with self.assertRaisesRegex(ValueError, 'Unexpected file'): lab.replay(output)

    def test_mutated_operator_record_and_chronology(self):
        for key, value in [('context', 'wrong'), ('capture_started_at', '2000-01-01T00:00:00Z'),
                           ('navigation_started_at', '2000-01-01T00:00:00Z'), ('page_receipt', '../x')]:
            records = copy.deepcopy(self.records); records['integrated']['records']['baseline'][key] = value
            with self.assertRaises(ValueError): lab.analyze(self.source, records)
        records = copy.deepcopy(self.records); del records['chrome']['records']['baseline']
        with self.assertRaisesRegex(ValueError, 'Missing'): lab.analyze(self.source, records)

    def test_server_log_mutations_rejected(self):
        logs = [json.loads(x) for x in (self.source/'requests.jsonl').read_text().splitlines()]
        post = next(r for r in logs if r.get('method') == 'POST')
        get = next(r for r in logs if r['agent'] != lab.AGENT and r.get('method') != 'POST')
        for label, rows in [('duplicate', logs+[post]), ('missing', [r for r in logs if r is not post]),
                            ('extra-get', logs+[get])]:
            source = self.root/label; shutil.copytree(self.source, source)
            (source/'requests.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
            with self.assertRaises(ValueError): lab.analyze(source, self.records)

    def test_preregistered_recipe_bytes_and_tools_cannot_be_replaced(self):
        for label in ('recipe', 'response', 'sources'):
            source = self.root/label; shutil.copytree(self.source, source); reg = tsep.read_json(source/'registration.json')
            if label == 'recipe': reg['cases'][0]['expected']['outcome'] = 'undetermined'
            elif label == 'response': reg['tasks'][0]['response_sha256'] = '0'*64
            else: reg['source_files']['examples/predeclared_canonical_lab.py'] = '0'*64
            (source/'registration.json').write_text(json.dumps(reg))
            receipt = tsep.read_json(source/'receipt.json'); receipt['registration_sha256'] = tsep.digest(source/'registration.json')
            (source/'receipt.json').write_text(json.dumps(receipt))
            with self.assertRaises(ValueError): lab.analyze(source, self.records)

    def test_not_collected_is_distinct_and_cannot_hide_requests(self):
        records = copy.deepcopy(self.records); records['chrome'] = {'status': 'not-collected', 'reason': 'test unavailability'}
        with self.assertRaisesRegex(ValueError, 'Extra/unmatched'): lab.analyze(self.source, records)
        source = self.root/'unavailable'; shutil.copytree(self.source, source)
        logs = [json.loads(x) for x in (source/'requests.jsonl').read_text().splitlines()]
        logs = [r for r in logs if r['agent'] != 'AUTHORED-UNIT-CLIENT/chrome']
        (source/'requests.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in logs))
        result = lab.analyze(source, records)
        self.assertEqual(result['observations'], 9); self.assertFalse(result['all_environments_collected'])
        self.assertEqual(result['environments']['chrome']['status'], 'not-collected')
