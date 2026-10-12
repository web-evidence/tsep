# TS12 — Canonical comparison evidence / Comparaison documentaire, profil 1

## Français

`google-canonical-comparison-v1` qualifie la documentation des comparaisons pour
l’ensemble sélectionné, avec trois règles semiAuto. A01 : plan et revue préalables ;
A02 : pièces natives attribuées et comparaisons ; A03 : qualification et décision
fournies. C ne signifie ni canonical correcte, ni accord Google, ni TS10 conforme,
ni indexation, ni état actuel de la page. Une différence peut accompagner C ; une
égalité sans revue reste NT. Aucun NA automatique. Les contrôles TS01–TS44 et
leurs titres sont conservés. Le diagnostic Search Console 1 et TS08 restent distincts.

### Plan et périmètre

La cible reprend le plan `intent.inspection` et les `inspection_records` natifs de
[TS08](inspection-evidence.md), avec les mêmes bornes, dates, provenance explicite
`inspection_synthetic`, contexte et sélection de 1–16 URL. `context.id` et
`intent.crawler` attribuent aussi les captures techniques. Un historique ne devient
pas prospectif. L’acquisition API, le dernier crawl rapporté, la capture technique
et les changements déclarés restent distincts ; lastCrawlTime ne date pas les champs.

`intent.canonical_comparison` contient reader, source_reader=`html-tree-canonical-v1`,
http_reader=`http-link-context-v1`, max_capture_age_hours et max_capture_offset_hours
(entiers 1–8760), puis members, exactement les URL sélectionnées. Chaque membre
contient url, preferred_url absolue HTTP(S) sans fragment, preference_source (source
indépendante de la simple recopie du résultat) et rendering. La fraîcheur compare
capture et évaluation ; le décalage compare acquisition API et capture. Ces seuils
locaux ne prouvent aucune identité de représentation. Les connaissances antérieures
restent dans le plan TS08. Les dates/hachages ne prouvent ni auteur ni histoire.

Le premier profil impose rendering.mode=`required`, dom_reader=`structured-inventory-v2`
et 1–16 required_states uniques, avec id/interactions/wait. Il n’accepte aucune
exemption libre ni exemption de stabilité. Source seule : observations conservées,
A02 inconclusive et contrôle NT sauf contradiction documentaire établie. C couvre
les surfaces et états déclarés, jamais tous les états possibles, frames, templates
ou shadow fermé. Aucune nouvelle collecte navigateur n’est effectuée par le lecteur.

`inspection_plan_review` garde sa liaison SHA-256 au JSON compact trié UTF-8
{url,intent}, reviewer/assistance/provenance/reason/complete/observed_at TS08 et
ses jugements selection/objectives. TS12 exige aussi preferences, surfaces et
temporal_policy, chacun supported/contradiction/unknown. Revue après plan et avant
chaque acquisition API et technique. Une contradiction fournie ou une acquisition
explicitement antérieure au plan échoue A01 ; un manque reste inconclusive.

### Pièces et comparaisons

`documents` contient exactement un document par membre, url/observed_at/context_id
et trace HTTP native complète ; les limites HTTP existantes restent applicables.
Le GET final doit être 200 et son URL exactement celle du membre. Une redirection
vers une autre URL laisse la comparaison inconclusive, sans substitution. Les états
DOM fournis lient scénario, contexte, URL, dates, trace HTTP et acquisition de même
navigation selon structured-inventory-v2. Provenance authored-synthetic seulement
pour un exercice ; same-navigation pour une pièce réelle. Aucune authenticité de
navigation n’est inférée. Les supports et empreintes existants restent obligatoires.

A02 reprend la qualification native/fraîcheur TS08-A02, exige une googleCanonical
présente et lisible, puis HTTP Link, HTML UTF-8 explicite et tous les états prévus.
Une googleCanonical absente reste inconclusive, sans succès par comparaison vide.
userCanonical absente est un fait API ; elle ne prouve aucune absence HTML/DOM.

HTTP : retenir le contexte du premier rel/anchor et tous les candidats du contexte
courant selon http-link-context-v1, avec doublons et ordre. Ignorer ses verdicts
TS10 de préférence : une cible différente n’est pas un échec documentaire TS12.
Les items d’autre contexte/relation restent dans l’observation, exclus des valeurs
comparées. Un item inconnu rend l’inventaire inconnu, sans effacer les autres surfaces.

HTML : deux inventaires statiques parse5/source-head, scripts activés/désactivés,
sans exécution. Exiger inventaires/préfixes complets, sans erreur, ambiguïté de
namespace/attribut, head indirect/réinséré ou template shadow/for. Retenir les link
canonical attribuables au head direct ou au body ordinaire avec leur position. La
position body est un fait conservé, pas un fail TS12. Les deux listes de valeurs et
positions doivent être identiques ; sinon surface inconnue. Garder les inventaires,
bases, segments et limites. Les templates ordinaires restent hors signaux actifs.
DOM : lecteur structuré existant, valeurs brutes et positions conservées ; aucune
source statique ne remplace un état rendu. Les URL relatives, vides, avec fragment
ou hors syntaxe HTTP(S) bornée restent inconnues dans ce profil. Ce refus n’affirme
pas qu’elles seraient invalides pour Google. Aucune résolution/base/normalisation
implicite. Les propriétés href résolues restent des pièces distinctes du DOM.

Chaque surface a state=present/absent/unknown et values, une liste ordonnée de toutes
les chaînes, doublons conservés. Une liste vide ne devient absent qu’après inventaire
complet qualifié. Comparer chaque valeur connue à Google et à la préférence avec
les libellés exact-string-equal/exact-string-different. Ces libellés ne concluent
pas à l’équivalence sémantique, y compris casse d’hôte/port/barre finale. Afficher
séparément Google, API userCanonical, HTTP, HTML et chaque DOM ; aucune valeur
« déclarée » synthétique. Toute lacune requise empêche A02 pass.

### Revue, décisions et agrégation

`comparison_reviews` contient exactement une revue par URL. Même enveloppe de revue
que TS08, liée à {url,intent,record,document} exact (document=null s’il manque), datée
après toutes les acquisitions disponibles, avant évaluation. La liaison porte sur
les pièces, jamais sur un résultat attendu. claims contient exactement les clés
googleCanonical, userCanonical, http, html, et dom:<id> pour chaque état prévu,
avec state et values. Une revendication explicite différente d’une liste complète
connue échoue A03 ; surface inconnue ou revendication absente/inconnue reste
inconclusive. Le lecteur ne devine aucune valeur et ne choisit pas parmi les doublons.

interpretation et temporal_interpretation sont supported/contradiction/unknown ;
objective_relation aligned/different/undetermined. temporal_scope doit être
reported-index-and-separate-captures ; current-live-page ou all-fields-at-last-crawl
est une contradiction explicite de portée. Une différence temporelle dans les
seuils n’est pas un défaut ; cause non établie admise. `changes` est une liste
explicitement fournie (vide admis), au plus 16 entrées {at,description,source} ;
elle documente des informations, sans établir une cause. Une liste vide n’atteste
pas l’absence de changements. Les changements restent dans la revue et les preuves.

explanation et decision reprennent les types TS08 : observation, hypothesis avec
test, unresolved ; accept, correct avec action, monitor avec criterion/due_at après
revue, revise-objective avec new_plan_reference. owner/reason requis. Une cause
présentée comme établie sort de ce premier profil et reste inconclusive sans preuve
contraire, jamais fail automatique pour pièce manquante. Aucune décision n’est
exécutée ; nouvelle intention = nouveau plan, ancien conservé.

Les facettes sont indépendantes : une revendication Google contredite par ses
propres octets attribués conserve fail malgré un DOM absent, une source inconnue ou
une fraîcheur insuffisante. Une propriété/empreinte API invalide ne permet pas ce
rapprochement. Un manque de revue seul ne devient pas NC. Omission/duplication/URL
non prévue empêche C. Borne cible TS08 4 Mio ; observation finale 4 Mio : dépassement
refusé, aucune absence ou contradiction extraite d’un diagnostic tronqué. Comptes
réels restreints ; cas et revues rédigés synthetic. Rapports FR/EN, preuves, gate,
EARL et rejeu portent cette portée documentaire, sans audit de site implicite.

## English

`google-canonical-comparison-v1` assesses documented comparisons for the explicit
selected set: three semiAuto rules, A01 prior plan/review, A02 attributed native
readings/comparisons, A03 supplied qualification/decision. C is neither correct
canonical, Google agreement, TS10 conformity, indexing nor current page state.
Difference may accompany C; equality without review remains NT. No automatic NA.
Keep TS01–TS44 titles/provenance and historical diagnostic1/TS08 semantics.

Reuse TS08 intent.inspection, native inspection_records, explicit inspection_synthetic,
context and 1–16 members, bounds and chronology. Add context.id and intent.crawler.
Acquisition, reported crawl, technical capture and supplied changes remain separate;
lastCrawlTime does not timestamp every field. Historical material is not prospective.
Hashes/dates authenticate neither people nor history.

intent.canonical_comparison contains reader, source_reader=html-tree-canonical-v1,
http_reader=http-link-context-v1, integer max_capture_age_hours and
max_capture_offset_hours (1–8760), and members matching the exact selected set.
Each has url, absolute fragment-free HTTP(S) preferred_url, preference_source
(independent of copying the result) and rendering. Age compares capture/assessment;
offset compares API/capture. Local thresholds establish no representation identity.
Retain prior knowledge in the TS08 plan. Require rendering.mode=required,
dom_reader=structured-inventory-v2 and 1–16 unique required_states with
id/interactions/wait. No free-text or stability exemption in this first profile.
Missing rendered states retain source observations but prevent A02 pass and whole
C. Scope covers declared states, never all possible states, frames, templates or
closed shadow. This reader performs no browser collection.

inspection_plan_review retains TS08 envelope and exact sorted compact UTF-8 JSON
{url,intent} SHA-256, selection/objectives, plus preferences/surfaces/temporal_policy
judgments supported/contradiction/unknown. Review follows plan and precedes every
API/technical acquisition. Supplied contradiction or explicit acquisition before
plan fails A01; gaps remain inconclusive.

Exactly one document per member retains url/observed_at/context_id and complete
native HTTP trace under existing bounds. Require final GET 200 at the exact member
URL; redirect elsewhere remains inconclusive, without substitution. Supplied DOM
states bind scenario/context/URL/dates/HTTP and same-navigation acquisition under
structured-inventory-v2. authored-synthetic acquisition only for exercises;
same-navigation for real evidence. Required support/hashes do not authenticate
execution. A02 reuses TS08-A02 native/freshness checks, requires present readable
Google canonical and every HTTP/HTML/DOM surface. Absent Google canonical remains
inconclusive, never vacuous success. Absent userCanonical is API absence only.

HTTP: retain first rel/anchor context, ordered duplicate current-context candidates
and unknowns through http-link-context-v1; ignore its TS10 preference outcomes.
Other-context/relation items remain evidence, excluded from compared values.
Unknown item makes that inventory unknown, without erasing other surfaces.
HTML: retain both static parse5/source-head scripting alternatives, no execution.
Require complete inventories/prefixes without parse/prefix/namespace/attribute
ambiguities, indirect/reinserted head or shadow/for templates. Keep attributed direct
head and ordinary body canonical values/positions. Body placement is a documented
fact, not TS12 failure. Both ordered value/position lists must match; otherwise
unknown. Preserve inventories, bases and byte spans. Ordinary template contents
are inactive. DOM uses the existing structured reader, raw values and positions;
static source cannot replace a rendered state. Relative, empty, fragment-bearing
or unsupported HTTP(S) syntax stays unknown in this profile, not a Google-invalid
claim. No implicit base resolution or normalization. DOM resolved href stays evidence.

Each surface is present/absent/unknown with ordered values, retaining duplicates.
Empty means absent only after complete qualified inventory. Compare each known value
to Google and preference using exact-string-equal/exact-string-different, never URL
semantic equivalence (including host case, default port and trailing slash). Keep
Google, API userCanonical, HTTP, HTML and each DOM separate. No synthesized declared
canonical. Any required gap prevents A02 pass.

comparison_reviews has exactly one supplied review per member, with TS08 envelope,
binding exact {url,intent,record,document}, document=null when missing. Review follows
all available acquisitions and precedes assessment. claims has exactly googleCanonical,
userCanonical,http,html,dom:<id> per planned state, each state/values. An explicit
claim contradicting a complete known list fails A03; missing/unknown claims or unknown
surfaces remain inconclusive. Never infer a value or choose among duplicates.
interpretation and temporal_interpretation use supported/contradiction/unknown;
objective_relation is aligned/different/undetermined. Require temporal_scope=
reported-index-and-separate-captures; current-live-page or all-fields-at-last-crawl
explicitly contradicts scope. Offset within policy is not a defect and an unresolved
cause is allowed. changes is an explicit list, empty allowed, ≤16 {at,description,source}
entries: information only, never proof of causality; empty does not prove no changes.

Retain TS08 explanation types observation/hypothesis with test/unresolved and decisions
accept/correct with action/monitor with criterion and future due_at/revise-objective
with separate new_plan_reference. owner/reason required. established-cause remains
outside this first profile, inconclusive without contradictory evidence; missing
proof alone does not fail. Execute no action or plan rewrite.

Facets remain independent: an attributable false Google claim fails despite missing
DOM, unknown source or old dates. Invalid API attribution/hash cannot support that
claim comparison. Missing review alone never fails. Missing/duplicate/unplanned
members prevent C. Target bound 4 MiB; final observation bound 4 MiB, refusal without
truncated absence/failure claims. Real account access restricted; authored material
synthetic. FR/EN reports, gate, EARL and exact replay retain documentary scope, not an
implicit site audit. See the distinct migration; frozen authored cases precede code.
