# Critical content evidence / Preuves de contenu critique — version 1

## Français

Draft.24 ajoute **TS44-A01/A02/A03**, avec le profil préalable
`critical-content-nojs-v1`. Le client de référence lit des réponses publiques sans
JavaScript. Une déclaration de capacité JS d'un agent ne dispense jamais de cette
référence. **C qualifie les pièces fournies et leur cohérence dans ce périmètre** ;
il ne prouve ni vérité des faits, ni lecture réelle, ingestion, citation ou classement.
Les revues et leur identité sont fournies, pas authentifiées par l'interpréteur.

### Règles

- **A01 — périmètre critique préalable** : inventaire des faits, titres, citations,
  liens et dates, consommateurs visés, représentations et états requis, avec revue
  motivée liée au plan avant la fenêtre de capture. Rejet explicite du plan = fail ;
  revue manquante, tardive, incomplète ou inconnue = inconclusive.
- **A02 — chemin d'accès sans JavaScript** : la représentation de livraison choisie
  avant collecte doit être directement la page, ou une ressource publique reliée
  depuis cette page par le lien préalablement nommé. Vérifier HTTP, destination et
  présence structurelle de chaque élément critique. Un refus HTTP qualifié, un lien
  absent/contraire ou un élément requis absent/vide échoue. Présence et sens sont
  séparés : une valeur erronée peut être accessible et échouer ensuite à A03.
- **A03 — cohérence et revue de contenu** : comparer les valeurs explicites de chaque
  représentation déclarée et des états rendus requis à l'inventaire préalable.
  Conserver une revue du contexte critique entier, liée à chaque représentation.
  Une valeur qualifiée contraire ou une revue liée contradictoire échoue, même si
  une autre représentation ou revue manque. L'égalité des chaînes seule ne réussit
  pas A03. Un état rendu fourni hors du plan empêche pass ; il n'efface pas un fail.

Aucune exemption atomique automatique. Les trois règles restent semiAuto. Une seule
règle passée ne clôt pas TS44. NA du contrôle conserve sa justification positive
habituelle ; preuve absente ou format non pris en charge ne signifie jamais NA.
Les règles n'évaluent pas la politique d'autorisation TS42 ou l'identité TS43.

### Plan préalable

Entrée captures 1/2 habituelle : `url`, `observed_at` (date d'évaluation), `context`
network/bounds/tool/tool_version et `intent.declared_at`, `intent.crawler` (chaîne
User-Agent ASCII complète, 1–2 048 caractères). `intent.critical_content` contient :

| Champ | Contrat |
| --- | --- |
| reader, javascript | `critical-content-nojs-v1`, strictement `false` |
| consumers | 1–16 objets name/reason non blancs et basis=`reference-no-js` ; aucune capacité fournisseur implicite |
| window_start, window_end | fenêtre après le plan, avant l'évaluation, de 24 h au maximum |
| max_duration_ms | entier 1–60 000 ; borne de chaque échange |
| origins | 1–16 origines HTTP(S) distinctes exactes, avec `/` final |
| items | 1–32 objets id/role/expected ; ID distinct, expected non vide, chaîne ≤1 024 caractères |
| role | title, fact, citation, updated, version ou link ; title/fact/citation/updated doivent être couverts |
| representations | 1–8 représentations, dont `page` HTML à l'URL cible ; id/url/final_url/format/selectors |
| delivery | ID de l'unique représentation de livraison décidée préalablement ; aucun repli opportuniste |
| states | 1–8 états rendus requis, id/reason/dom_reader=`structured-inventory-v2`/selectors |

Une version visible est contrôlée quand un item version est déclaré ; les dates
et références attendues appartiennent au plan, jamais à une vérité externe inférée.
Les URL initiales/finales utilisent le sous-ensemble HTTP(S) ASCII du lecteur rendu
existant : sans identifiants ni fragment, port valide, syntaxe/longueur bornées.
Les URL de citation/link attendues utilisent le même sous-ensemble.

Les selectors sont une table `item_id → {kind,value}`. La livraison et chaque état
rendu couvrent tous les items. Les autres représentations peuvent déclarer un
sous-ensemble, ou aucun item pour une page qui sert uniquement de point d'entrée.
Un HTML utilise `id-text` ou `id-href` selon le rôle ; value est un ID littéral,
sensible à la casse, jamais du CSS. Un JSON utilise `json-pointer`, forme chaîne
RFC 6901 (pas fragment URI), ≤1 024 caractères et 64 segments. IDs : 1–80 caractères
ASCII alphanumériques, `_` ou `-` pour objets ; ID HTML ≤128, sans espace ASCII.

Chaque représentation autre que page déclare
`discovery: {from:"page", element_id:"…"}`. Un seul saut de découverte est qualifié :
`a` dans body/noscript, ou `link rel=alternate` dans head. La destination résolue
exacte doit être l'URL initiale déclarée de la ressource. L'existence d'un fichier,
un lien dans un script, un `llms.txt` à la racine ou HTTP 200 ne prouvent pas cette
relation. HTTP Link et découverte à plusieurs sauts restent hors de ce profil.

### Captures, parsing et valeurs

La page conserve `target.http`. Les ressources conservent
`target.documents: [{id,url,http}]`. Chaque chaîne GET complète et anonyme contient
sent_at/received_at par saut ; ordre, fenêtre, durée, origine et client sont vérifiés
avant conclusion. Les redirections doivent aboutir au final_url prévu. Le lecteur
ne collecte rien, n'exécute aucune commande fournie et ne contourne aucun accès.

Pour HTML, l'[observateur source 1](source-content-observation.md) est invoqué sur
les octets conservés, avec Node 24 facultatif. Les deux hypothèses statiques restent
dans la preuve ; **seule l'hypothèse sans scripts fonde ce profil**. Ni l'une ni l'autre
n'exécute JS. Un arbre incomplet ou une erreur de parsing signalée reste inconclusif.
La sélection doit être unique, HTML et sous body/noscript ; un lien alternate de
découverte a sa règle head séparée. Contextes hidden/inert/aria-hidden/style en ligne,
details/dialog, templates, namespaces étrangers et shadow sélectionné ne sont pas
qualifiés. Le contenu d'un script n'est pas un fait admissible. Une classe CSS ou
l'absence de drapeau ne prouve aucune visibilité ; la revue du contexte reste requise.

`id-text` concatène les textes descendants en ordre d'arbre, sans espace inventé,
puis réduit les seules suites d'espaces ASCII (tab, LF, CR, FF, espace) à un espace
et retire ces espaces aux extrémités. Casse, NBSP et Unicode ne sont pas normalisés.
La même convention s'applique aux chaînes JSON et au rendu. Un href concerne
l'élément a/area sélectionné, pas une recherche de caractères dans son texte.

La résolution des href utilise le [lecteur URL épinglé](source-links-experiment.md),
avec ses preuves et son Node explicite. Un href absolu dont la sérialisation reste
strictement identique peut être indépendant de base. Sinon, tout base href actif
rend cette résolution inconclusive dans ce profil ; aucune base invalide n'est
remplacée silencieusement. En l'absence de base, l'URL finale documentée est utilisée.
Le lecteur TS10 historique n'est pas modifié.

Un JSON public est `application/json`, avec charset absent ou UTF-8 seulement, au
maximum 1 Mio, sans BOM. Clés répétées, non-finis, JSON invalide, profondeur excessive
ou feuille autre qu'une chaîne restent inconnus. RFC 6901 : décoder `~1` avant `~0`,
sans normalisation Unicode ; indices de tableau décimaux sans zéro initial. `-` et
syntaxe d'indice non qualifiée restent inconnus. Membre/index valide absent = élément
absent ; traversée d'un scalaire ou null ≠ preuve d'absence. Les URL de citation
JSON doivent déjà être absolues et qualifiées. Aucun format JSON métier imposé,
aucune interprétation de Markdown, JSON-LD, PDF ou vérité du contenu déduite.

### Rendu et revues

`target.render.states` conserve id/observed_at/complete/browser/browser_version,
javascript_enabled=`true`, errors=`[]` et l'enveloppe structurée existante. La capture
rendue doit suivre la réponse page et rester dans la fenêtre. Arbre, sérialisation,
script de capture, client et HTTP sont liés selon le contrat structuré. Un base_uri
modifié ou une sélection dans un shadow ouvert reste inconclusif. Templates, frames
et shadow fermé gardent leurs limites. Le HTML sérialisé n'est pas reparsé pour
effacer un résultat de l'arbre fourni.

Acquisition `authored-synthetic` : **« DOM rédigé, non observé dans un navigateur »**,
y compris à côté d'un HTTP réellement observé. `same-navigation` est une attribution
fournie, pas une authentification indépendante d'un navigateur. Aucune exécution JS
par l'interpréteur ni observation effective d'un fournisseur n'est revendiquée.

`critical_plan_review` contient reviewer/assistance/reason/provenance, observed_at,
binding_sha256, complete=`true`, judgment supported/contradiction/unknown. La liaison
est le SHA-256 du JSON UTF-8 trié compact de `{url,intent}`. Date : entre déclaration
et début de fenêtre. Provenances : human, human-assisted, synthetic-exercise.

`critical_reviews` contient ces mêmes champs et `representation_id` (`page`, ID
ressource ou `render:<state_id>`). La revue couvre le **contexte critique entier**,
y compris sens des faits, rattachement des sources et contradictions hors du bloc
sélectionné. Elle doit suivre la pièce et précéder l'évaluation. Sa liaison est le
SHA-256 du JSON UTF-8 trié compact de `{url,intent,subject,raw,source_http}` :

- page : raw=`target.http`, source_http=`null` ;
- ressource : raw=objet complet de documents correspondant, source_http=`null` ;
- rendu : raw=état complet correspondant, source_http=`target.http`.

Toute modification d'une représentation ou du plan impose une nouvelle revue ; une
revue du rendu ne qualifie pas la source. Aucun formulaire n'invente un jugement.
L'adaptateur refuse de relabeller une revue ou un DOM synthétique en preuve réelle.

### Bornes et résultats retenus

Les 68 cas initiaux / 204 couples ont été figés avant l'interpréteur. Trois cas /
neuf couples issus d'une revue du code ont ensuite été figés avant leurs corrections :
page d'entrée refusée, contenu sélectionné dans un shadow ouvert et état non prévu.
Les résultats antérieurs incorrects restent dans le journal local. Ce second corpus
n'est pas présenté comme antérieur à toute l'implémentation.

Absence de Node/format/capture/revue ne devient pas pass. Les attentes conclusives
qui nécessitent Node portent une limite de référence explicite, sans être réécrites
pour s'accorder au runtime. La comparaison indépendante JSON/rendu peut conserver
un fail malgré une autre lecture inconnue. Chaque requête, rendu et revue reste une
pièce fournie ; ces cas synthétiques ne sont pas un audit Edikka.

Bornes du parseur et du transport structurés existants conservées ; inventaires
interprétés cumulés ≤2 Mio par règle. Un dépassement rend la représentation concernée
inconnue, sans tronquer une liste pour conclure par absence. Les erreurs de lecture
sont mémorisées seulement pendant l'évaluation d'une règle afin de ne pas relancer
un parseur en échec pour chaque item. Aucun cache entre jeux de preuves.

## English

Draft.24 adds TS44-A01/A02/A03 under prior `critical-content-nojs-v1`. Its explicit
reference client has no JavaScript. An asserted provider JS capability cannot waive
that reference. C qualifies supplied evidence and coherence in the declared scope;
it proves neither factual truth nor actual agent consumption, ingestion, citation,
indexing or ranking. Supplied reviews and their authors are not authenticated.

A01 checks a prior reviewed critical inventory, consumers, representations and
required states. A bound rejection fails; absent/late/incomplete/unknown review is
inconclusive. A02 checks the preselected no-JS delivery path, expected public HTTP
response and structural presence. A qualified denial, missing/wrong discovery link
or absent/empty required element fails. A03 compares qualified values to the declared
inventory and requires a whole-critical-context review for every compared
representation. A qualified value/review contradiction survives other unknowns.
String equality alone cannot pass. An unplanned supplied rendered state prevents
pass without erasing independent failures. All three rules are semiAuto; no atomic
NA and no whole-control conclusion from a partial rule selection.

The input retains url, assessment observed_at, collection context and prior intent
with the complete reference User-Agent. The plan table above is normative in both
languages: 1–16 named consumers with reference-no-js basis; up to 24-hour window;
1–60,000 ms request bound; 1–16 exact origins; 1–32 distinct items covering at least
title/fact/citation/updated; optional version/link roles; expected nonempty strings
up to 1,024 characters. Up to eight representations and eight required states.
Delivery is exactly one preselected representation, with no opportunistic fallback.
Main page is declared HTML at the target. Every representation supplies expected
initial/final qualified HTTP URLs and format html/json. Citation/link expected URLs
use the existing bounded ASCII HTTP subset, without credentials or fragments.

Selectors map item IDs to kind/value. Delivery and every rendered state cover every
item; other representations may map a subset or none for a discovery-only page.
HTML uses literal case-sensitive id-text or id-href by role. Object IDs use 1–80
ASCII alphanumeric/underscore/hyphen characters; HTML IDs use at most 128 without
ASCII whitespace. JSON uses the RFC 6901 string form (not URI fragments), at most
1,024 characters and 64 tokens. Alternative resources declare discovery from page
and a literal element ID. Only one discovery hop is qualified: body/noscript anchor
or head link rel=alternate, resolving exactly to the declared initial resource URL.
HTTP Link, implicit root llms.txt conventions or multi-hop discovery are unsupported.

Page HTTP and extra document records retain complete anonymous GET chains, client,
per-hop timestamps, origins and expected final URL. The interpreter does not collect
or execute supplied commands. HTML is parsed with optional explicit Node 24 and the
pinned content observer; both static hypotheses are retained but only scripting
disabled drives this profile. No scripts execute. Incomplete/recovered trees,
duplicate IDs, hidden/inert/aria/inline-style/details/dialog/template/foreign/shadow
selection are unqualified. CSS visibility is never established. Noscript in the
no-JS source hypothesis is explicit; no TS01 reader is upgraded.

Text is tree-ordered descendant concatenation, followed only by ASCII whitespace
collapse/trim. No invented separators, case folding, NBSP or Unicode normalization.
References read href on a/area, not strings inside surrounding text. Qualified URL
resolution retains the pinned worker result. Exactly serialized independent
absolute hrefs can ignore a base; otherwise an active base is unknown in this first
profile. No base fallback is invented. With no base, use the captured final URL.

JSON: application/json with absent or UTF-8 charset only, ≤1 MiB, no BOM, duplicate
keys/nonfinite values rejected. Only string leaves qualify. Pointer decoding applies
~1 before ~0; exact Unicode keys, decimal array indices without leading zeros.
Absent valid member/index means absence; scalar traversal, null, '-' or unsupported
index syntax remain unknown. Citation/link JSON strings must already be qualified
absolute URLs. There is no custom business schema, Markdown/PDF/JSON-LD interpretation
or truth claim.

Rendered states use the existing structured-inventory-v2 envelope, complete error-free
state, explicit browser/version/JS context, after page response and within the
window. Script/tree/serialization, HTTP and client bindings remain mandatory.
Changed base or selected shadow context is unknown; frames/templates/closed shadow
remain outside coverage. The serialization is not reparsed to override the tree.
An authored-synthetic state must say it is an authored DOM, not observed in a browser,
even beside observed HTTP. Same-navigation is supplied attribution, not independent
authentication. Required state IDs must be prior; extra states retain an unknown.

Reviews have reviewer/assistance/reason/provenance, observed_at, binding_sha256,
complete=true and judgment supported/contradiction/unknown. Provenance is human,
human-assisted or synthetic-exercise. Plan review lies between declaration and
window start and binds compact sorted UTF-8 JSON `{url,intent}`. Representation
reviews follow their evidence and precede assessment; they cover the whole critical
context, meaning, source relationship and outside-block conflicts. They bind
`{url,intent,subject,raw,source_http}`: page raw is main HTTP and source_http null;
resource raw is its entire document record and source_http null; rendered raw is
the full state and source_http main HTTP. A review of rendered content cannot
qualify source HTML. Changes require new bindings; no review is fabricated by tools.
Synthetic reviews/DOMs cannot be imported as real evidence.

The initial 68 cases/204 pairs were frozen before the interpreter. Three additional
boundary cases/nine pairs were frozen after code review but before fixes, retaining
the observed former failures. They are not retrospectively described as pre-code.
Expected conclusive outcomes retain explicit optional-runtime limits. Missing Node,
formats or evidence never pass. Independent contradictions survive other unknowns.
Existing parser/structured transport bounds apply; combined retained inventories
are limited to 2 MiB per rule, with unavailable representations rather than truncated
absence claims. Reader failures are cached only within a rule evaluation, never
across supplied evidence sets. These authored cases are not an Edikka audit.

## References / Références

[RFC 6901](https://www.rfc-editor.org/rfc/rfc6901) defines pointer syntax;
[RFC 8259](https://www.rfc-editor.org/rfc/rfc8259) describes JSON. They do not define
SEO acceptance. Dated bounded text extracts and fingerprints are recorded in
provenance/critical-content-v1.json; the source-tree/DOM references remain in
provenance/source-content-v1.json. / Ces sources structurent la lecture, pas une
promesse SEO ou une capacité supposée d'un agent.
