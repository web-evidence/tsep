# Migration 0.1.0-draft.7 → 0.1.0-draft.8

## Français

Cette candidate ajoute TS02-A01/A02 et précise le périmètre serveur HTTP de sa
méthode exécutable. Les identifiants TS01–TS44, sévérités et profils sont conservés.
Le format de rapport reste 2 ; la version normative et son empreinte changent.
Les neuf règles TS01/TS07/TS10 conservent leurs attendus ; leur identité de version
est explicitement actualisée avec le protocole. Les 216 cas antérieurs sont
conservés, avec 38 nouveaux cas TS02. Les sorties TS07/TS10 des cas historiques
gardent leur empreinte de régression antérieure.

Un rapport draft.7 n'est pas un rapport draft.8 : ne pas modifier simplement sa
version ou ses empreintes. Conserver rapport, captures et outils antérieurs.
Pour une nouvelle évaluation, réimporter les captures originales avec les nouveaux
outils dans un autre dossier. Le rejeu historique exige l'archive historique.

TS02 exige désormais le plan antérieur, la revue fournie du responsable et la
matrice des deux règles pour toutes les sources déclarées. Une ancienne mention C
sans ces pièces ne se convertit pas en C. Une revue absente reste indéterminée ;
aucune date ni approbation ne doit être fabriquée rétroactivement. Une capture
ancienne sans plan préalable peut servir d'observation exploratoire, pas de
validation rétroactive de l'intention.

Interpréteur 7, adaptateur de captures 8 ; source TS02 ajoutée à la provenance.
Les demandes de revue TS07/TS10 préparées avec d'autres sources doivent rester
avec leurs anciens outils ou être préparées à nouveau explicitement. Aucun tag,
archive diffusée ou DOI antérieur n'est remplacé. Aucun DOI propre à cette nouvelle
candidate n'est revendiqué. Cette version ne finalise pas les quatre contrôles
prioritaires ni ne vaut validation d'Edikka.

## English

This candidate adds TS02-A01/A02 with an explicit server-side HTTP scope. Permanent
control IDs, severities, profiles and report format 2 are unchanged. Protocol
version and fingerprint change; the prior nine rules retain their semantics under
the new version identity. The 216 previous raw cases remain, plus 38 TS02 cases.

Do not relabel old reports or rehash them as migration. Preserve old reports,
captures and tool archives; historical replay needs historical tools. A new
assessment imports original evidence into a new directory. TS02 C now requires
the prior plan, supplied owner approval and complete two-rule/target coverage.
Missing prior approval remains inconclusive; do not backdate or fabricate it.

Interpreter 7 and capture adapter 8 add the TS02 source to runtime provenance.
Old TS07/TS10 review requests remain with their pinned tools or are explicitly
prepared anew. No old tag, archive or DOI is replaced; no new version DOI is
claimed. This candidate alone does not complete the four-control program or an
Edikka assessment. See [format and bounds](redirects.md).
