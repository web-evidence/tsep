Édition draft.7 / Draft.7: [texte HTML principal v3, limites et migration / main-document text v3, limits and migration](migration-0.3.0-draft.7.md).

Candidat local **0.3.0-draft.6** : [lot 1 FR/EN](migration-0.3.0-draft.6.md). `python3 scripts/verify.py --quick` = régressions ciblées uniquement / targeted regressions only. `python3 scripts/verify.py` = qualification complète / full qualification ; Node24 pré-vérifié, plafond fini7200s par étape. Aucun succès ni publication implicite.

Profil courant / Current profile **draft.5 publication-v2** : plafond total CI de 360 minutes et progression des étapes sur stderr après arrêt macOS à 240 minutes / 360-minute CI job ceiling and step progress on stderr after macOS reached 240 minutes. Toutes les étapes et les sept combinaisons conservées / Every step and all seven combinations retained. [Migration et échec observé FR/EN / Migration and observed failure](publication-profile-v2.md).

Profil historique / Historical profile — Profil de publication / Publication profile **draft.5 publication-v1** : citation alignée, CI7200s par étape/240min par job ; sept combinaisons et toutes les étapes conservées / aligned citation, CI7200s per step/240min per job; all seven combinations and every step retained. [Migration FR/EN](publication-profile-v1.md). Qualification et CI du commit exact requises avant publication / Qualification and exact-commit CI required before publication.

Correction non normative / Non-normative correction **method-corpus-v1** : métadonnée de version du corpus de méthode, cas et attentes conservés / method-corpus version metadata, cases and expectations retained. [Échec observé et migration FR/EN / Observed failure and migration](method-corpus-metadata-v1.md). Archive distincte et nouvelle qualification complète requises / Distinct archive and new complete qualification required.

Current preparation / Préparation courante **0.3.0-draft.5** : prerequisite corrections only, TS30-A01/A02 and TS37-A03; interpreter51/reader2, 44 controls/98 rules. [Migration](migration-0.3.0-draft.5.md). Previous qualified draft.4 archive retained. Full verification still required; no observed success implied. Profil complet Node24/Python3.12, plafond7200s, toutes les étapes conservées.

Non-normative distribution correction / Correction de distribution non normative : [minor report-test integration v1](report-test-integration-v1.md). The first full draft.4 attempt observed one generic test error; protocol and rules unchanged. Nouvelle qualification complète requise / New full qualification required.

Préparation / preparation **0.3.0-draft.4** :44 contrôles avec98 règles atomiques bornées /44 controls with98 bounded atomic rules. TS26–30/37 added;85 prior rules preserved. [Contract](render-transport-evidence.md), [migration](migration-0.3.0-draft.4.md). Qualification evidence is separate; no real site audit or publication.

Profil local complet44 / Full44 local profile: explicit Node24 and Python3.12.14, `TSEP_VERIFY_STEP_TIMEOUT=7200` (finite two-hour bound per step), all verifier steps and source-immutability guards retained. This accommodates the expanded suite and concurrent baseline qualification; a longer ceiling is not a successful run. FR : plafond fini de deux heures par étape pour la suite étendue et la qualification de base concurrente ; aucune vérification supprimée, aucun succès déduit du seul plafond. Observed results belong in dated delivery receipts.

0.3.0-draft.3 preparation:38 rule-bearing controls /85 rules, TS21/22/40 batch. Synthetic cases and supplied reviews; no actual indexing or causality inferred. [Contrat / contract](indexing-locale-evidence.md), [migration](migration-0.3.0-draft.3.md).

Current / courant : 0.3.0-draft.2, TS09/11/19/20/38, 35 controls /79 rules. Prior70 rules and versions retained. [Contract / contrat](url-policy-evidence.md), [migration](migration-0.3.0-draft.2.md). Full verification results belong to dated receipts, not this preparation heading.

Current preparation / Préparation courante : **0.3.0-draft.1**, branch feat/v030-ts12-18 from RC1 7b60c20. TS13-A01/A02 and TS14-A01 only; all earlier rules/versions retained. [Contract / contrat](sitemap-quality-evidence.md), [migration](migration-0.3.0-draft.1.md). Full local profile: explicit Node24, TSEP_VERIFY_STEP_TIMEOUT=3600; all checks enabled. No application/site update or publication; RC1 finalization independent.

Historical baseline / Base historique :

RC1 candidate / Candidat RC1: TSEP 0.2.0-rc.1; all TS01–TS44 work retained, 28 rule-bearing controls / 67 executable atomic rules. TS03-A01 remains a bounded synthetic .invalid HTTP matrix; 13 dedicated contradictory cases. Draft.47 app r2 import/export/replay receipt is preserved; any RC1 exact-archive receipt is tracked separately against the archive SHA. No real-site or soft-404 classification.
FR : préversion distincte ; TS03 reste une qualification de mécanisme synthétique. Aucun diagnostic de site réel n’est revendiqué. Voir le tableau des 44 contrôles, la migration RC1 et le dossier d’intégration applicative.

Previous candidate snapshot / État précédent :
Current candidate draft.44 / interpreter43 / presence reader3 / adapter43 / HTML26 / replay3 : TS25 UTF8 review admission and combined diagnostic bounds. 25 controls /64 rules. Explicit Node24 + TSEP_VERIFY_STEP_TIMEOUT=3600, all checks enabled. Qualification and app reception pending separately. [Migration](migration-draft.44.md).
FR : candidat TS25, bornes UTF8 des revues et diagnostics cumulés ; qualification et réception applicative distinctes.

Previous candidate / candidat précédent :
Current TS25 draft.43 / interpreter42 / reader2 : independent source failures survive malformed documentary render containers;183 preauthored cases,25controls/64rules. Adapter42/HTML25/replay3 retained. [Migration](migration-draft.43.md). Qualification and app acceptance separate.
FR : les absences source indépendantes restent en échec malgré un conteneur documentaire rendu mal formé ;183contre-cas, qualification et recette applicative distinctes.

Previous TS25 candidate / candidat précédent :
TS25 candidate draft.42/interpreter41/adapter42/HTML25/replay3: [presence](critical-presence-evidence.md), [migration](migration-draft.42.md). 25 contrôles outillés / tooled controls,64 règles / rules. Full qualification uses explicit Node24 and TSEP_VERIFY_STEP_TIMEOUT=3600; app import/reception separate.

TS24 revised candidate draft.41/interpreter40/adapter41/HTML24/replay3: [method](xdefault-role-evidence.md), [migration](migration-draft.41.md). 24 controls /62 rules. Prior draft.40 attempts preserved, not qualified. Full local profile: explicit Node24, TSEP_VERIFY_STEP_TIMEOUT=3600; all checks enabled. App acceptance separate.

Previous unqualified TS24 candidate draft.40/interpreter39/adapter41/HTML24/replay3: [x-default](xdefault-role-evidence.md), [migration](migration-draft.40.md). 24 contrôles outillés / tooled controls,62 règles / rules. Full qualification uses explicit Node24 and TSEP_VERIFY_STEP_TIMEOUT=3600; app import/reception separate.

TS23 candidate draft.39/interpreter38/adapter40/HTML23/replay3: [native hreflang](hreflang-reciprocity-evidence.md), [migration](migration-draft.39.md). 23 contrôles outillés / tooled controls,61 règles / rules; qualification and explicit app reception remain separate.

Local qualification profile / Profil local de qualification — TS23 draft.39

The local expanded TS16/TS18/TS23 suite uses explicit Node24 and `TSEP_VERIFY_STEP_TIMEOUT=3600` with `python3 scripts/verify.py`. The earlier TS16 attempt reached the1800s boundary and retained three fixture-coverage failures, corrected separately before retry; extending the time limit alone is not a fix. Every check, archive reconstruction and source-immutability guard remains enabled. This is a bounded local profile, not evidence of remote CI execution.

FR : suite locale étendue TS16/TS18/TS23 avec Node24 explicite, délai maximal3600s par étape et toutes les vérifications inchangées. L’essai TS16 antérieur a atteint1800s avec trois échecs de couverture des fixtures ; ceux-ci sont corrigés séparément avant la reprise. Le délai accru ne corrige aucun échec et ne vaut pas exécution CI distante. Les limites historiques décrites ci-dessous restent propres à leurs versions.

Previous candidate / Candidat précédent — draft.38:interpreter37 /adapter39 /HTML22 /replay3;22 contrôles /60 règles. [TS18](graph-reconciliation-evidence.md), [migration](migration-draft.38.md). Sources and supplied reviews remain bounded; full qualification and app reception are separate. Explicit Node24 and the 3600-second local profile above; historical CI limits below are separate.

Previous candidate / Candidat précédent — draft.37: interpreter36 / adapter38 / HTML21 / replay3; 21 contrôles /57 règles. [TS16](incoming-links-evidence.md), [migration](migration-draft.37.md). Qualification and application import are recorded separately. The qualified local TS16 run used the 3600-second profile above; the archived candidate heading still mentions its earlier 1800-second setting.

Previous transport / Transport précédent: adapter37 adds [TS17 DOM self-integrity intake1](essential-links-intake-v1.md); draft.36/interpreter35/HTML20/replay3 and native rules unchanged. Distinct qualified archive/import required; previous adapter36 artifacts retained.

Current build consistency / Cohérence de construction courante:
`maintain.py check` and `build` reject a stale version or fingerprint in the three
current generated reports (`examples/pass`, `fail`, `partial`) before the full
suite. Regenerate into a separate directory and inspect the diff before copying
current derivatives. Never rewrite historical archives to make them pass.
FR : les trois rapports courants doivent porter la version et l’empreinte exactes
du protocole. Une incohérence bloque la construction ; régénérer séparément,
examiner le diff et conserver les archives historiques intactes.

Previous candidate / Candidat précédent — draft.36 : interpreter35 /adapter37 /HTML20 /replay3 ;20 contrôles /56 règles. [TS17](essential-links-evidence.md), [migration](migration-draft.36.md). Explicit Node24 and documented timeout1800 required; no full qualification implied by this description.

Previous candidate / Candidat précédent — draft.35 : interpreter34 /adapter35 /HTML19 /replay3 ;19 contrôles /54 règles. [TS15](sitemap-files-evidence.md), [migration](migration-draft.35.md). TS15 uses standard Python; full suite still requires explicit Node24 and timeout1800 as documented below.

Previous candidate / Candidat précédent — draft.34 : interpreter33 / adapter34 / HTML18 / replay3 ;18 contrôles /51 règles. [TS33 contract](structured-validation-evidence.md), [migration](migration-draft.34.md). Node24/TSEP_SOURCE_NODE required for native page processing; default lightweight runs may be inconclusive. Previous entries below describe their own historical versions.

Closed historical runtime distribution 1: [contract and explicit migration / contrat et migration explicite](runtime-distribution-v1.md). Separate transport identity; historical engine bytes and native reports unchanged.
TS12/TS31/TS36 CLI intake 2: [raw-byte integrity and explicit migration / intégrité et migration](intake-integrity-v2.md). Normative draft.33 and application engine imports unchanged.
TS08 CLI intake 2: [integrity and explicit migration / intégrité et migration explicite](inspection-intake-v2.md). Complete intake inventory and raw-input bindings; normative draft.33 unchanged. Existing application engine imports are separate and unchanged by this source update.
TS32: [contract / contrat](structured-identity-evidence.md), [migration](migration-draft.33.md). Two explicit fingerprinted fixture extensions keep the core JSON file below its existing 8MiB bound; no recursive discovery or expected-verdict generation.
Previous local work / Travail local précédent — 2026-10-14 : draft.33, interpreter32 / adapter33 / HTML17 / replay3.
[HTML17 narrow metric grid / synthèse sur écran étroit](html-report.md#version-17--narrow-metric-grid--synthèse-sur-écran-étroit) is presentation-only; no historical report or application engine import is rewritten.
TS31 [contract / contrat](structured-content-evidence.md), [intake / import](structured-content-intake.md), [migration](migration-draft.32.md).
FR/EN : 17 contrôles outillés / tooled controls, 48 règles / rules. TS31:59 authored cases /177 pairs; TS32:62 cases /186 pairs; actual verification recorded separately. Supplied reviews, no authenticated visibility or real Edikka assessment.

Application integration preparation / Préparation applicative — 2026-10-13 :
[TS02 prospective collection](redirect-collection.md), non-normative version 1:
prior supplied approval, bounded native HTTP hops, durable failures and offline
assessment/replay. FR : approbation fournie, traces natives conservées, aucun audit
réel Edikka ; protocole draft.33 et règles inchangés. Eleven prefrozen synthetic
scenarios; observed verification belongs in the retained delivery report.

[TS08 CLI rehearsal](inspection-app-integration.md), non-normative version 1.
Thirteen synthetic end-to-end scenarios (including two selected URLs), four refusal
cases and a simulated-future-clock replay test; actual execution results
must be read in the retained rehearsal report. No OAuth/account qualification,
no additional control or normative version change.

Historical local work: draft.31, interpreter30 / adapter31 / HTML14 / replay3.
TS36 [contract](release-monitoring.md), [intake](release-monitoring-intake.md), [migration](migration-draft.31.md).
FR/EN : 15 contrôles outillés / tooled controls, 42 règles / rules; strict four-stage supplied documentary cycle, no real future observation.

Historical integration: draft.30, interpreter29 / adapter30 / HTML13 / replay3.
TS12 [contract](canonical-comparison.md), [intake](canonical-comparison-intake.md), [migration](migration-draft.30.md).
FR/EN: 14 contrôles outillés / tooled controls, 39 règles / rules; supplied rendered states required, no real account/browser trial inferred.

Historical integration: draft.29, interpreter28 / adapter29 / HTML12 / replay3.
TS08 [inspection evidence](inspection-evidence.md), [intake](search-console-acquisition.md), [migration](migration-draft.29.md).
FR : priorité du sprint du 12–14 octobre : TS08 puis TS12 ; qualification et gel mercredi. TS36 puis TS31–33 ensuite.
EN:13 tooled controls /36 rules; supplied API/review qualification only, no actual account assessment or new remote CI.

Historical integration: draft.28, interpreter 27 / adapter 28 / HTML 11 / replay 3.
Guided collector 8 / preflight 3 / intent 4: [parsed preparation and exact replay](guided-parsed-markers.md).
FR : préparation prospective avec refus des contradictions complètes par hypothèse ; sources/runtime liés, aucune application réelle déduite.
Optional prior [parsed-source markers](source-markers.md) extend TS01-A02; [migration](migration-draft.28.md) preserves historical readers and URL/hash/stability precedence.
FR : 76 cas atomiques rédigés, huit scénarios de paquets synthétiques ; aucune activation sur les captures historiques Edikka. Toujours 12 contrôles / 33 règles.

Historical integration: draft.27, interpreter 26 / adapter 27 / HTML 10 / replay 3.
Optional [source-marker readings 1](source-marker-readings.md) prepares TS01 with attributed parsed segments and two whole-document hypotheses; no normative promotion or historical migration.
FR : 52 documents synthétiques, 104 attentes après deux corrections explicites ; diagnostic rétrospectif de trois corps Edikka sans critères ni verdict TS01.
Historical October 11 priority: consolidate the existing 12 controls before deciding the Edikka application; further TS31–33/TS36 layers are deferred after the in-flight rendered component.
FR : priorité donnée par Bertrand le 11 octobre à la finalisation des 12 contrôles ; ne pas attendre les 44 pour décider ensuite de l’application.
Optional [supplied rendered JSON-LD observation 1](jsonld-rendered-observation.md) binds planned supplied DOM states to HTTP, retains snapshot bases and compares exact parsed-source/rendered texts. No browser execution or new control.
Optional [HTML JSON-LD observation 1](jsonld-html-observation.md): original-byte script attribution, two static hypotheses and combined documents under an explicit supplied-base hypothesis; 126 frozen expected readings, 63 exact replays and 10 over-limit refusals.
FR : captures historiques de trois pages Edikka retraitées avec contexte fourni ; ni état rendu, ni validation Schema.org/Google, ni règles TS31–33 déduits.
Optional [JSON-LD processing observation 1](jsonld-processing.md) prepares TS31–33: pinned offline processor, 48 frozen authored cases and exact explicit-Node replay.
FR : traitement JSON-LD qualifié sur ces cas, avec extraction HTML statique ci-dessus ; états rendus, base effective, faits visibles, identités et règles TS31–33 restent à intégrer. Toujours 12 contrôles / 33 règles.
[Controlled delivery laboratory 1](delivery-laboratory.md): eight frozen scenarios, 38 actual local HTTP exchanges, retained cache state/purge and offline replay; authored reviews.
FR : quatre C, trois NC et un NT dans le périmètre fictif ; aucune application Edikka.
[Delivery evidence](delivery-evidence.md): TS39 prior reviewed matrix, native SEO signals and context/cache attribution. [Migration](migration-draft.27.md).
FR : trois règles semiAuto, variantes légitimes et inconnues distinctes ; 77 cas rédigés, aucun audit Edikka ni accès réel Googlebot déduit.

Historical integration: draft.26, interpreter 25 / adapter 26 / HTML 9 / replay 3.
Optional [delivery variants observer 1](delivery-variants-observation.md) prepares TS39: prior cells, raw HTTP differences and bounded stored-side Vary matching, without a control verdict.
FR : matrice et inconnues conservées ; contexte géographique, réutilisation du cache et cohérence SEO restent à qualifier avant intégration normative TS39.
[TS41 bilingual erratum](migration-draft.26.md) clarifies unknown recalculation without changing reader behavior.
[Controlled release laboratory 1](release-laboratory.md) links actual loopback HTTP, process exits and local artifact operations; reviews remain authored.
FR : les six scénarios figés distinguent défaut détecté/bloqué et dispositif défectueux, sans audit Edikka.

Historical integration: draft.25, interpreter 25 / adapter 26 / HTML 9 / replay 3.
[Release process evidence](release-invariants.md): TS41 prior plan, native replay and negative-case response. [Migration](migration-draft.25.md).
FR : un défaut SEO correctement bloqué peut accompagner TS41 C ; premier profil strict sans dérogation. Le laboratoire de processus réel reste à produire.
EN: Authored cases and bounded native reader; actual process laboratory remains pending.
The complete bilingual insight r5 was prepared locally before this TS41 extension; CMS integration remains separate.

Historical integration: draft.24, interpreter 24 / adapter 25 / HTML 8 / replay 3.
[Critical content evidence](critical-content-evidence.md): TS44 prior scope, no-JS delivery and representation coherence, with bound supplied reviews. [Migration](migration-draft.24.md).
FR : trois règles TS44 ajoutées ; pas de lecture réelle d’agent ni de vérité des faits déduite.
Le [laboratoire contrôlé TS44](critical-content-laboratory.md) conserve quatre variantes et six requêtes HTTP réelles, avec DOM et revues rédigés. Intégration complète de l’insight préparée ensuite localement (r5), sans publication.
EN: Four controlled variants retain six actual loopback exchanges with authored DOM/reviews; no browser or agent observation.

Optional [source content observation 1](source-content-observation.md) prepares TS44 with two static scripting hypotheses, retained context and original-byte attribution. Draft.23 unchanged; atomic TS44 rules remain to integrate.
FR : observation structurelle, sans verdict TS44 ni rendu navigateur ; 30 documents contradictoires figés.

Historical integration: draft.23, interpreter 23 / adapter 24 / HTML 7 / replay 3.
[Agent access evidence](agent-access-evidence.md): TS43 test treatment, reviewed log correlation and honest attribution.
FR : un refus attendu du client de test peut être cohérent ; aucun accès réel de l’opérateur déduit.
[Migration](migration-draft.23.md). TS44 remains the next control.

Historical integration: draft.22, interpreter 22 / adapter 23 / HTML 6 / replay 3.
[Agent usage policy](agent-usage-policy.md): TS42 source mappings, owner decisions and qualified robots comparison.
FR : agents IA ajoutés après les performances sur demande du 11 octobre ; TS43/TS44 restent les étapes suivantes.
[Migration](migration-draft.22.md). No actual agent visit or operator compliance inferred.

Historical integration: draft.21, interpreter 21 / adapter 22 / replay 3.
Optional [performance intake workflow 1](performance-intake.md) keeps native files, numbered attempts and blank review requests offline.
FR : import natif, passages numérotés et revues fournies ; aucune nouvelle règle normative.
[Performance evidence](performance-evidence.md): TS34 field documentation and TS35 lab diagnosis; metric quality stays separate from C/NC/NT.
FR : cinq règles de performance ajoutées ; aucune mesure Edikka ni revue humaine déduite. [Migration](migration-draft.21.md).

Historical integration: draft.20, interpreter 20 / adapter 21 / replay 3.
Prior [preview intent](preview-intent.md) extends TS07-A01/A03 with permission intervals and retained unknowns.
FR : intentions de présentation préalables ; aucun affichage ou résultat Google déduit. [Migration](migration-draft.20.md).

Versions distinguish the normative protocol, interpreter, capture adapter and replay tool.
See the [current readiness table](control-implementation-status.md); historical package
versions are retained and are not silently upgraded.
FR : une édition locale ne prouve pas une publication ; les numéros des outils
évoluent séparément et les anciens dossiers se rejouent avec leurs outils exacts.

### Historical draft.28 publication checks / Vérification historique de publication draft.28

The CI workflow now explicitly selects Node 24.19.0 through `TSEP_SOURCE_NODE`
on its seven Python/OS combinations, so optional parsed-source tests are exercised.
It keeps a bounded 1,800-second subprocess deadline and a 60-minute job deadline.
The earlier 120-second subprocess / 10-minute job settings are too short for the
expanded suite with the optional runtime. The CLI default remains 120 seconds;
use `TSEP_VERIFY_STEP_TIMEOUT=1800` explicitly for this full verification profile.
These workflow settings describe prepared checks, not an observed remote success.
Read the run attached to the exact published commit for its actual result.

La CI sélectionne désormais Node 24.19.0 via `TSEP_SOURCE_NODE` sur ses sept
combinaisons Python/OS, afin d'exécuter les tests facultatifs de lecture parsée.
Chaque sous-processus reste limité à 1 800 secondes et chaque job à 60 minutes.
Les anciennes limites de 120 secondes par étape et 10 minutes par job sont trop
courtes pour la suite étendue avec ce runtime. Le défaut CLI reste 120 secondes ;
déclarer `TSEP_VERIFY_STEP_TIMEOUT=1800` pour ce profil complet. Cette préparation
ne prouve aucun succès distant : consulter le run du commit publié exact.

Earlier milestones / Jalons antérieurs :
Historical integration: draft.19, interpreter 19 / adapter 20 / replay 3.
Prior [HTTP canonical context](http-canonical-context.md) extends TS10-A01/A02 with retained raw parameters and context exclusions; [migration](migration-draft.19.md).
FR : premier rel et contexte anchor explicites ; aucun ancien profil migré et aucune revue déduite.

Earlier runtime measurement (draft.18) / Mesure antérieure selon le runtime :
Historical integration: draft.18, interpreter 18 / adapter 19 / replay 3.
The [runtime coverage observation](conformance.md#current-runtime-coverage--couverture-selon-le-runtime--2026-10-11)
distinguishes 109 reduced-coverage pairs without the optional source runtime from
eight with explicit Node 24.19.0, over the same 640 authored cases. A successful
verification is not complete method coverage or a site assessment.
La couverture observée dépend du runtime explicitement fourni ; les limites et
les attendus indéterminés restent visibles, sans score de site ni clôture implicite.
The [partial-family repair laboratory](canonical-partial-repair.md) provides a frozen twelve-phase recipe and an attributed browser/HTTP transport. Its actual browser campaign is separate from authored transport tests.
Le laboratoire de corrections partielles garde une famille fixe et une revue finale vide ; la recette n’est pas une observation navigateur.
Replay 3 adds an explicit [Python supervisor comparison](replay-comparison.md), with exact comparison still the default.
Rejeu 3 : les versions Python restent visibles ; seules leurs différences précisément liées peuvent être admises sur option.
Prior [source links v2](source-link-policy-v2.md) retain uncertainty under an unparseable first base; v1 stays unchanged.
Intégration historique : liens dépendants indéterminés, contradictions indépendantes conservées ; [migration](migration-draft.18.md).
The milestones below describe their historical versions / Les jalons ci-dessous gardent leur version historique.

The [invalid-base diagnostic](base-uri-diagnostic.md) reproduces the discrepancy in top-level and iframe contexts.
Diagnostic d’isolement : 12/24 attentes navigateur, 48/48 calculs URL/base explicites ; draft.17 inchangé.

Experimental [rendered-link observer 1](rendered-link-observation.md) retains href properties and effective bases.
Qualification navigateur : 25/26 attentes, divergence de base invalide conservée ; draft.17 inchangé.

Historical integration: draft.17, interpreter 17 / adapter 18 / replay 2.
Optional prior [A04 source links](source-link-policy.md); [migration](migration-draft.17.md).
Convergence de famille déclarée, comptes et inconnues explicites ; lecteurs rendus inchangés.
The milestones below are historical / Les jalons suivants sont historiques.

Optional [link-element observer 1](link-elements-observer.md) distinguishes HTML/SVG elements and namespaced attributes before A04 policy selection; draft.16 remains unchanged.
Observation des types de liens et templates, sans promotion normative.

Optional [source link resolution experiment 1](source-links-experiment.md) prepares A04: explicit Node24 URL parsing, static base hypotheses and attributed anchors; no normative change.
Expérience de liens source disponible, sans changement de verdict draft.16.

Historical integration: draft.16, interpreter 16 / adapter 17 / replay 2.
Optional prior [canonical source profile](source-canonical.md) extends TS10-A01/A02;
[explicit migration](migration-draft.16.md), unchanged A04 and DOM readers.
Intégration historique : canonical source qualifiée, preuves et revues toujours exigées.
The milestones below are historical / Les jalons suivants sont historiques.

Optional [source/head observation 1](source-head-observation.md) now qualifies canonical placement and source-token context, without changing draft.15 outcomes.
Observation facultative de position canonical et de contexte source ; aucune promotion normative implicite.

Historical integration: draft.15, interpreter 15 / adapter 16 / replay 2.
Optional prior [source directives](source-directives.md) now extends TS07-A01
and the A03 source prerequisite; Node 24 qualification remains explicit and optional.
Intégration historique : directives source TS07, deux hypothèses et preuves attribuées ;
[contrat et limites](source-directives.md), [migration](migration-draft.15.md).
The named milestones below are historical / Les jalons ci-dessous sont historiques.

Historical integration: draft.14, interpreter 14 / adapter 15 / sitemap reader 1.
Optional [static source-tree experiment 1](source-tree-experiment.md) now prepares
TS07/TS10 source coverage with a pinned parser and separate Node qualification.
It has no normative effect and adds no Node requirement to the core verifier.
Expérience facultative d’arbre source disponible ; aucun changement de verdict.
The [browser/source qualification](source-browser-qualification.md) records finite
iframe observations with predeclared BOM/shadow differences, not normative promotion.
Qualification en cadres navigateur disponible ; décodage et shadow restent distincts.
Optional [HTTP-source inventory 1](source-http-inventory.md) adds declared UTF-8/BOM
decoding, original-byte attribution and explicit template declarations. No verdict
changes; this reader remains separate from the normative pipeline.
Inventaire HTTP facultatif : octets, décodage, templates et mode conservés.
Optional prior sitemap-locations-v1 separates page loc from known unassessed
annotations. Legacy cases and missing reviews remain unchanged.
Intégration historique : draft.14, URL de pages distinctes des annotations ;
[méthode](sitemap-locations.md) et [migration](migration-draft.14.md).
The named milestones below are historical / Les jalons ci-dessous sont historiques.

Earlier integration: draft.13, interpreter 13 / adapter 14 / robots reader 3.
The optional, predeclared Google fields profile records a closed registry without
treating these fields as access rules. Earlier profiles and reviews stay unchanged.
Intégration antérieure : draft.13, champs robots hors portée accès relevés selon un
registre épinglé ; aucun verdict TS42 ni observation Googlebot. [Migration](migration-draft.13.md).
The named milestones below are historical / Les jalons nommés ci-dessous sont historiques.

Earlier integration: draft.12, interpreter 12 / adapter 13.
TS04 shares TS07's prior directive_crawler declaration; actual HTTP client scope
and engine observations remain distinct. [Migration](migration-draft.12.md).
Intégration antérieure : draft.12, portée du client TS04 explicite ; aucune revue
humaine ou observation Googlebot déduite. Les jalons ci-dessous sont historiques.
Offline [Search Console diagnostic 1](search-console-observations.md) links supplied
inspection responses to replayed technical evidence; no account access or TS08/TS12 verdict.
Ébauche Search Console disponible ; export réel et qualification humaine restent à obtenir.
Prior TS02 [owner-plan workflow 1](redirect-plan-workflow.md) prepares blank decisions
and binds supplied reviews to later captures, without collecting or inventing approval.
Parcours préalable TS02 disponible ; décision humaine et collecte réelle restent à établir.
Outils de ce jalon : [attributs de canonical et parcours de correction](canonical-attribute-coverage.md) ; recette humaine et application réelle restent distinctes.

Historical integration: draft.11 separates the actual HTTP client from TS07 directive semantics,
with a [same-navigation laboratory](same-navigation-laboratory.md) and [migration](migration-draft.11.md).
Intégration historique : draft.11 ; laboratoire synthétique, sans recette humaine ni conformité Edikka.
Earlier integration descriptions below retain their historical scope.

Historical integration: draft.10 adds the predeclared [structured rendered reader](structured-rendering.md) for TS07/TS10.
Intégration historique : draft.10, lecture structurée du rendu ; collecte réelle et recette humaine restent distinctes.
The historical draft.9 integration and earlier milestones below retain their named scope.

Historical integration: draft.9 adds TS04-A01/A02 and the shared TS07 robots reader,
with prior profiles, resource review workflow and [explicit migration](migration-draft.9.md).
Intégration historique : draft.9 ajoute TS04 et le lecteur partagé TS07, sans finaliser
les limites rendues ni transformer les essais synthétiques en audit Edikka.
Earlier milestone descriptions below retain their historical scope.

# Independent development / Développement autonome

Current priority also includes TS34/TS35 performance, explicitly requested on October 11.
The [performance contract](performance-evidence.md) separates method outcomes from metric quality.

Earlier priority: [four deeply verified controls](four-control-program.md), as
requested on October 10, superseding the ten-control target. Draft.8 adds two
[TS02 rules](redirects.md), retaining the prior 216 raw cases and adding 38.
Earlier CI figures below describe their named historical commits only.

The [candidate shared robots reader](robots-policy-experiment.md) and portable
loopback laboratory prepare TS04/TS07 without changing draft.8 or active rules.
Le lecteur robots candidat prépare TS04/TS07 ; son intégration normative reste à
faire. Ses observations expérimentales ne sont pas des verdicts de contrôle.

Priorité élargie le 11 octobre à TS34/TS35 performance ; couverture de formats partielle.
Priorité antérieure : [quatre contrôles approfondis](four-control-program.md).
Draft.8 ajoute deux règles TS02, sans finaliser le programme ni l'audit d'Edikka.
Les résultats CI historiques ci-dessous ne concernent pas cette candidate.

The [evidence gallery guide](evidence-gallery.md) connects the existing methods
and retained demonstrations without new collection or a cross-campaign score.
Le [guide de galerie de preuves](evidence-gallery.md) organise les démonstrations
existantes, en séparant cas réels, laboratoires et résultats expérimentaux.

The [44-control development inventory](control-implementation-status.md) separates
specified methods, executable coverage, known limitations and real assessments.
Le [suivi des 44 contrôles](control-implementation-status.md) distingue description,
outillage, limites ouvertes et application réelle ; il ne déclare pas leur achèvement.

## English

This repository is TSEP's development source. It is independent of the Edikka
website, CMS, database, server configuration and deployment process. Its initial
commit imports the 40 source files of `0.1.0-draft.1` byte-for-byte. The annotated
tag `v0.1.0-draft.1` preserves that imported candidate. Provenance is recorded
in `provenance/import.json`; no older Git history or private project files were imported.

The protocol is still a draft. Infrastructure commits after the import do not
rewrite the baseline tag or make a public release. A development archive is a
snapshot identified by its checksum; do not redistribute it under an existing
released archive's identity. Public repository, organization, domain and DOI are
not required to develop or validate the package locally.

### One verification command

Python 3.9+ and curl are required for the full local suite. The CLI itself only
uses Python's standard library. From the repository root:

```sh
python3 scripts/verify.py
```

It validates the contract, runs report/distribution tests and the raw-input
conformance suite, regenerates synthetic examples outside the source tree, runs the bounded HTTP cases on loopback,
builds an archive, extracts it and checks that rebuilding yields identical bytes.
Guided collector tests also bind 127.0.0.1 during the unit step: synthetic
changing pages exercise gzip/deflate, frozen intent and network-forbidden replay.
Tests also reject mixed module origins and changed collector sources before
network access, verify the two-phase JSON size budget, and reject a synthetic
self-signed TLS certificate before HTTP. `tests/tls_fixture.py` deliberately
contains a public disposable test certificate/key; never deploy or trust them.
The consumer workflow under `examples/` is prepared, not activated or observed
on remote CI. See [guided capture](guided-capture.md).

The tests include offline capture-to-bundle conversion, file integrity and partial
coverage; raw capture examples are regenerated alongside report examples. The
capture adapter has its own tool version and code fingerprints. It uses the
pinned normative protocol; draft.7 changes identity assessment, as documented
in its migration, without changing the adapter's bundle format.
It refuses source-file changes during verification. No Edikka environment,
credentials, package installation, browser or public-site collection is needed.
If a sandbox forbids a loopback listener, report that limitation; do not silently
skip the HTTP tests and claim the full verification passed.

Each subprocess step has a **120-second default deadline**, including each unit
test run. Set `TSEP_VERIFY_STEP_TIMEOUT` to a finite number of seconds greater than
zero and at most 86400 (fractions allowed), for example on a slower runner:

```sh
TSEP_VERIFY_STEP_TIMEOUT=300 python3 scripts/verify.py
```

The effective deadline is recorded as `step_timeout_seconds` in the JSON result.
Invalid values fail before any checks. A timeout fails verification and retains
the step name, duration, limit and partial output; it never skips a check or
turns it into success. The limit applies per step, not to the entire command;
the conformance adapter's own 15-second per-case limit remains separate.

The draft.7 external CLI test uses 15 named corpus cases, asserting pass/fail/
inconclusive coverage for all nine rules. They also include multiple targets and
a reference limit; the test rejects wrong verdicts and extra output. This reduces
adapter startups from 604 to 45. **Both conformance steps still run all 216 cases**
in the source tree and extracted archive; the corpus is unchanged. The unit-step
target is under 60 seconds, leaving at least the same amount of margin under the
default deadline. Actual timings depend on Python, machine load and hardware;
record the measured environment rather than asserting an unobserved CI result.

Git is needed for development, not for using a downloaded package. Use descriptive
branches in the form `<type>/<short-description>`, where type is `feat`, `fix`,
`docs`, `test` or `chore` (for example, `docs/contributor-guidance`). Integrate
changes sequentially after verification. Keep generated files in sync through
deliberate, reviewed regeneration. The canonical report contract and JSON did not
change during the repository split; distribution boundaries and verification
were strengthened.

### Distribution and integration boundaries

`release-files.json` is the explicit distribution inventory. The builder rejects
missing files, duplicates, unsafe paths, symlinks and common private file paths.
Unlisted local files cannot enter an archive. This is a packaging boundary, not
a guarantee against secrets deliberately written inside an allowed source file:
review source and Git diffs before publication.

`maintain.py build --output /tmp/tsep-development.zip` refuses an existing output
and creates deterministic bytes with a SHA256SUMS manifest. `.git`, environment files, Git bundles and working evidence stay outside the package.

Edikka's original `tools/tsep` is frozen, with a migration notice. Future changes
belong here. Edikka should consume a chosen release plus checksum through its own
reviewed integration. Do not symlink the repositories, synchronize both directions,
share `.git`, or couple a website build to TSEP's working tree.

### CI and public contributions

The GitHub workflow runs the same command on Linux/Python 3.9, 3.10, 3.11, 3.12,
3.13 and 3.14 and on macOS/Python 3.14. Action dependencies are pinned to verified commit hashes;
permissions are read-only and checkout does not persist credentials. It has no
deploy, release, secret, `pull_request_target` or automatic publication step.
The repository is [web-evidence/tsep](https://github.com/web-evidence/tsep), hosted
under [Web Evidence](https://github.com/web-evidence). It became public on
9 October 2026; the repository, issues, pull requests and CI are publicly readable.
Edikka remains the current steward; hosting does not establish independent governance.
Use its [issues](https://github.com/web-evidence/tsep/issues) and
[pull requests](https://github.com/web-evidence/tsep/pulls) to contribute.
Opening the development repository does not create a stable release or replace
the initial tag. For the current revision's result, inspect its commit in the
[verification workflow](https://github.com/web-evidence/tsep/actions/workflows/verify.yml).

### First observed CI run

On 9 October 2026, [run 1, attempt 1](https://github.com/web-evidence/tsep/actions/runs/37962185984)
completed successfully on commit `253b0a13389af53d50245f874f6bdcdb2b570a68`.
All seven jobs passed: Linux/Python 3.9, 3.10, 3.11, 3.12, 3.13 and 3.14,
and macOS/Python 3.14. Each job ran 152 unit tests and all 216 conformance cases
in both the checkout and the extracted archive, plus 48 loopback HTTP cases.
Each conformance run retained 454 agreements, zero disagreements and nine reduced
coverage pairs out of 463 rule/target pairs; reduced coverage is not a pass.
All fourteen unit-test steps stayed below 60 seconds; the longest took 49.354 seconds
including process startup, with the default 120-second step deadline unchanged.

The runner images and Python patch versions observed in the logs were:

| Runner label | Image and build | Python versions |
| --- | --- | --- |
| `ubuntu-latest` | `ubuntu-24.04`, `20261004.327.1` | 3.9.25, 3.10.22, 3.11.17, 3.12.15, 3.13.16, 3.14.8 |
| `macos-latest` | `macos-26-arm64`, `20260907.0351.1` | 3.14.7 |

The `-latest` labels can resolve to different images in later runs.

All seven archives and their rebuilds matched the archive built locally from
the same commit before push:
`4f8bc1575fa5591dc6fdbbbcbbaac97620e9e81e57d7de749223631f4685dafa` (SHA-256).
The maintainer retained the complete log ZIP for this attempt, SHA-256
`5e799a49546ec74a15f829dd1a6aab6b95168ac61d0598264632433c7fcc75d0`.
This run was first observed while the repository was private. Its logs are
accessible through the run page until the GitHub retention period
expires ([90 days by default](https://docs.github.com/en/organizations/managing-organization-settings/configuring-the-retention-period-for-github-actions-artifacts-and-logs-in-your-organization));
the effective repository setting was not checked. The retained ZIP identified
above is the durable reference after that expiry. Public access makes the run
inspectable; it does not establish independent practitioner review.
Windows was not tested.

These results and archive hashes belong to that commit, which predates this
documentation update. Later revisions, including documentation-only changes,
need their own verification and produce a different archive when packaged bytes
change. The protocol remains `0.1.0-draft.7`; the initial tag is not replaced.

## Français

Ce dépôt devient l’unique source de développement TSEP. Le premier commit et le
tag `v0.1.0-draft.1` conservent les 40 fichiers importés sans changement. Les
commits d’infrastructure suivants ne remplacent ni ce tag ni une publication.
La provenance est dans `provenance/import.json`. Aucun historique privé Edikka
n’est importé, aucun domaine, organisation ou DOI n’est nécessaire pour avancer.

Git sert au développement, pas à l’utilisation d’une archive téléchargée. Utiliser
des branches descriptives de la forme `<type>/<short-description>`, avec `feat`,
`fix`, `docs`, `test` ou `chore` comme type (par exemple,
`docs/contributor-guidance`). Intégrer les changements séquentiellement après
vérification. Régénérer les dérivés délibérément et relire leurs écarts.

La commande `python3 scripts/verify.py` vérifie contrat, tests, conformance sur entrées brutes, exemples temporaires,
sonde HTTP locale et archive reconstruite à l’identique. Elle exige Python 3.9+
et curl, sans dépendance Python externe ni accès à Edikka. Une restriction de
sandbox sur 127.0.0.1 reste une limite à signaler, jamais un test réussi.

Le délai maximal par étape de sous-processus vaut **120 secondes par défaut**,
y compris chaque exécution unitaire. `TSEP_VERIFY_STEP_TIMEOUT` accepte un nombre
fini de secondes strictement positif et inférieur ou égal à 86400, fractions
admises. Exemple pour une machine plus lente :
`TSEP_VERIFY_STEP_TIMEOUT=300 python3 scripts/verify.py`.
La sortie JSON expose la valeur effective dans `step_timeout_seconds`. Une valeur
invalide échoue avant les contrôles. Un dépassement fait échouer la vérification
et conserve nom de l’étape, durée, limite et sorties partielles ; aucun contrôle
n’est omis ou déclaré réussi. Ce délai s’applique à chaque étape, pas à la commande
entière ; les 15 secondes par cas d’adaptateur de conformance restent distinctes.

Le test CLI externe draft.7 utilise 15 cas nommés du corpus et vérifie la présence
de pass/fail/inconclusive pour chacune des neuf règles. Il conserve plusieurs
cibles, une limite de référence, les mauvais verdicts et les sorties en trop.
Les lancements d’adaptateur passent de 604 à 45. **Les deux étapes de conformance
exécutent toujours les 216 cas**, depuis les sources et l’archive extraite ; le
corpus reste inchangé. L’objectif unitaire est inférieur à 60 secondes, laissant
au moins autant de marge sous le délai par défaut. Les durées dépendent de Python,
du matériel et de sa charge ; ne revendiquer que les environnements mesurés.

Les tests du collecteur ouvrent aussi 127.0.0.1 pendant l’étape unitaire : pages
synthétiques changeantes, gzip/deflate, intention préalable et rejeu réseau interdit.
Les tests refusent aussi les origines de modules incohérentes et les sources de
collecteur modifiées avant le réseau, vérifient le budget JSON des deux phases et
refusent un certificat TLS synthétique auto-signé avant HTTP. Le certificat et
la clé de `tests/tls_fixture.py` sont des données de test volontairement publiques,
à ne jamais déployer ni approuver comme autorité de confiance.
Le workflow consommateur dans `examples/` est préparé, non activé et non observé
en CI distante. Voir la [collecte guidée](guided-capture.md).

Les tests couvrent aussi la conversion hors ligne captures → paquet, l’intégrité
et la couverture partielle ; les exemples de captures sont régénérés avec les
rapports. L’adaptateur possède sa version d’outil et ses empreintes de code. Il
utilise le protocole normatif figé ; draft.7 modifie l’évaluation d’identité selon
sa migration, sans changer le format du paquet de l’adaptateur.

Le constructeur utilise une liste explicite `release-files.json`, pas tous les
fichiers du répertoire. Les fichiers privés non listés restent exclus. Cette
frontière ne remplace pas une revue des sources avant publication. Une archive
de développement porte son empreinte ; elle ne doit pas usurper une version
publiée.

La copie `tools/tsep` dans Edikka est gelée. Toute évolution se fait ici ; le site
intégrera une version choisie avec empreinte et recette propres. Aucune synchronisation
bidirectionnelle, aucun lien symbolique ou historique Git partagé.

### CI et contributions publiques

La CI couvre Linux/Python 3.9, 3.10, 3.11, 3.12, 3.13 et 3.14 et macOS/Python 3.14.
Les dépendances d’actions sont figées sur des empreintes de commit vérifiées ;
les droits sont en lecture seule et le checkout ne conserve pas les identifiants.
Le workflow n’a ni déploiement, ni release, ni secret, ni `pull_request_target`,
ni étape de publication automatique.
Le dépôt [web-evidence/tsep](https://github.com/web-evidence/tsep) est hébergé sous
[Web Evidence](https://github.com/web-evidence). Il est devenu public le 9 octobre 2026 ;
le dépôt, les issues, les pull requests et la CI sont consultables publiquement.
Edikka reste le responsable actuel ; l’hébergement ne crée pas une gouvernance indépendante.
Contribuer par les [issues](https://github.com/web-evidence/tsep/issues) et
[pull requests](https://github.com/web-evidence/tsep/pulls). L’ouverture du dépôt
de développement ne crée pas de version stable et ne remplace pas le tag initial.
Pour le résultat de la révision actuelle, consulter son commit dans le
[workflow de vérification](https://github.com/web-evidence/tsep/actions/workflows/verify.yml).

### Première CI observée

Le 9 octobre 2026, le [run 1, tentative 1](https://github.com/web-evidence/tsep/actions/runs/37962185984)
a réussi sur le commit `253b0a13389af53d50245f874f6bdcdb2b570a68`.
Les sept jobs ont réussi : Linux/Python 3.9, 3.10, 3.11, 3.12, 3.13 et 3.14,
et macOS/Python 3.14. Chaque job a exécuté 152 tests unitaires et les 216 cas de
conformance dans les sources puis l’archive extraite, ainsi que 48 cas HTTP sur loopback.
Chaque passage de conformance conserve 454 accords, aucun désaccord et neuf
couples de couverture réduite sur 463 couples règle/cible ; une couverture réduite
n’est pas un pass. Les quatorze étapes unitaires sont restées sous 60 secondes ;
la plus lente a duré 49,354 secondes, démarrage du processus compris, sans modifier
le délai par défaut de 120 secondes par étape.

Les images des runners et les versions correctives de Python observées dans les
journaux étaient :

| Étiquette du runner | Image et build | Versions de Python |
| --- | --- | --- |
| `ubuntu-latest` | `ubuntu-24.04`, `20261004.327.1` | 3.9.25, 3.10.22, 3.11.17, 3.12.15, 3.13.16, 3.14.8 |
| `macos-latest` | `macos-26-arm64`, `20260907.0351.1` | 3.14.7 |

Les étiquettes `-latest` peuvent désigner d’autres images lors de runs suivants.

Les sept archives et leurs reconstructions ont la même empreinte que l’archive
construite localement depuis ce même commit avant l’envoi :
`4f8bc1575fa5591dc6fdbbbcbbaac97620e9e81e57d7de749223631f4685dafa` (SHA-256).
Le responsable a conservé le ZIP complet des journaux de cette tentative, SHA-256
`5e799a49546ec74a15f829dd1a6aab6b95168ac61d0598264632433c7fcc75d0`.
Ce run a été observé pour la première fois lorsque le dépôt était privé. Ses
journaux sont accessibles depuis sa page jusqu’à l’expiration de la
rétention GitHub ([90 jours par défaut](https://docs.github.com/en/organizations/managing-organization-settings/configuring-the-retention-period-for-github-actions-artifacts-and-logs-in-your-organization)) ;
le réglage effectif du dépôt n’a pas été vérifié. Le ZIP conservé, identifié
ci-dessus, est la référence durable après cette expiration. L’accès public rend
le run consultable ; il n’établit pas une revue indépendante de praticiens.
Windows n’a pas été testé.

Ces résultats et empreintes appartiennent à ce commit, antérieur à cette mise à
jour documentaire. Toute révision suivante, même documentaire, exige sa propre
vérification et produit une autre archive si les octets distribués changent.
Le protocole reste `0.1.0-draft.7` ; le tag initial n’est pas remplacé.

## Source-text extraction checks / Vérifications du texte source

Interpreter 5 retains the 96 original synthetic counterexamples and adds 51 SVG/noscript cases; it has 312 selected upstream HTML
character-reference expectations, frozen before implementation. Run
`python3 scripts/source_text_check.py` with each available Python: matching
`result_sha256` values compare exact segments/outcomes for this finite selection,
not all HTML or all runtime behavior. The command has no network dependency.
`python3 scripts/verify.py` also runs these fixtures through unit tests; the TS07
and TS10 corpus outputs must match their pre-change fingerprint. Runtime source
hashes are selected dependencies, not execution authentication. See
[source scope and migration](source-text-v5.md). No new remote CI run
is established by preparing tests or a matrix.

L’interpréteur 5 conserve les 96 cas synthétiques initiaux et ajoute 51 cas SVG/noscript,
avec les 312 attentes de
références de caractères issues d’un corpus externe, figés avant implémentation.
Exécuter `python3 scripts/source_text_check.py` avec chaque Python disponible :
un `result_sha256` identique compare les segments/résultats exacts de cette
sélection finie, sans prouver tous les comportements HTML ou Python. Aucun réseau.
La vérification complète exécute aussi ces cas ; les sorties TS07 et TS10 du
corpus doivent conserver leur empreinte antérieure. Les dépendances enregistrées
ne constituent pas une authentification d’exécution. Voir [sources, licence et
migration](source-text-v5.md). Préparer une matrice ne prouve pas une nouvelle CI distante.

## Reference diagnostics / Diagnostic des références

The diagnostic CLI imports HTTP decoding utilities, never the decision module.
Tests exercise several candidate limitations in a single document, raw contexts,
false tag spellings in attributes/scripts, bounded scanning, input preservation
and an isolated CLI without evaluator imports. Guided tests reject contradictory
reference markers, expose unavailable preparation checks even after a digest
match, stop modified preflight records before network, and disclose changed media
without changing normative outcomes. See [scope and migration](reference-diagnostics.md).

Le diagnostic utilise le décodage HTTP, sans importer le module de décision.
Les tests couvrent plusieurs limites candidates dans une page, les contextes bruts,
le faux balisage dans les attributs/scripts, les bornes et la conservation des
entrées. Le parcours guidé refuse les marqueurs contradictoires de référence,
conserve les avertissements malgré une empreinte égale, refuse un précontrôle
modifié avant le réseau et observe le média sans modifier le verdict normatif.

## Paired diagnostic / Diagnostic par paire

Campaign tests distinguish decoded-byte changes from compression, incomplete
responses, changed destinations, missing media and source-extraction limits. They
reject changed URL ordering, settings/source continuity, invalid times, tampered
manifests and JSON/raw sidecar disagreements. An isolated CLI runs without the
rule evaluator or collector. A guided loopback case retains equal-digest pass
while disclosing a removed Content-Type. See [scope](diagnostic-campaign.md).

Les tests distinguent changement des octets décodés, compression, réponse incomplète,
destination différente, type absent et limites de l’extracteur. Ils refusent les
écarts de liste, réglages, sources, dates, manifeste ou fichiers bruts. Le CLI isolé
fonctionne sans module de décision ni collecteur ; un cas loopback conserve le
pass par empreinte égale tout en signalant le Content-Type retiré.

## Unapplied noscript experiment / Expérience noscript non appliquée

The separate [experiment](noscript-experiment.md) has 68 authored cases frozen
before implementation, with per-mode expected source segments and candidates.
Tests also check Unicode offsets, disagreement/incomplete-reading behavior, bounds,
CLI isolation without evaluator/collector, and the unchanged active extractor.
It is included in verification/distribution for review, never imported by the
normative decision pipeline. Experimental candidate results are not report outcomes.

L’expérience séparée conserve 68 cas rédigés avant son code, avec segments et
candidats attendus par mode. Les tests ajoutent positions Unicode, désaccords,
lectures incomplètes, bornes, CLI isolé et refus inchangé de l’extracteur actif.
Elle est distribuée pour examen, jamais branchée sur les décisions normatives.

Experiment 3 adds 96 prefrozen form-control cases after the six list-scope cases.
The initial 68-case file stays intact; a single explicit v3 expectation delta
covers select inside disabled noscript. Reference comparisons with an isolated
historical parser are private evidence, not a runtime dependency or browser claim.

L'expérience 3 ajoute 96 cas de formulaires figés avant code après les six cas de
listes. Le fichier initial reste intact ; un seul écart d'attente v3 est explicite.
La comparaison externe historique reste une preuve privée limitée, sans dépendance
supplémentaire ni assimilation du lecteur source à un navigateur.

Experiment 4 adds 103 prefrozen explicit-table cases. Parent, order, literal
whitespace, whole-source refusal and global noscript hypotheses are exercised.
Earlier fixture files are preserved; one v3 empty-table expectation changes
explicitly. [Scope and migration](table-experiment-v4.md).

L'expérience 4 ajoute 103 cas de tableaux figés avant code. Parents, ordre,
espaces littéraux, refus intégral et hypothèses noscript sont éprouvés. Les
anciens fichiers restent intacts ; un cas v3 change explicitement d'attente.

The [prospective experiment](prospective-experiment.md) records criteria before
measurement and keeps draft.7 reports separate from experimental candidates.
Its nine prefrozen synthetic cases use loopback only; integrity and offline
replay checks are included in verification and the explicit distribution.

L'[expérience prospective](prospective-experiment.md) enregistre les critères avant
mesure et conserve le rapport draft.7 séparé du prototype. Neuf cas synthétiques
figés avant code, contrôles d'intégrité et rejeu hors ligne sont inclus dans la
vérification et la distribution explicite, sans dépendance à Edikka.

## Rendered canonical candidate / Candidat canonical rendu

The [standalone candidate 1](rendered-canonical-candidate.md) interprets structured
inventory 2 records under explicit exact-string criteria. Its 59 authored cases
were frozen before implementation; additional review cases are identified separately.
It preserves missing evidence, API ambiguity, partial coverage and source/DOM
boundaries. Verification includes offline evaluator-free CLI tests and packaging.
It does not change the protocol, earlier captures or normative outcomes. The
recorded 48-input application is retrospective, not independent validation.

Le [candidat autonome 1](rendered-canonical-candidate.md) interprète les relevés
d'inventaire 2 selon un critère explicite de chaîne exacte. Ses 59 cas rédigés
sont figés avant implémentation ; les ajouts de revue restent identifiés séparément.
Les tests incluent le CLI hors réseau sans import d'évaluateur, les limites de
preuve et la distribution. Aucun changement normatif ou de capture ancienne.
L'application consignée sur 48 entrées est rétrospective, sans validation indépendante.

## Predeclared canonical laboratory / Laboratoire canonical prédéclaré

[Laboratory 1 and intent adapter 2](predeclared-canonical-laboratory.md) add nine
predeclared synthetic page recipes, source/POST/chronology binding and offline
replay. Comparison core 1 stays unchanged; legacy migration is explicit. Tests
cover its 69 frozen cases plus two preference cases, tampering, duplicate requests,
missing observations, unavailability and retained mismatches. No normative change.

Neuf recettes synthétiques prédéclarées, liaison sources/POST/chronologie et rejeu
hors ligne. Le cœur de comparaison 1 reste intact ; migration explicite, tests
d'altération, doublons, absence, indisponibilité et conservation des écarts.
Aucune validation indépendante des règles ni modification normative.

## Canonical state sequences / Séquences d’états canonical

[Sequence experiment 1](canonical-state-sequences.md) adds an ordered ledger and
a three-state synthetic laboratory. It preserves earlier contradictions, unknowns
and missing states, without a sequence verdict or stability claim. One navigation
per page, chained receipts, fixed actions, no retry. Candidate 1/2 remain unchanged.

L’[expérience de séquences 1](canonical-state-sequences.md) conserve trois états
prédéclarés par page, leurs écarts et leurs lacunes, sans verdict global ni preuve
de stabilité. Les tests incluent altérations avec empreintes recalculées, ruptures
de chaîne, marqueur divergent et rejeu hors réseau. Aucun changement normatif.

## Source text v6 / Texte source v6

[Source text v6](source-text-v6.md) adds explicit select/table coverage under the
unchanged draft.7 contract. One historical synthetic expectation is explicitly
superseded; its frozen file remains intact. Nonempty noscript stays unresolved.

Le [lecteur v6](source-text-v6.md) accepte un sous-ensemble select/table explicite.
Une attente historique change explicitement, sans réécrire le fichier figé.
Le contrat draft.7 reste inchangé ; noscript non vide demeure indéterminé.

## Review and replay / Revue et rejeu

[The review and replay workflow](review-and-replay.md) adds one offline replay
command for all capture-adapter bundles and blank evidence-bound TS07/TS10 review
requests. Tests preserve failures, unknowns and synthetic provenance; no actual
human review or user acceptance is inferred. Protocol draft.7 is unchanged.

Le [parcours de revue et rejeu](review-and-replay.md) fournit une commande commune
et des fiches vides liées aux preuves. Les tests ne valent pas relecture humaine
ni recette utilisateur. Les inconnues et contradictions restent conservées.

[TS43 controlled loopback laboratory / Laboratoire contrôlé TS43](agent-access-laboratory.md): six prefrozen scenarios, eight local requests and offline replay; no real provider visit.
