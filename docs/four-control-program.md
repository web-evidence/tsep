# Programme prioritaire — quatre contrôles

Décision de Bertrand du 10 octobre 2026 : remplacer la cible quantitative de dix
contrôles par quatre contrôles approfondis, puis une première confrontation avec
la Search Console et un insight concret. Aucun ordre numérique n'est obligatoire.

| Contrôle | Problème métier à montrer | État à cette étape |
| --- | --- | --- |
| TS04 | Une règle de préproduction interdit l'exploration attendue | Draft.13 : deux règles, lecteur partagé TS07, registre fermé de champs hors portée accès, portée du client explicite, ressources et parcours de revue ; chaque application réelle et revue conserve son dossier |
| TS02 | Une migration mène à la mauvaise destination, ajoute un détour ou boucle | Draft.8 : règles et laboratoire ; parcours préalable 1 prépare et importe la décision fournie puis lie les captures. Décision humaine et application Edikka à établir |
| TS07 | Un noindex HTTP/source/rendu contredit l'intention ; robots peut empêcher sa lecture | Draft.11 : lecteur structuré et laboratoire de navigation attribuée ; exécutions livrées séparément, revue et application réelle à établir |
| TS10 | Canonical HTTP, HTML, rendu, sitemap ou liens désignent des URL incompatibles | Draft.11 : lecteur structuré canonical/liens et laboratoire attribué ; exécutions livrées séparément, limites source et revue de contenu à éprouver |

TS01 reste la base existante, sans être compté comme l'un de ces quatre objectifs.
Le [parcours préalable TS02](redirect-plan-workflow.md) fournit la fiche pratique ;
il ne remplit pas la décision du responsable ni ne collecte à sa place.
L'ordre de dépendance recommandé est TS04, TS02, TS07, TS10. TS02 peut avancer
indépendamment pendant la définition TS04. Un lecteur robots commun doit servir
TS04 et TS07, avec les politiques RFC/robot explicitement distinguées.

Le [lecteur robots partagé](robots.md) est intégré dans draft.9 pour TS04 et TS07,
avec deux profils explicites initiaux et un profil historique fixe ; draft.13 ajoute
un troisième profil explicite, sans modifier les précédents. Le laboratoire fournit
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

L'ébauche Search Console rapproche intention, état technique daté et état Google
rapporté. Le [diagnostic d'import 1](search-console-observations.md) fournit ce
rapprochement hors ligne avec rejeu technique et champs manquants conservés ;
aucune donnée réelle du compte n'est établie par ses essais synthétiques.
Le périmètre reste : URL déclarée canonique, URL canonique sélectionnée, état et dernier
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

Draft.14: [sitemap page locations / URL de pages](sitemap-locations.md), explicit prior reader;
language/image annotations retained without assessment. Profil historique conservé ;
A03 seule ne suffit pas à établir TS10. [Migration](migration-draft.14.md).
