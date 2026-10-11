#!/usr/bin/env python3
"""Build a scoped TSEP evidence bundle from supplied offline captures. Apache-2.0.

No collection, browser execution, automatic human review or expected-case verdicts.
The bounded reference interpreter supplies observations; the report validator is
always applied before delivery. Adapter versioning is separate from the protocol.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from conformance.evaluate import RULES, VERSION as INTERPRETER_VERSION, evaluate, url_parts
from provenance.runtime import loaded_sources, runtime_identity

VERSION = '24'
NAME = 'TSEP offline capture adapter'
ACCESS = ('public', 'restricted', 'synthetic')


def source_files():
    modules = {'adapters/captures.py': sys.modules[__name__], 'tsep.py': tsep}
    modules['conformance/http_canonical.py'] = importlib.import_module('conformance.http_canonical')
    modules['conformance/preview_intent.py'] = importlib.import_module('conformance.preview_intent')
    modules['conformance/performance.py'] = importlib.import_module('conformance.performance')
    modules['conformance/agent_policy.py'] = importlib.import_module('conformance.agent_policy')
    modules['conformance/agent_access.py'] = importlib.import_module('conformance.agent_access')
    for name in ('conformance.evaluate', 'conformance.http', 'conformance.canonical', 'conformance.sitemap_locations', 'conformance.canonical_attributes', 'conformance.source_text', 'conformance.redirects', 'conformance.robots', 'conformance.robots_control', 'conformance.structured_dom', 'experiments.rendered_metadata', 'experiments.rendered_canonical', 'provenance.runtime', 'conformance.source_directives', 'conformance.source_canonical', 'experiments.source_head', 'experiments.source_http', 'experiments.source_tree'):
        modules[name.replace('.', '/')+'.py'] = importlib.import_module(name)
    result = loaded_sources(ROOT, modules)
    result['collectors/rendered_metadata.js'] = tsep.digest(ROOT/'collectors/rendered_metadata.js')
    from experiments import source_http
    result.update(source_http.identity())
    from experiments import source_head
    result.update(source_head.identity())
    from conformance import source_link_policy
    from experiments import link_elements, url_resolution
    result.update(loaded_sources(ROOT, {'conformance/source_link_policy.py': source_link_policy,
        'experiments/link_elements.py': link_elements, 'experiments/url_resolution.py': url_resolution}))
    result.update(link_elements.identity()); result.update(url_resolution.identity())
    result['experiments/source_metadata.mjs'] = tsep.digest(ROOT/'experiments/source_metadata.mjs')
    return result


COVERAGE_INVENTORY = [
    {'state': 'implemented', 'fr': 'TS43 : client de test documenté, réponse prévue, journaux JSONL natifs et corrélation revue. Un refus prévu peut être cohérent ; aucune identité, visite ou accessibilité réelle de l’opérateur établie.',
     'en': 'TS43: documented test client, planned response, native JSONL logs and reviewed correlation. An expected denial can conform; no actual operator identity, visit or access established.'},
    {'state': 'implemented', 'fr': 'TS42 : usages documentés, décisions du responsable et arbitrages fournis ; comparaison robots bornée sur la représentation du client. Aucun agent réel ni respect des règles par un opérateur établi.',
     'en': 'TS42: documented purposes, supplied owner decisions and tradeoffs; bounded robots comparison on the client representation. No actual agent or operator compliance established.'},
    {'state':'implemented', 'fr':'TS34/TS35 : imports CrUX et Lighthouse distincts, valeurs et classes conservées ; C décrit la documentation, jamais une garantie de bonnes performances. Revues fournies sans authentification ; aucune collecte.',
     'en':'TS34/TS35: separate CrUX and Lighthouse imports with retained values/classes; C describes documentation, never a guarantee of good performance. Supplied reviews are not authenticated; no collection.'},
    {'state':'implemented', 'fr':'TS07-A01/A03 : profil préalable google-preview-intent-v1, intervalles de permission texte/image/vidéo, contradictions et inconnues conservées. Aucun affichage Google ou usage de contenu déduit.',
     'en':'TS07-A01/A03: prior google-preview-intent-v1, text/image/video permission intervals, retained contradictions and unknowns. No inferred Google display or content usage.'},
    {'state':'implemented', 'fr':'TS10-A01/A02 : http-link-context-v1 préalable, premier rel, contexte anchor attribué et inconnues conservées ; destination comparée littéralement. Ancien lecteur inchangé ; aucun choix Google déduit.',
     'en':'TS10-A01/A02: prior http-link-context-v1, first rel, attributed anchor context and retained unknowns; literal destination comparison. Historical reader unchanged; no inferred Google choice.'},
    {'state':'implemented','fr':'TS10-A04 : profils source préalables html-tree-links-v1/v2, liens HTML a/area attribués, base conditionnelle et URL sérialisées. Convergence dans une famille déclarée, pas présence ou suffisance du maillage ; v2 rend les href dépendants indéterminés sous première base non analysable ; rendu antérieur inchangé.',
     'en':'TS10-A04: prior html-tree-links-v1/v2 source profiles, attributed HTML a/area, conditional base and serialized URLs. Declared-family convergence, not link presence or sufficiency; v2 keeps dependent hrefs unknown under an unparseable first base; earlier rendered readers unchanged.'},
    {'state':'implemented','fr':'TS10-A01/A02 : lecteur source canonical préalable, positions et hypothèses attribuées ; rendu/revue toujours nécessaires.','en':'TS10-A01/A02: prior canonical source reader with attributed positions/hypotheses; rendering/reviews remain required.'},
    {'state':'implemented', 'fr':'TS07 : source_reader html-tree-directives-v1 préalable, deux hypothèses statiques et métadonnées attribuées aux octets ; Node 24 facultatif requis pour ce profil, aucun repli. Rendu et revues distincts.',
     'en':'TS07: prior html-tree-directives-v1 source_reader, two static hypotheses with byte-attributed metadata; optional Node 24 required for this profile, no fallback. Rendering and reviews remain separate.'},
    {'state': 'implemented', 'fr': 'TS10-A03 : lecteur sitemap-locations-v1 préalable ; loc de pages distincts des annotations langues/images conservées sans évaluation. Profil historique inchangé, extensions inconnues indéterminées.',
     'en': 'TS10-A03: prior sitemap-locations-v1 reader; page loc distinct from retained, unassessed language/image annotations. Legacy profile unchanged; unknown extensions inconclusive.'},
    {'state': 'implemented', 'fr': 'Profil robots google-robotstxt-fields-v2 : registre fermé de champs hors portée accès, valeurs conservées ; anciens profils inchangés, autres champs indéterminés.',
     'en': 'Robots profile google-robotstxt-fields-v2: closed registry of fields outside access scope, retained values; old profiles unchanged, other fields inconclusive.'},
    {'state': 'implemented', 'fr': 'TS04 : directive_crawler préalable distingue le groupe Googlebot et le client HTTP réel ; les refus HTTP restent propres au client observé, sans accès Googlebot déduit.',
     'en': 'TS04: prior directive_crawler separates the Googlebot group from the actual HTTP client; HTTP denials concern the observed client, without inferring Googlebot access.'},
    {'state': 'implemented', 'fr': 'TS10 : attributs ordinaires source et DOM structurés classés en commun ; modificateurs, namespaces et attributs inconnus indéterminés. DOM sérialisé historique inchangé.',
     'en': 'TS10: shared source/structured canonical attribute classification; modifiers, namespaces and unknown attributes inconclusive. Historical serialized DOM unchanged.'},
    {'state': 'implemented', 'fr': 'TS07/TS10 : lecteur DOM structuré préalable, arbre complet, provenance fournie, sans authentification de navigation. Limites source et revues conservées.',
     'en': 'TS07/TS10: predeclared structured DOM reader, complete tree and supplied attribution, without navigation authentication. Source limits and reviews retained.'},
    {'state': 'implemented', 'fr': 'TS04 : matrice robots préalable, ressources nécessaires, revues fournies et lecteur partagé TS07. Profils bornés explicites ; anciennes entrées TS07 sous profil historique fixe.',
     'en': 'TS04: prior robots matrix, required resources, supplied reviews and shared TS07 reader. Explicit bounded profiles; legacy TS07 inputs use a fixed historical profile.'},
    {'state': 'implemented', 'fr': 'Octets HTTP exacts en entrée v2 ; lecture des anciennes entrées UTF-8 v1.',
     'en': 'Exact HTTP bytes in input v2; legacy UTF-8 input v1 retained.'},
    {'state': 'implemented', 'fr': 'HTTP/1.1 chunked borné, gzip simple et deflate enveloppé zlib ; SHA-256 après décodage, sans normalisation.',
     'en': 'Bounded HTTP/1.1 chunked, single gzip member and zlib-wrapped deflate; SHA-256 after decoding, without normalization.'},
    {'state': 'implemented', 'fr': 'Rapport hors ligne, preuves originales et comparaison ; inconnues et échecs conservés.',
     'en': 'Offline report, original evidence and comparison; unknowns and failures retained.'},
    {'state': 'implemented', 'fr': 'TS01 : extracteur de texte source distinct de TS07 ; éléments ordinaires équilibrés, références de caractères, titre RCDATA et icônes SVG bornées sans texte.',
     'en': 'TS01: source-text extractor separate from TS07; balanced ordinary elements, character references, RCDATA title and bounded text-free SVG icons.'},
    {'state': 'deferred', 'fr': 'Brotli, gzip multimembre, extensions/trailers chunked, HTTP/2 brut : indéterminés.',
     'en': 'Brotli, multi-member gzip, chunk extensions/trailers and raw HTTP/2: inconclusive.'},
    {'state': 'deferred', 'fr': 'Marqueurs : UTF-8 explicite et HTML borné seulement. Octets non UTF-8 conservés et empreintes comparables, sans extraction de texte implicite.',
     'en': 'Markers: explicit UTF-8 and bounded HTML only. Non-UTF-8 bytes retained and hashes comparable, without implicit text extraction.'},
    {'state': 'implemented', 'fr': 'TS01 : select/option/optgroup et tableaux explicitement structurés ; aucune fermeture implicite ni réparation.',
     'en': 'TS01: explicitly structured select/option/optgroup and tables; no implied closure or repair.'},
    {'state': 'deferred', 'fr': 'TS01 : noscript/template/textarea non vides, texte SVG, MathML, select/table hors sous-ensemble, script échappé et HTML ambigu : extraction entière indéterminée.',
     'en': 'TS01: nonempty noscript/template/textarea, SVG text, MathML, unsupported select/table, escaped script and ambiguous HTML: whole extraction inconclusive.'},
    {'state': 'out-of-scope', 'fr': 'Cet adaptateur ne collecte pas, ne rend pas JavaScript et ne produit aucune revue humaine manquante.',
     'en': 'This adapter does not collect, render JavaScript or supply missing human reviews.'},
    {'state': 'out-of-scope', 'fr': 'Pas de preuve de Googlebot réel, indexation, classement ou conformité globale.',
     'en': 'No evidence of actual Googlebot behavior, indexing, ranking or global conformity.'},
]


def dated(value, fallback, issued_text):
    """Do not repair malformed source dates or label import time as capture time."""
    dates = [fallback]
    def visit(item):
        if isinstance(item, dict):
            for key, child in item.items():
                if key in ('observed_at', 'declared_at'):
                    dates.append(child)
                else:
                    visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)
    visit(value)
    parsed, unresolved = [], False
    for date in dates:
        try:
            parsed.append((tsep.timestamp(date), date))
        except (ValueError, TypeError):
            unresolved = True
    tsep.require(all(date <= tsep.timestamp(issued_text) for date, _ in parsed), 'Supplied evidence date is in the future')
    if unresolved:
        return issued_text, 'import-time-only; supplied date missing/invalid, unchanged in the retained record'
    return max(parsed, key=lambda pair: pair[0])[1], 'latest-supplied-date; target observation date used for undated derived fields'


def pieces(target):
    """Extract only supplied fields. Never create a DOM, review or absence proof."""
    result = {}
    if 'intent' in target:
        result['intent'] = {k: target[k] for k in
                            ('intent', 'context', 'reference', 'access_review', 'exemption_review', 'content_review', 'field_review', 'lab_review', 'agent_decision', 'execution', 'attribution', 'log_review') if k in target}
    documents = ('agent_documents', 'agent_reviews', 'client_documents', 'client_review')
    if any(k in target for k in documents):
        result['operator-docs'] = {k: target[k] for k in documents if k in target}
    if 'logs' in target:
        result['logs'] = target['logs']
    if 'agent_policy' in target.get('intent', {}) and 'robots' in target:
        result['configuration'] = {'robots': target['robots'], 'basis': 'Supplied policy representation, not server configuration access'}
    for source, kind in (('field', 'field-data'), ('lab', 'lab-data')):
        if source in target:
            result[kind] = target[source]
    host_policy = 'robots_plan' in target.get('intent', {})
    if 'http' in target or 'documents' in target or (host_policy and 'robots' in target):
        fields = ('http', 'documents', 'robots') if host_policy else ('http', 'documents')
        result['http'] = {k: target[k] for k in fields if k in target}
        # These are source response records, not invented HTML for non-HTML resources.
        surfaces = []
        docs = ([target] if 'http' in target else []) + (
            target['documents'] if isinstance(target.get('documents'), list) else [])
        for doc in docs:
            if not isinstance(doc, dict) or not isinstance(doc.get('http'), list):
                continue
            for hop in doc['http']:
                if isinstance(hop, dict) and isinstance(hop.get('response'), (str, dict)):
                    surfaces.append({k: hop[k] for k in ('url', 'complete', 'response') if k in hop})
        if surfaces:
            result['html'] = {'source_responses': surfaces,
                              'interpretation': 'Supplied source responses with media types and bodies; no DOM or HTML inferred.'}
    for source, kind in (('robots', 'robots'), ('sitemaps', 'sitemap'), ('crawl', 'crawl')):
        if source in target:
            result[kind] = target[source]
    rendered = []
    if 'render' in target:
        rendered.append({'url': target['url'], 'render': target['render']})
    docs = target.get('documents', [])
    crawl = target.get('crawl', {})
    crawl_docs = crawl.get('documents', []) if isinstance(crawl, dict) else []
    for collection in (docs, crawl_docs):
        if isinstance(collection, list):
            for doc in collection:
                if isinstance(doc, dict) and 'render' in doc:
                    rendered.append({k: doc[k] for k in ('url', 'context_id', 'observed_at', 'render') if k in doc})
    if rendered:
        result['render'] = rendered
    return result


def coverage(data, controls):
    requested = set(data['rules'])
    targets = len(data['targets'])
    return {cid: {'requested_rules': [r['id'] for r in control.get('rules', []) if r['id'] in requested],
                  'omitted_rules': [r['id'] for r in control.get('rules', []) if r['id'] not in requested],
                  'requested_pairs': targets * sum(r['id'] in requested for r in control.get('rules', [])),
                  'required_pairs': targets * len(control.get('rules', []))}
            for cid, control in controls.items()}


def control_result(cid, atoms, control, targets):
    all_pairs = {(rule['id'], target) for rule in control.get('rules', []) for target in targets}
    observed = {(atom['rule_id'], atom['target']) for atom in atoms}
    missing = sorted(all_pairs - observed)
    outcomes = [a['outcome'] for a in atoms]
    if 'fail' in outcomes:
        status = 'NC'
    elif not missing and 'pass' in outcomes and all(x in ('pass', 'not-applicable') for x in outcomes):
        status = 'C'
    else:
        status = 'NT'  # Missing rules and all-exempt subsets cannot establish C or whole-control NA.
    return {'control_id': cid, 'status': status,
            'evaluation_state': 'inconclusive' if status == 'NT' else 'complete',
            'reason': 'Computed supplied-capture outcomes: ' + ', '.join(
                label + '=' + str(outcomes.count(label)) for label in ('pass', 'fail', 'not-applicable', 'inconclusive'))
                + '; omitted pairs=' + str(len(missing)) + '; declared scope only.',
            'procedure': NAME + ' ' + VERSION + '; bounded reference interpretation, supplied reviews retained; no collection.',
            'evaluated_targets': [target for target in targets if any(a['target'] == target for a in atoms)],
            'evidence_ids': sorted({ref for a in atoms for ref in a['evidence_ids']}), 'atomic_results': atoms}


def build(input_path, output, *, assessor, label, selection_method, access, mode='manual', selected=None, exclusions=None):
    """New bundle only. Validation completes in staging before the output is created."""
    sources = source_files()
    runtime = runtime_identity()
    input_path, output = Path(input_path), Path(output)
    tsep.require(input_path.is_file() and not input_path.is_symlink(), 'Input must be a regular file, not a symlink')
    with input_path.open('rb') as handle:
        original = handle.read(tsep.MAX_JSON_BYTES + 1)
    data = tsep.parse_json(original)
    tsep.require(isinstance(data, dict) and set(data) == {'input_version', 'rules', 'targets'},
                 'Supply only a captures input object, not a case, expected outcomes or a report')
    tsep.require(data['input_version'] in ('1', '2'), 'Unsupported captures input version')
    tsep.require(isinstance(data['rules'], list) and data['rules']
                 and all(isinstance(r, str) and r in RULES for r in data['rules']), 'Explicit supported rules required')
    tsep.unique(data['rules'], 'capture rule')
    tsep.require(isinstance(data['targets'], list) and 0 < len(data['targets']) <= 100, 'Expected 1–100 explicit targets')
    issued_text = datetime.now(timezone.utc).isoformat()
    for target in data['targets']:
        tsep.require(isinstance(target, dict) and isinstance(target.get('url'), str), 'Target URL is required')
        url_parts(target['url'])
        dated(target, target.get('observed_at'), issued_text)
    targets = [t['url'] for t in data['targets']]
    tsep.unique(targets, 'capture target')
    tsep.require(access in ACCESS, 'Explicit evidence access is required')
    def synthetic_dom(value):
        if isinstance(value, dict):
            structured = value.get('structured_dom')
            if isinstance(structured, dict):
                acquisition = structured.get('acquisition')
                if isinstance(acquisition, dict) and acquisition.get('kind') == 'authored-synthetic':
                    tsep.require(access == 'synthetic', 'Authored structured DOM requires synthetic evidence access')
            for child in value.values():
                synthetic_dom(child)
        elif isinstance(value, list):
            for child in value:
                synthetic_dom(child)
    synthetic_dom(data)
    for target in data['targets']:
        agent_reviews = target.get('agent_reviews')
        records = list(agent_reviews) if isinstance(agent_reviews, list) else []
        records.append(target.get('agent_decision'))
        records.extend(target.get(k) for k in ('client_review', 'log_review', 'attribution'))
        for record in records:
            if isinstance(record, dict) and record.get('provenance') in ('human', 'human-assisted', 'synthetic-exercise'):
                tsep.require((record['provenance'] == 'synthetic-exercise') == (access == 'synthetic'),
                             'Agent review/decision provenance differs from evidence access')
        for name in ('field_review', 'lab_review'):
            review = target.get(name)
            if isinstance(review, dict) and review.get('provenance') in ('synthetic-exercise', 'supplied-review'):
                tsep.require((review['provenance'] == 'synthetic-exercise') == (access == 'synthetic'),
                             'Performance review provenance differs from evidence access')
    if any(r.startswith('TS02-') for r in data['rules']):
        for target in data['targets']:
            review = target.get('intent', {}).get('redirect_review', {})
            if review:
                tsep.require((review.get('provenance') == 'synthetic-exercise') == (access == 'synthetic'),
                             'Redirect review provenance differs from evidence access')
    if any(r.startswith('TS04-') for r in data['rules']):
        for target in data['targets']:
            documents = target.get('documents', [])
            reviews = [d.get('access_review') for d in documents if isinstance(d, dict)] if isinstance(documents, list) else []
            reviews.append(target.get('intent', {}).get('robots_plan', {}).get('no_required_resources'))
            for review in reviews:
                if review:
                    tsep.require((review.get('provenance') == 'synthetic-exercise') == (access == 'synthetic'),
                                 'Robots resource review provenance differs from evidence access')
    tsep.require(mode in ('manual', 'semiAuto', 'automatic'), 'Unknown assessment mode')
    parents = sorted({r.split('-')[0] for r in data['rules']})
    selected = parents if selected is None else selected
    tsep.require(set(parents) <= set(selected), 'Selected controls cannot omit requested-rule parents')
    client_scope = ''
    if 'TS04' in parents:
        scoped = [t for t in data['targets'] if 'directive_crawler' in t.get('intent', {})]
        if scoped:
            clients = sorted({str(t['intent'].get('crawler', '[undeclared]')) for t in scoped})
            client_scope = ('TS04 — client HTTP observé / observed HTTP client: '
                            + json.dumps(clients, ensure_ascii=False)
                            + '; accès réel Googlebot non observé / actual Googlebot access unobserved')
            # Replay receives the original label; do not duplicate its qualification.
            if not label.endswith(client_scope):
                label += ' | ' + client_scope
    report = tsep.initialize(targets, selected, 'custom', assessor, label, selection_method,
                             mode=mode, tool={'name': NAME, 'version': VERSION})
    report['issued_at'] = issued_text
    report['scope']['exclusions'] = list(exclusions or [])
    protocol = tsep.read_json(tsep.PROTOCOL_PATH)
    controls = {c['id']: c for c in protocol['controls'] if c['id'] in selected}
    declared_coverage = coverage(data, controls)
    # Only the raw input reaches the interpreter, never the conformance corpus.
    source_observations = []
    calculated = evaluate(data, source_observations=source_observations)
    tsep.require(source_files() == sources, 'Tool source files changed during interpretation')
    tsep.require(runtime_identity() == runtime, 'Selected runtime dependencies changed during interpretation')
    # Reject malformed metadata and incompatible modes before opening a destination.
    tsep.validate(report, ROOT)
    tsep.require(not output.is_symlink() and not output.exists(), 'Output already exists; choose a new directory')
    tsep.require(output.parent.is_dir(), 'Output parent directory must exist')
    output = output.parent.resolve()/output.name
    with tempfile.TemporaryDirectory(prefix='.tsep-capture-', dir=output.parent) as folder:
        stage = Path(folder)
        files = []
        def write(relative, value=None, raw=None):
            path = stage/relative
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = raw if raw is not None else (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
            with path.open('xb') as handle:
                handle.write(payload)
            files.append(relative)
            return path
        def artifact(aid, kind, relative, value, covered, date, description, raw=None):
            path = write(relative, value, raw)
            report['artifacts'].append({'id': aid, 'path': relative, 'sha256': tsep.digest(path),
                'kind': kind, 'targets': covered, 'observed_at': date, 'access': access, 'description': description})
            return aid
        shared = [artifact('supplied-input', 'operator-docs', 'input.json', None, targets, issued_text,
                           'Original supplied bytes. Artifact date is import time; source dates are retained inside, not verified.', raw=original)]
        metadata = {'adapter': {'name': NAME, 'version': VERSION}, 'protocol': report['protocol'],
                    'interpreter': {'name': 'TSEP bounded reference interpreter', 'version': INTERPRETER_VERSION},
                    'imported_at': issued_text, 'python': sys.version.split()[0],
                    'source_files': sources, 'runtime': runtime,
                    'source_verification': 'Loaded module file/spec origins match this tool root; on-disk hashes checked before and after interpretation. Not execution authentication.',
                    'input_sha256': hashlib.sha256(original).hexdigest(), 'access': access,
                    'coverage_inventory': COVERAGE_INVENTORY,
                    'network_requests_by_adapter': 0, 'coverage': declared_coverage,
                    'limitations': 'Reference interpreter only. Supplied intent/reviews are not authenticated; no collection, JS execution, engine observation or global conformity.'}
        shared.append(artifact('import-record', 'operator-docs', 'import.json', metadata, targets, issued_text,
                               'Import context, source-code fingerprints and omitted-rule coverage; import time is not capture time.'))
        shared.append(artifact('computed-results', 'validator-output', 'assessment.json', calculated, targets, issued_text,
                               'Computed reference outcomes, not normative conformance expectations; assessment performed at import time.'))
        diagnostic_refs = {target:[] for target in targets}
        for index, observation in enumerate(source_observations, 1):
            payload = (json.dumps(observation, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
            tsep.require(len(payload) <= tsep.MAX_JSON_BYTES, 'Source observation artifact exceeds replay JSON limit')
            aid = 'source-observation-' + str(index)
            diagnostic_refs[observation['target']].append(artifact(aid, 'validator-output',
                'observations/' + aid + '.json', observation, [observation['target']], issued_text,
                'Computed interpretation diagnostics, attributed metadata/directives and alternative decisions; import time, not capture or engine observation.'))
        refs = {}
        for index, target in enumerate(data['targets'], 1):
            refs[target['url']] = list(shared) + diagnostic_refs[target['url']]
            for kind, payload in pieces(target).items():
                aid = 'target-' + str(index) + '-' + kind
                date, basis = dated(payload, target.get('observed_at'), issued_text)
                refs[target['url']].append(artifact(aid, kind, 'evidence/' + aid + '.json',
                    {'target': target['url'], 'date_basis': basis, 'record': payload}, [target['url']], date,
                    'Derived supplied record; ' + basis + '. Original fields unchanged; no missing evidence inferred.'))
        atoms = [dict(row, evidence_ids=refs[row['target']]) for row in calculated]
        for i, result in enumerate(report['results']):
            cid = result['control_id']
            rows = [a for a in atoms if a['rule_id'].startswith(cid + '-')]
            if rows:
                report['results'][i] = control_result(cid, rows, controls[cid], targets)
                if cid in ('TS34', 'TS35'):
                    report['results'][i]['reason'] += ' C = documentation conforme / conforming documentation, not good performance. '
                    report['results'][i]['reason'] += '\n'.join(a['rule_id'] + ' — ' + a['reason'] for a in rows)
                if cid == 'TS42':
                    report['results'][i]['reason'] += ' Usages déclarés et pièces fournies seulement / Declared usages and supplied evidence only; no real agent visit, identity, operator compliance or citation established.'
                if cid == 'TS43':
                    report['results'][i]['reason'] += ' C = traitement documenté du client de test / documented test-client treatment. An expected denial may conform; real operator access, identity and visits remain unestablished.'
                if cid == 'TS04' and client_scope:
                    report['results'][i]['reason'] += ' ' + client_scope + '.'
                for atom in rows:
                    if atom['rule_id'] == 'TS10-A04' and any(reader + ':' in atom['reason'] for reader in ('html-tree-links-v1', 'html-tree-links-v2')):
                        report['results'][i]['reason'] += ' A04 scope for ' + atom['target'] + ': ' + atom['reason']
        summary = tsep.validate(report, stage)
        write('report.json', report)
        write('gate.json', summary)
        write('earl.jsonld', tsep.earl(report, summary))
        sums = ''.join(tsep.digest(stage/name) + '  ' + name + '\n' for name in sorted(files))
        write('SHA256SUMS', raw=sums.encode('utf-8'))
        # Reserve exclusively. Never merge into or replace an existing directory.
        output.mkdir(mode=0o700)
        try:
            for relative in files:
                dest = output/relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                with dest.open('xb') as handle:
                    handle.write((stage/relative).read_bytes())
        except BaseException:
            shutil.rmtree(output)
            raise
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='A single input_version 1 or 2 captures object; no expected outcomes')
    parser.add_argument('--output-dir', type=Path, required=True, help='New directory, existing parent; never overwrite')
    parser.add_argument('--assessor', required=True)
    parser.add_argument('--label', required=True)
    parser.add_argument('--selection-method', required=True)
    parser.add_argument('--access', choices=ACCESS, required=True)
    parser.add_argument('--mode', choices=['manual', 'semiAuto', 'automatic'], default='manual')
    parser.add_argument('--controls', help='Optional comma-separated custom control set; must include requested-rule parents')
    parser.add_argument('--exclude', action='append', default=[])
    parser.add_argument('--lang', choices=['fr', 'en'], default='en')
    parser.add_argument('--json', action='store_true', help='Structured gate summary instead of a readable summary')
    args = parser.parse_args(argv)
    try:
        summary = build(args.input, args.output_dir, assessor=args.assessor, label=args.label,
                        selection_method=args.selection_method, access=args.access, mode=args.mode,
                        selected=args.controls.split(',') if args.controls else None, exclusions=args.exclude)
        print(json.dumps(summary, ensure_ascii=False, indent=2) if args.json else tsep.readable_summary(summary, args.lang))
        # Successful conversion is not a delivery authorization; use tsep.py gate for its policy exit code.
        return 0
    except (ValueError, OSError, KeyError, TypeError, AttributeError, RecursionError) as error:
        print(json.dumps({'valid': False, 'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 64


if __name__ == '__main__':
    sys.exit(main())
