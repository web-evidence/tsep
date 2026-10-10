#!/usr/bin/env python3
"""Shared bounded robots observations for TS04 and TS07. Apache-2.0.

Explicit body profiles, bounded matching and retained winning lines. No network,
cache simulation, Googlebot authentication or control-conformity verdict.
"""
import hashlib
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from conformance import evaluate, http
from conformance.http import Unknown, need

VERSION = '1'
RFC = 'rfc9309-bounded-v1'
GOOGLE = 'google-documented-core-v1'
MAX_BYTES = 500 * 1024
MAX_PATH = 8192
MAX_LINES = 20000
MAX_RULES = 5000
MAX_STEPS = 1000000
UNRESERVED = frozenset('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~')
LIMITATION = ('Observation of the supplied capture, not the version cached '
              'by a crawler, actual engine access, indexing, or a TS04/TS07 verdict.')


def address(value):
    need(isinstance(value, str) and 0 < len(value) <= MAX_PATH,
         'Missing URL or experimental URL length bound exceeded')
    need(not re.search(r'[\s\x00-\x1f\x7f\\#]', value), 'Ambiguous URL character')
    parts = urlsplit(value)
    need(parts.scheme in ('http', 'https') and parts.hostname and parts.hostname.isascii()
         and parts.username is None and parts.password is None, 'HTTP(S) URL without userinfo required')
    authority = (parts.scheme, parts.hostname.lower(), parts.port if parts.port is not None else
                 (443 if parts.scheme == 'https' else 80))
    path = parts.path or '/'
    if '?' in value:
        path += '?' + parts.query
    return authority, path


def normalized(value, profile):
    """Encode UTF-8 and normalize escapes without decoding reserved delimiters."""
    result = []
    i = 0
    while i < len(value):
        char = value[i]
        if char == '%':
            need(i+2 < len(value) and re.fullmatch('[0-9a-fA-F]{2}', value[i+1:i+3]),
                 'Invalid percent escape; interpretation not inferred')
            byte = int(value[i+1:i+3], 16)
            if chr(byte) in UNRESERVED:
                need(profile == RFC, 'Unreserved percent normalization outside Google subset')
                result.append(chr(byte))
            else:
                result.append('%%%02X' % byte)
            i += 3
        else:
            need(ord(char) >= 0x21 and ord(char) != 0x7f, 'Whitespace/control in path pattern')
            result.append(char if ord(char) < 128 else ''.join('%%%02X' % b for b in char.encode('utf-8')))
            i += 1
    output = ''.join(result)
    need(len(output) <= MAX_PATH, 'Normalized path/pattern exceeds experimental bound')
    return output


def matches(path, pattern, budget):
    """Glob prefix with a final optional anchor; one shared work budget per body."""
    anchored = pattern.endswith('$')
    if anchored:
        pattern = pattern[:-1]
    i = j = 0
    star = retry = -1
    while i < len(path):
        budget[0] -= 1
        need(budget[0] >= 0, 'Experimental matching work bound exceeded')
        if j == len(pattern) and not anchored:
            return True
        if j < len(pattern) and pattern[j] == '*':
            star, retry = j, i
            j += 1
        elif j < len(pattern) and pattern[j] == path[i]:
            i += 1
            j += 1
        elif star >= 0:
            retry += 1
            i, j = retry, star+1
        else:
            return False
    while j < len(pattern) and pattern[j] == '*':
        budget[0] -= 1
        need(budget[0] >= 0, 'Experimental matching work bound exceeded')
        j += 1
    return j == len(pattern)


def body_policy(body, target, product_token, profile):
    result = {'profile': profile, 'decision': 'unknown', 'winning_lines': [],
              'selected_groups': [], 'ignored_lines': [], 'limitation': LIMITATION}
    try:
        need(profile in (RFC, GOOGLE), 'Explicit supported body profile required')
        need(isinstance(product_token, str) and re.fullmatch('[A-Za-z_-]+', product_token),
             'Product token must be declared separately from HTTP User-Agent')
        _, path = address(target)
        path = normalized(path, profile)
        need(isinstance(body, (str, bytes)), 'Complete robots body required')
        raw = body.encode('utf-8') if isinstance(body, str) else body
        result['body_sha256'] = hashlib.sha256(raw).hexdigest()
        result['body_bytes'] = len(raw)
        need(len(raw) <= MAX_BYTES, 'Body exceeds 500 KiB experimental bound; no truncation inferred')
        text = raw.decode('utf-8-sig')
        need(not re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', text), 'Control byte in robots body')
        lines = re.split(r'\r\n|\r|\n', text)
        need(len(lines) <= MAX_LINES, 'Experimental line bound exceeded')
        groups, agents, rules = [], [], []
        seen_rule = False
        rule_count = 0
        for number, raw_line in enumerate(lines, 1):
            line = raw_line.split('#', 1)[0].strip(' \t')
            if not line:
                continue
            if ':' not in line:
                need(profile == RFC, 'Unrecognized line under Google subset at line '+str(number))
                result['ignored_lines'].append(number)
                continue
            field, value = (s.strip(' \t') for s in line.split(':', 1))
            field = field.lower()
            if field == 'user-agent':
                valid = bool(re.fullmatch('[A-Za-z_-]+|\\*', value))
                need(valid or profile == RFC, 'Ambiguous Google user-agent group at line '+str(number))
                if not valid:
                    result['ignored_lines'].append(number)
                    continue
                if seen_rule:
                    groups.append((agents, rules))
                    agents, rules, seen_rule = [], [], False
                agents.append(value.lower())
            elif field in ('allow', 'disallow'):
                # Even an empty valid rule delimits the preceding user-agent group.
                if not agents:
                    result['ignored_lines'].append(number)
                    continue
                if value and not value.startswith('/'):
                    need(profile == RFC, 'Non-rooted rule outside Google subset')
                    result['ignored_lines'].append(number)
                    continue
                seen_rule = True
                if not value:
                    continue
                rule_count += 1
                need(rule_count <= MAX_RULES, 'Experimental rule bound exceeded')
                rules.append({'line': number, 'field': field, 'pattern': value,
                              'normalized': normalized(value, profile)})
            else:
                need(profile == RFC or field in ('sitemap', 'crawl-delay', 'host'),
                     'Unknown directive/tolerance outside Google subset at line '+str(number))
                result['ignored_lines'].append(number)
        if agents:
            groups.append((agents, rules))
        specific = [(a, r) for a, r in groups if product_token.lower() in a]
        selected = specific if specific else [(a, r) for a, r in groups if '*' in a]
        result['selected_groups'] = [a for a, _ in selected]
        if path.split('?', 1)[0] == '/robots.txt':
            need(profile == RFC, 'Implicit /robots.txt allowance outside Google body subset')
            result.update(decision='allow', reason='RFC model implicit robots.txt allowance')
            return result
        matched, budget = [], [MAX_STEPS]
        for _, group in selected:
            for rule in group:
                pattern = rule['normalized']
                need(profile == RFC or not (rule['field'] == 'allow' and '/index.htm' in pattern),
                     'Google index.htm parser tolerance outside subset')
                if matches(path, pattern, budget):
                    matched.append(dict(rule, specificity=len(pattern)))
        if matched:
            score = max((r['specificity'], r['field'] == 'allow') for r in matched)
            result['winning_lines'] = [r for r in matched if (r['specificity'], r['field'] == 'allow') == score]
            result['decision'] = 'allow' if score[1] else 'disallow'
            result['reason'] = 'Longest normalized pattern; Allow wins equal specificity'
        else:
            result.update(decision='allow', reason='No matching rule in selected groups under declared profile')
        result['matching_steps'] = MAX_STEPS-budget[0]
    except (Unknown, UnicodeError, TypeError, ValueError) as error:
        result.update(decision='unknown', winning_lines=[], reason=str(error))
    return result


def google_status(status):
    if type(status) is not int:
        return 'unknown'
    if status == 200:
        return 'parse'
    if status == 204:
        return 'empty'
    if 400 <= status < 500 and status != 429:
        return 'allow'
    return 'unknown'


def inspect_capture(data):
    """One origin/target observation; deliberately not an atomic/control result."""
    result = {'reader_version': VERSION, 'decision': 'unknown', 'limitation': LIMITATION,
              'profile': data.get('profile'), 'target': data.get('target'),
              'network_requests': 0}
    try:
        profile = data['profile']
        need(profile in (RFC, GOOGLE), 'Explicit supported profile required')
        origin, origin_path = address(data['origin'])
        target_origin, _ = address(data['target'])
        need(origin == target_origin and origin_path == '/', 'Target must belong to declared origin')
        robots_url = data['origin'].rstrip('/')+'/robots.txt'
        ua, token = data['request_user_agent'], data['product_token']
        need(isinstance(ua, str) and isinstance(token, str) and token.lower() in ua.lower(),
             'Declared product token absent from HTTP User-Agent')
        need(tsep.timestamp(data['declared_at']) <= tsep.timestamp(data['observed_at']),
             'Intent postdates robots capture')
        need(all(isinstance(data['context'].get(k), str) and data['context'][k].strip()
                 for k in ('network', 'bounds', 'tool', 'tool_version')), 'Missing collection context')
        hops = data['http']
        need(isinstance(hops, list) and 0 < len(hops) <= 6,
             'Capture absent or beyond five redirects; crawler outcome not inferred')
        final_url, status, headers, body = evaluate.trace(hops, robots_url, ua)
        result.update(robots_url=robots_url, final_robots_url=final_url, http_status=status,
                      redirects=len(hops)-1, observed_at=data['observed_at'])
        result['trace_sha256'] = evaluate.binding_digest(hops)
        if profile == GOOGLE and google_status(status) == 'allow':
            result.update(decision='allow', reason='Observed 4xx except 429: no restrictions under documented Google status policy; cache not observed')
        else:
            need(status in (200, 204) and (profile == GOOGLE or status == 200),
                 'HTTP/cache history outside declared profile coverage')
            if status == 204:
                need(not body, '204 body must be empty')
            else:
                need(evaluate.utf8_media(headers, ('text/plain',), default_utf8=True),
                     'Only complete UTF-8 text/plain robots bodies covered')
            result['body_reading'] = body_policy(body, data['target'], token, profile)
            result.update(decision=result['body_reading']['decision'], reason=result['body_reading']['reason'])
    except (Unknown, tsep.Invalid, ValueError, TypeError, KeyError, AttributeError) as error:
        result.update(decision='unknown', reason=str(error))
    return result



def legacy_allowed(text, target, crawler):
    groups, agents, rules = [], [], []
    for raw in text.splitlines():
        line = raw.split('#', 1)[0].strip()
        if not line:
            continue
        need(':' in line, 'Unsupported robots line')
        field, value = (s.strip() for s in line.split(':', 1))
        field = field.lower()
        if field == 'sitemap':
            continue
        if field == 'user-agent':
            need(re.fullmatch(r'[A-Za-z_-]+|\*', value), 'Unsupported robots agent')
            if rules:
                groups.append((agents, rules)); agents, rules = [], []
            agents.append(value.lower())
        elif field in ('allow', 'disallow'):
            # Empty values do not restrict, but still delimit a group.
            need(not value or (value.startswith('/') and value.isascii() and
                 not re.search(r'[%*$\s]', value)), 'Unsupported robots path pattern')
            if agents:
                rules.append((field, value))
        else:
            raise Unknown('Unsupported robots extension: ' + field)
    if agents:
        groups.append((agents, rules))
    specific = [r for a, r in groups if crawler.lower() in a]
    selected = specific if specific else [r for a, r in groups if '*' in a]
    parts = evaluate.url_parts(target)
    path = (parts.path or '/') + ('?' + parts.query if parts.query else '')
    need(path.isascii() and '%' not in path, 'Encoded/non-ASCII target path requires review')
    if parts.path == '/robots.txt':
        return True
    matches = [(len(value), field == 'allow') for group in selected for field, value in group
               if value and path.startswith(value)]
    return max(matches)[1] if matches else True
