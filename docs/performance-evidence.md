# Performance evidence / Preuves de performance — version 1

## Français

Draft.21 ajoute TS34-A01/A02/A03 et TS35-A01/A02. **C qualifie la documentation
et la méthode dans le périmètre, pas de bonnes performances.** Les mesures et
classes restent jointes aux résultats, au résumé de décision et à EARL. Les
lecteurs initiaux sont `crux-api-v1` et `lighthouse-json-v1`, en import hors ligne.
Search Console, RUM, PSI combiné et WebPageTest restent des sources possibles au
niveau du contrôle, mais ne sont pas convertis automatiquement par ces lecteurs.
Leur absence de prise en charge ne devient pas C ou NA.

### Entrées et attribution

Les entrées conservent le format captures 1 ou 2, une cible URL par dossier et
une intention `intent.performance.field` ou `intent.performance.lab`. L'intention
précède l'instant d'évaluation déclaré `target.observed_at`. Pour les diagnostics
de laboratoire, elle précède également les exécutions. Pour une cohorte terrain
historique, cela ne constitue pas un préenregistrement de la collecte des visites.

Chaque original garde `raw_json` (texte UTF-8 sans re-sérialisation), `sha256`,
`observed_at` (acquisition) et `source_url`. L'empreinte lie les octets fournis ;
elle n'authentifie ni le fournisseur ni l'acquisition. Au plus 4 Mio par original,
dans la limite globale d'entrée de 8 Mio. JSON dupliqué, invalide, non fini,
empreinte incorrecte, dates incohérentes ou format inconnu restent indéterminés.
Le dossier conserve les originaux même en cas de résultat défavorable.

### TS34 : données terrain

L'intention contient `granularity` (`url` ou `origin`), `key`, `form_factor`
(`PHONE`, `TABLET`, `DESKTOP` ou `ALL`) et `max_age_days` entier de 0 à 3660.
`field` contient le lecteur et la requête CrUX originale sans clé d'accès.

- **A01 — cohorte** : conserver l'identifiant demandé et retourné, appareil,
  `collectionPeriod.firstDate/lastDate` et contexte de population. Cible et clé
  prévue désignent exactement la cohorte retournée. Une normalisation n'est
  acceptée que si l'intention vise déjà l'URL normalisée et si le reçu CrUX lie
  `originalUrl` et `normalizedUrl`. Aucun repli URL→origine, groupe→URL ou
  mobile→tous appareils. Ces différences rendent l'attribution indéterminée.
  Une origine ne contient ni chemin ni requête.
  Une réponse de laboratoire ou PSI combinée présentée comme record CrUX est
  une contradiction de méthode. Une erreur API ne prouve pas une panne du site.
- **A02 — mesures** : classer les p75 LCP et INP en millisecondes entières,
  CLS comme chaîne décimale positive ou nulle, sans arrondi supplémentaire.
  Les bornes Good sont ≤2500 ms, ≤200 ms, ≤0,1 ; Poor est strictement >4000 ms,
  >500 ms, >0,25 ; l'intervalle restant est Needs improvement. Les décimales
  avec ou sans zéro avant le point sont acceptées, pas NaN, exposants ou signe.
  Une métrique absente reste inconnue ; FID et TBT ne remplacent pas INP.
  Une classification fournie, liée à la même source et contraire au p75, échoue
  même si une autre métrique manque. Une mesure mauvaise correctement classée
  réussit ce test documentaire.
- **A03 — décision** : conserver une revue fournie `field_review` avec auteur,
  provenance, date, empreinte de source et les trois métriques. Chaque entrée
  comporte la classe, un motif et une action (investigation, correction ou suivi).
  Revue manquante, non liée ou antérieure à l'acquisition : indéterminé. L'outil
  vérifie la présence et la liaison, pas la pertinence du jugement ni l'identité
  de l'auteur. Il ne rédige pas une revue humaine à la place d'une personne.

L'âge est une **différence de dates calendaires** entre la date UTC d'évaluation
et l'étiquette de fin de période, pas une durée exacte depuis la dernière visite.
La fin de période ne peut pas suivre l'acquisition de la source.
La fenêtre d'agrégation ne prouve ni des données chaque jour ni un effectif donné.
Les populations des trois métriques peuvent différer. Aucun avant/après, effet
causal de correction, stabilité future ou résultat de classement n'est déduit.

### TS35 : laboratoire

`intent.performance.lab` fixe URL demandée/finale, appareil, version Lighthouse,
identités de client/navigateur, âge maximal, nombre de passages (2 à 10) et
`settings` : `formFactor`, `throttlingMethod`, `throttling`, `screenEmulation`,
`emulatedUserAgent`, `disableStorageReset`, `blockedUrlPatterns`, `extraHeaders`.
Tous les paramètres de collecte présents sont comparés exactement au plan ; seul
`output`, qui choisit la présentation du rapport, est exclu. `gatherMode` doit
indiquer explicitement `navigation`. `lab.runs` conserve chaque original et son acquisition.

- **A01 — mesures attribuées** : nombre prévu de rapports distincts, datés après
  le plan, sans erreur d'exécution, mêmes paramètres déclarés et identités.
  Une URL demandée/finale contraire au plan échoue. Version, appareil, bridage
  ou navigateur différents rendent la série non comparable et indéterminée.
  LCP, CLS et TBT doivent conserver leurs unités natives. Le lecteur garde
  chaque valeur, minimum, maximum et médiane sans produire d'INP ni de verdict
  terrain. Répéter un fichier ne compte pas comme une nouvelle exécution.
- **A02 — diagnostic** : revue fournie `lab_review`, liée à la liste ordonnée
  des empreintes, datée après acquisition ; hypothèse, métriques concernées et
  prochaine mesure requises. `claims_field_cwv` et `claims_inp_from_tbt` doivent
  être explicitement faux. Une affirmation contraire, liée aux originaux Lighthouse, échoue même si un
  autre paramètre ou une mesure manque ; cette inconnue reste conservée.
  Revue absente ou incomplète : indéterminé. Une hypothèse conservée n'est pas
  une causalité démontrée. Le score Lighthouse reste dans l'original ; il ne
  remplace aucune de ces preuves.

Les répétitions documentent une dispersion avec un contexte déclaré. Elles ne
garantissent ni une reproductibilité statistique ni les conditions matérielles
réelles. Cette première édition ne compare pas deux campagnes avant/après et ne
qualifie pas les modes timespan/snapshot ou les formats autres que Lighthouse JSON.
Provenance des revues : `synthetic-exercise` pour les exercices, `supplied-review`
pour une revue effectivement fournie ; l'import vérifie sa cohérence avec l'accès
aux preuves. Aucune exemption atomique automatique.

## English

Draft.21 adds TS34-A01/A02/A03 and TS35-A01/A02. **C describes conforming evidence
documentation and method, not good performance.** Retained values/classes accompany
control results, gate summaries and EARL. Initial offline readers are `crux-api-v1`
and `lighthouse-json-v1`. Search Console, RUM, combined PSI and WebPageTest remain
possible control-level evidence sources but have no automatic conversion here.
Unsupported evidence cannot yield C or NA.

Captures input 1/2 retains one URL target, `intent.performance.field` or `.lab`,
and an explicit assessment time. Intent precedes assessment; lab intent also
precedes runs. Reassessment of a historical field cohort does not preregister its
visits. Originals retain UTF-8 `raw_json`, SHA-256, acquisition time and source URL.
Hashes bind supplied bytes, not authentic providers or collection. Limits: 4 MiB
per original and 8 MiB for the whole input. Invalid/duplicate-key JSON, nonfinite
numbers, broken hashes, inconsistent dates and unknown formats remain inconclusive.

TS34-A01 identifies the returned/requested cohort, aggregation dates, population
and device. Plan fields are granularity (url/origin), key, form_factor
(PHONE/TABLET/DESKTOP/ALL) and maximum age 0–3660 days. Target and planned key match
the returned cohort exactly. A normalized URL requires both a plan for that key
and the originalUrl/normalizedUrl binding. No URL-to-origin, group-to-URL or
mobile-to-all-device fallback. A lab/combined-PSI object mislabeled CrUX fails
method attribution; origins contain no path/query. API failure says nothing about site availability.

TS34-A02 classifies integer-ms LCP/INP p75 and nonnegative decimal-string CLS,
without new rounding. Good bounds are ≤2500 ms, ≤200 ms, ≤0.1; Poor bounds are
strictly >4000 ms, >500 ms, >0.25. Remaining values need improvement. A leading
zero before the decimal point is optional; signs/exponents/NaN are unsupported.
Missing metrics stay unknown; FID/TBT never substitute for INP. An explicitly
bound wrong classification fails despite another missing metric. Correctly
documented poor measurements pass this documentation test.

TS34-A03 requires a supplied field_review with author, provenance, date, source
hash and all three metrics, each retaining its class, reason and action. Missing,
unbound or pre-acquisition review is inconclusive. Presence/binding checks do not
validate the judgment or authenticate the reviewer; no human review is generated.
The field period cannot postdate source acquisition.
Age is the assessment UTC date minus the period's end-date label, not exact elapsed
time since a visit. Aggregation windows establish neither daily coverage nor sample
size; metric populations can differ. No before/after or causal/ranking conclusion.

TS35-A01 requires a prior lab plan for requested/final URL, device, Lighthouse
version, host/network user agents, maximum age, 2–10 distinct runs, and exact
formFactor/throttlingMethod/throttling/screenEmulation/emulatedUserAgent plus
disableStorageReset/blockedUrlPatterns/extraHeaders settings. Compare all supplied
collection settings against the plan; only presentation `output` is excluded.
An explicit `gatherMode: navigation` is required.
All complete reports postdate the plan and contain no runtime error. Wrong
requested/final URL fails; changed version, device, throttling or client makes the
series inconclusive. Retain native LCP/CLS/TBT units, individual values, min/max
and median. Duplicating a report is not another run; INP/field quality is not derived.

TS35-A02 retains a supplied lab_review bound to the ordered source hashes and
post-acquisition date, with hypothesis, measured metrics and next measurement.
claims_field_cwv and claims_inp_from_tbt must explicitly be false; contrary bound
claims fail when bound to Lighthouse originals even if an independent setting
or measure is unknown; the context uncertainty stays recorded. Missing/incomplete review remains inconclusive. A hypothesis is not
a proven cause. The original Lighthouse score cannot replace this evidence.

Repeated runs document spread under a declared setup, not statistical assurance,
authenticated hardware or future reproducibility. Initial readers do not compare
before/after campaigns, qualify timespan/snapshot or import other lab formats.
Review provenance is synthetic-exercise or supplied-review, checked against the
bundle's evidence access. There is no automatic atomic exemption.

## Sources

Consulted 2026-10-11; dated captures and scope in
[provenance](../provenance/performance-v1.json).

- [CWV thresholds](https://web.dev/articles/defining-core-web-vitals-thresholds)
- [Web Vitals and field/lab measurements](https://web.dev/articles/vitals)
- [CrUX API: identifiers, units and aggregation windows](https://developer.chrome.com/docs/crux/api)
- [Lab and field differences](https://web.dev/articles/lab-and-field-data-differences)

TSEP's evidence and review requirements are editorial protocol policy, not a
Google certification requirement. [Migration](migration-draft.21.md).
