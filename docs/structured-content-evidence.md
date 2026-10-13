# TS31 — supplied JSON-LD/content evidence v1 / preuves JSON-LD-contenu fournies v1

Contract frozen before implementation, 2026-10-13. Candidate draft.32; no published
standard, certification, Schema.org validation or Google eligibility claim.

## Français

Ce premier profil semiAuto qualifie une page explicitement sélectionnée, les deux
hypothèses statiques de sa source HTML et 1–16 états DOM fournis prévus avant la
capture. Il utilise les lecteurs facultatifs JSON-LD existants sans modifier leurs
algorithmes. Aucun navigateur ni compte Google n'est ouvert par l'interpréteur.
Le profil porte sur le JSON-LD ordinaire exact `application/ld+json`. Microdata,
RDFa, documents de frames, shadow et templates ne sont pas qualifiés par ce profil.
Une revue préalable doit confirmer que cette sélection couvre le JSON-LD pertinent
du périmètre déclaré. Un périmètre non couvert reste NT ; un sous-ensemble ne devient
pas conforme à l'ensemble du site. L'absence de script ne produit jamais NA.

### Entrées et chronologie

La cible fournit `structured_synthetic` booléen, `context` (network, bounds, tool,
tool_version), `observed_at`, `intent` et `jsonld`. Ce dernier est exactement la
requête du [lecteur source/rendu](jsonld-rendered-observation.md) : plan préalable,
HTTP natif complet, date HTTP, contextes distants fournis et états DOM attribués.
Les acquisitions synthétiques restent explicitement synthétiques.

`intent.structured_content` contient reader=`jsonld-visible-content-v1`,
selection_reason et population non vides, important_properties=`all-supplied`, et
1–16 `guidance` : chacune contient url HTTP(S), observed_at, raw_text UTF-8 et son
sha256. Il s'agit de références fournies, non authentifiées. Chaque texte est borné
à 512 Kio. La date d'intention égale celle du plan JSON-LD ; la fenêtre est au plus
24 h, se termine avant l'évaluation et les références sont acquises avant le plan.
L'URL cible est l'URL de départ ; le client et l'URL finale restent ceux du plan.

### A01 — périmètre et hypothèses revus avant acquisition

`structured_plan_review` est liée à `{url,intent,plan:jsonld.plan}`. Son horodatage
est entre la déclaration et le début de fenêtre. Les qualifications `scope`,
`source_base`, `guidance` valent supported, contradiction ou unknown. Elles portent
sur la population/les scénarios, les exclusions, la base source explicitement
fournie, les types et recommandations sélectionnés, et toutes les propriétés
importantes (aucune sélection opportuniste après résultat). Une contradiction
liée donne fail ; une revue absente/incomplète/inconnue donne inconclusive.

Toutes les revues exigent complete=true, reviewer, assistance, reason, observed_at,
provenance human/human-assisted/synthetic-exercise cohérente avec la cible, et
binding_sha256 exact. Ni l'auteur, ni les dates, ni la vérité ne sont authentifiés.

### A02 — lecture native complète dans le profil

Le lecteur recalcule source et DOM, rassemble les scripts de chaque représentation
avant expansion/aplatissement JSON-LD 1.1 avec jsonld.js 9.0.0 hors ligne et Node 24
explicitement fourni. Il conserve scripts, contextes, notices, bases, empreintes,
limites et erreurs. Aucun graphe précalculé fourni n'est accepté comme résultat.
JSON syntaxiquement invalide dans un script sélectionné et attribué donne fail.
Les clés JSON répétées restent ambiguës et inconclusives, sans accusation de syntaxe invalide. Une récupération
HTML ambiguë, une variante MIME non qualifiée, une limite, un contexte absent,
une erreur du processeur ou un runtime absent donne inconclusive, pas un défaut
de contenu. Une surface sans script peut être documentée, mais au moins une surface
doit livrer un graphe non vide ; les graphes vides et notices non résolues restent NT.
Des états manquants/dupliqués/imprévus restent inconnus. Une contradiction native
indépendante demeure fail même avec un autre état manquant. La différence entre
source et rendu n'est pas, seule, une contradiction sémantique.

### A03 — revue du contenu liée à chaque graphe

`structured_reviews` contient une entrée par surface à graphe non vide :
surface_id=`source:enabled`, `source:disabled`, ou `render:<id>`. Chaque entrée
contient `content`, `review` et `entities`. `content` contient kind=
`supplied-visible-content-transcript`, raw_text, sha256, observed_at et method non
vide ; c'est une pièce de contenu visible fournie, pas une visibilité calculée à
partir du DOM. Sa date suit la surface et reste dans la fenêtre. La revue suit
cette pièce et précède l'évaluation. La liaison vaut le digest canonique de
`{url,intent,plan,http,http_received_at,contexts,surface_id,state,content,graph}`,
où state vaut null pour la source, l'état natif exact pour le rendu ; graph est
le tableau flattened recalculé. Une modification de pièce invalide la revue.

`review.coverage` qualifie la complétude des scripts, entités et propriétés,
y compris des termes ignorés par expansion. `entities` contient exactement chaque
nœud aplati, avec index, node_sha256 et trois qualifications : visible_consistency,
type_suitability, no_fabrication. Chaque qualification exige reason et vaut
supported/contradiction/unknown. La revue concerne toutes les propriétés du nœud,
y compris les objets imbriqués ; elle ne prétend pas rendre les identifiants
littéralement visibles. Limite : 256 nœuds par surface. Un nœud manquant, ajouté,
répété ou modifié empêche un pass ; les contradictions des nœuds correctement liés
restent conservées. Chaque surface est traitée indépendamment.

Les trois règles sont nécessaires au C documentaire de la page sélectionnée.
Une revue fournie contradictoire vaut fail ; un champ inconnu reste inconclusive.
Aucune revue n'est automatiquement remplie ni présentée comme jugement humain
observé dans un cas synthétique. Un traitement JSON-LD réussi n'est ni une validation
de vocabulaire, ni une preuve indépendante des faits visibles, ni un résultat enrichi.

## English

This first semiAuto profile covers one explicitly selected page, both static source
hypotheses and 1–16 supplied DOM states planned before acquisition. It consumes the
existing optional JSON-LD readers without changing them. It opens no browser or
Google account. Only ordinary exact `application/ld+json` is qualified. Microdata,
RDFa, frame documents, shadow and templates remain outside this profile. A prior
review must qualify coverage of relevant JSON-LD in the declared scope; uncovered
scope stays inconclusive. No site-wide conclusion or automatic NA follows.

The target supplies a boolean `structured_synthetic`, context (network, bounds,
tool, tool_version), assessment observed_at, intent and jsonld. The latter is the
exact existing source/rendered request: prior plan, complete native HTTP, HTTP date,
supplied remote contexts and attributed DOM states. Synthetic acquisitions stay
synthetic. `intent.structured_content` declares reader=`jsonld-visible-content-v1`,
selection_reason, population, important_properties=`all-supplied`, and 1–16 supplied
guidance records (HTTP(S) url, observed_at, raw_text, sha256). Texts are bounded at
512 KiB. Intent and JSON-LD plan dates match, guidance predates the plan, the window
is at most 24 hours and ends by assessment. Target URL equals the planned start URL.

A01 qualifies `structured_plan_review`, bound to `{url,intent,plan:jsonld.plan}`,
between declaration and window start. Its scope, source_base and guidance judgments
cover population/scenarios/exclusions, the explicit source base, selected type
guidance and all important properties without post-result selection. Each judgment
is supported, contradiction or unknown. Bound contradiction fails; missing,
incomplete or unknown qualification is inconclusive. All reviews require complete,
reviewer, assistance, reason, observed_at, exact binding_sha256 and consistent
human/human-assisted/synthetic-exercise provenance. Identity, dates and truth are
supplied, never authenticated by hashes.

A02 recomputes each native source/DOM representation, combines selected scripts
before JSON-LD 1.1 expansion/flattening with pinned offline jsonld.js 9.0.0 and
explicit Node 24, and retains scripts, contexts, notices, bases, fingerprints and
errors. Syntactically invalid JSON in an attributed selected script fails. Duplicate
JSON keys remain ambiguous/inconclusive, not a syntax-failure claim. Ambiguous HTML
recovery, unqualified MIME variants, bounds, missing contexts, processor/runtime
failure remain inconclusive. An absent surface can be documented, but at least one
surface must produce a nonempty graph; empty graphs or unresolved notices cannot
pass. Missing/duplicate/unplanned states remain unknown. Independent known JSON
contradictions survive unrelated missing states. Source/rendered differences alone
do not prove semantic contradiction. Supplied precomputed results are not trusted.

A03 uses `structured_reviews`, one record per nonempty graph surface, named
`source:enabled`, `source:disabled` or `render:<id>`. Each record has content, review
and entities. Content contains kind=`supplied-visible-content-transcript`, raw_text,
sha256, observed_at, and method. It is supplied visibility evidence, not inferred
CSS visibility. Its date follows the surface within the window; review follows it
by assessment. The exact canonical binding is
`{url,intent,plan,http,http_received_at,contexts,surface_id,state,content,graph}`;
state is null for source or the exact rendered state, graph is recomputed flattened.
Changing any bound evidence invalidates review.

`review.coverage` qualifies all scripts/entities/properties, including terms lost
during expansion. `entities` accounts for every flattened node exactly once, with
index, node_sha256 and visible_consistency/type_suitability/no_fabrication judgments,
each containing value (supported/contradiction/unknown) and reason. They cover all
node properties and nested objects, not literal visibility of identifiers. Limit:
256 nodes per surface. Missing/extra/duplicate/changed nodes prevent pass while
independent correctly bound contradictions remain. Surfaces are independent.

All three rules are required for documentary C of this selected page. No automatic
review is supplied; authored judgments are labeled synthetic. JSON-LD processing
does not prove vocabulary validity, independently verified visible facts, rich
results, indexing or ranking. TS32 entity identity and TS33 validator categorization
remain separate controls.

## Sources

- [Google general structured-data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies): content relevance, visibility and limits of automated quality checks.
- [W3C JSON-LD 1.1 API](https://www.w3.org/TR/json-ld11-api/): processing semantics; no Google eligibility inference.

Consulted 2026-10-13. Dated capture provenance is retained in
`research/structured-content-2026-10-13/provenance.json`. TSEP requirements above
remain an editorial candidate, not an endorsement by these publishers.
