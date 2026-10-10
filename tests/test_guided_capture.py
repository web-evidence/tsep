"""Real loopback HTTP, synthetic pages: full prospective workflow. Apache-2.0."""
import copy
import gzip
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import socket
import ssl
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from collectors.ts01 import reference, seal, evaluate, replay, capture, verify, validate_settings, origin, collection_sources, MAX_TOTAL
from conformance.http import raw_bytes
from tests.tls_fixture import CERTIFICATE, PUBLIC_TEST_KEY


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, *args):
        pass

    def do_GET(self):
        self.server.requests.append((self.path, dict(self.headers)))
        number = len(self.server.requests)
        if self.path == '/redirect':
            self.send_response(301)
            self.send_header('Location', '/stable')
            self.send_header('Content-Length', '0')
            self.end_headers(); self.close_connection = True
            return
        if self.path == '/outside':
            self.send_response(302)
            self.send_header('Location', 'http://127.0.0.2:1/never-fetched')
            self.send_header('Content-Length', '0')
            self.end_headers(); self.close_connection = True
            return
        marker = 'Mission TSEP' if self.server.marker else 'Autre ressource'
        value = str(number) if self.path == '/dynamic' else 'stable'
        content = ('<html><head><title>Test</title></head><body><p>'+marker+
                   '</p><p>Révision '+value+'</p></body></html>').encode()
        if self.path == '/unsupported':
            content = content.replace(b'</body>', b'<select><option>Other</option></select></body>')
        if self.path == '/large':
            content = b'x'*4096
        coding = 'identity' if self.path in ('/large', '/slow', '/cut') else 'deflate' if self.path == '/deflate' else 'gzip'
        body = gzip.compress(content, mtime=0) if coding == 'gzip' else zlib.compress(content) if coding == 'deflate' else content
        self.send_response(200)
        if self.server.media is not None:
            self.send_header('Content-Type', self.server.media)
        self.send_header('Content-Encoding', coding)
        self.send_header('Transfer-Encoding', 'chunked')
        self.end_headers()
        try:
            if self.path == '/slow':
                self.wfile.write(b'1\r\nx\r\n');self.wfile.flush();time.sleep(.4)
            for value in body:  # Splits multibyte text and arbitrary compressed bytes.
                self.wfile.write(b'1\r\n'+bytes([value])+b'\r\n')
            if self.path != '/cut':
                self.wfile.write(b'0\r\n\r\n')
        except (BrokenPipeError, ConnectionResetError):
            pass
        self.close_connection = True


class GuidedCapture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.server.daemon_threads = True
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = 'http://127.0.0.1:'+str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory();self.root = Path(self.temp.name)
        self.server.requests = [];self.server.marker = True
        self.server.media = 'text/html; charset=UTF-8'

    def tearDown(self):
        self.temp.cleanup()

    def settings(self, paths=('/dynamic',), **overrides):
        return dict({'urls': [self.base+p for p in paths], 'origins': [self.base],
                     'agent': 'TSEP-synthetic-test/1', 'accept_encoding': 'gzip, deflate',
                     'timeout': 2, 'max_bytes': 524288, 'max_redirects': 3, 'allow_loopback': True,
                     'network': 'Synthetic local HTTP server', 'selection_method': 'Declared synthetic paths only',
                     'access': 'synthetic'}, **overrides)

    def prepare(self, paths=('/dynamic',), policy='markers', **overrides):
        settings = self.settings(paths, **overrides)
        reference(settings, self.root/'first')
        criteria = {url: {'policy': 'markers', 'required_markers': ['Mission TSEP'],
                          'forbidden_markers': ['Maintenance']} for url in settings['urls']} if policy == 'markers' else None
        seal(self.root/'first/reference', self.root/'intent.json', assessor='Synthetic test author',
             label='Synthetic prospective TS01', policy=policy, criteria=criteria)
        return settings

    def test_changed_gzip_page_passes_markers_and_offline_replay_is_portable(self):
        self.prepare()
        result = evaluate(self.root/'first/reference', self.root/'intent.json', self.root/'assessment')
        self.assertEqual(result['counts']['C'], 1)
        data = tsep.read_json(self.root/'assessment/input.json')
        self.assertEqual(data['input_version'], '2')
        target = data['targets'][0]
        self.assertNotEqual(target['intent']['expected_body_sha256'], target['reference_candidate']['expected_body_sha256'])
        self.assertLessEqual(tsep.timestamp(target['intent']['declared_at']), tsep.timestamp(target['started_at']))
        atoms = tsep.read_json(self.root/'assessment/bundle/assessment.json')
        self.assertIn('Changed body satisfies', atoms[1]['reason'])
        self.assertTrue(all(headers['Accept-Encoding'] == 'gzip, deflate' for _, headers in self.server.requests))
        for hop in target['http']:
            self.assertIn(b'Content-Encoding: gzip', raw_bytes(hop['response']))
        html = (self.root/'assessment/report-fr.html').read_text()
        self.assertIn('TS01 · 1 cibles déclarées', html)
        self.assertIn('response-', html)
        self.assertIn('Couverture déclarée par l’outil', html)
        moved = self.root/'moved';shutil.copytree(self.root/'assessment', moved)
        shutil.rmtree(self.root/'assessment');shutil.rmtree(self.root/'first');(self.root/'intent.json').unlink()
        with patch('socket.socket', side_effect=AssertionError('Network forbidden')), \
                patch('socket.getaddrinfo', side_effect=AssertionError('DNS forbidden')):
            self.assertTrue(replay(moved, self.root/'replay')['replayed'])
        self.assertEqual(len(self.server.requests), 2)

    def test_changed_stable_body_fails_and_digest_only_remains_unknown(self):
        for policy, status in (('stable', 'NC'), ('digest', 'NT')):
            with self.subTest(policy=policy):
                self.prepare(policy=policy)
                result = evaluate(self.root/'first/reference', self.root/'intent.json', self.root/'assessment')
                self.assertEqual(result['counts'][status], 1)
                self.assertEqual(result['decision'], 'NO_GO')
                for name in ('first', 'assessment'):shutil.rmtree(self.root/name)
                (self.root/'intent.json').unlink()

    def test_runtime_difference_is_disclosed_without_claiming_identical_environment(self):
        self.prepare()
        evaluate(self.root/'first/reference', self.root/'intent.json', self.root/'assessment')
        runtime = tsep.read_json(self.root/'assessment/bundle/import.json')['runtime']
        runtime['build'] += ' (synthetic runtime difference)'
        with patch('adapters.captures.runtime_identity', return_value=runtime), \
                patch('socket.socket', side_effect=AssertionError('Network forbidden')):
            replay(self.root/'assessment', self.root/'replay')
        receipt = tsep.read_json(self.root/'replay/replay.json')
        self.assertFalse(receipt['same_recorded_runtime'])
        self.assertTrue(receipt['same_atomic_observations_and_gate'])
        self.assertTrue(receipt['same_interpreter_adapter_sources'])

    def test_missing_required_marker_is_failure_not_unknown(self):
        self.prepare();self.server.marker = False
        self.assertEqual(evaluate(self.root/'first/reference', self.root/'intent.json', self.root/'assessment')['counts']['NC'], 1)

    def test_reference_marker_contradiction_refuses_seal_without_second_request(self):
        settings = self.settings(('/stable',))
        reference(settings, self.root/'first')
        for required, forbidden in [(['Absent'], []), (['Mission TSEP'], ['Révision'])]:
            criteria = {settings['urls'][0]: {'policy': 'markers', 'required_markers': required, 'forbidden_markers': forbidden}}
            with self.subTest(required=required), self.assertRaisesRegex(ValueError, 'Reference marker contradiction'):
                seal(self.root/'first/reference', self.root/'intent.json', assessor='Test', label='Synthetic', criteria=criteria)
            self.assertFalse((self.root/'intent.json').exists())
        self.assertEqual(len(self.server.requests), 1)

    def test_unavailable_preflight_stays_visible_even_when_digest_resolves_identity(self):
        self.prepare(paths=('/unsupported',))
        intent = tsep.read_json(self.root/'intent.json')
        self.assertEqual(intent['intent_version'], '3')
        self.assertEqual(intent['targets'][0]['reference_preflight']['state'], 'unavailable')
        self.assertEqual(evaluate(self.root/'first/reference', self.root/'intent.json', self.root/'assessment')['counts']['C'], 1)
        html = (self.root/'assessment/report-fr.html').read_text()
        self.assertIn('Précontrôle des marqueurs', html)
        self.assertIn('Unsupported HTML context: select', html)
        self.assertIn('unavailable', html)

    def test_changed_media_is_disclosed_without_changing_the_normative_digest_result(self):
        self.prepare(paths=('/stable',))
        self.server.media = 'text/plain; charset=UTF-8'
        result = evaluate(self.root/'first/reference', self.root/'intent.json', self.root/'assessment')
        self.assertEqual(result['counts']['C'], 1)
        target = tsep.read_json(self.root/'assessment/input.json')['targets'][0]
        self.assertTrue(target['context']['media_comparison']['raw_headers_differ'])
        self.assertIn('Type de média observé', (self.root/'assessment/report-fr.html').read_text())

    def test_removed_content_type_is_an_observed_change_not_an_unavailable_capture(self):
        self.prepare(paths=('/stable',))
        self.server.media = None
        result = evaluate(self.root/'first/reference', self.root/'intent.json', self.root/'assessment')
        self.assertEqual(result['counts']['C'], 1)  # Complete-body digest priority remains normative.
        target = tsep.read_json(self.root/'assessment/input.json')['targets'][0]
        observed = target['context']['media_comparison']
        self.assertEqual(observed['evaluation'], [])
        self.assertTrue(observed['raw_headers_differ'])
        self.assertNotIn('unavailable_reason', observed)

    def test_changed_frozen_preflight_is_rejected_before_evaluation_network(self):
        self.prepare()
        intent = tsep.read_json(self.root/'intent.json')
        intent['targets'][0]['reference_preflight']['state'] = 'unavailable'
        (self.root/'tampered-intent.json').write_text(json.dumps(intent))
        with self.assertRaisesRegex(ValueError, 'Reference preflight differs'):
            evaluate(self.root/'first/reference', self.root/'tampered-intent.json', self.root/'assessment')
        self.assertEqual(len(self.server.requests), 1)
        self.assertFalse((self.root/'assessment').exists())

    def test_deflate_and_redirects_keep_each_raw_hop(self):
        self.prepare(paths=('/deflate', '/redirect'), policy='digest')
        result = evaluate(self.root/'first/reference', self.root/'intent.json', self.root/'assessment')
        self.assertEqual(result['counts']['C'], 1)
        data = tsep.read_json(self.root/'assessment/input.json')
        self.assertEqual(len(data['targets'][1]['http']), 2)
        verify(self.root/'assessment')

    def test_out_of_scope_redirect_and_collection_limits_are_retained(self):
        for path, overrides in (('/outside', {}), ('/redirect', {'max_redirects':0}),
                                ('/large', {'max_bytes':1024}), ('/slow', {'timeout':.1}), ('/cut', {})):
            with self.subTest(path=path):
                before = len(self.server.requests)
                out = self.root/path[1:]
                data = capture(self.settings((path,), **overrides), out)
                target = data['targets'][0]
                self.assertNotIn('reference_candidate', target)
                self.assertTrue(target.get('interpretation_limit'))
                self.assertEqual(len(self.server.requests), before+1)
                self.assertLessEqual(len(raw_bytes(target['http'][0]['response'])), overrides.get('max_bytes', 524288))
                verify(out)
                with self.assertRaises(ValueError):
                    seal(out, self.root/'invalid-intent.json', assessor='Test', label='Test')
                self.assertFalse((self.root/'invalid-intent.json').exists())

    def test_loopback_is_opt_in_and_invalid_targets_never_fetch(self):
        data = capture(self.settings(('/stable',), allow_loopback=False), self.root/'private')
        self.assertIn('Non-public destination', data['targets'][0]['http'][0]['error'])
        self.assertEqual(self.server.requests, [])
        for url in ('file:///tmp/file', 'http://u:p@example.com/', 'http://example.com/#part',
                    'http://example.com/\r\nX:a', 'http://é.example/', 'http://example.com\\@localhost/'):
            with self.subTest(url=url), self.assertRaises(ValueError):origin(url)
        with self.assertRaises(ValueError):validate_settings(self.settings(timeout=float('nan')))

    def test_reference_tampering_future_intent_and_changed_settings_stop_before_network(self):
        self.prepare(policy='digest')
        intent = tsep.read_json(self.root/'intent.json')
        for kind in ('future', 'settings', 'target'):
            altered = copy.deepcopy(intent)
            if kind == 'future':altered['declared_at'] = '2999-01-01T00:00:00Z'
            elif kind == 'settings':altered['settings']['agent'] = 'Changed'
            else:altered['targets'] = []
            (self.root/'changed.json').write_text(json.dumps(altered))
            with self.assertRaises(ValueError):evaluate(self.root/'first/reference', self.root/'changed.json', self.root/'invalid')
            self.assertFalse((self.root/'invalid').exists())
        self.assertEqual(len(self.server.requests), 1)
        (self.root/'first/reference/target-1-hop-1-response.bin').write_bytes(b'tampered')
        with self.assertRaises(ValueError):evaluate(self.root/'first/reference', self.root/'intent.json', self.root/'invalid')

    def test_cli_rejects_existing_destination_and_invalid_scope(self):
        result = subprocess.run([sys.executable, str(ROOT/'collectors/ts01.py'), 'reference', '--target', self.base+'/stable',
                                 '--output', str(self.root), '--network', 'loopback', '--selection-method', 'synthetic',
                                 '--access', 'synthetic', '--allow-loopback'], capture_output=True)
        self.assertEqual(result.returncode, 64)
        self.assertEqual(self.server.requests, [])

    def test_supervisor_timeout_retains_partial_bytes_without_issuing_a_verdict(self):
        prefix = b'HTTP/1.1 200 OK\r\nContent-Length: 9\r\n\r\ncut'
        def expired(*args, **kwargs):
            config = json.loads(kwargs['input'])
            (Path(config['directory'])/'response.bin').write_bytes(prefix)
            raise subprocess.TimeoutExpired(args[0], kwargs['timeout'])
        with patch('collectors.ts01.subprocess.run', side_effect=expired):
            result = capture(self.settings(('/stable',)), self.root/'timeout')
        target = result['targets'][0]
        self.assertEqual(raw_bytes(target['http'][0]['response']), prefix)
        self.assertFalse(target['http'][0]['complete'])
        self.assertIn('including DNS', target['http'][0]['error'])
        self.assertNotIn('reference_candidate', target)
        verify(self.root/'timeout')
        self.assertEqual(self.server.requests, [])

    def test_evaluation_connection_failure_yields_retained_unknown_report(self):
        self.prepare(paths=('/stable',), policy='digest')
        with patch('collectors.ts01.subprocess.run', side_effect=subprocess.TimeoutExpired('worker', 3)):
            result = evaluate(self.root/'first/reference', self.root/'intent.json', self.root/'failed')
        self.assertEqual(result['counts']['NT'], 1)
        self.assertEqual(result['decision'], 'NO_GO')
        verify(self.root/'failed')
        self.assertTrue(replay(self.root/'failed', self.root/'failed-replay')['replayed'])
        self.assertEqual(len(self.server.requests), 1)

    def test_changed_collector_is_blocked_before_output_and_network(self):
        self.prepare(paths=('/stable',), policy='digest')
        altered = dict(collection_sources(), **{'collectors/http.py': '0'*64})
        with patch('collectors.ts01.collection_sources', return_value=altered), \
                patch('collectors.ts01.subprocess.run', side_effect=AssertionError('No request allowed')):
            with self.assertRaisesRegex(ValueError, 'Collector sources differ'):
                evaluate(self.root/'first/reference', self.root/'intent.json', self.root/'invalid')
            with self.assertRaisesRegex(ValueError, 'Collector sources differ'):
                seal(self.root/'first/reference', self.root/'new-intent.json', assessor='Test', label='Test')
        self.assertFalse((self.root/'invalid').exists())
        self.assertFalse((self.root/'new-intent.json').exists())
        self.assertEqual(len(self.server.requests), 1)

    def test_sources_changed_during_capture_preserve_attempt_without_assessment(self):
        before = collection_sources()
        changed = dict(before, **{'collectors/http.py': '0'*64})
        with patch('collectors.ts01.collection_sources', side_effect=[before, changed]):
            with self.assertRaisesRegex(ValueError, 'changed during collection'):
                capture(self.settings(('/stable',)), self.root/'changed')
        verify(self.root/'changed')
        self.assertFalse(tsep.read_json(self.root/'changed/capture.json')['sources_unchanged_during_collection'])

    def test_declared_final_url_is_checked_and_shown_beside_identity_verdict(self):
        settings = self.settings(('/redirect',))
        reference(settings, self.root/'first')
        criteria = {self.base+'/redirect': {'expected_final_url': self.base+'/wrong'}}
        with self.assertRaisesRegex(ValueError, 'Declared final URL differs'):
            seal(self.root/'first/reference', self.root/'bad.json', assessor='Test', label='Test', criteria=criteria)
        self.assertFalse((self.root/'bad.json').exists())
        criteria[self.base+'/redirect']['expected_final_url'] = self.base+'/stable'
        seal(self.root/'first/reference', self.root/'intent.json', assessor='Test', label='Test', criteria=criteria)
        data = tsep.read_json(self.root/'intent.json')
        self.assertEqual(data['targets'][0]['identity_basis']['policy'], 'digest')
        evaluate(self.root/'first/reference', self.root/'intent.json', self.root/'assessment')
        html = (self.root/'assessment/report-fr.html').read_text()
        results = html.split('<section id="results">', 1)[1].split('<section id="captures">', 1)[0]
        self.assertIn('URL finale déclarée par l’opérateur', results)
        self.assertIn('digest —', results)
        self.assertIn('Marqueurs requis', results)
        self.assertIn('Collecteur identique', results)
        self.assertIn('L’absence d’autres essais', html)

    def test_invalid_tls_certificate_is_refused_before_http(self):
        cert, key = self.root/'cert.pem', self.root/'key.pem'
        cert.write_text(CERTIFICATE); key.write_text(PUBLIC_TEST_KEY)
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        server.requests = []; server.marker = True; server.daemon_threads = True
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert, key)
        server.socket = context.wrap_socket(server.socket, server_side=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            url = 'https://127.0.0.1:'+str(server.server_port)+'/stable'
            data = capture(self.settings(urls=[url], origins=[url]), self.root/'tls-rejected')
            hop = data['targets'][0]['http'][0]
            self.assertFalse(hop['complete'])
            self.assertIn('CERTIFICATE_VERIFY_FAILED', hop['error'])
            self.assertNotIn('tls_certificate_verified', hop)
            self.assertEqual(raw_bytes(hop['response']), b'')
            self.assertNotIn('reference_candidate', data['targets'][0])
            self.assertEqual(server.requests, [])
            verify(self.root/'tls-rejected')
        finally:
            server.shutdown();server.server_close();thread.join()

    def test_phase_total_stops_requests_and_keeps_two_phases_under_json_limit(self):
        def bounded_worker(*args, **kwargs):
            config = json.loads(kwargs['input']); folder = Path(config['directory'])
            prefix = b'HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\n\r\n'
            response = prefix + b'x'*(config['max_bytes']-len(prefix))
            (folder/'response.bin').write_bytes(response)
            (folder/'metadata.json').write_text(json.dumps({'complete':True}))
            return subprocess.CompletedProcess(args[0], 0, '', '')
        settings = self.settings(tuple('/'+str(i)+'x'*3500 for i in range(10)), max_bytes=1024*1024)
        with patch('collectors.ts01.subprocess.run', side_effect=bounded_worker) as worker:
            first = capture(settings, self.root/'first')
            second = capture(settings, self.root/'second')
        self.assertEqual(worker.call_count, 4)
        self.assertEqual(first['phase_response_bytes'], MAX_TOTAL)
        self.assertEqual(second['phase_response_bytes'], MAX_TOTAL)
        self.assertIn('Phase byte bound reached', first['targets'][2]['collection_error'])
        for prior, target in zip(first['targets'], second['targets']):
            target['reference'] = {'http': prior['http']}
            target['context'] = {'bounds': settings, 'source_files': second['source_files']}
        serialized = json.dumps({'input_version':'2', 'rules':['TS01-A01','TS01-A02'], 'targets':second['targets']}, indent=2).encode()
        self.assertLess(len(serialized), tsep.MAX_JSON_BYTES)


if __name__ == '__main__':
    unittest.main()
