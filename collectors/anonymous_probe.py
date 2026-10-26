#!/usr/bin/env python3
"""One anonymous GET. No response body or private header value is written to disk."""
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
import re
import socket
import ssl
import sys
import time
from urllib.parse import urljoin, urlsplit
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collectors.http import request_bytes
from conformance.public_probes import digest, origin, url
from conformance.http import message


def now(): return datetime.now(timezone.utc).isoformat()


def collect(plan, *, allow_loopback=False):
    p = url(plan['url'])
    if p.query: raise ValueError('Anonymous private-route probes refuse query parameters')
    if not re.fullmatch(r'[A-Za-z0-9 ./_-]{1,100}',plan['agent']): raise ValueError('Invalid agent')
    result = {'profile':'anonymous-http-redacted-v1','url':plan['url'],'agent':plan['agent'],
        'method':'GET','cookies':False,'credentials':False,'plan_sha256':digest(plan),
        'started_at':now(),'complete':False,'body_retained':False,'redirect_followed':False}
    deadline = time.monotonic()+5
    sock = None
    try:
        addresses = socket.getaddrinfo(p.hostname,p.port or (443 if p.scheme=='https' else 80),type=socket.SOCK_STREAM)
        if not addresses: raise ValueError('No DNS answer')
        for *_, address in addresses:
            ip = ipaddress.ip_address(address[0])
            if not ip.is_global and not (allow_loopback and ip.is_loopback): raise ValueError('Non-public destination refused')
        result['dns_addresses'] = sorted(set(a[4][0] for a in addresses))
        for family,kind,proto,_,address in addresses:
            try:
                sock=socket.socket(family,kind,proto);sock.settimeout(max(.001,deadline-time.monotonic()));sock.connect(address);break
            except OSError:
                sock.close();sock=None
        if sock is None: raise OSError('Connection unavailable')
        result['peer_address']=sock.getpeername()[0]
        if p.scheme=='https':
            sock=ssl.create_default_context().wrap_socket(sock,server_hostname=p.hostname)
            result['tls_verified']=True
        sock.sendall(request_bytes(plan['url'],plan['agent'],'identity'))
        raw=bytearray()
        while True:
            if time.monotonic()>=deadline: raise TimeoutError()
            sock.settimeout(max(.001,deadline-time.monotonic()))
            chunk=sock.recv(min(65536,2097153-len(raw)))
            if not chunk: break
            raw.extend(chunk)
            if len(raw)>2097152: raise ValueError('Response byte bound exceeded')
            if b'\r\n\r\n' not in raw and len(raw)>65536: raise ValueError('Header bound exceeded')
        raw=bytes(raw)
        status,headers,body=message(raw,response=True)
        split=raw.find(b'\r\n\r\n')
        if split<0 or split>65536: raise ValueError('Invalid header boundary')
        if isinstance(body,str):body=body.encode()
        schemes=[]
        for h in headers.get('www-authenticate',[]):
            match=re.match(r'^([A-Za-z][A-Za-z0-9_-]*)\s+.+',h)
            if match:schemes.append(match[1].lower())
        result.update(complete=True,status=status,body_bytes=len(body),body_sha256=hashlib.sha256(body).hexdigest(),
            response_sha256=hashlib.sha256(raw).hexdigest(),headers_sha256=hashlib.sha256(raw[:split+4]).hexdigest(),
            authentication_schemes=schemes)
        locations=headers.get('location',[])
        if len(locations)==1:
            location=urljoin(plan['url'],locations[0])
            # Only a digest is retained: Location may contain a private session token.
            result['location_sha256']=hashlib.sha256(location.encode()).hexdigest()
        # Discard all raw bytes, including error bodies and authentication realms.
    except (OSError,ValueError) as error:
        result['complete']=False;result['error_type']=type(error).__name__
    finally:
        if sock is not None:sock.close()
        result['finished_at']=now()
    return result


if __name__=='__main__':
    settings=json.load(sys.stdin)
    print(json.dumps(collect(settings['plan'],allow_loopback=settings.get('synthetic_loopback') is True)))
