# Migration to draft.26 / Migration vers draft.26

## Français

Draft.26 corrige une divergence de rédaction FR/EN de TS41. Le texte français de
draft.25 laissait entendre qu’une sortie positive et un recalcul inconclusif
pouvaient, à eux seuls, établir une sortie falsifiée. Le texte anglais et le
lecteur conservaient déjà ce cas inconclusif : une limite du runtime ou de la
méthode ne suffit pas à accuser un ancien résultat conclusif. En revanche, des
sorties inconnues **inchangées** accompagnées d’un code processus 0 contredisent
bien la politique stricte. Dans les deux cas, le dispositif ne devient pas C.

La distinction est maintenant explicite dans les deux langues, avec un cas
supplémentaire figé avant la correction. Les 1 103 cas antérieurs, leurs attentes
et le code des lecteurs restent inchangés : **1 104 cas / 2 101 couples**, toujours
30 règles dans 11 contrôles. Interpréteur 25, adaptateur 26, HTML 9, rejeu 3.
Le [laboratoire TS41](release-laboratory.md) version 1 est un outil facultatif
distinct ; ses six scénarios ne sont pas six nouveaux contrôles.

Conserver tous les dossiers draft.25 avec leur archive et leurs empreintes.
Utiliser draft.26 pour une nouvelle évaluation ; une réévaluation explicite peut
relire les captures anciennes sans inventer de plan préalable ni réécrire le
rapport antérieur. Les commandes fournies dans les preuves ne sont jamais
exécutées au rejeu. Aucun résultat Edikka ni CI distante n’est établi ici.

## English

Draft.26 corrects inconsistent French TS41 wording in draft.25. French prose
implied that positive retained output versus inconclusive recalculation could
alone prove falsification. English prose and the reader already kept that case
inconclusive: runtime/method limits cannot alone accuse an earlier conclusive
result. In contrast, **unchanged unknown output** accompanied by process exit 0
does contradict the strict policy. Neither situation can establish process C.

Both languages now state the distinction explicitly, with one additional case
frozen before the correction. The previous 1,103 cases/expectations and reader
code stay unchanged: **1,104 cases / 2,101 pairs**, 30 rules across 11 controls.
Interpreter 25, adapter 26, HTML 9, replay 3. The separate optional
[TS41 laboratory](release-laboratory.md) version 1 adds six scenarios, not controls.

Keep historical draft.25 bundles and exact tools/hashes. Use draft.26 for new
assessments; explicitly reassess old captures without inventing prior intent or
rewriting the old report. Offline replay never executes commands supplied in
evidence. No Edikka assessment or remote CI is established by this migration.
