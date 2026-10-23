#!/usr/bin/env python3
"""One anonymous HTTP/1.1 GET, supervised by ts01.py. Apache-2.0.

Direct sockets preserve application HTTP bytes after TLS. No cookies, proxy,
authentication, browser or HTTP/2. The parent bounds DNS/process time as well.
"""
from datetime import datetime, timezone
import ipaddress
import json
from pathlib import Path
import socket
import ssl
import sys
import time
from urllib.parse import urlsplit


def now():
    return datetime.now(timezone.utc).isoformat()


def request_bytes(url, agent, encoding):
    parts = urlsplit(url)
    return ('GET '+(parts.path or '/')+('?' + parts.query if parts.query else '')+
            ' HTTP/1.1\r\nHost: '+parts.netloc+'\r\nUser-Agent: '+agent+
            '\r\nAccept: */*\r\nAccept-Encoding: '+encoding+
            '\r\nConnection: close\r\n\r\n').encode('ascii')


def fetch(config):
    """Parent supplies an exclusive temporary directory and validated settings."""
    root = Path(config['directory'])
    request = request_bytes(config['url'], config['agent'], config['accept_encoding'])
    (root/'request.bin').write_bytes(request)
    info = {'started_at': now(), 'complete': False, 'bytes_received': 0}
    limit = time.monotonic()+config['timeout']
    sock = None
    with (root/'response.bin').open('xb') as output:
        try:
            parts = urlsplit(config['url'])
            addresses = socket.getaddrinfo(parts.hostname, parts.port or (443 if parts.scheme == 'https' else 80),
                                           type=socket.SOCK_STREAM)
            if not addresses:
                raise ValueError('DNS returned no address')
            # Validate every answer, then connect to a checked numeric address.
            for _, _, _, _, address in addresses:
                ip = ipaddress.ip_address(address[0])
                if not ip.is_global and not (config['allow_loopback'] and ip.is_loopback):
                    raise ValueError('Non-public destination refused')
            last = None
            for family, kind, proto, _, address in addresses:
                try:
                    sock = socket.socket(family, kind, proto)
                    sock.settimeout(max(.001, limit-time.monotonic()))
                    sock.connect(address)
                    break
                except OSError as error:
                    last = error
                    sock.close()
                    sock = None
            if sock is None:
                raise last or OSError('Connection failed')
            info['peer_address'] = sock.getpeername()[0]
            if parts.scheme == 'https':
                sock.settimeout(max(.001, limit-time.monotonic()))
                sock = ssl.create_default_context().wrap_socket(sock, server_hostname=parts.hostname)
                info['tls_version'] = sock.version()
                info['tls_certificate_verified'] = True
            sock.settimeout(max(.001, limit-time.monotonic()))
            sock.sendall(request)
            while True:
                remaining = limit-time.monotonic()
                if remaining <= 0:
                    raise TimeoutError('Request deadline reached')
                sock.settimeout(remaining)
                chunk = sock.recv(min(65536, config['max_bytes']-info['bytes_received']+1))
                if not chunk:
                    info['complete'] = True
                    break
                # Retain the bounded prefix, never silently treat it as complete.
                keep = chunk[:config['max_bytes']-info['bytes_received']]
                output.write(keep)
                output.flush()
                info['bytes_received'] += len(keep)
                if len(keep) != len(chunk):
                    info.update(stop_reason='response-byte-limit', response_limit=config['max_bytes'],
                                overflow_bytes=len(chunk)-len(keep))
                    raise ValueError('Response byte bound reached')
        except (OSError, ValueError) as error:
            info['error'] = type(error).__name__+': '+str(error)
        finally:
            if sock is not None:
                sock.close()
            info['finished_at'] = now()
    (root/'metadata.json').write_text(json.dumps(info, indent=2)+'\n')


if __name__ == '__main__':
    fetch(json.load(sys.stdin))
