Édition locale courante : **0.1.0-draft.26** — [dispositif de déploiement](docs/release-invariants.md), [migration](docs/migration-draft.26.md), [accès et journaux agents](docs/agent-access-evidence.md), [usages](docs/agent-usage-policy.md) et [performance](docs/performance-evidence.md). Le traitement du client de test et ses traces ne prouvent pas l’accès réel de l’opérateur.

# TSEP — format d’échange de preuves

**Technical SEO Evidence Protocol · 0.1.0-draft.26 · initié par Edikka · [English](README.md)**

Transmettre un audit SEO technique que son destinataire peut examiner, rejouer et
contester : mêmes identifiants, périmètre explicite, preuves liées aux constats et
inconnues conservées. Le rapport distingue ce qui est établi de ce qui reste à vérifier.

Pour TS02, le [parcours du plan préalable](docs/redirect-plan-workflow.md) prépare
une fiche lisible et lie une décision réellement fournie aux captures ultérieures.
L'[ébauche Search Console](docs/search-console-observations.md) rapproche un export
API fourni et les preuves techniques rejouées, sans verdict TS08/TS12 automatique.

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
Trente règles précisent onze contrôles : TS01, TS02, TS04, TS07, TS10, TS34, TS35, TS41, TS42, TS43 et TS44. Elles disposent d’un interpréteur borné sur entrées brutes. La comparaison
de contenu TS10-A02 reste une revue humaine fournie et liée aux captures.

Les imports de performance séparent les p75/classes terrain (CrUX) des diagnostics
de laboratoire (séries Lighthouse). Décisions et hypothèses restent fournies ; une
revue manquante demeure inconnue. Voir la [méthode et ses limites](docs/performance-evidence.md).

Le [laboratoire TS44](docs/critical-content-laboratory.md) compare quatre variantes sur six échanges HTTP locaux réels, avec DOM et revues explicitement rédigés.

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
   Des captures structurées déjà disponibles peuvent aussi produire directement
   le [paquet de rapport, preuves et EARL](docs/capture-adapter.md), avec résultats calculés et couverture explicite.
   Le [rapport HTML autonome](docs/html-report.md) permet de lire les preuves hors
   ligne et de comparer deux évaluations conservées. Le [parcours guidé TS01](docs/guided-capture.md)
   collecte les octets bruts, fige les critères avant mesure et rejoue hors ligne ;
   l’interpréteur 5 fournit un [extracteur de texte source TS01](docs/source-text-v5.md)
   distinct de TS07, avec cas contradictoires figés et limites explicites.
   Le collecteur 6 précontrôle les marqueurs sur la référence ; l’adaptateur 6
   conserve la traçabilité et le HTML 4 affiche ce précontrôle et les types de média.
   Le [diagnostic de couverture](docs/reference-diagnostics.md) inventorie les limites
   candidates sans produire de verdict. Le [diagnostic par paire](docs/diagnostic-campaign.md)
   compare des phases préenregistrées et les limites d’extraction des corps changés.
   Le protocole est draft.26 ; la [proposition noscript TS01](docs/proposals/noscript-consensus.md) est non appliquée.
2. **Déclarer une couverture partielle** : sélectionner une liste `custom`, conserver
   les inconnues en NT/inconclusive et relier chaque preuve à sa cible. Une sélection
   TS01/TS07 ne satisfait pas un profil nommé. Aucun test isolé ne valide son parent.
3. **Passer la suite de conformance** : fournir un adaptateur JSON sur entrée/sortie
   standard, puis exécuter `python3 conformance/run.py --rules TS01-A01,TS01-A02 --command 'python3 mon_adaptateur.py'`
   pour ce sous-ensemble, ou omettre `--rules` pour les trente règles. Déclarer
   « passes TSEP 0.1.0-draft.26 conformance for TS01-A01, TS01-A02 » avec les bornes
   réellement prises en charge. [Format d’entrée et comparaison](docs/conformance.md). Publier séparément
   accords, désaccords et couverture réduite : les indéterminés acceptés sur des
   limites de référence signalées ne sont pas des évaluations réussies.

Un C automatique exige toutes les règles du contrôle `automatic`, leur couverture
complète et `assessor.tool.name/version`. TS01-A01/A02 sont automatic : 200 final
et identité de ressource selon l’intention préalable (URL, empreinte, stabilité
déclarée ou marqueurs littéraux dans le texte source extrait). Une variation
exige au moins un marqueur requis respecté pour passer par cette méthode ;
commentaires et script/style sont exclus. TS07-A01/A02/A03
restent semiAuto ; TS10-A02 reste manual. Définir une référence de contenu pertinente reste une responsabilité humaine.

Pour une première implémentation extérieure, utiliser le [kit pilote TS01](docs/pilot-ts01.fr.md) :
base technique figée, critères préalables, captures propres et rejeu humain.
Le kit permet la préparation ; le recrutement et le pilote ne sont pas lancés.

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

**Statut au 9 octobre 2026 : candidat de développement dans un dépôt public ;
vérification locale et CI distante observées, sans revue indépendante de praticiens établie.**

TSEP est hébergé dans [web-evidence/tsep](https://github.com/web-evidence/tsep), sous
[Web Evidence](https://github.com/web-evidence). Il a été initié par Edikka, qui
en reste le responsable. La [première CI](https://github.com/web-evidence/tsep/actions/runs/37962185984)
a réussi ses sept jobs sur le commit `253b0a1` : Linux/Python 3.9–3.14 et macOS/Python 3.14.
Le dépôt, les issues, les pull requests et la CI sont consultables publiquement. Voir les
[résultats datés et leur portée](docs/development.md#première-ci-observée) avant
d’appliquer ce résultat à une autre révision.
Pour une révision ultérieure, consulter son commit et son résultat dans le
[workflow de vérification](https://github.com/web-evidence/tsep/actions/workflows/verify.yml).

| Étape | Critère de succès avant la 1.0 |
| --- | --- |
| Stabiliser les méthodes | Applicabilité, preuves, limites et cas contradictoires pour chaque règle ; parité FR/EN vérifiée |
| Établir l’interopérabilité | Au moins une implémentation externe passe une couverture déclarée de la suite ; écarts documentés |
| Organiser la revue | Revue indépendante documentée et deux comainteneurs indépendants identifiés selon la gouvernance |
| Figer une version | Désaccords normatifs résolus ou explicitement exclus, migration documentée, archives reproductibles et CI observée sur la matrice annoncée |

Ces critères sont cumulatifs pour la 1.0 et ne constituent pas un calendrier de
publication. La CI observée répond à une partie du dernier critère. Tous les autres
critères restent ouverts, dont l’implémentation externe et la revue indépendante.

## Limites

TSEP est une proposition de format, pas une certification ou un standard reconnu.
Le validateur vérifie les déclarations et les empreintes, pas leur authenticité,
la pertinence de l’intention ni l’exactitude de tous les jugements. Une empreinte
ne prouve ni l’auteur ni la date réelle de collecte. Les cas fournis sont synthétiques.

L’interpréteur couvre trente règles dans un sous-ensemble documenté ; les entrées
non prises en charge restent indéterminées. TS07-A03 compare des captures source/DOM fournies, sans exécuter JavaScript ;
le plan et les exemptions nécessitent une revue. TS10 compare les signaux d’une famille déclarée et vérifie le rattachement de la revue
humaine de contenu, sans en garantir la justesse. Un contrôle partiel ne produit jamais de conformité globale.
Aucun résultat ne garantit indexation, classement ou comportement futur d’un moteur.

[Contrat FR](docs/contract.fr.md) · [44 contrôles](docs/controls.fr.md) ·
[Source bilingue](spec/protocol.json) · [Schéma](schemas/report.schema.json) ·
[Migration draft.7](docs/migration-draft.7.md) · [EARL](docs/interoperability.md) ·
[Gouvernance](GOVERNANCE.md) · [Contribuer](CONTRIBUTING.md) · [Historique](CHANGELOG.md) ·
[Clause de recette](docs/acceptance-clause.md) · [Sonde HTTP](probes/README.md).

Citer `TSEP@0.1.0-draft.26:TS07` avec périmètre, résultat, preuve et empreinte d’archive.
Textes/données CC BY 4.0, code Apache-2.0 : [licences](LICENSE.md), [citation](CITATION.cff).
[Développement, vérification complète et dépôt autonome](docs/development.md).

[TS02 HTTP trajectories / Trajectoires HTTP](docs/redirects.md) · [Draft.8 migration](docs/migration-draft.8.md)

[TS04 / shared robots](docs/robots.md) · [Draft.9 migration](docs/migration-draft.9.md)

[Structured rendered states / États rendus structurés](docs/structured-rendering.md) · [Draft.10 migration](docs/migration-draft.10.md)

[Same-navigation laboratory / Laboratoire avec navigation attribuée](docs/same-navigation-laboratory.md) · [Draft.11 migration](docs/migration-draft.11.md)

[Canonical attributes / Attributs de canonical](docs/canonical-attribute-coverage.md) · interpreter 11 / adapter 12

[Draft.12 — TS04 client scope / Portée du client TS04](docs/migration-draft.12.md)

[Draft.13 — Known robots fields / Champs robots connus](docs/migration-draft.13.md)

[Draft.14 — Sitemap page locations / URL de pages](docs/migration-draft.14.md)

[Draft.15 — Source directives / Directives source](docs/migration-draft.15.md)

[TS43 controlled loopback laboratory / Laboratoire contrôlé TS43](docs/agent-access-laboratory.md) : six prefrozen scenarios, eight actual local requests, fictional sources/reviews; no provider visit.
