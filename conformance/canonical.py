"""Bounded offline TS10 interpretation; human judgments remain supplied evidence.

Apache-2.0. No network, browser, similarity score or engine-selection inference.
"""
import hashlib
import re
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlsplit, urldefrag

import tsep
from conformance.evaluate import (Meta, Unknown, binding_digest, exchange, need,
                                  reviewed_exemption, text_present, trace, url_parts)

ERRORS = (Unknown, tsep.Invalid, KeyError, TypeError, ValueError, AttributeError)
NS = '{http://www.sitemaps.org/schemas/sitemap/0.9}'


def guarded(fn, *args):
    try:
        return fn(*args)
    except ERRORS as error:
        return 'inconclusive', str(error)


def combined(results):
    need(results, 'No assessed population')
    # An attributable contradiction survives incomplete coverage elsewhere.
    outcome = 'fail' if any(o == 'fail' for o, _ in results) else (
        'inconclusive' if any(o == 'inconclusive' for o, _ in results) else 'pass')
    return outcome, '; '.join(o + ': ' + r for o, r in results)


def unique_urls(values, label, nonempty=True):
    need(isinstance(values, list) and (bool(values) or not nonempty), 'Missing ' + label)
    need(all(isinstance(v, str) for v in values), 'Malformed ' + label)
    need(len(values) == len(set(values)) and len(values) <= 100, 'Duplicate/excessive ' + label)
    for url in values:
        url_parts(url)
    return values


def dated(target, record):
    need(tsep.timestamp(target['intent']['declared_at']) <= tsep.timestamp(record['observed_at'])
         <= tsep.timestamp(target['observed_at']), 'Capture/review outside declared assessment interval')


def capture(target, documents, url):
    need(isinstance(documents, list) and len(documents) <= 100, 'Missing/excessive document inventory')
    matches = [d for d in documents if d['url'] == url]
    need(len(matches) == 1, 'Missing/duplicate capture: ' + url)
    doc = matches[0]
    dated(target, doc)
    need(doc.get('context_id') == target['context']['id'], 'Capture context mismatch')
    return doc


def response(target, doc):
    return trace(doc['http'], doc['url'], target['intent']['crawler'])


class Links(Meta):
    """Strict source/DOM subset; never recover malformed HTML as a browser would."""
    def __init__(self):
        super().__init__()
        self.canonicals, self.anchors = [], []
        self.heads = self.bodies = 0

    def handle_starttag(self, tag, attrs):
        parent = self.stack[-1] if self.stack else None
        need(tag not in ('head', 'body') or parent == 'html', 'Misplaced head/body')
        if tag == 'head':
            self.heads += 1
            need(self.heads == 1 and self.bodies == 0, 'Ambiguous head')
        if tag == 'body':
            self.bodies += 1
            need(self.heads == 1 and self.bodies == 1, 'Missing head or ambiguous body')
        need(parent != 'html' or tag in ('head', 'body'), 'Unsupported HTML root child')
        need(parent != 'head' or tag in ('title', 'meta', 'link', 'script', 'style'), 'Invalid head element')
        super().handle_starttag(tag, attrs)
        if tag in ('link', 'a'):
            need(len(attrs) == len(set(k for k, _ in attrs)), 'Duplicate link attributes')
            values = dict(attrs)
            if tag == 'link' and 'canonical' in (values.get('rel') or '').lower().split():
                need(set(values) <= {'rel', 'href'}, 'Unsupported canonical attributes')
                self.canonicals.append((values.get('href'), parent == 'head'))
            if tag == 'a' and 'href' in values:
                need(isinstance(values['href'], str), 'Malformed anchor href')
                self.anchors.append(values['href'])

    def handle_startendtag(self, tag, attrs):
        need(tag in ('meta', 'link', 'br', 'img'), 'Unsupported self-closing HTML element')
        self.handle_starttag(tag, attrs)


def html(body):
    need(isinstance(body, str) and re.search(r'</html\s*>\s*$', body, re.I), 'HTML end not captured')
    parser = Links()
    parser.feed(body)
    parser.close()
    need(parser.roots == parser.heads == parser.bodies == 1 and not parser.stack, 'Incomplete HTML structure')
    return parser


def split_links(value, separator):
    parts, start, quoted, angle = [], 0, False, False
    for index, char in enumerate(value):
        need(char != '\\', 'Escaped Link syntax requires review')
        if char == '"' and not angle:
            quoted = not quoted
        elif not quoted:
            if char == '<':
                need(not angle, 'Ambiguous Link URI'); angle = True
            elif char == '>':
                need(angle, 'Ambiguous Link URI'); angle = False
            elif char == separator and not angle:
                parts.append(value[start:index].strip()); start = index + 1
    need(not quoted and not angle, 'Unterminated Link value')
    parts.append(value[start:].strip())
    need(all(parts), 'Empty Link value')
    return parts


def header_canonicals(headers):
    values = []
    for field in headers.get('link', []):
        for link in split_links(field, ','):
            parts = split_links(link, ';')
            match = re.fullmatch(r'<([^<>]*)>', parts[0])
            need(match, 'Unsupported Link target syntax')
            params = {}
            for part in parts[1:]:
                param = re.fullmatch(r'([A-Za-z][A-Za-z0-9_-]*)\s*=\s*(?:"([^"\\]*)"|([A-Za-z0-9_./:-]+))', part)
                need(param and param[1].lower() not in params, 'Ambiguous Link parameters')
                params[param[1].lower()] = param[2] if param[2] is not None else param[3]
            if 'canonical' in params.get('rel', '').lower().split():
                need(set(params) == {'rel'}, 'Canonical Link context/extension requires review')
                values.append(match[1])  # Preserve repeated, including identical, declarations.
    return values


def doms(target, doc, plan, final, headers):
    need(isinstance(plan, dict), 'Missing rendering plan')
    if plan.get('mode') == 'exempt':
        reviewed_exemption(doc, plan, headers)
        dated(target, doc['exemption_review'])
        return []
    need(plan.get('mode') == 'required', 'Unknown rendering mode')
    states = plan.get('required_states')
    need(isinstance(states, list) and states, 'Missing required rendered states')
    ids = [s['id'] for s in states]
    need(all(text_present(v) for v in ids) and len(ids) == len(set(ids)), 'Duplicate/empty planned state')
    render = doc.get('render', {})
    need(all(text_present(render.get('browser', {}).get(k)) for k in ('name', 'version')), 'Missing browser/version')
    records = render.get('states')
    need(isinstance(records, list), 'Missing DOM captures')
    need(all(r['id'] in ids for r in records), 'Unplanned DOM capture')
    results = []
    for state in states:
        try:
            need(isinstance(state['interactions'], list) and all(text_present(s) for s in state['interactions'])
                 and text_present(state['wait']), 'Missing state scenario')
            found = [r for r in records if r['id'] == state['id']]
            need(len(found) == 1, 'Missing/duplicate DOM capture: ' + state['id'])
            record = found[0]
            dated(target, record)
            need(tsep.timestamp(record['observed_at']) >= tsep.timestamp(doc['observed_at']), 'DOM predates source')
            need(record.get('url') == final and record.get('context_id') == target['context']['id']
                 and record.get('source_http_sha256') == binding_digest(doc['http']), 'DOM source binding mismatch')
            need(record.get('complete') is True and record.get('javascript_enabled') is True
                 and record.get('errors') == [], 'Incomplete/failed rendered state')
            need(record.get('interactions') == state['interactions'] and record.get('wait') == state['wait'],
                 'DOM scenario mismatch')
            results.append((html(record['dom']), None))
        except ERRORS as error:
            results.append((None, str(error)))
    return results


def surfaces(target, doc, plan):
    final, status, headers, body = response(target, doc)
    need(status == 200, 'Representation unavailable for canonical/link extraction')
    is_html = headers.get('content-type') == ['text/html; charset=utf-8']
    need(is_html or headers.get('content-type') == ['text/plain; charset=utf-8'], 'Unsupported representation media type')
    parsers = []
    if is_html:
        try:
            parsers.append((html(body), None))
        except ERRORS as error:
            parsers.append((None, str(error)))
    else:
        need(plan.get('mode') == 'exempt' and plan.get('basis') == 'non-html', 'Non-HTML rendering record required')
    try:
        rendered = doms(target, doc, plan, final, headers)
    except ERRORS as error:
        rendered = [(None, str(error))]
    return final, headers, parsers, rendered


def signals(values, preferred, label):
    bad = [(value, valid) for value, valid in values if not valid or value != preferred]
    return ('fail' if bad else 'pass', label + ': ' + repr(values))


def declarations(target, member, preferred):
    doc = capture(target, target.get('documents'), member['url'])
    final, headers, source, rendered = surfaces(target, doc, member['rendering'])
    required = member.get('required_methods')
    need(isinstance(required, list) and required and set(required) <= {'html', 'http', 'redirect', 'dom'}
         and len(required) == len(set(required)), 'Missing/unsupported required canonical methods')
    findings = []
    try:
        values = header_canonicals(headers)
        findings.append(signals([(v, True) for v in values], preferred, 'HTTP Link'))
        if 'http' in required and not values:
            findings.append(('fail', 'Required HTTP canonical absent'))
    except ERRORS as error:
        findings.append(('inconclusive', str(error)))
    redirected = len(doc['http']) > 1
    if redirected:
        findings.append(signals([(final, True)], preferred, 'Final redirect URL'))
    elif 'redirect' in required:
        findings.append(('fail', 'Required redirect absent'))
    for label, parsers in (('html', source), ('dom', rendered)):
        if label in required and not parsers:
            findings.append(('fail', 'Required ' + label + ' canonical surface absent'))
        for parser, error in parsers:
            if error:
                findings.append(('inconclusive', error)); continue
            findings.append(signals(parser.canonicals, preferred, label + ' canonical'))
            if label in required and not parser.canonicals:
                findings.append(('fail', 'Required ' + label + ' canonical absent'))
    return combined(findings)


def content_binding(target):
    return binding_digest({k: target[k] for k in ('intent', 'context', 'documents')})


def content_review(target, members):
    # Ensure the human review has complete, attributable representations to compare.
    for member in members:
        doc = capture(target, target.get('documents'), member['url'])
        final, headers, source, rendered = surfaces(target, doc, member['rendering'])
        need(all(error is None for _, error in source + rendered), 'Content review lacks complete source/DOM inputs')
    review = target.get('content_review', {})
    need(review.get('mode') == 'manual' and text_present(review.get('reviewer'))
         and text_present(review.get('reason')), 'Missing reasoned manual content review')
    dated(target, review)
    need(review.get('source_sha256') == content_binding(target), 'Content review binding mismatch')
    dates = [doc['observed_at'] for doc in target['documents']]
    dates += [r['observed_at'] for doc in target['documents'] for r in doc.get('render', {}).get('states', [])]
    need(all(tsep.timestamp(review['observed_at']) >= tsep.timestamp(d) for d in dates), 'Review predates compared evidence')
    rows = review.get('comparisons', [])
    need(isinstance(rows, list) and len(rows) == len(members), 'Incomplete content review population')
    need(sorted(r['url'] for r in rows) == sorted(m['url'] for m in members), 'Content review population differs from family')
    results = []
    for row in rows:
        need(text_present(row.get('reason')), 'Unreasoned content comparison')
        outcome = {'compatible': 'pass', 'incompatible': 'fail', 'inconclusive': 'inconclusive'}.get(row.get('outcome'))
        need(outcome, 'Unsupported content judgment')
        results.append((outcome, row['url'] + ': supplied manual judgment, not independently verified: ' + row['reason']))
    return combined(results)


def destination(target, members, preferred):
    doc = capture(target, target.get('documents'), preferred)
    hops = doc.get('http')
    need(isinstance(hops, list) and hops, 'Missing preferred-URL HTTP capture')
    status, _, _ = exchange(hops[0], preferred, target['intent']['crawler'])
    need(status >= 200 and status != 304, 'No complete preferred representation')
    if status != 200:
        return 'fail', 'Preferred URL does not return direct 200: ' + str(status) + '; content not established'
    member = next(m for m in members if m['url'] == preferred)
    final, headers, source, rendered = surfaces(target, doc, member['rendering'])
    findings = []
    try:
        findings.append(signals([(v, True) for v in header_canonicals(headers)], preferred, 'Preferred HTTP canonical'))
    except ERRORS as error:
        findings.append(('inconclusive', str(error)))
    for parser, error in source + rendered:
        findings.append(('inconclusive', error) if error else signals(parser.canonicals, preferred, 'Preferred HTML/DOM canonical'))
    findings.append(guarded(content_review, target, members))
    return combined(findings)


def exceptions(plan, allowed, sources=None):
    rows = plan.get('exceptions')
    need(isinstance(rows, list), 'Missing explicit exceptions list')
    result = set()
    for row in rows:
        need(row['url'] in allowed and text_present(row.get('reason')), 'Unjustified/unknown family exception')
        key = row['url'] if sources is None else (row['source'], row['url'])
        need(sources is None or row['source'] in sources, 'Exception source outside population')
        need(key not in result, 'Duplicate exception')
        result.add(key)
    return result


def xml_entries(body):
    need(not re.search(r'<!\s*(DOCTYPE|ENTITY)', body, re.I), 'DTD/entities unsupported')
    try:
        root = ET.fromstring(body)
    except ET.ParseError as error:
        raise Unknown('Incomplete/malformed sitemap XML: ' + str(error))
    need(root.tag in (NS + 'urlset', NS + 'sitemapindex') and not root.attrib, 'Unsupported sitemap root/namespace')
    index = root.tag == NS + 'sitemapindex'
    entries = []
    for entry in root:
        need(entry.tag == NS + ('sitemap' if index else 'url') and not entry.attrib, 'Unsupported sitemap element')
        allowed = {NS + n for n in (('loc', 'lastmod') if index else ('loc', 'lastmod', 'changefreq', 'priority'))}
        need(all(child.tag in allowed and not child.attrib and not list(child) for child in entry), 'Unsupported sitemap extension')
        locs = [c.text for c in entry if c.tag == NS + 'loc']
        need(len(locs) == 1 and text_present(locs[0]), 'Missing/duplicate sitemap loc')
        location = locs[0].strip(); url_parts(location); entries.append(location)
    need(len(entries) <= 50000, 'Sitemap entry limit exceeded')
    return index, entries


def sitemap_agreement(target, members, preferred):
    plan = target['intent']['canonical']['sitemaps']
    record = target.get('sitemaps', {})
    if plan.get('mode') == 'unused':
        need(text_present(plan.get('reason')) and isinstance(plan.get('inventory'), list)
             and plan['inventory'], 'Positive strategy/inventory required for sitemap absence')
        need(all(text_present(v) for v in plan['inventory']), 'Malformed absence inventory')
        need(not record.get('documents'), 'Absence record cannot hide sitemap captures')
        review = record.get('absence_review', {})
        dated(target, review)
        need(text_present(review.get('reviewer')) and text_present(review.get('reason'))
             and review.get('plan_sha256') == binding_digest(plan), 'Missing/badly bound sitemap absence review')
        support = review.get('support', [])
        need(isinstance(support, list) and support, 'Absence needs retained inventory records')
        for item in support:
            need(text_present(item.get('name')) and text_present(item.get('content'))
                 and item.get('sha256') == hashlib.sha256(item['content'].encode('utf-8')).hexdigest(),
                 'Missing/tampered sitemap absence record')
        return 'not-applicable', 'Documented unused-sitemap strategy and reviewed inventory; truth not independently verified'
    need(plan.get('mode') == 'required', 'Unknown sitemap strategy')
    roots = unique_urls(plan['roots'], 'sitemap roots')
    need(isinstance(plan.get('require_preferred'), bool), 'Missing sitemap inclusion intent')
    need(plan['require_preferred'] or text_present(plan.get('omission_reason')), 'Unjustified optional sitemap omission')
    family = [m['url'] for m in members]
    exempt = exceptions(plan, family)
    documents = record.get('documents')
    need(isinstance(documents, list), 'Missing sitemap inventory')
    findings, entries, visited = [], [], set()

    def visit(url, ancestry):
        need(len(ancestry) <= 10 and url not in ancestry, 'Cyclic/excessive sitemap index')
        if url in visited:
            return
        doc = capture(target, documents, url)
        final, status, headers, body = response(target, doc)
        need(final == url and status == 200 and headers.get('content-type') in
             (['application/xml; charset=utf-8'], ['text/xml; charset=utf-8']), 'Unavailable/unsupported sitemap response')
        is_index, locations = xml_entries(body)
        visited.add(url)
        if is_index:
            for location in locations:
                try:
                    visit(location, ancestry + [url])
                except ERRORS as error:
                    findings.append(('inconclusive', str(error)))
        else:
            entries.extend(locations)
            for location in locations:
                if location in family and location != preferred and location not in exempt:
                    findings.append(('fail', 'Competing family URL in sitemap: ' + location))
    for url in roots:
        try:
            visit(url, [])
        except ERRORS as error:
            findings.append(('inconclusive', str(error)))
    if any(d['url'] not in visited for d in documents):
        findings.append(('inconclusive', 'Unreconciled sitemap captures'))
    if not any(o == 'inconclusive' for o, _ in findings) and plan['require_preferred'] and preferred not in entries:
        findings.append(('fail', 'Required preferred URL missing from fully examined sitemap population'))
    findings.append(('pass', 'Examined declared sitemap inventory; no engine-selection inference'))
    return combined(findings)


def internal_links(target, members, preferred):
    plan = target['intent']['canonical']['links']
    sources = plan['sources']
    urls = unique_urls([s['url'] for s in sources], 'source population')
    origin = urlsplit(preferred)[:2]
    need(all(urlsplit(url)[:2] == origin for url in urls), 'Source outside declared internal origin')
    exempt = exceptions(plan, [m['url'] for m in members], urls)
    family = {m['url'] for m in members}
    documents = target.get('crawl', {}).get('documents')
    need(isinstance(documents, list), 'Missing crawl inventory')
    findings = []
    for source in sources:
        try:
            doc = capture(target, documents, source['url'])
            final, headers, initial, rendered = surfaces(target, doc, source['rendering'])
            need(urlsplit(final)[:2] == origin and headers.get('content-type') == ['text/html; charset=utf-8'],
                 'Source redirected outside internal origin or non-HTML')
            for parser, error in initial + rendered:
                if error:
                    findings.append(('inconclusive', error)); continue
                links = [(href, urldefrag(urljoin(final, href))[0]) for href in parser.anchors]
                bad = [(href, url) for href, url in links if url in family and url != preferred
                       and (source['url'], url) not in exempt]
                findings.append(('fail' if bad else 'pass', source['url'] + ' href/destination pairs: ' + repr(links)))
        except ERRORS as error:
            findings.append(('inconclusive', str(error)))
    if any(d['url'] not in urls for d in documents):
        findings.append(('inconclusive', 'Unreconciled crawl capture outside planned population'))
    return combined(findings)


def assess(target, rule):
    def run():
        intent, context = target['intent'], target['context']
        need(all(text_present(context.get(k)) for k in ('id', 'network', 'bounds', 'tool', 'tool_version')),
             'Missing canonical assessment context')
        dated(target, target)
        need(text_present(intent.get('crawler')), 'Missing crawler')
        plan = intent['canonical']; members = plan['members']; preferred = plan['preferred_url']
        urls = unique_urls([m['url'] for m in members], 'family inventory')
        need(preferred in urls and target['url'] == preferred, 'Target must identify the inventoried preferred family URL')
        if rule == 'TS10-A01':
            return combined([guarded(declarations, target, member, preferred) for member in members])
        if rule == 'TS10-A02':
            return destination(target, members, preferred)
        if rule == 'TS10-A03':
            return sitemap_agreement(target, members, preferred)
        return internal_links(target, members, preferred)
    return guarded(run)
