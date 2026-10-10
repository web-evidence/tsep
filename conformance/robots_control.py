"""TS04 policy/resource matrix and shared TS07 access interpretation. Apache-2.0."""
import hashlib
import json

import tsep
from conformance import robots
from conformance.http import Unknown, need


def present(value):
    return isinstance(value, str) and bool(value.strip())


def combine(rows):
    outcomes = [o for o, _ in rows]
    outcome = 'fail' if 'fail' in outcomes else 'inconclusive' if 'inconclusive' in outcomes else 'pass'
    return outcome, '; '.join(o+' — '+reason for o, reason in rows)


def plan(target):
    context, intent = target.get('context', {}), target.get('intent', {})
    need(all(present(context.get(k)) for k in ('network', 'bounds', 'tool', 'tool_version')), 'Contexte de collecte absent')
    need(tsep.timestamp(intent['declared_at']) <= tsep.timestamp(target['observed_at']), 'Intention postérieure à l’observation')
    need(present(intent.get('crawler')), 'Client HTTP non déclaré')
    policy = intent.get('robots_policy', {})
    need(policy.get('profile') in robots.PROFILES and present(policy.get('product_token')),
         'Profil robots explicite et product token requis')
    value = intent.get('robots_plan', {})
    origin, path = robots.address(value.get('origin'))
    need(path == '/' and robots.address(target['url']) == (origin, '/'), 'Cible hôte différente de l’origine du plan')
    need(present(value.get('required_resources_basis')), 'Justification de la population des ressources absente')
    rows = value.get('resources')
    need(isinstance(rows, list) and 0 < len(rows) <= 100, 'Matrice préalable de 1 à 100 ressources requise')
    seen = set()
    for row in rows:
        url = row['url']
        need(robots.address(url)[0] == origin and url not in seen, 'Ressource dupliquée ou d’une autre origine')
        seen.add(url)
        need(row.get('expected') in ('allow', 'disallow') and type(row.get('required')) is bool,
             'Politique attendue ou nécessité non déclarée')
        if row['required']:
            need(row['expected'] == 'allow', 'Ressource nécessaire déclarée interdite : intention contradictoire')
            need(robots.address(row.get('expected_final_url'))[0] == origin,
                 'Ressource finale d’une autre origine hors portée de cette matrice')
            statuses = row.get('terminal_statuses')
            need(isinstance(statuses, list) and statuses and len(statuses) == len(set(statuses))
                 and all(type(s) is int and 200 <= s < 300 for s in statuses),
                 'Statuts attendus de ressource absents ou non exploitables')
    return value


def policy_for(target, url, client_representation_only=False):
    intent = target['intent']
    policy = intent.get('robots_policy', {})
    record = target.get('robots', {})
    need(tsep.timestamp(intent['declared_at']) <= tsep.timestamp(record['observed_at'])
         <= tsep.timestamp(target['observed_at']), 'Capture robots hors période du plan')
    from conformance.evaluate import url_parts
    parts = url_parts(url)
    observation = robots.inspect_capture({
        'profile': policy.get('profile'), 'origin': parts.scheme+'://'+parts.netloc+'/',
        'target': url, 'product_token': policy.get('product_token'),
        'request_user_agent': intent['crawler'], 'declared_at': intent['declared_at'],
        'client_representation_only': client_representation_only,
        'observed_at': record['observed_at'], 'context': target['context'], 'http': record.get('http')})
    reading = observation.get('body_reading', {})
    lines = [(r['line'], r['field'], r['pattern']) for r in reading.get('winning_lines', [])]
    reason = observation['reason']+'; profil='+str(policy.get('profile'))+'; lignes='+json.dumps(lines, ensure_ascii=False)
    if policy.get('profile') == robots.GOOGLE_FIELDS:
        # Complete values remain in the retained robots response and reader output.
        # Bound the repeated per-resource explanation without hiding truncation.
        fields = reading.get('ignored_fields', [])
        preview = [{'line': row['line'], 'field': row['field'], 'value': row['value'][:160],
                    'value_truncated': len(row['value']) > 160} for row in fields[:16]]
        reason += ('; champs relevés hors portée accès / fields outside access scope='
                   + json.dumps(preview, ensure_ascii=False)
                   + '; champs supplémentaires / additional fields='+str(max(0, len(fields)-16))
                   + '; valeurs intégrales / complete values: retained robots response'
                   + '; registre / registry='+robots.FIELDS_SOURCE)
    return observation['decision'], reason


def directive_scope(intent):
    """Shared explicit product/client separation; absent field keeps legacy scope."""
    if 'directive_crawler' not in intent:
        return False
    policy = intent.get('robots_policy')
    need(intent['directive_crawler'] == 'googlebot' and isinstance(policy, dict) and
         isinstance(policy.get('product_token'), str) and policy['product_token'].lower() == 'googlebot',
         'Explicit directive crawler requires a matching robots product profile; HTTP agent is not the product token')
    return True


def ts04_policy_for(target, url):
    explicit = directive_scope(target['intent'])
    decision, reason = policy_for(target, url, client_representation_only=explicit)
    if explicit:
        reason += ('; directive_crawler=googlebot; policy applied only to HTTP client='
                   + target['intent']['crawler'] + '; actual Googlebot representation unobserved')
    return decision, reason


def policy_matrix(target, value):
    rows = []
    for expected in value['resources']:
        try:
            actual, reason = ts04_policy_for(target, expected['url'])
            outcome = 'inconclusive' if actual == 'unknown' else 'pass' if actual == expected['expected'] else 'fail'
            rows.append((outcome, expected['url']+': attendu='+expected['expected']+', observé='+actual+'; '+reason))
        except (Unknown, tsep.Invalid, KeyError, ValueError, TypeError) as error:
            rows.append(('inconclusive', expected['url']+': '+str(error)))
    return combine(rows)


def access_binding(target, document):
    value = {'intent': target['intent'], 'context': target['context'], 'url': document['url'],
             'observed_at': document['observed_at'], 'http': document['http']}
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def access_review(target, document):
    record = document.get('access_review', {})
    need(all(present(record.get(k)) for k in ('reviewer', 'reason', 'assistance'))
         and record.get('provenance') in ('human', 'human-assisted', 'synthetic-exercise'), 'Revue motivée de ressource absente')
    need(record.get('source_sha256') == access_binding(target, document), 'Revue non liée à ces preuves et intention')
    need(tsep.timestamp(record['observed_at']) >= tsep.timestamp(document['observed_at']), 'Revue antérieure à la réponse')
    outcome = record.get('outcome')
    need(outcome in ('no-obstacle', 'obstacle', 'inconclusive'), 'Décision de revue absente')
    return {'no-obstacle': 'pass', 'obstacle': 'fail', 'inconclusive': 'inconclusive'}[outcome], record['reason']


def resources(target, value):
    required = [r for r in value['resources'] if r['required']]
    if not required:
        record = value.get('no_required_resources', {})
        need(all(present(record.get(k)) for k in ('reviewer', 'reason'))
             and record.get('provenance') in ('human', 'human-assisted', 'synthetic-exercise'),
             'Absence de ressource nécessaire non justifiée par une revue fournie')
        need(tsep.timestamp(record['observed_at']) <= tsep.timestamp(target['intent']['declared_at']),
             'Revue d’inventaire postérieure au plan')
        return 'not-applicable', 'Aucune ressource nécessaire dans le périmètre explicitement revu : '+record['reason']
    documents = target.get('documents', [])
    need(isinstance(documents, list), 'Inventaire des réponses de ressources invalide')
    rows = []
    from conformance.evaluate import trace
    for expected in required:
        url = expected['url']
        local = []
        try:
            actual, reason = ts04_policy_for(target, url)
            local.append(('inconclusive' if actual == 'unknown' else 'pass' if actual == 'allow' else 'fail', reason))
        except (Unknown, tsep.Invalid, KeyError, ValueError, TypeError) as error:
            local.append(('inconclusive', str(error)))
        try:
            matching = [d for d in documents if isinstance(d, dict) and d.get('url') == url]
            need(len(matching) == 1, 'Réponse absente ou ambiguë pour '+url)
            doc = matching[0]
            need(tsep.timestamp(target['intent']['declared_at']) <= tsep.timestamp(doc['observed_at'])
                 <= tsep.timestamp(target['observed_at']), 'Réponse hors période du plan')
            final, status, _, _ = trace(doc.get('http'), url, target['intent']['crawler'])
            for hop in doc['http'][1:]:
                decision, detail = ts04_policy_for(target, hop['url'])
                local.append(('inconclusive' if decision == 'unknown' else 'pass' if decision == 'allow' else 'fail',
                              'Accès au saut '+hop['url']+': '+detail))
            if final != expected['expected_final_url'] or status not in expected['terminal_statuses']:
                local.append(('fail', 'Destination/statut contradictoire : '+final+' '+str(status)))
            else:
                local.append(access_review(target, doc))
        except (Unknown, tsep.Invalid, KeyError, ValueError, TypeError) as error:
            local.append(('inconclusive', str(error)))
        outcome, reason = combine(local)
        if 'directive_crawler' in target['intent']:
            reason += ('; HTTP observations refer to declared client=' + target['intent']['crawler']
                       + '; actual Googlebot HTTP access unobserved')
        rows.append((outcome, url+': '+reason))
    return combine(rows)


def assess(target, rule):
    try:
        value = plan(target)
        if rule == 'TS04-A01':
            return policy_matrix(target, value)
        need(rule == 'TS04-A02', 'Règle TS04 inconnue')
        return resources(target, value)
    except (Unknown, tsep.Invalid, KeyError, TypeError, ValueError, AttributeError) as error:
        return 'inconclusive', str(error)


def access_rule(target, final_url, status):
    """TS07: legacy inputs keep their fixed default; explicit profiles use TS04."""
    from conformance.evaluate import trace, url_parts, utf8_media, text_body
    intent = target['intent']
    need(intent.get('access_basis') == 'test-client-only', 'Access assumptions not declared')
    if status in (401, 403):
        return 'fail', 'Observed HTTP access denial to test client'
    directive_scope(intent)
    if 'robots_policy' in intent:
        actual, reason = policy_for(target, final_url, client_representation_only='directive_crawler' in intent)
        need(actual != 'unknown', reason)
        allowed = actual == 'allow'
    else:
        # Fixed legacy-exact-v1 default, not a favorable profile selected after capture.
        parts = url_parts(final_url)
        robots_url = parts.scheme+'://'+parts.netloc+'/robots.txt'
        record = target.get('robots', {})
        need(tsep.timestamp(record['observed_at']) <= tsep.timestamp(target['observed_at']), 'Robots capture postdates assessment')
        _, code, headers, body = trace(record.get('http'), robots_url, intent['crawler'])
        need(code == 200 and utf8_media(headers, ('text/plain',), default_utf8=True), 'Unsupported robots response; no default access inferred')
        allowed = robots.legacy_allowed(text_body(body), final_url, intent['crawler'])
    note = ('; directive_crawler=googlebot; policy applied only to HTTP client=' + intent['crawler']
            + '; actual Googlebot representation unobserved') if 'directive_crawler' in intent else ''
    if not allowed:
        return 'fail', 'Observed robots policy disallows this target crawler/path' + note
    review = target.get('access_review', {})
    need(status == 200 and review.get('outcome') == 'no-obstacle' and review.get('reason'), 'HTTP access unresolved or challenge not reviewed')
    need(tsep.timestamp(review['observed_at']) >= tsep.timestamp(target['observed_at']), 'Access review predates the HTTP capture')
    return 'pass', 'Robots allows path and no obstacle observed for declared test client; actual engine access unobserved' + note
