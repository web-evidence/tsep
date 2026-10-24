# 0.3.0-draft.1 — delta depuis RC1 / delta from RC1

| Contrôle / Control | Règles nouvelles / New rules | Portée / Scope |
| --- | --- | --- |
| TS13 | TS13-A01, TS13-A02 | Population native, pages et stratégie fournies / Supplied native population, pages and strategy |
| TS14 | TS14-A01 | Date et modification significative documentée / Documented date and significant change |

30 contrôles portent 70 règles ; 14 restent sans règle exécutable. Les 67 règles RC1
et leurs versions sont conservées ; aucun usage réel ni réception applicative de
cette édition vérifiés. Contrats, limitations et NT : [TS13/TS14](sitemap-quality-evidence.md).
30 rule-bearing controls /70 rules; 14 without executable rules. The 67 RC1 rules
and versions are retained. No verified real use or application receipt for this
edition. The complete matrix below describes **RC1**, retained as the baseline.
Le tableau complet ci-dessous décrit **RC1**, conservé comme référence historique.

# État des 44 contrôles — TSEP 0.2.0-rc.1

État arrêté au 17 octobre 2026. Cette préversion conserve les 44 identifiants et tout le travail déjà intégré au candidat précédent ; elle ne lance aucun contrôle supplémentaire. TSEP n’est ni une certification ni une norme reconnue.

La source bilingue décrit 44 contrôles. Dans RC1, 28 contrôles ont 67 règles atomiques exécutables. Les 16 autres gardent leur description, leur procédure et leurs limites, sans règle atomique exécutable dans cette version.

## Tableau français

La colonne des cas compte uniquement les entrées agrégées de tests/fixtures/control-cases.json ; TS03 affiche aussi ses 13 cas synthétiques dédiés. Les corpus de règles et les laboratoires locaux spécialisés ne sont pas tous comptés dans cette colonne. Un compte nul signifie qu’aucun cas agrégé n’est déclaré ici, pas qu’il n’existe aucune documentation ou aucun composant préparatoire.

« Aucun usage réel vérifié » signifie qu’aucun diagnostic d’un site réel n’est établi par cette préversion. Les fixtures, sources .invalid, tests localhost/loopback et dossiers d’application synthétiques qualifient des mécanismes bornés ; ils ne prouvent ni l’état d’un site, ni son crawl, son indexation, son ranking ou son adoption. Les reçus applicatifs antérieurs sont liés à leurs archives et versions propres ; ils ne valent pas réception de RC1. La version de l’application reste indépendante de la version du protocole.

| Contrôle | Règles atomiques exécutables | Cas dans control-cases.json | Usage réel de site vérifié dans RC1 | Intégration applicative |
| --- | --- | ---: | --- | --- |
| TS01 — La page finale répond avec un code HTTP exploitable. | TS01-A01, TS01-A02 | 12 | Aucun usage réel vérifié | Parcours futur demandé ; non implémenté ni reçu dans RC1. |
| TS02 — Les redirections sont intentionnelles, directes et sans boucle. | TS02-A01, TS02-A02 | 5 | Aucun usage réel vérifié | Pilote app antérieur documenté ; scénarios synthétiques, aucun site réel qualifié. |
| TS03 — Les erreurs serveur et soft 404 ne remplacent pas une réponse explicite. | TS03-A01 | 3 + 13 TS03-specific synthetic response cases | Aucun usage réel vérifié | Reçu app r2 de draft.47 conservé ; tout reçu RC1 est distinct et lié au SHA exact de l’archive. |
| TS04 — La politique robots effective correspond à l’intention déclarée. | TS04-A01, TS04-A02 | 4 | Aucun usage réel vérifié | Réception app antérieure, périmètre synthétique ; archive RC1 non reçue. |
| TS05 — Une directive Disallow n’est jamais présentée comme une garantie de désindexation. | TS05-A01 | 4 | Aucun usage réel vérifié | Réception app antérieure, périmètre synthétique ; archive RC1 non reçue. |
| TS06 — Les zones sensibles refusent réellement l’accès au serveur. | TS06-A01 | 5 | Aucun usage réel vérifié | Réception app antérieure, périmètre synthétique ; archive RC1 non reçue. |
| TS07 — Les directives meta robots et X-Robots-Tag sont cohérentes avec l’objectif de la page. | TS07-A01, TS07-A02, TS07-A03 | 15 | Aucun usage réel vérifié | Parcours futur demandé ; non implémenté ni reçu dans RC1. |
| TS08 — Le statut d’indexation réel est vérifié dans Search Console. | TS08-A01, TS08-A02, TS08-A03 | 5 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS09 — Les exclusions volontaires ont un propriétaire et une justification. | Aucune règle atomique exécutable dans RC1 | 0 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS10 — Chaque page canonique publie une URL absolue, stable et cohérente. | TS10-A01, TS10-A02, TS10-A03, TS10-A04 | 16 | Aucun usage réel vérifié | Parcours futur demandé ; non implémenté ni reçu dans RC1. |
| TS11 — Les variantes réellement dupliquées convergent sans masquer des pages distinctes. | Aucune règle atomique exécutable dans RC1 | 0 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS12 — La canonique choisie par Google est comparée à celle déclarée. | TS12-A01, TS12-A02, TS12-A03 | 5 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS13 — Le sitemap contient uniquement des URL absolues et canoniques utiles. | Aucune règle atomique exécutable dans RC1 | 0 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS14 — lastmod reflète une modification significative de la page. | Aucune règle atomique exécutable dans RC1 | 0 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS15 — Les limites et découpages de sitemap sont respectés. | TS15-A01, TS15-A02, TS15-A03 | 4 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS16 — Chaque page importante reçoit au moins un lien interne crawlable. | TS16-A01 | 3 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS17 — Les liens essentiels utilisent un élément a avec href résoluble. | TS17-A01, TS17-A02 | 3 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS18 — La profondeur et les pages orphelines sont mesurées sur un périmètre explicite. | TS18-A01, TS18-A02, TS18-A03 | 3 | Aucun usage réel vérifié | Réception app antérieure, périmètre synthétique ; archive RC1 non reçue. |
| TS19 — Les paramètres, filtres et calendriers ne créent pas un espace infini. | Aucune règle atomique exécutable dans RC1 | 0 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS20 — La structure d’URL est lisible, stable et encodée correctement. | Aucune règle atomique exécutable dans RC1 | 0 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS21 — Les URL découvertes mais non indexées sont investiguées par famille. | Aucune règle atomique exécutable dans RC1 | 0 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS22 — Chaque variante hreflang pointe vers une URL indexable et canonique. | Aucune règle atomique exécutable dans RC1 | 0 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS23 — Les annotations hreflang sont réciproques et incluent la page elle-même. | TS23-A01 | 3 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS24 — x-default représente une destination neutre ou la variante par défaut assumée. | TS24-A01 | 3 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS25 — Le contenu critique existe dans le HTML source ou devient observable après rendu. | TS25-A01, TS25-A02 | 3 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS26 — Les ressources nécessaires au rendu ne sont pas bloquées ni en erreur. | Aucune règle atomique exécutable dans RC1 | 0 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS27 — Les états et routes SPA produisent des URL partageables et des réponses serveur cohérentes. | Aucune règle atomique exécutable dans RC1 | 0 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS28 — Le document expose une structure HTML compréhensible sans dépendre de son apparence. | Aucune règle atomique exécutable dans RC1 | 0 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS29 — Les contenus essentiels restent disponibles lorsque scripts ou styles échouent. | Aucune règle atomique exécutable dans RC1 | 0 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS30 — Les métadonnées essentielles sont uniques, visibles et cohérentes avec la page. | Aucune règle atomique exécutable dans RC1 | 0 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS31 — Le JSON-LD décrit des entités visibles et appropriées au contenu. | TS31-A01, TS31-A02, TS31-A03 | 3 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS32 — Les identifiants @id relient les mêmes entités sans créer de doublons. | TS32-A01, TS32-A02, TS32-A03 | 3 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS33 — Les erreurs, avertissements et usages non pris en charge sont distingués. | TS33-A01, TS33-A02, TS33-A03 | 3 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS34 — Les Core Web Vitals terrain sont documentés et classés au 75e percentile. | TS34-A01, TS34-A02, TS34-A03 | 3 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS35 — Les tests de laboratoire servent au diagnostic, pas à simuler le terrain. | TS35-A01, TS35-A02 | 3 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS36 — Le suivi relie Search Console, logs et déploiements à des dates de décision. | TS36-A01, TS36-A02, TS36-A03 | 8 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS37 — HTTPS, HSTS et les ressources intégrées ne créent ni erreur de certificat ni contenu mixte. | Aucune règle atomique exécutable dans RC1 | 0 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS38 — Les variantes d’hôte, de casse et de slash convergent vers une règle unique. | Aucune règle atomique exécutable dans RC1 | 0 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS39 — Le CDN, Vary et la géolocalisation ne servent pas des signaux SEO contradictoires. | TS39-A01, TS39-A02, TS39-A03 | 5 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS40 — Les méthodes hreflang utilisées sont complètes et cohérentes. | Aucune règle atomique exécutable dans RC1 | 0 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS41 — Les invariants SEO critiques sont rejoués automatiquement avant et après déploiement. | TS41-A01, TS41-A02, TS41-A03 | 5 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |
| TS42 — Chaque agent automatisé est gouverné selon son usage documenté. | TS42-A01, TS42-A02, TS42-A03 | 5 | Aucun usage réel vérifié | Réception app antérieure, périmètre synthétique ; archive RC1 non reçue. |
| TS43 — L’accès des crawlers autorisés est testé avec leur chaîne complète et rapproché des journaux. | TS43-A01, TS43-A02, TS43-A03 | 5 | Aucun usage réel vérifié | Réception app antérieure, périmètre synthétique ; archive RC1 non reçue. |
| TS44 — Le contenu critique et ses preuves restent accessibles sans dépendre d’une exécution JavaScript non documentée. | TS44-A01, TS44-A02, TS44-A03 | 5 | Aucun usage réel vérifié | Aucune réception applicative RC1 revendiquée. |

## English status

State frozen on 17 October 2026. This release candidate retains all 44 identifiers and work already integrated into the preceding candidate; it starts no additional control. TSEP is neither a certification nor a recognized standard.

The bilingual source describes 44 controls. In RC1, 28 controls have 67 executable atomic rules. The other 16 retain their descriptions, procedures and limitations without an executable atomic rule in this edition.

## English table

The case column counts only aggregate entries in tests/fixtures/control-cases.json; TS03 also lists its 13 dedicated synthetic cases. Specialized rule corpora and local laboratories are not all counted in that column. Zero means no aggregate case is declared there, not that no documentation or preparatory component exists.

“None verified” means this prerelease establishes no real-site diagnosis. Fixtures, .invalid sources, localhost/loopback tests and synthetic application dossiers qualify bounded mechanisms; they establish no site's condition, crawl, indexing, ranking or adoption. Prior application receipts remain bound to their own archives and versions; they are not RC1 receipts. The application keeps its own version.

| Control | Executable atomic rules | Cases in control-cases.json | Real-site use verified in RC1 | Application integration |
| --- | --- | ---: | --- | --- |
| TS01 — The final page returns an actionable HTTP status code. | TS01-A01, TS01-A02 | 12 | None verified | Requested future flow; not implemented or received in RC1. |
| TS02 — Redirects are intentional, direct and loop-free. | TS02-A01, TS02-A02 | 5 | None verified | Earlier app pilot documented; synthetic scenarios, no real site qualified. |
| TS03 — Server errors and soft 404s do not replace an explicit response. | TS03-A01 | 3 + 13 TS03-specific synthetic response cases | None verified | Draft.47 app r2 receipt retained; any RC1 receipt is separate and bound to the exact archive SHA. |
| TS04 — The effective robots policy matches declared intent. | TS04-A01, TS04-A02 | 4 | None verified | Prior app receipt, synthetic scope; RC1 archive not received. |
| TS05 — A Disallow rule is never presented as a guarantee of deindexing. | TS05-A01 | 4 | None verified | Prior app receipt, synthetic scope; RC1 archive not received. |
| TS06 — Sensitive areas genuinely deny access at server level. | TS06-A01 | 5 | None verified | Prior app receipt, synthetic scope; RC1 archive not received. |
| TS07 — Robots meta directives and X-Robots-Tag match the page objective. | TS07-A01, TS07-A02, TS07-A03 | 15 | None verified | Requested future flow; not implemented or received in RC1. |
| TS08 — The actual indexing status is checked in Search Console. | TS08-A01, TS08-A02, TS08-A03 | 5 | None verified | No RC1 application receipt claimed. |
| TS09 — Intentional exclusions have an owner and a rationale. | No executable atomic rule in RC1 | 0 | None verified | No RC1 application receipt claimed. |
| TS10 — Each canonical page publishes an absolute, stable and consistent URL. | TS10-A01, TS10-A02, TS10-A03, TS10-A04 | 16 | None verified | Requested future flow; not implemented or received in RC1. |
| TS11 — Genuine duplicate variants converge without hiding distinct pages. | No executable atomic rule in RC1 | 0 | None verified | No RC1 application receipt claimed. |
| TS12 — Google’s selected canonical is compared with the declared canonical. | TS12-A01, TS12-A02, TS12-A03 | 5 | None verified | No RC1 application receipt claimed. |
| TS13 — The sitemap contains only useful absolute canonical URLs. | No executable atomic rule in RC1 | 0 | None verified | No RC1 application receipt claimed. |
| TS14 — lastmod reflects a significant change to the page. | No executable atomic rule in RC1 | 0 | None verified | No RC1 application receipt claimed. |
| TS15 — Sitemap size and segmentation limits are respected. | TS15-A01, TS15-A02, TS15-A03 | 4 | None verified | No RC1 application receipt claimed. |
| TS16 — Every important page receives at least one crawlable internal link. | TS16-A01 | 3 | None verified | No RC1 application receipt claimed. |
| TS17 — Essential links use an a element with a resolvable href. | TS17-A01, TS17-A02 | 3 | None verified | No RC1 application receipt claimed. |
| TS18 — Depth and orphan pages are measured within an explicit scope. | TS18-A01, TS18-A02, TS18-A03 | 3 | None verified | Prior app receipt, synthetic scope; RC1 archive not received. |
| TS19 — Parameters, filters and calendars do not create an infinite URL space. | No executable atomic rule in RC1 | 0 | None verified | No RC1 application receipt claimed. |
| TS20 — The URL structure is readable, stable and correctly encoded. | No executable atomic rule in RC1 | 0 | None verified | No RC1 application receipt claimed. |
| TS21 — Discovered but unindexed URLs are investigated by family. | No executable atomic rule in RC1 | 0 | None verified | No RC1 application receipt claimed. |
| TS22 — Each hreflang variant points to an indexable canonical URL. | No executable atomic rule in RC1 | 0 | None verified | No RC1 application receipt claimed. |
| TS23 — hreflang annotations are reciprocal and include the current page. | TS23-A01 | 3 | None verified | No RC1 application receipt claimed. |
| TS24 — x-default represents a neutral destination or an explicit default variant. | TS24-A01 | 3 | None verified | No RC1 application receipt claimed. |
| TS25 — Critical content exists in source HTML or becomes observable after rendering. | TS25-A01, TS25-A02 | 3 | None verified | No RC1 application receipt claimed. |
| TS26 — Resources required for rendering are neither blocked nor failing. | No executable atomic rule in RC1 | 0 | None verified | No RC1 application receipt claimed. |
| TS27 — SPA states and routes produce shareable URLs and consistent server responses. | No executable atomic rule in RC1 | 0 | None verified | No RC1 application receipt claimed. |
| TS28 — The document exposes an understandable HTML structure independently of appearance. | No executable atomic rule in RC1 | 0 | None verified | No RC1 application receipt claimed. |
| TS29 — Essential content remains available when scripts or styles fail. | No executable atomic rule in RC1 | 0 | None verified | No RC1 application receipt claimed. |
| TS30 — Essential metadata is unique, visible and consistent with the page. | No executable atomic rule in RC1 | 0 | None verified | No RC1 application receipt claimed. |
| TS31 — JSON-LD describes entities that are visible and appropriate to the content. | TS31-A01, TS31-A02, TS31-A03 | 3 | None verified | No RC1 application receipt claimed. |
| TS32 — Stable @id values connect the same entities without creating duplicates. | TS32-A01, TS32-A02, TS32-A03 | 3 | None verified | No RC1 application receipt claimed. |
| TS33 — Errors, warnings and unsupported uses are distinguished. | TS33-A01, TS33-A02, TS33-A03 | 3 | None verified | No RC1 application receipt claimed. |
| TS34 — Field Core Web Vitals are documented and classified at the 75th percentile. | TS34-A01, TS34-A02, TS34-A03 | 3 | None verified | No RC1 application receipt claimed. |
| TS35 — Laboratory tests support diagnosis rather than simulate field data. | TS35-A01, TS35-A02 | 3 | None verified | No RC1 application receipt claimed. |
| TS36 — Monitoring connects Search Console, logs and deployments to decision dates. | TS36-A01, TS36-A02, TS36-A03 | 8 | None verified | No RC1 application receipt claimed. |
| TS37 — HTTPS, HSTS and embedded resources create neither certificate errors nor mixed content. | No executable atomic rule in RC1 | 0 | None verified | No RC1 application receipt claimed. |
| TS38 — Host, case and trailing-slash variants converge on one rule. | No executable atomic rule in RC1 | 0 | None verified | No RC1 application receipt claimed. |
| TS39 — The CDN, Vary and geolocation do not serve contradictory SEO signals. | TS39-A01, TS39-A02, TS39-A03 | 5 | None verified | No RC1 application receipt claimed. |
| TS40 — The hreflang methods in use are complete and consistent. | No executable atomic rule in RC1 | 0 | None verified | No RC1 application receipt claimed. |
| TS41 — Critical SEO invariants are replayed automatically before and after deployment. | TS41-A01, TS41-A02, TS41-A03 | 5 | None verified | No RC1 application receipt claimed. |
| TS42 — Each automated agent is governed according to its documented purpose. | TS42-A01, TS42-A02, TS42-A03 | 5 | None verified | Prior app receipt, synthetic scope; RC1 archive not received. |
| TS43 — Access for authorized crawlers is tested with the full user-agent string and reconciled with logs. | TS43-A01, TS43-A02, TS43-A03 | 5 | None verified | Prior app receipt, synthetic scope; RC1 archive not received. |
| TS44 — Critical content and evidence remain accessible without undocumented JavaScript execution. | TS44-A01, TS44-A02, TS44-A03 | 5 | None verified | No RC1 application receipt claimed. |

## Faits de qualification / Qualification facts

- TS03-A01 reste une seule règle semi-automatique : plan préalable lié par empreinte, états de routes existing/removed/nonexistent, captures HTTP fictives .invalid et marqueurs littéraux UTF-8.
- Treize cas TS03 dédiés couvrent accord, contradictions, entrée absente/ambiguë, 206/304, date future, empreinte invalide et hôte non synthétique. La contradiction complète reste fail même si une autre entrée est manquante ; le contrôle complet n’est pass que si toute la matrice déclarée est couverte.
- Le reçu applicatif 0.1.0-draft.47 r2 a gardé 12 résultats r1 sans les relancer et évalué un cas supplémentaire ; son résultat atomique inconclusive et son statut de contrôle NT sont distincts. Tout reçu d’intégration RC1 est conservé dans le dossier de release séparé, lié au SHA exact de l’archive importée.
- Aucun usage de site réel n’est ajouté par cette version. Les vérifications déterministes du moteur sont rapportées séparément dans les notes de version et ne remplacent ni une observation réelle ni une revue humaine requise.
- Le tableau conserve les autres contrôles déjà intégrés à la source et aux outils. La suite de l’intégration applicative demandée est priorisée TS01, TS04, puis TS07 et TS10, sans nouveau contrôle ni changement de version de l’application.
- TS03-A01 remains a single semi-automated rule: fingerprint-bound prior plan, existing/removed/nonexistent route states, fictional .invalid HTTP captures and literal UTF-8 markers.
- Thirteen dedicated TS03 cases cover agreement, contradictions, missing/ambiguous input, 206/304, future dates, invalid fingerprints and non-synthetic hosts. A complete contradiction remains a fail when another input is missing; the full control is pass only when its declared matrix is covered.
- The 0.1.0-draft.47 r2 app receipt retained 12 r1 results without rerunning them and assessed one additional case; its inconclusive atomic result and NT control status remain distinct. Any RC1 intake receipt is kept in a separate release record bound to the exact imported archive SHA.
- This edition adds no real-site use. Deterministic engine checks are reported separately in release notes and do not replace a real observation or required human review.
- The table retains other work already integrated in the source and tools. The requested future app integration order is TS01, TS04, then TS07 and TS10, with no new control or application-version change.
