"""Actual loopback transport, synthetic plans/reviews; never an Edikka audit. Apache-2.0."""
import copy
import hashlib
import json
from pathlib import Path
import socketserver
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from adapters import redirect_plan
from adapters.package import inventory, json_bytes, seal
from adapters.replay import replay
from collectors import ts02
from conformance.http import raw_bytes

FIXTURE = ROOT/'tests/fixtures/redirect-collection-v1.json'
FROZEN = '5cc3a1e674c045a1c9705e790747a475d725d75329789d19b1038b28ed6f16d8'
CASES = json.loads(FIXTURE.read_text())['cases']


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        lines = []
        while True:
            line = self.rfile.readline(16384)
            lines.append(line)
            if line in (b'\r\n', b'\n', b''):
                break
        request = b''.join(lines)
        path = lines[0].split()[1].decode('ascii')
        self.server.hits.append(path)
        self.server.raw_requests.append(request)
        response = self.server.responses.get(path, 'HTTP/1.1 404 Missing\r\nContent-Length: 0\r\n\r\n')
        self.wfile.write(response.encode('ascii'))


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


class RedirectCollection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = Server(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = 'http://127.0.0.1:'+str(cls.server.server_address[1])

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.server.hits = []; self.server.raw_requests = []
        self.server.responses = dict(CASES[0]['responses'])

    def tearDown(self):
        self.temp.cleanup()

    def files(self, case=None, settings=None, second=False):
        case = case or CASES[0]
        self.server.responses = dict(case['responses'])
        target = {'url': self.base+'/start',
                  'context': {'network': 'Synthetic loopback fixture', 'bounds': 'Replaced before review',
                              'tool': 'To be bound', 'tool_version': 'To be bound'},
                  'intent': {'declared_at': ts02.now(), 'crawler': 'TSEP-synthetic-TS02/1',
                             'redirect_plan': {'mechanism': 'http', 'source_url': self.base+'/start',
                                 'expected_final_url': self.base+case.get('final_path', '/end'),
                                 'min_redirects': case.get('min_redirects', 1),
                                 'max_redirects': case.get('max_redirects', 1),
                                 'redirect_statuses': [301, 308],
                                 'terminal_statuses': case.get('terminal_statuses', [200])}}}
        data = {'kind': 'tsep-redirect-plan', 'access': 'synthetic',
                'selection_reason': 'Authored local fixture; no real owner or website judgment', 'targets': [target]}
        if second:
            other = copy.deepcopy(target)
            other['url'] = self.base+'/second'
            other['intent']['redirect_plan'].update(source_url=other['url'])
            data['targets'].append(other)
            self.server.responses['/second'] = self.server.responses['/start']
        config = dict(origins=[self.base], accept_encoding='identity', timeout=1, max_bytes=4096,
                      max_redirects=case.get('collect_redirects', 3), max_total_bytes=2*1024*1024,
                      max_seconds=10, allow_loopback=True)
        config.update(settings or {})
        (self.root/'plan.json').write_bytes(json_bytes(data))
        (self.root/'settings.json').write_bytes(json_bytes(config))
        return data, config

    def prepare(self, case=None, settings=None, second=False):
        self.files(case, settings, second)
        ts02.prepare(self.root/'plan.json', self.root/'settings.json', self.root/'request')

    def approve(self, outcome='approved'):
        response = tsep.read_json(self.root/'request/response-template.json')
        for row in response['responses']:
            row.update(reviewer='Synthetic test author', observed_at=ts02.now(), outcome=outcome,
                       reason='Authored expected policy for local fixture, not a human approval',
                       assistance='Automated exercise', provenance='synthetic-exercise')
        (self.root/'response.json').write_bytes(json_bytes(response))
        redirect_plan.import_response(self.root/'request', self.root/'response.json', self.root/'reviewed')

    def test_prefrozen_cases_native_transport_assessment_and_offline_replay(self):
        self.assertEqual(hashlib.sha256(FIXTURE.read_bytes()).hexdigest(), FROZEN)
        parent = self.root
        for case in CASES:
            with self.subTest(case=case['id']):
                self.root = parent/case['id']; self.root.mkdir()
                self.server.hits = []; self.server.raw_requests = []
                self.prepare(case); self.approve()
                ts02.collect(self.root/'reviewed', self.root/'collection')
                self.assertEqual(self.server.hits, case['hits'])
                raw = tsep.read_json(self.root/'collection/captures.json')['targets'][0]['http']
                for index, hop in enumerate(raw):
                    self.assertEqual(raw_bytes(hop['request']), self.server.raw_requests[index])
                    self.assertEqual(raw_bytes(hop['response']), case['responses'][case['hits'][index]].encode())
                with patch('socket.socket', side_effect=AssertionError('Assessment/replay must remain offline')):
                    result = ts02.assess(self.root/'collection', self.root/'report')
                    rr = replay(Path(result['bundle']), self.root/'replay')
                self.assertTrue(rr['replayed'])
                self.assertEqual(tsep.read_json(self.root/'report/assessment/bundle/gate.json')['counts'][case['expected']], 1)
                report = tsep.read_json(self.root/'report/assessment/bundle/report.json')
                self.assertEqual(report['controls'], ['TS02'])
                for lang in ('fr', 'en'):
                    self.assertTrue((self.root/f'report/report-{lang}.html').is_file())
                inventory(self.root/'collection'); inventory(self.root/'report')
        self.root = parent

    def test_preparation_is_offline_and_does_not_approve(self):
        with patch('socket.socket', side_effect=AssertionError('Offline')):
            self.prepare()
        row = tsep.read_json(self.root/'request/response-template.json')['responses'][0]
        self.assertIsNone(row['outcome']); self.assertEqual(row['reviewer'], '')
        context = tsep.read_json(self.root/'request/plan.json')['targets'][0]['context']
        self.assertEqual(context['collection']['source_files'], ts02.sources())
        self.assertEqual(context['tool'], ts02.NAME)
        self.assertIn(ts02.NAME, (self.root/'request/plan.html').read_text())
        self.assertEqual(self.server.hits, [])

    def test_missing_or_rejected_approval_refuses_before_network(self):
        self.prepare()
        with patch.object(ts02, 'worker', side_effect=AssertionError('Must not acquire')):
            with self.assertRaises(ValueError):
                ts02.collect(self.root/'request', self.root/'collection')
            self.approve('rejected')
            with self.assertRaisesRegex(ValueError, 'prior approval'):
                ts02.collect(self.root/'reviewed', self.root/'collection')
        self.assertFalse((self.root/'collection').exists()); self.assertEqual(self.server.hits, [])

    def test_two_targets_preserve_population(self):
        self.prepare(second=True); self.approve()
        ts02.collect(self.root/'reviewed', self.root/'collection')
        result = ts02.assess(self.root/'collection', self.root/'report')
        data = tsep.read_json(self.root/'collection/captures.json')
        self.assertEqual([t['url'] for t in data['targets']], [self.base+'/start', self.base+'/second'])
        self.assertEqual(self.server.hits, ['/start', '/end', '/second', '/end'])
        self.assertEqual(tsep.read_json(Path(result['bundle'])/'gate.json')['counts']['C'], 1)

    def test_rehashed_capture_cannot_disagree_with_raw_files(self):
        self.prepare(); self.approve(); ts02.collect(self.root/'reviewed', self.root/'collection')
        root = self.root/'collection'
        data = tsep.read_json(root/'captures.json'); data['targets'][0]['http'][0]['complete'] = False
        (root/'captures.json').write_bytes(json_bytes(data))
        ledger = tsep.read_json(root/'collection.json'); ledger['captures_sha256'] = tsep.digest(root/'captures.json')
        (root/'collection.json').write_bytes(json_bytes(ledger)); seal(root)
        with self.assertRaisesRegex(ValueError, 'native files'):
            ts02.assess(root, self.root/'report')
        self.assertFalse((self.root/'report').exists())

    def test_changed_collector_refuses_before_acquisition(self):
        self.prepare(); self.approve()
        altered = dict(ts02.sources(), **{'collectors/http.py': '0'*64})
        with patch.object(ts02, 'sources', return_value=altered), \
                patch.object(ts02, 'worker', side_effect=AssertionError('No request')):
            with self.assertRaisesRegex(ValueError, 'source files changed'):
                ts02.collect(self.root/'reviewed', self.root/'collection')
        self.assertFalse((self.root/'collection').exists())

    def test_phase_budget_preserves_prefix_and_unvisited_target(self):
        self.prepare(settings={'max_total_bytes': 1024, 'max_bytes': 4096}, second=True); self.approve()
        self.server.responses['/start'] = 'HTTP/1.1 301 Moved\r\nLocation: /end\r\nContent-Length: 2048\r\n\r\n'+'x'*2048
        ts02.collect(self.root/'reviewed', self.root/'collection')
        data = tsep.read_json(self.root/'collection/captures.json')
        self.assertEqual(len(raw_bytes(data['targets'][0]['http'][0]['response'])), 1024)
        self.assertFalse(data['targets'][0]['http'][0]['complete'])
        self.assertEqual(data['targets'][1]['http'], [])
        self.assertEqual(self.server.hits, ['/start'])
        result = ts02.assess(self.root/'collection', self.root/'report')
        self.assertEqual(tsep.read_json(Path(result['bundle'])/'gate.json')['counts']['NT'], 1)

    def test_total_deadline_stops_later_hops_and_remaining_targets(self):
        self.prepare(settings={'max_seconds': 1}, second=True); self.approve()
        with patch.object(ts02.time, 'monotonic', side_effect=[0, .1, 2, 2]):
            ts02.collect(self.root/'reviewed', self.root/'collection')
        data = tsep.read_json(self.root/'collection/captures.json')
        self.assertEqual(self.server.hits, ['/start'])
        self.assertEqual(len(data['targets'][0]['http']), 1)
        self.assertEqual(data['targets'][1]['http'], [])
        result = ts02.assess(self.root/'collection', self.root/'report')
        self.assertEqual(tsep.read_json(Path(result['bundle'])/'gate.json')['counts']['NT'], 1)

    def test_supervisor_timeout_retains_empty_attempt_without_inventing_response(self):
        self.prepare(); self.approve()
        with patch.object(ts02.subprocess, 'run', side_effect=subprocess.TimeoutExpired('worker', 1)):
            ts02.collect(self.root/'reviewed', self.root/'collection')
        hop = tsep.read_json(self.root/'collection/captures.json')['targets'][0]['http'][0]
        self.assertEqual(raw_bytes(hop['response']), b''); self.assertEqual(raw_bytes(hop['request']), b'')
        self.assertFalse(hop['complete']); self.assertIn('Supervisor', hop['error'])
        result = ts02.assess(self.root/'collection', self.root/'report')
        self.assertEqual(tsep.read_json(Path(result['bundle'])/'gate.json')['counts']['NT'], 1)

    def test_failed_collection_keeps_attempts_and_refuses_assessment(self):
        self.prepare(); self.approve()
        def failed(*args, **kwargs):
            (args[3]/'response.bin').write_bytes(b'partial')
            raise OSError('Synthetic local persistence failure')
        with patch.object(ts02, 'worker', side_effect=failed):
            with self.assertRaisesRegex(OSError, 'persistence'):
                ts02.collect(self.root/'reviewed', self.root/'collection')
        self.assertEqual((self.root/'collection/raw/target-1-hop-1/response.bin').read_bytes(), b'partial')
        inventory(self.root/'collection')
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            ts02.assess(self.root/'collection', self.root/'report')

    def test_existing_or_nested_outputs_are_refused(self):
        self.prepare(); self.approve()
        with patch.object(ts02, 'worker', side_effect=AssertionError('No request')):
            for destination in [self.root/'reviewed', self.root/'reviewed/nested']:
                with self.assertRaises(ValueError):
                    ts02.collect(self.root/'reviewed', destination)

    def test_assessment_does_not_overwrite_or_nest_into_collection(self):
        self.prepare(); self.approve()
        ts02.collect(self.root/'reviewed', self.root/'collection')
        before = inventory(self.root/'collection')
        with self.assertRaises(ValueError):
            ts02.assess(self.root/'collection', self.root/'collection/nested')
        ts02.assess(self.root/'collection', self.root/'report')
        with self.assertRaises(ValueError):
            ts02.assess(self.root/'collection', self.root/'report')
        self.assertEqual(inventory(self.root/'collection'), before)

    def test_loopback_scope_and_settings_refused_before_request(self):
        data, config = self.files()
        mutations = [dict(allow_loopback=False), dict(max_redirects=True), dict(timeout=float('inf')),
                     dict(max_seconds=0), dict(origins=[self.base+'/path']),
                     dict(origins=[self.base, self.base+'/']), dict(origins=['https://example.com'])]
        for change in mutations:
            with self.subTest(change=change), self.assertRaises(ValueError):
                ts02.validate_settings(dict(config, **change), data)
        data['access'] = 'public'
        with self.assertRaisesRegex(ValueError, 'Loopback'):
            ts02.validate_settings(config, data)
        self.assertEqual(self.server.hits, [])

    def test_cli_round_trip_and_reuse_refusal(self):
        self.files()
        def command(*args):
            return subprocess.run([sys.executable, str(ROOT/'collectors/ts02.py'), *map(str, args)],
                                  text=True, capture_output=True)
        r = command('prepare', self.root/'plan.json', '--settings', self.root/'settings.json', '--output', self.root/'request')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.approve()
        r = command('collect', self.root/'reviewed', '--output', self.root/'collection')
        self.assertEqual(r.returncode, 0, r.stderr); self.assertTrue(json.loads(r.stdout)['collected'])
        r = command('assess', self.root/'collection', '--output', self.root/'report')
        self.assertEqual(r.returncode, 0, r.stderr); self.assertTrue(json.loads(r.stdout)['assessed'])
        r = command('collect', self.root/'reviewed', '--output', self.root/'collection')
        self.assertEqual(r.returncode, 64); self.assertEqual(self.server.hits, ['/start', '/end'])


if __name__ == '__main__':
    unittest.main()
