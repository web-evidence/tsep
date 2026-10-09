# Technical SEO Evidence Protocol — TSEP

**0.1.0-draft.1 · version de travail · initié par Edikka · [English](README.md)**

Un audit SEO technique que l’on peut examiner et contester : contrôles identifiés,
périmètre déclaré, preuves traçables et inconnues explicites. Ce kit fonctionne
indépendamment du site Edikka. Il ne constitue ni une certification, ni un standard
reconnu, ni une note SEO, ni une garantie d’indexation ou de classement.

## Dépôt autonome

Ce dépôt est la source de développement indépendante. Voir [les règles de développement et d’intégration](docs/development.md). Vérification locale complète : `python3 scripts/verify.py`. Le tag d’import conserve le candidat initial ; les évolutions d’infrastructure restent un état de développement jusqu’à une publication distincte.

## Essayer en deux minutes

Python 3.9 ou supérieur, sans dépendance, compte, clé API ou collecte réseau pour
la démonstration. Depuis ce dossier :

```sh
python3 examples/replay.py
python3 tsep.py validate examples/pass/report.json
python3 tsep.py gate examples/fail/report.json
python3 tsep.py earl examples/partial/report.json
python3 -m unittest discover -s tests -v
```

Le validateur contrôle la structure du rapport et les empreintes des preuves,
pas la justesse du jugement de l’auditeur. Le cas d’échec renvoie volontairement
le code 1. Les exemples sont synthétiques : aucune mesure d’Edikka ou d’un tiers.
L’exemple réussi concerne **TS01 sur une seule URL**.

Pour initialiser un rapport, tous ses contrôles restant « non testés » :

```sh
python3 tsep.py init --profile TSEP-1 \
  --target https://example.com/ \
  --assessor 'Votre équipe' --label 'Échantillon accueil' \
  --selection-method 'Une URL choisie ; aucune généralisation au site' > rapport.json
```

Ajouter ensuite les preuves et les conclusions motivées. Une sélection
`--controls TS01,TS07` est un périmètre personnalisé, pas une satisfaction de
TSEP-1. La CLI ne visite pas l’URL.

## Les pièces du protocole

- [Contrat de rapport et règles de décision](docs/contract.fr.md)
- [44 contrôles en français](docs/controls.fr.md)
- [Source canonique bilingue](spec/protocol.json) et [schéma JSON](schemas/report.schema.json)
- [Interopérabilité EARL et relation à ACT, EN/FR](docs/interoperability.md)
- [Gouvernance et conflits d’intérêts, EN/FR](GOVERNANCE.md)
- [Contribution, EN/FR](CONTRIBUTING.md), [historique](CHANGELOG.md)
- [Clause de recette utilisable dans un devis, EN/FR](docs/acceptance-clause.md)
- [Licences et attribution](LICENSE.md)
- [Sonde HTTP bornée et ses 48 cas historiques de non-régression](probes/README.md)

Le JSON versionné, le contrat de rapport et le schéma forment ensemble le contrat
normatif du candidat. Une incohérence est un défaut à signaler. La grille Edikka
1.1 reste intacte dans `upstream/` ; TSEP possède une numérotation distincte.

## Profils de preuves

| Profil provisoire | Contrôles | Accès |
| --- | ---: | --- |
| TSEP-1 | 27 | Observations publiques et contexte d’audit déclaré |
| TSEP-2 | 29 | TSEP-1 et Google Search Console |
| TSEP-3 | 44 | TSEP-2, logs, configuration, inventaires, historique et CI |

Ces profils décrivent les accès nécessaires ; ils ne classent pas la qualité.
Public ne signifie pas automatisable. Le contexte indique le comportement attendu,
sans prouver qu’il existe. Les listes exactes d’IDs sont versionnées dans le JSON.
Les contrôles Google ne sont pas validés par un rapport Bing. Bing peut compléter
les preuves ; ce candidat ne comporte pas de série normative propre à Bing.

## Ce qui est vérifié

La CLI vérifie structure, périmètre, références, couverture des entrées requises,
empreintes SHA-256 et décision conservatrice. La suite teste **l’échange des
rapports**, pas 44 algorithmes de contrôle SEO. Elle ne prouve ni l’authenticité
d’une capture ni la qualité d’un jugement humain. Une empreinte établit une
intégrité ; elle n’atteste ni l’auteur ni la date réelle de collecte.

Les méthodes ne disposent pas encore d’une suite de cas par contrôle relue
indépendamment. Aucun adoptant, relecteur, comainteneur, dépôt public ou DOI n’est
revendiqué. Le nom reste provisoire, sans validation juridique. Aucun chiffre
d’adoption de llms.txt ne fonde ce travail.

## Reprendre et citer

Référence stable : `TSEP@0.1.0-draft.1:TS07`, avec périmètre, résultat et preuve.
Une alerte d’outil peut correspondre à une partie d’un contrôle ; elle ne suffit
pas à déclarer le contrôle entier conforme.

Citation : *Edikka. Technical SEO Evidence Protocol (TSEP), 0.1.0-draft.1,
9 octobre 2026. Version de travail.* Joindre l’empreinte de l’archive lors du
partage de ce candidat non publié ; ne pas inventer de DOI.

Texte et données sous CC BY 4.0, code original sous Apache-2.0. L’attribution peut
figurer dans la documentation ou les métadonnées ; aucune obligation promotionnelle
supplémentaire de lien retour n’est ajoutée.

Construction autonome et déterministe, avec sortie hors de ce dossier :

```sh
python3 maintain.py check
python3 maintain.py build --output /tmp/tsep-0.1.0-draft.1.zip
```
