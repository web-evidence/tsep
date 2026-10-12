"""Prefrozen policy differences, evidence attribution and conservative bounds. Apache-2.0."""
import copy
import hashlib
import itertools
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from conformance.http import encoded, Unknown
from experiments import robots_policy as robots

FIXTURES = ROOT/'tests/fixtures'
CASES = json.loads((FIXTURES/'robots-policy-v1-cases.json').read_text())['cases']
PROFILES = json.loads((FIXTURES/'robots-profiles-v1-cases.json').read_text())


def hop(url, status=200, body=b'User-agent: *\nDisallow: /private\n', headers=None):
    from urllib.parse import urlsplit
    p = urlsplit(url)
    request = ('GET '+(p.path or '/')+' HTTP/1.1\r\nHost: '+p.netloc+'\r\nUser-Agent: Googlebot\r\n\r\n').encode()
    response = ('HTTP/1.1 '+str(status)+' Test\r\nContent-Type: text/plain; charset=utf-8\r\n'+
                (headers or '')+'Content-Length: '+str(len(body))+'\r\n\r\n').encode()+body
    return {'url': url, 'complete': True, 'request': encoded(request), 'response': encoded(response)}


def capture():
    return {'profile': robots.GOOGLE, 'origin': 'https://example.com/',
            'target': 'https://example.com/private', 'product_token': 'Googlebot',
            'request_user_agent': 'Googlebot', 'declared_at': '2026-10-10T08:00:00Z',
            'observed_at': '2026-10-10T09:00:00Z',
            'context': {'network': 'synthetic', 'bounds': 'six exchanges', 'tool': 'fixture', 'tool_version': '1'},
            'http': [hop('https://example.com/robots.txt')]}


class RobotsPolicy(unittest.TestCase):
    def test_prefrozen_profiles(self):
        for filename, digest in [('robots-policy-v1-cases.json', '4a4c1af65d63a4341ee46507da33f50f5fc8f4542b905b5f659ed77cf03c46bf'),
                                 ('robots-profiles-v1-cases.json', '3eb75aa6f83f09ac27615e85b9a78920074edaf40a77ece60a1f4a47302113d1')]:
            self.assertEqual(hashlib.sha256((FIXTURES/filename).read_bytes()).hexdigest(), digest)
        self.assertEqual(len(CASES), 64)
        google = {r['id']: r['expected'] for r in PROFILES['google_profile']}
        for case in CASES:
            for profile, expected in [(robots.RFC, case['expected']), (robots.GOOGLE, google[case['id']])]:
                with self.subTest(case=case['id'], profile=profile):
                    result = robots.body_policy(case['body'], case['target'], case['product_token'], profile)
                    self.assertEqual(result['decision'], expected, result)

    def test_winning_lines_and_group_override_are_explained(self):
        body = 'User-agent: *\nDisallow: /\nUser-agent: Googlebot\nAllow: /assets/\nDisallow: /assets/\nAllow: /assets/main.css\n'
        value = robots.body_policy(body, 'https://example.com/assets/main.css', 'Googlebot', robots.GOOGLE)
        self.assertEqual(value['selected_groups'], [['googlebot']])
        self.assertEqual([(r['line'], r['field'], r['pattern']) for r in value['winning_lines']],
                         [(6, 'allow', '/assets/main.css')])

    def test_wildcard_algorithm_against_exhaustive_independent_small_language(self):
        # Reference enumerates every wildcard expansion via dynamic programming.
        # Independent from the production last-star algorithm; deliberately tiny.
        def reference(path, pattern):
            anchored = pattern.endswith('$')
            if anchored:
                pattern = pattern[:-1]
            positions = {0}
            for c in pattern:
                if c == '*':
                    positions = {j for i in positions for j in range(i, len(path)+1)}
                else:
                    positions = {i+1 for i in positions if i < len(path) and path[i] == c}
            return len(path) in positions if anchored else bool(positions)
        for n in range(5):
            for chars in itertools.product('ab*', repeat=n):
                for anchor in ('', '$'):
                    pattern = '/'+''.join(chars)+anchor
                    for m in range(5):
                        for suffix in itertools.product('ab', repeat=m):
                            path = '/'+''.join(suffix)
                            self.assertEqual(robots.matches(path, pattern, [1000]), reference(path, pattern), (path, pattern))

    def test_bounds_never_turn_missing_suffix_into_allow(self):
        for body in [b'\xff', b'#'+b'x'*robots.MAX_BYTES, b'\n'*robots.MAX_LINES,
                     ('User-agent: *\n'+'Disallow: /x\n'*(robots.MAX_RULES+1)).encode()]:
            result = robots.body_policy(body, 'https://example.com/', 'Googlebot', robots.GOOGLE)
            self.assertEqual(result['decision'], 'unknown')
            self.assertFalse(result['winning_lines'])
        body = b'User-agent: *\nDisallow: /\n#'
        body += b'x'*(robots.MAX_BYTES-len(body))
        self.assertEqual(robots.body_policy(body, 'https://example.com/', 'Googlebot', robots.GOOGLE)['decision'], 'disallow')
        with patch.object(robots.core, 'MAX_STEPS', 4):
            result = robots.body_policy('User-agent: *\nDisallow: /*z', 'https://example.com/abcdef', 'Googlebot', robots.GOOGLE)
            self.assertEqual(result['decision'], 'unknown')

    def test_http_statuses_and_no_cache_inference(self):
        for case in PROFILES['http_status_cases']:
            self.assertEqual(robots.google_status(case['status']), case['expected'])
            data = capture()
            data['http'] = [hop('https://example.com/robots.txt', case['status'], b'' if case['status'] == 204 else b'User-agent: *\nDisallow: /')]
            expected = {'parse': 'disallow', 'empty': 'allow', 'allow': 'allow', 'unknown': 'unknown'}[case['expected']]
            with self.subTest(status=case['status']):
                self.assertEqual(robots.inspect_capture(data)['decision'], expected)
        data['profile'] = robots.RFC
        data['http'] = [hop('https://example.com/robots.txt', 404)]
        self.assertEqual(robots.inspect_capture(data)['decision'], 'unknown')

    def test_initial_origin_retained_across_redirect_and_capture_bound(self):
        data = capture()
        data['http'] = [hop('https://example.com/robots.txt', 301, b'', 'Location: https://cdn.example/robots-data\r\n'),
                        hop('https://cdn.example/robots-data')]
        result = robots.inspect_capture(data)
        self.assertEqual(result['decision'], 'disallow')
        self.assertEqual(result['robots_url'], 'https://example.com/robots.txt')
        self.assertEqual(result['final_robots_url'], 'https://cdn.example/robots-data')
        data['http'].pop()
        self.assertEqual(robots.inspect_capture(data)['decision'], 'unknown')
        data['http'] *= 7
        self.assertEqual(robots.inspect_capture(data)['decision'], 'unknown')

    def test_wrong_origin_user_agent_hash_date_and_incomplete_response(self):
        good = capture()
        changes = [('target', 'http://example.com/private'), ('origin', 'https://example.com:8443/'),
                   ('request_user_agent', 'Bingbot'), ('product_token', '*'),
                   ('declared_at', '2026-10-11T00:00:00Z'), ('profile', 'unknown')]
        for field, value in changes:
            data = copy.deepcopy(good); data[field] = value
            with self.subTest(field=field):
                self.assertEqual(robots.inspect_capture(data)['decision'], 'unknown')
        data = copy.deepcopy(good); data['http'][0]['complete'] = False
        self.assertEqual(robots.inspect_capture(data)['decision'], 'unknown')
        data = copy.deepcopy(good); data['http'][0]['response']['sha256'] = '0'*64
        self.assertEqual(robots.inspect_capture(data)['decision'], 'unknown')

    def test_independent_of_network_and_active_protocol(self):
        with patch.object(socket, 'socket', side_effect=AssertionError('Network forbidden')):
            result = robots.inspect_capture(capture())
        self.assertEqual(result['decision'], 'disallow')
        self.assertEqual(result['network_requests'], 0)
        self.assertIn('TS04-A01', robots.evaluate.RULES)
        self.assertNotIn('status', result)
        self.assertEqual(json.loads((ROOT/'spec/protocol.json').read_text())['version'], '0.1.0-draft.29')

    def test_cli_preserves_input_hash_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source, output = root/'in.json', root/'out.json'
            source.write_text(json.dumps(capture()))
            args = [sys.executable, str(ROOT/'experiments/robots_policy.py'), str(source), '--output', str(output)]
            run = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            result = json.loads(output.read_text())
            self.assertEqual(result['input_sha256'], hashlib.sha256(source.read_bytes()).hexdigest())
            self.assertEqual(result['source_files']['experiments/robots_policy.py'], hashlib.sha256((ROOT/'experiments/robots_policy.py').read_bytes()).hexdigest())
            before = output.read_bytes()
            self.assertEqual(subprocess.run(args, capture_output=True).returncode, 64)
            self.assertEqual(output.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
