## 0.3.0-draft.10 — 2026-10-26

Candidat local non publié / Unpublished local candidate.

- FR : sondes publiques TS03-A02 et TS06-A02 avec plan préalable ; profil d’accès TS07 lié à une preuve ou une déclaration explicite ; aucune conformité globale déduite de la sonde seule. Migration normative explicite, profils historiques conservés.
- EN: public TS03-A02 and TS06-A02 probes with a prior plan; TS07 access profile bound to evidence or an explicit declaration; no whole-control conformity inferred from the probe alone. Explicit normative migration, historical profiles retained.
- FR/EN : lecture bornée et réversible des BOM de transport des journaux GitHub / bounded reversible reading of GitHub log transport BOMs. Aucun nouveau succès du contrôle court revendiqué / No new short-check success claimed.
- FR : un C global sur TS03 ou TS06 exige désormais A01 et A02. Sous le nouveau profil TS07, un refus 401/403 au seul client de test reste NT ; un Disallow prouvé reste NC.
- EN: whole-control C for TS03 or TS06 now requires A01 and A02. Under the new TS07 profile, a 401/403 denial to the test client alone stays NT; proven Disallow stays NC.
- [Migration FR/EN](docs/migration-0.3.0-draft.10.md). Qualification locale et distante du candidat exact encore requise / Exact-candidate local and remote qualification still required.

## 0.3.0-draft.9 — 2026-10-25

- FR : limite finale explicite : toute année RFC à deux chiffres reste NT en v2, sans simulation du parseur Google ; 15 attentes de candidats non publiés révisées par manifeste, entrées conservées, noindex indépendant décisif. EN: explicit final limit: every two-digit RFC year stays NT in v2 without simulating Google's parser; 15 unpublished-candidate expectations revised with a manifest, inputs preserved, independent noindex decisive.

- FR : seconde contre-revue : mois hors grammaire indéterminés ; années à deux chiffres comparées sans pivot Google inventé ; décalages négatifs nuls en UTC ; expiration strictement après la date ; profil inconnu sans exception hors raccourci HTTP. EN: second review fixes keep unknown months inconclusive, compare two-digit centuries without an invented Google pivot, interpret negative zero as UTC, require strictly later expiry and preserve inconclusive results for unsupported HTTP-shortcut profiles.

- FR : contre-revue R077 corrigée : dates entièrement consommées, grammaire v2 déterministe et NT sur formats non pris en charge, portées cachées refusées ; profils internes explicites, lecteur TS09 v1 conservé. EN: reviewed R077 fixes consume whole dates, use a deterministic bounded v2 grammar and keep unsupported formats inconclusive; hidden scopes are rejected, internal profiles explicit, TS09 v1 retained.

Publié le 26 octobre 2026 / Published 26 October 2026 : [v0.3.0-draft.9](https://github.com/web-evidence/tsep/releases/tag/v0.3.0-draft.9). TS07-A01 : profil Google v2, listes à espaces seules indéterminées, contradictions indépendantes conservées. / Google v2 profile, space-only rule lists remain inconclusive; independent contradictions retained. Migration explicite, aucune substitution des anciennes preuves. / Explicit migration, no replacement of old evidence.

Préparation / preparation **0.3.0-draft.8** : TS07 directives Googlebot, TS05 cohérence des moyens d’exclusion, TS09 preuve représentative et inventaires d’export exacts / Googlebot directives, exclusion-policy consistency, representative exclusion evidence and exact export inventories. [Migration FR/EN](docs/migration-0.3.0-draft.8.md). Préversion publiée le 25 octobre 2026 / Prerelease published on 25 October 2026: [v0.3.0-draft.8](https://github.com/web-evidence/tsep/releases/tag/v0.3.0-draft.8).

Correction de publication / Publication correction **publication-v2** : arrêt CI macOS au plafond de quatre heures observé et conservé ; plafond de six heures, progression des étapes sur stderr, nouvelle archive et qualification complète requises / observed four-hour macOS CI interruption retained; six-hour ceiling, step progress on stderr, distinct archive and complete qualification required. [Migration FR/EN](docs/publication-profile-v2.md). Norme, règles et tests inchangés / Normative source, rules and tests unchanged.

Préparation de publication / Publication preparation **publication-v1** : citation draft.5 et plafonds CI7200s/240min ; norme, lecteurs, règles et tests inchangés / draft.5 citation and CI7200s/240min ceilings; normative source, readers, rules and tests unchanged. [Migration FR/EN](docs/publication-profile-v1.md). Résultats locaux et CI à consigner séparément / Local and CI results recorded separately.

Correction de distribution / Distribution correction **method-corpus-v1** : métadonnée de version du corpus de méthode alignée sur draft.5 après un échec observé sur1254tests ; cas, attentes et norme inchangés / method-corpus version metadata aligned with draft.5 after one observed failure among1254tests; cases, expectations and normative source unchanged. [Migration FR/EN](docs/method-corpus-metadata-v1.md). Nouvelle qualification complète requise / New complete verification required.

Préparation / preparation **0.3.0-draft.5** : corrections bornées des préalables TS30/TS37, 44 contrôles/98 règles ; 95 définitions atomiques inchangées, toutes les règles RC1 conservées. [Migration](docs/migration-0.3.0-draft.5.md), [contrat / contract](docs/render-transport-prerequisites-v2.md). Nouvelle qualification distincte requise ; aucune publication ni audit réel.

Préparation / preparation **0.3.0-draft.4** :44 contrôles avec98 règles atomiques bornées /44 controls with98 bounded atomic rules. TS26–30/37 added;85 prior rules preserved. [Contract](docs/render-transport-evidence.md), [migration](docs/migration-0.3.0-draft.4.md). Qualification evidence is separate; no real site audit or publication.

# 0.3.0-draft.3 — 2026-10-18

- FR : six règles TS21/22/40,38 contrôles à règles /85 règles ;53 cas synthétiques et neuf cas de méthode, registre de codes figé, preuves conditionnelles TS40 explicites. Les79 règles précédentes conservent leurs objets/versions.
- EN: six TS21/22/40 rules,38 rule-bearing controls /85 rules;53 synthetic cases and nine method cases, frozen code registry, explicit TS40 conditional evidence. All79 prior rule objects/versions retained. No site/app change or publication.

# 0.3.0-draft.2 — 2026-10-18

- FR : neuf règles TS09/11/19/20/38 ; 35 contrôles à règles /79 règles. Dossiers sources bornés, revues liées, NT sur preuves insuffisantes ; 64 contre-cas synthétiques, migration bilingue, règles antérieures conservées.
- EN: nine TS09/11/19/20/38 rules;35 rule-bearing controls /79 rules. Bounded source dossiers, bound supplied reviews, NT for insufficient evidence;64 synthetic counterexamples, bilingual migration, prior rules preserved.
- Correctif de test préalable / prior test-only TS25 runtime portability correction:19 historical recipes retained, two actual-runtime boundaries added; no engine or threshold change. No publication or application/site change.

# 0.3.0-draft.1 — 2026-10-18

- FR : ajoute TS13-A01/A02 et TS14-A01 uniquement depuis RC1 ; 30 contrôles à règles /70 règles, règles antérieures et versions préservées. Contrat bilingue, migration et cas synthétiques ; aucune application/site/publication.
- EN: adds only TS13-A01/A02 and TS14-A01 from RC1; 30 rule-bearing controls /70 rules, earlier rules and versions preserved. Bilingual contract, migration and synthetic cases; no application/site/publication.

Historical baseline / Base historique :

## 0.2.0-rc.1 — 2026-10-17 — prerelease / préversion

- EN: Freeze the complete TS01–TS44 scope inherited from v0.1.0-draft.47; no new control. 28 controls carry 67 executable atomic rules. TS03-A01 remains limited to supplied synthetic .invalid HTTP matrices and literal body markers. Adds RC1 migration, an explicit 44-control status matrix, and a separate app integration dossier for future TS01/TS04 then TS07/TS10 flows. Application version remains independent.
- FR : fige le périmètre complet TS01–TS44 repris de v0.1.0-draft.47, sans nouveau contrôle. 28 contrôles portent 67 règles atomiques exécutables. TS03-A01 reste limité aux matrices HTTP synthétiques .invalid et aux marqueurs littéraux. Ajout de la migration RC1, du tableau d’état explicite des 44 contrôles et d’un dossier séparé pour les futurs parcours app TS01/TS04 puis TS07/TS10. La version app reste indépendante.
- TS03 application r2 receipt is for draft.47 only; a receipt tied to the exact RC1 archive is recorded separately after validation. No real-site use or global conformity is claimed.
- Migration: docs/migration-0.2.0-rc.1.md. Release notes: docs/release-notes-0.2.0-rc.1.md.

## Draft.44 — TS25 byte budgets / bornes en octets

Draft.44 / reader3 : les champs reviewer, assistance et reason des revues TS25 fournies sont limités à8192octets UTF8 bruts chacun, avant strip ou normalisation ; chaque objet revue, champs supplémentaires inclus, à32768octets de JSON compact UTF8. Toute revue fournie est vérifiée à l’admission, même inutilisée. Un dépassement donne un refus technique avant publication, jamais C ou NT public ; les originaux sont conservés sans réécriture. Le diagnostic natif de chaque règle est borné à4MiB de JSON compact UTF8 trié, y compris A01 et les sorties d’erreur. Au dépassement, un diagnostic compact explicitement incomplet conserve un fail indépendant établi, sinon inconclusive ; aucun pass. Le transport refuse ce marqueur et borne aussi à4MiB par cible la somme des artefacts TS25 réellement sérialisés (JSON UTF8 indent2, saut de ligne final), pour les règles demandées. Les maxima individuels ne garantissent pas que toutes leurs combinaisons respectent les bornes cumulées. Aucun changement des autres contrôles ni du validateur partagé.

Draft.44 / reader3: supplied TS25 review fields reviewer, assistance and reason are each limited to8192 raw UTF8 bytes before strip or normalization; each entire review object, including additional fields, to32768 compact UTF8 JSON bytes. Admission checks every supplied review, including unused ones. An overrun is technical refusal before publication, never public C or NT; exact originals are not rewritten. Each native rule diagnostic is bounded to4MiB of sorted compact UTF8 JSON, including A01 and error returns. Overflow produces an explicitly incomplete compact diagnostic retaining an independently established fail, otherwise inconclusive; never pass. Transport refuses that marker and also caps the sum of actual serialized TS25 observation artifacts per target at4MiB (UTF8 JSON indent2, trailing newline), for requested rules. Individual maxima do not guarantee that every combination satisfies aggregate bounds. Other controls and the shared validator are unchanged.

## Draft.43 — TS25 independent failure / défaut indépendant

Draft.43 / reader2 : le champ render est un objet documentaire contenant states. render:[] n’est pas équivalent à render:{states:[]}. Un conteneur non objet ou une population mal formée donne une couverture inconnue, sans coercition ni arrêt des lectures source indépendantes. Une absence source requise et qualifiée reste fail ; une source présente ne transforme pas cette couverture inconnue en pass. Une liste states vide est valide quand aucun état n’est requis. Les revues restent liées aux ID d’états, jamais à leurs indices. Cette frontière propre à TS25 ne migre pas celle de TS23. Les self-digests contradictoires conservent leur refus technique.

Draft.43 / reader2: render is a documentary object containing states. render:[] is not render:{states:[]}. A non-object container or malformed population makes coverage unknown, without coercion or stopping independent source readings. An independently required qualified source absence remains fail; positive source cannot turn unknown coverage into pass. An empty states list is valid when no state is required. Reviews remain bound to state IDs, never indexes. This TS25-specific boundary does not migrate TS23. Contradicted self-digests remain technical refusal.

## Draft.42 — TS25 critical stage presence / présence critique par stade

Five explicit roles, prior stage policies, source hypotheses, rendered states and bound supplied reviews. Finite declared scope; no execution, authenticated judgment, indexing or semantic validity. New native profile; historical manual artifacts unchanged.

## Draft.41 — TS24 unique destination policy / politique de destination unique

A qualified foreign target remains NC when the expected target is also present. Une cible qualifiée contraire reste NC même avec la bonne cible. Earlier draft.40 attempts retained; raw observation/report-intake boundaries explicit. No new control or extra atomic rule.

## Draft.40 — TS24 supplied x-default role / rôle fourni

Prior motivated context, native annotations and bound supplied review; no fabricated approval, native NA or soft404 heuristic. Migration and qualification receipts are separate.

## 0.1.0-draft.36 — local candidate, 2026-10-14

- FR : TS17 source/rendu séparés, stratégie préalable et états déclarés ; snapshots répétés visibles, absence qualifiée distincte d’une preuve manquante. Deux règles natives, aucun constat d’interaction ou d’acquisition authentifiée. Le descriptif TS17 est précisé ; upstream1.1 intact.
- EN: TS17 separate source/render stages, prior strategy and declared states; repeated snapshots disclosed, qualified absence distinct from missing evidence. Two native rules, no authenticated interaction/acquisition. TS17 description narrowed; upstream1.1 retained.
- Interpreter35 /adapter36 /HTML20 /replay3.20 tooled controls /56 rules. Qualification/app reception recorded separately; historical engines, public draft.28 and frozen demo unchanged.

## 0.1.0-draft.35 — local candidate, 2026-10-14

- FR : TS15, trois règles sur les fichiers fournis ;44 cas lecteur,31 cas du jeu et4 contre-exemples de revue figés. Le texte descriptif TS15 est précisé : population déclarée et structure minimale, pas validité complète. Origine non authentifiée, aucune exhaustivité du site. Grille upstream1.1 inchangée ; divergence explicite.
- EN: TS15, three supplied-file rules;44 reader cases,31 set cases and4 frozen review counterexamples. TS15 description narrowed to declared population/minimal structure, not full validity. Unauthenticated origin, no site completeness. Historical upstream1.1 unchanged; explicit editorial divergence.
- Interpreter34 /adapter35 /HTML19 /replay3.19 tooled controls /54rules. Historical engines, public draft.28 and frozen demo unchanged. Actual qualification/app import recorded separately.

- FR : changement de la description TS33 héritée : remplacer la promesse de test d’éligibilité par les trois qualifications bornées ; correspondance entre instantanés non établie. EN: changed the inherited TS33 description, replacing eligibility-testing language with three bounded qualifications; cross-snapshot correspondence remains unestablished. Upstream/grid1.1, public draft.28 and frozen demo unchanged.

## 0.1.0-draft.34 — local candidate, 2026-10-14

- FR : TS33, trois règles,52 cas synthétiques figés/156 paires ; captures liées TS31, noms Schema.org30.1 épinglés, messages natifs APIv1 et revues liées. Erreurs bloquantes conservées ; aucune éligibilité actuelle ni affichage déduits.
- EN: TS33, three rules,52 frozen synthetic cases/156 pairs; TS31-bound captures, pinned Schema.org30.1 names, native APIv1 messages and bound reviews. Blocking errors retained; no current eligibility/display inference.
- Interpreter33 / adapter34 / HTML18 / replay3.18 tooled controls /51rules. Historical engines, archives, public draft.28 and frozen demo remain separate. Qualification and app import evidence recorded separately.

## HTML17 — narrow metric grid / Synthèse sur écran étroit — 2026-10-14

- FR : les cartes de synthèse passent sur une seule colonne jusqu’à 380 pixels CSS ; les libellés restent entiers sans débordement, masquage ou troncature.
- EN: Stack overview metric cards in one column up to 380 CSS pixels, keeping labels readable without overflow, hiding or truncation.
- Presentation-only change: CSS, its derived CSP hash and renderer footer version. Draft.33, JSON reports, original evidence, historical replay and application engine pins remain unchanged. Generate a distinct HTML file; observed layout and source verification results belong to the separate delivery.

## TS02 prospective collector 1 — 2026-10-13 — non-normative

- FR : préparation liée aux outils et bornes, revue préalable fournie, collecte native HTTP bornée, tentatives conservées et évaluation/rejeu hors réseau via le moteur existant. Onze scénarios synthétiques figés ; aucune collecte Edikka ni approbation humaine créée.
- EN: Tool/bounds-bound preparation, supplied prior review, bounded native HTTP collection, retained attempts and offline engine assessment/replay. Eleven prefrozen synthetic scenarios; no Edikka collection or invented human approval.
- Draft.33, interpreter32 / adapter33 / HTML16 / replay3 and all 48 atomic rules remain unchanged. App migration requires an explicit whole-engine import; observed checks are recorded separately.

## 0.1.0-draft.33 — local candidate, 2026-10-13

- FR : trois règles TS32 sur le corpus JSON-LD déclaré, registre préalable, références et revues liées ; 62 cas figés,17 contrôles/48 règles. Aucune stabilité temporelle, identité réelle ou collecte de pages inférée.
- EN: three TS32 declared-corpus rules, prior registry, references and bound reviews;62 frozen cases,17 controls/48 rules. No temporal stability, real identity or page collection inferred.
- Explicit bounded/fingerprinted conformance extensions preserve all1494 earlier cases; general input limits unchanged. Interpreter32 / adapter33 / HTML16 / replay3.
- Draft.32 general verification failures exposed missing method fixtures, provenance-refusal expectations and historical-corpus boundaries. Corrections retain previous expected hashes and frozen rule outcomes. Final verification is recorded separately.

## 0.1.0-draft.32 — local candidate, 2026-10-13

- TS31: prior scope, recomputed source/rendered JSON-LD and entity-bound supplied content reviews; 49 prefrozen synthetic cases.
- FR : trois règles TS31, revues fournies et inconnues conservées ; aucune visibilité authentifiée, validation Schema.org ni résultat enrichi garanti.
- Interpreter31 / adapter32 / HTML15 / replay3; prior artifacts and TS08 application kit unchanged.
- Validation results are recorded after execution; no remote CI or actual Edikka review inferred.

## TS08 application rehearsal 1 — 2026-10-13 — non-normative

- FR : kit CLI import/rapport FR+EN/rejeu, treize exemples fictifs dont une sélection de deux URL, quatre refus attendus et test de rejeu avec horloge future simulée ; guide d'intégration applicative. Aucune nouvelle règle, donnée Google réelle ou qualification OAuth. Les résultats observés sont consignés dans le rapport du kit.
- EN: CLI intake/FR+EN report/replay rehearsal, thirteen authored scenarios including a two-URL selection, four expected refusals and replay test with a simulated future clock; application integration guide. No new rule, real Google acquisition or OAuth qualification. Actual results are retained in the rehearsal report.

## 0.1.0-draft.31 — 2026-10-12 — local candidate

- FR : TS36 ajoute trois règles semiAuto,65 cas préfigés, suivi daté et décisions fournies ; futur indéterminé, zéro causalité ou identité Google inférée. Import/revues/clôture, HTML FR/EN et rejeu ;15 contrôles/42 règles. [Migration](docs/migration-draft.31.md).
- EN: Three TS36 semiAuto rules,65 prefrozen authored cases, supplied chronology/decisions; future stages inconclusive, no inferred causality or Google identity. Intake/reviews/closure, bilingual HTML and replay;15 controls/42 rules.
- FR/EN: Correct the report-contract heading previously omitting TS12; existing rule objects/results remain unchanged.

## 0.1.0-draft.30 — local candidate, 2026-10-12

FR : TS12 ajoute plan, lectures natives API/HTTP/HTML/DOM et qualification/décision fournie. Rendu prévu requis, comparaisons littérales sans verdict TS10. 66 cas figés/198 couples ; 36 règles et 1 304 cas antérieurs préservés. Import hors ligne avec revues vides, preuves, FR/EN et rejeu ; aucune collecte réelle ni publication.

EN: TS12 adds prior plan, native API/HTTP/HTML/DOM comparisons and supplied qualification/decision. Planned rendering required; literal comparisons are not TS10 outcomes. 66 frozen cases/198 pairs, unchanged36 older rules/1,304 cases. Offline intake with blank reviews, evidence, FR/EN and replay; no actual collection or publication. [Migration](docs/migration-draft.30.md).

# 0.1.0-draft.29 — local candidate

TS08 : trois règles semiAuto, JSON API natifs, plan/revues liés, décisions typées, rapports FR/EN et rejeu. Google PASS ne devient pas C ; données anciennes, absences, erreurs et contradictions restent visibles. TS12 reste en attente.

TS08: three semiAuto rules, native API JSON, bound plans/reviews, typed decisions, FR/EN reports and replay. Google PASS is not C; retain old data, gaps, errors and independent contradictions. TS12 remains pending. [Migration](docs/migration-draft.29.md). No publication or real-account assessment inferred.

## Supplied rendered JSON-LD observation 1 — 2026-10-11

- Optional planned source/DOM workflow, supplied base attribution, exact payload comparison and offline replay; no normative version or control-count change.
- Lecture des états structurés fournis, erreurs/inconnues et frontières conservées ; aucune collecte navigateur ni validation Edikka.
- Latest priority / priorité : consolider les 12 contrôles existants avant la décision sur l’application Edikka.

## Optional HTML JSON-LD observation 1 — 2026-10-11 — non-normative

Attributed static script inventory, original bytes and parsed text, template/namespace context, two separate scripting hypotheses and combined-document processing with exact offline replay. 34 prefrozen HTML cases, 24 prefrozen graph scenarios and three additional frozen tokenizer/context boundaries. Source completeness, effective base and rendered states remain separate evidence; no TS31–33 atomic integration or normative change.
FR : trois captures Edikka historiques retraitées avec un contexte public capturé séparément ; erreurs initiales et limites conservées. Ni revue humaine, ni validité Schema.org/Google déduite. [Méthode](docs/jsonld-html-observation.md).

## Optional JSON-LD processing 1 — 2026-10-11 — non-normative

Pinned jsonld.js 9.0.0, explicit Node 24 subprocess, exact local contexts and per-document cache, expanded/flattened observations, warnings and exact replay. Forty initial and eight additional frozen authored cases; invalid Unicode-key failure retained and corrected. A captured official Schema.org context exposed an insufficient initial context-size limit; corrected bound, expected expansion and replay verified with authored data. Draft.27 and the normative corpus unchanged.
FR : base préparatoire TS31–33, pas de conformité Schema.org/Google ni de faits visibles déduits ; [méthode et limites](docs/jsonld-processing.md). Aucun audit Edikka.

## Controlled delivery laboratory 1 — 2026-10-11 — non-normative

Eight prefrozen TS39 scenarios, 38 actual local origin/cache HTTP exchanges, state and purge records, and offline replay. Distinguishes wrong cached content, mechanism-only failure, origin error and legitimate gzip/ETag variants. Draft.27 and the normative corpus unchanged.
FR : preuves manquantes conservées en NT, revues fictives et échecs de développement documentés ; [méthode](docs/delivery-laboratory.md). Aucun audit Edikka.

## 0.1.0-draft.27 — 2026-10-11 — Delivery evidence

Three TS39 rules connect prior reviewed configuration/matrix, native TS07/TS10 signals, semantic reviews and attributed context/cache evidence. 77 authored cases / 231 new pairs; all 1,104 earlier cases unchanged. No live CDN or Edikka assessment.
FR : deux erreurs de qualification conservées et corrigées ; [contrat](docs/delivery-evidence.md), [migration](docs/migration-draft.27.md).

## Critical-content laboratory 1 — 2026-10-11 — non-normative

Four prefrozen TS44 variants, six actual bounded loopback exchanges, native request logs and offline replay. DOM and reviews remain explicitly authored; no browser, agent or Edikka assessment. Draft.24 rules unchanged.
FR : HTTP réellement observé sur site fictif, états rédigés et revues synthétiques distincts. [Method / Méthode](docs/critical-content-laboratory.md).

## Optional delivery variants observer 1 — 2026-10-11

Preparatory TS39 observations: prior cells, raw HTTP chains and bounded stored-side Vary matching. Forty-nine frozen authored cases; no network or normative change. Draft.26 and its 30 rules remain unchanged.
FR : les en-têtes indépendants survivent à un corps tronqué ; ni région, réutilisation du cache, équivalence sémantique ni verdict TS39 déduits. [Method / Méthode](docs/delivery-variants-observation.md).

## 0.1.0-draft.26 — 2026-10-11 — TS41 bilingual clarification and local laboratory

Clarify inconclusive recalculation versus retained positive output; reader behavior and previous 1,103 cases unchanged. One additional frozen boundary, 1,104 cases / 2,101 pairs.
FR : correction explicite d’une divergence de rédaction FR/EN ; nouvelle version, anciens dossiers conservés. [Migration](docs/migration-draft.26.md).
Optional [release laboratory 1](docs/release-laboratory.md): six prefrozen scenarios, actual local HTTP/process/file operations, authored reviews. No production deployment or Edikka assessment. Interpreter 25 / adapter 26 / HTML 9 / replay 3 unchanged.

## 0.1.0-draft.25 — 2026-10-11 — deployment process evidence

Three TS41 rules distinguish process adequacy from underlying SEO outcomes. Native inputs and supplied journal are replayed without executing evidence commands; unknown never becomes green.
FR : plan préalable, couverture et réaction aux échecs/inconnues ; revues liées, défaut correctement bloqué conservé. 52 cas synthétiques ajoutés, 1 051 antérieurs inchangés. [Contrat](docs/release-invariants.md), [migration](docs/migration-draft.25.md).
Interpreter 25 / adapter 26 / HTML 9 / replay 3. Actual TS41 process laboratory and Edikka application remain pending.

## 0.1.0-draft.24 — 2026-10-11 — critical content without JavaScript

TS44 adds prior critical scope, declared no-JS delivery and bound representation coherence/review. Source HTML or explicitly linked HTML/JSON, separate attributed rendered states, no invented truth or agent consumption. 68 prefrozen cases plus 3 code-review boundary cases frozen before fixes; 980 previous cases retained.
FR : faits et sources critiques, chemin public déclaré et versions cohérentes ; DOM rédigé explicitement synthétique. [Contrat](docs/critical-content-evidence.md), [migration](docs/migration-draft.24.md).

## Source content observation 1 — 2026-10-11 — non-normative

Optional bounded content tree prepares TS44: literal IDs, duplicate/context retention, two static scripting hypotheses and original-byte attribution. Thirty authored cases frozen before implementation. Draft.23 and its existing rules remain unchanged.
FR : préparation structurelle TS44, sans verdict ni observation navigateur. [Method / Méthode](docs/source-content-observation.md).

## 0.1.0-draft.23 — 2026-10-11 — agent access and logs

TS43 adds three rules: documented test-client treatment, reviewed native-log correlation and attribution without invented identity. Expected denial can conform. 71 prefrozen cases; prior 909 cases and 21 rules retained.
FR : réponse prévue du client, traces et attribution séparées ; refus attendu possible, aucune visite ni identité opérateur déduite. [Contract / Contrat](docs/agent-access-evidence.md), [migration](docs/migration-draft.23.md).

## 0.1.0-draft.22 — 2026-10-11 — agent usage policy

TS42 gains three atomic rules: supplied source interpretation, distinct owner decisions and bounded robots comparison. Coupled purposes retain explicit owner tradeoffs; 52 prefrozen synthetic cases. Prior eighteen rules and 857 cases retained.
FR : sources et revues liées, décision du responsable distincte et arbitrages explicites ; aucune visite réelle ni conformité des opérateurs déduite. [Contract / Contrat](docs/agent-usage-policy.md), [migration](docs/migration-draft.22.md).

## 0.1.0-draft.20 — 2026-10-11

Optional prior preview-intent profile for TS07-A01/A03; minimum permission and maximum protection intervals, ordered raw directives, conservative image/video ambiguities and replayed diagnostics. Earlier readers and 701 raw cases unchanged. 74 prefrozen authored cases; no live Google observations.
FR : objectifs de permission/protection préalables, inconnues conservées ; migration explicite, aucune revue humaine déduite.

# Change history / Historique

## 0.1.0-draft.19 — 2026-10-11 — HTTP canonical context

Add optional prior http-link-context-v1 for TS10-A01/A02: first rel, explicit anchor
context, ordered raw parameters and unknowns, literal TSEP destination. Keep the
historical reader and all 640 prior cases unchanged; add 61 authored cases.
Interpreter19/adapter20, replay3. No inferred human review or engine outcome.

FR : contexte HTTP et destination séparés, contradictions attribuables conservées,
méthode bornée et migration explicite ; aucun résultat réel Edikka ajouté.
[Contract / Contrat](docs/http-canonical-context.md), [migration](docs/migration-draft.19.md).

## 0.1.0-draft.18 — 2026-10-11 — invalid first-base uncertainty

Optional prior html-tree-links-v2 keeps base-dependent source hrefs inconclusive
when the first base cannot be parsed. Independent contradictions, explicit zero,
v1 semantics, A01/A02 and rendered requirements remain. Interpreter18/adapter19.

Le profil source v2 conserve l’incertitude de base sans réécrire v1 ni effacer
une contradiction indépendante. [Contrat](docs/source-link-policy-v2.md),
[migration](docs/migration-draft.18.md). Aucun changement de capture historique.

## 0.1.0-draft.17 — 2026-10-10 — source link decisions

Optional prior A04 source profile qualifies HTML a/area href, final URL/base and
WHATWG resolution while preserving all 543 historical input/result pairs. Keeps
unknowns, declared-family scope and zero counts through report/gate/EARL. Source
does not replace rendered evidence. Interpreter 17, adapter 18, replay 2.
[Migration](docs/migration-draft.17.md), [method](docs/source-link-policy.md).

## 0.1.0-draft.16 — 2026-10-10 — canonical source decisions

Prior optional html-tree-canonical-v1 extends TS10-A01/A02 with qualified source/head
positions, alternative hypotheses and attributed replay. Independent HTTP/rendered
conflicts survive source unknowns. 55 authored cases; 488 historical inputs/results
preserved. Interpreter 16, adapter 17. [Migration](docs/migration-draft.16.md).

FR : lecture source canonical bornée, sans extension implicite A04/DOM ni revue
humaine inventée. Contrats détaillés désormais liés par empreinte normative.

## 0.1.0-draft.15 — 2026-10-10 — source directives

Prior optional html-tree-directives-v1 extends TS07-A01 and the A03 source prerequisite.
37 authored cases, interpreter 15, adapter 16; [migration](docs/migration-draft.15.md).
FR : hypothèses statiques distinctes et observations attribuées, aucun rendu déduit.

## 0.1.0-draft.14 — 2026-10-10 — page locations in annotated sitemaps

Optional prior sitemap-locations-v1 distinguishes page loc from known XHTML/image
annotations and ordinary fields, retaining values without validating them. Unknown
structures remain inconclusive; legacy reader and full traversal requirements stay.
Interpreter 14, adapter 15, reader 1; 52 prefrozen body and 24 control cases,
with exact preservation of all 427 earlier inputs/results. [Migration](docs/migration-draft.14.md).

FR : amélioration bornée de TS10-A03, sans verdict hreflang/image ni conformité
TS10 entière ; cas synthétiques, aucune collecte réelle induite par la suite.


## 0.1.0-draft.13 — 2026-10-10 — known robots fields outside access scope

Optional prior `google-robotstxt-fields-v2` records thirteen named fields without
changing access rules or groups. The registry is pinned to Google source; unknown
names and typos remain inconclusive. Earlier profiles, actual-client scope and
human review requirements remain unchanged. Interpreter 13, adapter 14, reader 3;
44 prefrozen body cases and 18 control cases, retaining all 409 earlier cases.
[Migration and sources](docs/migration-draft.13.md). No engine or TS42 assessment.

FR : registre fermé de champs conservés hors portée accès, nom du profil explicite,
sources distinctes, inconnus et limites préservés. Une interprétation plus complète
de la politique ne constitue ni une correction du site ni une revue humaine.

## 0.1.0-draft.12 — 2026-10-10 — TS04 actual-client scope

TS04 accepts the prior directive_crawler=googlebot field already used by TS07,
with shared product-profile validation and actual request-agent attribution.
Robots decisions concern the declared product on the client's captured bytes;
HTTP denials remain failures for that client, not claims about Googlebot access.
Absent field preserves historical outcomes; reviews remain required. Interpreter
12, capture adapter 13; 26 prefrozen cases, 383 prior cases retained.
[Migration](docs/migration-draft.12.md). No publication or site conformity claim.

FR : groupe robots distinct du client HTTP réel pour TS04, sans repli ni revue
inventée ; conserver les anciens dossiers et déclarer les options avant collecte.

## Documentation — 2026-10-10 — four-control evidence route

Separate the current draft.11 status (five controls with 13 atomic rules) from
the retained draft.7 inventory. The active four-control scope has 11 rules, with
TS01 as its foundation. The evidence route connects prior intent, captured
contradiction, simulated repair and replay, with real-site and Search Console
limits beside each claim. No normative change, new assessment or publication.

FR : état actuel distinct de l'historique, parcours des quatre contrôles et limites
des démonstrations ; aucune clôture d'audit ou validation humaine déduite.

## Diagnostic — 2026-10-10 — supplied Search Console observations

Offline diagnostic 1 retains original URL Inspection request/response bodies and
compares them with an exact URL/member in a replayed technical bundle. Missing
fields, errors, literal canonical differences and distinct dates remain visible.
Eleven prefrozen synthetic cases; no account access, live URL test, TS08/TS12 verdict
or normative change. [Usage and limitations](docs/search-console-observations.md).

FR : rapprochement hors ligne des preuves techniques et d'une inspection fournie ;
la date de crawl n'horodate pas tous les champs, aucun effet SEO causal n'est déduit.

## Workflow — 2026-10-10 — prior TS02 owner plan

Workflow 1 adds a readable prior plan, blank owner response, supplied-decision
import and exact binding to later captures. It retains rejected decisions, raw
captures and replayable native bundles. No collection, invented judgment or
normative change; draft.11, interpreter 11 and capture adapter 12 stay unchanged.
[Usage and limits](docs/redirect-plan-workflow.md).

FR : fiche préalable, réponse humaine réellement fournie et captures ultérieures
liées au plan ; aucune validation rétroactive ni conformité Edikka déduite.

## Tool coverage — 2026-10-10 — canonical attributes and repair sequence

Protocol draft.11 unchanged. Interpreter 11 / adapter 12 / structured reader 2
share a bounded canonical-attribute classifier; source id/class/data-/aria- no
longer cause blanket refusal, while modifiers and unknown structured attributes
remain inconclusive. Historical serialized DOM stays fixed. 30 prefrozen cases,
353 earlier cases unchanged; laboratory 2 adds a same-URL baseline/fault/simulated
repair recipe. [Coverage and migration](docs/canonical-attribute-coverage.md).

FR : couverture source élargie et lecture DOM corrigée, anciennes pièces conservées ;
la correction du laboratoire est synthétique et ne constitue pas une correction Edikka.

## 0.1.0-draft.11 — 2026-10-10 — actual client and directive semantics

Optional prior TS07 directive_crawler separates the exact HTTP agent from the
bounded Googlebot directive policy. Explicit robots profiles must match this
product. Old inputs retain their results. Same-navigation synthetic browser lab
retains planned responses, exact received requests, sent responses, page exports
and operator receipts, with offline native replay. 15 prefrozen raw cases added;
338 prior cases unchanged. Interpreter 10, capture adapter 11, shared robots
reader 2; no engine-visit claim, no completed human review. [Migration](docs/migration-draft.11.md).

FR : agent HTTP réel distinct de la sémantique des directives, laboratoire
synthétique de navigation attribuée et rejeu ; aucune assimilation à Googlebot.

## 0.1.0-draft.10 — 2026-10-10 — structured rendered states

Integrate a predeclared structured reader for TS07-A03 and TS10-A01/A02/A04,
with complete inventory, provenance guards, exact declarations and retained failures.
Keep the 299 prior raw cases; add 39 prefrozen authored cases. Interpreter 9,
capture adapter 10, review workflow 3 with structured capture identities, unchanged report format 2. [Migration](docs/migration-draft.10.md).
No real capture chain, human review or engine observation is inferred.

Intégration du lecteur structuré, provenance des acquisitions explicite, aucune
substitution favorable de valeur ou de lecteur. Les exigences source et humaines
restent présentes ; les arbres rédigés ne sont pas des captures navigateur.

## 0.1.0-draft.9 — 2026-10-10 — shared robots and TS04

Add TS04-A01/A02, prior origin/profile/resource matrices, evidence-bound access
reviews and shared TS07 policy interpretation. Preserve fixed legacy semantics;
attributable HTTP denial survives missing robots. Add 45 prefrozen raw cases to
the retained 254, blank TS04 review workflow, native loopback bundles and explicit
[migration](docs/migration-draft.9.md). Interpreter 8, capture adapter 9, review 2.
No publication, real engine observation or human approval is inferred.

Ajout de TS04, du lecteur partagé TS07 et du parcours de revue de ressources, avec
profils préalables, contradictions conservées et migration explicite. Treize règles,
299 cas synthétiques ; aucune finalisation implicite du rendu ni conformité Edikka.

## Robots reader experiment 1 / laboratory 2 — 2026-10-10

Prepare the shared TS04/TS07 reader with explicit bounded RFC and conservative
Google profiles, winning-line evidence and refusal bounds. Freeze 64 body cases
under two profiles plus 18 HTTP states before code. Add a portable synthetic
laboratory with 18 real loopback requests, corrections, retained bytes and offline
reinterpretation. No active interpreter, protocol, control or report change.

Lecteur robots candidat, profils distincts, preuves des règles retenues et cas
indéterminés conservés. Le laboratoire 2 émet réellement `googlebot` en minuscules
pour la comparaison TS07 active ; le premier essai et son refus de casse restent
dans les preuves locales. [Portée et limites](docs/robots-policy-experiment.md).

## 0.1.0-draft.8 — 2026-10-10 — TS02 HTTP trajectories

Add two bilingual redirect rules, prior owner-plan review, bounded HTTP comparison,
38 prefrozen contradictory cases, evidence imports and offline replay. Existing nine
rule semantics are retained. Interpreter 7, capture adapter 8. No publication.

Ajout de TS02-A01/A02, avec plan préalable et revue fournie, trajectoires HTTP,
contradictions et inconnues conservées. [Migration](docs/migration-draft.8.md).
Le programme prioritaire passe à [quatre contrôles](docs/four-control-program.md)
sur décision de Bertrand ; leur finalisation ne découle pas de cette version.

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
