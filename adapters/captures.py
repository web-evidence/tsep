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
from conformance.evaluate import RULES, VERSION as INTERPRETER_VERSION, evaluate, url_parts, binding_digest
from provenance.runtime import loaded_sources, runtime_identity

VERSION = '45'
NAME = 'TSEP offline capture adapter'
ACCESS = ('public', 'restricted', 'synthetic')


def verify_ts17_self_digests(target):
    """Transport self-integrity only; missing evidence/associations stay unknown.

    Inspect every supplied state before interpretation, including unplanned states
    and missing plans. Never repair a digest or infer acquisition authenticity.
    Historical readers and other controls keep their existing behavior.
    """
    render = target.get('render')
    states = render.get('states') if isinstance(render, dict) else None
    if not isinstance(states, list):
        return
    for state in states:
        structured = state.get('structured_dom') if isinstance(state, dict) else None
        if not isinstance(structured, dict):
            continue
        snapshot, declared = structured.get('snapshot'), structured.get('snapshot_sha256')
        if snapshot is not None and declared is not None:
            try:
                actual = binding_digest(snapshot)
            except (TypeError, ValueError, UnicodeError) as error:
                raise tsep.Invalid('TS17 DOM integrity: unhashable supplied snapshot') from error
            tsep.require(isinstance(declared, str) and declared == actual,
                         'TS17 DOM integrity: supplied snapshot self-fingerprint mismatch')
        acquisition = structured.get('acquisition')
        support = acquisition.get('support') if isinstance(acquisition, dict) else None
        if not isinstance(support, list):
            continue
        for item in support:
            if not isinstance(item, dict):
                continue
            content, declared = item.get('content'), item.get('sha256')
            if isinstance(content, str) and declared is not None:
                try:
                    actual = hashlib.sha256(content.encode('utf-8')).hexdigest()
                except UnicodeError as error:
                    raise tsep.Invalid('TS17 DOM integrity: unhashable supplied support content') from error
                tsep.require(isinstance(declared, str) and declared == actual,
                             'TS17 DOM integrity: supplied support self-fingerprint mismatch')


def source_files():
    modules = {'adapters/captures.py': sys.modules[__name__], 'tsep.py': tsep}
    modules['conformance/http_canonical.py'] = importlib.import_module('conformance.http_canonical')
    modules['conformance/preview_intent.py'] = importlib.import_module('conformance.preview_intent')
    modules['conformance/performance.py'] = importlib.import_module('conformance.performance')
    modules['conformance/agent_policy.py'] = importlib.import_module('conformance.agent_policy')
    modules['conformance/agent_access.py'] = importlib.import_module('conformance.agent_access')
    modules['conformance/critical_content.py'] = importlib.import_module('conformance.critical_content')
    modules['conformance/release_monitoring.py'] = importlib.import_module('conformance.release_monitoring')
    for name in ('essential_links','essential_links_source','essential_links_dom'):
        modules['conformance/'+name+'.py'] = importlib.import_module('conformance.'+name)
    for name in ('graph_bounds','graph_inventories','graph_documents','graph_reviews','graph_reconciliation'):
        modules['conformance/'+name+'.py'] = importlib.import_module('conformance.'+name)
    for name in ('hreflang_native','hreflang_reciprocity','xdefault_role','critical_presence'):
        modules['conformance/'+name+'.py'] = importlib.import_module('conformance.'+name)
    modules['adapters/hreflang_intake.py'] = importlib.import_module('adapters.hreflang_intake')
    modules['adapters/graph_intake.py'] = importlib.import_module('adapters.graph_intake')
    modules['conformance/incoming_links.py'] = importlib.import_module('conformance.incoming_links')
    modules['adapters/incoming_links_intake.py'] = importlib.import_module('adapters.incoming_links_intake')
    modules['conformance/sitemap_files.py'] = importlib.import_module('conformance.sitemap_files')
    modules['conformance/sitemap_set.py'] = importlib.import_module('conformance.sitemap_set')
    modules['conformance/structured_validation.py'] = importlib.import_module('conformance.structured_validation')
    modules['conformance/structured_identity.py'] = importlib.import_module('conformance.structured_identity')
    modules['conformance/structured_content.py'] = importlib.import_module('conformance.structured_content')
    modules['conformance/canonical_comparison.py'] = importlib.import_module('conformance.canonical_comparison')
    modules['conformance/inspection.py'] = importlib.import_module('conformance.inspection')
    modules['diagnostics/search_console.py'] = importlib.import_module('diagnostics.search_console')
    modules['conformance/delivery.py'] = importlib.import_module('conformance.delivery')
    modules['experiments/delivery_variants.py'] = importlib.import_module('experiments.delivery_variants')
    modules['conformance/release_invariants.py'] = importlib.import_module('conformance.release_invariants')
    modules['experiments/source_content.py'] = importlib.import_module('experiments.source_content')
    modules['conformance/source_markers.py'] = importlib.import_module('conformance.source_markers')
    modules['experiments/source_markers.py'] = importlib.import_module('experiments.source_markers')
    for name in ('conformance.evaluate', 'conformance.ts06_access', 'conformance.http', 'conformance.canonical', 'conformance.sitemap_locations', 'conformance.canonical_attributes', 'conformance.source_text', 'conformance.redirects', 'conformance.robots', 'conformance.robots_control', 'conformance.structured_dom', 'experiments.rendered_metadata', 'experiments.rendered_canonical', 'provenance.runtime', 'conformance.source_directives', 'conformance.source_canonical', 'experiments.source_head', 'experiments.source_http', 'experiments.source_tree'):
        modules[name.replace('.', '/')+'.py'] = importlib.import_module(name)
    result = loaded_sources(ROOT, modules)
    from conformance.structured_validation import VOCABULARY
    result[VOCABULARY] = tsep.digest(ROOT/VOCABULARY)
    result['collectors/rendered_metadata.js'] = tsep.digest(ROOT/'collectors/rendered_metadata.js')
    from experiments import source_http
    result.update(source_http.identity())
    from experiments import source_head
    result.update(source_head.identity())
    from experiments import source_content
    result.update(source_content.identity())
    from experiments import jsonld_rendered
    result.update(jsonld_rendered.identity())
    from conformance import source_link_policy
    from experiments import link_elements, url_resolution
    result.update(loaded_sources(ROOT, {'conformance/source_link_policy.py': source_link_policy,
        'experiments/link_elements.py': link_elements, 'experiments/url_resolution.py': url_resolution}))
    result.update(link_elements.identity()); result.update(url_resolution.identity())
    result['experiments/source_metadata.mjs'] = tsep.digest(ROOT/'experiments/source_metadata.mjs')
    return result


COVERAGE_INVENTORY = [
    {'state':'implemented','fr':'TS06-A01 : matrice fournie de routes `.invalid`, rôles synthétiques, canaris et triplets étiquetés ; aucune identité, aucun cache réel ni domaine live.','en':'TS06-A01: supplied `.invalid` route matrix, synthetic roles, canaries and labelled triplets; no real identity, real cache or live domain.'},
    {'state':'implemented','fr':'TS25 : cinq rôles déclarés, présence source/rendu et revues fournies ; aucune exécution ou visibilité authentifiée.','en':'TS25: five declared roles, source/render presence and supplied reviews; no authenticated execution or visibility.'},
    {'state':'implemented','fr':'TS24 : politique x-default, contexte motivé et revue de rôle fournis ; aucune neutralité ni approbation humaine inférée.','en':'TS24: supplied x-default policy, motivated context and role review; no inferred neutrality or human approval.'},
    {'state':'implemented','fr':'TS23 : réciprocité et auto-référence natives dans le groupe préalable ; aucune validité linguistique, indexabilité ou sélection Google déduite.', 'en':'TS23: native reciprocal/self annotations in the prior cluster; no inferred language validity, indexability or Google selection.'},
    {'state':'implemented','fr':'TS18 : inventaires, graphe borné et revues fournis ; aucune exhaustivité, identité de relecteur ou collecte authentifiée.', 'en':'TS18: supplied inventories, bounded graph and reviews; no completeness, authenticated reviewer or acquisition.'},
    {'state':'implemented','fr':'TS16 : liens entrants dans la population préalable fournie ; aucune exhaustivité du site ni importance authentifiée.', 'en':'TS16: incoming links within a prior supplied population; no site completeness or authenticated importance.'},
    {'state':'implemented','fr':'TS17 : liens essentiels a/href dans les source et états fournis ; stratégie préalable, scénarios et association HTTP/DOM déclarés, aucune interaction ou acquisition authentifiée.','en':'TS17: essential a/href links in supplied source/states; prior strategy, declared scenarios and HTTP/DOM association, no authenticated interaction/acquisition.'},
    {'state':'implemented','fr':'TS15 : population déclarée de fichiers fournis, limites natives et structure minimale ; aucun constat du serveur ni exhaustivité du site.','en':'TS15: declared population of supplied files, native bounds and minimal structure; no server observation or site completeness.'},
    {'state':'implemented','fr':'TS33 : syntaxe et noms de vocabulaire sur les captures liées, messages API indexés séparés ; erreurs bloquantes conservées, aucune éligibilité actuelle garantie.','en':'TS33: syntax/vocabulary names on bound captures, separate indexed API messages; blocking errors retained, no current eligibility guarantee.'},
    {'state':'implemented','fr':'TS32 : identifiants et références des exports JSON-LD fournis, registre préalable et revues liées ; cohérence du corpus, sans stabilité temporelle ni identité authentifiée.','en':'TS32: IDs/references from supplied JSON-LD exports, prior registry and bound reviews; corpus coherence, no temporal stability or authenticated identity.'},
    {'state':'implemented','fr':'TS31 : source et DOM JSON-LD fournis recalculés, périmètre et contenu revus avec liaison aux graphes ; visibilité, faits et résultats enrichis non authentifiés.','en':'TS31: recomputed supplied source/DOM JSON-LD, graph-bound scope/content reviews; visibility, facts and rich results are not authenticated.'},
    {'state':'implemented','fr':'TS36 : suivi documentaire baseline/J+1/J+7/J+30, API et logs fournis ; échéances futures NT, causalité et identité Google non établies.','en':'TS36: supplied baseline/D+1/D+7/D+30 API/log follow-up; future stages inconclusive, causality and Google identity unestablished.'},
    {'state':'implemented','fr':'TS12 : comparaisons littérales API/HTTP/HTML/DOM prévus et revues fournies ; C documentaire, jamais canonical correcte, TS10 ou indexation. Rendu absent : NT sauf contradiction indépendante.', 'en':'TS12: literal API/HTTP/HTML/planned DOM comparisons and supplied reviews; documentary C, never correct canonical, TS10 or indexing. Missing rendering: NT unless independent contradiction.'},
    {'state':'implemented','fr':'TS08 : sélection et objectifs préalables, JSON API natifs et revues/décisions fournies ; dossier qualifié seulement, aucun état live ou verdict TS12.','en':'TS08: prior selection/objectives, native API JSON and supplied reviews/decisions; documentation only, no live state or TS12 verdict.'},
    {'state':'implemented', 'fr':'TS01-A02 : identity_reader html-tree-markers-v1 préalable, segments parsés attribués et deux hypothèses globales. CRLF/CR bruts deviennent LF ; critères littéraux inchangés. Ni visibilité ni navigateur observés. Ancien lecteur et priorités URL/empreinte/stabilité conservés ; Node 24 requis pour cette seule branche, sans repli.',
     'en':'TS01-A02: prior html-tree-markers-v1 identity_reader, attributed parsed segments and two whole-document hypotheses. Raw CRLF/CR become LF; literal criteria unchanged. No visibility or browser observation. Historical reader and URL/hash/stability precedence retained; Node 24 required for this branch, without fallback.'},
    {'state':'implemented','fr':'TS39 : matrice/configuration revues, signaux natifs TS07/TS10 et revues sémantiques, contextes et cache liés aux preuves fournies. Aucune région, visite Googlebot ou production authentifiée.',
     'en':'TS39: reviewed matrix/configuration, native TS07/TS10 signals and semantic reviews, context/cache tied to supplied evidence. No authenticated geography, Googlebot visit or production.'},
    {'state':'implemented', 'fr':'TS41 : plan préalable, sorties natives recalculées, journal et réaction aux échecs/inconnues. C qualifie le dispositif déclaré ; les défauts SEO restent visibles. Aucune commande fournie exécutée ni CI distante authentifiée.',
     'en':'TS41: prior plan, recalculated native outputs, journal and failure/unknown response. C qualifies the declared process; SEO defects stay visible. No supplied command executed or remote CI authenticated.'},
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
    {'state': 'deferred', 'fr': 'TS01 sans identity_reader : noscript/template/textarea non vides, texte SVG, MathML, select/table hors sous-ensemble, script échappé et HTML ambigu : extraction entière indéterminée. Le profil parsé distinct garde les erreurs rapportées, texte étranger non blanc, frames et intervalles non attribuables indéterminés.',
     'en': 'TS01 without identity_reader: nonempty noscript/template/textarea, SVG text, MathML, unsupported select/table, escaped script and ambiguous HTML: whole extraction inconclusive. The distinct parsed profile keeps reported errors, nonblank foreign text, frames and unattributable spans inconclusive.'},
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
    if 'jsonld' in target:
        result['structured-data'] = target['jsonld']
    if 'sitemap_files' in target:
        result['sitemap'] = target['sitemap_files']
    if 'validation_record' in target:
        result['validator-output'] = target['validation_record']
    if 'identity_documents' in target:
        result['structured-data'] = {'identity_documents': target['identity_documents']}
        if 'jsonld' in target:
            result['structured-data']['jsonld'] = target['jsonld']
    if 'structured_reviews' in target:
        result['content'] = target['structured_reviews']
    if 'intent' in target:
        result['intent'] = {k: target[k] for k in
                            ('intent', 'context', 'reference', 'access_review', 'exemption_review', 'content_review', 'field_review', 'lab_review', 'agent_decision', 'execution', 'attribution', 'log_review', 'release_plan_review', 'release_review', 'delivery_plan_review', 'structured_plan_review', 'identity_plan_review', 'identity_reviews', 'validation_plan_review', 'validation_review', 'ts05_policy', 'ts06_access') if k in target}
    if 'ts03_response' in target.get('intent', {}):
        result['configuration'] = {
            'ts03_response': target.get('configuration', {}).get('ts03_response'),
            'basis': 'Bound synthetic TS03 route/status plan; no live server state'
        }
        if 'content' in target:
            result['content'] = {'ts03_expectations': target['content']}
    if 'ts05_policy' in target.get('intent', {}):
        result['configuration'] = {
            'ts05_policy_map': target['intent']['ts05_policy'],
            'configuration_record': target.get('configuration'),
            'basis': 'Supplied synthetic decision map and configuration record; no server state or index observed',
        }
    if 'ts06_access' in target.get('intent', {}):
        result['configuration'] = {
            'ts06_access_record': target.get('configuration', {}).get('ts06_access'),
            'basis': 'Supplied synthetic route-access plan/configuration; no live server state or network collection',
        }
    if 'release' in target.get('intent', {}):
        result['configuration'] = {'release':target['intent']['release'],
                                   'basis':'Supplied release plan; command identities are never executed'}
    for source,kind in (('release_runs','ci-output'),('release_events','change-history')):
        if source in target:result[kind]=target[source]
    critical = ('critical_plan_review','critical_reviews')
    if any(k in target for k in critical):
        result['content'] = {k:target[k] for k in critical if k in target}
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
    if 'delivery' in target.get('intent', {}):
        config={k:target[k] for k in ('delivery_configuration','delivery_sources') if k in target}
        if config:result['configuration']=config
        if 'delivery_observations' in target:result['http']={'delivery_observations':target['delivery_observations']}
        if 'delivery_semantic_reviews' in target:result['content']={'delivery_semantic_reviews':target['delivery_semantic_reviews']}
        logs={k:target[k] for k in ('delivery_context_reviews','delivery_cache_records') if k in target}
        if logs:result['logs']=logs
    if 'inspection' in target.get('intent', {}):
        result['intent'] = {k:target[k] for k in ('intent','context','inspection_plan_review','inspection_reviews','comparison_reviews') if k in target}
        if 'inspection_records' in target:result['search-console'] = target['inspection_records']
    if 'monitoring' in target.get('intent', {}):
        result['intent'] = {k:target[k] for k in ('intent','context','monitoring_plan_review','monitoring_reviews','monitoring_closure_review') if k in target}
        if 'monitoring_deployment' in target:result['change-history']=target['monitoring_deployment']
        checkpoints=target.get('monitoring_checkpoints')
        if isinstance(checkpoints,list):
            result['search-console']=[{k:c[k] for k in ('id','observed_at','inspection_records') if k in c} for c in checkpoints if isinstance(c,dict) and 'inspection_records' in c]
            result['logs']=[{k:c[k] for k in ('id','observed_at','logs') if k in c} for c in checkpoints if isinstance(c,dict) and 'logs' in c]
    incoming = target.get('incoming_links')
    if isinstance(incoming, dict):
        if 'inventory' in incoming: result['inventory'] = incoming['inventory']
        documents = incoming.get('documents')
        if isinstance(documents, list):
            other = {kind: result[kind] for kind in ('http','html','render') if kind in result}
            result['http'] = {'incoming_link_documents': documents}
            if 'http' in other: result['http']['other_supplied_evidence'] = other['http']
            responses = [{'url': d.get('url'), 'http': d['http']} for d in documents if isinstance(d, dict) and 'http' in d]
            if responses:
                result['html'] = {'source_responses': responses, 'interpretation': 'Supplied nested originals; no HTML/DOM inferred.'}
                if 'html' in other: result['html']['other_supplied_evidence'] = other['html']
            rendered = [{k:d[k] for k in ('url','render') if k in d} for d in documents if isinstance(d, dict) and 'render' in d]
            if rendered:
                result['render'] = {'incoming_link_documents': rendered, 'other_supplied_evidence': other['render']} if 'render' in other else rendered
    def retain(kind,key,value):
        prior=result.get(kind)
        result[kind]={key:value}
        if prior is not None: result[kind]['other_supplied_evidence']=prior
    inventories=target.get('graph_inventories')
    if isinstance(inventories,dict):
        retain('inventory','graph_inventories',inventories)
        for role,kind in (('crawl','crawl'),('sitemap','sitemap')):
            if role in inventories:retain(kind,'graph_'+role,inventories[role])
    graph=target.get('graph_documents')
    if isinstance(graph,list):
        retain('http','graph_documents',graph)
        responses=[{'url':d.get('url'),'http':d['http']} for d in graph if isinstance(d,dict) and 'http' in d]
        if responses:retain('html','graph_source_responses',responses)
        rendered=[{k:d[k] for k in ('url','render') if k in d} for d in graph if isinstance(d,dict) and 'render' in d]
        if rendered:retain('render','graph_documents',rendered)
    if 'graph_reviews' in target:retain('intent','graph_reviews',target['graph_reviews'])
    if 'xdefault_reviews' in target:retain('intent','xdefault_reviews',target['xdefault_reviews'])
    for name in ('presence_plan_review','presence_context_reviews'):
        if name in target: retain('intent',name,target[name])
    hreflang=target.get('hreflang_documents')
    if isinstance(hreflang,list):
        retain('http','hreflang_documents',hreflang)
        retain('hreflang','native_hreflang_sources',hreflang)
    if 'hreflang_unsupported_channels' in target:retain('hreflang','unsupported_supplied_channels',target['hreflang_unsupported_channels'])
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
                + '; omitted pairs=' + str(len(missing)) + '; declared scope only.'
                + (' TS41 C: process evidence only; underlying SEO failures and unknowns remain distinct.' if cid=='TS41' else ''),
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
    if set(data['rules']) & {'TS23-A01','TS24-A01'}:
        from adapters.hreflang_intake import verify_target
        for target in data['targets']:verify_target(target,data['input_version'])
    if any(rule.startswith('TS18-') for rule in data['rules']):
        from adapters.graph_intake import verify_target
        for target in data['targets']: verify_target(target,data['input_version'])
    if set(data['rules']) & {'TS25-A01','TS25-A02'}:
        for target in data['targets']:
            try: verify_ts17_self_digests(target)
            except tsep.Invalid as error: raise tsep.Invalid('TS25 transport self-integrity: '+str(error)) from error
        from conformance.critical_presence import verify_review_budgets
        for target in data['targets']:
            try: verify_review_budgets(target)
            except (ValueError,TypeError,UnicodeError) as error: raise tsep.Invalid('TS25 review budget: '+str(error)) from error
    if 'TS16-A01' in data['rules']:
        from adapters.incoming_links_intake import verify_target
        for target in data['targets']:
            verify_target(target, data['input_version'])
    if any(rule in ('TS17-A01', 'TS17-A02') for rule in data['rules']):
        for target in data['targets']:
            supplied_http = target.get('http')
            tsep.require(supplied_http is None or (type(supplied_http) is list
                         and all(type(hop) is dict for hop in supplied_http)),
                         'TS17 HTTP structure: expected a list of exchange objects, or absent/null evidence')
            verify_ts17_self_digests(target)
    tsep.require(access in ACCESS, 'Explicit evidence access is required')
    # Native release inputs are retained as strings. Inspect their supplied
    # provenance as well: wrapping synthetic evidence cannot make it public.
    # One bounded level only; recursive TS41 inputs are unsupported by the reader.
    evidence_targets=list(data['targets'])
    for target in data['targets']:
        runs=target.get('release_runs')
        if not isinstance(runs,list):continue
        for run in runs[:64]:
            raw=run.get('input_json') if isinstance(run,dict) else None
            if not isinstance(raw,str) or len(raw.encode())>512*1024:continue
            try:native=tsep.parse_json(raw.encode())
            except (ValueError,TypeError):continue
            nested=native.get('targets') if isinstance(native,dict) else None
            if isinstance(nested,list):
                for child in nested[:100]:
                    if isinstance(child,dict):
                        dated(child,child.get('observed_at'),issued_text)
                        evidence_targets.append(child)
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
    def delivery_provenance(value):
        if isinstance(value,dict):
            if value.get('provenance') in ('human','human-assisted','synthetic-exercise'):
                tsep.require((value['provenance']=='synthetic-exercise')==(access=='synthetic'),
                             'Delivery review provenance differs from evidence access')
            for child in value.values():delivery_provenance(child)
        elif isinstance(value,list):
            for child in value:delivery_provenance(child)
    for target in evidence_targets:
        for flag in ('delivery_synthetic', 'identity_synthetic', 'structured_synthetic', 'inspection_synthetic', 'sitemap_synthetic', 'link_synthetic', 'incoming_links_synthetic','graph_synthetic','hreflang_synthetic','xdefault_synthetic','presence_synthetic'):
            if flag in target:
                tsep.require(type(target[flag]) is bool and target[flag] == (access == 'synthetic'),
                             {'structured_synthetic': 'Structured-data provenance differs from access',
                              'delivery_synthetic': 'Delivery synthetic provenance differs from evidence access',
                              'identity_synthetic': 'Structured identity provenance differs from access',
                              'inspection_synthetic': 'Inspection provenance differs from access'}.get(flag, 'Explicit provenance differs from evidence access: ' + flag))
        if isinstance(target.get('intent'),dict) and 'critical_presence' in target['intent'] or any(k in target for k in ('presence_plan_review','presence_context_reviews')):
            tsep.require(type(target.get('presence_synthetic')) is bool and target['presence_synthetic']==(access=='synthetic'), 'Critical presence provenance differs from access')
            delivery_provenance(target)
        if 'delivery' in target.get('intent',{}):
            tsep.require((target.get('delivery_synthetic') is True)==(access=='synthetic'),
                         'Delivery synthetic provenance differs from evidence access')
            delivery_provenance(target)
    for target in evidence_targets:
        if ('sitemap_files' in target or
                isinstance(target.get('intent'), dict) and 'sitemap_files' in target['intent']):
            from conformance.sitemap_files import original_bytes
            tsep.require(type(target.get('sitemap_synthetic')) is bool and target['sitemap_synthetic']==(access=='synthetic'), 'Native sitemap provenance differs from evidence access')
            for native_file in target.get('sitemap_files',[]) if type(target.get('sitemap_files')) is list else []:
                if type(native_file) is dict:
                    tsep.require(native_file.get('provenance')==('synthetic-exercise' if access=='synthetic' else 'supplied-native-file'), 'Native file provenance mismatch')
                    if 'native' in native_file:
                        try: original_bytes(native_file['native'])
                        except (ValueError,TypeError,KeyError) as error: raise tsep.Invalid('Native sitemap intake refused: '+str(error)) from error
        if (any(name in target for name in ('validation_record', 'validation_plan_review', 'validation_review')) or
                isinstance(target.get('intent'), dict) and 'structured_validation' in target['intent']):
            tsep.require(access in ('synthetic','restricted'), 'Validation API evidence requires restricted access')
            delivery_provenance(target)
        if 'structured_identity' in target.get('intent',{}):
            tsep.require(type(target.get('identity_synthetic')) is bool and target['identity_synthetic']==(access=='synthetic'), 'Structured identity provenance differs from access')
            delivery_provenance(target)
        if 'structured_content' in target.get('intent',{}):
            tsep.require(type(target.get('structured_synthetic')) is bool and target['structured_synthetic']==(access=='synthetic'), 'Structured-data provenance differs from access')
            delivery_provenance(target)
        if 'inspection' in target.get('intent',{}):
            tsep.require((target.get('inspection_synthetic') is True)==(access=='synthetic'), 'Inspection provenance differs from access')
            tsep.require(access in ('synthetic','restricted'), 'Account inspection data requires restricted access')
            delivery_provenance(target)
    synthetic_dom(evidence_targets)
    for target in evidence_targets:
        agent_reviews = target.get('agent_reviews')
        records = list(agent_reviews) if isinstance(agent_reviews, list) else []
        records.append(target.get('agent_decision'))
        records.extend(target.get(k) for k in ('client_review', 'log_review', 'attribution', 'critical_plan_review', 'release_plan_review', 'release_review'))
        critical_reviews=target.get('critical_reviews')
        if isinstance(critical_reviews,list):records.extend(critical_reviews)
        for record in records:
            if isinstance(record, dict) and record.get('provenance') in ('human', 'human-assisted', 'synthetic-exercise'):
                tsep.require((record['provenance'] == 'synthetic-exercise') == (access == 'synthetic'),
                             'Agent review/decision provenance differs from evidence access')
        for name in ('field_review', 'lab_review'):
            review = target.get(name)
            if isinstance(review, dict) and review.get('provenance') in ('synthetic-exercise', 'supplied-review'):
                tsep.require((review['provenance'] == 'synthetic-exercise') == (access == 'synthetic'),
                             'Performance review provenance differs from evidence access')
    if any(r.startswith(('TS02-','TS41-')) for r in data['rules']):
        for target in evidence_targets:
            review = target.get('intent', {}).get('redirect_review', {})
            if review:
                tsep.require((review.get('provenance') == 'synthetic-exercise') == (access == 'synthetic'),
                             'Redirect review provenance differs from evidence access')
    if any(r.startswith(('TS04-','TS41-')) for r in data['rules']):
        for target in evidence_targets:
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
    if set(data['rules']) & {'TS25-A01','TS25-A02'}:
        from conformance.critical_presence import verify_public_diagnostic_budget
        try: verify_public_diagnostic_budget(source_observations)
        except (ValueError,TypeError,UnicodeError) as error: raise tsep.Invalid(str(error)) from error
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
        ts05_rules = {r['id'] for r in controls.get('TS05', {}).get('rules', [])}
        ts05_rows = [row for row in calculated if row['rule_id'] in ts05_rules]
        ts05_pairs = {(row['rule_id'], row['target']) for row in ts05_rows}
        ts05_whole_na = bool(ts05_rules) and ts05_rules <= set(data['rules']) and \
            ts05_pairs == {(rule, target) for rule in ts05_rules for target in targets} and \
            all(row['outcome'] == 'not-applicable' for row in ts05_rows)
        ts06_rules = {r['id'] for r in controls.get('TS06', {}).get('rules', [])}
        ts06_rows = [row for row in calculated if row['rule_id'] in ts06_rules]
        ts06_pairs = {(row['rule_id'], row['target']) for row in ts06_rows}
        ts06_whole_na = bool(ts06_rules) and ts06_rules <= set(data['rules']) and \
            ts06_pairs == {(rule, target) for rule in ts06_rules for target in targets} and \
            all(row['outcome'] == 'not-applicable' for row in ts06_rows)
        refs = {}
        for index, target in enumerate(data['targets'], 1):
            refs[target['url']] = list(shared) + diagnostic_refs[target['url']]
            for kind, payload in pieces(target).items():
                aid = 'target-' + str(index) + '-' + kind
                date, basis = dated(payload, target.get('observed_at'), issued_text)
                refs[target['url']].append(artifact(aid, kind, 'evidence/' + aid + '.json',
                    {'target': target['url'], 'date_basis': basis, 'record': payload}, [target['url']], date,
                    'Derived supplied record; ' + basis + '. Original fields unchanged; no missing evidence inferred.'))
        atoms = []
        for row in calculated:
            atom = dict(row, evidence_ids=refs[row['target']])
            if (row['rule_id'] in ts05_rules and row['outcome'] == 'not-applicable'
                    and not ts05_whole_na):
                atom['outcome'] = 'inconclusive'
                atom['reason'] += ('; target-level positive review does not create an atomic exemption; '
                                   'whole-control NA requires all declared targets to be positively reviewed')
            atoms.append(atom)
        for i, result in enumerate(report['results']):
            cid = result['control_id']
            if cid == 'TS05' and ts05_whole_na:
                intent_ids = sorted({a['id'] for a in report['artifacts']
                                     if a['kind'] == 'intent' and set(targets) <= set(a['targets'])})
                intent_ids.extend(sorted({a['id'] for a in report['artifacts']
                                          if a['kind'] == 'intent' and set(a['targets']) & set(targets)
                                          and a['id'] not in intent_ids}))
                report['results'][i] = {
                    'control_id': 'TS05', 'status': 'NA', 'evaluation_state': 'complete',
                    'reason': ('A complete, positive, dated TS05 inventory review establishes '
                               'non-applicability for every declared target; no site, server or index state inferred.'),
                    'procedure': NAME + ' ' + VERSION + '; positive whole-control applicability review; no collection.',
                    'evaluated_targets': list(targets), 'evidence_ids': intent_ids, 'atomic_results': [],
                }
                continue
            if cid == 'TS06' and ts06_whole_na:
                intent_ids = sorted({a['id'] for a in report['artifacts']
                                     if a['kind'] == 'intent' and set(targets) <= set(a['targets'])})
                intent_ids.extend(sorted({a['id'] for a in report['artifacts']
                                          if a['kind'] == 'intent' and set(a['targets']) & set(targets)
                                          and a['id'] not in intent_ids}))
                report['results'][i] = {
                    'control_id': 'TS06', 'status': 'NA', 'evaluation_state': 'complete',
                    'reason': ('A complete, positive, dated synthetic TS06 inventory review establishes '
                               'no sensitive routes for every declared target; no live site or server state inferred.'),
                    'procedure': NAME + ' ' + VERSION + '; positive synthetic whole-control applicability review; no collection.',
                    'evaluated_targets': list(targets), 'evidence_ids': intent_ids, 'atomic_results': [],
                }
                continue
            rows = [a for a in atoms if a['rule_id'].startswith(cid + '-')]
            if rows:
                report['results'][i] = control_result(cid, rows, controls[cid], targets)
                if cid in ('TS34', 'TS35'):
                    report['results'][i]['reason'] += ' C = documentation conforme / conforming documentation, not good performance. '
                    report['results'][i]['reason'] += '\n'.join(a['rule_id'] + ' — ' + a['reason'] for a in rows)
                if cid == 'TS42':
                    report['results'][i]['reason'] += ' Usages déclarés et pièces fournies seulement / Declared usages and supplied evidence only; no real agent visit, identity, operator compliance or citation established.'
                if cid == 'TS36':
                    report['results'][i]['reason'] += ' Suivi documentaire du changement / Documentary release follow-up; future stages remain inconclusive, no causal or authenticated Google visit claim.'
                if cid == 'TS24':
                    report['results'][i]['reason'] += ' Rôle x-default documentaire fourni / Supplied documentary x-default role; no authenticated reviewer, representative audience or soft404 detection.'
                if cid == 'TS23':
                    report['results'][i]['reason'] += ' Groupe et canaux déclarés / Supplied prior cluster and channels; no language validity, translation, indexing, canonical, x-default role or Google processing claim.'
                if cid == 'TS18':
                    report['results'][i]['reason'] += ' Graphe et revues fournis / Supplied bounded graph and reviews; no site-wide orphan, complete crawl, authenticated reviewer or universal depth threshold.'
                if cid == 'TS16':
                    report['results'][i]['reason'] += ' Population préalable fournie seulement / Prior supplied population only; bounded absence is not a site-wide orphan, authenticated importance, interaction or indexing claim.'
                if cid == 'TS17':
                    report['results'][i]['reason'] += ' Source et états déclarés seulement / Supplied source and declared states only; no authenticated interaction, acquisition or Google discovery.'
                if cid == 'TS15':
                    report['results'][i]['reason'] += ' Population déclarée de fichiers fournis seulement / Declared population of supplied files only; no server observation, site completeness or full XSD validity.'
                if cid == 'TS33':
                    report['results'][i]['reason'] += ' Couches séparées / Separate supplied page and indexed API layers; known vocabulary names only, no current eligibility or display guarantee.'
                if cid == 'TS32':
                    report['results'][i]['reason'] += ' Corpus JSON-LD et revues fournis / Supplied JSON-LD corpus and reviews; no authenticated sources, semantic identity or temporal stability.'
                if cid == 'TS31':
                    report['results'][i]['reason'] += ' JSON-LD et revues de contenu fournis / Supplied JSON-LD and content reviews; no authenticated visibility or facts, vocabulary validity or rich-result guarantee.'
                if cid == 'TS12':
                    report['results'][i]['reason'] += ' Comparaison documentaire des surfaces HTTP/HTML et états DOM prévus / Documentary comparison of HTTP/HTML and declared DOM states; literal strings, no semantic URL equivalence, TS10, current selection or indexing inferred.'
                if cid == 'TS08':
                    report['results'][i]['reason'] += ' Dossier de la sélection / Selected-set documentation; Google API verdict is distinct, no live state, indexing promise or TS12 outcome.'
                if cid == 'TS39':
                    report['results'][i]['reason'] += ' Matrice de diffusion déclarée et preuves fournies / Declared delivery matrix and supplied evidence; native tests are not whole-control assessments, no actual Googlebot visit, region or cache cause without qualified linked evidence.'
                if cid == 'TS44':
                    report['results'][i]['reason'] += ' Référence sans JS et représentations fournies / No-JS reference and supplied representations; no agent consumption, factual truth or citation established. Authored DOM is not a browser observation.'
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
