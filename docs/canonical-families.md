# Canonical families / Familles canoniques — TS10

## Français

Extension de conformance `input_version: "1"`, draft.5. Chaque cas reste
synthétique ; les chaînes HTTP, HTML, DOM et XML sont interprétées hors réseau.
Les verdicts attendus sont séparés de l’entrée. A01/A03/A04 restent `semiAuto` ;
A02 reste `manual`, même lorsque le comparateur est lancé par un logiciel.

### Cible, intention et captures

Une cible TS10 représente une **famille inventoriée**, identifiée ici par son URL
préférée dans `target.url`. Deux familles de même URL préférée doivent être réunies
ou évaluées séparément. `observed_at` borne la fin de l’examen ; `context` contient
`id`, `network`, `bounds`, `tool`, `tool_version`, tous non vides. L’intention est
antérieure à toutes les captures/revues, qui précèdent cette borne finale.

`intent` contient `declared_at`, `crawler` et l’objet `canonical` :

| Champ | Forme et signification |
| --- | --- |
| `preferred_url` | URL HTTP(S) absolue, sans fragment, présente dans `members` |
| `members` | Liste non vide et unique de `{url, required_methods, rendering}` |
| `required_methods` | Liste non vide sans doublon : `html`, `http`, `redirect`, `dom` |
| `sitemaps` | Stratégie ci-dessous |
| `links` | Population et exceptions ci-dessous |

Il n’y a pas de déduction de famille par paramètres, casse, slash ou similarité.
Une variante en 200 peut déclarer une préférence différente de sa propre URL.
Une méthode requise absente dans une capture complète donne fail ; une capture
manquante/ambiguë donne inconclusive. Toutes les déclarations présentes sont
examinées, y compris celles d’une méthode non exigée.

`target.documents` conserve les captures des membres. Chaque document contient
`url`, `observed_at`, `context_id` et `http` (échanges par saut selon le
[format commun](conformance.md)). Aucun téléchargement n’a lieu. Les captures
répétées d’une même URL sont ambiguës. Le contexte doit correspondre exactement.

Le plan `rendering` et les captures `document.render` suivent le
[format source/DOM](rendered-states.md) : états, interactions et attente préalables,
navigateur/version, date, URL finale, contexte, JavaScript activé, erreurs et DOM
complet. `source_http_sha256` lie chaque état à la trace ordonnée avec SHA-256 de
`json.dumps(http, sort_keys=True, separators=(',', ':'), ensure_ascii=False)` encodé
en UTF-8. Ce n’est pas une empreinte du protocole réseau. Un état requis manquant
ou mal attribué reste indéterminé ; une contradiction attribuable n’est pas effacée.

Un plan `{mode: "exempt", basis: "reviewed-stable"}` nécessite dans le document
`exemption_review` : `basis`, `reviewer`, `reason`, `observed_at`,
`source_http_sha256` et `support: [{name, content, sha256}]`. L’empreinte de support
porte sur les octets UTF-8 exacts de `content`. La revue suit la capture et explique
avec ses pièces pourquoi les signaux/liens n’exigent pas d’autres états. Le mode
`non-html` est réservé ici à `text/plain; charset=utf-8`, avec ce même record
positif. L’interpréteur ne prouve ni la sincérité ni la suffisance de ces revues.

### A01 — déclarations

Examiner tous les membres, HTTP Link finaux, HTML source et DOM requis. L’HTML
explicite doit contenir un head puis un body correctement emboîtés ; le sous-ensemble
d’éléments est celui du format commun. Un canonical hors head ou une URL différente,
relative ou avec fragment donne fail selon le critère TSEP. Les valeurs répétées
identiques restent visibles et peuvent passer. L’en-tête HTTP peut suffire, même
sans balise HTML ; une méthode `redirect` exige une chaîne complète vers la préférence.

Le parseur Link conserve les champs répétés et les listes séparées par virgules,
avec cibles entre chevrons et `rel` cité ou simple. Un paramètre répété, une syntaxe
ambiguë, un échappement ou un contexte canonical supplémentaire (`anchor`, etc.)
reste inconclusive. Les attributs canonical HTML autres que rel/href, `base`, le
HTML à réparer et les formats non pris en charge nécessitent une autre méthode.
Les scripts ne sont pas exécutés. Un format valide hors de ce sous-ensemble ne
constitue pas à lui seul un défaut SEO.

### A02 — destination et contenu

Un GET attribuable de l’URL préférée doit répondre directement 200. Une redirection
observée suffit à fail, même si sa suite n’est pas capturée ; un 404/5xx donne fail.
Un échange tronqué ou un 304 sans représentation reste inconclusive. Un canonical
présent sur cette destination doit revenir à la même préférence : une autre URL
établit déjà la chaîne interdite, sans collecter son graphe entier.

La comparaison de contenu est une **revue humaine fournie**, jamais un seuil de
similarité calculé. `target.content_review` contient :

- `mode: "manual"`, `reviewer`, `reason`, `observed_at` après les sources/DOM comparés ;
- `source_sha256` : même encodage JSON canonique que ci-dessus, appliqué à
  `{intent: target.intent, context: target.context, documents: target.documents}` ;
- `comparisons` : exactement un `{url, outcome, reason}` par membre, comparé à la
  préférence, avec `outcome` compatible/incompatible/inconclusive.

Toutes les représentations comparées doivent être complètes et attribuables.
Compatible donne pass, incompatible donne fail, jugement absent/indéterminé ou
empreinte périmée donne inconclusive. Le logiciel vérifie le rattachement et la
couverture du jugement ; il n’en vérifie pas la vérité. Les auteurs fictifs des
cas ne sont pas des professionnels sollicités ni une revue indépendante.

### A03 — sitemaps

`intent.canonical.sitemaps` en mode `required` déclare `roots` (URL uniques),
`require_preferred` booléen et `exceptions: [{url, reason}]`. Une préférence non
exigée nécessite `omission_reason`. `target.sitemaps.documents` contient les mêmes
captures datées que ci-dessus. Tous les index et leurs enfants doivent être joints.
Une branche manquante empêche pass et empêche de conclure à une omission ; une
variante concurrente observée et non exemptée reste fail malgré cette lacune.

Le XML accepté est un `urlset` ou `sitemapindex` dans l’espace de noms Sitemaps 0.9,
avec loc et métadonnées simples lastmod/changefreq/priority (lastmod seulement pour
les index). Loc est une URL absolue ; les entités XML ordinaires sont décodées.
DTD, entités déclarées, extensions, compression, redirections de sitemaps et cycles
restent inconclusive. Les URL hors famille ne deviennent pas des défauts de cette
famille. Une entrée préférée exigée et absente donne fail seulement après couverture
complète. Le sous-ensemble ne valide pas tout le protocole Sitemaps.

`mode: "unused"` exige `reason` et `inventory` non vide, plus
`target.sitemaps.absence_review` : reviewer, reason, observed_at, plan_sha256 (du
seul objet sitemaps de l’intention), support avec contenu et SHA-256. Il ne doit
cacher aucune capture de sitemap. Ce record positif donne `not-applicable` à A03
seulement. Un 404, un chemin deviné ou un fichier absent ne le remplace jamais.

### A04 — liens internes

`intent.canonical.links.sources` est une liste non vide de `{url, rendering}`,
unique, de même origine que la préférence dans cette méthode bornée.
`exceptions: [{source, url, reason}]` autorise des destinations précises avec motif.
`target.crawl.documents` conserve les sources réellement examinées ; la différence
avec la population prévue représente les échecs/lacunes. Une capture hors population
reste indéterminée, sans étendre silencieusement le périmètre.

L’interpréteur extrait les href des ancres de la source et des DOM requis, résout
les relatifs contre l’URL finale, enlève le fragment et conserve source/href/destination
dans le motif calculé. Il ne normalise ni paramètres, ni casse, ni slash. Une
destination membre concurrente sans exception donne fail, même si une autre page
manque. Zéro lien vers la famille peut passer seulement après examen de toutes les
pages et états déclarés. Les liens hors famille sont conservés sans verdict sur
leur qualité. `base`, DOM manquant ou récupération HTML nécessaire : inconclusive.

### Preuves de rapport et portée

Le corpus couvre pass/fail/inconclusive pour chaque règle et l’exemption positive
d’A03. `tests/test_canonical_families.py` utilise un **adaptateur de test** pour
produire les observations depuis l’interpréteur, créer les pièces, valider le
rapport et exporter EARL. Il ne fait pas partie d’un collecteur de production.
Les captures HTTP/HTML, l’inventaire/intention/revue, XML et crawl restent conservés
selon leurs types de preuve ; les DOM nécessaires sont conservés en render.

Un C TS10 exige les quatre règles pour chaque famille et toutes leurs preuves.
Une réussite A01 seule, une revue de contenu absente ou un crawl partiel ne suffisent
jamais. Un C automatique reste refusé. NC conserve les inconnues ; A03 NA n’exempte
pas le reste de TS10. Le contrôle reste limité aux familles, populations, contextes
et dates déclarés. Ni canonical choisi par un moteur, ni indexation, ni exhaustivité
du site ne sont déduits.

## English

Draft.5 extends conformance input_version 1 with synthetic raw HTTP/HTML/DOM/XML
inputs for four TS10 rules. No network collection occurs. Expected outcomes remain
separate. A01/A03/A04 stay semiAuto; A02 stays manual even when software runs the
comparison. The existing [common format](conformance.md) still applies to TS01/07.

### Target, intent and captures

A TS10 target is an inventoried family, identified by its preferred URL in
`target.url`. Merge families with the same preferred URL or assess them separately.
`observed_at` ends the assessment interval. `context` has nonempty id, network,
bounds, tool, tool_version. Intent predates every capture/review; all precede the
assessment end. `intent` has declared_at, crawler and `canonical`:

| Field | Shape and meaning |
| --- | --- |
| preferred_url | Absolute HTTP(S) URL without fragment, included in members |
| members | Nonempty unique list of {url, required_methods, rendering} |
| required_methods | Nonempty unique list drawn from html, http, redirect, dom |
| sitemaps | Strategy described below |
| links | Source population and exceptions described below |

No family is inferred from parameters, case, slashes or similarity. A duplicate
may remain 200 and point elsewhere. A required signal absent in complete evidence
fails; missing/ambiguous evidence is inconclusive. Assess all present declarations,
even from methods that were not required.

`target.documents` holds member captures: url, observed_at, context_id, http (raw
ordered hops in the common format). Duplicate captures of a URL are ambiguous;
context must match exactly. `rendering` and `document.render` follow the
[rendered-state format](rendered-states.md): prior states/interactions/waits,
browser/version, date, final URL, context, enabled JavaScript, errors and complete
DOM. Bind each state using source_http_sha256 of the ordered trace encoded as
UTF-8 `json.dumps(http, sort_keys=True, separators=(',', ':'), ensure_ascii=False)`.
This is not a wire-protocol hash. Missing/misattributed states remain inconclusive;
an attributable contradiction survives missing evidence elsewhere.

`{mode: "exempt", basis: "reviewed-stable"}` needs `document.exemption_review`
with basis, reviewer, reason, observed_at, source_http_sha256 and
`support: [{name, content, sha256}]`. Support hashes cover exact UTF-8 content.
The review follows capture and supplies records explaining why no other state is
needed for canonical/link signals. `non-html` supports only text/plain UTF-8 here,
with the same positive record. Review truth/adequacy is not independently checked.

### A01 — declarations

Assess each member's final HTTP Link headers, source HTML and required DOMs.
Explicit HTML needs a properly nested head then body within the common element
subset. A canonical outside head, a different/relative/fragment URL fails the TSEP
criterion. Preserve identical repeated declarations; they can agree. HTTP alone
can suffice without an HTML tag. A required redirect needs a complete chain ending
at the preference. Link fields/lists preserve repetitions, angle-bracket targets
and quoted/plain rel parameters. Duplicate parameters, ambiguous/escaped syntax
or extra canonical context such as anchor are inconclusive. Canonical HTML
attributes beyond rel/href, base, HTML recovery and unsupported media need another
method. Scripts are never executed. Valid syntax outside this bounded subset is
not inherently an SEO defect.

### A02 — destination and human content review

The preferred URL needs a directly attributable 200 GET. An observed redirect
fails even without its continuation; 404/5xx also fail. Truncated exchanges and
304 without representation are inconclusive. A present canonical must point to
that preference; another URL already establishes a forbidden chain without
collecting a whole graph.

`target.content_review` has mode manual, reviewer, reason and observed_at after
compared sources/DOMs. Its source_sha256 binds the JSON object
`{intent: target.intent, context: target.context, documents: target.documents}` using
the encoding above. `comparisons` contains exactly one {url, outcome, reason} per
member, compared with the preference. Outcomes compatible/incompatible/inconclusive
map to pass/fail/inconclusive. All compared representations must be complete and
attributable. Missing judgments or stale hashes are inconclusive. Software checks
binding and coverage, never content similarity or judgment truth. Fixture authors
are synthetic, not contacted professionals or an independent review.

### A03 — sitemap agreement

Required mode declares roots (unique URLs), boolean require_preferred and
exceptions [{url, reason}]. Optional omission requires omission_reason.
`target.sitemaps.documents` retains dated captures of all roots/index children.
Missing branches prevent pass and prevent concluding omission; an observed
unexempted competing family entry still fails. Accepted XML is Sitemaps 0.9 urlset
or sitemapindex with loc and simple lastmod/changefreq/priority metadata (only
lastmod for indexes). Loc is absolute; standard XML escapes are decoded. DTDs,
declared entities, extensions, compression, sitemap redirects and cycles are
inconclusive. Entries outside this family do not fail this family. A missing
required preference fails only after full declared coverage. This is not a full
Sitemaps protocol validator.

Unused mode requires reason, a nonempty inventory and
`target.sitemaps.absence_review`: reviewer, reason, observed_at, plan_sha256 of the
intent's sitemaps object, and support records with content/SHA-256. It must not
hide sitemap captures. This positive record yields not-applicable for A03 only;
a 404, guessed path or absent file never substitutes for it.

### A04 — internal-link agreement

`intent.canonical.links.sources` is a nonempty unique list of {url, rendering},
limited here to the preferred origin. Exceptions [{source, url, reason}] justify
specific destinations. `target.crawl.documents` records examined sources; differences
from planned population retain gaps/failures. Unplanned captures are inconclusive,
without silently expanding scope. Extract anchors from source and required DOMs,
resolve relative hrefs against the final URL and remove fragments; keep source,
href and destination in computed reasons. No parameter/case/slash normalization.
Unexempted competing family links fail even when another source is missing. Zero
family links pass only after every declared page/state is examined. Outside-family
links are retained without a quality claim. Base, missing DOM or HTML recovery
remain inconclusive.

### Report evidence and limits

Cases cover pass/fail/inconclusive for all four rules and positive A03 exemption.
`tests/test_canonical_families.py` uses a test-only adapter: compute outcomes,
retain evidence files, validate the report and export EARL. It is not a production
collector. Keep HTTP/HTML captures, inventory/intent/review, XML and crawl with
their evidence kinds; retain required DOMs as render. C needs all four rules and
their evidence for every family. A01 alone, absent content review or partial crawl
never suffice. Automatic C remains forbidden. NC retains unknowns; A03 NA does
not exempt the whole control. No inference of engine-selected canonical,
indexing, whole-site exhaustiveness or future behavior.

[Google canonical methods](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls),
[Sitemaps protocol](https://www.sitemaps.org/protocol.html),
[RFC 8288](https://www.rfc-editor.org/rfc/rfc8288).
[Captures datées / Dated captures](source-observations.md) · [Migration](migration-draft.5.md).
