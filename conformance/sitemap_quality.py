"""Bounded TS13/TS14 supplied evidence, independent of TS15 verdicts. Apache-2.0.

No network, browser execution, generated reviews or history authentication.
Existing sitemap/HTTP/source readers are reused without changing their behavior.
"""
import datetime as dt
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zlib

import tsep
from conformance import sitemap_files, sitemap_set
from conformance.http import Unknown, need

VERSION = '1'
RULES = ('TS13-A01', 'TS13-A02', 'TS14-A01')
QUALITY = 'supplied-sitemap-quality-v1'
LASTMOD = 'supplied-sitemap-lastmod-v1'
MAX_ENTRIES = 128
MAX_XML = 2 * 1024 * 1024
MAX_EVENT = 32768
ERRORS = (Unknown, ValueError, KeyError, TypeError, AttributeError, OverflowError)
PREFIX = 'Supplied sitemap quality / qualité sitemap fournie: '
LIMITATION = ('Declared supplied files/pages/history only; no site completeness, '
              'authenticated acquisition or reviewer, browser execution, Google '
              'canonical selection, indexing, ranking or actual change established.')


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def binding(target, subject):
    return digest(dict(target=target['url'], observed_at=target['observed_at'],
                       intent=target['intent'], context=target['context'],
                       sitemap_files=target.get('sitemap_files'), subject=subject))


def text(value, limit=8192):
    return isinstance(value, str) and bool(value.strip()) and len(value.encode('utf-8')) <= limit


def review(target, record, subject, after):
    need(type(record) is dict, 'Missing supplied review')
    need(len(json.dumps(record, ensure_ascii=False).encode('utf-8')) <= MAX_EVENT,
         'Review exceeds bounded profile')
    need(record.get('evidence_sha256') == binding(target, subject), 'Review binding mismatch')
    need(text(record.get('reviewer')) and text(record.get('reason')), 'Review attribution/rationale missing')
    allowed = ('synthetic-exercise',) if target['sitemap_synthetic'] else ('human', 'human-assisted')
    need(record.get('provenance') in allowed, 'Review provenance unqualified')
    # The binding includes every supplied file, including repeated page locations.
    # A review cannot predate another file merely because this page was seen first.
    after = max([after] + [tsep.timestamp(f['observed_at']) for f in target['sitemap_files']])
    need(after <= tsep.timestamp(record.get('reviewed_at')) <= tsep.timestamp(target['observed_at']),
         'Review chronology unqualified')
    need(record.get('judgment') in ('supported', 'contradicted'), 'Significance/quality not established')
    return 'fail' if record['judgment'] == 'contradicted' else 'pass'


def verify_target(target):
    """Refuse corrupt supplied originals; absent evidence remains assessable as NT."""
    files = target.get('sitemap_files')
    if isinstance(files, list):
        for item in files:
            if isinstance(item, dict) and 'native' in item:
                sitemap_files.original_bytes(item['native'])
    history = target.get('change_history')
    if isinstance(history, list):
        for item in history:
            if isinstance(item, dict) and 'event' in item:
                sitemap_files.original_bytes(item['event'])


def entries(target, row):
    """Yield only complete qualified native leaf entries; retain coverage gaps."""
    plan, start, end = sitemap_set.header(target)
    coverage, _ = sitemap_set.assess(target, 'TS15-A03')
    if coverage != 'pass':
        row('population', 'inconclusive', 'Declared file/root/child coverage unresolved; no site discovery')
    files = target.get('sitemap_files')
    need(type(files) is list and len(files) <= 16, 'Missing/excessive native files')
    result = []
    for url in plan['documents']:
        try:
            matched = [f for f in files if type(f) is dict and f.get('url') == url]
            need(len(matched) == 1, 'Missing/ambiguous native file')
            file = matched[0]
            need(file.get('provenance') == ('synthetic-exercise' if target['sitemap_synthetic'] else 'supplied-native-file'),
                 'File provenance mismatch')
            need(text(file.get('description')), 'Missing native file description')
            need(start <= sitemap_set.stamp(file['observed_at']) <= end, 'File outside prior window')
            native = file['native']
            parsed = sitemap_files.read_record(native)
            need(parsed['format'] == parsed['limits'] == 'pass' and parsed.get('xml_complete') is True,
                 'Native file not completely qualified; TS15 format/size outcomes remain separate')
            if parsed['kind'] == 'index':
                continue  # Index lastmod describes a file, outside page-change TS14.
            need(len(result) + parsed['count'] <= MAX_ENTRIES, '128-entry profile bound exceeded')
            need(parsed['decoded_bytes_read'] <= MAX_XML, '2MiB XML profile bound exceeded')
            raw = sitemap_files.original_bytes(native)
            if native['encoding'] == 'gzip':
                raw = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(raw, MAX_XML + 1)
            # The unchanged native reader has already rejected DTD/entities and
            # qualified UTF-8, structure, attributes and every optional leaf.
            root = ET.fromstring(raw)
            ns = '{' + sitemap_files.NS + '}'
            for index, element in enumerate(root):
                loc = element.find(ns + 'loc').text.strip(' \t\r\n')
                last = element.find(ns + 'lastmod')
                result.append(dict(file_url=url, entry_index=index, url=loc,
                                   lastmod=None if last is None else (last.text or '').strip(' \t\r\n'),
                                   observed_at=file['observed_at'], original_sha256=native['sha256']))
        except ERRORS as error:
            row(url, 'inconclusive', str(error))
    return result, start, end


def absolute(url):
    need(len(url) <= 4096, 'URL exceeds bounded leaf profile')
    sitemap_set.address(url)
    need('\\' not in url and not re.search(r'%(?![0-9A-Fa-f]{2})', url), 'Ambiguous URL escape/backslash')


def page(target, entry, plans, start, end, row):
    from conformance.evaluate import exchange, directive_values, utf8_media
    from conformance.canonical import html, header_canonicals
    url = entry['url']
    try:
        absolute(url)
        documents = target.get('documents')
        need(type(documents) is list and len(documents) <= MAX_ENTRIES, 'Missing/excessive page records')
        matches = [d for d in documents if type(d) is dict and d.get('url') == url]
        need(len(matches) == 1, 'Missing/ambiguous page record')
        doc = matches[0]
        need(text(target['context'].get('id')) and doc.get('context_id') == target['context']['id'], 'Page context mismatch')
        need(start <= sitemap_set.stamp(doc['observed_at']) <= end, 'Page outside prior window')
        hops = doc.get('http')
        need(type(hops) is list and 1 <= len(hops) <= 20 and type(hops[0]) is dict, 'Missing HTTP exchange')
        need(text(target['intent'].get('crawler')), 'Missing prior HTTP client')
        status, headers, body = exchange(hops[0], url, target['intent']['crawler'])
        need(status not in (206, 304) and status >= 200, 'Partial/conditional/informational response')
        if status != 200:
            row(url, 'fail', 'Listed page is not a direct 200: ' + str(status))
            return
        need(len(hops) == 1, 'Unexpected extra HTTP exchanges')
        # Headers remain independently interpretable when the source is unknown.
        directives = dict(crawler=target['intent']['crawler'], directive_crawler='googlebot', indexing='allow')
        for label, read in (
            ('HTTP directives', lambda: directive_values(headers, [], directives)),
            ('HTTP canonical', lambda: canonical_values(header_canonicals(headers), url)),
        ):
            try:
                outcome, reason = read()
                row(url, outcome, label + ': ' + reason)
            except ERRORS as error:
                row(url, 'inconclusive', label + ': ' + str(error))
        source_canonicals = None
        try:
            need(utf8_media(headers, ('text/html',)), 'Only explicit UTF-8 HTML pages qualified')
            parsed = html(body, source=True)
            source_canonicals = parsed.canonicals
            outcome, reason = canonical_values([v for v, _ in parsed.canonicals], url)
            if any(not in_head for _, in_head in parsed.canonicals):
                outcome, reason = 'fail', 'Canonical outside document head'
            row(url, outcome, 'Source canonical: ' + reason)
            outcome, reason = directive_values(headers, parsed.directives, directives)
            row(url, outcome, 'Source directives: ' + reason)
        except ERRORS as error:
            row(url, 'inconclusive', 'Source: ' + str(error))
        try:
            need(source_canonicals or header_canonicals(headers), 'No explicit canonical evidence in qualified surfaces')
        except ERRORS as error:
            row(url, 'inconclusive', str(error))
        try:
            need(type(plans) is list and 1 <= len(plans) <= MAX_ENTRIES, 'Missing/bounded prior page strategy')
            selected = [p for p in plans if type(p) is dict and p.get('url') == url]
            need(len(selected) == 1, 'Missing/ambiguous prior page strategy')
            plan = selected[0]
            absolute(plan['preferred_url'])
            need(plan.get('indexing') in ('allow', 'exclude') and type(plan.get('useful')) is bool, 'Unqualified indexing/usefulness intent')
            subject = {k: v for k, v in doc.items() if k != 'quality_review'}
            after = max(tsep.timestamp(doc['observed_at']), tsep.timestamp(entry['observed_at']))
            outcome = review(target, doc.get('quality_review'), subject, after)
            if plan['preferred_url'] != url or plan['indexing'] != 'allow' or not plan['useful']:
                outcome = 'fail'
            row(url, outcome, 'Evidence-bound supplied strategy/usefulness judgment; not authenticated')
            need(plan.get('rendering') == 'source-only', 'Required/unknown rendered states outside this source-only profile')
        except ERRORS as error:
            row(url, 'inconclusive', str(error))
    except ERRORS as error:
        row(url, 'inconclusive', str(error))


def canonical_values(values, url):
    return ('fail' if any(value != url for value in values) else 'pass',
            'Literal declarations: ' + repr(values))


def date_value(value):
    """Closed ISO date / zoned second-precision profile; no guessed local zone."""
    need(isinstance(value, str), 'Missing date string')
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        return dt.date.fromisoformat(value)
    need(re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})', value),
         'Date outside YYYY-MM-DD / zoned timestamp profile')
    if value[-1] != 'Z':
        hours, minutes = int(value[-5:-3]), int(value[-2:])
        need(hours <= 14 and minutes < 60 and (hours < 14 or minutes == 0), 'Invalid timezone offset')
    return dt.datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(dt.timezone.utc)


def lastmod(target, entry, row):
    subject = entry['file_url'] + '#' + str(entry['entry_index'])
    if entry['lastmod'] is None:
        row(subject, 'not-applicable', 'Complete native page entry has no lastmod; absence is not a defect')
        return
    try:
        if entry['lastmod'] == '':
            row(subject, 'fail', 'Complete native lastmod is empty, not a date')
            return
        try:
            value = date_value(entry['lastmod'])
        except Unknown as error:
            row(subject, 'inconclusive', 'Native lastmod precision/timezone outside profile: ' + str(error))
            return
        except ValueError as error:
            row(subject, 'fail', 'Native lastmod has an invalid calendar date/time: ' + str(error))
            return
        captured = tsep.timestamp(entry['observed_at']).astimezone(dt.timezone.utc)
        future = value > (captured if isinstance(value, dt.datetime) else captured.date())
        if future:
            row(subject, 'fail', 'Native lastmod postdates supplied sitemap capture')
        absolute(entry['url'])
        history = target.get('change_history')
        need(type(history) is list and len(history) <= MAX_ENTRIES, 'Missing/excessive supplied change history')
        matches = [h for h in history if type(h) is dict and h.get('file_url') == entry['file_url']
                   and type(h.get('entry_index')) is int and h['entry_index'] == entry['entry_index'] and h.get('url') == entry['url']]
        need(len(matches) == 1, 'Missing/ambiguous entry-bound change event')
        item = matches[0]
        native = item['event']
        raw = sitemap_files.original_bytes(native)
        need(native['complete'] is True and native['encoding'] == 'identity' and len(raw) <= MAX_EVENT,
             'Change event incomplete/encoded/above32KiB')
        event = tsep.parse_json(raw)
        need(type(event) is dict and event.get('url') == entry['url'] and text(event.get('change_id'))
             and text(event.get('description')), 'Unattributed native change event')
        changed = date_value(event.get('changed_at'))
        need(isinstance(changed, dt.datetime), 'Event requires zoned timestamp')
        need(changed <= captured, 'Change event postdates sitemap capture')
        if value != (changed if isinstance(value, dt.datetime) else changed.date()):
            row(subject, 'fail', 'Native lastmod differs from bound event at declared UTC precision')
        need(event.get('kind') in ('content', 'file-generation'), 'Event kind not qualified')
        if event['kind'] == 'file-generation':
            row(subject, 'fail', 'File generation alone does not establish a significant page change')
        review_subject = {k: v for k, v in item.items() if k != 'review'}
        outcome = review(target, item.get('review'), review_subject, captured)
        row(subject, outcome, 'Supplied significance judgment bound to native event and sitemap')
    except ERRORS as error:
        row(subject, 'inconclusive', str(error))


def assess(target, rule, *, diagnostics=None):
    rows = []
    def row(subject, outcome, reason):
        rows.append(dict(subject=subject, outcome=outcome, reason=reason))
    population = []
    try:
        need(rule in RULES, 'Unknown sitemap quality rule')
        population, start, end = entries(target, row)
        if not population:
            row('population', 'inconclusive', 'No complete qualified page entries')
        if rule == 'TS13-A01':
            for entry in population:
                try:
                    absolute(entry['url'])
                    row(entry['url'], 'pass', 'Native absolute HTTP(S) location; repeats retained, no equivalence inferred')
                except ERRORS as error:
                    row(entry['url'], 'fail', str(error))
        elif rule == 'TS13-A02':
            policy = target['intent'].get('sitemap_quality')
            need(type(policy) is dict and policy.get('reader') == QUALITY, 'Missing prior TS13 reader selection')
            seen = set()
            for entry in population:
                if entry['url'] not in seen:
                    page(target, entry, policy.get('pages'), start, end, row)
                    seen.add(entry['url'])
        else:
            policy = target['intent'].get('sitemap_lastmod')
            need(type(policy) is dict and policy.get('reader') == LASTMOD and policy.get('date_basis') == 'UTC',
                 'Missing prior TS14 reader/UTC date basis')
            for entry in population:
                lastmod(target, entry, row)
    except ERRORS as error:
        row('scope', 'inconclusive', str(error))
    outcomes = [r['outcome'] for r in rows]
    outcome = ('fail' if 'fail' in outcomes else 'inconclusive' if not rows or 'inconclusive' in outcomes
               else 'pass' if 'pass' in outcomes else 'not-applicable')
    note = dict(reader=LASTMOD if rule == 'TS14-A01' else QUALITY, version=VERSION,
                rule=rule, outcome=outcome, entries=population, rows=rows,
                scope='declared-file-population-only', limitation=LIMITATION)
    if diagnostics is not None:
        diagnostics.append(note)
    return outcome, PREFIX + json.dumps(note, ensure_ascii=False, sort_keys=True)
