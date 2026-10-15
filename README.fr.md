[TS23 — hreflang fourni / supplied hreflang](docs/hreflang-reciprocity-evidence.md), [draft.39 migration](docs/migration-draft.39.md).

[TS18 — graphe et inventaires fournis / supplied graph and inventories](docs/graph-reconciliation-evidence.md), [draft.38 migration](docs/migration-draft.38.md).

[TS16 — liens entrants fournis / supplied incoming links](docs/incoming-links-evidence.md), [draft.37 migration](docs/migration-draft.37.md).

[TS17 — liens essentiels fournis / supplied essential links](docs/essential-links-evidence.md), [draft.36 migration](docs/migration-draft.36.md).

[TS15 — fichiers sitemap fournis / supplied sitemap files](docs/sitemap-files-evidence.md), [draft.35 migration](docs/migration-draft.35.md).

[TS33 — validation layers / couches de validation](docs/structured-validation-evidence.md), [draft.34 migration](docs/migration-draft.34.md).

TS32 : [corpus d’identités JSON-LD déclaré](docs/structured-identity-evidence.md), [migration draft.33](docs/migration-draft.33.md). Cohérence du corpus fourni et revues liées ; aucune stabilité temporelle établie.
TS31 : [preuves JSON-LD/contenu](docs/structured-content-evidence.md), [migration draft.32](docs/migration-draft.32.md). Revues liées aux graphes fournis ; aucune visibilité authentifiée ni résultat enrichi garanti.

TS36 : [suivi après changement](docs/release-monitoring.md), [import et clôture](docs/release-monitoring-intake.md), [migration draft.31](docs/migration-draft.31.md). Cas rédigés uniquement ; aucune échéance réelle future accomplie.

Édition locale : **0.1.0-draft.39** — [TS33 : couches de validation](docs/structured-validation-evidence.md), [migration](docs/migration-draft.34.md). Vingt-deux contrôles outillés /60 règles ; aucune qualification réelle Edikka.

TS08 : [inspections natives](docs/inspection-evidence.md) et [acquisition](docs/search-console-acquisition.md) restent disponibles.

TS02 : le [collecteur prospectif](docs/redirect-collection.md) conserve chaque saut
HTTP dans les bornes approuvées, puis produit le rapport existant et son rejeu.
Workflow facultatif non normatif ; aucune évaluation réelle Edikka déduite.

Préparation TS31–33 : [états rendus fournis et comparaison source/DOM](docs/jsonld-rendered-observation.md), sans nouvelle collecte ni verdict. Priorité du 12 octobre : TS08 puis TS12, qualification avant l’application ; TS36 est maintenant disponible ; TS31–33 ensuite.

Préparation TS31–33 : [traitement JSON-LD hors ligne](docs/jsonld-processing.md), puis [extraction HTML attribuée et combinaison des blocs](docs/jsonld-html-observation.md). Cas contradictoires figés et rejeu exact ; base effective, faits visibles et validateurs restent à qualifier. Ces composants n’ajoutent pas de règles TS31–33.

Le [laboratoire TS39](docs/delivery-laboratory.md) ajoute huit expériences figées, 38 échanges HTTP réels entre origine et cache locaux, une correction avec purge et un rejeu hors ligne ; pages et revues restent fictives.

TS39 dispose de [trois règles de diffusion](docs/delivery-evidence.md) : matrice préalable, signaux par contexte et attribution du cache, avec revues liées et inconnues explicites.

# TSEP — format d’échange de preuves

**Technical SEO Evidence Protocol · 0.1.0-draft.39 · initié par Edikka · [English](README.md)**

Transmettre un audit SEO technique que son destinataire peut examiner, rejouer et
contester : mêmes identifiants, périmètre explicite, preuves liées aux constats et
inconnues conservées. Le rapport distingue ce qui est établi de ce qui reste à vérifier.

Pour TS02, le [parcours du plan préalable](docs/redirect-plan-workflow.md) prépare
une fiche lisible et lie une décision réellement fournie aux captures ultérieures.
L'[ébauche Search Console](docs/search-console-observations.md) rapproche un export
API fourni et les preuves techniques rejouées, sans verdict TS08/TS12 automatique.
L'[observateur de variantes de diffusion](docs/delivery-variants-observation.md)
prépare TS39 : différences HTTP et correspondance Vary bornée, sans verdict de contrôle.

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
Soixante règles atomiques précisent vingt-deux contrôles : TS01, TS02, TS04, TS07, TS08, TS10, TS12, TS15, TS16, TS17, TS18, TS31, TS32, TS33, TS34, TS35, TS36, TS39, TS41, TS42, TS43 et TS44. Leurs interpréteurs restent bornés aux preuves fournies. La comparaison
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
   Le collecteur 8 précontrôle les marqueurs sur la référence ; son [profil parsé guidé](docs/guided-parsed-markers.md)
   refuse toute hypothèse complète contradictoire et exige Node 24 dès la préparation.
   L’adaptateur 28 conserve les preuves ; le HTML 11 affiche le précontrôle.
   Le [diagnostic de couverture](docs/reference-diagnostics.md) inventorie les limites
   candidates sans produire de verdict. Le [diagnostic par paire](docs/diagnostic-campaign.md)
   compare des phases préenregistrées et les limites d’extraction des corps changés.
   Draft.28 ajoute un [profil distinct de marqueurs HTML parsés](docs/source-markers.md), facultatif.
   L’ancienne [proposition lexicale noscript TS01](docs/proposals/noscript-consensus.md) reste non appliquée.
2. **Déclarer une couverture partielle** : sélectionner une liste `custom`, conserver
   les inconnues en NT/inconclusive et relier chaque preuve à sa cible. Une sélection
   TS01/TS07 ne satisfait pas un profil nommé. Aucun test isolé ne valide son parent.
3. **Passer la suite de conformance** : fournir un adaptateur JSON sur entrée/sortie
   standard, puis exécuter `python3 conformance/run.py --rules TS01-A01,TS01-A02 --command 'python3 mon_adaptateur.py'`
   pour ce sous-ensemble, ou omettre `--rules` pour les soixante et une règles. Déclarer
   « passes TSEP 0.1.0-draft.39 conformance for TS01-A01, TS01-A02 » avec les bornes
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

L’interpréteur couvre soixante et une règles dans un sous-ensemble documenté ; les entrées
non prises en charge restent indéterminées. TS07-A03 compare des captures source/DOM fournies, sans exécuter JavaScript ;
le plan et les exemptions nécessitent une revue. TS10 compare les signaux d’une famille déclarée et vérifie le rattachement de la revue
humaine de contenu, sans en garantir la justesse. Un contrôle partiel ne produit jamais de conformité globale.
Aucun résultat ne garantit indexation, classement ou comportement futur d’un moteur.

[Contrat FR](docs/contract.fr.md) · [44 contrôles](docs/controls.fr.md) ·
[Source bilingue](spec/protocol.json) · [Schéma](schemas/report.schema.json) ·
[Migration draft.7](docs/migration-draft.7.md) · [EARL](docs/interoperability.md) ·
[Gouvernance](GOVERNANCE.md) · [Contribuer](CONTRIBUTING.md) · [Historique](CHANGELOG.md) ·
[Clause de recette](docs/acceptance-clause.md) · [Sonde HTTP](probes/README.md).

Citer `TSEP@0.1.0-draft.39:TS07` avec périmètre, résultat, preuve et empreinte d’archive.
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
