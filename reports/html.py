"""Self-contained, read-only presentation of validated TSEP reports. Apache-2.0.

No network, JavaScript, HTML capture execution or new assessment. All outcomes
come from the supplied reports; integrity is checked again before embedding bytes.
"""
import base64
import hashlib
from html import escape
import json
from pathlib import Path

import tsep
from conformance.http import raw_bytes

VERSION = '20'
MAX_EMBED_BYTES = 32 * 1024 * 1024  # Per report, including all evidence and JSON.
ROOT = Path(__file__).resolve().parent

TEXT = {
    'fr': {
        'essential_state_identity': 'États et scénarios déclarés par le fournisseur ; interactions non authentifiées.',
        'essential_binding': 'Portée : association aux octets HTTP fournis ; acquisition réelle non authentifiée.',
        'essential_repeated': 'Snapshots identiques pour plusieurs états déclarés',
        'essential_scripts_enabled': 'Hypothèse scripts activés',
        'essential_scripts_disabled': 'Hypothèse scripts désactivés',
        'essential_source': 'Source fournie',
        'essential_rendered': 'États rendus déclarés',
        'essential_found': 'Destinations présentes',
        'essential_missing': 'Destinations non relevées',
        'essential_state': 'Stade ou état',
        'essential_empty': 'Aucune',
        'essential_details': 'Diagnostic complet conservé',
        'essential_links_note': 'TS17 : stratégie source et états déclarés par le fournisseur ; aucune interaction, acquisition réelle ou découverte Google authentifiée.',
        'essential_links_values': 'Liens essentiels — stades séparés',
        'sitemap_files_note': 'TS15 : fichiers fournis dans une population déclarée ; racines non découvertes, aucun constat du serveur ni exhaustivité du site. Structure minimale seulement, pas validation XSD complète.',
        'sitemap_files_values': 'Population de fichiers fournis',
        'sitemap_roots_note': 'Racines déclarées ; leur découverte et l’exhaustivité du site ne sont pas établies.',
        'sitemap_population_count': 'Fichiers dans la population déclarée',
        'sitemap_roots': 'Racines déclarées',
        'sitemap_bytes': 'Octets décompressés lus',
        'sitemap_entries': 'Entrées comptées',
        'sitemap_measurement': 'Précision du nombre d’octets',
        'sitemap_exact': 'Exact',
        'sitemap_lower_bound': 'Borne inférieure',
        'sitemap_attribution': 'Attribution du format',
        'sitemap_count_unknown': 'Non établi',
        'sitemap_unattributed': 'Taille observée ; format sitemap non établi. Aucune violation de limite conclue.',
        'sitemap_observed': 'Date déclarée du fichier',
        'sitemap_complete': 'Lecture XML complète',
        'sitemap_yes': 'Oui',
        'sitemap_unknown': 'Non établie',

        'validation_note': 'TS33 : captures de page liées et instantané indexé séparé ; noms Schema.org seulement, erreurs conservées, aucune éligibilité actuelle ni apparition garantie.',
        'validation_values': 'Couches de validation retenues',
        'identity_note':'TS32 : identifiants, références et doublons qualifiés sur les exports fournis. Aucune stabilité temporelle, source ou identité authentifiée.',
        'identity_values':'Identifiants et références du corpus déclaré',
        'structured_note':'TS31 : JSON-LD recalculé et revues liées au contenu fourni. Aucune visibilité ou vérité authentifiée, validation Schema.org ou garantie de résultat enrichi.',
        'structured_values':'Lectures JSON-LD et qualifications du contenu',
        'monitoring_note':'TS36 : suivi documentaire baseline/J+1/J+7/J+30. Échéance future = indéterminé ; aucune causalité, visite Google authentifiée ou indexation déduite.',
        'monitoring_pending':'Échéance future', 'monitoring_title':'Observations par échéance',
        'monitoring_requests':'GET filtrés', 'monitoring_errors':'Réponses 5xx',
        'comparison_note': 'TS12 : dossier de comparaison HTTP/HTML et états DOM prévus. Égalité littérale ≠ équivalence d’URL ; ni canonical correcte, ni TS10, ni indexation déduits.',
        'comparison_values': 'Comparaisons attribuées et revue fournie',
        'comparison_surface': 'Surface', 'comparison_state': 'État de lecture',
        'comparison_present': 'Valeur(s) présente(s)', 'comparison_absent': 'Absence qualifiée',
        'comparison_dates': 'Dates distinctes : acquisition API / capture technique',
        'inspection_note': 'TS08 : dossier de la sélection, pas un état live ni une garantie d’indexation. Verdict Google, observations et décisions TSEP restent distincts.',
        'inspection_values': 'Lectures de l’API et qualification fournie',
        'delivery_note': 'TS39 compare les cellules déclarées à leur politique. Les variations légitimes restent distinctes des défauts. Revues et traces fournies ; aucune visite réelle Googlebot ou couverture de tous les POP déduite.',
        'delivery_values': 'Signaux et attribution par cellule',
        'delivery_native': 'Résultats des tests natifs conservés',
        'release_note': 'TS41 évalue le dispositif de déploiement. Un défaut SEO bien détecté et bloqué peut accompagner C ; ses résultats restent visibles ci-dessous. Reçus et revues fournis, sans authentification de CI distante.',
        'release_values': 'Vérifications du dispositif',
        'release_native': 'Résultats SEO sous-jacents conservés',
        'release_subject': 'Vérification',
        'release_execution': 'Exécution et phase',
        'critical_content_note': 'TS44 relie les faits critiques déclarés à des représentations fournies, sous une référence sans JavaScript. Un DOM rédigé reste un exemple ; aucune lecture réelle par un agent ni vérité des faits déduite.',
        'agent_access_note': 'C décrit le traitement prévu du client de test et ses traces. Un refus attendu peut être cohérent ; l’accès réel, l’identité et les visites de l’opérateur restent non établis.',
        'agent_note': 'Politique déclarée et décisions fournies : aucune visite réelle, identité d’agent ou application par un opérateur démontrée.',
        'agent_values': 'Usages et décisions conservés', 'agent_subject': 'Mécanisme / rôle',
        'agent_evidence': 'Preuves et choix fournis', 'agent_effective': 'Choix effectif',
        'agent_tradeoff': 'Arbitrage explicite', 'agent_raw': 'Diagnostic complet conservé',
        'performance_note': 'C signifie « documentation conforme ». La qualité des performances est indiquée séparément ci-dessous ; le laboratoire ne mesure pas les Core Web Vitals terrain.',
        'performance_values': 'Mesures de performance conservées',
        'metric_name': 'Métrique', 'metric_value': 'Valeur conservée', 'metric_quality': 'Qualité / portée',
        'good': 'Bon', 'needs-improvement': 'À améliorer', 'poor': 'Mauvais', 'unknown': 'Inconnu',
        'lab_only': 'Laboratoire · INP non mesuré', 'median_range': 'médiane ; min–max',
        'preflight': 'Précontrôle des marqueurs sur la référence',
        'preflight_note': 'Contrôle préparatoire déclaré, distinct du résultat TS01. Une empreinte identique peut conclure sans exécuter les marqueurs sur la mesure.',
        'media_comparison': 'Type de média observé : référence et mesure',
        'media_note': 'Un écart brut de Content-Type est à examiner ; il ne modifie pas la décision draft.7 et ne prouve pas à lui seul une incompatibilité.',
        'title': 'Rapport de preuves', 'subtitle': 'Des observations aux décisions, chaque résultat conserve ses preuves.',
        'offline': 'Document autonome · hors ligne', 'draft': 'Protocole expérimental',
        'overview': 'Vue d’ensemble', 'comparison': 'Comparaison', 'results': 'Résultats',
        'captures': 'Captures et intention', 'evidence': 'Pièces de preuve', 'method': 'Périmètre et méthode',
        'decision': 'Décision dans le périmètre', 'controls': 'Contrôles sélectionnés', 'targets': 'Cibles déclarées',
        'scope_only': 'La décision concerne uniquement les contrôles et les cibles déclarés.',
        'not_evaluated': 'contrôles hors sélection', 'artifact_count': 'pièces liées au rapport',
        'valid': 'Structure et empreintes vérifiées à la génération',
        'integrity_limit': 'Cette vérification établit la cohérence du rapport et l’intégrité des fichiers lus. Elle ne prouve ni leur authenticité, ni la justesse des jugements, ni l’indexation ou le classement.',
        'synthetic': 'Preuves synthétiques présentes', 'synthetic_note': 'Au moins une pièce est déclarée synthétique. Ce rapport ne doit pas être présenté comme un constat entièrement issu d’un site réel.',
        'restricted': 'Pièces déclarées restreintes incluses', 'restricted_note': 'Ce fichier autonome contient aussi les pièces restreintes du rapport. Conserver leurs restrictions d’accès lors de son partage.',
        'before': 'Rapport précédent', 'after': 'Rapport actuel', 'same_input': 'Même fichier de captures fourni',
        'same_input_note': 'Les deux rapports lient un fichier d’entrée fourni dont les octets sont identiques. Les résultats ci-dessous sont ceux des rapports conservés ; cet affichage ne réévalue pas les captures.',
        'other_input': 'Identité des captures non établie',
        'other_input_note': 'Les contrôles et cibles déclarés correspondent, mais aucun fichier d’entrée identique n’est établi. Ne pas attribuer les écarts au seul changement d’outil.',
        'rule': 'Règle', 'target': 'Cible', 'result': 'Résultat', 'reason': 'Motif conservé',
        'missing': 'Aucune observation fournie', 'changed': 'résultats atomiques différents',
        'assessor': 'Évaluateur déclaré', 'tool': 'Outil déclaré', 'issued': 'Émission du rapport',
        'mode': 'Mode d’évaluation', 'not_supplied': 'Non fourni', 'protocol': 'Protocole',
        'report_hash': 'SHA-256 du rapport JSON', 'download_report': 'Télécharger le rapport JSON original',
        'control_reason': 'Conclusion du contrôle', 'procedure': 'Procédure déclarée',
        'expectation': 'Attendu de la règle', 'limits': 'Limites de la règle', 'automation': 'Automatisation',
        'inputs': 'Types de preuve requis', 'linked': 'Preuves liées', 'unobserved': 'Observations absentes',
        'unobserved_note': 'Ces couples règle/cible ne figurent pas dans le rapport ; aucune réussite n’est ajoutée.',
        'intent': 'Intention préalable fournie', 'declared': 'Date de déclaration',
        'expected_url': 'URL finale attendue', 'expected_hash': 'Empreinte du corps attendue',
        'identity_reader': 'Lecteur de marqueurs déclaré', 'identity_legacy': 'Lecteur historique (aucun profil fourni)',
        'identity_parsed_note': 'Texte parsé selon deux hypothèses statiques ; aucune visibilité ni exécution JavaScript mesurée. Ce profil ne remplace pas les priorités URL, empreinte et stabilité.',
        'representation': 'Politique de représentation', 'markers': 'Marqueurs requis / interdits',
        'observed': 'Date d’observation déclarée', 'request_context': 'Contexte de la capture',
        'raw_response': 'Lire la réponse HTTP conservée', 'raw_request': 'Lire la requête conservée',
        'chain': 'Échanges fournis, dans leur ordre déclaré',
        'capture_note': 'Lecture des champs de l’entrée conservée, sans requête réseau ni nouvelle interprétation. Un statut visible dans une trace ne suffit pas à valider une règle.',
        'no_capture': 'Aucune entrée de captures liée sous la forme attendue ; consulter les pièces ci-dessous.',
        'download': 'Télécharger les octets d’origine', 'preview': 'Aperçu texte échappé',
        'binary': 'Pièce binaire : utiliser le téléchargement pour obtenir ses octets exacts.',
        'path': 'Chemin dans le paquet', 'access': 'Accès déclaré', 'description': 'Description conservée',
        'selection': 'Méthode de sélection', 'exclusions': 'Exclusions déclarées', 'profile': 'Profil',
        'none': 'Aucune', 'identity': 'Identité du rapport', 'source': 'Rapport source',
        'coverage_inventory': 'Couverture déclarée par l’outil', 'implemented': 'Pris en charge',
        'identity_criteria': 'Critères d’identité TS01-A02', 'criteria_origin': 'Origine des critères',
        'reference_adopted': 'URL finale et empreinte dérivées de la référence, adoptées par l’opérateur.',
        'operator_final': 'URL finale déclarée par l’opérateur et comparée à la référence ; empreinte issue de la référence.',
        'origin_unknown': 'Origine non déclarée dans les captures fournies.',
        'policy_digest': 'digest — une empreinte différente reste indéterminée sans autre critère.',
        'policy_stable': 'stable — toute variation, y compris un nonce ou une date, constitue un échec selon ce choix explicite.',
        'policy_markers': 'markers — comparaison des marqueurs seulement si l’empreinte diffère ; une empreinte identique ne teste pas les marqueurs.',
        'required_markers': 'Marqueurs requis', 'forbidden_markers': 'Marqueurs interdits',
        'collector_consistency': 'Collecteur identique entre référence et mesure, selon les empreintes vérifiées à la collecte.',
        'run_selection': 'Exécutions présentées : celles fournies dans ce paquet. L’absence d’autres essais ou une campagne exhaustive ne sont pas établies.',
        'deferred': 'Différé — indéterminé', 'out-of-scope': 'Hors couverture',
        'footer': 'Présentation générée par TSEP HTML report', 'read_only': 'Aucune collecte, aucun recalcul de verdict, aucune ressource externe.',
        'skip': 'Aller au contenu', 'all_evidence': 'Ouvrir une pièce pour lire son contenu et vérifier son empreinte.',
        'C': 'Conforme dans le périmètre', 'NC': 'Non conforme dans le périmètre',
        'NT': 'Non établi', 'NA': 'Non applicable', 'pass': 'Réussi', 'fail': 'Échec',
        'inconclusive': 'Indéterminé', 'not-applicable': 'Non applicable',
        'GO_WITH_RESERVATIONS': 'Attendus satisfaits, réserves conservées',
        'NO_GO': 'Une cause bloquante demeure', 'INCOMPLETE': 'Évaluation incomplète', 'REVIEW': 'Décision à examiner',
    },
    'en': {
        'essential_state_identity': 'Provider-declared states and scenarios; interactions are unauthenticated.',
        'essential_binding': 'Scope: supplied HTTP-byte association; actual acquisition is unauthenticated.',
        'essential_repeated': 'Identical snapshots across declared states',
        'essential_scripts_enabled': 'Scripting-enabled hypothesis',
        'essential_scripts_disabled': 'Scripting-disabled hypothesis',
        'essential_source': 'Supplied source',
        'essential_rendered': 'Declared rendered states',
        'essential_found': 'Destinations present',
        'essential_missing': 'Destinations not found in this reading',
        'essential_state': 'Stage or state',
        'essential_empty': 'None',
        'essential_details': 'Retained full diagnostic',
        'essential_links_note': 'TS17: source strategy and provider-declared states; no authenticated interaction, actual acquisition or Google discovery.',
        'essential_links_values': 'Essential links — separate stages',
        'sitemap_files_note': 'TS15: supplied files in a declared population; undiscovered roots, no server observation or site completeness. Minimal structure only, not full XSD validation.',
        'sitemap_files_values': 'Supplied file population',
        'sitemap_roots_note': 'Declared roots; their discovery and site completeness are not established.',
        'sitemap_population_count': 'Files in the declared population',
        'sitemap_roots': 'Declared roots',
        'sitemap_bytes': 'Decoded bytes read',
        'sitemap_entries': 'Entries counted',
        'sitemap_measurement': 'Byte measurement precision',
        'sitemap_exact': 'Exact',
        'sitemap_lower_bound': 'Lower bound',
        'sitemap_attribution': 'Format attribution',
        'sitemap_count_unknown': 'Not established',
        'sitemap_unattributed': 'Observed size; sitemap format not established. No limit violation concluded.',
        'sitemap_observed': 'Declared file date',
        'sitemap_complete': 'Complete XML reading',
        'sitemap_yes': 'Yes',
        'sitemap_unknown': 'Not established',

        'validation_note': 'TS33: bound page captures and separate indexed snapshot; Schema.org names only, errors retained, no guaranteed current eligibility or display.',
        'validation_values': 'Retained validation layers',
        'identity_note':'TS32: IDs, references and duplicates qualified in supplied exports. No temporal stability, authenticated source or identity.',
        'identity_values':'Identifiers and references in the declared corpus',
        'structured_note':'TS31: recomputed JSON-LD and reviews bound to supplied content. No authenticated visibility or truth, Schema.org validation or rich-result guarantee.',
        'structured_values':'JSON-LD readings and content qualifications',
        'monitoring_note':'TS36: documentary baseline/D+1/D+7/D+30 follow-up. Future stage is inconclusive; no causality, authenticated Google visit or indexing inferred.',
        'monitoring_pending':'Future stage', 'monitoring_title':'Observations by stage',
        'monitoring_requests':'Filtered GETs', 'monitoring_errors':'5xx responses',
        'comparison_note': 'TS12: comparison dossier for HTTP/HTML and planned DOM states. Literal equality is not URL equivalence; no correct canonical, TS10 or indexing inferred.',
        'comparison_values': 'Attributed comparisons and supplied review',
        'comparison_surface': 'Surface', 'comparison_state': 'Reading state',
        'comparison_present': 'Present value(s)', 'comparison_absent': 'Qualified absence',
        'comparison_dates': 'Separate dates: API retrieval / technical capture',
        'inspection_note': 'TS08: selected-set documentation, not live state or guaranteed indexing. Google verdict, observations and TSEP decisions remain distinct.',
        'inspection_values': 'API readings and supplied qualification',
        'delivery_note': 'TS39 compares declared cells against policy. Legitimate variation remains distinct from defects. Supplied reviews and traces; no actual Googlebot visit or whole-POP coverage inferred.',
        'delivery_values': 'Signals and attribution per cell',
        'delivery_native': 'Retained native test results',
        'release_note': 'TS41 assesses the deployment process. A correctly detected and blocked SEO defect can accompany C; its results stay visible below. Supplied receipts/reviews, without remote CI authentication.',
        'release_values': 'Process checks',
        'release_native': 'Retained underlying SEO results',
        'release_subject': 'Check',
        'release_execution': 'Execution and phase',
        'critical_content_note': 'TS44 binds declared critical facts to supplied representations under a no-JavaScript reference. An authored DOM remains an example; no actual agent consumption or factual truth inferred.',
        'agent_access_note': 'C describes planned test-client treatment and its traces. Expected denial can conform; real operator access, identity and visits remain unestablished.',
        'agent_note': 'Declared policy and supplied decisions: no actual visit, agent identity or operator compliance established.',
        'agent_values': 'Retained purposes and decisions', 'agent_subject': 'Mechanism / role',
        'agent_evidence': 'Supplied evidence and choices', 'agent_effective': 'Effective choice',
        'agent_tradeoff': 'Explicit tradeoff', 'agent_raw': 'Complete retained diagnostic',
        'performance_note': 'C means conforming documentation. Performance quality is shown separately below; laboratory measurements do not establish field Core Web Vitals.',
        'performance_values': 'Retained performance measurements',
        'metric_name': 'Metric', 'metric_value': 'Retained value', 'metric_quality': 'Quality / scope',
        'good': 'Good', 'needs-improvement': 'Needs improvement', 'poor': 'Poor', 'unknown': 'Unknown',
        'lab_only': 'Laboratory · INP not measured', 'median_range': 'median; min–max',
        'preflight': 'Reference marker preflight',
        'preflight_note': 'Supplied preparation check, separate from the TS01 result. An equal digest can resolve identity without checking evaluation markers.',
        'media_comparison': 'Observed media type: reference and evaluation',
        'media_note': 'A raw Content-Type difference needs inspection; it does not alter the draft.7 decision or alone establish incompatibility.',
        'title': 'Evidence report', 'subtitle': 'From observations to decisions, every result retains its evidence.',
        'offline': 'Self-contained · offline', 'draft': 'Experimental protocol',
        'overview': 'Overview', 'comparison': 'Comparison', 'results': 'Results',
        'captures': 'Captures and intent', 'evidence': 'Evidence files', 'method': 'Scope and method',
        'decision': 'Decision within scope', 'controls': 'Selected controls', 'targets': 'Declared targets',
        'scope_only': 'The decision concerns only the declared controls and targets.',
        'not_evaluated': 'controls outside selection', 'artifact_count': 'files linked to this report',
        'valid': 'Structure and fingerprints checked at generation',
        'integrity_limit': 'This check establishes report consistency and the integrity of the files read. It does not establish their authenticity, the correctness of judgments, indexing or ranking.',
        'synthetic': 'Synthetic evidence present', 'synthetic_note': 'At least one file is declared synthetic. Do not present this report as observations entirely collected from a real site.',
        'restricted': 'Declared restricted evidence included', 'restricted_note': 'This self-contained file also embeds the report’s restricted evidence. Preserve its access restrictions when sharing it.',
        'before': 'Previous report', 'after': 'Current report', 'same_input': 'Same supplied captures file',
        'same_input_note': 'Both reports link a supplied input file with identical bytes. The results below are those in the retained reports; this presentation does not reassess the captures.',
        'other_input': 'Capture identity not established',
        'other_input_note': 'Selected controls and declared targets match, but no identical input file is established. Do not attribute differences to the tool change alone.',
        'rule': 'Rule', 'target': 'Target', 'result': 'Result', 'reason': 'Retained reason',
        'missing': 'No observation supplied', 'changed': 'different atomic outcomes',
        'assessor': 'Declared assessor', 'tool': 'Declared tool', 'issued': 'Report issued',
        'mode': 'Assessment mode', 'not_supplied': 'Not supplied', 'protocol': 'Protocol',
        'report_hash': 'Report JSON SHA-256', 'download_report': 'Download original report JSON',
        'control_reason': 'Control conclusion', 'procedure': 'Declared procedure',
        'expectation': 'Rule expectation', 'limits': 'Rule limitations', 'automation': 'Automation',
        'inputs': 'Required evidence kinds', 'linked': 'Linked evidence', 'unobserved': 'Absent observations',
        'unobserved_note': 'These rule/target pairs are absent from the report; no passing result is added.',
        'intent': 'Supplied prior intent', 'declared': 'Declaration date',
        'expected_url': 'Expected final URL', 'expected_hash': 'Expected body digest',
        'identity_reader': 'Declared marker reader', 'identity_legacy': 'Historical reader (no supplied profile)',
        'identity_parsed_note': 'Parsed text under two static hypotheses; no measured visibility or JavaScript execution. This profile does not replace URL, hash and stability precedence.',
        'representation': 'Representation policy', 'markers': 'Required / forbidden markers',
        'observed': 'Declared observation date', 'request_context': 'Capture context',
        'raw_response': 'Read retained HTTP response', 'raw_request': 'Read retained request',
        'chain': 'Supplied exchanges in declared order',
        'capture_note': 'Fields read from the retained input, without network requests or new interpretation. A status visible in a trace is insufficient to validate a rule.',
        'no_capture': 'No linked captures input in the expected shape; consult the evidence below.',
        'download': 'Download original bytes', 'preview': 'Escaped text preview',
        'binary': 'Binary evidence: download the exact original bytes.',
        'path': 'Path within bundle', 'access': 'Declared access', 'description': 'Retained description',
        'selection': 'Selection method', 'exclusions': 'Declared exclusions', 'profile': 'Profile',
        'none': 'None', 'identity': 'Report identity', 'source': 'Source report',
        'coverage_inventory': 'Tool-declared coverage', 'implemented': 'Supported',
        'identity_criteria': 'TS01-A02 identity criteria', 'criteria_origin': 'Criteria origin',
        'reference_adopted': 'Final URL and digest derived from the captured reference, adopted by the operator.',
        'operator_final': 'Final URL declared by the operator and checked against the reference; digest derived from the reference.',
        'origin_unknown': 'Origin not declared in the supplied captures.',
        'policy_digest': 'digest — a changed digest remains inconclusive without further criteria.',
        'policy_stable': 'stable — any change, including a nonce or timestamp, fails under this explicit choice.',
        'policy_markers': 'markers — tested only when the digest differs; a matching digest does not test markers.',
        'required_markers': 'Required markers', 'forbidden_markers': 'Forbidden markers',
        'collector_consistency': 'Same collector for reference and evaluation, according to fingerprints checked during collection.',
        'run_selection': 'Presented runs: those supplied in this bundle. This does not establish the absence of other attempts or an exhaustive campaign.',
        'deferred': 'Deferred — inconclusive', 'out-of-scope': 'Outside coverage',
        'footer': 'Generated by TSEP HTML report', 'read_only': 'No collection, verdict recalculation or external resources.',
        'skip': 'Skip to content', 'all_evidence': 'Open a file to read its contents and inspect its fingerprint.',
        'C': 'Conforming in scope', 'NC': 'Nonconforming in scope', 'NT': 'Not established', 'NA': 'Not applicable',
        'pass': 'Pass', 'fail': 'Fail', 'inconclusive': 'Inconclusive', 'not-applicable': 'Not applicable',
        'GO_WITH_RESERVATIONS': 'Expectations met, reservations retained',
        'NO_GO': 'A blocking cause remains', 'INCOMPLETE': 'Incomplete assessment', 'REVIEW': 'Decision requires review',
    },
}


def esc(value):
    return escape(str(value), quote=True)


def pretty(value):
    return json.dumps(value, ensure_ascii=False, indent=2)


def badge(value, words):
    # All status classes are validated enums; labels also retain their raw codes.
    return '<span class="badge ' + esc(value) + '">' + esc(value) + ' · ' + esc(words[value]) + '</span>'


def item(label, value, code=False):
    return '<dt>' + esc(label) + '</dt><dd' + (' class="mono"' if code else '') + '>' + esc(value) + '</dd>'


def download(raw, label, name):
    # application/octet-stream avoids rendering captured HTML as an active page.
    return '<a class="download" download="' + esc(name) + '" href="data:application/octet-stream;base64,' + base64.b64encode(raw).decode('ascii') + '">' + esc(label) + ' ↓</a>'


def load(path, root=None):
    path = Path(path)
    with path.open('rb') as handle:
        original = handle.read(tsep.MAX_JSON_BYTES + 1)
    report = tsep.parse_json(original)
    root = Path(root) if root is not None else path.parent
    summary = tsep.validate(report, root)
    files, size = {}, len(original)
    tsep.require(size <= MAX_EMBED_BYTES, 'HTML evidence exceeds 32 MiB per report; no partial embedding')
    for artifact in report['artifacts']:
        file = tsep.evidence_path(root, artifact['path'])
        with file.open('rb') as handle:
            raw = handle.read(MAX_EMBED_BYTES - size + 1)
        size += len(raw)
        tsep.require(size <= MAX_EMBED_BYTES, 'HTML evidence exceeds 32 MiB per report; no partial embedding')
        tsep.require(hashlib.sha256(raw).hexdigest() == artifact['sha256'],
                     'Evidence changed while preparing HTML: ' + artifact['id'])
        files[artifact['id']] = raw
    return {'report': report, 'summary': summary, 'raw': original, 'files': files,
            'sha256': hashlib.sha256(original).hexdigest()}


def captures(bundle):
    artifact = next((a for a in bundle['report']['artifacts']
                     if a['id'] == 'supplied-input' and a['kind'] == 'operator-docs'), None)
    if artifact is not None:
        try:
            data = tsep.parse_json(bundle['files'][artifact['id']])
            if isinstance(data, dict) and data.get('input_version') in ('1', '2') and isinstance(data.get('targets'), list):
                return data
        except (ValueError, UnicodeError, RecursionError):
            pass
    return None


def report_identity(bundle, words, prefix):
    report = bundle['report']
    tool = report['assessor'].get('tool', {})
    return ('<dl>' + item(words['tool'], (tool.get('name', '') + ' ' + tool.get('version', '')).strip() or words['not_supplied'])
            + item(words['issued'], report['issued_at']) + item(words['protocol'], report['protocol']['version'])
            + item(words['report_hash'], bundle['sha256'], True) + '</dl>'
            + download(bundle['raw'], words['download_report'], prefix + '-report.json'))


def comparison(current, previous, words):
    old, new = previous['report'], current['report']
    tsep.require(old['protocol'] == new['protocol'] and old['profile'] == new['profile']
                 and set(old['controls']) == set(new['controls'])
                 and set(old['scope']['targets']) == set(new['scope']['targets']),
                 'HTML comparison requires identical protocol, profile, selected controls and target set')
    same = (captures(current) is not None and captures(previous) is not None
            and current['files']['supplied-input'] == previous['files']['supplied-input'])
    by_pair = lambda report: {(a['rule_id'], a['target']): a for r in report['results'] for a in r.get('atomic_results', [])}
    left, right = by_pair(old), by_pair(new)
    rows, changed = [], 0
    for key in sorted(set(left) | set(right)):
        before, after = left.get(key), right.get(key)
        changed += (before or {}).get('outcome') != (after or {}).get('outcome')
        cells = []
        for atom in (before, after):
            cells.append('<td>' + (badge(atom['outcome'], words) + '<p>' + esc(atom['reason']) + '</p>'
                                  if atom else esc(words['missing'])) + '</td>')
        rows.append('<tr><th scope="row"><code>' + esc(key[0]) + '</code></th><td class="target">' + esc(key[1]) + '</td>' + ''.join(cells) + '</tr>')
    label = 'same_input' if same else 'other_input'
    out = '<section id="comparison"><div class="section-head"><h2>' + esc(words['comparison']) + '</h2><span class="muted small">' + str(changed) + ' ' + esc(words['changed']) + '</span></div>'
    out += '<div class="card comparison"><h3>' + esc(words[label]) + '</h3><p class="comparison-intro">' + esc(words[label + '_note']) + '</p>'
    out += '<div class="two">'
    for bundle, side in ((previous, 'before'), (current, 'after')):
        out += '<div><p class="eyebrow">' + esc(words[side]) + '</p><p class="mono">' + esc(bundle['summary']['decision']) + '</p>' + report_identity(bundle, words, side) + '</div>'
    out += '</div></div><div class="table-scroll"><table><thead><tr>' + ''.join('<th scope="col">' + esc(words[x]) + '</th>' for x in ('rule', 'target', 'before', 'after')) + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div></section>'
    return out


def proof_links(refs, prefix):
    return '<div class="proof-links">' + ''.join('<a href="#' + prefix + '-evidence-' + esc(ref) + '">' + esc(ref) + '</a>' for ref in refs) + '</div>'


def identity_context(target, words):
    """Show supplied criteria, never infer operator approval or reevaluate them."""
    if not isinstance(target, dict) or not isinstance(target.get('intent'), dict):
        return ''
    intent = target['intent']
    context = target.get('context', {})
    context = context if isinstance(context, dict) else {}
    basis = context.get('identity_basis', {})
    basis = basis if isinstance(basis, dict) else {}
    origin = {'reference-adopted': 'reference_adopted', 'operator-final-url': 'operator_final'}.get(basis.get('origin'), 'origin_unknown')
    policy = ('stable' if intent.get('representation') == 'stable' else 'markers'
              if intent.get('required_markers') or intent.get('forbidden_markers') else 'digest')
    out = '<div class="notice identity-context"><strong>' + esc(words['identity_criteria']) + '</strong><dl>'
    out += item(words['criteria_origin'], words[origin]) + item(words['representation'], words['policy_'+policy])
    out += item(words['declared'], intent.get('declared_at', words['not_supplied']))
    out += item(words['expected_url'], intent.get('expected_final_url', words['not_supplied']))
    out += item(words['expected_hash'], intent.get('expected_body_sha256', words['not_supplied']), True)
    out += item(words['identity_reader'], intent.get('identity_reader', words['identity_legacy']))
    for label in ('required_markers', 'forbidden_markers'):
        out += item(words[label], pretty(intent.get(label, [])))
    out += '</dl>'
    if intent.get('identity_reader') == 'html-tree-markers-v1':
        out += '<p class="small">' + esc(words['identity_parsed_note']) + '</p>'
    if context.get('collector_matches_reference') is True:
        out += '<p class="small">' + esc(words['collector_consistency']) + '</p>'
    for key, label, note in (('reference_preflight', 'preflight', 'preflight_note'),
                             ('media_comparison', 'media_comparison', 'media_note')):
        if isinstance(context.get(key), dict):
            out += '<h5>'+esc(words[label])+'</h5><p class="small">'+esc(words[note])+'</p><pre>'+esc(pretty(context[key]))+'</pre>'
    return out + '</div>'


def performance_values(result, words):
    """Present retained reader diagnostics; never infer or recalculate a metric."""
    out = '<div class="notice"><strong>' + esc(words['performance_note']) + '</strong></div>'
    seen = set()
    for atom in result.get('atomic_results', []):
        if atom['target'] in seen:
            continue
        prefix = 'Performance documentation / documentation de performance: '
        if not atom['reason'].startswith(prefix):
            continue
        try:
            note = json.loads(atom['reason'][len(prefix):])
        except ValueError:
            continue
        if not isinstance(note, dict) or not isinstance(note.get('metrics'), dict):
            continue
        seen.add(atom['target'])
        rows = ''
        for name, value in note['metrics'].items():
            if not isinstance(value, dict):
                continue
            if 'classification' in value:
                display = str(value.get('p75', '—')) + ' ' + str(value.get('unit', '')) + ' · p75'
                quality = words.get(value['classification'], words['unknown'])
            else:
                display = str(value.get('median', '—')) + ' ; ' + str(value.get('minimum', '—')) + '–' + str(value.get('maximum', '—')) + ' ' + str(value.get('unit', '')) + ' (' + words['median_range'] + ')'
                quality = words['lab_only']
            rows += '<tr><th scope="row">' + esc(name) + '</th><td>' + esc(display) + '</td><td>' + esc(quality) + '</td></tr>'
        out += '<p class="rule-target">' + esc(atom['target']) + '</p><div class="table-wrap"><table><caption>' + esc(words['performance_values']) + '</caption><thead><tr>' + ''.join('<th scope="col">' + esc(words[k]) + '</th>' for k in ('metric_name', 'metric_value', 'metric_quality')) + '</tr></thead><tbody>' + rows + '</tbody></table></div>'
    return out


def agent_values(atom, words):
    """Format saved diagnostics without reading source documents or reassessing policy."""
    reason = atom.get('reason', '')
    prefix = next((p for p in ('Agent usage governance / gouvernance des usages agents: ',
                              'Agent access evidence / preuves accès agents: ',
                              'Critical content evidence / preuves contenu critique: ') if reason.startswith(p)), None)
    if prefix is None:
        return '<p class="reason">' + esc(reason) + '</p>'
    try:
        diagnostic = json.loads(reason[len(prefix):])
        rows = diagnostic['rows']
        if not isinstance(rows, list):
            raise ValueError('rows')
    except (ValueError, KeyError, TypeError):
        return '<p class="reason">' + esc(reason) + '</p>'
    out = '<div class="table-wrap"><table><caption>' + esc(words['agent_values']) + '</caption><thead><tr>'
    out += ''.join('<th scope="col">' + esc(words[k]) + '</th>' for k in ('agent_subject', 'agent_evidence', 'result', 'reason')) + '</tr></thead><tbody>'
    for row in rows:
        if not isinstance(row, dict):
            continue
        retained = []
        for key in ('actor_kind', 'purposes', 'reviewer', 'review_provenance', 'source_urls', 'source_sha256', 'decisions', 'client', 'test_expectation', 'observed_status', 'body_sha256', 'final_url', 'request_id', 'layer', 'log_record', 'differences', 'clock_skew_ms', 'execution_origin', 'declared_operator_identity', 'claims_operator_visit', 'operator_access'):
            if key in row:
                retained.append('<div><strong>' + esc(key) + '</strong><pre>' + esc(pretty(row[key])) + '</pre></div>')
        if 'effective_choice' in row:
            retained.append('<p><strong>' + esc(words['agent_effective']) + '</strong> · ' + esc(row['effective_choice'] or words['unknown']) + '</p>')
        if row.get('arbitration'):
            retained.append('<p><strong>' + esc(words['agent_tradeoff']) + '</strong></p><pre>' + esc(pretty(row['arbitration'])) + '</pre>')
        out += '<tr><th scope="row">' + esc(row.get('subject', '')) + '</th><td>' + ''.join(retained) + '</td><td>' + esc(words.get(row.get('outcome', ''), words['unknown'])) + '</td><td>' + esc(row.get('reason', '')) + '</td></tr>'
    return out + '</tbody></table></div><details><summary>' + esc(words['agent_raw']) + '</summary><pre>' + esc(reason) + '</pre></details>'


def release_values(atom, words):
    """Render saved process and native outcomes separately, without reevaluation."""
    reason=atom.get('reason','');prefix='Release process / dispositif de déploiement: '
    try:
        if not reason.startswith(prefix):raise ValueError('prefix')
        note=json.loads(reason[len(prefix):]);rows=note['rows']
        if not isinstance(rows,list):raise ValueError('rows')
    except (ValueError,KeyError,TypeError):
        return '<p class="reason">'+esc(reason)+'</p>'
    out='<div class="table-wrap"><table><caption>'+esc(words['release_values'])+'</caption><thead><tr>'
    out+=''.join('<th scope="col">'+esc(words[k])+'</th>' for k in ('release_subject','result','reason'))+'</tr></thead><tbody>'
    for row in rows:
        if isinstance(row,dict):
            out+='<tr><th scope="row">'+esc(row.get('subject',''))+'</th><td>'+esc(words.get(row.get('outcome'),words['unknown']))+'</td><td>'+esc(row.get('reason',''))+'</td></tr>'
    out+='</tbody></table></div>'
    executions=note.get('executions',[])
    native=''
    if isinstance(executions,list):
        for run in executions:
            if not isinstance(run,dict):continue
            for result in run.get('recalculated_results',[]):
                if isinstance(result,dict):
                    native+='<tr><th scope="row">'+esc(str(run.get('run_id',''))+' · '+str(run.get('phase','')))+'</th><td>'+esc(result.get('rule_id',''))+'<br>'+esc(result.get('target',''))+'</td><td>'+esc(words.get(result.get('outcome'),words['unknown']))+'</td></tr>'
    if native:
        out+='<div class="table-wrap"><table><caption>'+esc(words['release_native'])+'</caption><thead><tr>'
        out+=''.join('<th scope="col">'+esc(words[k])+'</th>' for k in ('release_execution','release_subject','result'))+'</tr></thead><tbody>'+native+'</tbody></table></div>'
    return out+'<details><summary>'+esc(words['agent_raw'])+'</summary><pre>'+esc(reason)+'</pre></details>'


def monitoring_values(atom, words):
    prefix='Release monitoring evidence / preuves de suivi: '
    reason=atom.get('reason','')
    if not reason.startswith(prefix):return ''
    try:
        note=json.loads(reason[len(prefix):])
        if not isinstance(note,dict):return ''
    except (ValueError,TypeError):return ''
    out='<h5>'+esc(words['monitoring_title'])+'</h5>'
    for stage in note.get('stages',[]):
        out+='<h6>'+esc(stage.get('id',''))+'</h6>'
        if stage.get('pending'):out+='<p class="notice">'+esc(words['monitoring_pending'])+'</p>'
        if stage.get('window_utc'):out+='<p>'+esc(pretty(stage['window_utc']))+'</p>'
        api=stage.get('api',{});logs=stage.get('logs',{});totals=logs.get('values',{})
        out+='<div class="table-wrap"><table><thead><tr><th scope="col">URL</th><th scope="col">Google (API)</th><th scope="col">'+esc(words['monitoring_requests'])+'</th><th scope="col">'+esc(words['monitoring_errors'])+'</th></tr></thead><tbody>'
        for url in sorted(set(api)|set(totals)):
            row=api.get(url,{});count=totals.get(url,{})
            out+='<tr><th scope="row">'+esc(url)+'</th><td>'+esc(row.get('value',words['unknown']))+'</td><td>'+esc(count.get('requests',words['unknown']))+'</td><td>'+esc(count.get('server_errors',words['unknown']))+'</td></tr>'
        out+='</tbody></table></div>'
        if logs.get('reason'):out+='<p>'+esc(logs['reason'])+'</p>'
        out+='<details><summary>'+esc(words['agent_raw'])+'</summary><pre>'+esc(pretty(stage))+'</pre></details>'
    if note.get('comparisons'):out+='<details><summary>'+esc(words['comparison'])+'</summary><pre>'+esc(pretty(note['comparisons']))+'</pre></details>'
    out+='<div class="table-wrap"><table><thead><tr>'+''.join('<th scope="col">'+esc(words[k])+'</th>' for k in ('release_subject','result','reason'))+'</tr></thead><tbody>'
    for row in note.get('rows',[]):out+='<tr><th scope="row">'+esc(row.get('subject',''))+'</th><td>'+esc(words.get(row.get('outcome'),words['unknown']))+'</td><td>'+esc(row.get('reason',''))+'</td></tr>'
    return out+'</tbody></table></div><details><summary>'+esc(words['agent_raw'])+'</summary><pre>'+esc(pretty(note))+'</pre></details>'


def comparison_values(atom, words):
    prefix = 'Canonical comparison evidence / preuves de comparaison: '
    reason = atom.get('reason', '')
    if not reason.startswith(prefix): return ''
    try:
        note = json.loads(reason[len(prefix):])
        if not isinstance(note, dict): return ''
    except (ValueError, TypeError): return ''
    out = ''
    for member in note.get('members', []):
        out += '<p><strong>'+esc(member.get('url',''))+'</strong></p><p>'+esc(words['comparison_dates'])+': '
        out += esc(member.get('retrieved_at', words['not_supplied']))+' / '+esc(member.get('observed_at',words['not_supplied']))+'</p>'
        out += '<div class="table-wrap"><table><caption>'+esc(words['comparison_values'])+'</caption><thead><tr>'
        out += ''.join('<th scope="col">'+esc(words[k])+'</th>' for k in ('comparison_surface','comparison_state','metric_value'))+'</tr></thead><tbody>'
        for name, fact in member.get('facts',{}).items():
            state = fact.get('state','unknown')
            label = words.get('comparison_'+state, words['unknown'])
            out += '<tr><th scope="row">'+esc(name)+'</th><td>'+esc(label)+'</td><td>'+esc(pretty(fact.get('values',[])))
            if fact.get('reason'): out += '<p>'+esc(fact['reason'])+'</p>'
            out += '</td></tr>'
        out += '</tbody></table></div>'
        if member.get('comparisons'):
            out += '<details><summary>'+esc(words['comparison'])+'</summary><pre>'+esc(pretty(member['comparisons']))+'</pre></details>'
        if member.get('supplied_review'):
            out += '<details><summary>'+esc(words['comparison_values'])+'</summary><pre>'+esc(pretty(member['supplied_review']))+'</pre></details>'
    out += '<div class="table-wrap"><table><thead><tr>'
    out += ''.join('<th scope="col">'+esc(words[k])+'</th>' for k in ('release_subject','result','reason'))+'</tr></thead><tbody>'
    for row in note.get('rows',[]):
        out += '<tr><th scope="row">'+esc(row.get('subject',''))+'</th><td>'+esc(words.get(row.get('outcome'),words['unknown']))+'</td><td>'+esc(row.get('reason',''))+'</td></tr>'
    return out+'</tbody></table></div><details><summary>'+esc(words['agent_raw'])+'</summary><pre>'+esc(pretty(note))+'</pre></details>'


def essential_links_values(atom, words):
    prefix='Supplied essential links / liens essentiels fournis: '
    reason=atom.get('reason','')
    if not reason.startswith(prefix):return ''
    try:
        note=json.loads(reason[len(prefix):]);stage=note['rule_stage'];value=note[stage]
        rows=[dict(id=key,**v) for key,v in value.get('hypotheses',{}).items()] if stage=='source' else value.get('rows',[])
        out='<div class="notice"><strong>'+esc(words['essential_source' if stage=='source' else 'essential_rendered'])+'</strong><p>'+esc(words['essential_state_identity'])+'</p><p>'+esc(words['essential_binding'])+'</p>'
        if value.get('reason'):out+='<p>'+esc(value['reason'])+'</p>'
        out+='</div>'
        for row in rows:
            out+='<div class="notice"><strong>'+esc(words['essential_state'])+' · '+esc(words.get('essential_scripts_'+str(row.get('id')),row.get('id','')) if stage=='source' else row.get('id',''))+'</strong><p>'+esc(words.get(row.get('outcome'),words['unknown']))+'</p>'
            if row.get('reason'):out+='<p>'+esc(row['reason'])+'</p>'
            for key,label in [('found','essential_found'),('missing','essential_missing')]:
                if key in row:out+='<p><strong>'+esc(words[label])+'</strong><br>'+('<br>'.join(esc(x) for x in row[key]) or esc(words['essential_empty']))+'</p>'
            for message in row.get('unknowns',[]):out+='<p>'+esc(message)+'</p>'
            out+='</div>'
        for group in note.get('repeated_snapshots',[]):out+='<div class="notice"><strong>'+esc(words['essential_repeated'])+'</strong><p>'+esc(', '.join(str(x) for x in group['state_ids']))+'</p><code>'+esc(group['snapshot_sha256'])+'</code></div>'
        return '<div class="essential-links-values">'+out+'<details><summary>'+esc(words['essential_details'])+'</summary><pre>'+esc(pretty(note))+'</pre></details></div>'
    except (ValueError,KeyError,TypeError,AttributeError):return ''


def sitemap_files_values(atom, words):
    prefix = 'Supplied sitemap files / fichiers sitemap fournis: '
    rendered = structured_values(atom, dict(words, structured_values=words['sitemap_files_values']), prefix=prefix)
    try:
        note = json.loads(atom.get('reason', '')[len(prefix):])
        summary = '<div class="notice"><strong>' + esc(words['sitemap_files_values']) + '</strong>'
        summary += '<p>' + esc(words['sitemap_roots_note']) + '</p><dl>'
        summary += '<dt>' + esc(words['sitemap_population_count']) + '</dt><dd>' + esc(note.get('declared_document_count', '—')) + '</dd>'
        summary += '<dt>' + esc(words['sitemap_roots']) + '</dt><dd>' + '<br>'.join(esc(u) for u in note.get('declared_roots', [])) + '</dd></dl></div>'
        for url, file in note.get('files', {}).items():
            measurement = {'exact': words['sitemap_exact'], 'lower-bound': words['sitemap_lower_bound']}.get(file.get('byte_measurement'), words['sitemap_unknown'])
            byte_value = file.get('decoded_bytes_read', '—')
            if file.get('byte_measurement') == 'lower-bound':
                byte_value = '≥ ' + str(byte_value)
            values = [('sitemap_bytes', byte_value),
                      ('sitemap_measurement', measurement), ('sitemap_entries', file.get('count') if file.get('count') is not None else words['sitemap_count_unknown']),
                      ('sitemap_observed', file.get('declared_observed_at', '—')),
                      ('sitemap_complete', words['sitemap_yes'] if file.get('xml_complete') is True else words['sitemap_unknown'])]
            summary += '<div class="notice"><strong>' + esc(url) + '</strong><dl>'
            if 'sitemaps-prefix-not-attributed' in file.get('reasons', []):
                summary += '<dt>' + esc(words['sitemap_attribution']) + '</dt><dd>' + esc(words['sitemap_unattributed']) + '</dd>'
            summary += ''.join('<dt>' + esc(words[label]) + '</dt><dd>' + esc(value) + '</dd>' for label, value in values)
            summary += '</dl></div>'
        rendered = summary + rendered
    except (ValueError, TypeError, AttributeError):
        pass
    return '<div class="sitemap-files-values">' + rendered.replace('<div class="table-wrap">', '<div class="table-wrap validation-table" tabindex="0" role="region" aria-label="' + esc(words['sitemap_files_values']) + '">', 1) + '</div>'

def validation_values(atom, words):
    rendered = structured_values(atom, dict(words, structured_values=words['validation_values']),
        prefix='Structured validation evidence / preuves des couches de validation: ')
    try:
        reason = atom.get('reason', '')
        note = json.loads(reason[len('Structured validation evidence / preuves des couches de validation: '):])
        snapshot = note.get('indexed_snapshot')
        if isinstance(snapshot, dict):
            dates = {
                'HTTP capture / capture HTTP': snapshot.get('page_http_received_at'),
                'Supplied DOM / DOM fourni': snapshot.get('page_dom_observed_at'),
                'Indexed last crawl / exploration indexée': snapshot.get('last_crawl_time'),
                'API retrieval / réception API': snapshot.get('retrieved_at'),
                'Cross-snapshot correspondence / correspondance entre instantanés': snapshot.get('correspondence'),
            }
            rendered = '<div class="notice"><strong>Separate snapshots / instantanés séparés</strong><pre>' + esc(pretty(dates)) + '</pre></div>' + rendered
    except (ValueError, TypeError, KeyError):
        pass
    return rendered.replace('<div class="table-wrap">', '<div class="table-wrap validation-table" tabindex="0" role="region" aria-label="' + esc(words['validation_values']) + '">', 1)


def identity_values(atom, words):
    return structured_values(atom,dict(words,structured_values=words['identity_values']),
        prefix='Structured identity evidence / preuves des identités JSON-LD: ')


def structured_values(atom, words, prefix='Structured content evidence / preuves JSON-LD-contenu: '):
    """Display retained TS31 rows; never execute JSON-LD or review code."""
    reason = atom.get('reason','')
    try:
        if not reason.startswith(prefix): raise ValueError('prefix')
        note = json.loads(reason[len(prefix):])
        if not isinstance(note['rows'],list): raise ValueError('rows')
    except (ValueError,KeyError,TypeError): return '<p class="reason">'+esc(reason)+'</p>'
    out = '<div class="table-wrap"><table><caption>'+esc(words['structured_values'])+'</caption><thead><tr>'
    out += ''.join('<th scope="col">'+esc(words[k])+'</th>' for k in ('release_subject','result','reason'))+'</tr></thead><tbody>'
    for row in note['rows']:
        out += '<tr><th scope="row">'+esc(row.get('subject',''))+'</th><td>'+esc(words.get(row.get('outcome'),words['unknown']))+'</td><td>'+esc(row.get('reason',''))+'</td></tr>'
    return out+'</tbody></table></div><details><summary>'+esc(words['agent_raw'])+'</summary><pre>'+esc(pretty(note))+'</pre></details>'


def inspection_values(atom, words):
    prefix = 'Inspection evidence / preuves d’inspection: '
    reason = atom.get('reason', '')
    try:
        if not reason.startswith(prefix):raise ValueError('prefix')
        note = json.loads(reason[len(prefix):])
        if not isinstance(note['rows'], list):raise ValueError('rows')
    except (ValueError, KeyError, TypeError):return '<p class="reason">'+esc(reason)+'</p>'
    out = '<div class="table-wrap"><table><caption>'+esc(words['inspection_values'])+'</caption><thead><tr>'
    out += ''.join('<th scope="col">'+esc(words[k])+'</th>' for k in ('release_subject','result','reason'))+'</tr></thead><tbody>'
    for row in note['rows']:
        out += '<tr><th scope="row">'+esc(row.get('subject',''))+'</th><td>'+esc(words.get(row.get('outcome'),words['unknown']))+'</td><td>'+esc(row.get('reason',''))+'</td></tr>'
    out += '</tbody></table></div><details open><summary>'+esc(words['inspection_values'])+'</summary><pre>'+esc(pretty(note.get('engine_readings',[])))+'</pre></details>'
    return out+'<details><summary>'+esc(words['agent_raw'])+'</summary><pre>'+esc(pretty(note))+'</pre></details>'


def delivery_values(atom, words):
    """Display supplied TS39 diagnostics; never re-run the interpreter."""
    reason=atom.get('reason','');prefix='Delivery evidence / preuves de diffusion: '
    try:
        if not reason.startswith(prefix):raise ValueError('prefix')
        note=json.loads(reason[len(prefix):]);rows=note['rows']
        if not isinstance(rows,list):raise ValueError('rows')
    except (ValueError,KeyError,TypeError):return '<p class="reason">'+esc(reason)+'</p>'
    out='<div class="table-wrap"><table><caption>'+esc(words['delivery_values'])+'</caption><thead><tr>'
    out+=''.join('<th scope="col">'+esc(words[k])+'</th>' for k in ('release_subject','result','reason'))+'</tr></thead><tbody>'
    for row in rows:
        if isinstance(row,dict):
            out+='<tr><th scope="row">'+esc(row.get('subject',''))+'</th><td>'+esc(words.get(row.get('outcome'),words['unknown']))+'</td><td>'+esc(row.get('reason',''))+'</td></tr>'
    out+='</tbody></table></div>'
    native=note.get('native_results',[])
    if isinstance(native,list) and native:
        out+='<details><summary>'+esc(words['delivery_native'])+'</summary><pre>'+esc(pretty(native))+'</pre></details>'
    return out+'<details><summary>'+esc(words['agent_raw'])+'</summary><pre>'+esc(reason)+'</pre></details>'


def results(bundle, controls, words, language):
    report = bundle['report']
    data = captures(bundle)
    targets = {t['url']: t for t in data['targets'] if isinstance(t, dict) and isinstance(t.get('url'), str)} if data else {}
    out = '<section id="results"><div class="section-head"><h2>' + esc(words['results']) + '</h2></div>'
    for result in report['results']:
        cid = result['control_id']
        control = controls[cid]
        rules = {r['id']: r for r in control.get('rules', [])}
        out += '<article class="card control"><div class="row"><div><span class="eyebrow">' + esc(cid) + '</span><h3 class="control-title">' + esc(control['title'][language]) + '</h3></div>' + badge(result['status'], words) + '</div>'
        if cid in ('TS34', 'TS35'):
            out += performance_values(result, words)
        if cid == 'TS36':
            out += '<div class="notice">' + esc(words['monitoring_note']) + '</div>'
        if cid == 'TS17':
            out += '<div class="notice">' + esc(words['essential_links_note']) + '</div>'
        if cid == 'TS15':
            out += '<div class="notice">' + esc(words['sitemap_files_note']) + '</div>'
        if cid == 'TS33':
            out += '<div class="notice">' + esc(words['validation_note']) + '</div>'
        if cid == 'TS32':
            out += '<div class="notice">' + esc(words['identity_note']) + '</div>'
        if cid == 'TS31':
            out += '<div class="notice">' + esc(words['structured_note']) + '</div>'
        if cid == 'TS12':
            out += '<div class="notice">' + esc(words['comparison_note']) + '</div>'
        if cid == 'TS08':
            out += '<div class="notice">' + esc(words['inspection_note']) + '</div>'
        if cid == 'TS39':
            out += '<div class="notice"><strong>' + esc(words['delivery_note']) + '</strong></div>'
        if cid == 'TS41':
            out += '<div class="notice"><strong>' + esc(words['release_note']) + '</strong></div>'
        if cid == 'TS42':
            out += '<div class="notice"><strong>' + esc(words['agent_note']) + '</strong></div>'
        if cid == 'TS44':
            out += '<div class="notice"><strong>' + esc(words['critical_content_note']) + '</strong></div>'
        if cid == 'TS43':
            out += '<div class="notice"><strong>' + esc(words['agent_access_note']) + '</strong></div>'
        out += '<p class="reason">' + esc(result['reason']) + '</p><details><summary>' + esc(words['procedure']) + '</summary><p class="small">' + esc(result['procedure']) + '</p>' + proof_links(result['evidence_ids'], 'current') + '</details>'
        seen = set()
        for atom in result.get('atomic_results', []):
            rule = rules[atom['rule_id']]
            seen.add((atom['rule_id'], atom['target']))
            out += '<div class="rule"><div class="row"><h4><code>' + esc(atom['rule_id']) + '</code> · ' + esc(rule['title'][language]) + '</h4>' + badge(atom['outcome'], words) + '</div>'
            out += '<p class="rule-target">' + esc(atom['target']) + '</p>'
            out += (essential_links_values(atom, words) if cid == 'TS17' else sitemap_files_values(atom, words) if cid == 'TS15' else validation_values(atom, words) if cid == 'TS33' else identity_values(atom, words) if cid == 'TS32' else structured_values(atom, words) if cid == 'TS31' else monitoring_values(atom, words) if cid == 'TS36' else comparison_values(atom, words) if cid == 'TS12' else inspection_values(atom, words) if cid == 'TS08' else delivery_values(atom, words) if cid == 'TS39' else release_values(atom, words) if cid == 'TS41' else
                    agent_values(atom, words) if cid in ('TS42', 'TS43', 'TS44') else '<p class="reason">' + esc(atom['reason']) + '</p>')
            out += proof_links(atom['evidence_ids'], 'current')
            if atom['rule_id'].startswith('TS01-'):
                out += identity_context(targets.get(atom['target']), words)
            out += '<details><summary>' + esc(words['expectation']) + '</summary><dl>' + item(words['expectation'], rule['acceptance'][language]) + item(words['automation'], rule['automation']) + item(words['inputs'], ', '.join(rule['required_inputs'])) + item(words['limits'], rule['limitations'][language]) + '</dl></details></div>'
        missing = [(rid, target) for rid in rules for target in report['scope']['targets'] if (rid, target) not in seen]
        if missing:
            out += '<details class="notice"><summary>' + esc(words['unobserved']) + ' (' + str(len(missing)) + ')</summary><p>' + esc(words['unobserved_note']) + '</p><ul>' + ''.join('<li><code>' + esc(rid) + '</code> · ' + esc(target) + '</li>' for rid, target in missing) + '</ul></details>'
        out += '</article>'
    return out + '</section>'


def capture_view(bundle, words):
    data = captures(bundle)
    out = '<section id="captures"><div class="section-head"><h2>' + esc(words['captures']) + '</h2></div><p class="muted small">' + esc(words['capture_note']) + '</p>'
    if data is None:
        return out + '<p class="empty">' + esc(words['no_capture']) + '</p></section>'
    for target in data['targets']:
        if not isinstance(target, dict):
            continue
        out += '<article class="card target-card"><h3>' + esc(target.get('url', words['not_supplied'])) + '</h3>'
        intent = target.get('intent', {})
        if isinstance(intent, dict):
            fields = [('declared', 'declared_at'), ('expected_url', 'expected_final_url'),
                      ('expected_hash', 'expected_body_sha256'), ('representation', 'representation')]
            out += '<details><summary>' + esc(words['intent']) + '</summary><dl class="context">'
            out += ''.join('<div>' + item(words[label], intent.get(key, words['not_supplied']), key == 'expected_body_sha256') + '</div>' for label, key in fields)
            out += '</dl><pre>' + esc(pretty(intent)) + '</pre></details>'
        out += '<p class="small muted">' + esc(words['observed']) + ' · ' + esc(target.get('observed_at', words['not_supplied'])) + '</p>'
        hops = target.get('http', [])
        if isinstance(hops, list) and hops:
            out += '<p class="eyebrow">' + esc(words['chain']) + '</p><ol class="chain">'
            for hop in hops:
                if not isinstance(hop, dict):
                    continue
                response = hop.get('response', '')
                if isinstance(response, dict):
                    try:
                        response = raw_bytes(response).split(b'\r\n', 1)[0].decode('latin-1')
                    except ValueError:
                        response = words['not_supplied']
                out += '<li><span class="hop-status mono">' + esc(response.split('\r\n', 1)[0] if isinstance(response, str) else words['not_supplied']) + '</span><p>' + esc(hop.get('url', '')) + '</p>'
                for key, label in [('request', 'raw_request'), ('response', 'raw_response')]:
                    if isinstance(hop.get(key), str):
                        out += '<details><summary>' + esc(words[label]) + '</summary><pre>' + esc(hop[key]) + '</pre></details>'
                    elif isinstance(hop.get(key), dict):
                        out += '<details><summary>' + esc(words[label]) + '</summary>'
                        try:
                            raw = raw_bytes(hop[key])
                            out += '<p class="hash">SHA-256 · ' + esc(hashlib.sha256(raw).hexdigest()) + '</p>'
                            out += download(raw, words['download'], key+'-'+hashlib.sha256(raw).hexdigest()[:12]+'.bin')
                            out += '<pre>' + esc(raw.split(b'\r\n\r\n', 1)[0].decode('latin-1')) + '</pre>'
                            out += '<p class="small muted">' + esc(words['binary']) + '</p>'
                        except ValueError:
                            out += '<pre>' + esc(pretty(hop[key])) + '</pre>'
                        out += '</details>'
                out += '</li>'
            out += '</ol>'
        out += '<details><summary>' + esc(words['request_context']) + '</summary><pre>' + esc(pretty(target.get('context', {}))) + '</pre></details></article>'
    return out + '</section>'


def evidence_view(bundle, words, prefix):
    out = ''
    for artifact in bundle['report']['artifacts']:
        raw = bundle['files'][artifact['id']]
        out += '<details class="evidence" id="' + prefix + '-evidence-' + esc(artifact['id']) + '"><summary>' + esc(artifact['id']) + ' <span class="badge neutral">' + esc(artifact['kind']) + '</span><span class="path">' + esc(artifact['path']) + '</span></summary>'
        out += '<dl class="context"><div>' + item(words['description'], artifact['description']) + item(words['targets'], ', '.join(artifact['targets'])) + '</div><div>' + item('SHA-256', artifact['sha256'], True) + item(words['observed'], artifact['observed_at']) + item(words['access'], artifact['access']) + '</div></dl>'
        out += download(raw, words['download'], prefix + '-' + artifact['id'] + '.bin')
        try:
            text = raw.decode('utf-8')
            # NULs in valid UTF-8 may still indicate a binary file.
            if '\x00' in text:
                raise ValueError('binary')
            out += '<details><summary>' + esc(words['preview']) + '</summary><pre>' + esc(text) + '</pre></details>'
        except (UnicodeDecodeError, ValueError):
            out += '<p class="small muted">' + esc(words['binary']) + '</p>'
        out += '</details>'
    return out


def render(report_path, *, evidence_root=None, language='en', compare=None, compare_root=None):
    tsep.require(language in TEXT, 'Unknown HTML language')
    words = TEXT[language]
    current = load(report_path, evidence_root)
    previous = load(compare, compare_root) if compare is not None else None
    report, summary = current['report'], current['summary']
    protocol = tsep.read_json(tsep.PROTOCOL_PATH)
    controls = {c['id']: c for c in protocol['controls']}
    css = (ROOT/'report.css').read_text(encoding='utf-8')
    css_hash = base64.b64encode(hashlib.sha256(css.encode()).digest()).decode('ascii')
    csp = "default-src 'none'; style-src 'sha256-" + css_hash + "'; base-uri 'none'; form-action 'none'"
    out = '<!doctype html><html lang="' + language + '"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="' + esc(csp) + '"><meta name="referrer" content="no-referrer"><title>TSEP · ' + esc(words['title']) + ' · ' + esc(report['scope']['label']) + '</title><style>' + css + '</style></head><body>'
    out += '<a class="skip" href="#main">' + esc(words['skip']) + '</a><header class="top"><div class="wrap masthead"><div class="brand">TSEP<span class="muted"> /</span></div><div class="small muted">' + esc(words['offline']) + '</div></div><div class="wrap hero"><p class="eyebrow">' + esc(words['title']) + '</p><h1>' + esc(words['subtitle']) + '</h1><p class="scope-label">' + esc(report['scope']['label']) + '</p><div class="hero-foot"><span class="pill">' + esc(report['protocol']['version']) + '</span><span class="pill">' + esc(words['draft']) + '</span><span class="small muted">' + esc(report['issued_at']) + '</span></div></div></header>'
    sections = ['overview'] + (['comparison'] if previous else []) + ['results', 'captures', 'evidence', 'method']
    out += '<nav class="nav" aria-label="' + esc(words['title']) + '"><div class="wrap">' + ''.join('<a href="#' + s + '">' + esc(words[s]) + '</a>' for s in sections) + '</div></nav><main id="main" class="wrap">'
    state = 'negative' if summary['counts']['NC'] else ('unknown' if summary['counts']['NT'] else '')
    out += '<section id="overview"><div class="metrics"><div class="card decision-card ' + state + '"><span class="eyebrow">' + esc(words['decision']) + '</span><p class="metric code mono">' + esc(summary['decision']) + '</p><p>' + esc(words[summary['decision']]) + '</p><p class="small"><strong>' + esc(', '.join(report['controls'])) + ' · ' + str(len(report['scope']['targets'])) + ' ' + esc(words['targets'].lower()) + '</strong></p><p class="small muted">' + esc(words['scope_only']) + '</p></div>'
    out += '<div class="card"><span class="eyebrow">' + esc(words['controls']) + '</span><p class="metric">' + str(summary['selected_controls']) + ' <span class="muted">/ ' + str(summary['protocol_controls']) + '</span></p><p class="small muted">' + str(len(summary['unevaluated_controls'])) + ' ' + esc(words['not_evaluated']) + '</p></div>'
    out += '<div class="card"><span class="eyebrow">' + esc(words['targets']) + '</span><p class="metric">' + str(len(report['scope']['targets'])) + '</p><p class="small muted">' + str(len(report['artifacts'])) + ' ' + esc(words['artifact_count']) + '</p></div></div>'
    out += '<div class="notice"><strong>' + esc(words['valid']) + '</strong>' + esc(words['integrity_limit']) + '</div>'
    for result in report['results']:
        if result['control_id'] in ('TS34', 'TS35'):
            out += '<div class="card"><h3>' + esc(result['control_id']) + ' · ' + esc(words['performance_values']) + '</h3>' + performance_values(result, words) + '</div>'
    out += '<p class="small muted">' + esc(words['run_selection']) + '</p>'
    for access, label in [('synthetic', 'synthetic'), ('restricted', 'restricted')]:
        if any(a['access'] == access for bundle in (current, previous) if bundle
               for a in bundle['report']['artifacts']):
            out += '<div class="notice synthetic"><strong>' + esc(words[label]) + '</strong>' + esc(words[label + '_note']) + '</div>'
    out += '</section>'
    metadata = current['files'].get('import-record')
    if metadata:
        try:
            inventory = tsep.parse_json(metadata).get('coverage_inventory', [])
            if isinstance(inventory, list) and inventory:
                out += '<section class="card"><h2>' + esc(words['coverage_inventory']) + '</h2><ul>'
                for entry in inventory:
                    if isinstance(entry, dict) and entry.get('state') in ('implemented', 'deferred', 'out-of-scope'):
                        out += '<li><strong>' + esc(words[entry['state']]) + '</strong> · ' + esc(entry.get(language, '')) + '</li>'
                out += '</ul></section>'
        except (ValueError, AttributeError):
            pass
    if previous:
        out += comparison(current, previous, words)
    out += results(current, controls, words, language) + capture_view(current, words)
    out += '<section id="evidence"><div class="section-head"><h2>' + esc(words['evidence']) + '</h2></div><p class="muted small">' + esc(words['all_evidence']) + '</p><div class="card">' + evidence_view(current, words, 'current') + '</div>'
    if previous:
        out += '<details class="card"><summary>' + esc(words['before']) + ' · ' + esc(words['evidence']) + '</summary>' + evidence_view(previous, words, 'previous') + '</details>'
    out += '</section><section id="method"><div class="section-head"><h2>' + esc(words['method']) + '</h2></div><div class="card meta-grid"><div><h3>' + esc(words['selection']) + '</h3><p class="small">' + esc(report['scope']['selection_method']) + '</p><dl>' + item(words['profile'], report['profile']) + item(words['exclusions'], '; '.join(report['scope']['exclusions']) or words['none']) + '</dl></div>'
    out += '<div><h3>' + esc(words['assessor']) + '</h3><dl>' + item(words['assessor'], report['assessor']['name']) + item(words['mode'], report['assessor']['mode']) + item(words['controls'], ', '.join(report['controls'])) + '</dl></div>'
    out += '<div><h3>' + esc(words['identity']) + '</h3>' + report_identity(current, words, 'current') + '</div></div></section></main>'
    out += '<footer class="footer"><div class="wrap"><p>' + esc(words['footer']) + ' ' + VERSION + ' · ' + esc(words['read_only']) + '</p><p class="hash">' + esc(words['protocol']) + ' SHA-256 · ' + esc(report['protocol']['sha256']) + '</p></div></footer></body></html>\n'
    return out


def write(report_path, output, **options):
    """Validate everything before creating a new output; never replace a file."""
    output = Path(output)
    tsep.require(not output.exists() and not output.is_symlink(), 'HTML output already exists; choose a new file')
    document = render(report_path, **options)
    handle = output.open('x', encoding='utf-8', newline='\n')
    try:
        with handle:
            handle.write(document)
    except OSError:
        output.unlink()
        raise
    return {'html': str(output), 'sha256': tsep.digest(output), 'renderer_version': VERSION}
