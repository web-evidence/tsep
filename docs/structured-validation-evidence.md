# TS33 — structured validation layers / couches de validation

Normative profile `jsonld-validation-layers-v1`, draft.34. Interpreter33,
adapter34, HTML18; replay3 unchanged. Fifty-two prefrozen synthetic cases,
156 rule/target pairs. Execution evidence is recorded separately.

## Français

Le profil porte sur une page sélectionnée, ses captures HTTP/DOM fournies et un
instantané indexé Google séparé. Une erreur bloquante constatée reste NC même
documentée. C ne garantit ni validité Schema.org complète, ni éligibilité actuelle,
ni affichage, ni indexation. Les 44 identifiants et leur provenance sont conservés.

L’entrée reprend exactement `jsonld`, `structured_synthetic`, le contexte et
`intent.structured_content` du [lecteur TS31](structured-content-evidence.md).
TS33 recalcule la sélection des scripts et les graphes depuis ces captures avec
les lecteurs natifs épinglés ; aucun résultat TS31 ni extrait libre n’est cru.
Il ne juge pas la visibilité ni la véracité des contenus. Départ/final/URL cible
identiques ; fenêtre de capture de 24 heures au plus. La source est lue avec et
sans scripting et tous les états DOM prévus sont nécessaires. Origine et dates
restent déclarées, non authentifiées.

`intent.structured_validation` exige reader, vocabulary=`schemaorg-all-30.1`,
source=`ts31-bound-surfaces`, engine=`google-url-inspection-v1`,
relationship=`separate-indexed-snapshot`, site_url, 1–16 features distinctes
et une guidance par fonction (feature, URL, raw_text, SHA-256, observed_at).
La documentation précède le plan. Les sources fictives ne servent qu’aux essais.

A01 vérifie le périmètre et la revue préalable `validation_plan_review`, liée à
`{url,intent,plan:jsonld.plan}` par SHA-256 du JSON UTF-8 canonique (clés triées,
séparateurs compacts, Unicode non échappé). Les jugements scope/support/separation
sont supported, contradiction ou inconnus. Une contradiction de prise en charge
documentée donne fail ; une fonction absente des résultats Google ne prouve pas
qu’elle n’est pas prise en charge. La lecture sémantique des documents reste une
revue fournie ; aucun jugement humain n’est produit automatiquement.

A02 recalcule les surfaces liées et compare les IRI de classes/propriétés au
fichier complet Schema.org30.1 épinglé. http://schema.org/ et https://schema.org/
sont équivalents pour cette seule comparaison. Cœur, extensions, pending et
termes historiques sont inclus ; isPartOf/supersededBy restent affichés, sans
échec automatique. Terme absent ou rôle classe/propriété contradictoire : fail.
Vocabulaire étranger, contexte manquant, graphe nommé/vide, absence de classe,
notice non résolue ou runtime manquant : inconclusive. Une syntaxe JSON invalide
attribuée donne fail ; les clés dupliquées restent ambiguës. Pas de vérification
des domaines, plages de valeurs, adéquation sémantique, RDFa ou Microdata.
Maximum 256 termes distincts par surface. Pas de collecte réseau ni repli.

A03 lit `validation_record` : provenance synthetic-exercise ou supplied-google-api,
description, tool=`google-url-inspection`, api_version=`v1`,
backend_version=`not-exposed`, complete=true, http_status=200, retrieved_at,
request/response `{raw_text,sha256}`. Chaque corps natif est limité à512Kio,
JSON strict sans doublons. La requête doit contenir la même inspectionUrl/siteUrl
et languageCode=en-US. Réception dans la fenêtre ; lastCrawlTime présent et
antérieur ou égal à réception. Cette date n’est pas celle de tous les champs.
L’API concerne la version indexée, jamais un test live ni le Rich Results Test.
Les octets JSON-LD actuels ne sont jamais attribués au résultat Google.

Le lecteur conserve verdict, tous les groupes detectedItems, items et issues.
ERROR ou FAIL donne fail ; WARNING exige qualification distincte. Verdict réservé,
criticité/champ inconnu, sortie absente/incomplète, API en erreur ou fonction
prévue non détectée : inconclusive, sans masquer un ERROR indépendant déjà lu.
Les listes proto omises d’issues signifient zéro message dans cet objet, jamais
zéro erreur de syntaxe sur la page : les éléments non analysables peuvent manquer.
Bornes :64groupes,64items/groupe,128issues/item,256items et256messages au total.

`validation_review` reprend les champs de revue TS08 : provenance, reviewer,
assistance, reason, complete, observed_at et binding_sha256, lié ici à
`{url,intent,record:validation_record}`. Elle suit la réception et précède la fin
d’évaluation. interpretation vaut supported/contradiction. messages couvre
exactement chaque chemin `detectedItems/G/items/I/issues/J`, sa severity,
message_sha256 (UTF-8 exact), une decision accepted/correction-planned/contradiction
et une raison. Une revue complète qui omet, invente, duplique ou rétrograde un
message donne fail ; une revue absente/incomplète reste inconnue. Aucun choix de
revue n’annule ERROR. Les originaux et les trois couches restent séparés.

Le dossier réel API doit être restricted ; les exercices doivent être synthetic.
Pas de NA dans ce profil. C exige les trois règles pass sur tout le périmètre
fourni. Un sous-ensemble de règles ne suffit pas. NC exige une contradiction,
sinon NT. Code sans captures liées : NT. Une panne technique ne devient pas NC.
L’import hors application reste `adapters/captures.py`; le rejeu conserve les
octets et exige le même moteur et Node24 explicite via TSEP_SOURCE_NODE.

## English

This profile assesses one selected page's supplied HTTP/DOM captures and a
separate Google indexed snapshot. A blocking error stays fail even when documented.
C does not mean complete Schema.org validity, current eligibility, display or
indexing. The 44 control IDs and provenance remain unchanged.

Input uses the exact TS31 jsonld/structured_synthetic/context and
intent.structured_content grammar. TS33 recomputes scripts and graphs with pinned
native readers, accepting neither a previous TS31 verdict nor an unbound snippet.
Start/final/target URLs must match, capture window <=24hours, both source scripting
modes and all planned rendered states are required. No visibility or factual
judgment; supplied origin and timestamps are not authenticated.

intent.structured_validation requires the exact constants and fields specified
above, 1–16 distinct intended Google features and one fingerprinted, dated guidance
capture per feature, available before the plan. A01 checks scope/support/separation
in a supplied prior review, bound to canonical `{url,intent,plan:jsonld.plan}`.
Canonical JSON uses sorted keys, compact separators and unescaped UTF-8 Unicode.
Documented unsupported intended use fails; absence from Google results is not
unsupported-use evidence. Semantic interpretation of guidance is supplied review,
never an automatically invented human judgment.

A02 reprocesses bound surfaces and checks class/property names against pinned
Schema.org30.1 all sections, including historical terms. HTTP/HTTPS namespace
equivalence applies only to this lookup. Core, extensions, pending and historical
terms are included; isPartOf/supersededBy are retained without automatic failure.
Missing names or a contradictory class/property role fail. Foreign vocabulary,
missing context, named/empty graph, absent class, unresolved notice or unavailable
runtime are inconclusive. Attributed invalid JSON syntax fails; duplicate keys
remain ambiguous. No domain/range/value, semantic suitability, RDFa or Microdata
validation. At most256 distinct terms/surface; no network or fallback.

A03 consumes the original bounded strict API JSON request/response and metadata
listed above, matching URL/property and en-US language, capture window and known
last crawl <=retrieval. APIv1 identifies the documented format; backend version is
explicitly unavailable. Only an indexed snapshot is read, never live/RRT output
or proof that Google inspected the supplied page bytes. lastCrawlTime does not
timestamp every field. All native messages are inventoried: ERROR/FAIL fails even
with no review; WARNING needs an exact-message qualification. Unknown severities,
reserved verdicts, unknown rich-result fields, unsuccessful/incomplete outputs or
missing intended features are inconclusive without hiding independent known errors.
Omitted proto issue arrays mean no messages in that item, not no page syntax errors.
Unparseable rich results may be absent. The explicit bounds above apply.

validation_review follows TS08 supplied-review identity/provenance/completeness
and chronology rules, binding `{url,intent,record:validation_record}`. Its complete
messages array must match every native path, severity and UTF-8 message digest;
each carries a reason and accepted/correction-planned/contradiction decision.
Omission, duplication, invention or downgrade fails. Absent/incomplete review is
unknown. interpretation is supported/contradiction; no decision cancels ERROR.
Originals and layer outcomes stay separate. Real API evidence is restricted;
authored cases are synthetic. No NA, no complete-control C from partial rules.
Known contradictions yield NC; otherwise missing evidence yields NT. A technical
failure is not itself NC. Standalone capture import/replay retains original bytes
and needs the exact engine plus explicit Node24/TSEP_SOURCE_NODE.

## Sources and reproducibility / Sources et reproductibilité

Official dated captures and hashes: [provenance](../research/structured-validation-2026-10-14/provenance.json).
Schema.org data has its own [license/attribution](../third_party/schemaorg/NOTICE.txt).
API field meanings: [official reference](https://developers.google.com/webmaster-tools/v1/urlInspection.index/UrlInspectionResult).
Indexed-only boundary: [method](https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect).
The editorial TSEP profile is not endorsed by these sources. No real Google test,
remote CI or independent human review is established by the synthetic corpus.

## Snapshot separation / Séparation des instantanés

FR : les dates HTTP, DOM fournis, exploration indexée et réception API sont affichées séparément. Leur correspondance demeure `not-established`, même si les trois qualifications passent. Le profil ne compare pas les fonctions natives Google aux types Schema.org ; la présence de noms connus à la capture ne prouve pas une fonction prise en charge dans cette capture. EN: supplied HTTP/DOM dates, indexed crawl and API retrieval are displayed separately. Their correspondence remains `not-established` even when all three qualifications pass. This profile does not compare native Google features with Schema.org types; known captured names do not establish a supported feature in that capture.

### Intake without a plan / Import sans plan

FR : la restriction d’accès de la réponse API et les étiquettes de provenance
s’appliquent dès qu’une réponse ou une revue TS33 est fournie, même si le plan
manque. Une étiquette synthétique ne devient pas publique/restreinte ni humaine
par omission du plan. Ces contradictions d’import sont refusées techniquement.
Un dossier synthétique intact sans plan reste NT, avec ses originaux et son
étiquette synthétique conservés ; aucune approbation ni NC n’est fabriqué.

EN: API access restrictions and provenance labels apply whenever a TS33 response
or review is supplied, even without a plan. Omitting the plan cannot relabel
synthetic material as public/restricted or human. Such intake contradictions are
technically refused. An intact synthetic dossier without its plan stays NT,
retaining its original bytes and synthetic label; no approval or NC is fabricated.

FR : le même contrôle de provenance couvre aussi l’unique niveau d’entrées JSON
natives TS41 que l’adaptateur inspecte déjà (borne512Kio, au plus64 exécutions).
L’enveloppe ne transforme pas ses pièces synthétiques en données publiques.
EN: The same provenance check covers the single native TS41 JSON-input level
already inspected by the adapter (512KiB bound, at most64 runs). Wrapping does
not relabel its synthetic records as public data. Recursive inputs remain unsupported.

FR : les drapeaux de provenance explicites déjà reconnus par l’adaptateur restent
vérifiés même sans plan ni pièce reconnue. Une valeur non booléenne ou incompatible
avec l’accès est refusée. Cela vérifie une cohérence déclarative, pas l’authenticité.
Une origine inconnue n’est pas renommée automatiquement synthétique ou réelle.
EN: Existing explicit provenance flags are checked even without a plan or a
recognized record. Nonboolean values or access conflicts are refused. This checks
declared consistency, not authenticity. Unknown origin is not automatically
renamed synthetic or real.
