# Programme prioritaire — quatre contrôles

Décision de Bertrand du 10 octobre 2026 : remplacer la cible quantitative de dix
contrôles par quatre contrôles approfondis, puis une première confrontation avec
la Search Console et un insight concret. Aucun ordre numérique n'est obligatoire.

| Contrôle | Problème métier à montrer | État à cette étape |
| --- | --- | --- |
| TS04 | Une règle de préproduction interdit l'exploration attendue | Draft.9 : deux règles, lecteur partagé TS07, ressources et parcours de revue ; recette humaine/application réelle à établir |
| TS02 | Une migration mène à la mauvaise destination, ajoute un détour ou boucle | Draft.8 : règles, interpréteur et laboratoire avant/après de 20 requêtes locales ; parcours pratique du plan humain à compléter |
| TS07 | Un noindex HTTP/source/rendu contredit l'intention ; robots peut empêcher sa lecture | Méthode existante ; couverture rendue et parcours de revue à consolider |
| TS10 | Canonical HTTP, HTML, rendu, sitemap ou liens désignent des URL incompatibles | Méthode existante ; limites DOM et revue de contenu à résoudre |

TS01 reste la base existante, sans être compté comme l'un de ces quatre objectifs.
L'ordre de dépendance recommandé est TS04, TS02, TS07, TS10. TS02 peut avancer
indépendamment pendant la définition TS04. Un lecteur robots commun doit servir
TS04 et TS07, avec les politiques RFC/robot explicitement distinguées.

Le [lecteur robots partagé](robots.md) est intégré dans draft.9 pour TS04 et TS07,
avec deux profils explicites et un profil historique fixe. Le laboratoire fournit
les paquets natifs et des questions de revue sans réponses inventées. Une méthode
exécutable n'est pas une recette humaine ni une évaluation réelle d'Edikka.

Une méthode ne sera déclarée aboutie que lorsque ses règles FR/EN, cas conformes,
contradictoires et indéterminés, preuves attribuables, collecte ou import explicite,
rapport, rejeu et limites auront été vérifiés. Les exigences de rendu ou de revue
ne seront pas retirées pour tenir un délai. Des contrôles finalisés techniquement
ne signifient pas une conformité réelle d'Edikka ; chaque évaluation garde son
périmètre, sa date et ses preuves.

La démonstration reliera problème, pièce exacte, correction demandée et nouvelle
observation, avec un témoin correct. Les défauts seront isolés, puis combinés de
manière explicite. Un 200 final n'est pas la conclusion. Une boucle n'est pas
présentée comme terminant en 200 ; une borne de collecte n'est pas une boucle.
Les captures synthétiques restent distinctes des captures réelles.

L'ébauche Search Console rapprochera intention, état technique daté et état Google
rapporté : URL déclarée canonique, URL canonique sélectionnée, état et dernier
crawl. Sans données du compte, seuls des exemples synthétiques sont possibles.
Des dates différentes ou champs absents ne démontrent pas une régression. Aucun
gain de classement ni causalité ne sera attribué à TSEP sur cette seule base.

## English

The owner's October 10 decision supersedes the ten-control target with deep work
on TS04, TS02, TS07 and TS10, followed by a first Search Console comparison and a
concrete insight. TS01 stays as existing infrastructure. This is a development
program, not a completion claim. Keep rendered/human requirements, verify each
method and distinguish technical completion from a real site's assessment.
Demonstrate problem, evidence, requested correction and recapture, including a
positive control. Search Console records remain separate dated observations,
without live-test, ranking or causal claims. Publication remains a separate action.
