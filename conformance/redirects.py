"""Bounded TS02 HTTP redirect-plan interpretation. Apache-2.0; no collection."""
import hashlib
import json
import re
from urllib.parse import urljoin, urlsplit

import tsep
from conformance.http import Unknown, need
from conformance import http

REDIRECTS = (301, 302, 303, 307, 308)
HEADER_READER = 'http-trajectory-headers-v1'


def chunk_prefix(body):
    """Reject contradictory chunk framing without claiming a complete body."""
    offset=0
    while True:
        end=body.find(b'\r\n',offset)
        if end<0:
            need(re.fullmatch(b'[0-9a-fA-F]{0,16}\\r?',body[offset:]), 'Malformed chunk-size prefix')
            return
        line=body[offset:end]
        need(re.fullmatch(b'[0-9a-fA-F]{1,16}',line), 'Unsupported chunk-size prefix')
        size=int(line,16);offset=end+2
        need(size>0, 'Complete chunk stream or unsupported trailers before collection limit')
        if len(body)<offset+size:return
        tail=body[offset+size:offset+size+2]
        need(b'\r\n'.startswith(tail),'Malformed chunk-data prefix')
        if len(tail)<2:return
        offset+=size+2


def header_exchange(hop, expected, target):
    from conformance.evaluate import exchange, request_attribution
    if hop.get('complete') is True:
        return exchange(hop,expected,target['intent']['crawler'])
    request_attribution(hop,expected,target['intent']['crawler'])
    raw=http.raw_bytes(hop.get('response'))
    collection=target['context'].get('collection',{})
    maximum=collection.get('settings',{}).get('max_bytes')
    limit=hop.get('response_limit')
    need(collection.get('version')=='2' and type(maximum) is int and
         type(limit) is int and 1024<=limit==maximum<=1024*1024 and
         hop.get('complete') is False and hop.get('stop_reason')=='response-byte-limit' and
         type(hop.get('overflow_bytes')) is int and hop['overflow_bytes']==1 and
         type(hop.get('bytes_received')) is int and hop['bytes_received']==len(raw)==limit,
         'No attributable collector byte-limit stop; incomplete response stays unknown')
    first,headers,body=http.header_fields(hop['response'])
    status=re.fullmatch(r'HTTP/1\.[01] ([1-5][0-9]{2})(?: [^\r\n]*)?',first)
    need(status,'Unsupported HTTP status line')
    if 'transfer-encoding' in headers:
        need(first.startswith('HTTP/1.1 ') and 'content-length' not in headers and
             len(headers['transfer-encoding'])==1 and headers['transfer-encoding'][0].lower()=='chunked',
             'Ambiguous or unsupported partial transfer framing')
        chunk_prefix(body)
    if 'content-length' in headers:
        values=headers['content-length']
        need(len(values)==1 and re.fullmatch(r'[0-9]{1,16}',values[0]) and int(values[0])>len(body),
             'Contradictory or ambiguous partial Content-Length')
    need(int(status[1]) not in (204,304) and int(status[1])>=200,'Partial body on bodyless response')
    return int(status[1]),headers,None


def present(value):
    return isinstance(value, str) and bool(value.strip())


def url(value):
    need(isinstance(value, str) and value and not re.search(r'[^\x21-\x7e]|[\\<>"#]', value),
         'URL hors portée : espaces, fragment, caractères non ASCII ou ambigus')
    need(not re.search(r'%(?![0-9a-fA-F]{2})', value), 'Échappement URL invalide')
    parsed = urlsplit(value)
    need(parsed.scheme in ('http', 'https') and parsed.hostname and parsed.username is None
         and parsed.password is None, 'URL HTTP(S) absolue sans identifiants requise')
    parsed.port  # Reject malformed ports; no network resolution.
    return value


def plan(target):
    intent = target.get('intent', {})
    context = target.get('context', {})
    need(all(present(context.get(k)) for k in ('network', 'bounds', 'tool', 'tool_version')),
         'Contexte de collecte manquant')
    need(tsep.timestamp(intent['declared_at']) <= tsep.timestamp(target['observed_at']),
         'Plan déclaré après la capture')
    need(present(intent.get('crawler')), 'Client HTTP non déclaré')
    value = intent.get('redirect_plan', {})
    need(value.get('mechanism') == 'http', 'Seules les redirections serveur HTTP sont couvertes')
    need(url(target['url']) == url(value.get('source_url')), 'Plan destiné à une autre URL source')
    url(value.get('expected_final_url'))
    lo, hi = value.get('min_redirects'), value.get('max_redirects')
    need(type(lo) is int and type(hi) is int and 0 <= lo <= hi <= 19,
         'Nombre de redirections autorisé absent ou hors borne 0–19')
    for field, allowed in (('redirect_statuses', set(REDIRECTS)),
                           ('terminal_statuses', set(range(200, 300)) | set(range(400, 600)))):
        values = value.get(field)
        need(isinstance(values, list) and values and all(type(s) is int and s in allowed for s in values)
             and len(values) == len(set(values)), 'Statuts autorisés invalides : '+field)
    return value


def review_binding(target):
    intent = {k: v for k, v in target['intent'].items() if k != 'redirect_review'}
    value = {'url': target['url'], 'intent': intent, 'context': target['context']}
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode('utf-8')).hexdigest()


def review(target):
    record = target['intent'].get('redirect_review', {})
    need(all(present(record.get(k)) for k in ('reviewer', 'reason', 'assistance'))
         and record.get('role') == 'responsible-owner', 'Validation motivée du responsable absente')
    need(record.get('provenance') in ('human', 'human-assisted', 'synthetic-exercise'),
         'Provenance de validation absente')
    need(record.get('plan_sha256') == review_binding(target), 'Validation non liée à ce plan et contexte')
    need(tsep.timestamp(target['intent']['declared_at']) <= tsep.timestamp(record['observed_at'])
         <= tsep.timestamp(target['observed_at']), 'Validation hors période préalable à la capture')
    need(record.get('outcome') in ('approved', 'rejected'), 'Décision du responsable non fournie')
    if record['outcome'] == 'rejected':
        return 'fail', 'Le responsable a explicitement rejeté le plan fourni'
    return 'pass', 'Validation préalable fournie et liée au plan ; identité et sincérité non authentifiées'


def trajectory(target, expected):
    from conformance.evaluate import exchange
    hops = target.get('http')
    need(isinstance(hops, list) and 0 < len(hops) <= 20, 'Trace absente ou au-delà de 20 échanges')
    destination = target['url']
    visited = set()
    count = 0
    reader=target['intent'].get('redirect_reader')
    need(reader in (None,HEADER_READER),'Unknown redirect reader; no fallback')
    partial=False
    for number, hop in enumerate(hops):
        url(destination)
        status, headers, _ = (header_exchange(hop,destination,target) if reader==HEADER_READER
                              else exchange(hop, destination, target['intent']['crawler']))
        partial=partial or hop.get('complete') is not True
        visited.add(destination)
        if status in REDIRECTS:
            count += 1
            # These contradictions need only the attributable prefix, not a later response.
            if status not in expected['redirect_statuses']:
                return 'fail', 'Type de redirection non autorisé : '+str(status)+' sur '+destination
            if count > expected['max_redirects']:
                return 'fail', 'Nombre de redirections supérieur au plan : '+str(count)+' > '+str(expected['max_redirects'])
            locations = headers.get('location', [])
            if not locations or locations == ['']:
                return 'fail', 'Redirection HTTP sans destination Location sur '+destination
            need(len(locations) == 1, 'Plusieurs Location : destination ambiguë')
            location = locations[0]
            need(not re.search(r'[^\x21-\x7e]|[\\<>"#]', location), 'Location hors portée ou ambiguë')
            destination = url(urljoin(destination, location))
            if destination in visited:
                return 'fail', 'Boucle démontrée : Location revient vers '+destination
            need(number < len(hops)-1, 'Chaîne inachevée : prochaine réponse absente, boucle non démontrée')
        else:
            need(status >= 200 and not 300 <= status < 400, 'Réponse terminale hors portée')
            if status not in expected['terminal_statuses']:
                return 'fail', 'Statut terminal non autorisé : '+str(status)
            if destination != expected['expected_final_url']:
                return 'fail', 'Destination finale incorrecte : '+destination+' ; attendue : '+expected['expected_final_url']
            if count < expected['min_redirects']:
                return 'fail', 'Nombre de redirections inférieur au plan : '+str(count)
            need(number == len(hops)-1, 'Échange supplémentaire après la réponse terminale')
            need('refresh' not in headers, 'Refresh HTTP présent : navigation complémentaire non couverte')
            return 'pass', str(count)+' redirection(s), destination et statut conformes au plan HTTP déclaré'+(
                ' ; en-têtes complets, corps arrêté à la borne de collecte et non évalué' if partial else '')
    raise Unknown('Aucune réponse terminale')


def assess(target, rule):
    try:
        expected = plan(target)
        if rule == 'TS02-A01':
            return review(target)
        need(rule == 'TS02-A02', 'Règle TS02 inconnue')
        return trajectory(target, expected)
    except (Unknown, tsep.Invalid, ValueError, TypeError, KeyError, AttributeError) as error:
        return 'inconclusive', str(error)
