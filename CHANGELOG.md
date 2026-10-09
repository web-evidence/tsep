# Change history / Historique

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
