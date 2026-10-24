"""TS33: bound page JSON-LD terms and separate native indexed messages. Apache-2.0.

No network collection, RRT emulation, authentication or current eligibility claim.
"""
import json
from pathlib import Path

import tsep
from conformance import inspection, structured_content as content
from conformance.agent_policy import ERRORS, combine, digest, present
from conformance.http import need

VERSION = '1'
READER = 'jsonld-validation-layers-v1'
PREFIX = 'Structured validation evidence / preuves des couches de validation: '
RULES = ('TS33-A01', 'TS33-A02', 'TS33-A03')
VOCABULARY = 'third_party/schemaorg/schemaorg-all-https-30.1.jsonld'
VOCABULARY_SHA256 = '07e7c663dbc12a0937581745e59a98ed12b8698f38e8e3b03650287d9df88ae5'
ROOT = Path(__file__).resolve().parents[1]
LIMITATION = ('Selected TS31-bound supplied page surfaces and a separate indexed API snapshot. '
    'Known term names only, not domain/range/value validity. No authenticated origin, '
    'cross-snapshot correspondence, same Google input bytes, live eligibility, display, indexing or ranking established.')


def header(t):
    _, page, declared, start, end, observed = content.header(t)
    p = t['intent']['structured_validation']
    need(p.get('reader') == READER and p.get('vocabulary') == 'schemaorg-all-30.1'
         and p.get('source') == 'ts31-bound-surfaces' and p.get('engine') == 'google-url-inspection-v1'
         and p.get('relationship') == 'separate-indexed-snapshot', 'Unsupported/unbound validation layer scope')
    need(page['start_url'] == page['final_url'] == t['url'] and end-start <= 86400,
         'Profile requires same-URL page surfaces and at most a 24-hour capture window')
    inspection.observer().check_request(dict(inspectionUrl=t['url'], siteUrl=p['site_url']))
    features = p['features']
    need(type(features) is list and 1 <= len(features) <= 16 and all(present(v) for v in features)
         and len(set(features)) == len(features), 'Require 1–16 distinct prior engine features')
    guides = p['guidance']
    need(type(guides) is list and len(guides) == len(features), 'One dated guidance capture per intended feature required')
    names = []
    for g in guides:
        content.native.processor.absolute(g['url'])
        need(content.text_record(g) <= declared, 'Feature guidance postdates plan')
        names.append(g['feature'])
    need(all(type(v) is str for v in names) and set(names) == set(features), 'Missing/duplicate guidance coverage')
    return p, declared, start, end, observed


def plan_binding(t):
    return digest(dict(url=t['url'], intent=t['intent'], plan=t['jsonld']['plan']))


def review_binding(t):
    return digest(dict(url=t['url'], intent=t['intent'], record=t['validation_record']))


def vocabulary():
    raw = (ROOT / VOCABULARY).read_bytes()
    need(tsep.digest(ROOT / VOCABULARY) == VOCABULARY_SHA256, 'Pinned Schema.org vocabulary changed')
    data = tsep.parse_json(raw)
    return {n['@id'][7:]: n for n in data['@graph'] if n['@id'].startswith('schema:')}


def terms(graph):
    """Read expanded class/property IRIs, excluding IDs and literal datatype values."""
    found = set()
    def walk(value):
        if type(value) is list:
            for child in value: walk(child)
        elif type(value) is dict:
            if '@value' in value: return
            need('@graph' not in value, 'Named graph outside bounded vocabulary reader')
            for key, children in value.items():
                if key == '@type':
                    need(type(children) is list and all(type(x) is str for x in children), 'Malformed expanded classes')
                    found.update(('class', x) for x in children)
                elif not key.startswith('@'):
                    found.add(('property', key)); walk(children)
                elif key in ('@list', '@reverse', '@set', '@included'):
                    walk(children)
    walk(graph)
    need(len(found) <= 256, 'More than 256 distinct vocabulary terms per surface')
    return sorted(found)


def term_result(kind, iri, vocab):
    name = next((iri[len(prefix):] for prefix in ('https://schema.org/', 'http://schema.org/')
                 if iri.startswith(prefix)), None)
    need(name is not None, 'Foreign vocabulary outside pinned Schema.org scope: ' + iri)
    entry = vocab.get(name)
    if not entry:
        return 'fail', 'Term absent from pinned Schema.org 30.1 (all sections including historical terms): ' + iri
    wanted = 'rdfs:Class' if kind == 'class' else 'rdf:Property'
    roles = entry.get('@type', []); roles = roles if type(roles) is list else [roles]
    if wanted not in roles: return 'fail', 'Known term is not declared as the requested ' + kind + ': ' + iri
    detail = {k: entry[k] for k in ('schema:isPartOf', 'schema:supersededBy') if k in entry}
    return 'pass', 'Known ' + kind + ': ' + iri + ('; recorded status ' + json.dumps(detail, sort_keys=True) if detail else '')


def native_record(t, p, start, end):
    r = t['validation_record']
    need(r.get('provenance') in ('synthetic-exercise', 'supplied-google-api') and present(r.get('description'))
         and (r['provenance'] == 'synthetic-exercise') == t['structured_synthetic'], 'Missing/inconsistent native record provenance')
    need(r.get('tool') == 'google-url-inspection' and r.get('api_version') == 'v1'
         and r.get('backend_version') == 'not-exposed', 'Unsupported tool/API identity; backend version is not exposed')
    need(r.get('complete') is True and type(r.get('http_status')) is int and r['http_status'] == 200,
         'Incomplete or unsuccessful native API response; technical outcome, not a green assessment')
    when = content.stamp(r['retrieved_at']); need(start <= when <= end, 'API retrieval outside prior capture window')
    request, response = inspection.body(r['request']), inspection.body(r['response'])
    url = inspection.observer().check_request(request)
    need(url == t['url'] and request['siteUrl'] == p['site_url'] and request.get('languageCode') == 'en-US',
         'Native request URL/property/language differs from prior scope')
    need(type(response) is dict and 'error' not in response, 'API error is not a validation result')
    result = response['inspectionResult']; need(type(result) is dict, 'Missing inspection result')
    index = result.get('indexStatusResult')
    need(type(index) is dict and content.stamp(index['lastCrawlTime']) <= when,
         'Missing/invalid last crawl or crawl later than retrieval; not a timestamp for every field')
    rich = result.get('richResultsResult'); need(type(rich) is dict, 'Missing native rich-results result')
    return r, rich, when


def assess(t, rule, *, diagnostics=None):
    obs = dict(reader=READER, version=VERSION, rule=rule, rows=[], inventories={}, limitation=LIMITATION)
    rows = obs['rows']
    def row(subject, fn):
        try: outcome, reason = fn()[:2]
        except ERRORS + (OSError,) as error: outcome, reason = 'inconclusive', str(error)
        rows.append(dict(subject=subject, outcome=outcome, reason=reason))
    def unknown(subject, reason): rows.append(dict(subject=subject, outcome='inconclusive', reason=reason))
    try:
        p, declared, start, end, observed = header(t)
        if rule == 'TS33-A01':
            review = inspection.review(t.get('validation_plan_review'), plan_binding(t), declared, start, t['structured_synthetic'])
            for key in ('scope', 'support', 'separation'):
                row('plan:' + key, lambda key=key: inspection.judgment(review, key))
        elif rule == 'TS33-A02':
            e = content.Evidence(t, obs['inventories']); vocab = vocabulary(); count = 0
            if e.o['unexpected_states']: unknown('surfaces', 'Unplanned supplied rendered states')
            for surface in e.surfaces():
                sid = surface['id']
                row(sid + ':syntax-attribution', lambda surface=surface: e.qualify(surface))
                try:
                    need(e.qualify(surface)[0] == 'pass', 'No qualified graph for vocabulary reading; syntax result retained separately')
                    if surface['reading']['status'] == 'absent': continue
                    graph = surface['processing']['flattened']; selected = terms(graph)
                    need(any(k == 'class' for k, _ in selected), 'No class in the complete nonempty graph')
                    count += 1
                    for kind, iri in selected:
                        row(sid + ':' + kind, lambda kind=kind, iri=iri: term_result(kind, iri, vocab))
                except ERRORS + (OSError,) as error: unknown(sid + ':vocabulary', str(error))
            if not count: unknown('markup', 'No qualified typed graph; absence never becomes C or NA')
        elif rule == 'TS33-A03':
            record, rich, when = native_record(t, p, start, end)
            obs['inventories']['native_record'] = record
            original = inspection.body(record['response'])
            obs['indexed_snapshot'] = dict(url=t['url'], retrieved_at=record['retrieved_at'],
                page_http_received_at=t['jsonld'].get('http_received_at'),
                page_dom_observed_at=[dict(id=state.get('id'), observed_at=state.get('observed_at'))
                    for state in t['jsonld'].get('states', []) if type(state) is dict],
                correspondence='not-established',
                last_crawl_time=original['inspectionResult']['indexStatusResult']['lastCrawlTime'],
                api_version='v1', backend_version='not-exposed', relationship='separate-indexed-snapshot',
                request_sha256=record['request']['sha256'], response_sha256=record['response']['sha256'],
                warning='lastCrawlTime is not the update time of every field; no freshness/current-state claim')
            verdict = rich.get('verdict')
            if verdict == 'FAIL': row('indexed:verdict', lambda: ('fail', 'Native rich-results verdict is FAIL'))
            elif verdict == 'PASS': row('indexed:verdict', lambda: ('pass', 'Native PASS for this indexed snapshot only'))
            else: unknown('indexed:verdict', 'Unknown/excluded/reserved native verdict: ' + str(verdict))
            if set(rich) - {'verdict', 'detectedItems'}: unknown('indexed:format', 'Unknown rich-results fields')
            groups = rich.get('detectedItems', []); need(type(groups) is list and len(groups) <= 64, 'Invalid/excessive native detected groups')
            found = []; messages = []; item_count = 0
            for gi, group in enumerate(groups):
                try:
                    need(type(group) is dict and present(group.get('richResultType')), 'Missing detected feature name')
                    found.append(group['richResultType'])
                    if set(group) - {'richResultType', 'items'}: unknown('indexed:group:' + str(gi), 'Unknown group fields')
                    items = group.get('items', []); need(type(items) is list and 1 <= len(items) <= 64, 'Missing/excessive native items')
                    for ii, item in enumerate(items):
                        try:
                            need(type(item) is dict and ('name' not in item or type(item['name']) is str), 'Malformed native item')
                            item_count += 1
                            if set(item) - {'name', 'issues'}: unknown('indexed:item:' + str(ii), 'Unknown item fields')
                            issues = item.get('issues', []); need(type(issues) is list and len(issues) <= 128, 'Invalid/excessive native issue list')
                            for ji, issue in enumerate(issues):
                                path = 'detectedItems/%d/items/%d/issues/%d' % (gi, ii, ji)
                                try:
                                    need(type(issue) is dict, 'Malformed native issue')
                                    severity = issue.get('severity')
                                    if severity == 'ERROR': row(path, lambda: ('fail', 'Native ERROR remains blocking even when documented'))
                                    elif severity == 'WARNING': row(path, lambda: ('pass', 'Native WARNING; exact-message qualification required separately'))
                                    else: unknown(path, 'Unknown native severity: ' + str(severity))
                                    need(present(issue.get('issueMessage')), 'Missing native issue text')
                                    if set(issue) - {'severity', 'issueMessage'}: unknown(path + ':format', 'Unknown issue fields')
                                    messages.append(dict(path=path, severity=severity, message_sha256=content.native.sha(issue['issueMessage'])))
                                except ERRORS as error: unknown(path, str(error))
                        except ERRORS as error: unknown('indexed:item:' + str(ii), str(error))
                except ERRORS as error: unknown('indexed:group:' + str(gi), str(error))
            need(len(messages) <= 256 and item_count <= 256, 'Native issue/item population exceeds bounded profile')
            if len(found) != len(set(found)): unknown('indexed:groups', 'Duplicate native feature groups')
            if not item_count or not set(p['features']) <= set(found):
                unknown('indexed:coverage', 'Planned feature absent/empty; not proof of unsupported use or absence of syntax errors')
            obs['native_messages'] = messages
            def qualify():
                review = inspection.review(t.get('validation_review'), review_binding(t), when, observed, t['structured_synthetic'])
                supplied = review.get('messages'); need(type(supplied) is list and len(supplied) <= 256, 'Missing/excessive message qualifications')
                need(all(type(x) is dict and present(x.get('path')) for x in supplied), 'Malformed message qualification')
                paths = [x['path'] for x in supplied]
                if len(paths) != len(set(paths)) or set(paths) != {m['path'] for m in messages}:
                    return 'fail', 'Complete supplied review omits, duplicates or invents native messages'
                for message in messages:
                    q = next(v for v in supplied if v['path'] == message['path'])
                    if q.get('severity') != message['severity'] or q.get('message_sha256') != message['message_sha256']:
                        return 'fail', 'Supplied classification/text contradicts native message: ' + message['path']
                    need(present(q.get('reason')) and q.get('decision') in ('accepted', 'correction-planned', 'contradiction'), 'Missing/unknown message decision')
                    if q['decision'] == 'contradiction': return 'fail', 'Bound message qualification records a contradiction'
                return inspection.judgment(review, 'interpretation')
            row('indexed:bound-message-review', qualify)
        else: need(False, 'Unsupported structured-validation rule')
    except ERRORS + (OSError,) as error: unknown('scope', str(error))
    obs['outcome'] = combine(rows)
    if diagnostics is not None: diagnostics.append(obs)
    return obs['outcome'], PREFIX + json.dumps({k: v for k, v in obs.items() if k != 'inventories'}, ensure_ascii=False, sort_keys=True)
