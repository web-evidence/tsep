# Control implementation status / État de développement des contrôles

## Current snapshot / État actuel — 2026-10-11

La version locale est **0.1.0-draft.25**. Les versions des outils sont distinctes :
interpréteur **25**, adaptateur de captures **26**, rejeu **3**. Ces numéros ne
prouvent ni une publication distante ni une version stable 1.0. Chaque dossier
historique reste lié à sa version et à ses empreintes ; il n'est jamais remplacé.

Le programme actif porte sur **quatre contrôles approfondis : TS04, TS02, TS07,
TS10**, avec TS01 comme socle. Il remplace la cible antérieure de dix contrôles.
Le 11 octobre, Bertrand a ajouté explicitement la performance : TS34 et TS35.
Le même jour, il a demandé les agents IA après les performances : TS42, puis TS43 et TS44.
Le même jour, il a autorisé TS41, TS39, TS36 et TS31–33. TS41 est intégré en premier ; les cinq autres restent à développer.
La source décrit **44 contrôles**. **Onze** disposent de règles atomiques
exécutables : TS01 (2), TS02 (2), TS04 (2), TS07 (3), TS10 (4), TS34 (3), TS35 (2), TS41 (3), TS42 (3), TS43 (3), TS44 (3),
soit **30 règles**. Les quatre priorités SEO en représentent 11. Les 33 autres sont décrits,
sans le même niveau de règles et d'outillage exécutables.

| Contrôle | Méthode exécutable disponible | Application réelle encore incomplète |
| --- | --- | --- |
| TS01, socle | HTTP final, identité selon critères préalables, rapport et rejeu | Les captures Edikka conservées restent NT, notamment à cause de noscript non vide. La proposition lexicale n'est pas qualifiée comme deux lectures navigateur. Ce refus ne démontre pas un défaut SEO. |
| TS02 | Plan préalable, import d'une décision fournie, liaison aux captures, comparaison des chaînes | Décision réelle du responsable, collecte ultérieure et résultats dans le périmètre décidé |
| TS04 | Lecteur robots partagé, profils explicites, matrice par origine, ressources requises, parcours de revue et rejeu | Seize chemins autorisés selon la matrice opérateur capturée ; revues motivées manquantes, contrôle entier non établi |
| TS07 | Directives HTTP/source/rendu, hypothèses source distinctes, objectifs de permissions texte/image/vidéo préalables | Trois sources examinées ne remplacent pas les états rendus attribués et revues exigés ; aucune observation Google déduite |
| TS10 | Canonical HTTP avec contexte, source, rendu, sitemaps et liens ; familles déclarées et rejeu | Les populations des campagnes sont distinctes ; qualification des familles, états rendus et revues de contenu encore nécessaires |
| TS34 | Import CrUX hors ligne : cohorte, période, appareil, p75 et classes ; décision fournie liée aux sources | Aucun nouveau relevé terrain Edikka ; autres formats non qualifiés ; C documentaire ne signifie pas bonnes performances |
| TS35 | Série Lighthouse : plan préalable, conditions exactes, mesures, dispersion et hypothèse fournie | Aucune nouvelle campagne réelle Edikka ; autres formats et comparaison avant/après non qualifiés |
| TS41 | Plan préalable, reçus natifs recalculés, couverture de la population et réaction aux échecs/inconnues | Cas rédigés vérifiés ; laboratoire de processus réel et application Edikka encore à produire. C ne garantit pas la santé SEO |
| TS42 | Correspondances liées aux sources et revues, décisions du responsable, arbitrages et lecture robots bornée | Aucune décision réelle du responsable Edikka ni visite d’agent établie ; autres mécanismes non qualifiés |
| TS44 | Inventaire préalable, chemin public sans JS, valeurs HTML/JSON et rendu attribué, revues liées | Laboratoire contrôlé disponible : six HTTP réels, DOM et revues rédigés ; application Edikka encore à produire |
| TS43 | Traitement prévu du client de test, chaîne complète et journaux JSONL liés, attribution explicite | Expérience contrôlée loopback disponible ; aucun accès réel de l’opérateur, identité ou visite établis ; application TS44 distincte |

TS44 dispose désormais de [trois règles exécutables](critical-content-evidence.md) : plan critique préalable, accès sans JS et cohérence des représentations avec revues liées. Le [laboratoire contrôlé](critical-content-laboratory.md) conserve six échanges HTTP réels sur quatre variantes fictives ; DOM et revues restent rédigés. L’application réelle à Edikka reste à réaliser.

Les extensions récentes sont [les liens source v2](source-link-policy-v2.md),
[le contexte HTTP canonical](http-canonical-context.md) et
[les intentions de présentation](preview-intent.md), puis
[les preuves de performance](performance-evidence.md). Leurs migrations sont
explicites ; un ancien dossier ne sélectionne pas automatiquement un nouveau lecteur.

### Critères d'achèvement encore ouverts

Les contrats bilingues, cas contradictoires, outils d'import, rapports et rejeux
existent. Leur vérification logicielle ne suffit pas à déclarer les quatre
méthodes entièrement qualifiées dans un usage réel. La suite doit établir une
voie de preuve praticable pour chaque type d'entrée requis, avec les inconnues
expliquées. Obtenir C n'est pas une condition : un NC ou NT justifié est utile.

| Besoin | Preuve qui permettrait de le clôturer | Situation actuelle |
| --- | --- | --- |
| Décision TS02 | Plan daté du responsable et revue liée, puis captures postérieures | Parcours disponible ; décision réelle non fournie |
| Accès et ressources TS04/TS07 | Revue motivée des ressources/captures dans le client et le périmètre déclarés | Fiches préparées ; réponses humaines non inventées |
| Rendu TS07/TS10 | Plan préalable, captures des états nécessaires, HTTP et DOM liés à la même navigation, contexte et erreurs conservés | Outils et anciens exemples existent ; nouvelle campagne de douze phases bloquée dès le premier contrôle, zéro capture HTTP/DOM de contrôle |
| Équivalence TS10 | Revue de contenu motivée, liée aux membres et aux preuves examinées | Parcours disponible ; revue humaine réelle absente |
| Ébauche Search Console | Diagnostic hors ligne et exercices rejouables ; observation réelle séparée si fournie | Ébauche implémentée ; aucun export réel du compte Edikka fourni |
| Insight | Texte FR/EN, preuves, liens et parcours d'intégration vérifiés ; recette de la page séparée | Préparation livrée ; intégration CMS, recette visuelle et publication non réalisées |

Le blocage navigateur `ERR_BLOCKED_BY_CLIENT` est conservé. Il n'est pas contourné
par un changement d'origine, de navigateur ou des protections. Les lectures locales
et cas rédigés ne remplacent pas la campagne manquante. Les contextes temporels et
indexifembedded de TS07 restent une extension à qualifier ; ils ne sont pas
présentés comme le préalable qui manque à toutes les pages.

### Ce que mesurent les tests

TS44 ajoute **71 cas / 213 couples**, dont 68 figés avant interpréteur et trois cas de frontières figés avant corrections. Draft.24 contient **1 051 cas / 1 942 couples**. Ces exercices restent synthétiques.

TS43 ajoute **71 cas figés / 213 couples**, tous synthétiques. Le corpus draft.23
contient **980 cas / 1 729 couples**. Le [laboratoire contrôlé](agent-access-laboratory.md)
fixe six scénarios et huit requêtes loopback ; il reste distinct d’un audit Edikka.

Relevé historique TS42 : **52 cas figés / 156 couples**, tous synthétiques. Le corpus draft.22
contient **909 cas / 1 516 couples** ; la vérification complète et ses limites
sont conservées dans le journal local du lot. Aucun audit Edikka ne découle de ces cas.

Relevé historique performance : le lot performance ajoute **82 cas synthétiques / 216 couples règle-cible** avec
216 accords sur les attentes, y compris les inconnues prévues. Le corpus draft.21
compte **857 cas / 1 360 couples** : 1 249 accords, zéro désaccord et 111 couvertures
réduites sans Node optionnel. Les accords comprennent 536 attendus indéterminés.
Le [relevé conservé](../provenance/performance-core-2026-10-11.json) décrit cette
exécution ; ce n’est ni un audit Edikka ni une validation humaine.

Relevé historique draft.20, avant la performance : sur **775 cas synthétiques / 1 144 couples règle-cible**, le relevé draft.20 trouve
1 033 accords et 111 couvertures réduites sans Node optionnel ; avec Node 24.19.0
explicitement fourni, 1 136 accords et huit couvertures réduites. Aucun désaccord
interdit dans ces exécutions. Les accords comprennent **433 attendus indéterminés**.
Les huit cas restants suivent leurs anciens profils : ce nombre ne recense pas
toutes les limites des méthodes et ne doit pas devenir un objectif de « zéro NT ».
Voir les [résultats, empreintes et limites](conformance.md#draft20-runtime-coverage).

Les 628 tests de vérification exécutés dans la source puis dans l'archive du lot
preview-intent vérifient des propriétés logicielles. Ils ne prouvent ni 628 audits,
ni contrôles terminés, ni une revue humaine ou une exécution CI distante.

## English — current state

The local edition is **0.1.0-draft.25**, with interpreter **25**, capture adapter
**26** and replay **3**. These version numbers do not establish a public release
or stable 1.0. Historical packages keep their exact tools and fingerprints.

The active human priority is four deeply developed controls, TS04/TS02/TS07/TS10,
with TS01 as the foundation, superseding the older ten-control target. Forty-four
controls are specified. On October 11 the user explicitly added TS34/TS35 performance.
The user then added TS42–TS44 agents, in that order after performance.
The user also authorized TS41, TS39, TS36 and TS31–33. TS41 is integrated first; the other five remain pending.
Eleven controls now have 30 executable atomic rules, including 11 for the four SEO
priorities, five for performance, three for TS41 and nine for TS42/TS43/TS44. The other 33 lack equivalent executable coverage.
TS42 binds source mappings, supplied owner decisions and tradeoffs to a bounded robots comparison. No real owner approval or agent visit is established. TS43 now supplies planned test-client treatment, reviewed native-log correlation and explicit attribution, with a controlled loopback experiment. Actual operator access/identity/visits remain unestablished. TS44 now has three bounded executable [critical-content rules](critical-content-evidence.md); a controlled laboratory retains six actual loopback exchanges with authored DOM/reviews, while real Edikka application remains pending.
TS34 imports CrUX cohorts/p75 with exact classes and supplied decisions. TS35 imports
planned repeated Lighthouse reports with declared context, spread and supplied hypotheses.
No new real Edikka performance campaign, other-source reader or before/after comparison
is established. Conforming documentation can accompany poor performance.

Available methods include prior redirect decisions, shared robots policies,
attributed source/rendered directives, preview permission objectives, canonical
HTTP context, sitemaps and family links. Imports, reports, contradictory cases
and offline replay exist. Real method qualification still needs a practical route
for every required evidence type; a justified NC or NT is valid, with no obligation
to obtain C. Owner decisions, required human reviews and complete attributed rendered
paths are not supplied by authored tests. TS01's noscript proposal remains unpromoted.

The twelve-phase browser campaign was blocked at its first control and obtained
zero control HTTP/DOM captures. Keep the failed attempt and do not bypass the
browser restriction. TS07's time/embedding semantics remain an extension to qualify,
not the universal missing prerequisite for ordinary pages. Separate A01 declared
permissions from A02 access and actual Google observations.

The Search Console draft is an implemented offline diagnostic with synthetic
exercises, not real Edikka account data or a TS08/TS12 assessment. The bilingual
insight handoff is prepared; CMS integration, visual acceptance and publication
remain separate and unperformed.

TS43 adds 71 frozen synthetic cases / 213 pairs. Draft.23 contains 980 cases / 1,729 pairs.
The [controlled laboratory](agent-access-laboratory.md) fixes six scenarios and eight loopback
requests, with fictional sources/reviews; it is not an Edikka audit.

The historical performance addition has 82 synthetic cases / 216 pairs, all matching authored
expectations, including unknowns. Draft.21 has 857 cases / 1,360 pairs: 1,249
agreements, zero disagreements and 111 reduced pairs without optional Node.
Agreements include 536 inconclusive expectations. The [retained observation](../provenance/performance-core-2026-10-11.json)
is software evidence, not a real Edikka assessment or human validation.

The historical draft.20 775-case / 1,144-pair corpus gives 1,033 agreements and 111 reduced pairs
without optional Node, or 1,136 agreements and eight reduced pairs with explicit
Node 24.19.0, with no disallowed disagreement. Agreements include 433 normative
inconclusive expectations. The eight legacy-profile limits are not a complete
inventory of method boundaries. The preview-intent source/archive verification
ran 628 software tests in each location, not 628 audits or human acceptance.
See the [dated measurements](conformance.md#draft20-runtime-coverage).

The inventory and dated development notes below are historical. Their old counts,
priorities and next steps must not be read as the current state.

## Français

**Inventaire historique : 10 octobre 2026, protocole 0.1.0-draft.7, code 716899e.**
Document de pilotage non normatif. Il décrit la couverture du développement,
jamais la conformité d’Edikka ou d’un site. La priorité de travail est désormais
la réalisation méthodique des **44 contrôles**, avec traitement des limites
connues avant d’élargir les démonstrations. La galerie reste un point d’étape.

### Avancement du 10 octobre après le point de référence

Le commit `13cdd23` étend TS01 aux select/table explicitement structurés :
[limites et migration de l’outil](source-text-v6.md). La réévaluation des mêmes
entrées Edikka conserve TS01 NT, le refus suivant portant sur noscript. Le
[parcours de revue et rejeu](review-and-replay.md) prépare des décisions humaines
vides et permet le rejeu des trois types de paquets. Ni ce parcours ni les tests
logiciels ne prouvent leur recette par Bertrand ou une revue effectivement réalisée.

Bertrand a remplacé la cible de dix par [quatre contrôles prioritaires](four-control-program.md) :
TS04, TS02, TS07 et TS10. L'ébauche Search Console et l'insight suivent les résultats
établis. Les colonnes méthode, application réelle et recette utilisateur restent
séparées. Les 44 lignes ci-dessous restent le **point de référence draft.7**.

Draft.8 ajoute TS02-A01/A02 : onze règles sont désormais définies pour TS01, TS02,
TS07 et TS10 (3 automatic, 6 semiAuto, 2 manual). Ce décompte inclut TS01, qui n'est
pas l'un des quatre objectifs du jour. Le laboratoire TS02 avant/après a réalisé
20 requêtes locales synthétiques ; le parcours pratique du plan humain reste ouvert.
TS04 dispose maintenant d'un [lecteur candidat](robots-policy-experiment.md) et
d'un laboratoire ; ses règles atomiques et l'intégration partagée avec TS07 restent
à réaliser. Les limites rendues/humaines restent dans le suivi.
Ces nombres ne déclarent ni quatre méthodes finalisées, ni quatre audits réalisés.

Draft.9 ajoute TS04-A01/A02 et le lecteur partagé TS07 : treize règles dans cinq
contrôles, dont TS01 hors des quatre priorités. A01/A02 TS04 sont semiAuto, avec
revue des ressources fournie et liée aux preuves. Le parcours est implémenté ; la
recette humaine et l'application réelle ne sont pas déduites des essais synthétiques.

Draft.10 ajoute le lecteur DOM structuré ; draft.11 sépare l’agent HTTP réel des
sémantiques TS07 et fournit un [laboratoire de navigation attribuée](same-navigation-laboratory.md).
Les treize règles restent réparties dans cinq contrôles. Une exécution navigateur,
une recette humaine et un audit du site exigent chacun leurs propres pièces.

### Décompte historique vérifié à draft.7

- **44 contrôles décrits** dans `spec/protocol.json`, avec procédure et attendus.
- **3 contrôles possèdent des règles atomiques et un interpréteur borné** :
  TS01 (2), TS07 (3), TS10 (4), soit **9 règles**.
- Parmi ces règles : 2 automatic, 6 semiAuto et 1 manual. L’interpréteur des règles
  semiAuto/manual ne remplace pas les revues exigées.
- **41 contrôles n’ont pas encore de règles atomiques détaillées exécutables.**
  Ils disposent déjà d’une description et peuvent être renseignés avec des preuves
  selon le contrat ; cela ne signifie pas qu’ils disposent du même outillage.
- Aucun de ces décomptes ne signifie « 3 contrôles achevés », « 44 audits faits »
  ou « 392 tests = 392 critères ». Les tests logiciels vérifient aussi les refus
  attendus et les résultats indéterminés.

La définition normative reste dans la [source](../spec/protocol.json) et le
[contrat](contract.fr.md). Les composants réutilisables et les expériences ne
confèrent pas automatiquement une couverture à un autre contrôle.

### Condition de clôture d’un lot de développement

Pour chaque contrôle : préciser les unités et l’applicabilité ; détailler les
règles et les entrées ; fixer les attentes avant les essais ; couvrir au minimum
accord, contradiction, preuve absente, entrée ambiguë et limite de couverture ;
implémenter ce qui est automatisable ; définir et tester le parcours des revues
réellement nécessaires ; conserver un exemple rejouable et ses limites ; vérifier
la distribution. L’absence de données ou de revue reste non établie.

Un changement normatif exige une version distincte, les contrats français et
anglais, la migration et les cas contradictoires. Une extension d’outil doit être
identifiée, testée et comparée sur les mêmes preuves conservées. Une clôture doit
citer son commit, les preuves et les limites acceptées ; ce tableau ne la déduit
jamais d’un nombre de tests. Couvrir une méthode bornée ne veut pas dire supporter
toutes les pages, tous les moteurs ou tous les environnements.

**Deux jalons restent séparés :** développement de la méthode/outillage, puis
application au périmètre réel avec les accès et revues requis. Search Console
fait partie des entrées de TS08, TS12, TS21 et TS36 : on peut préparer leurs règles
sans accès, mais pas déclarer leur application réelle achevée sans ces preuves.
L’attente d’une entrée externe n’empêche pas le travail indépendant sur les autres
méthodes ; elle demeure un point ouvert explicite.

### Inventaire historique des 44 contrôles à draft.7

Le tableau suit les identifiants permanents. La colonne suivante est un travail
à réaliser, pas une nouvelle exigence normative ni une classification finale de
l’automatisation. Des sous-ensembles utiles existent déjà dans des composants.

| Contrôle | Attendu hérité | Développement actuel | Prochaine étape |
| --- | --- | --- | --- |
| TS01 | La page finale répond avec un code HTTP exploitable. | Partiel : 2 règles atomiques | Traiter les refus select/noscript de la lecture source ; préserver les critères et rapports antérieurs. |
| TS02 | Les redirections sont intentionnelles, directes et sans boucle. | Décrit ; règles atomiques à détailler | Définir les tests des destinations attendues, sauts supplémentaires, boucles et traces incomplètes. |
| TS03 | Les erreurs serveur et soft 404 ne remplacent pas une réponse explicite. | Décrit ; règles atomiques à détailler | Séparer statut HTTP, identité du contenu et hypothèse soft 404 ; prévoir revue et contre-exemples. |
| TS04 | La politique robots effective correspond à l’intention déclarée. | Décrit ; règles atomiques à détailler | Détailler la politique par robot/origine et ses erreurs ; réutiliser TS07-A02 sans lui attribuer tout TS04. |
| TS05 | Une directive Disallow n’est jamais présentée comme une garantie de désindexation. | Décrit ; règles atomiques à détailler | Formaliser la revue de cohérence exploration/indexation ; aucun Disallow ne vaut preuve de désindexation. |
| TS06 | Les zones sensibles refusent réellement l’accès au serveur. | Décrit ; règles atomiques à détailler | Définir les tests autorisés sans session, les preuves de configuration et les limites de couverture du cache. |
| TS07 | Les directives meta robots et X-Robots-Tag sont cohérentes avec l’objectif de la page. | Partiel : 3 règles atomiques | Traiter les limites du lecteur HTML et les revues du plan de rendu et de l’accès. |
| TS08 | Le statut d’indexation réel est vérifié dans Search Console. | Décrit ; règles atomiques à détailler | Définir les entrées d’inspection datées, champs manquants et rattachement à la propriété ; données réelles ensuite. |
| TS09 | Les exclusions volontaires ont un propriétaire et une justification. | Décrit ; règles atomiques à détailler | Structurer famille exclue, justification, propriétaire, échéance et revue réellement réalisée. |
| TS10 | Chaque page canonique publie une URL absolue, stable et cohérente. | Partiel : 4 règles atomiques | Traiter les refus DOM ; qualifier séparément le candidat structuré et la revue humaine du contenu. |
| TS11 | Les variantes réellement dupliquées convergent sans masquer des pages distinctes. | Décrit ; règles atomiques à détailler | Détailler les familles et la comparaison éditoriale ; ne pas confondre similarité et duplication. |
| TS12 | La canonique choisie par Google est comparée à celle déclarée. | Décrit ; règles atomiques à détailler | Définir la comparaison datée canonique déclarée/Google ; conserver valeurs absentes et divergence qualifiée. |
| TS13 | Le sitemap contient uniquement des URL absolues et canoniques utiles. | Décrit ; règles atomiques à détailler | Définir les règles des entrées sitemap, leur état HTTP et leur cohérence ; réutiliser sans généraliser TS10-A03. |
| TS14 | lastmod reflète une modification significative de la page. | Décrit ; règles atomiques à détailler | Lier lastmod à une modification significative prouvée et à son historique ; prévoir jugement éditorial. |
| TS15 | Les limites et découpages de sitemap sont respectés. | Décrit ; règles atomiques à détailler | Détailler taille décompressée, compte, encodage et index incomplets avec cas de limites. |
| TS16 | Chaque page importante reçoit au moins un lien interne crawlable. | Décrit ; règles atomiques à détailler | Définir population cible, points d’entrée et couverture du crawl avant de conclure à une absence de lien. |
| TS17 | Les liens essentiels utilisent un élément a avec href résoluble. | Décrit ; règles atomiques à détailler | Définir inventaire source/DOM des liens essentiels et résolution ; boutons et onclick restent distincts. |
| TS18 | La profondeur et les pages orphelines sont mesurées sur un périmètre explicite. | Décrit ; règles atomiques à détailler | Relier inventaires CMS, sitemap et crawl ; distinguer page orpheline et inventaire incomplet. |
| TS19 | Les paramètres, filtres et calendriers ne créent pas un espace infini. | Décrit ; règles atomiques à détailler | Définir motifs, paramètres, bornes et hypothèses de piège de crawl ; pas d’infinité déduite d’un échantillon. |
| TS20 | La structure d’URL est lisible, stable et encodée correctement. | Décrit ; règles atomiques à détailler | Fixer la politique d’URL avant comparaison : casse, encodage et paramètres ne sont pas équivalents par défaut. |
| TS21 | Les URL découvertes mais non indexées sont investiguées par famille. | Décrit ; règles atomiques à détailler | Structurer investigation par famille, preuves Search Console/logs/sitemap et hypothèses testables. |
| TS22 | Chaque variante hreflang pointe vers une URL indexable et canonique. | Décrit ; règles atomiques à détailler | Définir extraction des annotations et vérification des destinations dans un groupe explicite. |
| TS23 | Les annotations hreflang sont réciproques et incluent la page elle-même. | Décrit ; règles atomiques à détailler | Définir réciprocité, auto-référence, doublons et groupes partiellement collectés. |
| TS24 | x-default représente une destination neutre ou la variante par défaut assumée. | Décrit ; règles atomiques à détailler | Définir l’applicabilité et la revue de la destination x-default selon l’intention. |
| TS25 | Le contenu critique existe dans le HTML source ou devient observable après rendu. | Décrit ; règles atomiques à détailler | Fixer les contenus critiques et états requis ; comparer source/rendu sans affirmer reproduire Google. |
| TS26 | Les ressources nécessaires au rendu ne sont pas bloquées ni en erreur. | Décrit ; règles atomiques à détailler | Lier ressources requises, réseau, robots, CSP et erreurs à chaque état ; une console vide ne suffit pas. |
| TS27 | Les états et routes SPA produisent des URL partageables et des réponses serveur cohérentes. | Décrit ; règles atomiques à détailler | Définir ouvertures directes, actualisation, historique et URL des routes SPA avec scénarios contradictoires. |
| TS28 | Le document expose une structure HTML compréhensible sans dépendre de son apparence. | Décrit ; règles atomiques à détailler | Séparer constats structurels et jugement sur la compréhension du document. |
| TS29 | Les contenus essentiels restent disponibles lorsque scripts ou styles échouent. | Décrit ; règles atomiques à détailler | Définir modes dégradés et critères de disponibilité des contenus ; ne pas les confondre avec un test fonctionnel complet. |
| TS30 | Les métadonnées essentielles sont uniques, visibles et cohérentes avec la page. | Décrit ; règles atomiques à détailler | Définir unicité, présence et cohérence des métadonnées ; conserver la revue de pertinence. |
| TS31 | Le JSON-LD décrit des entités visibles et appropriées au contenu. | Décrit ; règles atomiques à détailler | Lier chaque assertion structurée au contenu et aux exigences du type ; préserver les revues nécessaires. |
| TS32 | Les identifiants @id relient les mêmes entités sans créer de doublons. | Décrit ; règles atomiques à détailler | Définir identité des nœuds, stabilité des @id et cas ambigus sans fusion automatique. |
| TS33 | Les erreurs, avertissements et usages non pris en charge sont distingués. | Décrit ; règles atomiques à détailler | Séparer syntaxe, vocabulaire et éligibilité ; conserver sorties, versions et erreurs des validateurs. |
| TS34 | Les Core Web Vitals terrain sont documentés et classés au 75e percentile. | Décrit ; règles atomiques à détailler | Définir source terrain, période, appareil, population, granularité et données manquantes. |
| TS35 | Les tests de laboratoire servent au diagnostic, pas à simuler le terrain. | Décrit ; règles atomiques à détailler | Définir contexte et répétitions de laboratoire ; ne pas convertir un score en mesure terrain. |
| TS36 | Le suivi relie Search Console, logs et déploiements à des dates de décision. | Décrit ; règles atomiques à détailler | Définir baseline, changement, observations et décisions ; ne pas fabriquer les observations futures. |
| TS37 | HTTPS, HSTS et les ressources intégrées ne créent ni erreur de certificat ni contenu mixte. | Décrit ; règles atomiques à détailler | Détailler certificat, politique HSTS, variantes et sous-ressources ; le test TLS du collecteur ne couvre pas TS37. |
| TS38 | Les variantes d’hôte, de casse et de slash convergent vers une règle unique. | Décrit ; règles atomiques à détailler | Définir les variantes pertinentes et les rapprochements redirection/canonical/sitemap/liens. |
| TS39 | Le CDN, Vary et la géolocalisation ne servent pas des signaux SEO contradictoires. | Décrit ; règles atomiques à détailler | Définir régions, clés de cache, Vary, contextes et comparaisons ; couverture partielle explicite. |
| TS40 | Les méthodes hreflang utilisées sont complètes et cohérentes. | Décrit ; règles atomiques à détailler | Définir toutes les méthodes hreflang présentes et leurs contradictions sans mélanger les populations. |
| TS41 | Les invariants SEO critiques sont rejoués automatiquement avant et après déploiement. | Trois règles exécutables ; entrées natives et journal fourni | Plan et revues préalables, couverture et réaction aux échecs/inconnues ; laboratoire de processus réel et application Edikka encore à produire. |
| TS42 | Chaque agent automatisé est gouverné selon son usage documenté. | Décrit ; règles atomiques à détailler | Structurer usages, sources opérateur datées, décision et responsable ; aucune identité déduite du jeton seul. |
| TS43 | L’accès des crawlers autorisés est testé avec leur chaîne complète et rapproché des journaux. | Décrit ; règles atomiques à détailler | Définir requêtes avec agent complet, rapprochement logs et limites d’identité ; imitation ≠ visite réelle. |
| TS44 | Le contenu critique et ses preuves restent accessibles sans dépendre d’une exécution JavaScript non documentée. | Décrit ; règles atomiques à détailler | Définir les faits/contenus critiques et leurs preuves accessibles ; aucune promesse de citation par un moteur. |

### Premier lot : traiter le socle existant

Le premier dossier à instruire est **TS01, lecture source**. Il faut séparer le
refus de syntaxe `select` et la question de méthode `noscript` : copier le lecteur
expérimental dans l’interpréteur actif ferait implicitement ce choix. La décision
sur les hypothèses de lecture précède toute promotion. Les résultats rédigés ou
les deux lectures concordantes ne valent pas preuve du comportement d’un moteur.

| Sujet ouvert | État exact | Action et preuve de clôture attendue |
| --- | --- | --- |
| TS01 : `select`, tables et autres contextes refusés | L’interpréteur actif reste borné ; un candidat séparé traite davantage de constructions | Définir l’extension précise, garder les contre-exemples, réévaluer les preuves inchangées avec une version identifiée ; conserver tout refus restant |
| TS01 : interprétation de `noscript` | Deux hypothèses existent seulement dans l’expérience | Formaliser la décision avant intégration, avec désaccords et entrées partielles ; toute nouvelle sémantique exige une migration normative |
| TS10 : DOM refusés | Les deux campagnes conservent leurs attentes non atteintes | Définir le raccordement du relevé structuré aux preuves HTTP/source, puis tester les contradictions et captures manquantes ; ne pas nettoyer les anciens DOM |
| TS07/TS10 : revues absentes | Un résultat technique ne remplace pas la revue du plan, de l’accès ou du contenu | Définir la saisie et la liaison des revues ; ne déclarer une revue réalisée qu’avec son auteur, sa portée et ses pièces |
| Marqueurs présents, formulaire retiré | Angle mort observé sur une copie synthétique | Conserver ce contre-exemple ; traiter la présence du contenu critique dans les méthodes concernées, sans transformer TS01 en test fonctionnel général |
| Environnements navigateur | Les environnements observés peuvent partager un moteur et des interventions auxiliaires | Déclarer leur portée ; tester séparément de nouveaux environnements si nécessaire, sans revendiquer une indépendance non prouvée |
| TS02–TS44 sans règles détaillées, hors TS07/TS10 | 41 contrôles à développer | Ouvrir des lots successifs à partir du tableau, sans attribuer à tout un contrôle un test partiel existant |
| Écart local/public | Outils récents non encore publiés au point de référence | Préparer une distribution identifiée après vérification ; la publication reste une action distincte, pas une condition pour écrire les prochains tests |

Pour chaque sujet : conserver problème, reproduction, décision de méthode,
correctif/version, résultat après correction et limites restantes. Une explication
ou une galerie ne ferme pas à elle seule une limitation de l’outil. À l’inverse,
une preuve réellement absente ne se « corrige » pas en changeant le verdict.

Après le lot de consolidation : avancer par familles et dépendances, en commençant
par redirections et erreurs HTTP (TS02/TS03), puis accès/robots, familles d’URL,
sitemaps/liens, internationalisation, rendu/contenus, données structurées,
mesures/suivi et agents. Chaque contrôle reste individuellement suivi. Les données
Search Console sont recueillies lors de l’application des méthodes concernées ;
aucune campagne GSC ou publication d’insight n’est déclenchée par ce document.

## English

**Development snapshot: 10 October 2026, protocol draft.7, code 716899e.** This is
non-normative planning, not a site assessment. Priority is methodical coverage of
all 44 controls, addressing known limitations before expanding demonstrations.
The source describes 44 controls. Only TS01, TS07 and TS10 have detailed atomic
rules and a bounded reference interpreter: 2, 3 and 4 rules respectively. Of the
nine rules, two are automatic, six semi-automatic and one manual. Interpreting
supplied evidence does not replace the reviews required by the latter categories.
The remaining 41 controls have descriptions/procedures but no detailed executable
atomic rules. Existing components may be reusable; experiments and test counts
never establish whole-control completion or site conformity.

The French table enumerates every permanent control and its next development
step, not new normative requirements or a final automation classification. A lot
closes only with explicit applicability, units, inputs, rules, predeclared test
expectations, contradictory/missing/ambiguous/partial cases, implementation or
review workflow, retained replayable examples, distribution verification and
identified remaining limitations. A normative change needs a distinct version,
French/English contracts, migration guidance and contradictory cases. Tool changes
need their own identity and comparison on retained inputs. Closure cites evidence
and a commit, never just a passing test count.

Development completion and real application are separate milestones. Search
Console is required for TS08/TS12/TS21/TS36: methods can be developed without account
access, but their real assessments cannot be completed without the required data.
Missing external evidence/reviews stay open without blocking unrelated development.

The first consolidation lot covers the existing foundation: TS01 unsupported
source contexts and the separate unresolved noscript reading policy; TS10 refused
DOMs and the explicit future binding of structured evidence; missing TS07/TS10
human reviews; the marker-versus-function blind spot; declared browser coverage;
and the local/public distribution gap. A description alone does not fix a reader
limitation, and missing evidence cannot be fixed by changing an outcome. Preserve
original captures, historical reports and failed expectations. Do not clean DOMs
or silently promote an experiment. Define the reading policy before any promotion.

Subsequent lots address redirects/errors, access/robots, URL families, sitemaps
and links, internationalization, rendering/content, structured data, measurements
and agents according to their dependencies. Track each of the 44 controls
individually. This planning document triggers no account access, site mutation,
publication, new conformity outcome or claim of independent review.
