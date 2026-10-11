# Migration to draft.25 / Migration vers draft.25

## Français

Draft.25 ajoute TS41-A01/A02/A03 sous le profil préalable explicite
`intent.release.reader = release-invariants-v1` : plan, couverture des exécutions,
exercice négatif et réaction aux échecs/inconnues. Interpréteur 25, adaptateur 26,
HTML 9 ; rejeu 3 inchangé. Les 1 051 anciens cas et leurs attentes sont conservés.
52 nouveaux cas synthétiques ajoutent 156 couples : **1 103 cas, 2 098 couples,
30 règles dans 11 contrôles**. Les IDs et titres TS01–TS44 restent inchangés.

Conserver les anciens dossiers avec leurs outils, protocole et empreintes.
Une nouvelle évaluation TS41 exige un plan établi avant les tentatives, une
population explicite, une matrice d’invariants, une politique et un exercice
négatif. Joindre les reçus natifs, le journal et les revues liées ; aucun plan
ni avis humain ne peut être ajouté rétroactivement comme s’il avait préexisté.
Les exports CI propriétaires demandent un adaptateur distinct. Les commandes
présentes dans les preuves ne sont jamais exécutées par ce lecteur.

Les phases pre/post examinent le même artefact candidat autour de son application.
L’artefact précédent est un contexte déclaré, sans mesure de sa version déduite.
Une comparaison ne prouve pas la causalité d’une régression. Un défaut correctement
bloqué peut accompagner TS41 C ; le défaut et les inconnues SEO restent visibles
dans le rapport. C ne signifie pas « site sain » ni « CI distante authentifiée ».

Les 43 premiers cas ont été figés avant le lecteur ; neuf cas de bord avant leurs
corrections. Leurs dates sont fictives. Les tests d’import utilisent une horloge
fictive explicite postérieure aux captures, sans modifier les fichiers figés ni
faire passer ces dates pour des observations réelles. Le laboratoire de processus
réel TS41 et l’application à Edikka restent à produire. TS39, TS36 et TS31–33
sont autorisés pour la suite, sans être ajoutés à la couverture de cette version.

## English

Draft.25 adds TS41-A01/A02/A03 under explicit prior release-invariants-v1:
plan, execution coverage, negative rehearsal and failure/unknown response.
Interpreter 25, adapter 26, HTML 9; replay 3 unchanged. Preserve all 1,051 prior
cases/expectations. Fifty-two new authored cases add 156 pairs: **1,103 cases,
2,098 pairs, 30 rules across 11 controls**. All TS01–TS44 IDs/titles stay unchanged.

Keep historical bundles with exact tools/protocol/hashes. New TS41 assessments
declare the attempt population, invariant matrix, policy and negative rehearsal
before execution, then retain native receipts, journal and bound reviews. Never
retrofit a prior plan or invent human approval. Provider-specific CI formats need
separate adapters; supplied command strings are never executed by this reader.

Pre/post phases assess the candidate artifact around application. The previous
artifact is supplied context, not an inferred old-version measurement. Comparison
does not establish causality. Correctly blocking an SEO defect can accompany
TS41 C; underlying defects/unknowns stay visible. C does not establish whole-site
health or authenticated remote CI.

Forty-three cases were frozen before the reader; nine boundary cases before fixes.
Their dates are fictional; importer tests explicitly use a fictional later clock,
without rewriting the frozen files or claiming actual observations. An actual
local TS41 process laboratory and Edikka application remain pending. The authorized
TS39, TS36 and TS31–33 work is outside this version’s executable coverage.
