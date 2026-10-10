# Change history / Historique

## Noscript experiment 4 — 2026-10-10 — unapplied explicit-table coverage

Add explicit table/caption/column-group/section/row/cell grammar, with all closing
tags required. Preserve text boundaries and reject fostered text, direct rows,
nested tables and unsupported section order. Freeze 103 authored cases before
implementation; retain all earlier fixture bytes with one explicit v3 expectation
delta for an empty table. No normative or active interpreter change.

Ajout des tableaux explicites, bornés et correctement imbriqués ; textes mal
placés, sections implicites, tableaux imbriqués et fermetures omises restent
refusés. 103 cas figés avant code et un seul écart antérieur explicite ; aucun
changement normatif ni de l'interpréteur actif. [Portée](docs/table-experiment-v4.md).

## Noscript experiment 3 — 2026-10-10 — unapplied form-control coverage

Add strictly balanced select/optgroup/option and literally empty textarea to the
isolated experiment. Freeze 96 authored cases before implementation; preserve
v1/v2 files and record the one changed v1 expectation explicitly. Option attributes,
selection and visibility do not supply source text. Refuse complex children,
omitted closes and nonempty textarea. No protocol, active interpreter or report
migration. Compare synthetic inputs with an isolated historical external parser;
retain CRLF and candidate disagreements rather than claim browser equivalence.

Extension expérimentale bornée des listes et textarea littéralement vide ; 96 cas
figés avant code, fichiers v1/v2 conservés et un changement d'attente explicite.
Tous les textes d'option comptent, pas les attributs ni l'état de sélection.
Les refus et écarts avec un parseur historique externe restent visibles. Aucun
changement normatif ni migration des rapports. [Portée](docs/noscript-experiment.md).

## Noscript experiment 2 — 2026-10-10 — unapplied coverage correction

The first retained-page reapplication exposed an overbroad ancestor-li guard.
Allow a nested ul/ol/menu to create its own list-item scope; keep unclosed items
within the same scope refused. Six counterexamples were frozen before this fix.
Keep all 68 initial expectations and the v1 observations; no normative change.

La première réapplication a révélé un refus excessif des li dans une liste imbriquée
valide. ul/ol/menu crée désormais sa propre portée ; un li non fermé dans la même
portée reste refusé. Six cas figés avant correctif, 68 attentes initiales et
résultats v1 conservés. Aucun changement du protocole ou de l’interpréteur actif.

## Noscript experiment 1 — 2026-10-10 — unapplied local experiment

Freeze 68 authored whole-document cases before implementing two global lexical
noscript hypotheses. Retain source ranges, per-reading marker evidence and
candidate agreement; incomplete readings never contribute a prefix. Standalone
CLI, no normative evaluator dependency, no report or HTTP identity verdict.
Active interpreter 5, draft.7, all prior tools/cases and their outcomes are unchanged.
The experiment is not an HTML5 tree-construction oracle. [Scope](docs/noscript-experiment.md).

68 documents synthétiques figés avant le prototype : deux hypothèses globales,
positions source, preuves de marqueurs et concordance candidate. Aucun préfixe
accepté si une lecture reste incomplète, aucun verdict TSEP. Interpréteur 5,
draft.7 et outils antérieurs inchangés. Lectures lexicales bornées, pas une preuve
générale du comportement d’un navigateur ; aucune promotion normative.

## Collector 6, preflight 2 and campaign diagnostic 1 — 2026-10-10 — local development

Compare two registered capture phases without TSEP outcomes: decoded-byte
changes, per-page non-exhaustive construction inventory and complete source
extraction availability or first refusal. Verify manifests, raw/JSON binding,
settings, ordering, timestamps and source continuity. Signal Content-Type removal
or addition when both responses are available. Interpreter 5, adapter 6, intent 3,
HTML 4 and draft.7 stay unchanged. A bilingual noscript consensus proposal is
explicitly unapplied; select coverage is not extended. [Scope](docs/diagnostic-campaign.md).

Comparaison diagnostique de deux phases préenregistrées, sans verdict : octets
décodés, inventaire non exhaustif par page, extraction complète ou premier refus.
Empreintes, correspondance JSON/brut, réglages, ordre, dates et sources vérifiés.
Ajout/retrait de Content-Type signalé quand les réponses sont disponibles.
Protocole draft.7 et interpréteur 5 inchangés ; proposition noscript bilingue non
appliquée. Aucun changement de couverture select, publication ou nouvelle CI distante.

## Interpreter 5, adapter 6 and collector 5 — 2026-10-10 — local development

Extend SVG style exclusion only within the bounded icon subset: explicit body,
no literal `<` before the closing tag. Reject markup even inside CSS strings or
comments; whole extraction stays inconclusive for ambiguity. Freeze 51 additional
synthetic cases before implementation; preserve all v4 expectations. Nonempty
noscript stays unresolved because scripting mode is not specified. No normative,
TS07/TS10, report-format or corpus change. Diagnostic 1 remains explicitly tied
to interpreter 4 coverage. [Scope and migration](docs/source-text-v5.md).

Exclusion bornée des styles SVG, dans un body explicite, sans `<` littéral avant
fermeture. Le balisage, même dans une chaîne CSS, garde toute l’extraction
indéterminée. 51 nouveaux cas figés avant implémentation ; attentes v4 conservées.
Noscript non vide reste indéterminé, faute de mode scripting précisé au contrat.
Interpréteur 5, adaptateur 6, collecteur 5 ; protocole draft.7, TS07/TS10, formats
et corpus inchangés. Aucune publication ni nouvelle CI distante revendiquée.

## Collector 4, HTML 4 and diagnostic 1 — 2026-10-10 — local development

Add a separate offline HTML construction inventory with no TSEP outcomes. It
continues beyond the first candidate limitation and records runtime/input hashes,
with explicit non-exhaustiveness and sample-only counts. Collector 4 preflights
markers on retained references before sealing: contradictions refuse the seal;
unsupported extraction remains a visible warning. Guided intent 3 records and
rechecks preparation before network evaluation. HTML 4 displays these supplied
checks and raw Content-Type differences without changing outcomes. Interpreter 4,
adapter 5, protocol draft.7, contracts and corpus remain unchanged. Old archives
are retained. [Scope and migration](docs/reference-diagnostics.md).

Inventaire HTML hors ligne distinct, sans résultat TSEP : poursuite après la
première limite candidate, empreintes et runtime déclarés, comptage limité à
l’échantillon et absence de garantie d’exhaustivité. Le collecteur 4 précontrôle
les marqueurs de la référence avant scellement : contradiction refusée, extraction
indisponible signalée. Intention guidée 3, revérifiée avant le réseau. HTML 4
présente ces contrôles préparatoires et les écarts bruts de Content-Type sans
changer les résultats. Interpréteur 4, adaptateur 5, draft.7, contrats et corpus
inchangés. Anciennes archives conservées ; aucune publication ni CI distante nouvelle.


## Interpreter 4, adapter 5 and collector 3 — 2026-10-10 — local development

Separate bounded TS01 source-text extraction from the unchanged TS07 parser.
Freeze 96 synthetic counterexamples and 312 selected upstream character-reference
expectations before implementation. Preserve numeric characters Python unescape
would drop. Unsupported regions remain wholly inconclusive. Record selected
Python HTML dependency hashes and disclose runtime differences on replay.
Draft.7, its contract/fingerprint, 216 normative cases, binary input 2 and HTML 3
remain unchanged. [Scope and migration](docs/source-text-v4.md). No public release
or new remote CI execution is claimed.

Extraction bornée TS01 distincte du parseur TS07 inchangé. 96 contre-exemples
synthétiques et 312 attentes externes de références de caractères figés avant
implémentation. Caractères numériques conservés même lorsque Python unescape les
supprimerait. Zone non prise en charge : extraction entière indéterminée.
Empreintes des dépendances HTML de Python enregistrées ; différences de runtime
signalées au rejeu. Draft.7, contrat/empreinte, 216 cas normatifs, entrée binaire 2
et HTML 3 inchangés. Aucune publication ni nouvelle CI distante revendiquée.


## Collector 2, adapter 4 and HTML 3 — 2026-10-10 — local development

Guard collector source equality before sealing/evaluation and verify loaded local
module origins against the inventoried tool root. Retain raw attempts if source
files change during collection. Guided intent v2 records criteria provenance;
optional declared final URLs must match the reference. Display criteria beside
TS01 results and state that supplied runs are not exhaustive. Add negative TLS,
mixed-import, source-change and two-phase byte-budget tests. New reference/intent
required with collector 2; preserve old tool archives for historical replay.
Interpreter 3, draft.7, normative corpus and report contracts remain unchanged.

Vérification du collecteur identique avant scellement/mesure et des origines des
modules locaux inventoriés. Tentatives brutes conservées si les sources changent.
Intention guidée v2 avec origine des critères et URL finale déclarée facultative,
contrôlée contre la référence. Critères visibles près des résultats TS01 et
périmètre des exécutions explicite. Tests TLS négatif, imports incohérents, sources
modifiées et budget des deux phases. Nouvelle référence/intention requise avec le
collecteur 2 ; anciennes archives préservées pour le rejeu. Interpréteur 3,
draft.7, corpus normatif et contrats inchangés. Voir [migration](docs/guided-capture.md).

## Binary tools 3, guided collector 1 and HTML 2 — 2026-10-10 — local development

Add exact-byte input v2 alongside unchanged legacy v1, bounded gzip and zlib-deflate
decoding, and a supervised anonymous HTTP/1.1 collector. Reference → frozen intent
→ evaluation → offline replay retains raw attempts, failures and source hashes.
HTML 2 adds raw binary downloads, adjacent decision scope and declared coverage.
Add contradictory binary/loopback workflow tests and a prepared consumer CI example.
No normative change: draft.7, fingerprints, report contract, 216 cases and gate
policy remain unchanged. No public release or new remote CI result is claimed.

Ajout de l’entrée binaire v2, v1 historique conservée, décodage gzip/deflate-zlib
borné et collecteur HTTP/1.1 anonyme supervisé. Référence → intention figée → mesure
→ rejeu hors ligne : octets, tentatives, échecs et empreintes de sources conservés.
HTML 2 ajoute téléchargement binaire, périmètre adjacent à la décision et couverture
déclarée. Tests contradictoires binaires/parcours loopback et exemple CI consommateur
préparé. Aucun changement normatif : draft.7, empreintes, contrat de rapport,
216 cas et décision inchangés. Aucune publication ni nouvelle CI distante déclarée.

## Tool coverage 2 and HTML reports — 2026-10-10 — local development

The reference interpreter and captures adapter advance to tool version 2 with
bounded HTTP/1.1 chunked decoding. Preserve decoded content bytes; malformed,
ambiguous, compressed, extended or trailer-bearing captures remain inconclusive.
Add the standalone bilingual HTML report engine version 1, embedded original
evidence and optional comparison of retained reports. Add contradictory transfer
tests and presentation integrity/portability tests. Document migration and limits.
Protocol draft.7, normative fingerprints, report/input formats, the 216-case
corpus and gate policy remain unchanged. No publication or new remote CI run is
claimed. The earlier pilot baseline remains historical, not this new tool revision.

L’interpréteur et l’adaptateur de captures passent en version d’outil 2 avec
décodage HTTP/1.1 chunked borné. Octets du contenu préservés ; troncatures,
ambiguïtés, compression, extensions et trailers restent indéterminés. Ajout du
moteur de rapport HTML bilingue version 1, preuves originales embarquées et
comparaison facultative de rapports conservés. Tests contradictoires du transfert,
intégrité/portabilité de la présentation, migration et limites documentées.
Contrat draft.7, empreintes normatives, formats, corpus de 216 cas et décision
inchangés. Aucune publication ni nouvelle CI distante déclarée. La base du pilote
précédent reste une référence historique, distincte de cette révision de l’outil.

## TS01 pilot kit — 2026-10-09

Add a bilingual pilot plan, an explicitly unactivated registration template and
implementation/ambiguity issue templates and a manifest of the unchanged technical
baseline, verifiable without Git. Link the kit from both READMEs and
include it in the explicit distribution inventory. The technical baseline is
824c48b; protocol draft.7, executable tools, corpus and decision rules are unchanged.
This documentation is not an external implementation, a human review or an
adoption result. Participant, funding and dates remain to be agreed before activation.
CITATION.cff includes the actually reserved version DOI 10.5281/zenodo.23268700
with an explicit publication condition; reservation alone is not registration.

Ajout du plan pilote bilingue, d’un modèle d’activation explicitement non activé
et de modèles d’issues implémentation/ambiguïté, avec manifeste de la base technique
inchangée vérifiable sans Git. Liens depuis les deux README et
ajout à l’inventaire explicite de distribution. Base technique 824c48b ; protocole
draft.7, outils exécutables, corpus et règles de décision inchangés. Ces documents
ne constituent ni une implémentation extérieure, ni une revue humaine, ni une
adoption. Participant, financement et dates restent à convenir avant activation.
CITATION.cff contient le DOI de version effectivement réservé 10.5281/zenodo.23268700,
sous condition explicite de publication ; sa réservation seule n’est pas un enregistrement.

## Public repository access — 2026-10-09

Open `web-evidence/tsep` to public reading and contributions. Align the EN/FR
README, development, governance and contribution guidance with that access;
add the repository URL to `CITATION.cff`. Keep the first CI run's measured results
and commit scope as historical evidence, with a link to later workflow runs.
Protocol draft.7, licenses, decision rules and the initial tag are unchanged.
Public access does not establish a stable release, adoption or independent review.

Ouverture de `web-evidence/tsep` à la consultation et aux contributions publiques.
README, développement, gouvernance et contribution alignés en FR/EN ; URL du dépôt
ajoutée à `CITATION.cff`. Résultats mesurés et portée du commit de la première CI
conservés comme preuves historiques, avec lien vers les runs suivants.
Protocole draft.7, licences, règles de décision et tag initial inchangés.
L’accès public n’établit ni version stable, ni adoption, ni revue indépendante.

## Repository and observed CI — 2026-10-09 — unpublished documentation

Link the private Web Evidence repository and the first successful remote CI run
on `253b0a1` from `README.md`, `README.fr.md` and `docs/development.md`. Record its
scope, measured environments, restricted access, archive and log checksums and
log retention; distinguish that tested revision from this documentation update.
Clarify hosting, Edikka stewardship and organization administration in
`GOVERNANCE.md`; update the public-access comment in `CITATION.cff`.
Protocol draft.7, licenses, decision rules and historical tags are unchanged.
This entry does not claim public access or independent practitioner review.

`README.md`, `README.fr.md` et `docs/development.md` reliés au dépôt privé Web Evidence
et à la première CI distante réussie sur `253b0a1`. Portée, environnements mesurés,
accès restreint, empreintes et rétention des journaux consignés ; révision testée
distinguée de cette mise à jour documentaire. Hébergement, responsabilité Edikka
et administration de l’organisation clarifiés dans `GOVERNANCE.md` ; commentaire
sur l’accès public actualisé dans `CITATION.cff`. Protocole draft.7, licences,
règles de décision et tags historiques inchangés ; aucune ouverture publique ni revue
indépendante de praticiens déclarée acquise.

## Contributor guidance — 2026-10-09 — unpublished documentation

R-028: rewrite contributor instructions in English without private infrastructure
requirements; use descriptive `feat/`, `fix/`, `docs/`, `test/` and `chore/` branches.
Align the development guide in English and French. Packaging exclusions and
protocol draft.7 are unchanged. No remote repository or CI run created.

R-028 : instructions de contribution génériques en anglais, branches descriptives
neutres et guide de développement aligné FR/EN. Exclusions de distribution et
contrat draft.7 inchangés. Aucun dépôt distant ni lancement de CI effectué.

## Verification runtime — 2026-10-09 — unpublished development tooling

R-027: sample 15 contradictory cases for external-adapter CLI tests, including
wrong verdicts and extra rows; retain the full 216-case conformance checks.
Make the 120-second per-step deadline configurable with
`TSEP_VERIFY_STEP_TIMEOUT`, with explicit timeout diagnostics. Protocol draft.7,
corpus, report and decision semantics unchanged; no remote CI execution claimed.

R-027 : 15 cas contradictoires pour le test CLI externe, erreurs et lignes en trop
conservées ; conformance complète maintenue. Délai de 120 s par étape configurable,
dépassements explicites. Contrat draft.7 et corpus inchangés ; aucune CI distante
déclarée exécutée. [Vérification FR/EN](docs/development.md).

## 0.1.0-draft.7 — 2026-10-09 — unpublished development candidate

R-024: changed-body identity requires at least one positive required marker;
absent forbidden-only markers remain inconclusive. R-026: HTML markers use source
text excluding comments, script/style and attributes, with explicit extraction
boundaries and limits. R-025: `conformance/run.py --rules` tests a declared subset
and reports omitted rules/pairs separately. Wrong or extra results still fail.
Nineteen new contradictory cases, FR/EN contracts and migration. IDs, format 2,
automation and gate policy unchanged. [Migration](docs/migration-draft.7.md).

R-024 : interdits seuls absents → inconclusive ; un requis est nécessaire au pass
sur variation. R-026 : texte source extrait, sans commentaires, script/style ni
attributs, limites explicites. R-025 : sous-ensemble de conformance déclaré par
`--rules`, omissions visibles, aucun contrôle partiel promu C. Dix-neuf nouveaux
cas contradictoires et migration FR/EN ; aucune publication ou revue indépendante
déclarée acquise.

## Offline capture adapter 1 — 2026-10-09 — unpublished development tooling

Convert supplied raw captures into validated report/evidence/gate/EARL bundles
with original bytes, code fingerprints, per-target artifacts and explicit omitted
rules. Preserve failures, unknowns and assessment-mode restrictions. Add three
controlled raw examples, FR/EN documentation and workflow tests on the corpus.
Protocol draft.6, identifiers, schema and decision policy remain unchanged.

Conversion de captures fournies en paquet rapport/preuves/décision/EARL validé,
avec octets d’origine, empreintes du code et règles omises explicites. Inconnues,
échecs et restrictions d’automatisation conservés. Trois exemples bruts contrôlés,
documentation FR/EN et tests du parcours. Contrat draft.6 inchangé ; aucune collecte,
publication ou validation indépendante. [Parcours](docs/capture-adapter.md).

## 0.1.0-draft.6 — 2026-10-09 — unpublished development candidate

R-019: TS01-A02 uses prior identity markers or explicit stability for changed
bodies; a bare digest change is inconclusive. R-020: normative expectations are
separate from reference limits, with exact agreements, disagreements and reduced
coverage. R-021: case-insensitive media types/UTF-8 charset, including charset-free
robots.txt. Gate cause NC/NT is explicit; decision policy is unchanged.

R-023: short mutation receipts, optional JSON, inline atomic records and English
summary punctuation. R-022: EARL TestRequirement/TestCase hierarchy, retaining
assertion links. FR/EN spec/docs, 40 additional synthetic cases and regression
coverage. Format 2 and TS01–TS44 remain unchanged. [Migration](docs/migration-draft.6.md).

R-019 : une variation seule ne prouve plus un échec d’identité ; marqueurs et
stabilité sont fixés avant mesure. R-020 : attendus normatifs distincts des limites
du parseur et couverture réduite comptée séparément. R-021 : casse Content-Type et
UTF-8 correctement traitée. Causes NC/NT, CLI et hiérarchie EARL précisées, sans
modifier la politique de décision. Aucun contrôle partiel ne devient C global.

## 0.1.0-draft.5 — 2026-10-09 — unpublished development candidate

- Add bounded raw-input conformance for TS10-A01–A04: inventoried canonical signals,
  direct preferred destination, complete sitemap trees and declared internal sources.
- Bind source/DOM captures and supported reviews to context/date/fingerprints;
  TS10-A02 retains supplied, reasoned human content comparison and manual automation.
- Add 80 synthetic cases, per-rule contradictory outcomes and report/EARL integration
  tests that reject partial/automatic C while retaining failures and unknowns.
- Extend FR/EN contracts, input documentation and dated primary references. Format 2,
  TS01–TS44, grid 1.1, severities/profiles and existing five-rule inputs unchanged.
  [Migration](docs/migration-draft.5.md). No publication or external validation claimed.

## 0.1.0-draft.4 — 2026-10-09 — unpublished development candidate

TS07-A03 source/DOM conformance: prior state plans, source/context bindings, browser
metadata, chronology, script errors and documented exemptions. Keep observed state
failures despite other gaps; never pass a late removal of source noindex. A03 pass
now needs http/html/render/intent. Five bounded rules are executable over supplied
captures; no browser or JavaScript execution. IDs and semiAuto classification stay
unchanged. [Migration](docs/migration-draft.4.md).

Conformance TS07-A03 source/DOM : plan préalable, liaison source/contexte,
métadonnées navigateur, chronologie, erreurs et exemptions documentées. Conserver
les échecs malgré les autres inconnues ; aucun pass par retrait tardif du noindex
source. Pass A03 exige http/html/render/intent. Cinq règles bornées comparées sur
captures fournies, sans lancer navigateur ou JavaScript. IDs et semiAuto conservés.

## 0.1.0-draft.3 — 2026-10-09 — unpublished development candidate

Explicit rule automation and guarded automatic C; TS01-A02 now uses an exact prior
URL/body hash reference. Executable four-rule raw-input conformance, atomic EARL
assertions, safe evidence/record CLI and readable gate. TSEP-2 is defined by webmaster
evidence, with Google first. Bilingual README/migration, broader Python CI matrix,
AGENTS excluded from distribution. No publication, remote CI result or external review claimed.

Automatisation explicite et C automatique conditionnel ; TS01-A02 compare désormais
URL/empreinte à une référence préalable exacte. Conformance exécutable sur quatre
règles, EARL atomique, CLI de saisie des preuves/résultats et résumé lisible. TSEP-2
défini par les preuves webmaster, Google en première série. README/migration FR/EN,
matrice Python élargie, AGENTS exclu de la distribution. Aucune publication, CI
distante observée ou revue externe revendiquée. [Migration](docs/migration-draft.3.md).

## 0.1.0-draft.2 — 2026-10-09 — unpublished development candidate

Nine bilingual atomic rules for TS01, TS07 and TS10, with authored synthetic
method cases and adversarial report coverage tests. Report format 2 requires
rule/target evidence for C on these controls; partial observations cannot establish
a complete control. TS07 adds robots evidence; conditional rendering and justified
absence of sitemap/HTML surfaces are explicit. This remains a report validator,
not an automatic implementation of the SEO methods. IDs, severities, profiles,
upstream provenance and the initial tag are preserved. No publication or
independent review. See [migration](docs/migration-draft.2.md).

Neuf règles atomiques FR/EN pour TS01/07/10, cas synthétiques à jugements de
référence rédigés et tests contradictoires de couverture. Format de rapport 2,
preuves par couple règle/cible, aucun C d’un contrôle entier à partir d’une
observation partielle. Nouvelle preuve robots pour TS07 ; rendu conditionnel et
absences justifiées de sitemap/HTML explicites. Les méthodes SEO ne deviennent pas
automatiques. Identités, sévérités, profils, provenance et tag initial conservés.
Migration explicite ; aucune publication ni revue indépendante.

## 0.1.0-draft.1 — 2026-10-09 — unpublished candidate

Initial independent version sequence derived from Edikka grid 1.1. The 44 IDs and
original FR/EN files are retained, with source hashes. Add bilingual applicability,
acceptance, NA conditions, input requirements, evidence profiles, report schema,
conservative gating, EARL companion, examples and report-interchange tests.
Original software: Apache-2.0; protocol text/data: CC-BY-4.0.

This is a new interpretation contract, not an editorial patch of the 1.1 grid.
Every control gains explicit acceptance and scope rules. Material clarifications:

- TS04: robots.txt 200 is not universally mandatory; evaluate effective policy.
- TS16/TS18: an authoritative inventory is required for claims about a population;
  a crawl cannot establish that inventory's completeness.
- TS19/TS20: policy/configuration inputs prevent a public-only conformance claim.
- TS25: local rendering and Google inspection are separate observations.
- TS32: do not require every example entity type from the legacy grid.
- TS34: field evidence can come from CrUX, Search Console or RUM; C establishes
  correct measurement/reporting, not that measured performance is good.
- TS37: HSTS scope is a documented policy decision; preload is not mandatory.
- TS40: multiple hreflang methods are allowed if complete and consistent.
- TS42: distinguish documented purposes including advertising where applicable.
- All controls: no implied automatic implementation; no global GO from a partial
  probe. NT is split into unstarted and inconclusive for EARL export.
- Gate: any nonblocking NT now prevents GO (INCOMPLETE); all-NA is INCOMPLETE.

The technical references inherited from grid 1.1 have not all been freshly
revalidated. New design observations about robots.txt, hreflang, CrUX, ACT, EARL
and ASVS were checked on 2026-10-09 in the local development recipe. No market
data, independent review, public repository, DOI or adopter is asserted.

### Français

Première version propre à TSEP, dérivée de la grille 1.1 sans réécrire ses fichiers
historiques. Chaque contrôle reçoit des attendus et un périmètre explicites : il
s’agit d’un nouveau contrat, pas d’un renommage. Les précisions ci-dessus modifient
notamment les accès requis pour TS16/18/19/20 et évitent des exigences excessives
sur robots.txt, les entités Schema.org et les méthodes hreflang. TS34 mesure la
qualité de lecture des données, pas une performance nécessairement bonne.

Toute inconnue non bloquante empêche désormais le GO ; tous les résultats NA ne
valent pas une recette réussie. Les références historiques ne sont pas toutes
revérifiées. Aucune publication, adoption, collecte ou revue indépendante nouvelle.
