"""TS42 declared usage governance, supplied reviews and bounded robots policy.

Apache-2.0. No provider registry, collection, identity or compliance inference.
"""
from datetime import timezone
import hashlib
import json
import re
from urllib.parse import urlsplit

import tsep
from conformance import robots
from conformance.http import Unknown, need

VERSION = '1'
PURPOSES = ('search', 'training', 'user-action', 'advertising', 'grounding', 'other')
KINDS = ('crawler', 'user-action', 'control-token')
PROVENANCE = ('human', 'human-assisted', 'synthetic-exercise')
ERRORS = (Unknown, tsep.Invalid, KeyError, TypeError, ValueError, AttributeError,
          OverflowError, RecursionError)


def present(value):
    return isinstance(value, str) and 0 < len(value.strip()) <= 8192


def identifier(value):
    return isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9_-]{1,80}', value)


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def owner_binding(target):
    return digest({'url': target['url'], 'intent': target['intent']})


def mapping_binding(mechanism, documents):
    return digest({'mechanism': mechanism, 'documents': [
        {k: d[k] for k in ('id', 'source_url', 'observed_at', 'sha256')} for d in documents]})


def header(target):
    observed = tsep.timestamp(target['observed_at']).astimezone(timezone.utc)
    declared = tsep.timestamp(target['intent']['declared_at'])
    need(declared <= observed, 'Intent postdates assessment')
    plan = target['intent']['agent_policy']
    need(plan['reader'] == 'agent-governance-v1', 'Unsupported governance reader')
    ms = plan['mechanisms']
    need(isinstance(ms, list) and 0 < len(ms) <= 32, 'Declare 1–32 mechanisms')
    ids = []
    for m in ms:
        need(isinstance(m, dict) and identifier(m.get('id')), 'Invalid mechanism identifier')
        ids.append(m['id'])
        need(present(m.get('operator')) and m.get('actor_kind') in KINDS,
             'Declare operator and crawler/user-action/control-token kind')
        token = m.get('product_token')
        need(isinstance(token, str) and re.fullmatch(r'[A-Za-z_-]{1,128}', token),
             'Declare a literal ASCII product token, not an HTTP User-Agent')
        need(m.get('mechanism') in ('robots-txt', 'other'), 'Unsupported mechanism declaration')
        purposes = m.get('purposes')
        need(isinstance(purposes, list) and purposes and len(purposes) <= len(PURPOSES)
             and all(p in PURPOSES for p in purposes) and len(set(purposes)) == len(purposes),
             'Declare distinct supported purpose labels')
        if 'other' in purposes:
            need(present(m.get('other_purpose')), 'Explain the other purpose')
        sources = m.get('source_ids')
        need(isinstance(sources, list) and 0 < len(sources) <= 16
             and all(identifier(s) for s in sources) and len(set(sources)) == len(sources),
             'Declare distinct operator source IDs')
    need(len(ids) == len(set(ids)), 'Duplicate mechanism identifier')
    return plan, observed


def source_mapping(target, plan, mechanism, observed):
    originals = target['agent_documents']
    need(isinstance(originals, list) and len(originals) <= 64, 'Missing/bounded operator sources')
    age = plan.get('max_source_age_days')
    need(type(age) is int and 0 <= age <= 3660, 'Declare maximum source age in UTC calendar days')
    docs = []
    # Source array order is part of the binding; IDs identify each required item.
    for source_id in mechanism['source_ids']:
        found = [d for d in originals if isinstance(d, dict) and d.get('id') == source_id]
        need(len(found) == 1, 'Missing or ambiguous operator source: '+source_id)
    docs = [d for d in originals if isinstance(d, dict) and d.get('id') in mechanism['source_ids']]
    dates = []
    for doc in docs:
        raw = doc.get('raw_text')
        need(isinstance(raw, str) and 0 < len(raw.encode('utf-8')) <= 256 * 1024,
             'Missing/excessive exact UTF-8 source text')
        need(hashlib.sha256(raw.encode('utf-8')).hexdigest() == doc.get('sha256'),
             'Operator source fingerprint mismatch')
        address = urlsplit(doc.get('source_url', ''))
        need(address.scheme in ('http', 'https') and address.hostname
             and not address.username and not address.password
             and not re.search(r'[\s\x00-\x1f]', doc.get('source_url', '')),
             'Invalid operator source URL')
        need(address.port is None or 0 < address.port <= 65535,
             'Invalid operator source port')
        acquired = tsep.timestamp(doc['observed_at']).astimezone(timezone.utc)
        need(acquired <= observed and (observed.date()-acquired.date()).days <= age,
             'Operator source is future-dated or exceeds declared age')
        dates.append(acquired)
    reviews = target.get('agent_reviews')
    need(isinstance(reviews, list) and len(reviews) <= 64, 'Missing/bounded documentation reviews')
    found = [r for r in reviews if isinstance(r, dict) and r.get('mechanism_id') == mechanism['id']]
    need(len(found) == 1, 'Missing/ambiguous documentation review')
    review = found[0]
    need(all(present(review.get(k)) for k in ('reviewer', 'assistance', 'reason'))
         and review.get('provenance') in PROVENANCE, 'Documentation review provenance missing')
    need(review.get('binding_sha256') == mapping_binding(mechanism, docs),
         'Documentation review is not bound to this mapping and these sources')
    reviewed = tsep.timestamp(review['observed_at'])
    need(max(dates) <= reviewed <= observed, 'Documentation review outside source/assessment dates')
    status = review.get('mapping')
    need(status in ('supported', 'contradiction', 'unknown'), 'Missing mapping judgment')
    info = {'mechanism_id': mechanism['id'], 'actor_kind': mechanism['actor_kind'],
            'product_token': mechanism['product_token'], 'purposes': mechanism['purposes'],
            'source_sha256': [d['sha256'] for d in docs], 'source_urls': [d['source_url'] for d in docs],
            'review_provenance': review['provenance'], 'reviewer': review['reviewer'],
            'robots_applicable': review.get('robots_applicable')}
    if status == 'contradiction':
        return 'fail', 'Supplied bound review contradicts the documented mapping: '+review['reason'], info
    need(status == 'supported' and review.get('complete') is True
         and type(review.get('robots_applicable')) is bool,
         'Mapping, completeness or robots applicability remains unknown')
    return 'pass', 'Supplied source interpretation retained; provider and reviewer are not authenticated', info


def decision_authority(target, plan, observed):
    owner = plan.get('owner'); delegates = plan.get('delegates')
    need(present(owner) and isinstance(delegates, list) and len(delegates) <= 32
         and all(present(d) for d in delegates) and len(set(delegates)) == len(delegates)
         and owner not in delegates, 'Declare owner and distinct named delegates')
    record = target['agent_decision']
    need(record.get('author') in [owner]+delegates
         and record.get('provenance') in PROVENANCE
         and all(present(record.get(k)) for k in ('assistance', 'reason')),
         'Decision author must be the declared owner/delegate, with provenance')
    need(record.get('binding_sha256') == owner_binding(target), 'Owner decision binding differs from target/intent')
    date = tsep.timestamp(record['observed_at'])
    need(tsep.timestamp(target['intent']['declared_at']) <= date <= observed,
         'Owner decision outside intent/assessment dates')
    if 'robots' in target:
        need(date <= tsep.timestamp(target['robots']['observed_at']) <= observed,
             'Owner decision postdates policy capture or capture postdates assessment')
    need(type(record.get('accepted')) is bool, 'Explicit owner acceptance required')
    return record['accepted']


def choices(plan, mechanisms):
    decisions = plan.get('decisions')
    need(isinstance(decisions, list) and len(decisions) <= 192, 'Missing/bounded usage decisions')
    wanted = [(m['id'], p) for m in mechanisms for p in m['purposes']]
    result = []
    for mid, purpose in wanted:
        found = [d for d in decisions if isinstance(d, dict)
                 and d.get('mechanism_id') == mid and d.get('purpose') == purpose]
        need(len(found) == 1, 'Missing or duplicate purpose decision: '+mid+'/'+purpose)
        d = found[0]
        need(d.get('choice') in ('allow', 'deny') and present(d.get('reason')),
             'Usage decision needs a choice and a reason')
        result.append(d)
    return result


def arbitration(plan, mechanisms, decisions):
    token = mechanisms[0]['product_token'].lower()
    records = plan.get('arbitrations')
    need(isinstance(records, list) and len(records) <= 32, 'Missing/bounded arbitration array')
    found = [r for r in records if isinstance(r, dict)
             and isinstance(r.get('product_token'), str) and r['product_token'].lower() == token]
    need(len(found) <= 1, 'Ambiguous product-token arbitration')
    original = {d['choice'] for d in decisions}
    if not found:
        return (next(iter(original)) if len(original) == 1 else None), None
    record = found[0]
    need(len(original) > 1 and record.get('choice') in ('allow', 'deny')
         and present(record.get('reason')), 'Arbitration must explicitly resolve conflicting usage choices')
    pairs = record.get('affected_pairs')
    need(isinstance(pairs, list) and all(isinstance(p, dict) and set(p) == {'mechanism_id', 'purpose'} for p in pairs),
         'Arbitration must enumerate all affected purpose pairs')
    named = [(p['mechanism_id'], p['purpose']) for p in pairs]
    wanted = [(d['mechanism_id'], d['purpose']) for d in decisions]
    need(len(named) == len(set(named)) and set(named) == set(wanted), 'Arbitration tradeoff scope differs')
    return record['choice'], record


def grouped(plan):
    result = {}
    # The same physical robots token cannot be split by operator or invented ID.
    for m in plan['mechanisms']:
        result.setdefault(m['product_token'].lower(), []).append(m)
    return result


def combine(rows):
    states = [r['outcome'] for r in rows]
    return 'fail' if 'fail' in states else 'inconclusive' if 'inconclusive' in states else 'pass'


def assess(target, rule, *, diagnostics=None):
    obs = {'reader': 'agent-governance-v1', 'rule': rule, 'rows': [],
           'limitation': 'Declared inventory and supplied reviews/decisions; no authenticated provider, owner, visitor, operator compliance, indexing or citation. Policy describes only the test-client representation.'}
    rows = obs['rows']
    def row(key, action):
        try:
            outcome, reason, details = action()
        except ERRORS as error:
            outcome, reason, details = 'inconclusive', str(error), {}
        rows.append(dict(details, subject=key, outcome=outcome, reason=reason))
    try:
        plan, observed = header(target)
        groups = grouped(plan)
        if rule == 'TS42-A01':
            for m in plan['mechanisms']:
                row(m['id'], lambda m=m: source_mapping(target, plan, m, observed))
        elif rule == 'TS42-A02':
            accepted = decision_authority(target, plan, observed)
            if not accepted:
                rows.append({'subject': 'owner', 'outcome': 'fail', 'reason': 'Supplied owner/delegate decision rejects this plan'})
            else:
                all_choices = choices(plan, plan['mechanisms'])
                need(len(all_choices) == len(plan['decisions']), 'Decision outside declared scope')
                records = plan.get('arbitrations')
                need(isinstance(records, list) and all(isinstance(r, dict)
                     and isinstance(r.get('product_token'), str) and r['product_token'].lower() in groups for r in records),
                     'Arbitration outside declared mechanisms')
                for token, ms in groups.items():
                    def governance(ms=ms):
                        ds = choices(plan, ms); effective, tradeoff = arbitration(plan, ms, ds)
                        return 'pass', 'Bound owner/delegate decision retained; conflicting wishes may still require arbitration', {'decisions': ds, 'effective_choice': effective, 'arbitration': tradeoff}
                    row(token, governance)
        elif rule == 'TS42-A03':
            need(decision_authority(target, plan, observed), 'No accepted owner/delegate decision')
            for token, ms in groups.items():
                def policy(ms=ms, token=token):
                    mapping = [source_mapping(target, plan, m, observed) for m in ms]
                    need(all(o == 'pass' for o, _, _ in mapping), 'Unestablished usage mapping')
                    need(all(m['mechanism'] == 'robots-txt' for m in ms)
                         and all(info['robots_applicable'] is True for _, _, info in mapping),
                         'Usage mechanism not qualified for robots Allow/Disallow')
                    ds = choices(plan, ms); effective, tradeoff = arbitration(plan, ms, ds)
                    need(effective is not None, 'Coupled purposes have opposite wishes without explicit owner arbitration')
                    need(plan.get('robots_profile') == robots.RFC, 'Only the declared bounded RFC robots profile is qualified')
                    record = target['robots']; acquired = tsep.timestamp(record['observed_at'])
                    need(tsep.timestamp(target['intent']['declared_at']) <= acquired <= observed,
                         'Robots capture outside prior intent and assessment')
                    robots.address(target['url'])  # Validate before retaining its exact authority.
                    parts = urlsplit(target['url'])
                    origin = parts.scheme+'://'+parts.netloc+'/'
                    reading = robots.inspect_capture({'profile': robots.RFC, 'origin': origin,
                        'target': target['url'], 'product_token': token,
                        'request_user_agent': target['intent']['crawler'], 'client_representation_only': True,
                        'declared_at': target['intent']['declared_at'], 'observed_at': record['observed_at'],
                        'context': target['context'], 'http': record.get('http')})
                    need(reading.get('http_status') == 200 and reading['decision'] in ('allow', 'disallow'),
                         'No qualified complete HTTP 200 robots policy: '+reading['reason'])
                    need(not reading.get('body_reading', {}).get('ignored_lines'),
                         'Robots contains ignored fields or syntax outside this usage-policy profile')
                    wanted = 'allow' if effective == 'allow' else 'disallow'
                    info = {'decisions': ds, 'effective_choice': effective, 'arbitration': tradeoff,
                            'mapping_evidence': [v for _, _, v in mapping], 'policy_reading': reading}
                    return ('pass' if reading['decision'] == wanted else 'fail'), 'Captured policy '+reading['decision']+'; adopted owner choice '+effective, info
                row(token, policy)
        else:
            raise Unknown('Unsupported agent-policy rule')
    except ERRORS as error:
        rows.append({'subject': 'context', 'outcome': 'inconclusive', 'reason': str(error)})
    result = combine(rows)
    obs['outcome'] = result
    if diagnostics is not None:
        diagnostics.append(obs)
    return result, 'Agent usage governance / gouvernance des usages agents: '+json.dumps(obs, ensure_ascii=False, sort_keys=True)
