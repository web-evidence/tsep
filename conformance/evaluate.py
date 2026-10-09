#!/usr/bin/env python3
"""Bounded offline interpreter for four TSEP rules. Apache-2.0; no collection."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import urljoin, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tsep

RULES = ('TS01-A01', 'TS01-A02', 'TS07-A01', 'TS07-A02')


class Unknown(ValueError):
    pass


def need(condition, reason):
    if not condition:
        raise Unknown(reason)


def url_parts(url):
    parts = urlsplit(url)
    need(parts.scheme in ('http', 'https') and parts.hostname and not parts.fragment
         and not parts.username and not re.search(r'[\s\x00-\x1f]', url), 'Unsupported target URL')
    return parts


def message(raw, response=False):
    need(isinstance(raw, str) and '\r\n\r\n' in raw, 'Missing raw HTTP header/body boundary')
    head, body = raw.split('\r\n\r\n', 1)
    lines = head.split('\r\n')
    headers = {}
    for line in lines[1:]:
        need(re.fullmatch(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+:[^\r\n]*", line), 'Unsupported HTTP header syntax')
        key, value = line.split(':', 1)
        headers.setdefault(key.lower(), []).append(value.strip())
    if response:
        match = re.fullmatch(r'HTTP/1\.[01] ([1-5][0-9]{2})(?: [^\r\n]*)?', lines[0])
        need(match, 'Unsupported HTTP status line')
        need('transfer-encoding' not in headers and
             headers.get('content-encoding', ['identity']) == ['identity'], 'Encoded body not supported')
        if 'content-length' in headers:
            values = headers['content-length']
            need(len(values) == 1 and values[0].isdigit() and
                 int(values[0]) == len(body.encode('utf-8')), 'Incomplete or ambiguous Content-Length')
        return int(match[1]), headers, body
    return lines[0], headers, body


def trace(hops, start, crawler):
    need(isinstance(hops, list) and 0 < len(hops) <= 20, 'Missing or excessive HTTP hops')
    expected = start
    for number, hop in enumerate(hops):
        need(hop.get('complete') is True, 'Incomplete HTTP capture')
        need(hop.get('url') == expected, 'Missing or mismatched redirect hop')
        parts = url_parts(expected)
        first, request_headers, _ = message(hop.get('request'))
        request_path = (parts.path or '/') + ('?' + parts.query if parts.query else '')
        need(first == 'GET ' + request_path + ' HTTP/1.1', 'Unconditional GET capture required')
        need(request_headers.get('host') == [parts.netloc], 'Request Host differs from hop URL')
        need(request_headers.get('user-agent') == [crawler], 'Request crawler differs from intent')
        need(not any(k in request_headers for k in ('if-none-match', 'if-modified-since', 'range',
                                                     'authorization', 'cookie')), 'Unsupported conditional/authenticated request')
        status, headers, body = message(hop.get('response'), True)
        if status in (301, 302, 303, 307, 308):
            locations = headers.get('location', [])
            need(len(locations) == 1 and locations[0], 'Missing or ambiguous Location')
            expected = urljoin(expected, locations[0])
            need(number < len(hops) - 1, 'Unfinished redirect chain')
        else:
            need(number == len(hops) - 1, 'Unexpected hop after terminal response')
            need(status >= 200, 'Informational response without final response')
            need(status != 304, '304 without representation is inconclusive')
            return hop['url'], status, headers, body
    raise Unknown('No terminal response')


class Meta(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.directives = []
        self.stack = []
        self.roots = 0

    def handle_starttag(self, tag, attrs):
        # A browser parser or render is required for these stateful contexts.
        need(tag in ('html', 'head', 'body', 'title', 'meta', 'link', 'p', 'a', 'h1',
                     'div', 'span', 'script', 'style', 'br', 'img'), 'Unsupported HTML element/context')
        if tag == 'html':
            self.roots += 1
            need(not self.stack and self.roots == 1, 'Ambiguous HTML root')
        else:
            need(self.stack, 'Element outside HTML root')
        if tag not in ('meta', 'link', 'br', 'img'):
            self.stack.append(tag)
        if tag == 'meta':
            keys = [key for key, _ in attrs]
            need(len(keys) == len(set(keys)), 'Duplicate meta attributes')
            item = dict(attrs)
            need(item.get('name') is None or isinstance(item['name'], str), 'Invalid meta name')
            if (item.get('name') or '').lower() in ('robots', 'googlebot'):
                need(isinstance(item.get('content'), str), 'Missing robots meta content')
                self.directives.append(item['content'])

    def handle_endtag(self, tag):
        need(self.stack and self.stack[-1] == tag, 'HTML requires browser error recovery')
        self.stack.pop()

    def handle_data(self, data):
        need(not data.strip() or self.stack, 'Text outside HTML root')
        need('<' not in data or self.stack[-1] in ('script', 'style'), 'Unparsed HTML markup')


def directive_result(headers, body, intent):
    need(intent.get('crawler') == 'googlebot', 'Only the Googlebot directive series is implemented')
    need(intent.get('indexing') in ('allow', 'exclude'), 'Missing indexing intent')
    need(intent.get('following', 'unspecified') in ('allow', 'disallow', 'unspecified'), 'Unknown link intent')
    need('presentation' not in intent, 'Presentation restrictions require review')
    need(headers.get('content-type', []) == ['text/html; charset=utf-8'], 'Unsupported media type or encoding')
    need(bool(re.search(r'</html\s*>\s*$', body, re.I)), 'HTML end not captured')
    parser = Meta()
    parser.feed(body)
    parser.close()
    need(parser.roots == 1 and not parser.stack, 'Incomplete HTML structure')
    directives = list(parser.directives)
    for value in headers.get('x-robots-tag', []):
        # Only a leading, unambiguous crawler scope is supported.
        match = re.match(r'^([A-Za-z_-]+):\s*(.*)$', value)
        if match and match[1].lower() not in ('max-snippet', 'max-image-preview', 'max-video-preview', 'unavailable_after'):
            if match[1].lower() != 'googlebot':
                continue
            value = match[2]
        directives.append(value)
    tokens = set()
    for value in directives:
        for token in value.lower().split(','):
            token = token.strip()
            if not token:
                continue
            if re.fullmatch(r'max-(?:snippet|video-preview):\s*(?:-1|[0-9]+)', token) or re.fullmatch(r'max-image-preview:\s*(?:none|standard|large)', token):
                continue  # No presentation objective in this bounded input format.
            need(token in ('index', 'noindex', 'follow', 'nofollow', 'all', 'none', 'nosnippet'),
                 'Unsupported directive or scope: ' + token)
            tokens.add(token)
    excluded = bool(tokens & {'noindex', 'none'})
    restricted_links = bool(tokens & {'nofollow', 'none'})
    matches = excluded == (intent['indexing'] == 'exclude')
    if intent.get('following', 'unspecified') != 'unspecified':
        matches = matches and restricted_links == (intent['following'] == 'disallow')
    return ('pass' if matches else 'fail', 'Combined source directives compared with declared indexing/link intent; previews not assessed')


def robots_allowed(text, target, crawler):
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
    parts = url_parts(target)
    path = (parts.path or '/') + ('?' + parts.query if parts.query else '')
    need(path.isascii() and '%' not in path, 'Encoded/non-ASCII target path requires review')
    if parts.path == '/robots.txt':
        return True
    matches = [(len(value), field == 'allow') for group in selected for field, value in group
               if value and path.startswith(value)]
    return max(matches)[1] if matches else True


def evaluate_target(target, rule):
    try:
        intent = target.get('intent', {})
        need(intent.get('public_canonical') is True, 'Applicability not established for bounded URL population')
        context = target.get('context', {})
        need(all(context.get(k) for k in ('network', 'bounds', 'tool', 'tool_version')), 'Missing request context')
        need(tsep.timestamp(intent['declared_at']) <= tsep.timestamp(target['observed_at']), 'Intent postdates observation')
        crawler = intent.get('crawler')
        need(isinstance(crawler, str) and crawler, 'Missing crawler')
        final_url, status, headers, body = trace(target.get('http'), target['url'], crawler)
        if rule == 'TS01-A01':
            return ('pass' if status == 200 else 'fail', 'Final complete GET status: ' + str(status))
        if rule == 'TS01-A02':
            expected = intent.get('expected_body_sha256', '')
            need(isinstance(expected, str) and re.fullmatch('[a-f0-9]{64}', expected)
                 and isinstance(intent.get('expected_final_url'), str), 'Missing exact representation reference')
            url_parts(intent['expected_final_url'])
            actual = hashlib.sha256(body.encode('utf-8')).hexdigest()
            matches = actual == expected and final_url == intent['expected_final_url']
            return ('pass' if matches else 'fail', 'Exact final URL and decoded body SHA-256 comparison: ' + actual)
        if rule == 'TS07-A01':
            return directive_result(headers, body, intent)
        need(intent.get('access_basis') == 'test-client-only', 'Access assumptions not declared')
        parts = url_parts(final_url)
        robots_url = parts.scheme + '://' + parts.netloc + '/robots.txt'
        robots = target.get('robots', {})
        need(tsep.timestamp(robots['observed_at']) <= tsep.timestamp(target['observed_at']), 'Robots capture postdates assessment')
        _, robot_status, robot_headers, robot_body = trace(robots.get('http'), robots_url, crawler)
        need(robot_status == 200 and robot_headers.get('content-type') == ['text/plain; charset=utf-8'], 'Unsupported robots response; no default access inferred')
        allowed = robots_allowed(robot_body, final_url, crawler)
        if not allowed:
            return 'fail', 'Observed robots policy disallows this target crawler/path'
        if status in (401, 403):
            return 'fail', 'Observed HTTP access denial to test client'
        review = target.get('access_review', {})
        need(status == 200 and review.get('outcome') == 'no-obstacle' and review.get('reason'),
             'HTTP access unresolved or challenge not reviewed')
        need(tsep.timestamp(review['observed_at']) >= tsep.timestamp(target['observed_at']),
             'Access review predates the HTTP capture')
        return 'pass', 'Robots allows path and no obstacle observed for declared test client; actual engine access unobserved'
    except (Unknown, tsep.Invalid, KeyError, TypeError, ValueError) as error:
        return 'inconclusive', str(error)


def evaluate(data):
    tsep.require(data.get('input_version') == '1', 'Unsupported conformance input version')
    targets, rules = data.get('targets', []), data.get('rules', [])
    tsep.require(targets and rules and set(rules) <= set(RULES), 'Explicit nonempty targets and supported rules required')
    tsep.unique(rules, 'conformance rule')
    tsep.unique([t['url'] for t in targets], 'conformance target')
    results = []
    for target in targets:
        for rule in rules:
            outcome, reason = evaluate_target(target, rule)
            results.append({'rule_id': rule, 'target': target['url'], 'outcome': outcome, 'reason': reason})
    return results


if __name__ == '__main__':
    try:
        # Input is a single case's input object, never its expected outcomes.
        data = json.load(sys.stdin, object_pairs_hook=tsep.unique_object)
        print(json.dumps(evaluate(data), ensure_ascii=False))
    except (ValueError, TypeError, KeyError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(64)
