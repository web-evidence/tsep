"""Synthetic binary, compressed and adversarial HTTP inputs. Apache-2.0."""
import base64
import copy
import gzip
import hashlib
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from conformance.evaluate import evaluate
from conformance.http import Unknown, encoded, raw_bytes, message, body_digest

CASES = {c['id']: c for c in tsep.read_json(ROOT/'conformance/cases.json')['cases']}


def chunks(body, size=1):
    return b''.join(format(len(body[i:i+size]), 'x').encode()+b'\r\n'+body[i:i+size]+b'\r\n'
                    for i in range(0, len(body), size))+b'0\r\n\r\n'


def response(content, coding='identity', chunked=False, media='text/html; charset=utf-8'):
    payload = gzip.compress(content, mtime=0) if coding == 'gzip' else zlib.compress(content) if coding == 'deflate' else content
    header = 'HTTP/1.1 200 OK\r\nContent-Type: '+media+'\r\nContent-Encoding: '+coding+'\r\n'
    if chunked:
        return encoded((header+'Transfer-Encoding: chunked\r\n\r\n').encode()+chunks(payload))
    return encoded((header+'Content-Length: '+str(len(payload))+'\r\n\r\n').encode()+payload)


class BinaryHTTP(unittest.TestCase):
    def test_every_byte_and_utf8_split_roundtrip(self):
        for content in (bytes(range(256)), 'Vérification € 😀\r\n'.encode(), b'\x00\xff\xfe'):
            for coding in ('identity', 'gzip', 'deflate'):
                for chunked in (False, True):
                    with self.subTest(coding=coding, chunked=chunked):
                        original = response(content, coding, chunked)
                        status, headers, body = message(original, True)
                        self.assertEqual(status, 200)
                        self.assertEqual(body, content)
                        self.assertEqual(body_digest(body), hashlib.sha256(content).hexdigest())
                        self.assertEqual(encoded(raw_bytes(original)), original)

    def test_binary_fingerprint_and_encoding_errors_are_input_errors(self):
        data = copy.deepcopy(CASES['complete-reference']['input'])
        data['input_version'] = '2'
        hop = data['targets'][0]['http'][0]
        valid = encoded(hop['response'].encode())
        for bad in ({'base64':'@@', 'sha256':'0'*64}, dict(valid, sha256='0'*64),
                    dict(valid, base64=valid['base64']+'\n'), {'base64':'eA==', 'sha256':None},
                    dict(valid, extra='unrecognized')):
            hop['response'] = bad
            with self.subTest(value=bad), self.assertRaises(tsep.Invalid):
                evaluate(data)
        hop['response'] = valid
        data['input_version'] = '1'
        with self.assertRaises(tsep.Invalid):
            evaluate(data)

    def test_bounded_inflation_checksum_truncation_and_trailing_bytes(self):
        good = raw_bytes(response(b'a'*1000, 'gzip'))
        header, body = good.split(b'\r\n\r\n', 1)
        for payload in (body[:-1], body+b'extra', body+body, body[:-8]+b'\x00'*8):
            raw = b'HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\n\r\n'+payload
            with self.subTest(size=len(payload)), self.assertRaises(Unknown):
                message(encoded(raw), True)
        with patch('conformance.http.MAX_CONTENT_BYTES', 100), self.assertRaisesRegex(Unknown, 'bound'):
            message(encoded(good), True)
        for coding in ('br', 'gzip, deflate', 'gzip\r\nContent-Encoding: gzip'):
            with self.subTest(coding=coding), self.assertRaises(Unknown):
                message(encoded(b'HTTP/1.1 200 OK\r\nContent-Encoding: '+coding.encode()+b'\r\n\r\n'+body), True)
        raw_deflate = zlib.compress(b'text')[2:-4]
        with self.assertRaises(Unknown):
            message(encoded(b'HTTP/1.1 200 OK\r\nContent-Encoding: deflate\r\n\r\n'+raw_deflate), True)

    def test_binary_identity_does_not_require_text_decoding(self):
        data = copy.deepcopy(CASES['complete-reference']['input'])
        data['input_version'] = '2'; data['rules'] = ['TS01-A01', 'TS01-A02']
        target = data['targets'][0]
        body = b'<html><head></head><body>caf\xe9</body></html>'
        target['http'][-1]['response'] = response(body, 'gzip', True, 'text/html; charset=iso-8859-1')
        target['intent']['expected_body_sha256'] = hashlib.sha256(body).hexdigest()
        self.assertEqual([r['outcome'] for r in evaluate(data)], ['pass', 'pass'])
        target['intent']['expected_body_sha256'] = '0'*64
        target['intent'].pop('representation', None)
        target['intent']['required_markers'] = ['café']
        self.assertEqual(evaluate(data)[1]['outcome'], 'inconclusive')

    def test_selected_ts01_inputs_keep_outcomes_when_binary_encoded(self):
        def binary(value):
            if isinstance(value, dict):
                return {k: encoded(v.encode()) if k in ('request', 'response') and isinstance(v, str)
                        else binary(v) for k, v in value.items()}
            if isinstance(value, list):
                return [binary(v) for v in value]
            return value
        # HTTP-bound review digests stay bound to their original representation;
        # changing that representation is not silently authorized for TS07/TS10.
        for name in ('complete-reference', 'identity-stable-changed', 'identity-timestamp-markers',
                     'identity-forbidden-marker', 'identity-timestamp-no-markers', 'two-targets-must-stay-distinct'):
            data = copy.deepcopy(CASES[name]['input']); data['rules'] = ['TS01-A01', 'TS01-A02']
            converted = binary(data); converted['input_version'] = '2'
            with self.subTest(case=name):
                self.assertEqual(evaluate(converted), evaluate(data))


if __name__ == '__main__':
    unittest.main()
