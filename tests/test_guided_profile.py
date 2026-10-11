"""Prospective guided profile: actual loopback transport and hostile replay edits."""
import copy
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch

import tsep
from collectors import ts01, preflight

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which(os.environ.get('TSEP_SOURCE_NODE') or 'node')
NODE24 = bool(NODE and subprocess.run([NODE, '--version'], capture_output=True).stdout.startswith(b'v24.'))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        self.server.requests.append(self.path)
        raw = self.server.body.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def reseal(root):
    names = [line.split('  ', 1)[1] for line in (root/'SHA256SUMS').read_text().splitlines()]
    (root/'SHA256SUMS').unlink()
    ts01.manifest(root, names)


class GuidedProfile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.server.daemon_threads = True
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = 'http://127.0.0.1:'+str(cls.server.server_port)+'/'
        p = ROOT/'tests/fixtures/guided-profile-v2.json'
        assert hashlib.sha256(p.read_bytes()).hexdigest() == p.with_suffix('.sha256').read_text().split()[0]
        cls.cases = json.loads(p.read_text())['cases']

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)
        self.server.requests = []
        self.server.body = self.cases[0]['reference_body']
        self.settings = {'urls': [self.url], 'origins': [self.url], 'agent': 'TSEP-guided-synthetic/1',
                         'accept_encoding': 'identity', 'timeout': 2, 'max_bytes': 524288,
                         'max_redirects': 1, 'allow_loopback': True, 'network': 'Actual loopback; authored pages',
                         'selection_method': 'One explicitly chosen synthetic URL', 'access': 'synthetic'}
        self.node_env = patch.dict(os.environ, {'TSEP_SOURCE_NODE': NODE or '/missing-node'})
        self.node_env.start()

    def tearDown(self):
        self.node_env.stop(); self.temp.cleanup()

    def criteria(self, case=None):
        case = case or self.cases[0]
        return {self.url: dict({'policy': 'markers'}, **{k: case[k] for k in
            ('identity_reader', 'required_markers', 'forbidden_markers') if k in case})}

    def collect_reference(self):
        ts01.reference(self.settings, self.root/'first')

    def seal(self, criteria=None):
        return ts01.seal(self.root/'first/reference', self.root/'intent.json', assessor='Synthetic author',
                         label='Authored guided profile', criteria=criteria or self.criteria())

    def evaluate(self):
        return ts01.evaluate(self.root/'first/reference', self.root/'intent.json', self.root/'assessment')

    @unittest.skipUnless(NODE24, 'Explicit or PATH Node 24 required for actual parsed-profile transport')
    def test_frozen_transport_cases_and_portable_exact_replay(self):
        for case in self.cases:
            with self.subTest(case=case['id']), tempfile.TemporaryDirectory() as folder:
                self.root = Path(folder); self.server.requests = []; self.server.body = case['reference_body']
                self.collect_reference()
                if case['expected_reference_preflight'] == 'contradiction':
                    with self.assertRaisesRegex(ValueError, 'Reference marker contradiction'):
                        self.seal(self.criteria(case))
                    self.assertEqual(len(self.server.requests), 1)
                    self.assertFalse((self.root/'intent.json').exists())
                    continue
                receipt = self.seal(self.criteria(case))
                self.assertEqual(receipt['reference_preflight'][0]['state'], case['expected_reference_preflight'])
                self.server.body = case['evaluation_body']
                result = self.evaluate()
                self.assertEqual(result['counts'][case['expected_control_status']], 1)
                intent = tsep.read_json(self.root/'intent.json')
                self.assertEqual(intent['intent_version'], '4')
                self.assertEqual(intent['targets'][0]['identity_basis']['identity_reader'], case.get('identity_reader'))
                shutil.rmtree(self.root/'first'); (self.root/'intent.json').unlink()
                with patch('socket.socket', side_effect=AssertionError('No network')), \
                     patch('socket.getaddrinfo', side_effect=AssertionError('No DNS')):
                    self.assertTrue(ts01.replay(self.root/'assessment', self.root/'replay')['replayed'])
                detail = tsep.read_json(self.root/'replay/replay.json')
                self.assertTrue(detail['same_source_observations']); self.assertTrue(detail['same_report_results'])
                self.assertEqual(len(self.server.requests), 2)
                self.assertIn('report-fr.html', ts01.verify(self.root/'replay'))

    def test_unknown_null_or_wrong_policy_rejected_before_parser_and_measurement(self):
        self.collect_reference()
        for policy, reader in [('markers', None), ('markers', 'unknown'), ('digest', 'html-tree-markers-v1'),
                               ('stable', 'html-tree-markers-v1')]:
            options = self.criteria(); options[self.url].update(policy=policy, identity_reader=reader)
            with self.subTest(policy=policy, reader=reader), \
                 patch.object(preflight.source_http, 'inventory', side_effect=AssertionError('No parsing')), \
                 self.assertRaisesRegex(ValueError, 'identity_reader requires'):
                self.seal(options)
        self.assertEqual(len(self.server.requests), 1)

    def test_missing_node_refuses_sealing_without_evaluation_request(self):
        self.collect_reference()
        with patch.dict(os.environ, {'TSEP_SOURCE_NODE': '/tsep-deliberately-missing-node'}), \
             self.assertRaisesRegex(ValueError, 'requires a usable Node 24'):
            self.seal()
        self.assertFalse((self.root/'intent.json').exists())
        self.assertEqual(len(self.server.requests), 1)

    def test_marker_bounds_precede_cross_product_or_parser(self):
        class MustNotSearch(str):
            def __contains__(self, other):
                raise AssertionError('Cross-product ran before bounds')
        with patch.object(preflight.source_http, 'inventory', side_effect=AssertionError('No parser')), \
             self.assertRaisesRegex(ValueError, 'Invalid or excessive'):
            preflight.reference_check({}, b'', 'markers', [MustNotSearch(str(i)) for i in range(65)], [],
                                      identity_reader='html-tree-markers-v1')

    @unittest.skipUnless(NODE24, 'Node 24 required')
    def test_changed_profile_or_preflight_is_refused_before_measurement(self):
        self.collect_reference(); self.seal()
        original = tsep.read_json(self.root/'intent.json')
        for field in ('reader', 'receipt', 'sources'):
            changed = copy.deepcopy(original)
            if field == 'reader': del changed['targets'][0]['intent']['identity_reader']
            elif field == 'receipt': changed['targets'][0]['reference_preflight']['diagnostic_sha256'] = '0'*64
            else: changed['reference_source_files']['collectors/preflight.py'] = '0'*64
            (self.root/'intent.json').write_text(json.dumps(changed))
            with self.subTest(field=field), self.assertRaises(ValueError): self.evaluate()
            self.assertEqual(len(self.server.requests), 1)
            self.assertFalse((self.root/'assessment').exists())

    @unittest.skipUnless(NODE24, 'Node 24 required')
    def test_changed_runtime_probe_refuses_measurement(self):
        self.collect_reference(); self.seal()
        actual = preflight.source_http.inventory
        def changed(*args, **kwargs):
            value = actual(*args, **kwargs); value['runtime']['node'] += '-changed'
            return value
        with patch.object(preflight.source_http, 'inventory', side_effect=changed), \
             self.assertRaisesRegex(ValueError, 'runtime changed'):
            self.evaluate()
        self.assertEqual(len(self.server.requests), 1)

    @unittest.skipUnless(NODE24, 'Node 24 required')
    def test_document_unknown_warns_while_unchanged_digest_remains_normative(self):
        self.server.body = '<!doctype html><html><head></head><body><p>Expected</p><svg><text>Other</text></svg></body></html>'
        self.collect_reference(); receipt = self.seal()
        self.assertEqual(receipt['reference_preflight'][0]['state'], 'unavailable')
        self.assertTrue(receipt['warnings'])
        self.assertEqual(self.evaluate()['counts']['C'], 1)
        self.assertIn('unavailable', (self.root/'assessment/report-fr.html').read_text())

    @unittest.skipUnless(NODE24, 'Node 24 required')
    def test_coherently_rehashed_diagnostic_is_rejected_even_with_same_verdict(self):
        self.collect_reference(); self.seal(); self.server.body = self.cases[0]['evaluation_body']; self.evaluate()
        source = self.root/'assessment'; bundle = source/'bundle'
        diagnostic = next((bundle/'observations').glob('source-observation-*.json'))
        value = tsep.read_json(diagnostic); value['observations'][0]['reason'] += ' tampered'
        diagnostic.write_text(json.dumps(value, ensure_ascii=False))
        report = tsep.read_json(bundle/'report.json')
        for artifact in report['artifacts']:
            if artifact['path'] == diagnostic.relative_to(bundle).as_posix(): artifact['sha256'] = tsep.digest(diagnostic)
        (bundle/'report.json').write_text(json.dumps(report, ensure_ascii=False))
        gate = tsep.validate(report, bundle)
        (bundle/'earl.jsonld').write_text(json.dumps(tsep.earl(report, gate), ensure_ascii=False))
        reseal(bundle); reseal(source)
        with self.assertRaisesRegex(ValueError, 'source diagnostics'):
            ts01.replay(source, self.root/'replay')
        detail = tsep.read_json(self.root/'replay/replay.json')
        self.assertTrue(detail['same_atomic_observations_and_gate'])
        self.assertFalse(detail['same_source_observations'])
        ts01.verify(self.root/'replay')

    def test_transitive_parser_sources_are_bound_before_collection(self):
        sources = ts01.collection_sources()
        for name in ('conformance/source_markers.py', 'experiments/source_markers.py',
                     'experiments/source_content.mjs', 'third_party/source-tree/parse5-8.0.1.tgz'):
            self.assertEqual(sources[name], tsep.digest(ROOT/name))

    @unittest.skipUnless(NODE24, 'Node 24 required')
    def test_changed_retained_reference_preflight_binding_prevents_replay(self):
        self.collect_reference(); self.seal(); self.server.body = self.cases[0]['evaluation_body']; self.evaluate()
        source = self.root/'assessment'
        value = tsep.read_json(source/'intent.json')
        value['targets'][0]['reference_preflight']['state'] = 'unavailable'
        (source/'intent.json').write_text(json.dumps(value))
        reseal(source)
        with self.assertRaisesRegex(ValueError, 'binding mismatch'):
            ts01.replay(source, self.root/'replay')
        self.assertFalse((self.root/'replay').exists())
        self.assertEqual(len(self.server.requests), 2)

    @unittest.skipUnless(NODE24, 'Node 24 required')
    def test_coherently_rehashed_report_text_is_rejected_with_same_atomic_results(self):
        self.collect_reference(); self.seal(); self.server.body = self.cases[0]['evaluation_body']; self.evaluate()
        source = self.root/'assessment'; bundle = source/'bundle'
        report = tsep.read_json(bundle/'report.json')
        report['results'][0]['reason'] += ' Altered report explanation.'
        (bundle/'report.json').write_text(json.dumps(report, ensure_ascii=False))
        (bundle/'earl.jsonld').write_text(json.dumps(tsep.earl(report, tsep.validate(report, bundle)), ensure_ascii=False))
        reseal(bundle); reseal(source)
        with self.assertRaisesRegex(ValueError, 'report or tool sources differ'):
            ts01.replay(source, self.root/'replay')
        receipt = tsep.read_json(self.root/'replay/replay.json')
        self.assertTrue(receipt['same_atomic_observations_and_gate'])
        self.assertTrue(receipt['same_source_observations'])
        self.assertFalse(receipt['same_report_results'])
