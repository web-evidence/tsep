# TS36 — Release follow-up evidence / Preuves de suivi, profil 1

## Français

`release-monitoring-v1` qualifie un dossier de suivi d'un seul changement déclaré,
avec trois règles semiAuto : A01 plan/référence/déploiement ; A02 observations
aux échéances ; A03 comparaisons, anomalies et décisions fournies. C ne signifie
ni absence de défaut, ni indexation, ni causalité, ni TS08/TS12 conformes. Ce premier
profil strict comprend baseline, d1, d7 et d30 ; les autres calendriers ou exemptions
nécessitent un profil distinct. Les journées sont des durées de 24 heures UTC,
pas des dates civiles locales. Aucun NA atomique automatique.

### Plan préalable et changement

La cible captures 2 reprend `intent.inspection`, `inspection_synthetic`, context,
url et observed_at de TS08 pour 1–16 URL ; ces URL sélectionnées ne couvrent pas
implicitement le site. Les objectifs, raisons de sélection, connaissances antérieures
et sources restent obligatoires. `intent.monitoring` contient reader, release_id,
environment, before_artifact_sha256, after_artifact_sha256, risk, schedule_reason,
baseline_start, baseline_end, deployment_window_start, deployment_window_end,
window_hours (entier 1–24), review_grace_hours (entier 1–168), log_layer et
user_agents (1–16 chaînes distinctes non blanches, chacune ≤2048 caractères).
Les IDs sont ASCII bornés à 80 caractères et les empreintes sont SHA-256 minuscules.

Déclaration ≤ début baseline < fin baseline ≤ début fenêtre de déploiement < fin,
fenêtre de déploiement ≤7 jours. Baseline dure exactement window_hours. Aucun
recalage rétroactif du plan. La revue `monitoring_plan_review` lie `{url,intent}`,
après déclaration et avant baseline_start ; elle qualifie selection, objectives,
schedule et logging : supported / contradiction / unknown. Métadonnées de revue
TS08 : reviewer, assistance, provenance, observed_at, reason, complete, binding_sha256.
Les dates, empreintes et identités sont déclarées et non authentifiées.

`monitoring_deployment` contient provenance (synthetic-exercise ou supplied-release),
description, observed_at et body `{raw_text,sha256}`. Son JSON strict, ≤512 Kio,
contient release_id, environment, before_artifact_sha256, after_artifact_sha256,
deployed_at et other_changes (liste explicite ≤16 objets at/description/source).
Les champs d'identité différents du plan établissent une contradiction A01. Le
déploiement doit suivre la fin de baseline et se trouver dans la fenêtre prévue ;
un déploiement déclaré antérieur à la baseline contredit A01. Un reçu absent,
incomplet ou non intègre reste inconclusive. Export après déploiement, avant
évaluation. La liste vide de changements ne prouve pas l'absence de tout autre facteur.
La baseline doit aussi être fournie avant le déploiement ; une baseline enregistrée
après celui-ci ne devient pas antérieure en changeant son étiquette.

### Échéances et pièces

`monitoring_checkpoints` est une liste de 0–4 dossiers à IDs uniques parmi baseline,
d1,d7,d30. Aucune substitution ou échéance étrangère. Chaque dossier contient id,
observed_at, inspection_records natifs TS08 et logs. La fenêtre baseline est celle
du plan ; dN couvre [déploiement + N×24 h, début + window_hours). Son évaluation
locale est entre fin de fenêtre et fin + review_grace_hours, avant l'évaluation
globale. La fraîcheur API est calculée à cette évaluation locale historique, pas
réinterprétée comme état actuel. Le lecteur ne collecte rien et ne décale aucune date.

Chaque API est acquise dans sa fenêtre fermée au début et ouverte à la fin, puis
qualifiée par TS08-A02, avec les mêmes limites de champs/âges. Une URL de requête
explicitement différente échoue ; erreurs API, valeurs inconnues, pièces altérées
et âge excessif restent inconnus. Aucun test live. Acquisition et lastCrawlTime
restent distincts ; le dernier crawl ne date pas chacun des champs. Un crawl avant
le déploiement est conservé comme tel, sans effet du changement déduit.

`logs` contient reader=`supplied-monitoring-log-v1`, format=`normalized-jsonl`,
provenance (synthetic-exercise ou supplied-log), description, normalization_source,
layer, window_start, window_end, observed_at, complete, raw_jsonl et sha256.
Le profil lit un export normalisé fourni, pas un format fournisseur arbitraire.
Conserver sa méthode de normalisation/source ; aucune commande n'est exécutée.
La fenêtre doit correspondre exactement à celle de l'échéance, layer au plan,
complete=true et fin ≤ observed_at ≤ date du dossier. Le journal UTF-8 est limité
à 512 Kio et 10000 lignes non vides. JSON strict sans doublons de clés ; chaque
ligne possède id unique, at, url HTTP(S), method ASCII, user_agent non blanc et
status entier 100–599. Les temps sont dans la fenêtre [début,fin), en ordre non
décroissant. Une ligne non qualifiée refuse l'inventaire entier, sans total partiel.
Un journal vide explicitement complet est permis, sous réserve de la revue fournie.

Compter séparément pour chaque URL exacte les GET dont le User-Agent correspond
exactement à une chaîne du plan : requests et server_errors (500–599). Conserver
les lignes exclues ; aucun classement d'opérateur par substring/IP/DNS implicite.
Zéro signifie zéro ligne correspondante dans cet export ; il ne prouve pas absence
de visites Google. La complétude de la couche, filtres, horloges et normalisation
est qualifiée par la revue, pas authentifiée. Les fenêtres ont la même durée ;
les différences de comptes ne prouvent ni trafic global ni changement de demande.

Une échéance future reste inconclusive, même avec une étiquette « terminée ».
Une échéance passée sans pièce reste aussi inconclusive ; le retard ne fabrique
ni un défaut SEO ni une absence de suivi. Les dossiers disponibles et contradictions
indépendantes sont conservés. C du contrôle exige les quatre échéances intégrales.

### Revues et décisions

`monitoring_reviews` comprend exactement une revue par échéance. Chaque revue lie
`{url,intent,deployment:monitoring_deployment,checkpoint:<dossier>}` ; après toutes
les acquisitions/API/exports de cette échéance, avant l'évaluation globale. Les
métadonnées TS08 et la cohérence de provenance sont obligatoires. Cette revue est
fournie, jamais créée par le lecteur. `claims` comprend api et logs, chacun indexé
par les URL exactes du plan. api[URL] est le verdict Google littéral PASS/FAIL/NEUTRAL ;
logs[URL] contient requests et server_errors, entiers non négatifs. Un champ faux
contre une lecture complète connue échoue A03, même si une autre surface manque.
Une lecture inconnue ne prouve jamais que la revendication est fausse.

Chaque revue qualifie interpretation, anomalies, log_completeness et clock_scope
(supported / contradiction / unknown), décrit objective_relation (aligned/different)
et temporal_scope=`reported-index-and-separate-log-windows`. Les revendications
current-live-page, all-fields-at-last-crawl ou authenticated-googlebot à la place
de cette portée sont des contradictions. L'explication contient kind
observation/hypothesis/unresolved et text ; une hypothesis exige test. Une causalité
affirmée sans profil de preuve reste inconnue. Décision fournie accept, correct
(avec action), monitor (criterion et due_at après revue), ou revise-objective
(new_plan_reference), toujours owner et reason. Une situation défavorable expliquée
et traitée peut accompagner C documentaire ; aucune correction n'est exécutée.

`monitoring_closure_review` lie `{url,intent,monitoring_deployment,monitoring_checkpoints,
monitoring_reviews}`. Même métadonnées, après tous les dossiers/revues disponibles,
avant évaluation. Son champ completed doit être true pour clore le cycle. Si des
fenêtres futures à la date de la revue de clôture sont connues et completed=true, la clôture est contradictoire ;
completed=false conserve l'inconclusive. Un simple manque sans contradiction connue
reste inconclusive. Le jugement causality=not-established est requis ; established
sans preuve indépendante reconnue par ce profil reste inconclusive.

Le rapport conserve les verdicts Google et comptes par période, puis leurs
comparaisons baseline→dN (verdict identique/différent/inconnu, deltas de comptes
seulement si les deux inventaires sont connus). Ces changements observés ne sont
ni une causalité de déploiement ni une preuve de régression globale. Les avis
« signés » sont des décisions identifiées, datées et liées aux pièces ; le lecteur
ne vérifie pas de signature cryptographique ou d'identité du signataire.

Bornes : cible et diagnostic complet ≤4 Mio chacun ; dépassement = inconclusive
sans conclusion partielle conservée. Les limites globales captures s'appliquent.
Données réelles restricted, exercices synthetic ; ne jamais rebaptiser une revue
rédigée en revue humaine. Une application réelle commencée le 12 octobre ne peut
avoir atteint J+7/J+30 le 14. Le profil ne crée ni automation ni future observation.

Références techniques : [inspection Google](https://support.google.com/webmasters/answer/9012289?hl=en),
[vérification des requêtes](https://developers.google.com/crawling/docs/crawlers-fetchers/verify-google-requests),
[budget de crawl](https://developers.google.com/crawling/docs/crawl-budget).
Les délais et décisions TSEP sont un choix éditorial, pas une prescription Google.

## English

`release-monitoring-v1` assesses a documentary follow-up for one declared release.
Three semiAuto rules: A01 prior plan/baseline/deployment, A02 due observations,
A03 supplied comparisons/anomaly decisions. C establishes neither healthy SEO,
indexing, causality nor TS08/TS12 conformity. This strict first profile requires
baseline,d1,d7,d30; alternative calendars/exemptions need another profile. Days
mean elapsed 24-hour UTC durations, not local calendar dates. No atomic automatic NA.

Use captures2 with TS08 intent.inspection, inspection_synthetic, context, URL and
assessment time for 1–16 selected URLs, with prior objectives/sources/knowledge.
intent.monitoring fields: reader, release_id, environment, before_artifact_sha256,
after_artifact_sha256, risk, schedule_reason, baseline_start/end,
deployment_window_start/end, integer window_hours1–24, review_grace_hours1–168,
log_layer and1–16 unique nonblank user_agents ≤2048 characters each. IDs use bounded
ASCII≤80; hashes lowercase SHA-256. Declaration≤baseline start<end≤deployment-window
start<end, deployment window≤7 days. Baseline duration equals window_hours.
monitoring_plan_review binds {url,intent}, between declaration and baseline start,
and supplies selection/objectives/schedule/logging judgments supported/contradiction/
unknown. All reviews use TS08 metadata: reviewer, assistance, provenance, observed_at,
reason, complete, binding_sha256. Dates/hashes/identities are not authenticated.

monitoring_deployment has provenance synthetic-exercise|supplied-release, description,
observed_at and body {raw_text,sha256}. Strict JSON≤512KiB contains release_id,
environment, before_artifact_sha256, after_artifact_sha256, deployed_at and explicit
other_changes list≤16 of at/description/source. Identity mismatch with the plan
fails A01. Deployment before baseline end fails; otherwise it must be within its
planned window. Missing/incomplete/altered receipts are inconclusive. Export follows
deployment and precedes assessment. Empty changes do not prove no other influences.
Baseline must itself have been recorded before deployment; relabeling a later
observation does not create a pre-change baseline.

monitoring_checkpoints is a list of0–4 unique baseline/d1/d7/d30 entries, each with
id, observed_at, TS08 inspection_records and logs. Windows: declared baseline;
dN=[deployment+N×24h, start+window_hours). Local historical assessment lies between
window end and end+review_grace_hours, no later than outer assessment. API freshness
is assessed at that local historical time, never promoted to current state. Acquire
API within [start,end), retaining TS08-A02 native qualification, fields and ages.
Explicit request/member mismatch fails; API errors, unknown fields, altered evidence
or excessive age remain unknown. Inspection is not live; acquisition and crawl dates
remain distinct. A pre-release reported crawl cannot establish a release effect.

logs fields: reader=supplied-monitoring-log-v1, format=normalized-jsonl,
provenance synthetic-exercise|supplied-log, description, normalization_source, layer,
window_start/end, observed_at, complete, raw_jsonl, sha256. This is supplied normalized
JSONL, not an arbitrary provider log format. Retain normalization method/source;
execute no command. Exact planned window/layer, complete=true, end≤export≤checkpoint
time. UTF-8≤512KiB/10000 nonblank strict JSON lines, unique IDs and no duplicate keys.
Each line: id, at, HTTP(S) url, ASCII method, nonblank user_agent, integer status100–599.
Ordered times belong to [start,end). Any unreadable line refuses the entire inventory,
without partial counts. Explicit complete empty logs are allowed, subject to review.
For each exact selected URL, count GETs matching one exact planned User-Agent:
requests and server_errors(status500–599). Retain excluded lines. No inferred operator
identity from substrings/IP/DNS. Zero is only zero matching supplied records, never
proof of no Google visits. Reviewed layer/filter/clock/normalization completeness
is not authenticated. Equal-duration count deltas are not whole-site traffic demand.

Future stages remain inconclusive, regardless of labels; missing past evidence also
remains inconclusive, never inferred SEO failure or absence of follow-up. Preserve
available stages and independent contradictions. Whole-control C requires all four.

monitoring_reviews has exactly one per stage, binding
{url,intent,deployment:monitoring_deployment,checkpoint:<entry>}, after all stage
acquisitions/API/exports and before assessment. Metadata/provenance as above. Reader
creates no review. claims.api and claims.logs have exact planned URL keys: API claims
are literal PASS/FAIL/NEUTRAL; log claims contain nonnegative integer requests and
server_errors. A wrong known complete claim fails A03 despite another unknown;
unknown evidence cannot establish a false claim. Each review supplies interpretation,
anomalies, log_completeness, clock_scope judgments; objective_relation aligned/different;
temporal_scope=reported-index-and-separate-log-windows. current-live-page,
all-fields-at-last-crawl or authenticated-googlebot temporal claims fail. Explanation:
kind observation/hypothesis/unresolved plus text, and test for hypothesis. Unsupported
established causality stays inconclusive. Supplied decision accept/correct(action)/
monitor(criterion and future due_at)/revise-objective(new_plan_reference), with owner
and reason. Adverse observations properly documented may accompany C; no action runs.

monitoring_closure_review binds {url,intent,monitoring_deployment,monitoring_checkpoints,
monitoring_reviews}, after all available records/reviews, before assessment. completed
must be true for closure. Known windows still future at closure-review time plus completed=true contradict closure;
false or mere missing evidence remains inconclusive. causality=not-established is
required; established without a supported independent proof profile is inconclusive.
Reports retain API verdicts/counts and baseline→dN observations: same/different/unknown
verdict, count deltas only when both complete inventories are known. No causal or
global regression claim. Signed decisions mean identified/dated/evidence-bound
supplied judgments, not verified cryptographic signatures or signer identity.

Target and complete diagnostic each≤4MiB; overflow is inconclusive without partial
conclusion. Captures global bounds also apply. Real evidence is restricted, authored
exercises synthetic; never relabel fictional reviews as human. A real October12
start cannot reach D+7/D+30 on October14. No automation or future observation is created.
Official technical references are linked above; TSEP timing/decisions are editorial,
not Google requirements.
