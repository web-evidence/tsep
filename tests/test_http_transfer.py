"""HTTP transfer coverage without changing content identity. Synthetic, Apache-2.0."""
import copy
import hashlib
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from conformance.evaluate import Unknown, evaluate, message

CASES = {c['id']: c for c in tsep.read_json(ROOT/'conformance/cases.json')['cases']}


def chunked(content, width=7):
    # Cut on Unicode boundaries because input v1 requires a UTF-8 raw message.
    chunks = [content[i:i + width] for i in range(0, len(content), width)]
    return ''.join(format(len(c.encode('utf-8')), 'x') + '\r\n' + c + '\r\n'
                   for c in chunks) + '0\r\n\r\n'


class HTTPTransfer(unittest.TestCase):
    def response(self, body, extra=''):
        return 'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n' + extra + '\r\n' + body

    def test_framing_changes_neither_content_bytes_nor_digest(self):
        content = 'Une réponse à vérifier.\r\n\n0\r\n\r\n<article>é</article>\n'
        for width in (1, 7, 8192):
            with self.subTest(width=width):
                original = self.response(chunked(content, width))
                status, headers, decoded = message(original, True)
                self.assertEqual(status, 200)
                self.assertEqual(decoded.encode(), content.encode())
                self.assertEqual(hashlib.sha256(decoded.encode()).digest(), hashlib.sha256(content.encode()).digest())
                self.assertEqual(headers['transfer-encoding'], ['chunked'])
                self.assertEqual(original, self.response(chunked(content, width)))

    def test_repeated_non_framing_headers_are_preserved(self):
        response = self.response(chunked('é'), 'X-Robots-Tag: noindex\r\nX-Robots-Tag: nofollow\r\n')
        self.assertEqual(message(response, True)[1]['x-robots-tag'], ['noindex', 'nofollow'])

    def test_zero_body_hex_case_and_transfer_token_case(self):
        self.assertEqual(message(self.response('000\r\n\r\n'), True)[2], '')
        self.assertEqual(message(self.response('A\r\n0123456789\r\n0\r\n\r\n').replace('chunked', 'CHUNKED'), True)[2], '0123456789')

    def test_incomplete_ambiguous_and_unsupported_messages_never_pass(self):
        for body in ('', '1', '1\r\n', '2\r\na', '1\r\na0\r\n\r\n',
                     '1\r\na\r\n', '0\r\n', '0\r\n\r\nextra', 'z\r\nx\r\n0\r\n\r\n',
                     '-1\r\nx\r\n0\r\n\r\n', ' 1\r\nx\r\n0\r\n\r\n',
                     '1;name=value\r\nx\r\n0\r\n\r\n',
                     '1\r\nx\r\n0\r\nX-Robots-Tag: noindex\r\n\r\n',
                     '1\r\né\r\n0\r\n\r\n', 'f'*1000 + '\r\nx\r\n0\r\n\r\n'):
            with self.subTest(body=body[:100]), self.assertRaises(Unknown):
                message(self.response(body), True)
        for header in ('Content-Length: 1\r\n', 'Transfer-Encoding: chunked\r\n',
                       'Content-Encoding: gzip\r\n', 'Content-Encoding: br\r\n'):
            with self.subTest(header=header), self.assertRaises(Unknown):
                message(self.response(chunked('x'), header), True)
        for coding in ('gzip, chunked', 'chunked, chunked', 'identity', 'chunked;foo=bar'):
            with self.subTest(coding=coding), self.assertRaises(Unknown):
                message(self.response(chunked('x')).replace('chunked\r\n', coding + '\r\n', 1), True)
        with self.assertRaises(Unknown):
            message(self.response(chunked('x')).replace('HTTP/1.1', 'HTTP/1.0'), True)

    def test_chunking_preserves_pass_fail_and_inconclusive_semantics(self):
        for name in ('complete-reference', 'identity-stable-changed', 'identity-timestamp-no-markers',
                     'identity-timestamp-markers', 'identity-forbidden-marker', 'two-targets-must-stay-distinct'):
            with self.subTest(case=name):
                data = copy.deepcopy(CASES[name]['input'])
                data['rules'] = ['TS01-A01', 'TS01-A02']
                before = evaluate(data)
                for target in data['targets']:
                    for hop in target['http']:
                        head, content = hop['response'].split('\r\n\r\n', 1)
                        lines = [line for line in head.split('\r\n') if not line.lower().startswith('content-length:')]
                        hop['response'] = '\r\n'.join(lines) + '\r\nTransfer-Encoding: chunked\r\n\r\n' + chunked(content)
                self.assertEqual(evaluate(data), before)
                data['targets'][0]['http'][-1]['response'] = data['targets'][0]['http'][-1]['response'][:-2]
                self.assertTrue(all(row['outcome'] == 'inconclusive' for row in evaluate(data)[:2]))


if __name__ == '__main__':
    unittest.main()
