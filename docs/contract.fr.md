TS15-A03 admet uniquement pass/inconclusive, déclaration fermée `allowed_outcomes` dans la source ; fail/NA rejetés. Voir le contrat des fichiers sitemap et la migration draft.35.

Draft.35 — TS15-A01/A02/A03 : [fichiers fournis / supplied files](sitemap-files-evidence.md), [migration](migration-draft.35.md). Population déclarée, aucun serveur observé / Declared population, no server observation.

Draft.34 — TS33-A01/A02/A03 : [contrat / contract](structured-validation-evidence.md), [migration](migration-draft.34.md). Captures liées, messages natifs séparés / Bound captures, separate native messages. Erreur bloquante conservée / Blocking errors retained.

Draft.33 ajoute TS32-A01/A02/A03 : registre préalable, identifiants/références natifs et revues liées. [Contrat](structured-identity-evidence.md), [migration](migration-draft.33.md). Cohérence du corpus fourni, sans stabilité temporelle authentifiée.
Draft.32 ajoute TS31-A01/A02/A03 : périmètre préalable, lecture JSON-LD native et revues de contenu liées par entité. [Contrat bilingue](structured-content-evidence.md), [migration](migration-draft.32.md). Preuves fournies, aucune visibilité ou vérité authentifiée ni résultat enrichi garanti.

Draft.31 ajoute TS36-A01/A02/A03 : chronologie, échéances et décisions fournies. [Contrat bilingue](release-monitoring.md), [import](release-monitoring-intake.md), [migration](migration-draft.31.md). Baseline/J+1/J+7/J+30 stricts ; futur NT, aucune causalité ni visite Google authentifiée.

Draft.30 ajoute TS12-A01/A02/A03 : plan, comparaisons attribuées et revue/décision fournie. [Contrat bilingue](canonical-comparison.md), [migration](migration-draft.30.md). Rendu prévu requis ; C documentaire, pas TS10 ni indexation.

Draft.29 ajoute trois règles TS08 : périmètre/objectifs, inspections natives et revues/décisions liées. [Contrat bilingue](inspection-evidence.md), [migration](migration-draft.29.md). C qualifie le dossier sélectionné, jamais une indexation garantie.

# Contrat de rapport — TSEP 0.1.0-draft.35

### Diffusion et variantes — draft.27

TS39 ajoute trois règles : matrice/configuration, signaux par cellule et attribution des contextes/cache. [Contrat](delivery-evidence.md), [migration](migration-draft.27.md). Les tests natifs et les revues restent explicites ; aucun accès réel Googlebot déduit.


### Clarification TS41 — draft.26

Le recalcul inconclusif ne suffit pas à accuser une ancienne sortie positive ; une inconnue inchangée masquée par un code 0 reste une contradiction. [Migration et correction FR/EN](migration-draft.26.md). Lecteur inchangé.

### Dispositif de déploiement — draft.25

TS41 ajoute trois règles : plan, couverture des exécutions et réaction aux échecs/inconnues. [Contrat](release-invariants.md), [migration](migration-draft.25.md). C qualifie le dispositif déclaré ; un défaut SEO correctement bloqué reste visible.

### Contenu critique — draft.24

TS44 ajoute trois règles : périmètre préalable, livraison sans JS, cohérence et revue des représentations. [Contrat](critical-content-evidence.md), [migration](migration-draft.24.md). Aucun fait vrai, accès réel d’agent ou citation déduit.

### Accès et journaux agents — draft.23

TS43 ajoute trois règles pour le client de test, ses traces et son attribution. Un refus attendu peut être cohérent ; aucun accès réel opérateur déduit. [Contrat](agent-access-evidence.md), [migration](migration-draft.23.md).

### Usages agents — draft.22

TS42 ajoute trois règles : sources et revues, décisions du responsable, comparaison robots bornée. [Contrat](agent-usage-policy.md), [migration](migration-draft.22.md). Finalités couplées et arbitrages explicites ; aucune visite réelle déduite.

### Performance — draft.21

TS34 et TS35 disposent de cinq règles atomiques. [Contrat performance](performance-evidence.md), [migration](migration-draft.21.md). C qualifie la documentation, pas de bonnes performances ; les valeurs/classes et les revues manquantes restent visibles.

### Preview intent / Intentions de présentation — draft.20

Le profil préalable facultatif google-preview-intent-v1 étend TS07-A01/A03 avec des intervalles de permission texte/image/vidéo. [Contrat bilingue normatif](preview-intent.md) et [migration](migration-draft.20.md). Les anciennes entrées, extractions, revues et inconnues restent distinctes. Aucun affichage Google déduit.

### Contexte canonical HTTP — draft.19

Le profil préalable facultatif `intent.canonical.http_reader: "http-link-context-v1"`
étend TS10-A01/A02 selon le [contrat HTTP](http-canonical-context.md). Sans champ,
le lecteur historique reste fixe. Premier rel, contexte anchor, destination littérale,
preuves et inconnues sont conservés ; aucune revue humaine ou sélection Google
n’est déduite. [Migration explicite](migration-draft.19.md).


## Périmètre déclaré

Choisir un profil de preuves ou une liste explicite de contrôles avant l’audit.
Identifier les vraies unités dans `scope.targets` : URL, hôtes, inventaires,
groupes de langues ou déploiements. Décrire sélection et exclusions. Un identifiant
de groupe doit être expliqué par une preuve listant ses membres. Une URL ne
représente pas automatiquement le site entier.

Créer des rapports distincts lorsque les populations diffèrent selon les contrôles.
Ne pas généraliser aux gabarits, régions, robots ou dates non observés. Un changement
de périmètre produit un nouveau rapport ; conserver le précédent et le motif.

## Résultats des contrôles

| Code | Sens | Condition |
| --- | --- | --- |
| C | Conforme dans le périmètre | Tous les attendus, cibles et types d’entrées couverts |
| NC | Non conforme dans le périmètre | Au moins une contradiction étayée avec un attendu |
| NA | Non applicable | Preuve positive de non-applicabilité sur tout le périmètre |
| NT | Non établi | Non commencé, accès/preuve absent, examen partiel ou indéterminé |

Chaque résultat porte un motif et la procédure réellement exécutée. NT distingue
`not-started` et `inconclusive`, ce dernier conservant tentatives et limites connues.
Un délai dépassé, un accès absent ou un inventaire incomplet n’est pas automatiquement
un défaut SEO. Une contradiction observée autorise NC en expliquant les autres
limites. NA ne remplace jamais un accès manquant.

Le schéma décrit la structure. Les règles complémentaires de la CLI imposent
unicité des IDs/cibles, correspondance exacte contrôles/résultats, totalité d’un
profil nommé, preuve pour C/NC/NA et couverture complète des cibles pour C/NA.
C exige aussi chaque type d’entrée pour chaque cible. Un fichier peut couvrir
plusieurs cibles si son contenu le justifie ; le validateur contrôle la déclaration,
pas sa véracité.

Les attendus portent aussi sur les pratiques de vérification. TS08 établit un état
d’indexation documenté, pas une promesse d’indexation. TS34 établit une lecture
correcte des mesures terrain ; C ne signifie pas que les performances mesurées
sont bonnes. Conserver les mesures défavorables et leurs conséquences opérationnelles.

## Règles atomiques des contrôles déclarés

Le format de rapport est `2`. Un **contrôle** garde son identifiant TSxx et son
résultat C/NC/NA/NT sur le périmètre. Un **test atomique** répond à un attendu
identifié par `TSxx-Ayy` dans le JSON canonique. Une **observation** est une
capture ou un constat daté dans un contexte donné ; son existence ne suffit pas
à réussir le test. Chaque règle déclare `automation` : `automatic`, `semiAuto` ou `manual`.

Pour les contrôles qui déclarent des règles atomiques dans la source, `atomic_results` relie chaque couple `rule_id`/`target`
à un `outcome` (`pass`, `fail`, `not-applicable`, `inconclusive`), un `reason` et
des `evidence_ids`. Les preuves doivent aussi figurer dans le résultat du contrôle
et couvrir la cible. Tous les types d’entrée de la règle sont exigés pour `pass`.
Une contradiction `fail` peut être étayée par un sous-ensemble des entrées.
`not-applicable` n’est autorisé que pour les règles possédant `na_inputs`, avec
ces pièces et une justification positive. Une absence de fichier n’en est pas une.

- C exige tous les couples règle/cible, sans échec ni inconnue, avec les preuves
  requises. Un test réussi isolé, un exit 0 de sonde, une omission ou des exemptions
  seules ne suffisent pas. La CLI rejette une déclaration C incohérente, sans la
  transformer silencieusement en NT.
- NC exige au moins un `fail` prouvé ; conserver les autres inconnues. L’état
  `complete` signifie alors conclusion NC établie, pas collecte exhaustive.
- NT n’efface aucun `fail` ; il conserve les tentatives et lacunes. `not-started`
  n’admet aucune observation ; `inconclusive` peut contenir des tests réussis.
- NA du contrôle entier exige sa condition de non-applicabilité, une preuve de
  type `intent` couvrant chaque cible et aucune observation atomique applicable.
  Pour TS10, cette preuve comprend l’inventaire et la stratégie. Un record positif
  d’absence de sitemap ou de surface HTML ne dispense pas des autres règles.

Chaque cible désigne une URL ou une famille explicitement inventoriée. Fixer
robot, intention, conditions, population de liens et états nécessaires dans la
preuve avant l’examen ; scinder les rapports pour des contextes incompatibles.
Pour un non-HTML, le record `html` documente son absence légitime et le type reçu.
Pour une famille sans sitemap, le record `sitemap` justifie cette absence. Ce ne
sont pas des captures HTML/XML fabriquées. TS07 exige désormais une preuve `robots` ;
le rendu requis doit être joint en `render`. TS10-A01 requiert aussi le DOM lorsqu’il
affecte les déclarations, même si le validateur ne peut pas déterminer ce besoin.

La CLI vérifie les déclarations, références et couvertures, pas la justesse de la
lecture HTTP/HTML, de l’intention ou des exemptions. Les cas de méthode historiques
ont des verdicts rédigés. La [suite exécutable distincte](conformance.md) interprète
les entrées brutes de quarante-deux règles dans des limites documentées ; elle
n’implémente pas tous les contrôles. Aucun C ne
s’étend aux contrôles non sélectionnés, à un site entier ou à l’indexation réelle.
Voir [migration et cas](migration-draft.2.md).

### Captures rendues TS07-A03 — draft.4

Un pass exige les quatre types http, html, render et intent pour la cible, afin
que le test soit relié à sa source. Le plan fixe les états, interactions et attentes
avant les observations. Conserver navigateur/version, activation JavaScript,
erreurs, date et contexte de chaque capture. L’URL finale, le contexte et une
empreinte de la trace HTTP lient les DOM à la source évaluée.

Une contradiction dans un état complet et attribuable donne fail, même si un autre
état reste inconclusive. Sans contradiction, un état requis manquant, tronqué,
en erreur, ambigu ou non attribuable empêche pass. Un noindex source retiré tardivement
ne donne pas pass à A03 ; le verdict source A01 reste distinct. La revue préalable
du plan et la suffisance des captures gardent cette règle semiAuto.

Une exemption exige une revue documentée, liée à la source, avec pièces conservées ;
une liste vide, un DOM absent ou la simple affirmation « pas de JS » ne suffisent
pas. L’interpréteur compare des captures fournies : il n’exécute pas JavaScript et
ne simule pas le moteur. Voir [format et limites](rendered-states.md) et
[migration draft.4](migration-draft.4.md). La validation du rapport contrôle les
références/types de preuves ; elle ne parse pas elle-même les DOM ni le plan.

### Familles canoniques TS10 — draft.5

A01 rapproche les déclarations de tous les membres inventoriés : méthodes et états
requis fixés auparavant, captures datées et liées au contexte/source. Conserver
les signaux répétés et les contradictions malgré les autres lacunes. Les exemptions
de rendu exigent une revue étayée. A02 exige une destination directement en 200 et
une revue humaine motivée pour chaque membre comparé à la préférence, liée par
empreinte aux pièces examinées ; elle reste manual.

A03 rapproche tous les index et enfants attendus avant de conclure à une omission.
A04 rapproche toutes les pages sources et états nécessaires ; zéro lien n’est pas
une réussite si la population reste partielle. Un échec attribuable survit à une
autre branche/page manquante. Les exceptions identifient précisément leur objet
et leur motif. Une absence positive de sitemap exempte seulement A03.

Le [format exécutable](canonical-families.md) borne les interprétations HTTP/HTML,
DOM et XML. Le rapport conserve preuves, résultats et inconnues ; sa validation ne
parse pas ces captures ni ne garantit la justesse des revues. Aucun C automatique
TS10, aucun C à partir d’un sous-ensemble des règles. Voir la
[migration draft.5](migration-draft.5.md).

## Automatisation et identité de représentation

Un C en `assessor.mode: "automatic"` est valide seulement si le contrôle possède
un ensemble non vide de règles atomiques **toutes** `automation: "automatic"` et
si le rapport déclare `assessor.tool: {"name": "…", "version": "…"}` avec des valeurs
non blanches. Toutes les exigences règle/cible/preuve restent applicables. Une
exemption ne contourne pas l’exigence d’automatisation. Un contrôle sans règles
atomiques définies ne peut pas produire un C automatique. `semiAuto` exige une
interprétation humaine ; `manual`, un jugement humain. Ce classement décrit la
méthode, pas la qualité de la preuve.

TS01-A01 et A02 sont automatic. A01 exige un **200 final** ; son titre hérité est
plus large. A02 compare `expected_final_url` et `expected_body_sha256` préalables :

1. Une URL finale différente donne fail, même sans empreinte de référence.
2. À URL identique, une empreinte identique du corps complet donne pass.
3. Sinon, `representation: "stable"` déclaré impose fail pour tout changement.
4. Sinon, des listes valides `required_markers` / `forbidden_markers` donnent fail
   si un requis manque ou un interdit apparaît. Pass exige **au moins un requis**,
   tous les requis présents et tous les interdits absents. Avec seulement des
   interdits absents, ou sans critères valides : inconclusive.

Les références URL/empreinte doivent être valides ; une capture incomplète ou non
attribuable ne permet pas pass. Marqueurs UTF-8 uniques et non blancs, recherchés
littéralement avec casse dans le **texte source extrait**, sans regex :

- HTML : caractères des segments textuels, entités HTML décodées ; commentaires,
  contenu de `script` et `style`, balises et attributs exclus. Ne jamais concaténer
  les segments à travers une balise ou un commentaire pour créer un marqueur.
- `text/plain` : corps décodé intégral, sans interprétation de pseudo-balisage.
- Sans profil distinct, pas de normalisation des espaces ou de la casse. Une extraction ou un décodage
  indéterminé ne permet aucun verdict conclusif fondé sur les marqueurs.

Cette extraction n’affecte pas le SHA-256 du corps complet. Elle ne mesure pas la
visibilité : titre et texte masqué par CSS peuvent compter. Ni CSS ni JavaScript
ne sont exécutés ; les contextes non pris en charge par la référence sont
documentés dans la [conformance](conformance.md).
Des listes vides ne prouvent rien. Un interdit contenu dans un requis rend
l’intention contradictoire. Des marqueurs invalides ou une politique de
représentation inconnue ne résolvent pas une variation d’empreinte. L’ordre ci-dessus
s’applique : les marqueurs sont une alternative en cas d’empreinte différente et
ne contournent jamais un échec de stabilité. Une empreinte de référence absente
à URL identique reste inconclusive, même avec marqueurs. Le responsable répond de
la pertinence des références et marqueurs. Une variation horodatée seule n’est pas
un défaut SEO. NT sur TS01 bloquant donne toujours NO_GO.
TS07-A01/A02/A03 et TS10-A01/A03/A04 sont semiAuto ; TS10-A02 reste manual.
Voir la [migration draft.7](migration-draft.7.md) pour la réévaluation obligatoire.

Draft.28 ajoute le profil préalable facultatif `identity_reader: "html-tree-markers-v1"`
dans la seule branche des marqueurs HTML. Le [contrat des marqueurs parsés](source-markers.md)
précise ses deux hypothèses globales, les segments attribués, le prétraitement CRLF/CR
vers LF et les contextes/erreurs hors portée. Les critères restent littéraux ; deux
lectures pass donnent pass, deux fail donnent fail, sinon inconclusive. Sans ce
champ, le lecteur historique reste inchangé. URL, empreinte et stabilité conservent
leurs priorités. Nouvelle intention puis nouvelle capture : aucune migration
implicite d'un ancien dossier ; voir [migration draft.28](migration-draft.28.md).

Voir [migration depuis draft.2](migration-draft.3.md) et [parcours CLI](cli.md).
`add-evidence` et `record` valident avant de remplacer le rapport, actualisent sa
date d’émission et ne déduisent aucun verdict. Conserver les évaluations précédentes.

## Paquet de preuves

Conserver rapport et fichiers ensemble. Chaque preuve indique ID, chemin POSIX
relatif, SHA-256, type, cibles, date d’observation avec fuseau et description.
Déclarer l’accès `public`, `restricted` ou `synthetic`. TSEP-1 exige des preuves
publiques, sauf l’intention déclarée ; TSEP-2 admet en plus les preuves restreintes issues des outils webmaster
du moteur visé ; Google constitue la première série normative (TS08/TS12). L’évaluateur doit documenter leur vraie origine. Les preuves fictives
sont signalées dans le résultat. Le type `webmaster-tools` exige `engine` ; seul `engine: "google"` satisfait
l’entrée `search-console` existante. Le type historique `search-console` signifie
Google et ne peut pas déclarer un autre moteur. Les autres moteurs nécessitent
leur propre série normative future ; leurs preuves ne valident pas les contrôles Google.
Les chemins absolus, traversées et liens symboliques sortants sont refusés.
Les références se résolvent localement ; la validation ne télécharge rien.

Inclure commande, outil/version, environnement, conditions des requêtes,
échantillonnage et sorties utiles. Distinguer HTML source et DOM rendu. Les preuves
précèdent l’émission du rapport. Déclarer les occultations et restrictions d’accès.
Un rapport public sans ses preuves privées ne peut pas revendiquer leur
reproductibilité publique.

Les empreintes attestent seulement l’intégrité des fichiers. L’évaluateur reste
responsable de leur provenance, de leur exactitude et de leur usage autorisé.
Ce candidat ne fournit ni horodatage de confiance ni signature cryptographique
ni chaîne de collecte inviolable.

## Décision de recette

Elle concerne uniquement les contrôles sélectionnés et les cibles déclarées.
La sévérité provient du protocole figé, sans déclassement dans le rapport.
Appliquer dans cet ordre :

1. NC ou NT bloquant : `NO_GO`.
2. Autre NT, ou tous les contrôles NA : `INCOMPLETE`.
3. NC majeur : `REVIEW`.
4. Sinon : `GO_WITH_RESERVATIONS`, avec écarts mineurs/informatifs et limites conservés.

Cette politique de livraison est proposée par TSEP ; ce n’est pas une règle d’un
moteur de recherche. Un rapport valide peut être NO_GO. Un GO ne prouve ni
indexation, ni classement, ni conformité d’accessibilité ou de sécurité.
La décision de livrer appartient au responsable. Ce candidat ne prévoit ni
dérogation silencieuse ni surcharge des sévérités.

`validate` renvoie 0 si le rapport est valide, quelle que soit la décision.
`gate` renvoie 0 pour GO_WITH_RESERVATIONS, 1 pour NO_GO, 2 pour REVIEW/INCOMPLETE,
64 pour un rapport invalide, une preuve manquante ou des données d’appel invalides.
Le parseur d’arguments utilise le code conventionnel 2 pour une syntaxe CLI erronée.

Le JSON conserve les IDs `blocking` et ajoute `blocking_causes`, un tableau de
`{control_id, status}` avec NC ou NT pour chaque contrôle bloquant. Le résumé
FR/EN affiche la même cause. Décision et codes de sortie restent inchangés.

## Versions et revendications d’implémentation

Figer version et SHA-256 du protocole. Citer `TSEP@0.1.0-draft.14:TS01`. Ne jamais
remplacer silencieusement un artefact publié. Changer applicabilité, attendus,
preuves ou décisions exige une nouvelle version et une note de migration.
TS01–TS44 restent des identités permanentes.

La suite démontre seulement « réussit les tests d’échange des rapports fournis
avec 0.1.0-draft.14 ». Elle ne valide pas 44 algorithmes SEO. Toute revendication
plus large exige une correspondance par règle et des limites publiées. Aucune
interopérabilité avec un outil tiers n’a encore été démontrée.

## TS02 — draft.8

TS02-A01 exige un plan approuvé avant capture et une revue fournie, liée au plan et au contexte. TS02-A02 compare les trajectoires HTTP et conserve les contradictions de préfixe malgré les lacunes. Une revue absente empêche C ; une capture absente ne donne pas NA. Le périmètre serveur HTTP, le format, les bornes et la migration sont dans [redirections](redirects.md) et [migration draft.8](migration-draft.8.md). Les règles TS01/TS07/TS10 conservent leurs attendus.

## TS04 et accès TS07 — draft.9

TS04-A01 confronte une matrice préalable par origine/robot au profil robots déclaré.
TS04-A02 exige l'accès aux ressources nécessaires, les trajectoires attendues et
des revues fournies liées aux réponses. Une contradiction prouvée reste fail malgré
d'autres lacunes ; une revue ou capture absente ne devient ni pass ni NA.
L'exemption A02 exige une revue positive d'absence de ressource nécessaire avant
le plan. Profils, format, bornes, empreintes et chronologie sont définis dans
[la méthode robots](robots.md), en cohérence avec les règles de la source JSON.
Le plan fixe son profil avant mesure ; ne pas choisir a posteriori celui qui réussit.

TS07-A02 partage ce lecteur. Sans nouveau champ robots_policy, l'entrée conserve
le profil fixe historique legacy-exact-v1 ; un profil explicite refusé ne se replie
jamais vers ce profil. Un refus HTTP 401/403 attribuable conserve fail même sans
robots. Les limites de rendu, autres directives et revues ne sont pas supprimées.
Voir [migration draft.9](migration-draft.9.md). Aucune visite réelle du moteur,
conformité globale ou indexation n'est déduite de ces résultats.

## États DOM structurés — draft.10

TS07-A03 et TS10-A01/A02/A04 acceptent le lecteur structuré préalablement choisi,
avec arbre complet, sérialisation, liaisons et pièces de navigation. Une origine
rédigée reste synthetic ; des acquisitions séparées ou une API connue comme altérée
restent indéterminées. Aucun repli vers la sérialisation pour obtenir un accord.
Les revues, en-têtes et sources conservent leur rôle ; aucune assimilation au moteur.
Le [contrat détaillé](structured-rendering.md) et la [migration](migration-draft.10.md)
définissent les bornes, décisions et distinctions avec les anciens candidats.

## Agent de collecte et sémantique — draft.11

Le champ facultatif préalable TS07 `directive_crawler=googlebot` distingue la
sémantique des directives de `crawler`, agent HTTP exact inchangé. Il évalue
uniquement la représentation reçue par ce client. A02 exige un profil robots
explicite dont le produit concorde ; aucune assimilation à une visite Googlebot.
Les anciennes entrées gardent leur comportement. Le [laboratoire attribué](same-navigation-laboratory.md)
et la [migration](migration-draft.11.md) décrivent preuves, rejets et limites.

## Portée du client TS04 — draft.12

TS04 accepte désormais le même champ préalable `directive_crawler=googlebot` que
TS07, avec `robots_policy` explicite et `product_token` concordant. `crawler`
reste le User-Agent HTTP exact ; chaque trace est toujours liée à cet agent.
La sélection du groupe Googlebot porte sur la représentation reçue par ce client,
pas sur une réponse reçue par Googlebot. Les résultats l'indiquent explicitement.

Un champ nul, inconnu ou incohérent ne se replie pas vers le groupe du client.
Une réponse de ressource contraire au statut/destination déclaré reste un échec
limité au client observé, y compris 401/403/429/5xx quand 200 est attendu. Elle
ne prouve pas un refus à Googlebot. Les revues manquantes et limites de population
demeurent ; l'extension ne suffit pas à conclure C. Sans nouveau champ, les
anciennes entrées gardent leur comportement. Conserver le dossier initial, puis
déclarer un nouveau plan avant les nouvelles captures : [migration draft.12](migration-draft.12.md).

## Profil robots à champs identifiés — draft.13

Le profil facultatif `google-robotstxt-fields-v2`, déclaré avant capture, relève
les douze champs classés inutilisés dans le reporting de google/robotstxt au commit
`22b355ff855419e6a3ff8ff09c0ad7fdb17116f9`, plus sitemap. Ces champs ne modifient
ni l'accès ni les groupes. La liste, les sources distinctes (documentation et
code), les valeurs conservées et les bornes d'affichage figurent dans la
[migration draft.13](migration-draft.13.md). Aucun verdict TS42 n'en découle.
Les noms proches et autres champs restent indéterminés ; anciens profils et
exigences de revue inchangés. Aucune extension rétroactive d'une intention.

## Lecture des URL de sitemap — draft.14

TS10-A03 accepte le lecteur facultatif préalable `sitemap-locations-v1`. Les loc
directs de pages restent distincts des annotations XHTML/image et des champs
ordinaires relevés sans validation de leurs valeurs. Le profil historique ne
change pas ; aucun repli depuis une valeur inconnue. Une omission exige toujours
un parcours complet, une contradiction attribuable reste conservée. Les structures
reconnues, namespaces, captures, bornes et inconnues sont définis dans la
[méthode](sitemap-locations.md) et la [migration](migration-draft.14.md). Ce succès
atomique seul ne donne ni C à TS10, ni validation hreflang/image, ni choix Google.

## Directives source — draft.15

TS07-A01 et le préalable source A03 acceptent le profil facultatif préalable html-tree-directives-v1. L’accord de deux hypothèses statiques reste distinct des états rendus. Les contextes refusés, encodage, bornes, attribution aux octets, observations et rejeu sont normatifs dans [le contrat bilingue](source-directives.md), inclus dans les empreintes normatives. Les anciennes entrées et exigences de revue restent inchangées. Voir [migration](migration-draft.15.md).

### Source canonical — draft.16

Le profil facultatif préalable html-tree-canonical-v1 étend uniquement la source de
TS10-A01/A02. Son [contrat normatif bilingue](source-canonical.md) définit applicabilité,
entrées, hypothèses alternatives, contradictions qualifiées, inconnues, preuves et
limites. Les revues de rendu/contenu restent exigées ; A04 et les lecteurs DOM ne
changent pas. Les calculs conservent des observations comparées au rejeu. Voir la
[migration](migration-draft.16.md), sans modifier rétroactivement une intention.

### Liens source — draft.17

TS10-A04 accepte le profil préalable html-tree-links-v1 sous intent.canonical.links. Le [contrat bilingue normatif](source-link-policy.md) définit population, URL, base, hypothèses, inconnues et bornes. La portée de convergence, y compris zéro lien observé, accompagne les motifs atomiques/contrôle, HTML, EARL et scope_notes du gate. Rendu et revues inchangés ; [migration explicite](migration-draft.17.md).

### Bases non analysables — draft.18

TS10-A04 accepte désormais aussi le profil préalable html-tree-links-v2. Une première base dont le href échoue à l’analyse WHATWG rend les href dépendants indéterminés, tout en conservant les contradictions indépendantes. Profil v1, A01/A02 et rendu inchangés. Le [contrat normatif bilingue](source-link-policy-v2.md) et la [migration](migration-draft.18.md) précisent les preuves, hypothèses, zéro observé et limites.
