"""Registered diagnostic pairs: real byte changes without normative outcomes."""
import hashlib
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from conformance.http import encoded
from diagnostics.campaign import compare, render

ROOT = Path(__file__).resolve().parents[1]


class Campaign(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.urls = ['https://example.com/a', 'https://example.com/b']
        self.settings = {'urls': self.urls}
        self.reg = {'kind': 'diagnostic-registration', 'phases': 2, 'minimum_gap_seconds': 30,
                    'registered_at': '2026-10-10T00:00:00Z', 'settings': self.settings}
        self.save(self.root/'registration.json', self.reg)
        for name, start, end, content in [('a', '00:00:01', '00:00:02', 'First'), ('b', '00:01:01', '00:01:02', 'Second')]:
            root = self.root/name
            root.mkdir()
            targets = []
            for number, url in enumerate(self.urls, 1):
                body = ('<html><body><p>'+('Stable' if number == 1 else content)+'</p></body></html>').encode()
                request = ('GET /'+url[-1]+' HTTP/1.1\r\nHost: example.com\r\n\r\n').encode()
                response = b'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: '+str(len(body)).encode()+b'\r\n\r\n'+body
                for kind, raw in [('request', request), ('response', response)]:
                    (root/('target-'+str(number)+'-hop-1-'+kind+'.bin')).write_bytes(raw)
                targets.append({'url': url, 'observed_at': '2026-10-10T'+end+'Z', 'http': [{'url': url, 'complete': True, 'request': encoded(request), 'response': encoded(response)}]})
            data = {'settings': self.settings, 'collector_version': 'synthetic-test',
                    'source_files': {'synthetic.py': '0'*64}, 'sources_unchanged_during_collection': True,
                    'started_at': '2026-10-10T'+start+'Z', 'finished_at': '2026-10-10T'+end+'Z', 'targets': targets}
            self.save(root/'capture.json', data)
            self.manifest(root)

    def save(self, path, data):
        path.write_text(json.dumps(data)+'\n')

    def manifest(self, root):
        names = ['capture.json']+[f'target-{i}-hop-1-{kind}.bin' for i in (1, 2) for kind in ('request', 'response')]
        (root/'SHA256SUMS').write_text(''.join(hashlib.sha256((root/name).read_bytes()).hexdigest()+'  '+name+'\n' for name in names))

    def run_pair(self):
        return compare(self.root/'registration.json', self.root/'a', self.root/'b')

    def change_capture(self, mutate):
        path = self.root/'b/capture.json'
        data = json.loads(path.read_text())
        mutate(data)
        self.save(path, data)
        self.manifest(path.parent)

    def replace_response(self, raw):
        self.change_capture(lambda d: d['targets'][0]['http'][0].update(response=encoded(raw)))
        (self.root/'b/target-1-hop-1-response.bin').write_bytes(raw)
        self.manifest(self.root/'b')

    def test_compare_exact_decoded_bytes_without_network_or_rule_outcomes(self):
        with patch('socket.socket', side_effect=AssertionError('No network')):
            result = self.run_pair()
        self.assertEqual(result['counts'], {'changed': 1, 'unchanged': 1, 'unresolved': 0})
        self.assertEqual(result['changed_pages_with_complete_extraction'], 1)
        self.assertEqual(result['gap_seconds'], 59)
        self.assertNotIn('outcome', result)
        self.assertNotIn('decision', result)
        self.assertTrue(result['pages'][1]['second']['extraction']['available'])

    def test_incomplete_response_is_not_an_unchanged_body(self):
        self.change_capture(lambda data: data['targets'][0]['http'][0].update(complete=False))
        result = self.run_pair()
        self.assertEqual(result['counts'], {'changed': 1, 'unchanged': 0, 'unresolved': 1})
        self.assertIsNone(result['pages'][0]['media_headers_differ'])

    def test_changed_destination_or_error_status_not_counted_as_variable_page(self):
        self.change_capture(lambda data: data['targets'][0]['http'][0].update(url='https://example.com/elsewhere'))
        self.assertEqual(self.run_pair()['counts']['unresolved'], 1)
        self.change_capture(lambda data: data['targets'][0]['http'][0].update(url=self.urls[0]))
        raw = (self.root/'b/target-1-hop-1-response.bin').read_bytes().replace(b'200 OK', b'503 Unavailable')
        self.replace_response(raw)
        self.assertEqual(self.run_pair()['counts']['unresolved'], 1)

    def test_decoded_body_comparison_does_not_confuse_compression_with_content_change(self):
        original = (self.root/'b/target-1-hop-1-response.bin').read_bytes()
        body = original.split(b'\r\n\r\n', 1)[1]
        compressed = gzip.compress(body, mtime=7)
        response = b'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Encoding: gzip\r\nContent-Length: '+str(len(compressed)).encode()+b'\r\n\r\n'+compressed
        self.replace_response(response)
        self.assertEqual(self.run_pair()['pages'][0]['body_comparison'], 'unchanged')

    def test_missing_media_is_observed_but_extraction_is_unavailable(self):
        raw = (self.root/'b/target-1-hop-1-response.bin').read_bytes().replace(b'Content-Type: text/html; charset=utf-8\r\n', b'')
        self.replace_response(raw)
        page = self.run_pair()['pages'][0]
        self.assertEqual(page['body_comparison'], 'unchanged')
        self.assertTrue(page['media_headers_differ'])
        self.assertFalse(page['second']['extraction']['available'])

    def test_first_extraction_refusal_and_nonexhaustive_inventory_are_distinct(self):
        body = b'<html><body><noscript><img></noscript><select></select></body></html>'
        self.replace_response(b'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n'+body)
        page = self.run_pair()['pages'][0]
        self.assertEqual(page['body_comparison'], 'changed')
        current = page['second']
        self.assertFalse(current['inventory_exhaustive'])
        self.assertIn('noscript', current['extraction']['reason'])
        self.assertEqual({r['code'] for r in current['inventory']['candidate_limits']}, {'nonempty:noscript', 'context:select'})

    def test_registration_target_order_and_collector_identity_are_enforced(self):
        for mutate in [lambda d: d['targets'].reverse(),
                       lambda d: d.update(source_files={'other.py': '1'*64}),
                       lambda d: d.update(sources_unchanged_during_collection=False),
                       lambda d: d.update(collector_version='different')]:
            original = (self.root/'b/capture.json').read_bytes()
            self.change_capture(mutate)
            with self.assertRaises(ValueError): self.run_pair()
            (self.root/'b/capture.json').write_bytes(original)
            self.manifest(self.root/'b')

    def test_timestamp_registration_and_minimum_interval_are_enforced(self):
        for mutation in [{'registered_at': '2026-10-10T00:02:00Z'}, {'minimum_gap_seconds': 60},
                         {'registered_at': '2026-10-10T00:00:00'}, {'minimum_gap_seconds': float('nan')}]:
            self.save(self.root/'registration.json', dict(self.reg, **mutation))
            with self.assertRaises(ValueError): self.run_pair()

    def test_json_and_raw_sidecar_must_agree_even_after_manifest_recomputed(self):
        path = self.root/'b/target-1-hop-1-response.bin'
        path.write_bytes(path.read_bytes()+b'x')
        self.manifest(path.parent)
        with self.assertRaisesRegex(ValueError, 'sidecar mismatch'): self.run_pair()

    def test_manifest_tampering_and_path_escape_are_rejected(self):
        path = self.root/'b/SHA256SUMS'
        path.write_text('0'*64+'  ../outside\n')
        with self.assertRaisesRegex(ValueError, 'Unsafe'): self.run_pair()

    def test_render_is_inert_and_never_embeds_raw_captured_body(self):
        result = self.run_pair()
        result['pages'][0]['url'] = '<script>alert(1)</script>'
        for lang in ('fr', 'en'):
            html = render(result, lang)
            self.assertNotIn('<script>', html)
            self.assertIn('&lt;script&gt;', html)
            self.assertNotIn('<p>First</p>', html)
            self.assertIn('Content-Security-Policy', html)

    def test_cli_works_without_the_rule_evaluator_or_collector(self):
        tools = self.root/'tools'
        files = ['diagnostics/campaign.py','diagnostics/coverage.py','conformance/source_text.py',
                 'conformance/http.py','provenance/runtime.py','tsep.py']
        for name in files:
            path = tools/name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/name, path)
        result = subprocess.run([sys.executable, '-I', str(tools/'diagnostics/campaign.py'),
                                 str(self.root/'registration.json'), str(self.root/'a'), str(self.root/'b'),
                                 '--output-dir', str(self.root/'output')], capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['counts']['changed'], 1)
        self.assertFalse((tools/'conformance/evaluate.py').exists())


if __name__ == '__main__': unittest.main()
