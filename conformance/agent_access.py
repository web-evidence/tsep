"""TS43 documented test-client behavior and reviewed server-log correlation.

Apache-2.0. Offline supplied evidence only; never authenticates an operator visit.
"""
from datetime import timedelta, timezone
import hashlib
import json
import re
from urllib.parse import urlsplit

import tsep
from conformance.agent_policy import digest, present, identifier, ERRORS, PROVENANCE
from conformance.http import need, Unknown, message, body_digest
from conformance.robots import address

VERSION = '1'


def origin(url):
    address(url)
    p = urlsplit(url)
    return p.scheme+'://'+p.netloc+'/'


def correlation_binding(target):
    return digest({k: target.get(k) for k in ('url', 'intent', 'http', 'logs')})


def attribution_binding(target):
    return digest({k: target.get(k) for k in ('url', 'intent', 'http', 'logs', 'execution')})


def client_binding(client, documents):
    return digest({'client': client, 'documents': [
        {k: d[k] for k in ('id', 'source_url', 'observed_at', 'sha256')} for d in documents]})


def reviewed(record, expected, earliest, observed):
    need(isinstance(record, dict) and record.get('provenance') in PROVENANCE
         and all(present(record.get(k)) for k in ('reviewer', 'assistance', 'reason')),
         'Missing supplied review/provenance')
    need(record.get('binding_sha256') == expected, 'Review does not bind these exact supplied inputs')
    need(earliest <= tsep.timestamp(record['observed_at']) <= observed,
         'Review outside evidence/assessment dates')


def header(target):
    p = target['intent']['agent_access']
    need(p['reader'] == 'agent-access-v1', 'Unsupported agent access reader')
    declared = tsep.timestamp(target['intent']['declared_at'])
    observed = tsep.timestamp(target['observed_at'])
    start, end = tsep.timestamp(p['window_start']), tsep.timestamp(p['window_end'])
    need(declared <= start < end <= observed and end-start <= timedelta(days=1),
         'Prior intent, bounded test window and assessment dates required')
    need(type(p.get('clock_skew_ms')) is int and 0 <= p['clock_skew_ms'] <= 30000,
         'Declare clock uncertainty 0–30000 ms')
    need(type(p.get('max_duration_ms')) is int and 1 <= p['max_duration_ms'] <= 60000,
         'Declare request duration 1–60000 ms')
    client = p['client']
    need(present(client.get('operator')) and client.get('actor_kind') in ('crawler', 'user-action'),
         'No documented HTTP client; control-only token cannot be impersonated')
    need(isinstance(client.get('product_token'), str)
         and re.fullmatch('[A-Za-z_-]{1,128}', client['product_token']), 'Literal product token required')
    ua = client.get('full_user_agent')
    need(isinstance(ua, str) and 0 < len(ua) <= 2048 and re.fullmatch('[\x20-\x7e]+', ua),
         'Complete explicit ASCII HTTP User-Agent required')
    origins = p.get('origins')
    need(isinstance(origins, list) and 0 < len(origins) <= 16
         and all(isinstance(o, str) and origin(o) == o for o in origins)
         and len(set(origins)) == len(origins) and origin(target['url']) in origins,
         'Declare distinct exact origins including the target')
    need(identifier(p.get('log_layer')), 'Explicit log layer required')
    field = p.get('id_header')
    need(isinstance(field, str) and re.fullmatch('[a-z][a-z0-9-]{0,79}', field),
         'Declare a lowercase response request-ID header')
    need(all(present(target.get('context', {}).get(k)) for k in ('network', 'bounds', 'tool', 'tool_version')),
         'Complete collection context required')
    return p, observed


def capture(target, plan):
    from conformance.evaluate import exchange, trace
    hops = target['http']; ua = plan['client']['full_user_agent']
    final, status, headers, body = trace(hops, target['url'], ua)
    views = []
    start, end = tsep.timestamp(plan['window_start']), tsep.timestamp(plan['window_end'])
    previous = start
    for hop in hops:
        sent, received = tsep.timestamp(hop['sent_at']), tsep.timestamp(hop['received_at'])
        need(previous <= sent <= received <= end
             and received-sent <= timedelta(milliseconds=plan['max_duration_ms']),
             'HTTP exchange outside declared order/window/duration')
        need(origin(hop['url']) in plan['origins'], 'Redirect origin outside prior scope')
        code, response_headers, _ = exchange(hop, hop['url'], ua)
        _, request_headers, _ = message(hop['request'])
        views.append({'url': hop['url'], 'status': code, 'response_headers': response_headers,
                      'request_headers': request_headers, 'sent': sent, 'received': received})
        previous = received
    return (final, status, headers, body), views


def documentation(target, plan, observed):
    client = plan['client']; refs = client.get('source_ids')
    need(isinstance(refs, list) and 0 < len(refs) <= 16 and all(identifier(s) for s in refs)
         and len(refs) == len(set(refs)), 'Distinct source references required')
    sources = target.get('client_documents')
    need(isinstance(sources, list) and 0 < len(sources) <= 64, 'Bounded client source documents required')
    for ref in refs:
        need(sum(isinstance(d, dict) and d.get('id') == ref for d in sources) == 1,
             'Missing or ambiguous client documentation source')
    docs = [d for d in sources if isinstance(d, dict) and d.get('id') in refs]
    age = plan.get('max_source_age_days')
    need(type(age) is int and 0 <= age <= 3660, 'Declare client-source maximum UTC calendar-day age')
    dates = []
    for doc in docs:
        raw = doc.get('raw_text')
        need(isinstance(raw, str) and 0 < len(raw.encode('utf-8')) <= 256*1024,
             'Exact UTF-8 source text required within bound')
        need(hashlib.sha256(raw.encode()).hexdigest() == doc.get('sha256'), 'Client source hash mismatch')
        u = urlsplit(doc['source_url'])
        need(u.scheme in ('http', 'https') and u.hostname and not u.username and not u.password
             and not re.search(r'[\s\x00-\x1f]', doc['source_url'])
             and (u.port is None or 0 < u.port <= 65535), 'Invalid client source URL')
        acquired = tsep.timestamp(doc['observed_at']).astimezone(timezone.utc)
        need(acquired <= observed and (observed.astimezone(timezone.utc).date()-acquired.date()).days <= age,
             'Client source future-dated or older than declared bound')
        dates.append(acquired)
    record = target.get('client_review')
    reviewed(record, client_binding(client, docs), max(dates), observed)
    judgment = record.get('full_user_agent')
    info = {'client': client, 'source_sha256': [d['sha256'] for d in docs],
            'source_urls': [d['source_url'] for d in docs], 'reviewer': record['reviewer'],
            'review_provenance': record['provenance']}
    if judgment == 'contradiction':
        return 'fail', 'Bound source review contradicts the declared full HTTP client', info
    need(judgment == 'supported', 'Documented full client remains unknown')
    return 'pass', 'Supplied review supports this exact HTTP client; source/reviewer not authenticated', info


def behavior(target, plan):
    (url, status, _, body), views = capture(target, plan)
    expected = plan.get('test_access')
    need(plan.get('operator_access') == 'allow', 'Declare authorized operator intent separately')
    need(isinstance(expected, dict) and expected.get('action') in ('allow', 'deny')
         and expected.get('policy_basis') in ('ua-only', 'identity-gated', 'other')
         and present(expected.get('reason')), 'Explicit prior treatment and basis for the test client required')
    wanted = expected.get('status')
    need(type(wanted) is int and ((expected['action'] == 'allow' and wanted == 200)
         or (expected['action'] == 'deny' and wanted in (401, 403))), 'Unsupported test response expectation')
    origin(expected['final_url'])
    info = {'test_expectation': expected, 'observed_status': status, 'final_url': url,
            'body_sha256': body_digest(body), 'hops': len(views),
            'operator_access': 'not-established', 'scope': 'test-client-only'}
    if status != wanted or url != expected['final_url']:
        return 'fail', 'Observed test response differs from prior test-client expectation', info
    wanted_body = expected.get('expected_body_sha256')
    if expected['action'] == 'allow' or wanted_body is not None:
        need(isinstance(wanted_body, str) and re.fullmatch('[a-f0-9]{64}', wanted_body),
             'A declared complete-body reference is required to qualify allowed test access')
        if body_digest(body) != wanted_body:
            return 'fail', 'Test body differs from the explicitly fixed reference, even if HTTP is 200', info
    return 'pass', 'Test client received its declared response; real operator access is not established', info


def logs(target, plan, observed, views):
    source = target['logs']
    need(source['reader'] == 'tsep-request-log-v1' and source.get('format') == 'native-jsonl',
         'Only native attributable JSONL log records are qualified')
    raw = source.get('raw_jsonl')
    need(isinstance(raw, str) and len(raw.encode()) <= 1024*1024, 'Exact bounded JSONL required')
    need(hashlib.sha256(raw.encode()).hexdigest() == source.get('sha256'), 'Log source hash mismatch')
    start, end = tsep.timestamp(source['window_start']), tsep.timestamp(source['window_end'])
    acquired = tsep.timestamp(source['observed_at'])
    need(source.get('complete') is True and start <= tsep.timestamp(plan['window_start'])
         and tsep.timestamp(plan['window_end']) <= end <= acquired <= observed,
         'Complete supplied log window covering the declared test is not established')
    need(source.get('origins') == plan['origins'] and source.get('layer') == plan['log_layer'],
         'Log export origin/layer differs from declared correlation scope')
    record = target.get('log_review')
    reviewed(record, correlation_binding(target), max(acquired, views[-1]['received']), observed)
    need(all(record.get(k) is True for k in ('server_generated_id', 'per_request_id',
              'client_facing', 'clock_bound_confirmed', 'complete')),
         'ID origin/freshness, client-facing layer, clock bound or export completeness unqualified')
    lines = raw.splitlines(); need(len(lines) <= 10000, 'Excessive log records')
    rows = []
    for line in lines:
        need(bool(line.strip()), 'Blank/incomplete JSONL record')
        r = tsep.parse_json(line.encode())
        need(isinstance(r, dict) and identifier(r.get('request_id'))
             and isinstance(r.get('method'), str) and re.fullmatch('[A-Z]{1,20}', r['method'])
             and present(r.get('user_agent')) and identifier(r.get('layer'))
             and type(r.get('status')) is int and 100 <= r['status'] <= 599,
             'Malformed native request log record')
        origin(r['url']); tsep.timestamp(r['request_at'])
        rows.append(r)
    return rows, source


def correlate(view, views, records, plan):
    field = plan['id_header']
    need(field not in view['request_headers'], 'Client-supplied request ID cannot establish independent server attribution')
    values = view['response_headers'].get(field)
    need(isinstance(values, list) and len(values) == 1 and identifier(values[0]),
         'One attributable response request ID is required')
    rid = values[0]
    need(sum(v['response_headers'].get(field) == [rid] for v in views) == 1,
         'Response request ID reused across test exchanges')
    found = [r for r in records if r['request_id'] == rid and r['layer'] == plan['log_layer']]
    need(len(found) == 1, 'No unique log candidate in the declared layer')
    r = found[0]; when = tsep.timestamp(r['request_at'])
    skew = timedelta(milliseconds=plan['clock_skew_ms'])
    need(view['sent']-skew <= when <= view['received']+skew,
         'Matching ID outside request clock window; stale/cache correlation refused')
    expected = {'url': view['url'], 'method': 'GET', 'user_agent': plan['client']['full_user_agent'],
                'status': view['status']}
    differences = {k: {'http': value, 'log': r[k]} for k, value in expected.items() if r[k] != value}
    info = {'request_id': rid, 'layer': plan['log_layer'], 'log_record': r,
            'differences': differences, 'sent_at': view['sent'].isoformat(),
            'received_at': view['received'].isoformat(), 'clock_skew_ms': plan['clock_skew_ms']}
    if differences:
        return 'fail', 'Bound in-window server record contradicts the captured exchange', info
    return 'pass', 'Unique reviewed in-window correlation; supplied logs and clock are not authenticated', info


def attribution(target, plan, observed):
    _, views = capture(target, plan)
    execution = target['execution']
    need(execution.get('origin') == 'assessor-test' and present(execution.get('initiator')),
         'Explicit test execution origin and initiator required')
    command = execution.get('command')
    need(isinstance(command, list) and 0 < len(command) <= 128
         and all(present(a) for a in command), 'Retain supplied command arguments without executing them')
    start, end = tsep.timestamp(execution['started_at']), tsep.timestamp(execution['ended_at'])
    need(tsep.timestamp(target['intent']['declared_at']) <= start <= views[0]['sent']
         and views[-1]['received'] <= end <= observed, 'Execution record does not bound the captured test')
    record = target.get('attribution')
    reviewed(record, attribution_binding(target), end, observed)
    info = {'execution_origin': execution['origin'], 'declared_operator_identity': record.get('operator_identity'),
            'claims_operator_visit': record.get('claims_operator_visit'), 'operator_access': 'not-established',
            'reviewer': record['reviewer'], 'review_provenance': record['provenance']}
    if record.get('claims_operator_visit') is True or record.get('operator_identity') == 'verified' or record.get('request_origin') == 'operator':
        return 'fail', 'An assessor-initiated test is misrepresented as a verified operator visit', info
    need(record.get('claims_operator_visit') is False and record.get('operator_identity') == 'not-verified'
         and record.get('request_origin') == 'assessor-test', 'Explicit unverified operator identity and test origin required')
    return 'pass', 'Test attribution retained; neither User-Agent nor a supplied IP establishes an operator visit', info


def assess(target, rule, *, diagnostics=None):
    obs = {'reader': 'agent-access-v1', 'rule': rule, 'rows': [],
           'limitation': 'Supplied test-client evidence only; sources, reviews, logs and execution origin unauthenticated. No actual operator access, identity, visit, citation or security certification established.'}
    def row(key, action):
        try:
            outcome, reason, details = action()
        except ERRORS as error:
            outcome, reason, details = 'inconclusive', str(error), {}
        obs['rows'].append(dict(details, subject=key, outcome=outcome, reason=reason))
    try:
        plan, observed = header(target)
        if rule == 'TS43-A01':
            row('documented-client', lambda: documentation(target, plan, observed))
            row('test-response', lambda: behavior(target, plan))
        elif rule == 'TS43-A02':
            _, views = capture(target, plan)
            records, _ = logs(target, plan, observed, views)
            for i, view in enumerate(views, 1):
                row('hop-'+str(i), lambda view=view: correlate(view, views, records, plan))
        elif rule == 'TS43-A03':
            row('request-attribution', lambda: attribution(target, plan, observed))
        else:
            raise Unknown('Unsupported agent access rule')
    except ERRORS as error:
        obs['rows'].append({'subject': 'context', 'outcome': 'inconclusive', 'reason': str(error)})
    states = [r['outcome'] for r in obs['rows']]
    result = 'fail' if 'fail' in states else 'inconclusive' if 'inconclusive' in states else 'pass'
    obs['outcome'] = result
    if diagnostics is not None:
        diagnostics.append(obs)
    return result, 'Agent access evidence / preuves accès agents: '+json.dumps(obs, ensure_ascii=False, sort_keys=True)
