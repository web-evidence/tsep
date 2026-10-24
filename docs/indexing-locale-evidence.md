# Indexing investigations and locale methods / Diagnostic d’indexation et langues

Normative profile indexing-locale-v1, reader1,0.3.0-draft.3.
[Shared dossier](evidence-dossier-v1.md), [dated primary references](source-captures/indexing-locale-2026-10-18.md).
No collection, imported verdict acceptance or generated human judgments.
Aucune collecte, acceptation de verdict importé ou revue humaine produite.

## Français — formats et portée

Le dossier commun reste requis. Les plans ci-dessous sont des items déclarés avant
les pièces. Toutes les dates/provenances restent fournies et non authentifiées.
Les exemples `.invalid`, réponses Google rédigées et revues fictives sont
explicitement synthétiques, sans appel Google ni audit réel.

TS21 : item `{id, urls, site_url, reported_state, inspections, sitemap,
sitemap_members, logs, log_start, log_end, diagnosis}` ;1–16 URL uniques.
Inspections=[{url, request, response, http_status}] associe deux records natifs JSON
`search-console` (corps exacts de requête et réponse) et le statut d’acquisition
fourni. Le lecteur request/engine_state historique est réutilisé sans modifier
TS08. Les seules familles lexicales initiales sont « Crawled - currently not
indexed » et « Discovered - currently not indexed » en anglais. Le statut décrit
la version enregistrée, pas un test live ou la cause. Ce profil vérifie une famille
préalablement sélectionnée, étayée par inspections individuelles ; il ne reconstitue
pas le rapport Pages complet ni sa population totale. La revue de segmentation
justifie cette sélection. Les pièces de compte exigent restricted ou synthetic.

Le sitemap est un urlset natif UTF-8 complet. Les logs sont un export TSV fourni,
avec en-tête `timestamp\turl\tstatus\tuser_agent` et0–128 lignes ; tous les événements
sont dans la fenêtre donnée, les statuts sont100–599. L’export est une représentation
fournie et revue des logs, pas une authentification de visite. Zéro ligne n’établit
aucune absence globale. Le record content `family-diagnosis-v1` contient family_id,
urls, diagnosis, hypothesis, prediction, falsification, measurement, decision,
owner, due_date ISO, causality et follow_up. Ce profil admet seulement
causality=unproven, follow_up=planned-not-observed. Le suivi réel requiert une méthode
séparée ; un C qualifie la documentation du diagnostic, pas une correction future.

TS22/TS40 : item `{id, mappings, pages, methods, sitemaps, rendering, destinations}`.
Mappings :1–32 paires code/URL ; pages :1–16 URL uniques présentes dans mappings.
Methods : un à trois noms parmi html, http-link, sitemap ; sitemaps identifie1–16
records lorsque la méthode est utilisée. Rendering=source-only-reviewed : la revue
liée doit justifier la suffisance des sources et l’inventaire des méthodes ; les
cas dépendant du DOM restent NT. Une méthode HTTP/HTML publiée mais omise du plan
est une inconnue. Aucun assemblage de méthodes incomplètes ne crée une réussite.

HTML/HTTP réutilisent les lecteurs natifs TS23. Les deux hypothèses HTML doivent
s’accorder pour qualifier une association ; contexte global inconnu ne prouve pas
l’absence. Les associations indépendantes qualifiées restent comparables malgré
les lacunes. Le XML impose urlset/url/loc du namespace sitemap et xhtml:link avec
exactement rel=alternate, hreflang, href ;1Mio maximum,128 pages et32 annotations
par page. DTD/entities, index, autres extensions et structures ambiguës : NT.
Une omission n’est NC que sur une surface complète ; une capture manquante est NT.

TS22 destinations=[{url,indexing,robots_url,robots_profile}] : une stratégie pour
chaque destination. Indexing=allow attendu ; robots_url est /robots.txt du même
origin, HTTP direct200 dans ce profil. Le profil robots déclaré est un des profils
Google existants ; le lecteur conserve la portée de la représentation reçue par
le client fourni. La canonical HTTP/HTML explicite doit désigner la destination.
Les sources HTML ambiguës ou nécessitant un rendu restent indéterminées.

Le registre figé est lié par empreinte au transport/rejeu. Langue : deux lettres
actuelles ; script optionnel : quatre lettres enregistrées ; région optionnelle :
deux lettres dans le sous-ensemble documenté. Codes inconnus/forme incompatible :
fail ; obsolètes et régions AA/AC/CP/CQ/DG/EA/EZ/IC/TA/XK/ZZ : NT. EU/UN/UK : fail
sur l’effet régional attendu. x-default qualifie seulement le jeton réservé,
sans emprunter le verdict TS24. La syntaxe enregistrée ne détecte ni langue réelle,
qualité de traduction, localisation ou traitement du moteur.

TS40 a pour entrées communes hreflang et intent. Les originaux HTTP/HTML/sitemap
sont exigés conditionnellement par les méthodes déclarées : une méthode HTML seule
n’exige pas de faux fichier sitemap. Cette précision remplace sa liste globale
d’entrées de draft.2. Le validateur de rapports vérifie les types communs et la
couverture ; le lecteur natif vérifie les preuves conditionnelles.

## English — formats and scope

The shared dossier remains required. Plans precede supplied observations; dates
and provenance are not authenticated. Fictional .invalid pages, authored Google
responses and fictional reviews are synthetic, without a Google call or real audit.

TS21 items contain id, urls (1–16 unique), site_url, reported_state, inspections,
sitemap, sitemap_members, logs, log_start, log_end and diagnosis. Inspection entries
{url,request,response,http_status} identify two original JSON search-console records
and supplied acquisition status. Existing request/engine_state readers are reused
without changing TS08. Initial literal English labels are Crawled - currently not
indexed and Discovered - currently not indexed. They concern recorded state, not a
live test or cause. This profile checks a prior selected family backed by individual
inspections; it does not reconstruct the full Pages report or its total population.
Bound segmentation review justifies the selection. Account evidence is restricted
or synthetic.

Sitemap is a complete native UTF8 urlset. Supplied TSV logs have header
timestamp\turl\tstatus\tuser_agent and0–128 rows, events inside the declared window,
statuses100–599. This reviewed log export is not authenticated crawler evidence;
zero rows never prove global absence. The content family-diagnosis-v1 record has
family_id, urls, diagnosis, hypothesis, prediction, falsification, measurement,
decision, owner, ISO due_date, causality and follow_up. This profile admits only
causality=unproven and follow_up=planned-not-observed. Actual follow-up requires a
separate method; C qualifies diagnostic documentation, not a future correction.

TS22/TS40 items have id,mappings,pages,methods,sitemaps,rendering,destinations.
Mappings contain1–32 code/URL pairs;1–16 unique pages occur in mappings. Methods
select one to three of html,http-link,sitemap; sitemap use requires1–16 explicit
native records. Rendering=source-only-reviewed requires bound review justifying
source sufficiency and method inventory; DOM-dependent cases remain NT. Published
HTTP/HTML methods omitted from the plan are unknown. Partial methods are never
merged into a successful complete set.

HTML/HTTP reuse native TS23 readers. Both static HTML hypotheses must agree to
qualify an association; global ambiguity cannot prove absence. Qualified independent
mappings remain comparable despite gaps. XML requires sitemap urlset/url/loc and
xhtml:link with exactly rel=alternate, hreflang,href; at most1MiB,128 pages and32
annotations/page. DTD/entities,indexes,other extensions/ambiguity are NT. Omission
is NC only on a complete surface; missing capture is NT.

TS22 destinations each specify url,indexing,robots_url,robots_profile. Expected
indexing=allow; same-origin /robots.txt must be direct200 under a declared existing
Google profile. The result concerns the supplied client's representation. Explicit
HTTP/HTML canonicals must point to the destination. Ambiguous/render-dependent HTML
is inconclusive.

The frozen registry is fingerprinted in transport/replay. Current two-letter
language, optional registered four-letter script and optional two-letter region
from the bounded subset are checked. Unknown/incompatible tokens fail; deprecated
entries and AA/AC/CP/CQ/DG/EA/EZ/IC/TA/XK/ZZ regions are NT; EU/UN/UK fail the expected
regional effect. x-default qualifies only its reserved token, borrowing no TS24
outcome. Registered syntax establishes no actual language, translation quality,
localization or engine processing.

TS40 common inputs are hreflang and intent. Native HTTP/HTML/sitemap evidence is
conditional on declared methods; HTML-only use requires no invented sitemap.
This explicitly replaces the draft.2 unconditional input list. Report validation
checks common kinds/coverage; the native reader checks conditional evidence.

## TS21-A01

### Français

**Attribution des familles non indexées**

Entrées : search-console, logs, sitemap, intent.

**Périmètre** — Familles ou groupes explicitement sélectionnés pour TS21 ; profil indexing-locale-v1, docs/indexing-locale-evidence.md.

**Procédure** — Lire les requêtes/réponses Google URL Inspection fournies pour chaque URL retenue, comparer propriété, URL et libellé de famille ; rapprocher le urlset natif et l’export TSV de logs dans leur fenêtre. Exiger la revue de segmentation et d’attribution.

**Attendus** — Les pièces natives sont disponibles et attribuées à la famille choisie ; l’appartenance sitemap concorde avec le plan. Un désaccord de requête, de famille ou de sitemap échoue. Les logs décrivent seulement leur fenêtre et leur client fourni.

**Preuves** — Plan préalable, originaux exacts, empreintes, dates/contexte, observations et revue motivée liée à tout le dossier. Types minimaux : search-console, logs, sitemap, intent. Preuves natives conditionnelles selon les méthodes déclarées.

**Hypothèses** — Périmètre, provenance, segmentation et revues fournis, non authentifiés. Deux hypothèses HTML statiques ne sont pas deux navigations. Les codes figés ne prédisent pas le traitement du moteur.

**Indéterminés** — Pièce manquante, résultat API absent/erroné, libellé non pris en charge, logs non interprétables ou revue absente : indéterminé.

**Non-applicabilité** — Pas d’exemption atomique. Une population vide, Google non évalué ou un groupe non observé reste NT dans ce profil.

**Limites** — Lecture hors ligne de pièces fournies ; ni origine Google, identité humaine ou visite de robot authentifiée, ni état actuel de l’index, causalité, qualité de traduction, ciblage ou conformité globale établis.

### English

**Attribution of nonindexed families**

Inputs: search-console, logs, sitemap, intent.

**Scope** — Explicitly selected TS21 families or clusters; indexing-locale-v1, docs/indexing-locale-evidence.md.

**Procedure** — Read supplied Google URL Inspection requests/responses for each selected URL, compare property, URL and family label; reconcile native urlset and TSV log export in their declared window. Require segmentation/attribution review.

**Expectations** — Native pieces are available and attributed to the selected family; sitemap membership agrees with the plan. Request, family-label or sitemap disagreement fails. Logs describe only their supplied window and client.

**Evidence** — Prior plan, exact originals, fingerprints, dates/context, observations and reasoned review bound to the whole dossier. Minimum kinds: search-console, logs, sitemap, intent. Conditional native evidence follows declared methods.

**Assumptions** — Supplied unauthenticated scope, provenance, segmentation and reviews. Two static HTML hypotheses are not two navigations. Frozen codes do not predict engine processing.

**Inconclusive** — Missing evidence, absent/error API result, unsupported label, uninterpretable logs or absent review: inconclusive.

**Non-applicability** — No atomic exemption. Empty population, unassessed Google or an unobserved cluster remains NT in this profile.

**Limitations** — Offline reading of supplied evidence; no authenticated Google origin, human identity or crawler visit; no current index state, causality, translation quality, targeting or global conformity established.

## TS21-A02

### Français

**Hypothèse testable et décision sans causalité inventée**

Entrées : content, intent.

**Périmètre** — Familles ou groupes explicitement sélectionnés pour TS21 ; profil indexing-locale-v1, docs/indexing-locale-evidence.md.

**Procédure** — Lire family-diagnosis-v1 : diagnostic, hypothèse, prédiction, réfutation, mesure, décision, propriétaire et échéance pour la même liste d’URL. Vérifier la distinction entre suivi prévu et résultat observé puis la revue liée.

**Attendus** — Les axes de diagnostic sont renseignés et revus ; causality=unproven et follow_up=planned-not-observed. Une causalité proclamée à partir du libellé ou de la corrélation échoue dans ce profil.

**Preuves** — Plan préalable, originaux exacts, empreintes, dates/contexte, observations et revue motivée liée à tout le dossier. Types minimaux : content, intent. Preuves natives conditionnelles selon les méthodes déclarées.

**Hypothèses** — Périmètre, provenance, segmentation et revues fournis, non authentifiés. Deux hypothèses HTML statiques ne sont pas deux navigations. Les codes figés ne prédisent pas le traitement du moteur.

**Indéterminés** — Hypothèse sans critère de réfutation, famille mal attribuée, suivi prétendu observé hors méthode séparée, jugement manquant : indéterminé.

**Non-applicabilité** — Pas d’exemption atomique. Une population vide, Google non évalué ou un groupe non observé reste NT dans ce profil.

**Limites** — Lecture hors ligne de pièces fournies ; ni origine Google, identité humaine ou visite de robot authentifiée, ni état actuel de l’index, causalité, qualité de traduction, ciblage ou conformité globale établis.

### English

**Testable hypothesis and decision without invented causality**

Inputs: content, intent.

**Scope** — Explicitly selected TS21 families or clusters; indexing-locale-v1, docs/indexing-locale-evidence.md.

**Procedure** — Read family-diagnosis-v1: diagnosis, hypothesis, prediction, falsification, measurement, decision, owner and due date for the same URL list. Check planned-versus-observed follow-up and bound review.

**Expectations** — Diagnostic axes are supplied and reviewed; causality=unproven and follow_up=planned-not-observed. Declaring causality from a label or correlation fails this profile.

**Evidence** — Prior plan, exact originals, fingerprints, dates/context, observations and reasoned review bound to the whole dossier. Minimum kinds: content, intent. Conditional native evidence follows declared methods.

**Assumptions** — Supplied unauthenticated scope, provenance, segmentation and reviews. Two static HTML hypotheses are not two navigations. Frozen codes do not predict engine processing.

**Inconclusive** — Hypothesis without falsification, misattributed family, claimed observed follow-up outside a separate method or missing judgment: inconclusive.

**Non-applicability** — No atomic exemption. Empty population, unassessed Google or an unobserved cluster remains NT in this profile.

**Limitations** — Offline reading of supplied evidence; no authenticated Google origin, human identity or crawler visit; no current index state, causality, translation quality, targeting or global conformity established.

## TS22-A01

### Français

**Annotations natives et codes enregistrés**

Entrées : hreflang, http, html, intent.

**Périmètre** — Familles ou groupes explicitement sélectionnés pour TS22 ; profil indexing-locale-v1, docs/indexing-locale-evidence.md.

**Procédure** — Lire séparément HTML, en-têtes Link et urlset XHTML déclarés ; conserver les accords des deux hypothèses HTML statiques. Vérifier chaque code observé dans le sous-ensemble figé du registre IANA et l’attribution à la destination prévue.

**Attendus** — Les codes observés appartiennent au profil langue/script/région documenté et les destinations concordent. Un code explicitement invalide ou une destination contraire échoue ; x-default qualifie seulement le jeton réservé.

**Preuves** — Plan préalable, originaux exacts, empreintes, dates/contexte, observations et revue motivée liée à tout le dossier. Types minimaux : hreflang, http, html, intent. Preuves natives conditionnelles selon les méthodes déclarées.

**Hypothèses** — Périmètre, provenance, segmentation et revues fournis, non authentifiés. Deux hypothèses HTML statiques ne sont pas deux navigations. Les codes figés ne prédisent pas le traitement du moteur.

**Indéterminés** — Code obsolète, région exceptionnelle hors sous-ensemble, méthode ou page manquante, contexte HTML ambigu, annotation relative ou revue manquante : indéterminé.

**Non-applicabilité** — Pas d’exemption atomique. Une population vide, Google non évalué ou un groupe non observé reste NT dans ce profil.

**Limites** — Lecture hors ligne de pièces fournies ; ni origine Google, identité humaine ou visite de robot authentifiée, ni état actuel de l’index, causalité, qualité de traduction, ciblage ou conformité globale établis.

### English

**Native annotations and registered codes**

Inputs: hreflang, http, html, intent.

**Scope** — Explicitly selected TS22 families or clusters; indexing-locale-v1, docs/indexing-locale-evidence.md.

**Procedure** — Read declared HTML, Link headers and XHTML urlsets separately; retain agreement of both static HTML hypotheses. Check each observed code against the frozen IANA registry subset and attribution to its planned destination.

**Expectations** — Observed codes belong to the documented language/script/region profile and destinations agree. An explicitly invalid code or conflicting destination fails; x-default qualifies only the reserved token.

**Evidence** — Prior plan, exact originals, fingerprints, dates/context, observations and reasoned review bound to the whole dossier. Minimum kinds: hreflang, http, html, intent. Conditional native evidence follows declared methods.

**Assumptions** — Supplied unauthenticated scope, provenance, segmentation and reviews. Two static HTML hypotheses are not two navigations. Frozen codes do not predict engine processing.

**Inconclusive** — Deprecated code, exceptional region outside the subset, missing method/page, ambiguous HTML, relative annotation or absent review: inconclusive.

**Non-applicability** — No atomic exemption. Empty population, unassessed Google or an unobserved cluster remains NT in this profile.

**Limitations** — Offline reading of supplied evidence; no authenticated Google origin, human identity or crawler visit; no current index state, causality, translation quality, targeting or global conformity established.

## TS22-A02

### Français

**Destinations hreflang et signaux d’indexabilité**

Entrées : hreflang, http, html, robots, intent.

**Périmètre** — Familles ou groupes explicitement sélectionnés pour TS22 ; profil indexing-locale-v1, docs/indexing-locale-evidence.md.

**Procédure** — Pour chaque destination sélectionnée : comparer intention d’indexation, HTTP direct 200, directives HTTP/HTML, canonical explicite vers elle-même et robots.txt du même origin avec le profil Google préalable. Exiger la revue du périmètre source.

**Attendus** — Les signaux qualifiés autorisent la destination prévue et concordent avec elle. Une réponse contraire, un noindex, une canonical divergente ou un refus robots étayé échoue malgré d’autres inconnues.

**Preuves** — Plan préalable, originaux exacts, empreintes, dates/contexte, observations et revue motivée liée à tout le dossier. Types minimaux : hreflang, http, html, robots, intent. Preuves natives conditionnelles selon les méthodes déclarées.

**Hypothèses** — Périmètre, provenance, segmentation et revues fournis, non authentifiés. Deux hypothèses HTML statiques ne sont pas deux navigations. Les codes figés ne prédisent pas le traitement du moteur.

**Indéterminés** — Robots absent/non qualifié, canonical absente, trace partielle, rendu nécessaire ou revue absente : indéterminé. Permission d’indexation n’est pas indexation.

**Non-applicabilité** — Pas d’exemption atomique. Une population vide, Google non évalué ou un groupe non observé reste NT dans ce profil.

**Limites** — Lecture hors ligne de pièces fournies ; ni origine Google, identité humaine ou visite de robot authentifiée, ni état actuel de l’index, causalité, qualité de traduction, ciblage ou conformité globale établis.

### English

**Hreflang destinations and indexing-permission signals**

Inputs: hreflang, http, html, robots, intent.

**Scope** — Explicitly selected TS22 families or clusters; indexing-locale-v1, docs/indexing-locale-evidence.md.

**Procedure** — For every selected destination compare indexing intent, direct HTTP200, HTTP/HTML directives, explicit self-canonical and same-origin robots.txt under the prior Google profile. Require source-scope review.

**Expectations** — Qualified signals permit and agree with the planned destination. A conflicting response, noindex, divergent canonical or evidenced robots denial fails despite other unknowns.

**Evidence** — Prior plan, exact originals, fingerprints, dates/context, observations and reasoned review bound to the whole dossier. Minimum kinds: hreflang, http, html, robots, intent. Conditional native evidence follows declared methods.

**Assumptions** — Supplied unauthenticated scope, provenance, segmentation and reviews. Two static HTML hypotheses are not two navigations. Frozen codes do not predict engine processing.

**Inconclusive** — Missing/unqualified robots, absent canonical, partial trace, required rendering or absent review: inconclusive. Indexing permission is not indexing.

**Non-applicability** — No atomic exemption. Empty population, unassessed Google or an unobserved cluster remains NT in this profile.

**Limitations** — Offline reading of supplied evidence; no authenticated Google origin, human identity or crawler visit; no current index state, causality, translation quality, targeting or global conformity established.

## TS40-A01

### Français

**Complétude indépendante des méthodes publiées**

Entrées : hreflang, intent.

**Périmètre** — Familles ou groupes explicitement sélectionnés pour TS40 ; profil indexing-locale-v1, docs/indexing-locale-evidence.md.

**Procédure** — Inventorier les méthodes avant capture ; lire chaque méthode/page séparément et vérifier tout le groupe attendu, auto-référence comprise. Une méthode secondaire ne complète pas une primaire partielle.

**Attendus** — Chaque méthode complète contient les associations prévues. Une omission démontrée dans une surface complète ou une destination contraire échoue ; un jeu unique de méthodes est autorisé.

**Preuves** — Plan préalable, originaux exacts, empreintes, dates/contexte, observations et revue motivée liée à tout le dossier. Types minimaux : hreflang, intent. Preuves natives conditionnelles selon les méthodes déclarées.

**Hypothèses** — Périmètre, provenance, segmentation et revues fournis, non authentifiés. Deux hypothèses HTML statiques ne sont pas deux navigations. Les codes figés ne prédisent pas le traitement du moteur.

**Indéterminés** — Capture/méthode absente, XML tronqué/index, méthode publiée omise du plan, association hors groupe ou revue absente : indéterminé.

**Non-applicabilité** — Pas d’exemption atomique. Une population vide, Google non évalué ou un groupe non observé reste NT dans ce profil.

**Limites** — Lecture hors ligne de pièces fournies ; ni origine Google, identité humaine ou visite de robot authentifiée, ni état actuel de l’index, causalité, qualité de traduction, ciblage ou conformité globale établis.

### English

**Independent completeness of published methods**

Inputs: hreflang, intent.

**Scope** — Explicitly selected TS40 families or clusters; indexing-locale-v1, docs/indexing-locale-evidence.md.

**Procedure** — Inventory methods before capture; read every method/page independently and check the complete expected group including self-reference. A secondary method does not complete a partial primary one.

**Expectations** — Each complete method contains the expected mappings. Demonstrated omission on a complete surface or a conflicting destination fails; one chosen method is allowed.

**Evidence** — Prior plan, exact originals, fingerprints, dates/context, observations and reasoned review bound to the whole dossier. Minimum kinds: hreflang, intent. Conditional native evidence follows declared methods.

**Assumptions** — Supplied unauthenticated scope, provenance, segmentation and reviews. Two static HTML hypotheses are not two navigations. Frozen codes do not predict engine processing.

**Inconclusive** — Missing capture/method, truncated/index XML, published method omitted from plan, outside-group mapping or absent review: inconclusive.

**Non-applicability** — No atomic exemption. Empty population, unassessed Google or an unobserved cluster remains NT in this profile.

**Limitations** — Offline reading of supplied evidence; no authenticated Google origin, human identity or crawler visit; no current index state, causality, translation quality, targeting or global conformity established.

## TS40-A02

### Français

**Cohérence des méthodes et des pages du groupe**

Entrées : hreflang, intent.

**Périmètre** — Familles ou groupes explicitement sélectionnés pour TS40 ; profil indexing-locale-v1, docs/indexing-locale-evidence.md.

**Procédure** — Comparer les associations qualifiées entre méthodes/pages sans fusionner leurs jeux. Conserver un conflit de destination indépendant même si une troisième méthode manque ; comparer l’égalité des jeux quand les deux sont complets.

**Attendus** — Les méthodes complètes et les pages concordent. Une seule méthode complète est admise. Un conflit natif ou une différence de jeux complets échoue.

**Preuves** — Plan préalable, originaux exacts, empreintes, dates/contexte, observations et revue motivée liée à tout le dossier. Types minimaux : hreflang, intent. Preuves natives conditionnelles selon les méthodes déclarées.

**Hypothèses** — Périmètre, provenance, segmentation et revues fournis, non authentifiés. Deux hypothèses HTML statiques ne sont pas deux navigations. Les codes figés ne prédisent pas le traitement du moteur.

**Indéterminés** — Comparaison sans surface qualifiée, capture partielle, méthode manquante ou revue absente : indéterminé, sauf contradiction indépendante établie.

**Non-applicabilité** — Pas d’exemption atomique. Une population vide, Google non évalué ou un groupe non observé reste NT dans ce profil.

**Limites** — Lecture hors ligne de pièces fournies ; ni origine Google, identité humaine ou visite de robot authentifiée, ni état actuel de l’index, causalité, qualité de traduction, ciblage ou conformité globale établis.

### English

**Consistency across methods and cluster pages**

Inputs: hreflang, intent.

**Scope** — Explicitly selected TS40 families or clusters; indexing-locale-v1, docs/indexing-locale-evidence.md.

**Procedure** — Compare qualified mappings across methods/pages without merging their sets. Retain independent destination conflicts even when a third method is missing; compare set equality when both are complete.

**Expectations** — Complete methods and pages agree. One complete method is allowed. A native conflict or differing complete sets fails.

**Evidence** — Prior plan, exact originals, fingerprints, dates/context, observations and reasoned review bound to the whole dossier. Minimum kinds: hreflang, intent. Conditional native evidence follows declared methods.

**Assumptions** — Supplied unauthenticated scope, provenance, segmentation and reviews. Two static HTML hypotheses are not two navigations. Frozen codes do not predict engine processing.

**Inconclusive** — Comparison without a qualified surface, partial capture, missing method or absent review: inconclusive unless an independent contradiction is established.

**Non-applicability** — No atomic exemption. Empty population, unassessed Google or an unobserved cluster remains NT in this profile.

**Limitations** — Offline reading of supplied evidence; no authenticated Google origin, human identity or crawler visit; no current index state, causality, translation quality, targeting or global conformity established.

