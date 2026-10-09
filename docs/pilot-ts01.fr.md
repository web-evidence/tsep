# Pilote d’implémentation TS01

**Plan pilote 1 · préparé le 9 octobre 2026 · recrutement non lancé** · [English](pilot-ts01.en.md)

Un développeur extérieur à Edikka peut-il implémenter TS01 depuis les documents
publics et produire des résultats qu’une autre personne peut rejouer ? Ce pilote
limité teste cette question. Il ne mesure ni l’adoption, ni les 44 contrôles, ni
un site entier, ni la maturité de TSEP 1.0. Edikka a initié TSEP et bénéficie
commercialement de sa réputation ; voir la [gouvernance](../GOVERNANCE.md).
Les revues assistées par IA ne sont pas des relectures humaines indépendantes.

## Figer la référence

Utiliser le protocole **0.1.0-draft.7**, le format de rapport 2 et les règles
**TS01-A01 et TS01-A02**. La base technique est le commit
`824c48b19abe15f76f9a9058718cff461a7dbabb` ; son archive de développement porte
le SHA-256 `8164b70b08aa200ab0c45f905e0079dd2bfd9ba22e6a1f9428e2c1a840f11de0`.
Le SHA-256 du protocole normatif est
`c7666df08e752400a588963e8781b6441e05b634c62289a607c04f807a5604da`.
Le kit pilote est un ajout documentaire ultérieur, sans modification de ces règles
ni du corpus. Un paquet qui l’inclut possède une autre empreinte : inscrire son
commit exact, son SHA-256 et son DOI de version dans la fiche d’activation.
Le [manifeste de référence](pilot-ts01-baseline.sha256) fige 72 fichiers inchangés
de cette base technique, dont tous les outils, contrats, schémas et corpus.
Les README, l’historique, l’inventaire de distribution et la citation sont des
exceptions documentaires, sans rôle dans l’interprétation des règles ou décisions. Depuis
la racine du paquet extrait, sans Git :

```sh
shasum -a 256 -c docs/pilot-ts01-baseline.sha256
```

Sous Linux, `sha256sum -c docs/pilot-ts01-baseline.sha256` est équivalent. Vérifier
aussi le paquet complet avec `shasum -a 256 -c SHA256SUMS`.
`package_archive_sha256` désigne le ZIP construit par `maintain.py` depuis le commit
du paquet. Le dépôt manuel Zenodo prévu envoie ce ZIP exact, pas une archive source
GitHub automatique. Inscrire le nom du fichier déposé et son SHA-256 téléchargé dans
`zenodo_archive_filename` / `zenodo_archive_sha256` ; ils doivent désigner les mêmes
octets. Exemple : `shasum -a 256 /path/to/downloaded-package.zip`. La recette et les
journaux joints séparément ne font pas partie de ce ZIP. Un DOI seul ne prouve pas
cette égalité.

Lire le [contrat](contract.fr.md), le [format et les limites de conformance](conformance.md)
et le [parcours de rapport](cli.md). TS01-A01 exige un **200 final**. TS01-A02
vérifie l’identité selon l’intention préalable, dans l’ordre du contrat. En particulier,
`representation: "stable"` déclaré auparavant fait échouer toute variation d’empreinte
du corps, même limitée à un horodatage. Ces résumés sont informatifs ; le contrat
et `spec/protocol.json` prévalent. Déclarations, implémentation originale, captures
propres, livrables publics, rejeu humain et délais ci-dessous sont des exigences
propres au pilote, sans ajout au protocole. Geler texte normatif, base exécutable et corpus attendu
pendant l’essai. Consigner les ambiguïtés publiquement ; une interprétation normative
modifiée exige une nouvelle version du protocole et un pilote identifié séparément,
jamais la réécriture des anciens résultats.

## Activer avant l’implémentation

Copier le [modèle d’activation](pilot-ts01-registration.json) dans un nouveau fichier
versionné ; ne jamais remplacer le modèle livré. La copie suit les états
`template-not-activated` → `activated` → `concluded`. Avant l’implémentation,
renseigner tous les champs d’`activation`, convenir des dates et committer le plan
accepté. Consigner son URL de commit immuable et l’événement public de publication/CI
hors de ce même commit pour éviter une autoréférence. Les issues peuvent y renvoyer,
mais une issue modifiable seule n’est pas le plan figé. Le modèle vide **ne constitue
pas** une étude activée ou pré-enregistrée. Garder `conclusion` vide jusqu’à la
publication des résultats observés. Une date locale, une date d’auteur Git ou une
empreinte seules ne prouvent pas un horodatage indépendant.

La fenêtre proposée est de 30 jours calendaires à partir du début convenu, puis
14 jours pour publier le résultat. Le responsable (Edikka) et le participant confirment les dates
avant de commencer ; ce document n’engage ni démarrage, ni nomination, ni rémunération,
ni recrutement. Déclarer séparément les relations du participant et du relecteur avec Edikka sur
les 12 mois précédents et pendant le pilote, leurs financements/rémunérations,
les liens entre relecteur et participant et l’assistance IA. Recueillir l’accord
de chacun pour publier son nom, son affiliation et les relations déclarées. Une implémentation extérieure
rémunérée est signalée comme commandée, sans adoption spontanée revendiquée.
Un nom différent ne suffit pas à établir l’indépendance.

Le participant écrit sa propre interprétation des deux règles ; envelopper ou
copier `conformance/evaluate.py` ou `adapters/captures.py` ne produit pas une seconde
implémentation, pas plus qu’un portage ligne à ligne dans un autre langage. Déclarer
l’exposition antérieure au code d’interprétation de référence et la consultation
prévue : `never`, `after-first-version` ou `throughout`. Si elle suit une première
version, conserver le commit/empreinte de celle-ci avant de lire la référence.
Journaliser la consultation réelle et la reprendre dans la conclusion ; la lecture
de la référence limite ce que le pilote prouve sur la clarté du texte normatif.
La réutilisation du validateur de rapport, du comparateur et de
l’exporteur est permise et déclarée. Consigner dépendances, code repris et aides.
Utiliser les documents publics ; journaliser l’aide technique dans des issues
publiques avant de s’y appuyer. Ne jamais y publier d’identifiants ou données privées :
anonymiser la question et consigner toute aide technique privée sans son contenu sensible.

## Exécuter et conserver

Python 3.9+ exécute les outils de référence. L’adaptateur externe lit un objet JSON
d’entrée sur stdin et écrit uniquement son tableau de résultats sur stdout ; les
diagnostics vont sur stderr. Depuis la racine du paquet figé, remplacer le chemin
de l’adaptateur par celui du participant :

```sh
python3 conformance/run.py --rules TS01-A01,TS01-A02 \
  --command 'python3 /path/to/participant_adapter.py' > conformance-result.json
```

Exécuter tous les cas sélectionnés du corpus inchangé. Le comparateur valide le
corpus complet et sélectionne les couples TS01 ; ne pas modifier `expected`, omettre
des cibles ou supprimer des sorties en trop. Publier code de sortie, commande exacte,
environnement, version/empreinte de l’adaptateur, accords, désaccords et couverture
réduite **par règle**. Seuls les couples explicitement marqués comme limites de
référence admettent inconclusive à la place d’un attendu conclusif ; ils ne sont
jamais des évaluations réussies. Le corpus contient pass, fail et inconclusive pour
chacune des deux règles.

Produire au moins un rapport depuis les **propres captures** du participant,
pas depuis les exemples fournis. Conserver intention préalable, conditions de
requête, chaque saut HTTP, corps complets, outil/version, dates et limites. Utiliser
des ressources de test publiques possédées ou expressément autorisées ; collecte
limitée. Exclure secrets de production et données personnelles. Déclarer les cas
contrôlés comme tels. Conserver les captures brutes et expliquer leur conversion
éventuelle au format borné. Référence de corps/marqueurs antérieure à l’évaluation :
ne pas inventer l’intention après le résultat. Les marqueurs du texte source ne
prouvent ni visibilité rendue, ni indexation, ni classement.

L’interpréteur du participant fournit les résultats atomiques. Créer un rapport
`custom` limité à TS01 par le [parcours init → add-evidence → record](cli.md), ou son
propre exporteur. Attribuer les résultats réellement automatiques avec
`init --mode automatic --tool NAME --tool-version VERSION`, l’identité de
l’interpréteur du participant et les autres arguments requis ; conserver aussi
l’empreinte du code. Les corrections manuelles restent déclarées comme telles,
sans être renommées automatiques. Puis exécuter :

```sh
python3 tsep.py validate /path/to/bundle/report.json
python3 tsep.py gate /path/to/bundle/report.json > gate.json
python3 tsep.py gate /path/to/bundle/report.json --summary --lang fr
python3 tsep.py earl /path/to/bundle/report.json > earl.jsonld
```

Conserver chaque code de sortie. `validate` 0 signifie rapport valide ; `gate` 1
peut correctement signifier NO_GO. Gate 0 signifie GO_WITH_RESERVATIONS **dans le
périmètre déclaré**. Gate 2 signifie INCOMPLETE/REVIEW ; 64 signifie données invalides
(une erreur de syntaxe de commande peut aussi renvoyer 2 : lire le message). NC ou NT
n’est pas un échec du pilote s’il traduit correctement les preuves. Chaque rapport conserve les deux règles, toutes ses cibles, inconnues
et contradictions. Un C automatique exige aussi des preuves complètes et le nom
et la version de l’outil.

## Décider sur preuves

Le pilote réussit seulement si **toutes** ces conditions sont prouvées :

1. **P01 — Plan et attribution.** Le plan activé et les déclarations ont été respectés ; l’interprétation extérieure
   est attribuable et accessible à la revue.
2. **P02 — Conformance.** Le passage complet TS01 n’a aucun désaccord. La couverture réduite acceptée est
   publiée séparément ; aucune règle ne repose uniquement sur des indéterminés.
3. **P03 — Preuves propres.** Au moins un rapport issu de captures propres est valide, ses résultats atomiques
   sont justifiés par les captures et l’intention préalable, gate/EARL conservent
   résultats et portée. Les captures propres établissent au moins un résultat
   conclusif par règle.
4. **P04 — Rejeu humain.** Un humain nommé extérieur à Edikka, différent de l’implémenteur, rejoue les
   entrées figées et obtient les mêmes résultats atomiques, statut du contrôle et
   décision gate. Dates d’émission et présentation JSON peuvent différer. Il vérifie
   la pertinence des preuves, pas seulement le succès des commandes.
5. **P05 — Minimum public et accès pour la revue.** Publier le source de
   l’adaptateur, la sortie de conformance, le rapport, gate et EARL. Les captures
   requises et l’intention préalable sont accessibles au relecteur ; toute restriction
   sur les captures est motivée. Un résumé public expose les limites de rejeu public
   qui en découlent. Ne pas exposer de données sensibles pour satisfaire ce critère ;
   un minimum public non atteint interdit le succès.
6. **P06 — Conclusion publiée.** Publier la conclusion humaine signée, l’effort
   passé, les ambiguïtés, interventions, consultation du code de référence, limites
   et constats défavorables à la date convenue. Ces IDs P01–P06 sont ceux du plan JSON.

Utiliser `success`, `failure` ou `unfinished` pour la conclusion du **pilote**,
séparée des résultats TSEP. Un désaccord persistant, une réussite sans preuve,
un résultat non reproductible ou une aide technique non déclarée interdit le succès.
Retrait, absence de relecteur ou délai dépassé donne `unfinished`, jamais succès ;
conserver le motif et les constats techniques partiels. Attribuer séparément tout
échec technique au participant, à la référence ou à une cause indéterminée, sur
preuves ; un attendu erroné du corpus ne doit pas être imputé à l’implémenteur.
Le passage figé conserve néanmoins son désaccord. Publier le résultat, y
compris défavorable, à la date convenue. Les corrections ultérieures sont des
ajouts datés, pas des remplacements.

Utiliser les modèles de [rapport d’implémentation](../.github/ISSUE_TEMPLATE/pilot-implementation.md)
et d’[ambiguïté](../.github/ISSUE_TEMPLATE/pilot-ambiguity.md).
La revue humaine du contrat peut avancer en parallèle de l’implémentation ; celle
du rapport final suit sa production. Aucun relecteur n’est nommé par ce kit.

## Indicateurs à douze mois

Proposition distincte pour décision du propriétaire : compter les implémentations
extérieures prouvées, contributeurs externes substantiels distincts, cahiers des
charges tiers distincts citant TSEP et citations publiées indépendantes. Exclure
les propres productions Edikka, doublons, étoiles et téléchargements comme preuves
d’adoption. Une preuve absente reste inconnue, pas zéro. Fixer publiquement définitions,
point de départ, date de début et bilan à douze mois avant mesure ; aucun objectif
chiffré ni suivi programmé n’est adopté ici. Les objectifs à douze mois non tranchés
ne modifient pas les critères du pilote.
