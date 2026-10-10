#!/usr/bin/env python3
"""Offline URL Inspection comparison, never a TS08/TS12 verdict. Apache-2.0."""
import argparse
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
from html import escape
from pathlib import Path
import re
import sys
import tempfile
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from adapters import captures, package, replay as replay_module
from adapters.package import inventory, json_bytes, publish, regular, seal
from conformance import canonical, redirects
from provenance.runtime import loaded_sources

VERSION = '1'
ENUMS = {
    'verdict': {'VERDICT_UNSPECIFIED', 'PASS', 'PARTIAL', 'FAIL', 'NEUTRAL'},
    'robotsTxtState': {'ROBOTS_TXT_STATE_UNSPECIFIED', 'ALLOWED', 'DISALLOWED'},
    'indexingState': {'INDEXING_STATE_UNSPECIFIED', 'INDEXING_ALLOWED', 'BLOCKED_BY_META_TAG',
                      'BLOCKED_BY_HTTP_HEADER', 'BLOCKED_BY_ROBOTS_TXT'},
    'pageFetchState': {'PAGE_FETCH_STATE_UNSPECIFIED', 'SUCCESSFUL', 'SOFT_404', 'BLOCKED_ROBOTS_TXT',
                       'NOT_FOUND', 'ACCESS_DENIED', 'SERVER_ERROR', 'REDIRECT_ERROR', 'ACCESS_FORBIDDEN',
                       'BLOCKED_4XX', 'INTERNAL_CRAWL_ERROR', 'INVALID_URL'},
    'crawledAs': {'CRAWLING_USER_AGENT_UNSPECIFIED', 'DESKTOP', 'MOBILE'},
}
FIELDS = list(ENUMS) + ['coverageState', 'lastCrawlTime', 'googleCanonical', 'userCanonical']


def now():
    return datetime.now(timezone.utc).isoformat()


def sources():
    return dict(captures.source_files(), **loaded_sources(ROOT, {
        'diagnostics/search_console.py': sys.modules[__name__],
        'adapters/package.py': package, 'adapters/replay.py': replay_module}))


def stamp(value):
    """Preserve nanosecond ordering; datetime alone truncates beyond microseconds."""
    match = re.fullmatch(r'(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(?:\.(\d{1,9}))?(Z|[+-]\d\d:\d\d)', value) if isinstance(value, str) else None
    tsep.require(match is not None, 'Expected an RFC3339 timestamp with timezone and at most nine fractional digits')
    base = tsep.timestamp(match[1]+match[3])
    delta = base - datetime(1970, 1, 1, tzinfo=timezone.utc)
    return Decimal(delta.days*86400+delta.seconds) + Decimal('0.'+(match[2] or '0'))


def relation(left, right):
    if left is None or right is None:
        return 'unavailable'
    try:
        a, b = stamp(left), stamp(right)
        return 'before' if a < b else 'after' if a > b else 'same-time'
    except (ValueError, TypeError):
        return 'unavailable'


def field(data, key):
    if key not in data:
        return {'state': 'absent', 'value': None}
    value = data[key]
    result = {'state': 'present', 'value': value}
    if not isinstance(value, str):
        result['state'] = 'invalid'
    elif not value:
        result['state'] = 'empty'
    elif key in ENUMS:
        if value.endswith('_UNSPECIFIED') and value in ENUMS[key]:
            result['state'] = 'unspecified'
        elif value not in ENUMS[key] or value in ('PARTIAL', 'BLOCKED_BY_ROBOTS_TXT'):
            result['state'] = 'unknown-value'  # Includes reserved values; never turn them into a pass.
    elif key == 'lastCrawlTime' or key in ('googleCanonical', 'userCanonical'):
        try:
            stamp(value) if key == 'lastCrawlTime' else redirects.url(value)
        except (ValueError, TypeError):
            result['state'] = 'invalid'
    return result


def equal(left, right):
    if left.get('state') != 'present' or right.get('state') != 'present':
        return 'unavailable'
    return 'equal' if left['value'] == right['value'] else 'different'


def check_request(request):
    tsep.require(isinstance(request, dict) and {'inspectionUrl', 'siteUrl'} <= set(request)
                 and set(request) <= {'inspectionUrl', 'siteUrl', 'languageCode'},
                 'Expected the original inspection request body, without credentials/headers')
    inspection = redirects.url(request['inspectionUrl'])
    url = urlsplit(inspection)
    site = request['siteUrl']
    tsep.require(isinstance(site, str), 'Missing Search Console property')
    if site.startswith('sc-domain:'):
        domain = site[len('sc-domain:'):]
        tsep.require(re.fullmatch(r'[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?', domain)
                     and all(label and len(label) <= 63 and not label.startswith('-') and not label.endswith('-') for label in domain.split('.')),
                     'Unsupported domain property syntax')
        hostname = url.hostname.lower(); domain = domain.lower()
        tsep.require(hostname == domain or hostname.endswith('.'+domain), 'Inspection URL is outside the declared domain property')
    else:
        prefix = urlsplit(redirects.url(site))
        tsep.require(not prefix.query and prefix.path.endswith('/'), 'URL-prefix property must end with / and have no query')
        for path in (url.path, prefix.path):
            dots = re.sub('%2e', '.', path, flags=re.I)
            tsep.require(not re.search('%(?:2f|5c)', path, re.I) and
                         not any(segment in ('.', '..') for segment in dots.split('/')),
                         'Ambiguous path outside bounded URL-prefix comparison')
        def origin(parts):
            return parts.scheme.lower(), parts.hostname.lower(), parts.port or (443 if parts.scheme == 'https' else 80)
        tsep.require(origin(url) == origin(prefix) and url.path.startswith(prefix.path), 'Inspection URL is outside the declared URL-prefix property')
    if 'languageCode' in request:
        tsep.require(isinstance(request['languageCode'], str) and request['languageCode'].strip(), 'Invalid language code')
    return inspection


def observation(root):
    root = Path(root)
    raw = regular(root/'manifest.json', tsep.MAX_JSON_BYTES)
    meta = tsep.parse_json(raw)
    tsep.require(set(meta) == {'kind', 'format_version', 'provenance', 'description', 'retrieved_at',
                               'http_status', 'request_sha256', 'response_sha256', 'change'},
                 'Unknown/missing observation manifest fields')
    tsep.require(meta['kind'] == 'tsep-url-inspection-observation' and meta['format_version'] == VERSION,
                 'Unsupported URL Inspection observation')
    tsep.require(meta['provenance'] in ('supplied-google-api', 'synthetic-exercise')
                 and redirects.present(meta['description']), 'Describe the actual observation provenance')
    tsep.require(stamp(meta['retrieved_at']) <= stamp(now()), 'Inspection retrieval is future-dated')
    tsep.require(type(meta['http_status']) is int and 100 <= meta['http_status'] <= 599, 'Invalid supplied HTTP status')
    files = {'manifest.json': raw}
    for name in ('request', 'response'):
        files[name+'.json'] = regular(root/(name+'.json'), tsep.MAX_JSON_BYTES)
        tsep.require(hashlib.sha256(files[name+'.json']).hexdigest() == meta[name+'_sha256'], 'Changed '+name+' bytes')
    request = tsep.parse_json(files['request.json'])
    response = tsep.parse_json(files['response.json'])
    url = check_request(request)
    change = meta['change']
    if change is not None:
        tsep.require(isinstance(change, dict) and set(change) == {'occurred_at', 'description', 'evidence_sha256'}
                     and redirects.present(change['description']), 'Describe the actual change and its evidence')
        tsep.require(stamp(change['occurred_at']) <= stamp(now()), 'Change is future-dated')
        files['change-evidence.txt'] = regular(root/'change-evidence.txt', tsep.MAX_JSON_BYTES)
        tsep.require(files['change-evidence.txt'].strip() and
                     hashlib.sha256(files['change-evidence.txt']).hexdigest() == change['evidence_sha256'],
                     'Missing/changed change evidence')
    return meta, request, response, url, files


def engine_state(response, status, retrieved):
    result = response.get('inspectionResult') if isinstance(response, dict) else None
    index = result.get('indexStatusResult') if isinstance(result, dict) else None
    usable = status == 200 and isinstance(index, dict) and not (isinstance(response, dict) and 'error' in response)
    fields = {k: field(index if usable else {}, k) for k in FIELDS}
    state = 'recorded' if usable else 'api-error' if status != 200 else 'missing-or-malformed-index-result'
    crawl = fields['lastCrawlTime']
    chronology = relation(crawl['value'], retrieved) if crawl['state'] == 'present' else 'unavailable'
    if chronology == 'after':
        chronology = 'inconsistent-crawl-after-retrieval'
    return {'state': state, 'http_status': status, 'fields': fields, 'crawl_vs_retrieval': chronology,
            'google_vs_user_canonical': equal(fields['googleCanonical'], fields['userCanonical']),
            'uninterpreted_index_fields': sorted(set(index)-set(FIELDS)) if isinstance(index, dict) else [],
            'raw_response_retained': True, 'live_test': False}


def technical(data, report, url):
    matches = []
    for target in data['targets']:
        members = target.get('intent', {}).get('canonical', {}).get('members', [])
        if target['url'] == url or any(m.get('url') == url for m in members):
            matches.append(target)
    tsep.require(len(matches) == 1, 'Inspection URL has no unique exact target/member in the technical input')
    target = matches[0]
    docs = [d for d in target.get('documents', []) if d.get('url') == url]
    doc = docs[0] if len(docs) == 1 else target if target.get('url') == url and 'http' in target else None
    intent = target.get('intent', {})
    preferred = intent.get('canonical', {}).get('preferred_url')
    result = {'assessment_target': target['url'], 'inspected_url': url,
              'intent_declared_at': intent.get('declared_at'),
              'source_observed_at': doc.get('observed_at') if doc else None,
              'assessment_end': target.get('observed_at'),
              'canonical_intent': field({'googleCanonical': preferred} if preferred is not None else {}, 'googleCanonical'),
              'indexing_intent': intent.get('indexing'),
              'http_client': intent.get('crawler'),
              'render_browser': doc.get('render', {}).get('browser') if doc else None,
              'context': target.get('context'), 'canonical_signals': [],
              'recorded_atomic_results': [a for a in report.get('atomic_results', []) if a['target'] == target['url']],
              'atomic_result_scope': 'Recorded assessment target/family, not automatically a per-inspected-URL verdict'}
    member = next((m for m in intent.get('canonical', {}).get('members', []) if m.get('url') == url), None)
    if member is not None:
        try:
            bound_doc = canonical.capture(target, target.get('documents'), url)
            final, headers, source, rendered = canonical.surfaces(target, bound_doc, member['rendering'])
            result['source_final_url'] = final
            try:
                values = canonical.header_canonicals(headers)
                result['canonical_signals'].append({'surface': 'HTTP Link', 'values': [[v, True] for v in values]})
            except canonical.ERRORS as error:
                result['canonical_signals'].append({'surface': 'HTTP Link', 'unavailable_reason': str(error)})
            for label, rows in (('HTML source', source), ('Rendered state', rendered)):
                for parser, error in rows:
                    entry = {'surface': label}
                    try:
                        if error:
                            raise ValueError(error)
                        entry['values'] = [list(pair) for pair in parser.canonicals]
                    except canonical.ERRORS as exc:
                        entry['unavailable_reason'] = str(exc)
                    result['canonical_signals'].append(entry)
        except canonical.ERRORS as error:
            result['canonical_signals'].append({'surface': 'Technical canonical', 'unavailable_reason': str(error)})
    return result


def compare(meta, request, engine, local):
    fields = engine['fields']
    crawl = fields['lastCrawlTime']['value'] if fields['lastCrawlTime']['state'] == 'present' else None
    if engine['crawl_vs_retrieval'] == 'inconsistent-crawl-after-retrieval':
        crawl = None
    change = meta['change']
    permission = {'INDEXING_ALLOWED': 'allow', 'BLOCKED_BY_META_TAG': 'exclude',
                  'BLOCKED_BY_HTTP_HEADER': 'exclude'}.get(fields['indexingState']['value']) if fields['indexingState']['state'] == 'present' else None
    permission_comparison = ('equal' if permission == local['indexing_intent'] else 'different') if (
        permission is not None and local['indexing_intent'] in ('allow', 'exclude')) else 'unavailable'
    signals = []
    for row in local['canonical_signals']:
        for value, valid in row.get('values', []):
            signals.append({'surface': row['surface'], 'value': value, 'valid_in_reader': valid,
                            'google_comparison': equal(fields['googleCanonical'], {'state': 'present' if valid else 'invalid', 'value': value})})
    return {'kind': 'tsep-search-console-comparison-only', 'diagnostic_version': VERSION,
            'provenance': meta['provenance'], 'inspection_url': request['inspectionUrl'], 'property': request['siteUrl'],
            'retrieved_at': meta['retrieved_at'], 'change': change, 'engine': engine, 'technical': local,
            'comparisons': {'google_vs_declared_preference': equal(fields['googleCanonical'], local['canonical_intent']),
                            'user_vs_declared_preference': equal(fields['userCanonical'], local['canonical_intent']),
                            'local_canonical_signals': signals,
                            'indexing_permission_vs_intent': permission_comparison,
                            'crawl_vs_technical_source': relation(crawl, local['source_observed_at']),
                            'crawl_vs_change': relation(crawl, change['occurred_at'] if change else None),
                            'change_vs_technical_source': relation(change['occurred_at'] if change else None, local['source_observed_at'])},
            'network_requests': 0, 'tsep_verdict_created': False,
            'limitations': ['Supplied request/response binding and dates, not authenticated Google origin or account ownership.',
                'Inspection API data concerns the indexed version, not a live URL test.',
                'A literal canonical difference is not automatically a regression, technical failure or causal effect.',
                'Absent/empty/unknown fields remain unavailable; indexing permission is not indexing itself.',
                'Later crawl does not prove that Google saw the same representation as the technical client.',
                'lastCrawlTime is not an update timestamp for every returned inspection field.',
                'A later crawl or equal canonical does not demonstrate incorporation of a change; processing may lag or the value may predate the change.',
                'No TS08/TS12 verdict, ranking claim, whole-site claim or independent human review is created.']}


def render(value, language):
    fr = language == 'fr'
    title = 'Inspection Google et preuves TSEP' if fr else 'Google inspection and TSEP evidence'
    synthetic = value['provenance'] == 'synthetic-exercise'
    label = ('EXEMPLE SYNTHÉTIQUE — aucun appel Google' if fr else 'SYNTHETIC EXAMPLE — no Google request') if synthetic else (
        'Réponse API fournie — origine non authentifiée' if fr else 'Supplied API response — origin not authenticated')
    html = '<!doctype html><html lang="'+language+'"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
    html += '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'">'
    html += '<title>'+title+'</title><style>body{font:17px/1.5 system-ui;max-width:1120px;margin:36px auto;padding:0 20px;color:#172b38;background:#f7f9fa}aside{background:#fff1ce;padding:18px;border-left:5px solid #a96800}table{width:100%;border-collapse:collapse;background:white;margin:18px 0}th,td{border:1px solid #bdc9d0;padding:12px;text-align:left;overflow-wrap:anywhere}pre{white-space:pre-wrap;overflow-wrap:anywhere}summary{cursor:pointer;font-weight:650}a{color:#175797}</style><body>'
    html += '<h1>'+title+'</h1><aside><strong>'+label+'</strong><p>'+(
        'Rapprochement de données datées. Aucun verdict TS08/TS12 ni test en direct. Une différence exige une analyse.' if fr else
        'Comparison of dated evidence. No TS08/TS12 verdict or live test. A difference requires analysis.')+'</p></aside>'
    html += '<p>'+escape(value['inspection_url'])+'</p><p>'+escape(value['property'])+'</p>'
    html += '<table><caption>'+('Clients et représentations' if fr else 'Clients and representations')+'</caption><tr><th>'+('Capture technique HTTP' if fr else 'Technical HTTP capture')+'</th><th>'+('Navigateur de rendu fourni' if fr else 'Supplied rendering browser')+'</th><th>'+('Type de robot rapporté par Google' if fr else 'Crawler type reported by Google')+'</th></tr><tr>'
    for item in (value['technical']['http_client'], value['technical']['render_browser'], value['engine']['fields']['crawledAs']['value']):
        html += '<td>'+escape(str(item) if item is not None else ('Non fourni' if fr else 'Not supplied'))+'</td>'
    html += '</tr></table><p>'+('Des clients ou états rendus différents peuvent recevoir des représentations différentes. Cet import ne tranche pas cette hypothèse.' if fr else 'Different clients or rendered states may receive different representations. This import does not resolve that possibility.')+'</p>'
    html += '<table><caption>'+('Dates conservées' if fr else 'Retained dates')+'</caption><tr><th>'+('Événement' if fr else 'Event')+'</th><th>Date</th></tr>'
    rows = [('Intention / Intent',value['technical']['intent_declared_at']),('Capture technique / Technical capture',value['technical']['source_observed_at']),('Dernier crawl rapporté / Reported last crawl',value['engine']['fields']['lastCrawlTime']['value']),('Inspection récupérée / Inspection retrieved',value['retrieved_at']),('Changement documenté / Documented change',value['change']['occurred_at'] if value['change'] else None)]
    for name, item in rows:
        html += '<tr><th>'+name+'</th><td>'+escape(str(item) if item is not None else ('Non fourni' if fr else 'Not supplied'))+'</td></tr>'
    html += '</table><table><caption>'+('Canonical : valeurs et rapprochements' if fr else 'Canonical values and comparisons')+'</caption><tr><th>Signal</th><th>'+('Valeur' if fr else 'Value')+'</th><th>'+('État du champ' if fr else 'Field state')+'</th></tr>'
    for name, item in [('Intention TSEP',value['technical']['canonical_intent']),('Google userCanonical',value['engine']['fields']['userCanonical']),('Google googleCanonical',value['engine']['fields']['googleCanonical'])]:
        html += '<tr><th>'+name+'</th><td>'+escape(str(item['value']) if item['value'] is not None else '—')+'</td><td>'+escape(item['state'])+'</td></tr>'
    html += '</table><h2>'+('Ce que l’on peut rapprocher' if fr else 'What can be compared')+'</h2>'
    labels = {'equal': 'Valeurs identiques', 'different': 'Valeurs différentes', 'unavailable': 'Comparaison impossible',
              'before': 'Antérieur', 'after': 'Postérieur', 'same-time': 'Même instant'} if fr else {
              'equal': 'Equal values', 'different': 'Different values', 'unavailable': 'Unavailable',
              'before': 'Before', 'after': 'After', 'same-time': 'Same instant'}
    comparisons = value['comparisons']
    html += '<table><tr><th>'+('Rapprochement' if fr else 'Comparison')+'</th><th>'+('Lecture' if fr else 'Reading')+'</th></tr>'
    for label, key in [('Canonical Google / préférence déclarée' if fr else 'Google canonical / declared preference','google_vs_declared_preference'),
                       ('Canonical utilisateur rapportée / préférence déclarée' if fr else 'Reported user canonical / declared preference','user_vs_declared_preference'),
                       ('Dernier crawl / capture technique' if fr else 'Last crawl / technical capture','crawl_vs_technical_source'),
                       ('Dernier crawl / changement documenté' if fr else 'Last crawl / documented change','crawl_vs_change'),
                       ('Permission d’indexation / intention' if fr else 'Indexing permission / intent','indexing_permission_vs_intent')]:
        html += '<tr><th>'+label+'</th><td>'+labels[comparisons[key]]+'</td></tr>'
    html += '</table><p>'+('Les valeurs sont comparées telles quelles, sans normaliser les URL. La date de crawl ne date pas chacun des champs Google. Une permission d’indexation ne prouve pas une indexation.' if fr else
        'Values are compared literally, without URL normalization. Crawl time does not timestamp every Google field. Indexing permission does not establish indexing.')+'</p><p>'+(
        'Même après un crawl ultérieur, un accord ne prouve pas la prise en compte du changement et un écart peut refléter un traitement encore différé. Aucune cause n’est déduite ici.' if fr else
        'Even after a later crawl, agreement does not prove that a change was incorporated, and a difference may reflect pending processing. No cause is inferred here.')+'</p>'
    html += '<h2>'+('Signaux de la capture technique' if fr else 'Technical capture signals')+'</h2><table><tr><th>Surface</th><th>'+('Déclarations ou limite' if fr else 'Declarations or limitation')+'</th></tr>'
    for item in value['technical']['canonical_signals']:
        detail = item.get('unavailable_reason') or (json_bytes(item['values']).decode().strip() if item.get('values') else ('Aucune déclaration extraite sur cette surface' if fr else 'No declaration extracted on this surface'))
        html += '<tr><th>'+escape(item['surface'])+'</th><td>'+escape(detail)+'</td></tr>'
    if not value['technical']['canonical_signals']:
        html += '<tr><td colspan="2">'+('Aucune famille canonical exploitable dans ce paquet technique.' if fr else 'No usable canonical family in this technical bundle.')+'</td></tr>'
    html += '</table><h2>'+('Champs rapportés par Google' if fr else 'Fields reported by Google')+'</h2><p>'+escape(value['engine']['state'])+' · HTTP '+str(value['engine']['http_status'])+'</p><table><tr><th>Champ / Field</th><th>Valeur / Value</th><th>État / State</th></tr>'
    for name, item in value['engine']['fields'].items():
        label = ('Verdict rapporté par Google (API)' if fr else 'Verdict reported by Google (API)') if name == 'verdict' else name
        html += '<tr><th>'+escape(label)+'</th><td>'+escape(str(item['value']) if item['value'] is not None else '—')+'</td><td>'+escape(item['state'])+'</td></tr>'
    html += '</table>'
    for name, item in [('Rapprochements / Comparisons',value['comparisons']),('Champs Google / Google fields',value['engine']),('Preuves techniques / Technical evidence',value['technical']),('Limites / Limitations',value['limitations'])]:
        html += '<details><summary>'+name+'</summary><pre>'+escape(json_bytes(item).decode())+'</pre></details>'
    html += '<p><a href="observation/request.json">Requête originale / Original request</a> · <a href="observation/response.json">Réponse originale / Original response</a> · <a href="comparison.json">JSON</a></p></body></html>'
    return html


def build(observation_dir, technical_bundle, output):
    output = Path(output); technical_bundle = Path(technical_bundle)
    source_files = sources()
    meta, request, response, url, original_files = observation(observation_dir)
    entries = inventory(technical_bundle)
    metadata = tsep.read_json(technical_bundle/'import.json')
    synthetic = meta['provenance'] == 'synthetic-exercise'
    tsep.require(synthetic == (metadata['access'] == 'synthetic'), 'Do not mix synthetic and real evidence')
    tsep.require(output.parent.is_dir() and not output.exists() and not output.is_symlink(),
                 'Choose a NEW output directory with an existing parent')
    with tempfile.TemporaryDirectory(prefix='.tsep-inspection-', dir=output.parent) as folder:
        stage = Path(folder)
        # Recompute the technical package under its exact tools before comparison.
        replayed = replay_module.replay(technical_bundle, stage/'technical-replay')
        source_input = tsep.read_json(technical_bundle/'input.json')
        report = tsep.read_json(technical_bundle/'report.json')
        local = technical(source_input, report, url)
        engine = engine_state(response, meta['http_status'], meta['retrieved_at'])
        value = compare(meta, request, engine, local)
        value['technical_replayed'] = replayed['replayed']
        (stage/'observation').mkdir()
        for name, raw in original_files.items():
            (stage/'observation'/name).write_bytes(raw)
        (stage/'technical-original').mkdir()
        for name in entries:
            (stage/'technical-original'/name).parent.mkdir(parents=True, exist_ok=True)
            (stage/'technical-original'/name).write_bytes(regular(technical_bundle/name))
        (stage/'technical-original/SHA256SUMS').write_bytes(regular(technical_bundle/'SHA256SUMS'))
        (stage/'comparison.json').write_bytes(json_bytes(value))
        for language in ('fr','en'):
            (stage/('report-'+language+'.html')).write_text(render(value,language), encoding='utf-8')
        receipt = {'kind':'tsep-search-console-diagnostic-import','version':VERSION,'created_at':now(),
                   'source_files':source_files,'original_technical_manifest_sha256':tsep.digest(technical_bundle/'SHA256SUMS'),
                   'observation_sha256':{n:hashlib.sha256(b).hexdigest() for n,b in original_files.items()},
                   'network_requests':0,'tsep_verdict_created':False}
        (stage/'receipt.json').write_bytes(json_bytes(receipt))
        seal(stage); inventory(stage)
        tsep.require(sources() == source_files, 'Diagnostic sources changed during execution')
        publish(stage,output)
    return value


def replay(source, output):
    source = Path(source)
    inventory(source)
    receipt = tsep.read_json(source/'receipt.json')
    tsep.require(receipt['kind'] == 'tsep-search-console-diagnostic-import' and receipt['version'] == VERSION
                 and receipt['source_files'] == sources(), 'Use the exact historical diagnostic tools')
    tsep.require(receipt['original_technical_manifest_sha256'] == tsep.digest(source/'technical-original/SHA256SUMS'), 'Changed technical manifest binding')
    for name, digest in receipt['observation_sha256'].items():
        tsep.require(name in ('manifest.json','request.json','response.json','change-evidence.txt')
                     and tsep.digest(source/'observation'/name) == digest, 'Changed inspection binding')
    before = tsep.read_json(source/'comparison.json')
    after = build(source/'observation', source/'technical-original', output)
    tsep.require(after == before, 'Comparison differs; retained new output for inspection')
    return {'replayed':True,'same_comparison':True,'network_requests':0,'tsep_verdict_created':False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    compare_args = sub.add_parser('compare')
    compare_args.add_argument('observation', type=Path)
    compare_args.add_argument('--technical', type=Path, required=True)
    compare_args.add_argument('--output', type=Path, required=True)
    replay_args = sub.add_parser('replay')
    replay_args.add_argument('source', type=Path)
    replay_args.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        value = build(args.observation,args.technical,args.output) if args.command == 'compare' else replay(args.source,args.output)
        print(json_bytes(value).decode(),end='')
        return 0
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as error:
        print(str(error),file=sys.stderr)
        return 64


if __name__ == '__main__':
    sys.exit(main())
