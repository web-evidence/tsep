# Migration draft.29 → draft.30

## Français

TS12 ajoute trois règles semiAuto sous [google-canonical-comparison-v1](canonical-comparison.md).
Total local : 14 contrôles outillés, 39 règles ; toujours 44 identifiants/titres.
Interpréteur 29, adaptateur 30, HTML 13, import comparaison 1 ; rejeu 3, inspection1
et diagnostic Search Console 1 inchangés. Les 36 règles et 1 304 cas antérieurs
conservent leurs objets ; les 66 nouveaux cas/198 couples sont rédigés et figés
avant le lecteur. Le premier essai a relevé 55 sorties inconclusives inattendues :
le lecteur utilisait de mauvais noms de clés pour les hypothèses statiques. Corriger
ces noms a donné 198 accords, sans modifier les attentes ni les fixtures.

Garder les paquets draft.29 et antérieurs avec leurs outils exacts. Une nouvelle
évaluation TS12 nécessite un nouveau plan préalable explicite, les JSON natifs,
les captures HTTP/HTML, tous les états DOM structurés prévus et des revues fournies.
Ne pas reconstruire une intention passée ni réétiqueter un dossier historique.
Un plan TS08 existant n’invente pas les préférences et scénarios de rendu TS12.
Le premier profil refuse toute exemption de rendu : source seule reste partielle,
NT sauf contradiction documentaire indépendante. Canonical Google absente : NT.
Les comparaisons sont littérales, sans normalisation d’URL ni causalité déduite.
Une divergence correctement documentée peut accompagner C ; une égalité sans
revue ne suffit pas. Aucun résultat TS10 ou état live n’est déduit.

Les imports de compte restent locaux/restreints et les exercices synthetic. Aucun
essai réel Edikka, nouvelle capture navigateur, CI distante, push ou publication
n’est établi par cette migration. Le blocage navigateur historique reste ouvert.

## English

TS12 adds three semiAuto rules under [google-canonical-comparison-v1](canonical-comparison.md).
Local totals:14 tooled controls,39 rules, unchanged44 identifiers/titles. Interpreter29,
adapter30, HTML13, comparison intake1; replay3, inspection1 and Search Console
diagnostic1 unchanged. Preserve all36 older rule objects and1,304 historical cases.
The66 authored cases/198 pairs precede the reader. Its first run produced55 unexpected
inconclusive outcomes because of incorrect static-hypothesis key names. Correcting
the reader produced198 agreements without changing fixture bytes or expectations.

Keep draft29 and older bundles with exact original tools. New TS12 assessment needs
an explicit prior plan, native API JSON, HTTP/HTML, every planned structured DOM
state and supplied reviews. Do not invent past intent or relabel historical input.
An existing TS08 plan does not create TS12 preferences/render scenarios. This first
profile has no rendering exemption: source-only is partial, NT unless an independent
documentation contradiction exists. Absent Google canonical remains NT. Comparisons
are literal, without normalization or inferred causality. Documented divergence can
accompany C; agreement alone cannot. No TS10 or live state inferred.

Real account imports remain local/restricted, authored exercises synthetic. This
migration establishes no actual Edikka trial, new browser capture, remote CI, push
or publication. The historical browser restriction remains unresolved.
