"""Explicit, bounded HTTP Link canonical policy; offline and not an engine model.

Apache-2.0. RFC syntax/context and TSEP's literal destination policy are separate.
The fixed historical reader in canonical.py is intentionally not modified.
"""
import json
import ipaddress
import re
from urllib.parse import urlsplit

from conformance.http import Unknown, need
from conformance.canonical_attributes import GOOGLE_MODIFIERS, VERSION as ATTRIBUTE_VERSION

READER = 'http-link-context-v1'
VERSION = '1'
MAX_FIELDS = 100
MAX_LINKS = 1000
MAX_PARAMETERS = 100
MAX_BYTES = 65536
MAX_DIAGNOSTIC_BYTES = 1024 * 1024
TOKEN = re.compile(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+")
URI = re.compile(r'(?:(?P<scheme>[A-Za-z][A-Za-z0-9+.-]*):)?(?://(?P<authority>[^/?#]*))?'
                 r'(?P<path>[^?#]*)(?:\?(?P<query>[^#]*))?(?:#(?P<fragment>.*))?\Z')
PCHAR = r"(?:[A-Za-z0-9._~!$&'()*+,;=:@-]|%[0-9A-Fa-f]{2})"


class PopulationLimit(Unknown):
    pass


def uri_parts(value):
    need(isinstance(value, str) and len(value) <= 8192, 'Unsupported URI reference size/type')
    need(all(32 < ord(c) < 127 for c in value), 'Non-ASCII/whitespace URI reference')
    match = URI.fullmatch(value)
    need(match, 'Malformed URI reference')
    parts = match.groupdict()
    need(re.fullmatch('(?:'+PCHAR+'|/)*', parts['path']), 'Malformed URI path')
    for key in ('query', 'fragment'):
        need(parts[key] is None or re.fullmatch('(?:'+PCHAR+'|[/?])*', parts[key]),
             'Malformed URI '+key)
    authority = parts['authority']
    need(authority is None or re.fullmatch('(?:'+PCHAR+r'|[\[\]])*', authority),
         'Malformed URI authority')
    if authority is not None:
        try:
            parsed = urlsplit(value)
            parsed.port
            if '[' in authority or ']' in authority:
                need(authority.count('[') == authority.count(']') == 1 and
                     authority.startswith('['), 'Unsupported IP-literal authority')
                literal = authority[1:authority.index(']')]
                need('%' not in literal, 'Scoped IP literal needs review')
                ipaddress.IPv6Address(literal)
        except ValueError as error:
            raise Unknown('Unsupported URI authority: '+str(error)) from error
    if parts['scheme'] is None and authority is None:
        need(':' not in parts['path'].split('/')[0], 'Colon in relative first path segment')
    return parts


def remove_dots(path):
    output = ''
    while path:
        if path.startswith('../'): path = path[3:]
        elif path.startswith('./'): path = path[2:]
        elif path.startswith('/./'): path = path[2:]
        elif path == '/.': path = '/'
        elif path.startswith('/../') or path == '/..':
            path = path[3:] if path.startswith('/../') else '/'
            output = output.rsplit('/', 1)[0] if '/' in output else ''
        elif path in ('.', '..'): path = ''
        else:
            end = path.find('/', 1 if path.startswith('/') else 0)
            if end < 0: output += path; path = ''
            else: output += path[:end]; path = path[end:]
    return output


def resolve(reference, base):
    """RFC3986 component resolution; preserve empty query/fragment and double slash."""
    r, b = uri_parts(reference), uri_parts(base)
    need(b['scheme'] and b['authority'], 'Missing absolute resolution base')
    if r['scheme'] is not None:
        t = dict(r); t['path'] = remove_dots(r['path'])
    else:
        t = dict(r, scheme=b['scheme'])
        if r['authority'] is not None:
            t['path'] = remove_dots(r['path'])
        else:
            t['authority'] = b['authority']
            if not r['path']:
                t['path'] = b['path']
                t['query'] = b['query'] if r['query'] is None else r['query']
            elif r['path'].startswith('/'):
                t['path'] = remove_dots(r['path'])
            else:
                prefix = b['path'].rsplit('/', 1)[0]+'/' if '/' in b['path'] else '/'
                t['path'] = remove_dots(prefix+r['path'])
    return ((t['scheme']+':' if t['scheme'] is not None else '') +
            ('//'+t['authority'] if t['authority'] is not None else '') + t['path'] +
            ('?'+t['query'] if t['query'] is not None else '') +
            ('#'+t['fragment'] if t['fragment'] is not None else ''))


def context_relation(context, final):
    if context == final: return 'current'
    for value in (context, final):
        p = uri_parts(value)
        need(p['scheme'] in ('http', 'https') and p['authority'], 'Context outside HTTP(S) coverage')
        # Never call a potentially equivalent spelling a definitely foreign context.
        need(re.fullmatch(r'[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?', p['authority']) and
             '%' not in value and p['path'].startswith('/') and
             remove_dots(p['path']) == p['path'] and
             p['query'] != '' and p['fragment'] != '', 'Context spelling/equivalence needs review')
    return 'other'


def split_field(field):
    """Keep unambiguous completed items; do not recover inside a broken quoted/URI item."""
    need(isinstance(field, str), 'Invalid Link field type')
    quoted = angle = escaped = False
    start = 0
    for i, char in enumerate(field):
        if char != '\t' and not 32 <= ord(char) < 127:
            yield field[start:].strip(), 'Non-ASCII/control character in Link item'; return
        if escaped: escaped = False; continue
        if quoted:
            if char == '\\': escaped = True
            elif char == '"': quoted = False
        elif angle:
            if char == '>': angle = False
            elif char == '<':
                yield field[start:].strip(), 'Nested Link target'; return
        elif char == '"': quoted = True
        elif char == '<': angle = True
        elif char == '>':
            yield field[start:].strip(), 'Unmatched Link target delimiter'; return
        elif char == ',':
            if field[start:i].strip(): yield field[start:i].strip(), None
            start = i+1
    tail = field[start:].strip()
    if tail: yield tail, 'Unterminated Link item' if quoted or angle or escaped else None


def parse_item(raw):
    need(raw.startswith('<') and '>' in raw, 'Missing Link target delimiters')
    end = raw.index('>'); target = raw[1:end]; uri_parts(target)
    rest, params = raw[end+1:], []
    while rest.strip(' \t'):
        rest = rest.lstrip(' \t'); need(rest.startswith(';'), 'Malformed Link parameter separator')
        rest = rest[1:].lstrip(' \t'); m = TOKEN.match(rest)
        need(m, 'Malformed Link parameter name')
        name = m[0].lower(); rest = rest[m.end():].lstrip(' \t'); value = None
        if rest.startswith('='):
            rest = rest[1:].lstrip(' \t')
            if rest.startswith('"'):
                output, i, closed = [], 1, False
                while i < len(rest):
                    c = rest[i]; i += 1
                    if c == '"': closed = True; break
                    if c == '\\':
                        need(i < len(rest), 'Unterminated quoted pair'); c = rest[i]; i += 1
                    need(c == '\t' or 32 <= ord(c) < 127, 'Unsupported quoted character')
                    output.append(c)
                need(closed, 'Unterminated quoted parameter'); value = ''.join(output); rest = rest[i:]
            else:
                m = TOKEN.match(rest); need(m, 'Malformed Link parameter value')
                value = m[0]; rest = rest[m.end():]
        params.append({'name': name, 'value': value})
        need(len(params) <= MAX_PARAMETERS, 'Link parameter bound exceeded')
    return target, params


def classify(record, final, preferred):
    target, params = parse_item(record['raw'])
    record.update(target=target, parameters=params)
    rels = [p['value'] for p in params if p['name'] == 'rel']
    need(rels and isinstance(rels[0], str) and rels[0], 'Missing/empty first rel')
    tokens = re.split(' +', rels[0])
    need(all(t and (re.fullmatch(r'[A-Za-z][A-Za-z0-9.-]*', t) or
                   (uri_parts(t)['scheme'] is not None)) for t in tokens), 'Malformed relation list')
    record.update(relations=tokens, ignored_later_rel=rels[1:])
    if 'canonical' not in [t.lower() for t in tokens]:
        record['classification'] = 'other-relation'; return
    anchors = [p['value'] for p in params if p['name'] == 'anchor']
    need(len(anchors) <= 1 and (not anchors or isinstance(anchors[0], str)),
         'Repeated/valueless anchor needs review')
    context = resolve(anchors[0], final) if anchors else final
    record.update(context=context, context_basis='anchor' if anchors else 'final-get-200-url')
    relation = context_relation(context, final)
    if relation == 'other':
        record['classification'] = 'other-context'; return
    other = [p['name'] for p in params if p['name'] not in ('rel', 'anchor')]
    modifiers = [n for n in other if n in GOOGLE_MODIFIERS]
    need(not modifiers, 'Canonical modifiers need review: '+', '.join(modifiers))
    need(not other, 'Unsupported HTTP Link parameters: '+', '.join(other))
    # TSEP still requires an absolute, fragment-free literal preference. No URI normalization.
    record['classification'] = 'compatible' if target == preferred else 'conflict'
    record['criterion'] = 'TSEP absolute fragment-free literal destination, not generic URI validity'


def assess(headers, final, preferred, required, selection, *, document_url, source_sha256,
           observed_at, diagnostics=None):
    record = {'kind': 'http-canonical-observation', 'reader': selection, 'version': VERSION,
              'modifier_registry_version': ATTRIBUTE_VERSION, 'document_url': document_url,
              'final_url': final, 'observed_at': observed_at, 'source_http_sha256': source_sha256,
              'required_http_canonical': required, 'items': [], 'errors': [],
              'scope': 'Final attributable GET 200 only; intermediate hops retained in original evidence; no engine observation.'}
    try:
        need(selection == READER, 'Unsupported http_reader; no historical fallback')
        fields = headers.get('link', [])
        need(isinstance(fields, list) and len(fields) <= MAX_FIELDS and all(isinstance(f, str) for f in fields),
             'Invalid/excessive Link field population')
        need(sum(len(f.encode('utf-8')) for f in fields) <= MAX_BYTES, 'Link byte bound exceeded')
        record['fields'] = fields
        for field_index, field in enumerate(fields):
            try:
                for item_index, (raw, error) in enumerate(split_field(field)):
                    if len(record['items']) >= MAX_LINKS:
                        raise PopulationLimit('Link item bound exceeded')
                    item = dict(field_index=field_index, item_index=item_index, raw=raw)
                    record['items'].append(item)
                    try:
                        need(not error, error)
                        classify(item, final, preferred)
                    except Unknown as error:
                        item.update(classification='unknown', reason=str(error))
            except PopulationLimit:
                raise
            except Unknown as error:
                record['errors'].append(dict(field_index=field_index, reason=str(error)))
        counts = {kind: sum(x['classification'] == kind for x in record['items']) for kind in
                  ('compatible', 'conflict', 'unknown', 'other-context', 'other-relation')}
        record['counts'] = counts
        unknown = counts['unknown'] or record['errors']
        outcome = ('fail' if counts['conflict'] else 'inconclusive' if unknown else
                   'fail' if required and not counts['compatible'] else 'pass')
        record['outcome'] = outcome
        record['reason'] = READER+': '+json.dumps(counts, sort_keys=True)+'; '+(
            'Attributable contradiction retained' if counts['conflict'] else
            'Unresolved Link interpretation' if unknown else
            'Required HTTP canonical absent' if outcome == 'fail' else 'Declared final-response context examined')
        need(len(json.dumps(record, ensure_ascii=False, indent=2).encode()) <= MAX_DIAGNOSTIC_BYTES,
             'HTTP canonical diagnostic exceeds 1 MiB')
    except (Unknown, TypeError, ValueError) as error:
        # A population/diagnostic bound is a whole-reader refusal, never a partial failure.
        record = {k: v for k, v in record.items() if k not in ('items', 'fields', 'errors', 'counts')}
        record.update(outcome='inconclusive', reason=str(error))
    if diagnostics is not None: diagnostics.append(record)
    return record['outcome'], record['reason']
