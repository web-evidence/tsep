"""Closed-profile loopback origin/cache used only by the TS39 laboratory.

Apache-2.0. Not a general HTTP cache. Requests, responses and actual state retained.
"""
import copy
from datetime import datetime, timezone
from email.utils import format_datetime, parsedate_to_datetime
import gzip
import hashlib
import json
from pathlib import Path
import re
import socket
import socketserver
import time
from urllib.parse import urlsplit

import tsep
from conformance.http import encoded, raw_bytes, message, header_fields

UA = 'TSEPDeliveryTest/1.0'


def now(): return datetime.now(timezone.utc).isoformat()
def compact(value): return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
def sha(value): return hashlib.sha256(value.encode() if isinstance(value, str) else value).hexdigest()


def loopback(base):
    tsep.require(isinstance(base, str) and re.fullmatch(r'http://127\.0\.0\.1:[1-9][0-9]{0,4}', base)
                 and 0 < urlsplit(base).port <= 65535, 'Only numeric loopback is permitted')
    return urlsplit(base)


def request(base, path, language, encoding):
    host = loopback(base).netloc
    tsep.require(path in ('/page', '/robots.txt') and language in (None, 'de')
                 and encoding in ('identity', 'gzip'), 'Outside closed request profile')
    fields = ['GET ' + path + ' HTTP/1.1', 'Host: ' + host, 'User-Agent: ' + UA]
    if language is not None: fields.append('Accept-Language: ' + language)
    fields.extend(['Accept-Encoding: ' + encoding, 'Connection: close', '', ''])
    return '\r\n'.join(fields).encode('ascii')


def request_values(raw, base):
    first, fields, body = message(raw)
    path = first.split(' ')[1] if len(first.split(' ')) == 3 else ''
    language = fields.get('accept-language', [None])[0]
    encoding = fields.get('accept-encoding', [''])[0]
    tsep.require(not body and raw == request(base, path, language, encoding),
                 'Received bytes differ from exact closed request profile')
    return path, language, encoding


def fetch(base, path, language=None, encoding='identity'):
    parts = loopback(base); raw_request = request(base, path, language, encoding)
    sent = now(); start = time.monotonic_ns(); pieces = []; size = 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.settimeout(3); client.connect(('127.0.0.1', parts.port))
        peer = client.getpeername()[0]; client.sendall(raw_request)
        while True:
            remaining = 3 - (time.monotonic_ns() - start) / 1e9
            tsep.require(remaining > 0, 'Response duration exceeds three seconds')
            client.settimeout(remaining); part = client.recv(4096)
            if not part: break
            size += len(part); tsep.require(size <= 32768, 'Response exceeds 32768 bytes')
            pieces.append(part)
    end = time.monotonic_ns(); received = now(); raw_response = b''.join(pieces)
    status, fields, _ = message(raw_response, True)
    tsep.require(status == 200 and fields.get('connection') == ['close'], 'Unexpected laboratory response')
    return {'url': base + path, 'complete': True, 'sent_at': sent, 'received_at': received,
            'start_mono_ns': start, 'end_mono_ns': end, 'peer_address': peer,
            'request': encoded(raw_request), 'response': encoded(raw_response)}


def representation(recipe, config, public_base, path, language, encoding):
    if path == '/robots.txt':
        return recipe['page']['robots'].encode(), 'fr', 'robots', None, False
    kind = config['representation']; expected_language = 'de' if language == 'de' else 'fr'
    actual_language = 'fr' if kind in ('bilingual', 'encoding') else expected_language
    marker = recipe['page']['bilingual' if kind == 'bilingual' else actual_language]
    canonical = public_base + ('/wrong' if kind == 'bad-canonical' else '/page')
    text = recipe['page']['prefix'].format(language=actual_language, canonical=canonical, marker=marker)
    compressed = kind == 'encoding' and encoding == 'gzip'
    content = text.encode('utf-8')
    wire = gzip.compress(content, mtime=0) if compressed else content
    vary = 'Accept-Encoding' if kind == 'encoding' else 'Accept-Language'
    return wire, actual_language, '"' + sha(wire) + '"', vary, compressed


def origin_response(recipe, config, public_base, path, language, encoding, at):
    body, actual_language, etag, vary, compressed = representation(recipe, config, public_base, path, language, encoding)
    fields = [('Content-Type', ('text/plain' if path == '/robots.txt' else 'text/html') + '; charset=utf-8'),
              ('Content-Length', str(len(body))), ('Date', format_datetime(tsep.timestamp(at), usegmt=True)),
              ('Cache-Control', 'no-store' if path == '/robots.txt' else 'public, max-age=300'),
              ('Content-Language', actual_language), ('ETag', etag)]
    if vary: fields.append(('Vary', vary))
    if compressed: fields.append(('Content-Encoding', 'gzip'))
    fields.append(('Connection', 'close'))
    return ('HTTP/1.1 200 OK\r\n' + ''.join(k + ': ' + v + '\r\n' for k, v in fields) + '\r\n').encode('ascii') + body


def wire_with_age(origin_wire, age):
    head, body = origin_wire.split(b'\r\n\r\n', 1)
    return head + b'\r\nAge: ' + str(age).encode('ascii') + b'\r\n\r\n' + body


def initial_age(exchange):
    _, fields, _ = message(exchange['response'], True)
    date = parsedate_to_datetime(fields['date'][0])
    apparent = max(0, int((tsep.timestamp(exchange['received_at']) - date).total_seconds() * 1e9))
    delay = exchange['end_mono_ns'] - exchange['start_mono_ns']
    tsep.require(delay >= 0, 'Negative measured origin delay')
    return max(apparent, delay)  # This closed origin supplies no upstream Age.


def selected_key(mode, public_base, path, language, encoding, vary):
    key = ['GET', public_base + path]
    if mode == 'honor':
        key.append([vary.lower(), encoding if vary == 'Accept-Encoding' else language])
    return key


def snapshot(entries):
    return [{'entry_id': e['entry_id'], 'key': copy.deepcopy(e['key']),
             'origin_response_sha256': e['origin']['response']['sha256'],
             'stored_request_sha256': e['stored_request']['sha256']} for e in entries]


class Server(socketserver.TCPServer):
    allow_reuse_address = True
    def handle_error(self, request, client_address):
        self.scope_error = self.scope_error or 'Server handler failed; partial records retained'


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        server = self.server; self.connection.settimeout(3); lines = []; length = 0
        try:
            while True:
                line = self.rfile.readline(4097)
                length += len(line)
                tsep.require(line and length <= 4096, 'Request exceeds closed profile byte limit')
                lines.append(line)
                if line == b'\r\n': break
            raw = b''.join(lines); at = now(); mono = time.monotonic_ns()
            path, language, encoding = request_values(raw, server.base)
            tsep.require(self.client_address[0] == '127.0.0.1', 'Non-loopback client')
            config = tsep.read_json(server.config_path)
            tsep.require(config == server.configurations[config['id']], 'Configuration differs from registration')
            tsep.require(len(server.records) < server.max_requests, 'Excessive laboratory requests')
            record = {'id': server.layer + '-' + str(len(server.records) + 1),
                      'phase': config['id'], 'at': at, 'mono_ns': mono, 'url': server.base + path,
                      'peer_address': self.client_address[0], 'request': encoded(raw),
                      'configuration_sha256': tsep.digest(server.config_path)}
            if server.layer == 'origin':
                response = origin_response(server.recipe, config, server.public_base, path, language, encoding, at)
            else:
                response, detail = serve(server, config, raw, path, language, encoding)
                record.update(detail)
            record['response'] = encoded(response); record['sent_at'] = now()
            server.records.append(record)
            self.wfile.write(response); self.wfile.flush()
        except Exception as error:
            server.scope_error = type(error).__name__ + ': ' + str(error)
            raise


def serve(server, config, raw_request, path, language, encoding):
    mode = config['mode']; entry = None
    for candidate in server.entries:
        key = selected_key(mode, server.base, path, language, encoding, candidate['vary'])
        if candidate['key'] == key and mode != 'bypass' and path != '/robots.txt':
            entry = candidate; break
    origin = None
    if entry is None:
        origin = fetch(server.origin_base, path, language, encoding)
        original = raw_bytes(origin['response'])
        if mode == 'bypass' or path == '/robots.txt':
            return original, {'action': 'bypass', 'origin_exchange': origin,
                              'entry_id': None, 'cache_event': None, 'cache_before': snapshot(server.entries),
                              'cache_after': snapshot(server.entries)}
        _, fields, _ = message(original, True)
        vary = fields['vary'][0]
        tsep.require(vary in ('Accept-Language', 'Accept-Encoding') and fields['cache-control'] == ['public, max-age=300'],
                     'Origin cache policy outside closed profile')
        server.entry_serial += 1
        entry = {'entry_id': 'entry-' + str(server.entry_serial),
                 'key': selected_key(mode, server.base, path, language, encoding, vary),
                 'vary': vary, 'origin': origin, 'stored_request': encoded(raw_request),
                 'initial_age_ns': initial_age(origin), 'stored_mono_ns': origin['end_mono_ns']}
        action = 'store'
    else:
        action = 'serve'
    before = snapshot(server.entries)
    if action == 'store': server.entries.append(entry)
    event_mono = time.monotonic_ns(); event_at = now()
    current_age = entry['initial_age_ns'] + event_mono - entry['stored_mono_ns']
    tsep.require(0 <= current_age < 300 * 10**9, 'Entry is not fresh under closed max-age=300 policy')
    response = wire_with_age(raw_bytes(entry['origin']['response']), current_age // 10**9)
    _, _, decoded = message(response, True)
    event = {'event_id': 'cache-' + str(len(server.records) + 1), 'kind': action,
             'entry_id': entry['entry_id'], 'layer': 'controlled-edge', 'at': event_at,
             'mono_ns': event_mono, 'request_sha256': sha(raw_request), 'response_sha256': sha(response),
             'body_sha256': sha(decoded), 'key': copy.deepcopy(entry['key']),
             'initial_age_ns': entry['initial_age_ns'], 'stored_mono_ns': entry['stored_mono_ns'],
             'current_age_ns': current_age, 'stored_request': entry['stored_request'],
             'origin_response': entry['origin']['response']}
    return response, {'action': action, 'origin_exchange': origin, 'entry_id': entry['entry_id'],
                      'cache_event': event, 'cache_before': before, 'cache_after': snapshot(server.entries)}


def set_configuration(server, origin, config, operations):
    before = snapshot(server.entries)
    previous = server.config_path.read_text() if server.config_path.exists() else None
    started = now()
    for target in (server, origin):
        tmp = target.config_path.with_suffix('.next')
        with tmp.open('x', encoding='utf-8') as handle: handle.write(compact(config) + '\n')
        tmp.replace(target.config_path)
    operations.append({'kind': 'configuration', 'phase': config['id'], 'started_at': started,
        'ended_at': now(), 'previous_raw': previous, 'new_raw': server.config_path.read_text(),
        'before': before, 'after': snapshot(server.entries)})


def purge(server, phase, reason, operations):
    before = snapshot(server.entries); started = now(); server.entries.clear()
    operations.append({'kind': 'purge', 'phase': phase, 'reason': reason,
                       'started_at': started, 'ended_at': now(), 'before': before, 'after': snapshot(server.entries)})
