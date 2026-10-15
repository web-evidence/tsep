# TS25 — critical stage presence / présence critique par stade

Draft.44 defines TS25-A01/A02, reader `critical-stage-presence-v1`, interpreter43,
adapter43, HTML25, replay3. This document specifies a candidate; it does not
establish observed qualification, browser execution, actual client application
or certification. Sources and application receipts are separate.

## Français

Draft.44 / reader3 : les champs reviewer, assistance et reason des revues TS25 fournies sont limités à8192octets UTF8 bruts chacun, avant strip ou normalisation ; chaque objet revue, champs supplémentaires inclus, à32768octets de JSON compact UTF8. Toute revue fournie est vérifiée à l’admission, même inutilisée. Un dépassement donne un refus technique avant publication, jamais C ou NT public ; les originaux sont conservés sans réécriture. Le diagnostic natif de chaque règle est borné à4MiB de JSON compact UTF8 trié, y compris A01 et les sorties d’erreur. Au dépassement, un diagnostic compact explicitement incomplet conserve un fail indépendant établi, sinon inconclusive ; aucun pass. Le transport refuse ce marqueur et borne aussi à4MiB par cible la somme des artefacts TS25 réellement sérialisés (JSON UTF8 indent2, saut de ligne final), pour les règles demandées. Les maxima individuels ne garantissent pas que toutes leurs combinaisons respectent les bornes cumulées. Aucun changement des autres contrôles ni du validateur partagé.


Draft.43 / reader2 : le champ render est un objet documentaire contenant states. render:[] n’est pas équivalent à render:{states:[]}. Un conteneur non objet ou une population mal formée donne une couverture inconnue, sans coercition ni arrêt des lectures source indépendantes. Une absence source requise et qualifiée reste fail ; une source présente ne transforme pas cette couverture inconnue en pass. Une liste states vide est valide quand aucun état n’est requis. Les revues restent liées aux ID d’états, jamais à leurs indices. Cette frontière propre à TS25 ne migre pas celle de TS23. Les self-digests contradictoires conservent leur refus technique.


TS25 compare des **éléments critiques préalablement déclarés** aux originaux
HTTP et aux états DOM fournis. Un résultat C porte seulement sur cette population,
ces éléments, leurs politiques et conditions. Il ne prouve ni l’exhaustivité du
site ni ce que Google a rendu ou indexé. La revue de pertinence du périmètre et
la revue de visibilité/contexte sont réellement fournies par leur responsable ;
le lecteur vérifie leurs liens et leurs dates, sans authentifier leur auteur.
Les exercices rédigés restent marqués synthétiques.

### Entrées et décisions préalables

L’entrée captures de version2 conserve `url`, `observed_at`, `context`, `intent`,
`http`, `render`, `presence_synthetic`, `presence_plan_review` et
`presence_context_reviews`. Le plan `intent.critical_presence` contient :

- `reader`, `window_start`, `window_end`, `max_duration_ms`, `origins`, `final_url` ;
- `population`, `scope_reason`, `items`, `roles`, `states`.

`intent.declared_at` précède la fenêtre ; `intent.crawler` est le User-Agent
HTTP exact, sans usurpation d’une visite Google. La fenêtre couvre au plus24h,
chaque échange au plus30000ms. Contexte réseau, bornes, outil et version sont
explicites. Les URL initiale/finale et chaque saut appartiennent à 1–16 origines
HTTP(S) déclarées. L’interprétation exige une trace complète donnant la réponse
finale200 attendue. Les statuts autres que200 et les réponses non attribuables
restent inconnus pour la présence ; cela ne remplace pas TS01/TS02.

1–32 éléments portent chacun `id`, `role`, `reason`, `selector_id`, `expected`,
`policy`, `states`. Le rôle JSON-LD ajoute `json_pointer`. Les identifiants sont
uniques, les sélecteurs sont des ID HTML littéraux ; aucune sélection CSS libre.
Chaque état préalable porte exactement `id`, `reason`, `browser`,
`browser_version`, `conditions`. Les trois derniers doivent correspondre aux
champs fournis de l’état. Au plus16 états, liste vide permise pour source seule.
Un élément source-only sélectionne zéro état ; les autres politiques en
sélectionnent1–16. Des états prévus pour diagnostic peuvent être fournis sans
être requis par un élément source-only.

A01 exige exactement une décision pour chacun des cinq rôles ci-dessous :
`included` avec les `item_ids` exacts, ou `outside-declared-scope` avec une liste
vide et un motif. Une déclaration générique « complet » ne les remplace pas.
Une exclusion n’est pas une NA. La revue préalable lie le digest canonique de
`{url,intent}`, porte `complete:true`, et un jugement `supported` ou
`contradiction`. Elle est datée entre la déclaration et le début de fenêtre.
`reviewer`, `assistance`, `reason`, `provenance` sont conservés. `supported`
donne pass ; `contradiction` donne fail ; absence, invalidité ou unknown donne
inconclusive. Cette règle ne transforme pas le jugement en fait authentifié.

### Lecture des cinq rôles

| Rôle | Critère borné |
| --- | --- |
| `body-text` | Texte de l’élément HTML dans le body ordinaire, comparé exactement après réduction des seuls espaces ASCII ; NBSP conservé. |
| `document-title` | Élément title enfant direct du head, même comparaison textuelle. Un titre SVG ne compte pas. |
| `link` | Élément HTML a dans le body, href non vide résolu par le lecteur WHATWG Node24 épinglé, égal à l’URL HTTP(S) absolue attendue. Area hors profil. |
| `canonical` | Link enfant direct du head portant le jeton rel canonical et la référence attendue. Ne prouve pas la préférence de Google ni l’unicité globale des canonicals. |
| `jsonld` | Script du head/body de type ASCII insensible à la casse application/ld+json sans paramètre ; chaîne brute au pointeur JSON préalable, comparée sans normalisation ni expansion. |

L’ID absent prouve uniquement l’absence **à cet ID**, pas celle du contenu dans
toute la page. Un ID dupliqué, namespace étranger, contexte inerte/masqué non
qualifié, shadow ou base explicite actif est inconclusive. Les hypothèses source
statiques avec/sans scripting doivent concorder : présent/absent contradictoires
restent inconnus. Aucune exécution JavaScript n’a lieu.

Le JSON est le texte brut du script : pas de décodage d’entités HTML. Bloc vide,
syntaxe JSON mal formée ou identité attendue absente/contraire : absence qualifiée
sur ce bloc complet. Clés dupliquées, non-fini, structure scalaire non prise en
charge, MIME avec paramètres, script externe, dépassement64KiB : inconclusive.
Objet/tableau, profondeur<=64 et<=50000 nœuds ; pointeur RFC6901 sans forme fragment,
index de tableau canonique, feuille chaîne. Aucune validation Schema.org/Google,
concordance sémantique ou identité JSON-LD développée n’est déduite ; TS31–33
restent distincts. Un @id relatif ne devient pas absolu implicitement.

Les DOM fournis utilisent structured-inventory-v2, même navigation déclarée,
empreintes, HTTP et User-Agent associés, document complet, scripts activés,
sans erreurs, date après réception HTTP et avant la fin de fenêtre. Les limites
du collecteur, frames non collectés et shadow fermé inconnu restent explicites.
Une empreinte égale entre plusieurs états est un diagnostic, pas une preuve
qu’ils sont indépendants ni une erreur automatique.

Un texte/lien rendu structurellement présent nécessite aussi une revue de
contexte/visibilité liée à `{url,intent,http,state,item_id}`. Elle est postérieure
à l’état et antérieure à l’évaluation, complète, avec les champs de provenance
ci-dessus. `supported` confirme le jugement fourni ; `contradiction` fournit un
défaut. Plusieurs revues du même couple élément/état, même identiques, restent
inconclusives ; aucune préférence pour la dernière. Une absence native déjà
qualifiée reste un défaut sans cette revue. Title/canonical/JSON-LD reposent sur
leurs critères structurels explicites, sans jugement de visibilité CSS.

### Composition et inconnues

A02 applique la politique de chaque élément : source-only utilise la source ;
render-only exige tous ses états ; source-or-render passe si une branche est
présente, échoue seulement si les deux sont absentes ; source-and-render exige
les deux branches et échoue si l’une est absente. Dans la branche rendue requise,
une absence qualifiée domine une autre inconnue ; sinon tout doit être présent.
L’état requis manquant rend sa lecture inconnue, pas absente. Une branche source
positive peut donc satisfaire OR même si un état rendu manque.

Les états fournis non prévus ou dupliqués rendent la couverture inconnue. Ils
ne suppriment jamais un défaut indépendant qualifié. Cette limite conservatrice
peut faire passer une couverture de C à NT lorsqu’on ajoute des pièces hors plan ;
elle n’invente pas NC. Un élément inconnu n’efface pas un autre élément absent.
A01/A02 restent séparés : C exige les deux pass, NC conserve tout fail qualifié,
NT exprime les preuves restantes insuffisantes. Aucune NA native.

### Transport, original, migration et limites

L’adaptateur conserve l’entrée exacte et les revues originales. Chaque
self-digest DOM/support fourni est contrôlé, y compris hors plan. Une corruption
ou provenance explicitement incompatible provoque un refus technique sans
publication de rapport ; cela n’est pas un NT. L’entrée totale est bornée8MiB,
les diagnostics4MiB, les valeurs attendues1024 caractères. Aucun dépassement ne
permet une conclusion d’absence tronquée. Export et rejeu conservent les versions
exactes sans accès à l’application ou au réseau.

Voir [migration](migration-draft.44.md). Aucun verdict TS44/TS31/TS32/TS33 n’est
emprunté. Les autres rôles, interactions et conditions ne sont pas implicitement
couverts. Le profil ne prouve ni vérité, autorité thématique, absence de
cannibalisation, indexation, classement ou conformité globale.

## English

Draft.44 / reader3: supplied TS25 review fields reviewer, assistance and reason are each limited to8192 raw UTF8 bytes before strip or normalization; each entire review object, including additional fields, to32768 compact UTF8 JSON bytes. Admission checks every supplied review, including unused ones. An overrun is technical refusal before publication, never public C or NT; exact originals are not rewritten. Each native rule diagnostic is bounded to4MiB of sorted compact UTF8 JSON, including A01 and error returns. Overflow produces an explicitly incomplete compact diagnostic retaining an independently established fail, otherwise inconclusive; never pass. Transport refuses that marker and also caps the sum of actual serialized TS25 observation artifacts per target at4MiB (UTF8 JSON indent2, trailing newline), for requested rules. Individual maxima do not guarantee that every combination satisfies aggregate bounds. Other controls and the shared validator are unchanged.


Draft.43 / reader2: render is a documentary object containing states. render:[] is not render:{states:[]}. A non-object container or malformed population makes coverage unknown, without coercion or stopping independent source readings. An independently required qualified source absence remains fail; positive source cannot turn unknown coverage into pass. An empty states list is valid when no state is required. Reviews remain bound to state IDs, never indexes. This TS25-specific boundary does not migrate TS23. Contradicted self-digests remain technical refusal.


TS25 compares **prior declared critical items** with supplied original HTTP and
DOM states. C applies only to that population, inventory, policies and conditions.
It proves neither site completeness nor what Google rendered/indexed. Scope and
visibility/context judgments must actually be supplied by their responsible
reviewer; bindings and chronology are checked, authors are not authenticated.
Authored exercises remain synthetic.

Capture input2 retains url, observed_at, context, intent, http, render,
presence_synthetic, presence_plan_review and presence_context_reviews. The prior
intent.critical_presence contains reader, window_start/end, max_duration_ms,
origins, final_url, population, scope_reason, items, roles and states. Intent must
precede a <=24h window; each HTTP exchange<=30000ms; exact client and network/tool
context supplied. Initial/final/hop URLs must belong to1–16 declared exact origins.
A complete expected final200 is required; other status/unknown attribution is
inconclusive for presence, without replacing TS01/02.

1–32 unique items contain id, role, reason, selector_id, expected, policy, states;
JSON-LD adds json_pointer. Selectors are literal IDs, not arbitrary CSS. At most16
prior states each contain exactly id, reason, browser, browser_version, conditions;
last three match the supplied state. Source-only items select no states; other
policies select1–16. Optional planned diagnostic states may accompany source-only.

A01 requires exactly five explicit role dispositions: included with exact item_ids,
or outside-declared-scope with zero items and a reason. A generic completeness
assertion is insufficient. An exclusion is not NA. The complete prior supplied
review binds canonical digest of {url,intent}, dated between declaration and window
start, with reviewer, assistance, reason, provenance, judgment. Supported passes;
contradiction fails; missing, invalid or unknown review is inconclusive. A passing
check does not authenticate that judgment.

The five roles are: ordinary-body HTML text with ASCII whitespace collapse only
(NBSP retained); direct-head document title; ordinary-body native a/href equal to
the declared absolute HTTP URL through pinned Node24 WHATWG resolution (area
unsupported); direct-head link rel canonical with expected target; and inline
head/body JSON-LD script with exact case-insensitive MIME application/ld+json and
no parameters, compared as a raw string at a prior JSON pointer. Canonical here
does not establish global uniqueness or Google preference. Missing ID proves
absence at that ID only. Duplicate ID, foreign/inert/unqualified hidden context,
shadow or active explicit base is unknown. Two alternative static source hypotheses
must agree; disagreement is unknown, not a rendered-state conjunction. No JS runs.

JSON is raw script text without HTML entity decoding or JSON-LD expansion.
Empty/malformed syntax or missing/conflicting expected identity in a complete
selected block fails that item. Duplicate keys, nonfinite values, unsupported
scalars, parameterized MIME, external script or >64KiB block are unknown.
Object/array required, depth<=64 and<=50000 nodes; RFC6901 pointer, no fragment
syntax, canonical array indexes and string leaves. Relative @id stays relative.
No Schema.org/Google eligibility or semantic validity, no borrowed TS31–33 verdict.

Supplied structured-inventory-v2 DOM must be complete, script-enabled, without
errors, after HTTP and within the window, bound to supplied same-navigation HTTP
and User-Agent. Collector bounds, uncollected frames and unknown closed shadow
remain explicit. Equal snapshot hashes across states are diagnostic, neither proof
of independent observations nor automatic failure.

Structurally present rendered body-text/link requires a complete supplied context/
visibility judgment bound to {url,intent,http,state,item_id}, after snapshot and
before assessment. Supported confirms the supplied judgment; contradiction fails.
Missing, unbound or multiple reviews for one item/state (even identical) are
unknown; no latest-wins rule. Qualified native absence remains failure without a
review. Title/canonical/JSON-LD use the stated structural criteria, without CSS
visibility claims.

A02: source-only uses source; render-only requires all selected states; OR passes
if either branch is present and fails only if both are absent; AND needs both
present and fails if either is absent. In required rendered states, qualified
absence dominates unknown; otherwise all must be present. Missing state means
unknown, not absent. Positive source can satisfy OR despite missing render.
Unplanned or duplicate supplied states make coverage unknown without erasing an
independent failure. Adding out-of-plan evidence may reduce coverage C to NT,
never fabricate NC. One unknown item never erases another qualified absence.
Whole-control C requires A01/A02 pass; any fail yields NC, otherwise NT. No native NA.

Adapter checks every supplied DOM/support self-digest, including out-of-plan
states. Corruption or explicit provenance mismatch is technical refusal with no
report, distinct from NT. Exact originals/reviews retained. Input<=8MiB, combined
diagnostics<=4MiB, expected string<=1024 characters; exceeded bounds cannot justify
truncated absence. Export/replay binds exact versions without application/network.
[Migration](migration-draft.44.md) is explicit, no historical artifact rewritten.
No actual execution, authenticated review, semantic truth, topical authority,
cannibalization, indexing, ranking or global conformity inferred.

## Public reference / Référence publique

[Google JavaScript SEO basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)
distinguishes crawling/rendering concerns. It is contextual documentation, not a
validation of this profile. Public dated capture2026-10-15T01:35:11Z,
SHA-256 `3bf8735af5e3ea4a0b99c06eeb2373afa5b65cac0bc8c77c1ff9626074937970`,
221711 bytes; acquisition receipt retained in the local qualification dossier.
