#!/usr/bin/env python3
"""Bounded offline interpreter for thirteen TSEP rules. Apache-2.0; no collection."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import urljoin, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tsep

RULES = ('TS01-A01', 'TS01-A02', 'TS02-A01', 'TS02-A02', 'TS04-A01', 'TS04-A02', 'TS07-A01', 'TS07-A02', 'TS07-A03',
         'TS10-A01', 'TS10-A02', 'TS10-A03', 'TS10-A04')
VERSION = '11'  # Interpreter coverage version; normative protocol version is separate.


from conformance.http import Unknown, need, message, unchunk, text_body, body_digest, raw_bytes


def media_type(headers):
    """Parse one unambiguous Content-Type; only charset values are case-folded."""
    values = headers.get('content-type', [])
    need(len(values) == 1, 'Missing or repeated Content-Type')
    token = r"[!#$%&'*+.^_`|~0-9A-Za-z-]+"
    match = re.match(r'^(' + token + '/' + token + r')[ \t]*', values[0])
    need(match, 'Malformed Content-Type')
    kind, rest, params = match[1].lower(), values[0][match.end():], {}
    parameter = re.compile(r';[ \t]*(' + token + r')=(?:(' + token + r')|"((?:[^"\\\r\n]|\\[\t\x20-\x7e])*)")[ \t]*')
    while rest:
        match = parameter.match(rest)
        need(match, 'Malformed Content-Type parameter')
        key = match[1].lower()
        need(key not in params, 'Repeated Content-Type parameter')
        value = match[2] if match[2] is not None else re.sub(r'\\(.)', r'\1', match[3])
        params[key] = value.lower() if key == 'charset' else value
        rest = rest[match.end():]
    return kind, params


def utf8_media(headers, kinds, default_utf8=False):
    kind, params = media_type(headers)
    return kind in kinds and params.get('charset', 'utf-8' if default_utf8 else None) == 'utf-8'


def identity_result(final_url, headers, body, intent):
    expected_url = intent.get('expected_final_url')
    need(isinstance(expected_url, str), 'Missing reference URL')
    url_parts(expected_url)
    if final_url != expected_url:
        return 'fail', 'Final URL differs from declared reference URL'
    expected = intent.get('expected_body_sha256', '')
    need(isinstance(expected, str) and re.fullmatch('[a-f0-9]{64}', expected), 'Missing reference body SHA-256')
    actual = body_digest(body)
    if actual == expected:
        return 'pass', 'Final URL and complete body SHA-256 match: ' + actual
    if intent.get('representation') == 'stable':
        return 'fail', 'Declared stable representation changed: ' + actual
    need('representation' not in intent, 'Unsupported representation policy')
    required, forbidden = intent.get('required_markers', []), intent.get('forbidden_markers', [])
    for markers in (required, forbidden):
        need(isinstance(markers, list) and all(text_present(m) for m in markers)
             and len(markers) == len(set(markers)), 'Malformed identity markers')
    need(not any(bad in good for good in required for bad in forbidden), 'Contradictory identity markers')
    need(required or forbidden, 'Body digest changed without stable policy or identity markers')
    segments = identity_text(headers, body)
    missing = [m for m in required if not any(m in text for text in segments)]
    present = [m for m in forbidden if any(m in text for text in segments)]
    if missing or present:
        return 'fail', 'Identity marker contradiction: ' + json.dumps({'missing': missing, 'forbidden': present}, ensure_ascii=False)
    need(required, 'Forbidden markers absent, but no required identity marker establishes identity')
    return 'pass', 'Changed body satisfies required and forbidden markers in extracted source text: ' + actual


def url_parts(url):
    parts = urlsplit(url)
    need(parts.scheme in ('http', 'https') and parts.hostname and not parts.fragment
         and not parts.username and not re.search(r'[\s\x00-\x1f]', url), 'Unsupported target URL')
    return parts



def exchange(hop, expected, crawler):
    """Validate one attributable exchange, including an unfinished redirect."""
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
    return status, headers, body


def trace(hops, start, crawler):
    need(isinstance(hops, list) and 0 < len(hops) <= 20, 'Missing or excessive HTTP hops')
    expected = start
    for number, hop in enumerate(hops):
        status, headers, body = exchange(hop, expected, crawler)
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



def identity_text(headers, body):
    body = text_body(body)
    kind, params = media_type(headers)
    need(params.get('charset') == 'utf-8', 'Identity markers require explicit UTF-8')
    if kind == 'text/plain':
        return [body]
    need(kind == 'text/html', 'Unsupported identity marker media type')
    need(bool(re.search(r'</html\s*>\s*$', body, re.I)), 'HTML end not captured')
    from conformance.source_text import extract
    return extract(body)


def directive_result(headers, body, intent):
    body = text_body(body)
    need(intent.get('directive_crawler', intent.get('crawler')) == 'googlebot',
         'Only the Googlebot directive series is implemented')
    need(intent.get('indexing') in ('allow', 'exclude'), 'Missing indexing intent')
    need(intent.get('following', 'unspecified') in ('allow', 'disallow', 'unspecified'), 'Unknown link intent')
    need('presentation' not in intent, 'Presentation restrictions require review')
    need(utf8_media(headers, ('text/html',)), 'Unsupported media type or encoding')
    need(bool(re.search(r'</html\s*>\s*$', body, re.I)), 'HTML end not captured')
    parser = Meta()
    parser.feed(body)
    parser.close()
    need(parser.roots == 1 and not parser.stack, 'Incomplete HTML structure')
    return directive_values(headers, parser.directives, intent)


def directive_values(headers, values, intent):
    need(intent.get('directive_crawler', intent.get('crawler')) == 'googlebot',
         'Only the Googlebot directive series is implemented')
    need(intent.get('indexing') in ('allow', 'exclude'), 'Missing indexing intent')
    need(intent.get('following', 'unspecified') in ('allow', 'disallow', 'unspecified'), 'Unknown link intent')
    need('presentation' not in intent, 'Presentation restrictions require review')
    directives = list(values)
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
    reason = 'Combined source directives compared with declared indexing/link intent; previews not assessed'
    if 'directive_crawler' in intent:
        reason += '; directive_crawler=googlebot; HTTP User-Agent=' + str(intent.get('crawler')) + '; semantics applied only to this client representation, not evidence of what Googlebot receives'
    return ('pass' if matches else 'fail', reason)


def robots_allowed(text, target, crawler):
    from conformance.robots import legacy_allowed
    return legacy_allowed(text, target, crawler)


def binding_digest(hops):
    """Bind supplied DOM captures to the exact ordered input trace, not a live site."""
    encoded = json.dumps(hops, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return hashlib.sha256(encoded.encode('utf-8')).hexdigest()


def text_present(value):
    return isinstance(value, str) and bool(value.strip())


def reviewed_exemption(target, plan, headers):
    need(plan.get('basis') in ('non-html', 'reviewed-stable'), 'Unsupported rendering exemption basis')
    render = target.get('render', {})
    need(isinstance(render, dict), 'Malformed rendering record')
    need(not plan.get('required_states') and not render.get('states'),
         'Exemption cannot hide planned or captured rendered states')
    review = target.get('exemption_review', {})
    need(isinstance(review, dict), 'Missing documented exemption review')
    need(review.get('basis') == plan['basis'] and text_present(review.get('reviewer'))
         and text_present(review.get('reason')), 'Missing documented exemption review')
    need(review.get('source_http_sha256') == binding_digest(target['http']), 'Exemption review is not bound to source')
    need(tsep.timestamp(review['observed_at']) >= tsep.timestamp(target['observed_at']),
         'Exemption review predates source')
    supporting = review.get('support', [])
    need(isinstance(supporting, list) and supporting, 'Exemption needs supporting records, not a no-JS assertion')
    for record in supporting:
        need(isinstance(record, dict) and text_present(record.get('name')) and text_present(record.get('content')),
             'Missing exemption supporting record')
        need(record.get('sha256') == hashlib.sha256(record['content'].encode('utf-8')).hexdigest(),
             'Exemption supporting record fingerprint mismatch')
    if plan['basis'] == 'non-html':
        need(media_type(headers)[0] in ('application/pdf', 'image/png') or utf8_media(headers, ('text/plain',)),
             'Non-HTML exemption contradicts media type or type is unsupported')
    else:
        need(utf8_media(headers, ('text/html',)), 'Stable HTML review requires HTML source')
    return 'not-applicable', 'Documented ' + plan['basis'] + ' review and supporting records; review truth not independently verified'


def rendered_result(target, final_url, headers, body):
    """Compare supplied DOMs; do not execute scripts or infer absent states."""
    intent = target['intent']
    plan = intent.get('rendering', {})
    need(isinstance(plan, dict), 'Missing rendering plan')
    if plan.get('mode') == 'exempt':
        return reviewed_exemption(target, plan, headers)
    need(plan.get('mode') == 'required', 'Rendering applicability/plan not established')
    required = plan.get('required_states', [])
    need(isinstance(required, list) and required, 'Required states must be explicitly inventoried')
    for state in required:
        need(isinstance(state, dict) and text_present(state.get('id')) and text_present(state.get('wait'))
             and isinstance(state.get('interactions'), list)
             and all(text_present(x) for x in state['interactions']), 'Incomplete required-state plan')
    ids = [s['id'] for s in required]
    need(len(ids) == len(set(ids)), 'Duplicate planned state')
    need(text_present(target['context'].get('id')), 'Rendering requires an explicit context ID')
    render = target.get('render', {})
    need(isinstance(render, dict), 'Malformed rendering record')
    browser = render.get('browser', {})
    need(isinstance(browser, dict), 'Missing render browser/version')
    need(text_present(browser.get('name')) and text_present(browser.get('version')), 'Missing render browser/version')
    states = render.get('states', [])
    need(isinstance(states, list) and all(isinstance(s, dict) and text_present(s.get('id')) for s in states),
         'Malformed rendered-state inventory')
    results = []
    extras = sorted({s['id'] for s in states} - set(ids))
    if extras:
        results.append(('inconclusive', 'Unplanned states: ' + ', '.join(extras)))
    source_hash = binding_digest(target['http'])
    for expected in required:
        label = expected['id']
        try:
            matches = [s for s in states if s['id'] == label]
            need(len(matches) == 1, 'Missing or duplicate capture')
            state = matches[0]
            need(state.get('complete') is True, 'Incomplete DOM capture')
            need(state.get('url') == final_url and state.get('context_id') == target['context']['id']
                 and state.get('source_http_sha256') == source_hash, 'Source, URL or context binding mismatch')
            need(tsep.timestamp(state['observed_at']) >= tsep.timestamp(target['observed_at']), 'DOM predates source')
            need(state.get('javascript_enabled') is True, 'JavaScript execution not established')
            need(state.get('interactions') == expected['interactions'] and state.get('wait') == expected['wait'],
                 'Interaction or waiting condition differs from plan')
            need(isinstance(state.get('errors'), list) and not state['errors'], 'Script/render errors or missing error record')
            from conformance.structured_dom import Surface, reader, READER
            if reader(plan, state) == READER:
                need(utf8_media(headers, ('text/html',)), 'Unsupported rendered source media')
                surface = Surface(state, final_url, target['http'], intent['crawler'])
                outcome, reason = directive_values(headers, surface.directives, intent)
                reason += '; ' + surface.detail
            else:
                need(isinstance(state.get('dom'), str), 'Missing raw DOM')
                outcome, reason = directive_result(headers, state['dom'], intent)
        except (Unknown, tsep.Invalid, KeyError, TypeError, ValueError) as error:
            outcome, reason = 'inconclusive', str(error)
        results.append((outcome, label + ': ' + reason))
    try:
        source_outcome, source_reason = directive_result(headers, body, intent)
    except (Unknown, tsep.Invalid, KeyError, TypeError, ValueError) as error:
        source_outcome, source_reason = 'inconclusive', str(error)
    detail = '; '.join(outcome + ' — ' + reason for outcome, reason in results)
    detail += '; source: ' + source_outcome + ' — ' + source_reason
    if any(outcome == 'fail' for outcome, _ in results):
        return 'fail', detail  # Keep a demonstrated contradiction even when other states are unknown.
    if source_outcome != 'pass' or any(outcome == 'inconclusive' for outcome, _ in results):
        return 'inconclusive', detail + '; source contradiction/removal or incomplete comparison cannot yield pass'
    return 'pass', detail + '; declared states only, not engine rendering or indexing'


def evaluate_target(target, rule):
    if rule.startswith('TS04-'):
        from conformance.robots_control import assess
        return assess(target, rule)
    if rule.startswith('TS02-'):
        from conformance.redirects import assess
        return assess(target, rule)
    if rule.startswith("TS10-"):
        from conformance.canonical import assess
        return assess(target, rule)
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
            return identity_result(final_url, headers, body, intent)
        if rule == 'TS07-A01':
            return directive_result(headers, body, intent)
        if rule == 'TS07-A03':
            return rendered_result(target, final_url, headers, body)
        from conformance.robots_control import access_rule
        return access_rule(target, final_url, status)
    except (Unknown, tsep.Invalid, KeyError, TypeError, ValueError) as error:
        return 'inconclusive', str(error)


def evaluate(data):
    tsep.require(data.get('input_version') in ('1', '2'), 'Unsupported conformance input version')
    def verify_wire(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key == 'http' and isinstance(child, list):
                    for hop in child:
                        if isinstance(hop, dict):
                            for field in ('request', 'response'):
                                if isinstance(hop.get(field), dict):
                                    tsep.require(data['input_version'] == '2', 'Binary HTTP records require input_version 2')
                                    try:
                                        raw_bytes(hop[field])
                                    except Unknown as error:
                                        raise tsep.Invalid('HTTP evidence integrity error: '+str(error)) from error
                verify_wire(child)
        elif isinstance(value, list):
            for child in value:
                verify_wire(child)
    verify_wire(data)
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
