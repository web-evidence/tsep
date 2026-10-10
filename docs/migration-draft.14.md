# Migration draft.14 — sitemap locations / URL de pages

## Français

L’interpréteur passe à 14, l’adaptateur à 15 et le nouveau lecteur sitemap est 1.
Le format de rapport 2, les 44 identités TS01–TS44, leur provenance et les treize
règles atomiques sont conservés. L’extension normative concerne TS10-A03 seulement.

Pour une nouvelle campagne, déclarer `intent.canonical.sitemaps.reader` égal à
`sitemap-locations-v1` avant toute capture, avec les racines, la famille préférée,
les exceptions, l’exigence d’inclusion et les bornes du parcours. Le lecteur
distingue les loc de pages des annotations connues sans évaluer leurs valeurs.
Les détails et cas refusés sont dans [la méthode bilingue](sitemap-locations.md).

Ne pas remplacer un ancien rapport, outil, plan ou tag. Conserver l’archive et son
empreinte. Un plan sans lecteur reste historique ; une valeur explicite inconnue
ne se replie jamais. Changer l’outil modifie les empreintes de sources : préparer
un nouveau plan/capture. Une relecture de données anciennes est possible, mais
doit être nommée rétrospective, sans prétendre que ce choix était préalable.

Une réussite A03 est limitée à la concordance des entrées de la population avec
la préférence déclarée. Elle ne prouve ni TS10 entier, ni un choix Google, ni
l’exhaustivité du site. Une erreur de collecte/plan antérieur reste documentée,
sans réparation rétroactive des intentions. Rendu et revues manquants restent
inconnus. Les 427 cas historiques conservent exactement entrées et sorties.

## English

Interpreter 14, adapter 15 and new sitemap reader 1 retain report format 2, all
44 control identities/provenance and thirteen atomic rules. Only TS10-A03 gains
this normative reader extension; [the bilingual method](sitemap-locations.md)
specifies its scope, assumptions, limits and contradictory synthetic cases.

Before new captures, declare reader sitemap-locations-v1 alongside roots, preferred
family, exceptions, inclusion intent and traversal bounds. Separate page loc from
known unassessed annotations. Keep previous reports, tools, plans, archives,
fingerprints and tags. An absent field stays historical, unknown explicit values
never fall back. Changed tool sources require a new plan/capture. Reinterpretation
of old data must be labeled retrospective, never a prior-profile assessment.

A03 success only establishes agreement with declared preference in the examined
population, not whole TS10, Google selection or site-wide completeness. Retain
earlier preparation errors, absent rendering and missing human judgments. All 427
historical cases retain exact inputs and computed outputs.
