# Migration to draft.24 / Migration vers draft.24

## Français

Draft.24 ajoute trois règles TS44 et le profil explicite
`intent.critical_content.reader = critical-content-nojs-v1`.
Interpréteur 24, adaptateur 25 et HTML 8 ; rejeu 3 inchangé.
Les 980 cas antérieurs, leurs 24 règles et tous les IDs/titres TS01–TS44 restent
conservés. Les 71 nouveaux cas synthétiques ajoutent 213 couples, soit 1 051 cas
et 1 942 couples pour 27 règles dans dix contrôles. Cela ne signifie pas que les
44 contrôles sont outillés ou qu'Edikka est conforme.

Conserver tout ancien dossier avec son protocole, ses outils et ses empreintes.
Ne pas modifier son intention ou sa revue pour le convertir en résultat draft.24.
Pour une nouvelle évaluation TS44, fixer inventaire critique, client sans JS,
représentation de livraison, ressources et états rendus **avant** capture ; obtenir
une revue de périmètre puis joindre les pièces et revues liées. Les fichiers anciens
peuvent être explorés rétrospectivement, mais pas dotés d'un plan antidaté.

Node 24 reste facultatif ; son absence réduit explicitement la couverture. JSON et
HTML sont des formats qualifiés bornés, sans fallback Markdown. Un rendu rédigé
reste synthétique et doit le dire. Aucune nouvelle capture navigateur ou mesure
Edikka n'est créée par cette migration. Les lacunes TS01/TS02/TS04/TS07/TS10,
Search Console et l'intégration CMS restent séparées.

## English

Draft.24 adds three TS44 rules and explicit prior critical-content-nojs-v1.
Interpreter 24, adapter 25, HTML 8; replay 3 unchanged. Preserve the previous
980 cases/24 rules and all 44 IDs/titles. Seventy-one new authored cases add 213
pairs: 1,051 cases/1,942 pairs, 27 rules across ten controls. This is not completion
of all controls or Edikka conformity.

Keep old bundles with exact tools/protocol/hashes; never retrofit plans or reviews.
A new TS44 assessment declares critical inventory, no-JS client, delivery path,
resources and required states before capture, with supplied bound reviews. Old
records can support retrospective exploration, never an invented prior plan.
Optional Node limits remain explicit. Only bounded qualified HTML/JSON formats;
no Markdown fallback. Authored DOM remains synthetic. No browser/site observation
or earlier method gap is resolved merely by this migration.
