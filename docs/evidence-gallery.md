# Evidence gallery / Galerie de preuves

## Français

Cette galerie est un **parcours de lecture**, pas un nouveau comparateur ni un
rapport global. Elle prépare une démonstration publique à partir de paquets
conservés, avec leur méthode et leurs outils d’origine. L’assemblage ne constitue
ni une nouvelle collecte, ni une validation indépendante. Le protocole normatif
reste `0.1.0-draft.7` ; les expériences ne sont pas promues implicitement.

### Parcours proposé

| Étape | Ce que le lecteur peut examiner | Limite à montrer au même endroit |
| --- | --- | --- |
| Cas réel TS01 | Réponses, intention, critères et rapport conservés d’une page réelle | Un refus du lecteur ou une identité non établie reste visible ; ne pas remplacer le rapport par le résultat d’une expérience |
| Copies perturbées | [Recettes](perturbation-experiment.md) appliquées à une source retenue, dont un contre-exemple où des marqueurs subsistent malgré une fonction retirée | Copies synthétiques, pas incidents observés sur le site ; les marqueurs ne testent pas le fonctionnement |
| HTTP versus HTML | [Laboratoire TS07](ts07-laboratory.md) : `X-Robots-Tag: noindex` avec un HTML inchangé | Absence de directive dans le HTML ≠ absence de directive HTTP ; correction donnant NT, pas C |
| Source versus état rendu | [États TS07](rendered-states.md) et [import](render-import.md) : état après interaction, source conservée et résultats atomiques | États discrets, plan explicite, revue d’accès manquante ; aucun comportement de moteur démontré |
| Déclarations canoniques | [Laboratoire TS10](canonical-laboratory.md) : HTTP Link, HTML, sitemap et liens | Garder les attentes non atteintes et les refus DOM du lecteur ; un rejeu identique ne les transforme pas en succès |
| Inventaire structuré | [Métadonnées DOM](rendered-metadata-inventory.md), [candidat](rendered-canonical-candidate.md) et [recettes prédéclarées](predeclared-canonical-laboratory.md) | Expériences séparées des décisions TSEP ; API et environnement non authentifiés |
| Historique | [Séquences](canonical-state-sequences.md) : accord, contradiction, puis accord dans trois relevés | Le dernier état ne supprime pas le précédent ; aucune conclusion de stabilité entre captures |

Les liens décrivent les méthodes distribuées. Ils ne signifient pas que des
captures privées sont incluses dans l’archive du protocole. Une galerie locale
peut réunir les paquets existants ; une édition publique demande une sélection
explicite des fichiers et une publication distincte.

### Présenter chaque cas

Conserver l’identifiant du paquet et du cas, son empreinte, sa date, son caractère
réel/synthétique, sa méthode, les versions d’outils, l’environnement déclaré, les
preuves et le résultat d’origine. Montrer côte à côte les champs HTTP, les balises
source et les états DOM **effectivement disponibles dans ce cas**. Ne pas remplir
une colonne avec la preuve d’une autre campagne. Une absence de capture se dit
« non collecté », pas « aucun signal ». Une absence de champ dans une réponse
complète ne décrit que cette réponse.

Le texte d’un extrait reste exact et sa source complète reste accessible. Les
chemins d’ancêtres lexicaux ne sont pas des positions DOM. Une différence visible
entre deux pièces n’établit pas seule sa cause. La galerie ne calcule ni égalité
de listes, ni priorité entre surfaces, ni score entre campagnes. Les légendes de
présentation restent distinctes des décisions existantes.

Séparer visuellement le cas réel, ses copies perturbées et les laboratoires
synthétiques. Séparer aussi les résultats normatifs des candidats expérimentaux.
Les actions d’interface qui révèlent un résultat pré-calculé doivent le dire ;
elles ne lancent pas un test. Le rejeu Python utilise les octets conservés et les
outils propres à chaque paquet, sans collecte ni exécution navigateur.

### Rejeu et maturité

Vérifier chaque archive et son manifeste avant extraction. Conserver les outils
d’origine et les limites de leur rejeu. Un résultat identique avec code 2 dans le
laboratoire TS10 signifie que les écarts aux attentes subsistent : l’intégrité du
rejeu et la réussite nominale du scénario sont deux faits distincts. Ne pas
additionner les cas ou les assertions de campagnes hétérogènes en un indicateur
de couverture ou de qualité SEO. Les exemples sont une sélection éditoriale.

Le dépôt public, le travail local et la version normative sont trois informations
distinctes. Dater toute comparaison Git et citer les commits réellement observés.
Des tests locaux ne sont pas une CI distante observée. La relecture d’un bilan par
un assistant IA n’est ni une revue humaine, ni une exécution indépendante.

Avant l’insight : choisir quelques cas avec une question concrète, rendre leurs
preuves et commandes accessibles, conserver un contre-exemple et une limite,
préparer une archive publique identifiée, puis faire la recette de lecture/rejeu.
L’intégration et la publication Edikka restent séparées. Aucune promesse de
classement, d’indexation, d’adoption, de certification ou de reconnaissance du
protocole ne découle de cette galerie.

## English

This is a **reading route**, not a new comparator or an aggregate report. It
organizes retained packages with their original tools and methods, without new
collection or independent validation. The normative protocol remains draft.7;
experiments are not implicitly promoted. The table above connects the real TS01
case, authored source perturbations, TS07 HTTP and rendered-state laboratories,
the TS10 laboratory, structured DOM inventories, canonical candidates and ordered
state sequences. Method links do not include private observations in the protocol
distribution. Public packaging and publication remain separate actions.

Every case retains package/case identity, checksums, date, real/synthetic origin,
method, tool versions, declared environment, evidence and original result. Show
HTTP fields, source tags and DOM snapshots only when actually available for that
case; never fill a gap with another campaign's evidence. Missing captures are
uncollected, not absent signals. A missing field in a complete response describes
only that response. Excerpts remain exact and link to complete evidence. Lexical
ancestors are not DOM positions. Visible differences alone do not establish cause.
No new list equality, precedence, score or cross-campaign outcome is calculated.

Visually separate real observations, their synthetic copies and synthetic sites;
also separate normative results from experiments. Interface controls displaying
precomputed results do not execute tests. Python replay uses retained bytes and
each package's own tools, without collection or browser execution. Verify package
manifests before extraction. Identical replay with the TS10 laboratory's code 2
preserves unmet expectations; replay integrity does not make its scenarios pass.
Do not sum heterogeneous case/assertion counts into SEO coverage or quality.

Public repository state, local work and normative version are separate facts.
Date Git comparisons and cite observed commits. Local tests are not observed
remote CI. AI review of a supplied account is neither human review nor independent
execution. For the insight, choose concrete questions, expose evidence and replay
commands, retain a counterexample and a limitation, prepare an identified public
archive and perform a reading/replay acceptance check. Edikka integration and
publication are separate; no indexing, ranking, adoption, certification or
recognition follows from this gallery. This addition changes no normative rule,
old capture, comparison, report, published archive or tag.
