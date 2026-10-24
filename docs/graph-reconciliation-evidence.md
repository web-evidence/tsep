# TS18 — supplied graph reconciliation / rapprochement de graphe fourni

Candidate profile `supplied-graph-reconciliation-v1`; native document plan
`supplied-graph-documents-v1`. Draft.38, interpreter37, adapter39, HTML22, replay3.
The three atomic rules are separate from individual URL/pair observations.
Qualification results are recorded separately from this contract.

## Français

Le plan antérieur `intent.graph` fixe une origine HTTP(S) exacte,1–16 documents,
1–4 racines choisies dans ces documents,1–8 familles couvrant chaque document une
seule fois, une justification de sélection et une fenêtre de24h au maximum.
Chaque document indique une URL demandée égale à son URL finale et1–16 états
nommés, dont au moins un déclaré sans interaction ;64 états au total. Aucune
équivalence de redirection, canonical, barre finale, casse ou paramètres n’est
inférée. Le JSON est limité à8MiB, les diagnostics à4MiB ; aucun verdict tronqué.

`graph_inventories` conserve les originaux `reference`, `crawl`, `cms`, `sitemap` :
base64 canonique, SHA256, complétude et date fournies. Chaque original est borné à
1MiB. La référence contient exactement les URL ordonnées du plan en UTF-8,
une par ligne, avec LF final facultatif ; sa date précède le plan liant son hash.
Les trois autres dates restent dans la fenêtre préalable et sont visibles auprès
du rapprochement. Jusqu’à128 URL distinctes par inventaire. Les URL hors population
restent des diagnostics non évalués ; elles ne deviennent pas des orphelins.

Crawl et CMS utilisent CSV avec dialecte déclaré : encodage `utf-8` ou
`utf-8-sig`, séparateur virgule ou point-virgule, guillemet double,
`doublequote:true`, en-tête ligne1 et nom exact de colonne URL. Pas de détection
heuristique ;32 colonnes,65536 caractères par champ, URL4096 caractères au plus.
Le sitemap réutilise le lecteur TS15 sur un URLset fourni, décodage déclaré,
structure et bornes qualifiées ; aucun index récursif ni collecte.

Chaque production fournit `mode`, `tool`, `tool_version`, `derived_from`.
Le crawl fermé ajoute seulement `seed_roots` et `frontier_sha256` (SHA256 JSON
canonique `{nodes,roots}`), mode `follow-links`, dépendances vides, racines exactes.
Il déclare un départ depuis ces seules racines ; mode liste, amorçage mixte ou
champ d’amorçage supplémentaire sont hors profil et restent NT. Le CMS déclare
`native-export` sans dépendance ; le sitemap déclare `native-export` ou
`cms-generated` dépendant de `cms`. Ces déclarations ne sont pas authentifiées.
L’appartenance à un crawl ne crée jamais une arête ni une profondeur.

`graph_documents` conserve jusqu’à32 dossiers HTTP/DOM originaux. Les lecteurs
TS16/TS17 qualifient les témoins source et DOM : source sous deux hypothèses
statiques concordantes, DOM lié au HTTP et déclaré sans interaction. Un témoin
positif indépendant établit une paire présente ; l’absence exige toutes les
surfaces éligibles qualifiées ; sinon la paire reste inconnue. Les états après
interaction sont diagnostiques. HTTP200 ne prouve ni contenu attendu ni absence
de soft404 ; cette limite reste visible.

Le calcul utilise uniquement les documents déclarés et des sources distinctes,
sans auto-liens. Distance basse : arêtes connues et possibles ; distance haute :
chemin connu. États : `exact`, `interval`, `no_proven_route`, `unreachable` dans
ce seul graphe borné. Les degrés entrants sont aussi des intervalles. Un candidat
sans entrant exige degré maximal0 et n’est jamais une racine ni un orphelin global.
Les cycles déconnectés restent distincts des pages sans aucun lien entrant.

A01 qualifie le rapprochement documentaire, A02 les mesures natives. Leurs domaines fermés sont pass/inconclusive : aucune valeur fail fabriquée pour ces mesures. A03 vérifie
les revues fournies `graph_reviews`, sans produire de jugement : chaque famille,
différence connue d’inventaires, candidat sans entrant et document inaccessible
reçoit un sujet calculé. Les revues lient le plan, les dossiers d’inventaire entiers
(dates comprises), les originaux du graphe et les mesures par SHA256 canonique.
Elles indiquent sujet, hash, auteur fourni, date, motif, provenance synthétique et
`explained`, `defect` ou `unresolved`. La date suit la fin de fenêtre et précède
l’observation. Une revue manquante, ambiguë, mal liée ou supportée par une mesure
inconnue reste indéterminée. Une différence connue et revue comme défaut peut
rester NC malgré un graphe incomplet ailleurs. Le sens du motif et l’identité du
relecteur ne sont pas authentifiés. Les revues de test sont explicitement rédigées
pour les scénarios synthétiques ; aucune revue Edikka ou personnelle n’est créée.

## English

The prior `intent.graph` fixes an exact HTTP(S) origin,1–16 documents,1–4 roots,
1–8 families covering each document exactly once, selection rationale and a
capture window of at most24hours. Requested and final document URLs must match
exactly. Each source declares1–16 named states including a no-interaction state;
64 states total. No redirect/canonical/query/case/slash equivalence. Input JSON is
bounded to8MiB and diagnostics to4MiB, with no truncated conclusion.

Retain canonical base64, SHA256, completeness and supplied dates for original
reference/crawl/CMS/sitemap inventories, each at most1MiB and128 distinct URLs.
The UTF-8 ordered reference lines (optional final LF) predate the plan binding
its hash. Other dates must lie within the window and remain visible alongside
reconciliation. Outside URLs are unevaluated diagnostics, never orphan claims.
CSV encoding/delimiter/quoting/header/URL column are explicit, without guessing:
UTF-8 or UTF-8-BOM, comma/semicolon, double quotes, doublequote enabled, header1;
32 columns,65536 characters per field,4096 per URL. Sitemap uses the exact TS15
URLset reader with declared encoding, no recursive index or acquisition.

Production is supplied and unauthenticated. Crawl declares closed `follow-links`
production from the exact roots only, no dependencies, with bound nodes/roots
frontier. Additional seeding fields, mixed or list seeding are inconclusive.
CMS is a native export; a CMS-generated sitemap explicitly retains its dependency.
Crawl membership never creates native graph edges or establishes reachability.

Up to32 original document records feed the existing TS16/TS17 source/DOM readers.
An independent qualified witness establishes an edge; absence needs every eligible
qualified surface; otherwise unknown. After-interaction states are diagnostic.
HTTP200 does not establish expected source content or exclude soft404s.

Distances use known edges for the upper bound and possible edges for the lower
bound. Exact/interval/no-proven-route/bounded-unreachable states remain distinct.
Incoming degrees count distinct non-self sources as intervals. A no-incoming
candidate needs upper degree0 and is neither a root nor a site-wide orphan.
Disconnected cycles are separate. There is no universal SEO depth threshold.

A01 qualifies original reconciliation; A02 qualifies native measurements; their closed outcome domains are pass/inconclusive, with no fabricated fail for these measurements; A03
checks supplied documentary reviews, never inventing them. Native subjects cover
each family, known inventory difference, bounded no-incoming candidate and
unreachable document. Reviews bind the prior plan, entire inventory records
including dates, graph originals and measurements with canonical SHA256. Supplied
reviewer/date/rationale/synthetic flag/disposition must match. Review time follows
window end and precedes observation. Missing/ambiguous/misbound/unresolved reviews
or unqualified supporting measurements remain inconclusive. An independently
evidenced supplied defect survives unrelated unknowns. Reviewer authenticity and
rationale semantics are not assessed. Synthetic authored test reviews are never
real personal/Edikka approval.

## Integrity, outcomes and delivery / intégrité, résultats et livraison

Provided inconsistent self-hashes are technical intake refusals, including
unplanned evidence or missing plans. Missing evidence remains native inconclusive.
No digest repair, C/NA from absence, global conformity, certification, indexing or
ranking inference. Originals remain intact in exports and exact offline replay.
No network acquisition. Consumers require explicit qualified import and separate
app acceptance; this contract itself proves neither. Historical failures remain.
