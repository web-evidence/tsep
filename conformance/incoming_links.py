"""TS16 reader on supplied bounded evidence. Apache-2.0.

No crawl, authenticated selection, observed interaction or global orphan claim.
Each destination is interpreted within the prior supplied population.
"""
import base64
import hashlib
import json
import os
from datetime import timedelta
from urllib.parse import urlsplit

import tsep
from conformance.evaluate import trace, message
from conformance.source_link_policy import Surface
from conformance import essential_links_dom
from experiments import link_elements, url_resolution

PROFILE = 'incoming-document-links-v1'
PREFIX = 'Supplied incoming links / liens entrants fournis: '
ERRORS = (ValueError, TypeError, KeyError, OSError, AttributeError, OverflowError)


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def named(value):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 4096


def unknown(reason):
    return {'outcome': 'inconclusive', 'reason': str(reason)}


def exact_urls(values, origin, node):
    need(all(isinstance(u, str) and len(u) <= 4096 for u in values),
         'Bounded exact URL strings required')
    results = url_resolution.resolve([{'url': u, 'base': None} for u in values], node=node)['results']
    for text, row in zip(values, results):
        need(row['ok'] and row['protocol'] in ('http:', 'https:')
             and row['href'] == text and '#' not in text
             and not urlsplit(text).username and not urlsplit(text).password,
             'Exact credential-free fragment-free WHATWG HTTP(S) document required')
        need(row['origin'] == origin, 'Document outside the declared exact origin')
    return results


def header(target):
    need(type(target) is dict, 'Target must be an object')
    need(len(json.dumps(target, ensure_ascii=False, allow_nan=False).encode('utf-8')) <= 8*1024*1024,
         'Input exceeds bounded JSON profile')
    need(type(target.get('incoming_links_synthetic')) is bool, 'Explicit synthetic provenance required')
    context = target.get('context')
    need(type(context) is dict and all(named(context.get(k)) for k in ('network', 'bounds', 'tool', 'tool_version')),
         'Named capture context required')
    intent = target.get('intent')
    need(type(intent) is dict and type(intent.get('incoming_links')) is dict, 'Missing prior incoming-link plan')
    plan = intent['incoming_links']
    need(plan.get('reader') == PROFILE, 'Unsupported incoming-link profile')
    need(named(plan.get('selection_reason')) and named(intent.get('crawler')), 'Prior selection rationale and client required')
    declared, start, end, observed = [tsep.timestamp(v) for v in
        (intent['declared_at'], plan['window_start'], plan['window_end'], target['observed_at'])]
    need(declared <= start <= end <= observed and end-start <= timedelta(hours=24), 'Unqualified prior window chronology')
    need(type(plan.get('max_duration_ms')) is int and 0 < plan['max_duration_ms'] <= 30000,
         'Finite integer per-exchange duration bound required')
    node = os.environ.get('TSEP_SOURCE_NODE')
    need(named(node), 'Explicit qualified Node runtime unavailable')
    origin = plan.get('origin')
    need(named(origin), 'Explicit origin required')
    exact_urls([origin + '/'], origin, node)
    sources, destinations = plan.get('sources'), plan.get('destinations')
    need(type(sources) is list and 1 <= len(sources) <= 16, 'Bounded1..16source population required')
    need(type(destinations) is list and 1 <= len(destinations) <= 32, 'Bounded1..32important destinations required')
    need(all(type(d) is dict and set(d) == {'url', 'reason'} and named(d['reason']) for d in destinations),
         'Each destination needs an exact URL and supplied importance rationale')
    destination_urls = [d['url'] for d in destinations]
    need(all(type(u) is str for u in destination_urls) and len(set(destination_urls)) == len(destination_urls),
         'Distinct destination URLs required')
    total_states = 0
    for source in sources:
        need(type(source) is dict and set(source) == {'url', 'final_url', 'states'}, 'Source URL/final URL/state plan required')
        states = source['states']
        need(type(states) is list and 1 <= len(states) <= 16, 'Bounded1..16states per source required')
        need(all(type(s) is dict and set(s) == {'id', 'browser', 'browser_version', 'scenario', 'interaction'}
                 and all(named(v) for v in s.values()) and s['interaction'] in ('none', 'after-interaction') for s in states),
             'Named prior state, browser and explicit interaction class required')
        need(len({s['id'] for s in states}) == len(states) and any(s['interaction'] == 'none' for s in states),
             'Distinct states and at least one no-interaction state per source required')
        total_states += len(states)
    need(total_states <= 64, 'Total declared state bound exceeded')
    source_urls = [s['url'] for s in sources]
    need(all(type(u) is str for u in source_urls) and len(set(source_urls)) == len(source_urls), 'Distinct source URLs required')
    exact_urls(destination_urls + source_urls + [s['final_url'] for s in sources] + [target['url']], origin, node)
    incoming = target.get('incoming_links')
    need(type(incoming) is dict, 'Missing supplied incoming-link evidence')
    inventory = incoming.get('inventory')
    need(type(inventory) is dict and named(inventory.get('label')), 'Missing named original source inventory')
    encoded, digest = inventory.get('base64'), inventory.get('sha256')
    need(type(encoded) is str and len(encoded) <= 4*((131072+2)//3), 'Bounded original inventory required')
    raw = base64.b64decode(encoded, validate=True)
    need(len(raw) <= 131072 and base64.b64encode(raw).decode('ascii') == encoded, 'Canonical original inventory byte container required')
    need(isinstance(digest, str) and hashlib.sha256(raw).hexdigest() == digest == plan.get('inventory_sha256'),
         'Original inventory and prior plan fingerprints differ or are missing')
    need(tsep.timestamp(inventory['observed_at']) <= declared, 'Inventory postdates the plan binding its digest')
    text = raw.decode('utf-8')
    body = text[:-1] if text.endswith('\n') else text
    need(body.split('\n') == source_urls, 'Exact inventory lines differ from the ordered prior source population')
    documents = incoming.get('documents')
    need(type(documents) is list and len(documents) <= 48 and all(type(d) is dict and isinstance(d.get('url'), str) for d in documents),
         'Bounded supplied document records required')
    return plan, source_urls, destination_urls, documents, start, end, node


def capture(target, document, plan, start, end, node, required_final=None, source=False):
    hops = document.get('http')
    need(type(hops) is list and 1 <= len(hops) <= 16 and all(type(h) is dict for h in hops), 'Missing or unqualified HTTP exchange population')
    final, status, headers, body = trace(hops, document['url'], target['intent']['crawler'])
    exact_urls([h['url'] for h in hops] + [final], plan['origin'], node)
    # The inherited raw trace also checks request bytes, client and complete chain.
    # Require agreement with WHATWG for every actual redirect transition.
    transitions = []
    for hop in hops[:-1]:
        _, hdrs, _ = message(hop['response'], True)
        transitions.append({'url': hdrs['location'][0], 'base': hop['url']})
    if transitions:
        resolved = url_resolution.resolve(transitions, node=node)['results']
        need(all(r['ok'] and r['href'] == h['url'] for r, h in zip(resolved, hops[1:])), 'Redirect resolution differs from exact archived transition')
    previous = start
    for hop in hops:
        sent, received = tsep.timestamp(hop['sent_at']), tsep.timestamp(hop['received_at'])
        need(previous <= sent <= received <= end and received-sent <= timedelta(milliseconds=plan['max_duration_ms']),
             'HTTP chronology/duration outside the prior window')
        previous = received
    need(status != 206, 'Partial representation cannot establish a complete original')
    if source:
        need(status == 200 and final == required_final, 'No complete expected source HTTP200 document')
    return {'qualified': True, 'url': document['url'], 'final_url': final, 'status': status,
            'received_at': previous.isoformat(), 'headers': headers, 'body': body}


def source_surface(captured, destinations):
    result = {'kind': 'source', 'destinations': {u: unknown('Unavailable source') for u in destinations}}
    try:
        notes = []
        Surface(captured['headers'], captured['body'], 'html-tree-links-v2', destinations, destinations[0], [],
                document_url=captured['final_url'], requested_url=captured['url'], diagnostics=notes)
        note = notes[0]
        need('inventory' in note and 'hypotheses' in note, note.get('reason', 'Source interpretation unavailable'))
        result['source_sha256'] = note['body_sha256']
        readings = {}
        for mode in ('enabled', 'disabled'):
            read, decision = note['inventory']['readings'][mode], note['hypotheses'][mode]
            reasons = list(decision.get('unknowns', []))
            if not read['complete']:
                reasons.append('Incomplete source inventory')
            if read['parse_errors']:
                reasons.append('Reported HTML recovery unqualified')
            if any(r['namespace'] == link_elements.HTML and r['tag'] == 'base' and not r['template_indices'] and link_elements.attribute(r, 'href') is not None for r in read['records']):
                reasons.append('Active base outside initial closed source profile')
            if 'links' not in decision:
                reasons.append(decision.get('reason', 'Missing qualified link records'))
            readings[mode] = {'unknowns': list(dict.fromkeys(reasons)), 'links': decision.get('links', [])}
        for destination in destinations:
            rows, witnesses = [], []
            for mode, reading in readings.items():
                matches = [r for r in reading['links'] if r['tag'] == 'a' and r.get('destination') == destination]
                rows.append('inconclusive' if reading['unknowns'] else 'pass' if matches else 'fail')
                if matches and not reading['unknowns']:
                    link = matches[0]
                    witnesses.append({'source_url': captured['url'], 'source_final_url': captured['final_url'],
                        'surface': 'source-' + mode, 'raw_href': link['href'], 'resolved_document': destination,
                        'anchor_reference': {'source_sha256': note['body_sha256'], 'node_index': link['node_index'], 'body_span_bytes': link['body_span_bytes']}})
            outcome = rows[0] if len(set(rows)) == 1 else 'inconclusive'
            result['destinations'][destination] = {'outcome': outcome, 'witnesses': witnesses if outcome == 'pass' else [],
                'hypothesis_outcomes': dict(zip(('enabled', 'disabled'), rows))}
        result['hypothesis_unknowns'] = {m: r['unknowns'] for m, r in readings.items()}
    except ERRORS as error:
        result['reason'] = str(error)
    return result


def rendered_surfaces(target, document, prior, captured, destinations, plan):
    result = []
    render = document.get('render')
    states = render.get('states') if type(render) is dict else None
    if type(states) is not list or len(states) > 16:
        states = None
    for planned in prior['states']:
        row = {'kind': 'rendered', 'id': planned['id'], 'eligible': planned['interaction'] == 'none'}
        if not row['eligible']:
            row['reason'] = 'Provider-declared after-interaction state is diagnostic only'
            result.append(row)
            continue
        row['destinations'] = {u: unknown('Required no-interaction state unavailable') for u in destinations}
        matches = [s for s in states if type(s) is dict and s.get('id') == planned['id']] if states is not None else []
        if len(matches) != 1:
            row['reason'] = 'Required state missing, excessive or ambiguous'
            result.append(row)
            continue
        state = matches[0]
        if any(state.get(k) != planned[k] for k in ('browser', 'browser_version', 'interaction')):
            row['reason'] = 'Supplied state identity/interaction differs from the prior plan'
            result.append(row)
            continue
        value = essential_links_dom.assess({'state': state, 'document_url': captured['final_url'], 'destinations': destinations,
            'http': document['http'], 'crawler': target['intent']['crawler'], 'http_received_at': captured['received_at'],
            'window_end': plan['window_end'], 'synthetic': target['incoming_links_synthetic']})
        row['reason'] = value.get('reason')
        if value['outcome'] in ('pass', 'fail'):
            row['snapshot_sha256'] = value['snapshot_sha256']
            for url in destinations:
                matches = [w for w in value['witnesses'] if w['resolved_document'] == url]
                witness = []
                if matches:
                    w = matches[0]
                    witness = [{'source_url': captured['url'], 'source_final_url': captured['final_url'],
                        'surface': 'rendered-' + planned['id'], 'raw_href': w['raw_href'], 'resolved_document': url,
                        'anchor_reference': {'snapshot_sha256': value['snapshot_sha256'], 'node_id': w['node_id']}}]
                row['destinations'][url] = {'outcome': 'pass' if matches else 'fail', 'witnesses': witness}
        result.append(row)
    return result


def assess_target(target):
    result = {'kind': PROFILE, 'outcome': 'inconclusive', 'authenticates_evidence': False,
        'scope': 'Declared source population only; no site-wide orphan, actual crawl or indexing conclusion.',
        'source_content_identity': 'Not assessed: an HTTP200 error template may supply a valid navigation witness. No soft404 or expected-content identity detection.',
        'state_identity': 'provider-declared-no-interaction-not-observed', 'sources': [], 'destinations': []}
    try:
        plan, source_urls, urls, documents, start, end, node = header(target)
    except ERRORS as error:
        result['reason'] = str(error)
        return result
    groups = {}
    for document in documents:
        groups.setdefault(document['url'], []).append(document)
    result['unplanned_documents'] = sorted(set(groups) - set(source_urls) - set(urls))
    originals = {}
    for url in urls:
        try:
            need(len(groups.get(url, [])) == 1, 'Destination original missing or ambiguous')
            captured = capture(target, groups[url][0], plan, start, end, node)
            originals[url] = {k: v for k, v in captured.items() if k not in ('headers', 'body')}
        except ERRORS as error:
            originals[url] = {'qualified': False, 'reason': str(error), 'identity_verified': False, 'status': None}
    for prior in plan['sources']:
        row = {'url': prior['url'], 'pairs': {u: unknown('Source unavailable') for u in urls}, 'surfaces': []}
        try:
            need(len(groups.get(prior['url'], [])) == 1, 'Source original missing or ambiguous')
            document = groups[prior['url']][0]
            captured = capture(target, document, plan, start, end, node, required_final=prior['final_url'], source=True)
            row['http'] = {k: v for k, v in captured.items() if k not in ('headers', 'body')}
            others = [u for u in urls if u != captured['final_url']]
            if others:
                row['surfaces'] = [source_surface(captured, others)] + rendered_surfaces(target, document, prior, captured, others, plan)
            for url in urls:
                if url == captured['final_url']:
                    row['pairs'][url] = {'outcome': 'fail', 'self_excluded': True, 'reason': 'Same exact document cannot witness its own incoming link', 'witnesses': []}
                    continue
                eligible = [s['destinations'][url] for s in row['surfaces'] if s.get('eligible', True)]
                outcomes = [s['outcome'] for s in eligible]
                outcome = 'pass' if 'pass' in outcomes else 'fail' if outcomes and all(x == 'fail' for x in outcomes) else 'inconclusive'
                witnesses = [w for s in eligible if s['outcome'] == 'pass' for w in s.get('witnesses', [])]
                pair = {'outcome': outcome, 'witnesses': witnesses, 'surface_outcomes': outcomes}
                if outcome == 'pass' and originals[url].get('qualified') and originals[url]['final_url'] == captured['final_url']:
                    pair.update(outcome='inconclusive', witnesses=[], reason='Literal destination redirects back to this source document; pair identity unqualified')
                row['pairs'][url] = pair
        except ERRORS as error:
            row['reason'] = str(error)
        result['sources'].append(row)
    for url in urls:
        pairs = [s['pairs'][url] for s in result['sources']]
        positive = [p for p in pairs if p['outcome'] == 'pass']
        absent = bool(pairs) and all(p['outcome'] == 'fail' for p in pairs)
        original = originals[url]
        outcome = 'pass' if positive and original['qualified'] else 'fail' if absent else 'inconclusive'
        result['destinations'].append({'url': url, 'outcome': outcome, 'original': original,
            'bounded_absence': absent, 'witnesses': [w for p in positive for w in p['witnesses']],
            'reason': 'Qualified incoming witness and destination original' if outcome == 'pass' else
                'No witness within every eligible qualified surface of this prior population; not a site-wide orphan' if absent else
                'No complete qualified witness/original pair or bounded absence',
            'missing_original_note': None if original['qualified'] else 'Destination original/status not archived or unqualified; identity not verified. Bounded absence may also indicate a plan error.'})
    outcomes = [r['outcome'] for r in result['destinations']]
    result['outcome'] = 'fail' if 'fail' in outcomes else 'inconclusive' if 'inconclusive' in outcomes else 'pass'
    result['reason'] = 'Per-destination incoming evidence within the prior bounded selection only'
    if len(json.dumps(result, ensure_ascii=False).encode('utf-8')) > 4*1024*1024:
        return {'kind': PROFILE, 'outcome': 'inconclusive', 'authenticates_evidence': False, 'reason': 'Diagnostic exceeds bounded profile; no truncated conclusion'}
    return result


def assess(target, rule, *, diagnostics=None):
    result = assess_target(target) if rule == 'TS16-A01' else unknown('Unsupported incoming-link rule')
    if diagnostics is not None:
        diagnostics.append(result)
    return result['outcome'], PREFIX + json.dumps(result, ensure_ascii=False, sort_keys=True)
