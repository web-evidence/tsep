"""Bounded HTTP byte decoding. Apache-2.0. No network or lossy text conversion."""
import base64
import binascii
import hashlib
import re
import zlib

import tsep

MAX_WIRE_BYTES = 8 * 1024 * 1024
MAX_CONTENT_BYTES = 8 * 1024 * 1024
MAX_HEADER_BYTES = 64 * 1024


class Unknown(ValueError):
    pass


def need(condition, reason):
    if not condition:
        raise Unknown(reason)


def encoded(raw):
    """Input v2: exact bytes, canonical base64 and their independent fingerprint."""
    return {'base64': base64.b64encode(raw).decode('ascii'),
            'sha256': hashlib.sha256(raw).hexdigest()}


def raw_bytes(value):
    if isinstance(value, bytes):
        need(len(value) <= MAX_WIRE_BYTES, 'HTTP message exceeds byte bound')
        return value
    if isinstance(value, str):
        raw = value.encode('utf-8')
        need(len(raw) <= MAX_WIRE_BYTES, 'HTTP message exceeds byte bound')
        return raw
    need(isinstance(value, dict) and set(value) == {'base64', 'sha256'},
         'Expected raw UTF-8 text or input v2 base64/sha256 record')
    text = value['base64']
    need(isinstance(text, str) and len(text) <= 4*((MAX_WIRE_BYTES+2)//3), 'Encoded HTTP message exceeds bound')
    try:
        raw = base64.b64decode(text, validate=True)
    except (ValueError, binascii.Error) as error:
        raise Unknown('Invalid HTTP base64') from error
    need(len(raw) <= MAX_WIRE_BYTES and base64.b64encode(raw).decode('ascii') == text, 'Noncanonical or excessive HTTP base64')
    need(hashlib.sha256(raw).hexdigest() == value['sha256'], 'HTTP byte fingerprint mismatch')
    return raw


def text_body(value):
    if isinstance(value, str):
        return value
    try:
        return value.decode('utf-8')
    except (UnicodeDecodeError, AttributeError) as error:
        raise Unknown('Content is not valid UTF-8; no replacement decoding') from error


def body_digest(body):
    return hashlib.sha256(body.encode('utf-8') if isinstance(body, str) else body).hexdigest()


def unchunk(body):
    """Only transfer framing removed. Bytes may split inside any text sequence."""
    legacy = isinstance(body, str)
    wire = body.encode('utf-8') if legacy else body
    need(len(wire) <= MAX_WIRE_BYTES, 'Chunked body exceeds interpreter limit')
    offset, content = 0, bytearray()
    while True:
        end = wire.find(b'\r\n', offset)
        need(end != -1, 'Incomplete chunk-size line')
        line = wire[offset:end]
        need(re.fullmatch(b'[0-9A-Fa-f]{1,16}', line),
             'Malformed or unsupported chunk-size line (extensions not supported)')
        size = int(line, 16)
        offset = end + 2
        if size == 0:
            need(wire[offset:offset+2] == b'\r\n', 'Incomplete chunked ending or unsupported trailers')
            need(offset+2 == len(wire), 'Unexpected bytes after chunked ending')
            result = bytes(content)
            return text_body(result) if legacy else result
        need(size <= len(wire)-offset, 'Incomplete chunk data')
        need(wire[offset+size:offset+size+2] == b'\r\n', 'Missing chunk-data CRLF or incorrect byte size')
        content.extend(wire[offset:offset+size])
        offset += size+2


def decode_content(body, headers):
    values = headers.get('content-encoding', ['identity'])
    need(len(values) == 1 and values[0].lower() in ('identity', 'gzip', 'deflate'),
         'Unsupported or repeated Content-Encoding')
    coding = values[0].lower()
    if coding == 'identity':
        need(len(body) <= MAX_CONTENT_BYTES, 'Decoded content exceeds byte bound')
        return body
    try:
        decoder = zlib.decompressobj(16+zlib.MAX_WBITS if coding == 'gzip' else zlib.MAX_WBITS)
        content = decoder.decompress(body, MAX_CONTENT_BYTES+1)
    except zlib.error as error:
        raise Unknown('Invalid '+coding+' content stream') from error
    need(len(content) <= MAX_CONTENT_BYTES, 'Decoded content exceeds byte bound')
    need(decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail,
         'Incomplete content stream, trailing bytes or multiple gzip members')
    return content


def header_fields(raw):
    wire = raw_bytes(raw)
    need(b'\r\n\r\n' in wire, 'Missing raw HTTP header/body boundary')
    head, body = wire.split(b'\r\n\r\n', 1)
    need(len(head) <= MAX_HEADER_BYTES, 'HTTP headers exceed bound')
    lines = head.decode('utf-8' if isinstance(raw, str) else 'latin-1').split('\r\n')
    headers = {}
    for line in lines[1:]:
        need(re.fullmatch(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+:[^\r\n\x00-\x08\x0b\x0c\x0e-\x1f\x7f]*", line),
             'Unsupported HTTP header syntax')
        key, value = line.split(':', 1)
        headers.setdefault(key.lower(), []).append(value.strip(' \t'))
    return lines[0], headers, body


def message(raw, response=False):
    first, headers, body = header_fields(raw)
    legacy = isinstance(raw, str)
    if not response:
        return first, headers, text_body(body) if legacy else body
    match = re.fullmatch(r'HTTP/1\.[01] ([1-5][0-9]{2})(?: [^\r\n]*)?', first)
    need(match, 'Unsupported HTTP status line')
    if 'transfer-encoding' in headers:
        need(first.startswith('HTTP/1.1 '), 'Transfer-Encoding requires HTTP/1.1')
        need('content-length' not in headers, 'Ambiguous Transfer-Encoding with Content-Length')
        values = headers['transfer-encoding']
        need(len(values) == 1 and values[0].lower() == 'chunked', 'Unsupported or repeated Transfer-Encoding')
        body = unchunk(body)
    if 'content-length' in headers:
        values = headers['content-length']
        need(len(values) == 1 and re.fullmatch(r'[0-9]{1,16}', values[0])
             and int(values[0]) == len(body), 'Incomplete or ambiguous Content-Length')
    # Content-Length measures compressed content, before content decoding.
    body = decode_content(body, headers)
    return int(match[1]), headers, text_body(body) if legacy else body
