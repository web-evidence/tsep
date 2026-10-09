# Contrat de rapport — TSEP 0.1.0-draft.2

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

## Règles atomiques TS01, TS07 et TS10

Le format de rapport est `2`. Un **contrôle** garde son identifiant TSxx et son
résultat C/NC/NA/NT sur le périmètre. Un **test atomique** répond à un attendu
identifié par `TSxx-Ayy` dans le JSON canonique. Une **observation** est une
capture ou un constat daté dans un contexte donné ; son existence ne suffit pas
à réussir le test. Les méthodes atomiques restent manuelles ou assistées.

Pour ces trois contrôles, `atomic_results` relie chaque couple `rule_id`/`target`
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
lecture HTTP/HTML, de l’intention ou des exemptions. Les cas de méthode fournis
ont des verdicts de référence rédigés, pas un moteur SEO automatique. Aucun C ne
s’étend aux contrôles non sélectionnés, à un site entier ou à l’indexation réelle.
Voir [migration et cas](migration-draft.2.md).

## Paquet de preuves

Conserver rapport et fichiers ensemble. Chaque preuve indique ID, chemin POSIX
relatif, SHA-256, type, cibles, date d’observation avec fuseau et description.
Déclarer l’accès `public`, `restricted` ou `synthetic`. TSEP-1 exige des preuves
publiques, sauf l’intention déclarée ; TSEP-2 admet en plus les preuves Search Console
restreintes. L’évaluateur doit documenter leur vraie origine. Les preuves fictives
sont signalées dans le résultat. Ce candidat refuse un C entièrement automatique,
aucun contrôle complet ne disposant encore d’une telle implémentation.
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

## Versions et revendications d’implémentation

Figer version et SHA-256 du protocole. Citer `TSEP@0.1.0-draft.2:TS01`. Ne jamais
remplacer silencieusement un artefact publié. Changer applicabilité, attendus,
preuves ou décisions exige une nouvelle version et une note de migration.
TS01–TS44 restent des identités permanentes.

La suite démontre seulement « réussit les tests d’échange des rapports fournis
avec 0.1.0-draft.2 ». Elle ne valide pas 44 algorithmes SEO. Toute revendication
plus large exige une correspondance par règle et des limites publiées. Aucune
interopérabilité avec un outil tiers n’a encore été démontrée.
