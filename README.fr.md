# TSEP — format d’échange de preuves

**Technical SEO Evidence Protocol · 0.1.0-draft.3 · initié par Edikka · [English](README.md)**

Transmettre un audit SEO technique que son destinataire peut examiner, rejouer et
contester : mêmes identifiants, périmètre explicite, preuves liées aux constats et
inconnues conservées. Le rapport distingue ce qui est établi de ce qui reste à vérifier.

## Pour qui

Équipes SEO et développement qui préparent une recette, commanditaires qui examinent
les preuves d’un audit, éditeurs d’outils qui veulent exporter leurs observations
dans un format commun sans transformer leur couverture partielle en conformité globale.

## La sortie réelle

Un `report.json`, ses fichiers de preuves avec SHA-256, une décision sur les seuls
contrôles/cibles déclarés et un compagnon EARL JSON-LD. Chaque contrôle porte C,
NC, NA ou NT ; les règles atomiques portent pass, fail, not-applicable ou inconclusive.

**TS01–TS44 sont les identifiants permanents hérités de la grille 1.1.** La séquence
de versions TSEP est distincte ; les sources FR/EN et leur provenance restent intactes.
Neuf règles précisent TS01, TS07 et TS10. Quatre disposent d’un interpréteur borné
sur entrées brutes : TS01-A01/A02 et TS07-A01/A02.

## Essayer en deux minutes

Python 3.9+, bibliothèque standard uniquement ; exemples synthétiques, sans compte
ni collecte réseau. Depuis la racine :

```sh
python3 tsep.py validate examples/pass/report.json
python3 tsep.py gate examples/pass/report.json --summary --lang fr
python3 tsep.py gate examples/fail/report.json --summary --lang fr
python3 conformance/run.py
python3 tsep.py earl examples/partial/report.json
```

Le cas réussi affiche `GO_WITH_RESERVATIONS`, `C=1` et **1 contrôle sur 44, une cible,
preuves synthétiques**. Le cas d’échec retourne volontairement le code 1. Une
validation du rapport établit sa cohérence et l’intégrité des fichiers.

## Implémenter TSEP

1. **Émettre un rapport** : figer version et empreinte du protocole, déclarer cibles,
   sélection et outil. `init` commence en NT ; `add-evidence` calcule le SHA-256 et
   enregistre type, cibles et date ; `record` ajoute le résultat motivé du contrôle
   et ses observations atomiques. Voir le [parcours CLI complet](docs/cli.md).
2. **Déclarer une couverture partielle** : sélectionner une liste `custom`, conserver
   les inconnues en NT/inconclusive et relier chaque preuve à sa cible. Une sélection
   TS01/TS07 ne satisfait pas un profil nommé. Aucun test isolé ne valide son parent.
3. **Passer la suite de conformance** : fournir un adaptateur JSON sur entrée/sortie
   standard, puis exécuter `python3 conformance/run.py --command 'python3 mon_adaptateur.py'`.
   Déclarer les quatre règles et les bornes réellement prises en charge, pas « 44
   contrôles automatiques ». [Format d’entrée et comparaison](docs/conformance.md).

Un C automatique exige toutes les règles du contrôle `automatic`, leur couverture
complète et `assessor.tool.name/version`. TS01-A01/A02 sont automatic : 200 final
et égalité exacte URL/empreinte du corps avec l’intention préalable. TS07-A01/A02
restent semiAuto. Définir une référence de contenu pertinente reste une responsabilité humaine.

## Profils de preuves

| Profil | Contrôles | Type de preuve |
| --- | ---: | --- |
| TSEP-1 | 27 | Observations publiques et contexte déclaré |
| TSEP-2 | 29 | TSEP-1 et outils webmaster du moteur visé ; Google, première série normative |
| TSEP-3 | 44 | TSEP-2, logs, configuration, inventaires, historique et CI |

Ces profils décrivent les preuves nécessaires, pas un niveau de qualité. Le type
`webmaster-tools` déclare son `engine` ; une preuve d’un autre moteur ne valide pas
la série Google. Les listes exactes de contrôles sont versionnées dans le JSON.

## Statut et trajectoire vers la 1.0

**Statut : candidat de développement non publié ; validation locale, sans revue indépendante établie.**

| Étape | Critère de succès avant la 1.0 |
| --- | --- |
| Stabiliser les méthodes | Applicabilité, preuves, limites et cas contradictoires pour chaque règle ; parité FR/EN vérifiée |
| Établir l’interopérabilité | Au moins une implémentation externe passe une couverture déclarée de la suite ; écarts documentés |
| Organiser la revue | Revue indépendante documentée et deux comainteneurs indépendants identifiés selon la gouvernance |
| Figer une version | Désaccords normatifs résolus ou explicitement exclus, migration documentée, archives reproductibles et CI observée sur la matrice annoncée |

Ces critères sont des objectifs, pas des résultats acquis ni un calendrier de publication.

## Limites

TSEP est une proposition de format, pas une certification ou un standard reconnu.
Le validateur vérifie les déclarations et les empreintes, pas leur authenticité,
la pertinence de l’intention ni l’exactitude de tous les jugements. Une empreinte
ne prouve ni l’auteur ni la date réelle de collecte. Les cas fournis sont synthétiques.

L’interpréteur couvre quatre règles dans un sous-ensemble documenté ; les entrées
non prises en charge restent indéterminées. TS07-A03 et TS10 exigent d’autres
preuves et examens. Un contrôle partiel ne produit jamais de conformité globale.
Aucun résultat ne garantit indexation, classement ou comportement futur d’un moteur.

[Contrat FR](docs/contract.fr.md) · [44 contrôles](docs/controls.fr.md) ·
[Source bilingue](spec/protocol.json) · [Schéma](schemas/report.schema.json) ·
[Migration draft.3](docs/migration-draft.3.md) · [EARL](docs/interoperability.md) ·
[Gouvernance](GOVERNANCE.md) · [Contribuer](CONTRIBUTING.md) · [Historique](CHANGELOG.md) ·
[Clause de recette](docs/acceptance-clause.md) · [Sonde HTTP](probes/README.md).

Citer `TSEP@0.1.0-draft.3:TS07` avec périmètre, résultat, preuve et empreinte d’archive.
Textes/données CC BY 4.0, code Apache-2.0 : [licences](LICENSE.md), [citation](CITATION.cff).
[Développement, vérification complète et dépôt autonome](docs/development.md).
