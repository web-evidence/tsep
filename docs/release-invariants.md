# Release invariant evidence / Preuves de non-régression — version 1

## Français

Le profil explicite `release-invariants-v1` de TS41 (draft.25) examine le dispositif
sur une population préalable de **tentatives de déploiement**, pas la conformité
SEO globale. Les résultats SEO sous-jacents restent distincts. Un défaut détecté
et effectivement bloqué peut accompagner un dispositif conforme ; aucune inconnue
n'est renommée réussite. Le profil n'exécute jamais les commandes fournies.

Trois règles : A01 plan préalable et revue de représentativité ; A02 couverture,
chronologie, rattachement aux artefacts et fidélité des sorties ; A03 exercice
négatif et réaction du dispositif selon la phase. Les règles sont semiAuto : les
revues fournies restent requises et leur auteur n'est pas authentifié. Une
contradiction indépendante reste fail malgré une autre pièce manquante. Les
attendus absents, non qualifiés ou ambigus restent inconclusive ; aucune exemption
atomique automatique, aucun NA déduit d'un journal vide.

### Contrat d'entrée borné

L'entrée captures habituelle contient une cible URL identifiant le périmètre,
`observed_at`, `context` et `intent.declared_at`. `intent.release` contient :

- `reader: release-invariants-v1`, `window_start`, `window_end` : plan antérieur à
  la fenêtre, fenêtre au plus 31 jours, close avant l'évaluation ;
- `population` : 1–16 tentatives `{id, before_artifact, candidate_artifact}` ; les
  artefacts sont des empreintes SHA-256, les IDs ASCII uniques de 1–80 caractères.
  Les phases pre et post examinent toutes deux candidate_artifact, avant puis après
  son application. before_artifact identifie seulement le contexte antérieur déclaré
  et revu : aucun examen de cette ancienne version ni effet causal n’est déduit ;
- `matrix` : 1–128 cellules `{id, rule_id, target, intent_sha256, context_sha256}`.
  Couples règle/cible uniques, IDs uniques, URL HTTP(S) explicites ; les 27 règles
  antérieures à TS41 sont qualifiées, jamais TS41 récursif. Intention et contexte
  sous-jacents sont liés au JSON compact trié UTF-8. L'attendu est pass pour chaque
  cellule ; les exemptions éventuelles restent non vérifiées dans ce profil ;
- `command` : `{argv, version, sha256, environment}`. argv contient 1–32 chaînes
  non vides ≤1 024 caractères ; version non vide et empreintes SHA-256 de l'outil
  et de l'environnement. Ces valeurs sont comparées aux reçus, jamais exécutées
  et ne prouvent pas à elles seules le contenu du binaire ou de la machine ;
- `policy` exactement `{pass:0, fail:1, inconclusive:2, pre:"block", post:"hold",
  overrides:"forbidden"}`. Premier profil strict : tout échec ou inconnu préalable
  bloque, un échec/inconnu après application exige un événement de suspension.
  Une dérogation observée contredit cette politique ; les politiques autorisant
  des dérogations restent hors de ce profil, sans effacement du défaut ;
- `negative` : `{id, artifact_sha256, required_failures}` ; ID distinct des
  tentatives, liste non vide d'IDs de cellules dont l'exercice doit produire fail.
  L'exercice précède les tentatives et utilise le même outil et la même matrice.

`release_runs` conserve au maximum 64 reçus : id unique, attempt_id, phase
`negative|pre|post`, artifact_sha256, trigger_event_id, started_at, ended_at,
complete (booléen), command identique au plan, input_json/input_sha256,
stdout_json/stdout_sha256, exit_code entier. Chaque chaîne JSON UTF-8 est limitée
à 512 Kio ; le cumul des chaînes d'un dossier à 4 Mio. Dates ordonnées dans la
fenêtre. Les entrées natives sont captures 1/2 avec règles/cibles explicites,
sans récursion TS41 ; les observations sous-jacentes sont datées dans l'exécution
et leurs intentions précèdent le plan TS41. Les cellules couvertes doivent être
exactement celles de la matrice ; une cellule omise reste inconnue.

L'interpréteur recalcule les règles sélectionnées sur les entrées conservées, avec
ses outils dont l'adaptateur archive les versions et empreintes. Il compare les
triples règle/cible/outcome de stdout, conserve les raisons originales et les
raisons recalculées séparément. Les versions exactes sont requises pour le rejeu ;
un rapport ancien n'est pas promu silencieusement. Si un runtime optionnel manque,
la limite reste visible ; elle ne permet pas d'accuser l'ancien résultat d'être
faux. Une différence d'outcome n'étaye fail que lorsque le recalcul est conclusif,
ou lorsque stdout prétend pass alors que l'entrée documente explicitement une
inconnue indépendante du runtime. Un recalcul indéterminé seul ne prouve pas une
falsification du rapport conservé.

`release_events` conserve raw_jsonl, sha256, exported_at. Au plus 128 lignes non
vides et 512 Kio, JSON strict sans clés dupliquées, IDs uniques, temps croissants.
Une ligne contient id, attempt_id, kind, at, artifact_sha256 et run_id. Types :
trigger-negative, negative-held, trigger-pre, blocked, deployed, trigger-post,
post-accepted, post-held, override. Les triggers précèdent l'exécution liée et
les actions la suivent. Chaque reçu possède exactement un trigger et une action
de sa phase ; tout événement orphelin, doublon ou phase étrangère rend la couverture
inconnue, sans effacer une contradiction indépendante. Une tentative appliquée exige les deux exécutions ; une
tentative explicitement bloquée n'invente pas d'exécution après déploiement.
L'absence dans un journal ne prouve jamais que le déploiement n'a pas eu lieu.
Un événement override est conservé et contredit la politique stricte.

`release_plan_review` : reviewer, assistance, reason, provenance
(human|human-assisted|synthetic-exercise), observed_at, binding_sha256, complete,
judgment (supported|contradiction|unknown). Liaison du JSON compact trié
`{url,intent}` ; revue après déclaration et avant fenêtre. Elle qualifie sélection,
représentativité et exclusions, pas une population implicite de tout le site.

`release_review` a les mêmes champs et qualifie la complétude de la population,
les liens de déclenchement, couche observée, horloges, identité déclarée du runner
et portée des événements. Liaison `{url,intent,release_events,release_runs}` ;
revue après export et exécutions, avant évaluation. Le jugement supported exige
`population_complete`, `attribution_supported`, `clock_supported` tous true.
Une revue rejetée est une contradiction ; absente/incomplète reste inconnue.
Les revues synthétiques imposent une livraison synthetic.

### Lecture des résultats et limites

Les cellules conservent leurs résultats sous-jacents. La décision de l'exécution
est fail si une cellule échoue, sinon inconclusive si une cellule manque/est
inconnue/non applicable, sinon pass. Elle ne transforme pas un défaut antérieur
au changement en nouvelle régression. Avant/après : pass→fail = contradiction
apparue dans la comparaison qualifiée ; fail→fail = défaut préexistant ;
inconclusive→fail = défaut après, apparition non établie. Ce vocabulaire ne prouve
aucune causalité du déploiement. Un état non comparable reste inconnu.

Le premier lecteur porte sur données natives TSEP et journal normalisé fourni.
Les exports propres à un fournisseur CI exigent un adaptateur qualifié distinct.
Les reçus, empreintes, dates et revues ne sont pas une authentification de CI ou
de production. Une CI préparée n'est pas une CI observée. Les exemples rédigés,
processus réellement exécutés en laboratoire et déploiements réels sont toujours
étiquetés séparément. Un dossier TS41 C n'affirme ni absence de défaut SEO ni
réussite d'un autre contrôle, indexation, classement ou couverture de tout site.

## English

Explicit `release-invariants-v1` assesses a process over prior declared deployment
**attempts**, not global SEO. Underlying failures stay visible: detecting and
blocking a defect can demonstrate an adequate process. Unknown is never success.
A01 covers prior plan/review; A02 traceable complete execution coverage and faithful
outputs; A03 negative rehearsal and phase-specific action. All three are semiAuto,
without automatic atomic exemptions. Independent contradictions survive other gaps.

The normal captures target identifies the scope by URL, observed_at, context and
intent.declared_at. intent.release has reader, a prior window of at most31 days,
1–16 population entries (id, before_artifact, candidate_artifact), 1–128 unique
matrix cells (id, rule_id, target, intent_sha256, context_sha256), command, policy
and negative rehearsal. IDs are unique bounded ASCII; artifact/tool/environment
hashes are SHA-256. Native intent/context bindings use sorted compact UTF-8 JSON.
Cells require pass and cover only the27 rules preceding TS41; no recursive TS41.
Exemptions are not treated as verified success by this first profile.

command contains argv (1–32 nonempty strings up to1024 characters), version,
sha256 and environment. These supplied identities are compared, never executed or
independently authenticated. policy is exactly pass0/fail1/inconclusive2, pre:block,
post:hold, overrides:forbidden. Both failure and unknown block before deployment;
both require an explicit hold after deployment. An observed override conflicts
with this strict profile; policies permitting overrides remain unqualified.
negative has a distinct id, artifact_sha256 and nonempty required_failures list of
matrix cell IDs. Its execution precedes attempts with the same command and matrix.

release_runs retains at most64 unique receipts: id, attempt_id, phase
negative/pre/post, artifact_sha256, trigger_event_id, started_at, ended_at,
complete, command, input_json/input_sha256, stdout_json/stdout_sha256, integer
exit_code. Each native JSON string is ≤512KiB; cumulative strings ≤4MiB. Ordered
times stay in the window. Native captures1/2 use explicit rules/targets without
TS41. Native observation times fall within the execution; native intent precedes
the TS41 plan. Exact matrix coverage is required; omitted cells remain unknown.

Selected rules are recalculated from supplied inputs with the adapter's recorded
interpreter/source identities. Compare rule/target/outcome triples, retaining
original and recalculated reasons separately. Exact tools are needed for replay;
old reports are not silently upgraded. Missing optional runtime cannot establish
that an old conclusive result was false. A conclusively recalculated mismatch can
fail; an inconclusive recalculation alone cannot prove report falsification.
An exit code 0 accompanying unchanged unknown outputs is a separate contradiction.

release_events retains raw_jsonl, sha256, exported_at: ≤128 nonempty strict JSON
lines, ≤512KiB, unique IDs and nondecreasing timestamps. Rows have id, attempt_id,
kind, at, artifact_sha256, run_id. Kinds are trigger-negative, negative-held,
trigger-pre, blocked, deployed, trigger-post, post-accepted, post-held, override.
Triggers precede linked runs; actions follow them. Applied attempts need pre/post;
explicitly blocked attempts do not invent post-runs. A missing event in a journal
never establishes that no deployment happened. Overrides remain visible failures
against this strict policy.

Both reviews retain reviewer, assistance, reason, provenance
human/human-assisted/synthetic-exercise, observed_at, binding_sha256, complete and
judgment supported/contradiction/unknown. Prior release_plan_review binds
{url,intent} between declaration and window start; it qualifies selection,
representativeness and exclusions. Later release_review binds
{url,intent,release_events,release_runs}, after export/runs and before assessment.
It qualifies population completeness, triggering, observed layer, clocks and
runner attribution; supported also requires population_complete,
attribution_supported and clock_supported all true. Rejection fails; missing,
incomplete or unknown review remains inconclusive. Fictional reviews require
synthetic delivery. Author identities remain supplied, not authenticated.

Both pre/post phases assess candidate_artifact around its application.
before_artifact is only supplied reviewed prior context, not an assessed old-code
baseline. Each receipt requires exactly one trigger and one phase-specific action;
orphan, duplicate or foreign-phase events leave coverage unknown, while independent
contradictions survive.

Run decision: fail if any selected cell fails, otherwise inconclusive for missing,
unknown or not-applicable cells, otherwise pass. Before/after pass→fail records a
new observed contradiction; fail→fail retains an existing defect;
inconclusive→fail cannot establish when it appeared. Neither establishes causality.
Different/unqualified contexts cannot support a comparison.

First profile: native TSEP outputs and supplied normalized journal. Provider-specific
CI exports need separately qualified adapters. Hashes/receipts do not authenticate
CI/production; configured CI is not observed CI. Keep authored exercises, actual
local processes and real deployments explicitly separate. TS41 C does not establish
SEO health, another control's success, indexing/ranking or whole-site coverage.
