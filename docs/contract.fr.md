# Contrat de rapport — TSEP 0.1.0-draft.6

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
à réussir le test. Chaque règle déclare `automation` : `automatic`, `semiAuto` ou `manual`.

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
lecture HTTP/HTML, de l’intention ou des exemptions. Les cas de méthode historiques
ont des verdicts rédigés. La [suite exécutable distincte](conformance.md) interprète
les entrées brutes de neuf règles dans des limites documentées ; elle
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
4. Sinon, les listes `required_markers` / `forbidden_markers` décident : tous les
   requis présents et tous les interdits absents donnent pass ; toute violation
   donne fail. Sans critères d’identité valides et non vides : inconclusive.

Les références URL/empreinte doivent être valides ; une capture incomplète ou non
attribuable ne permet pas pass. Marqueurs UTF-8 uniques et non blancs, recherchés
littéralement avec casse dans le corps décodé, sans normalisation, regex ni DOM.
Des listes vides ne prouvent rien. Un interdit contenu dans un requis rend
l’intention contradictoire. Des marqueurs invalides ou une politique de
représentation inconnue ne résolvent pas une variation d’empreinte. L’ordre ci-dessus
s’applique : les marqueurs sont une alternative en cas d’empreinte différente et
ne contournent jamais un échec de stabilité. Une empreinte de référence absente
à URL identique reste inconclusive, même avec marqueurs. Le responsable répond de
la pertinence des références et marqueurs. Une variation horodatée seule n’est pas
un défaut SEO. NT sur TS01 bloquant donne toujours NO_GO.
TS07-A01/A02/A03 et TS10-A01/A03/A04 sont semiAuto ; TS10-A02 reste manual.
Voir la [migration draft.6](migration-draft.6.md) pour la réévaluation obligatoire.

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

Figer version et SHA-256 du protocole. Citer `TSEP@0.1.0-draft.6:TS01`. Ne jamais
remplacer silencieusement un artefact publié. Changer applicabilité, attendus,
preuves ou décisions exige une nouvelle version et une note de migration.
TS01–TS44 restent des identités permanentes.

La suite démontre seulement « réussit les tests d’échange des rapports fournis
avec 0.1.0-draft.6 ». Elle ne valide pas 44 algorithmes SEO. Toute revendication
plus large exige une correspondance par règle et des limites publiées. Aucune
interopérabilité avec un outil tiers n’a encore été démontrée.
