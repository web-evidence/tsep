# Migration draft.28 → draft.29

## Français

Candidate locale : TS08 ajoute trois règles semiAuto sous le profil explicite
[google-inspection-evidence-v1](inspection-evidence.md). Total : 13 contrôles
outillés, 36 règles, toujours 44 identifiants et leur provenance. Interpréteur 28,
adaptateur 29, HTML 12, intake inspection 1 ; diagnostic Search Console 1 et rejeu3
inchangés. TS12 reste à intégrer. Les 1 257 cas historiques conservent leurs objets
et leur ordre ; aucune règle antérieure n’est modifiée sémantiquement.

Les rapports et paquets draft.28 restent attachés à leurs versions et outils
exacts. Ne pas les réétiqueter ni reconstruire leurs intentions. Une nouvelle
évaluation TS08 exige le plan, les réponses natives et les revues réellement
fournies. Un JSON historique peut être importé séparément ; il ne devient pas une
acquisition prospective. Absence d’accès/revue = inconclusive, pas NA ou C. Les
réponses défavorables correctement documentées peuvent passer ; Google PASS seul
ne suffit pas. Les limites source/rendu et le blocage navigateur antérieur restent
ouverts et distincts. Aucune application réelle Edikka ou CI distante nouvelle.

Les 47 cas initiaux ont été figés avant le lecteur. Le premier passage a relevé
une erreur dans le cas « unknown-url-no-fields » : sa revue conservait PASS alors
que la réponse avait NEUTRAL. Le fail observé était correct. La fixture V1 reste
intacte ; V2 corrige seulement claimed_verdict et la relation indéterminée à
l’objectif, sans changer les attentes. Les tests conservent cet échec historique.

## English

Local candidate: TS08 adds three semiAuto rules under explicit
[google-inspection-evidence-v1](inspection-evidence.md). There are13 tooled controls,
36 rules and unchanged44 identifiers/provenance. Interpreter28, adapter29, HTML12,
inspection intake1; Search Console diagnostic1 and replay3 unchanged. TS12 remains
pending. All1,257 historical case objects and their order remain unchanged;
no older rule changes meaning.

Keep draft28 reports/bundles with their exact tools and versions. No relabelling
or reconstructed past intent. New TS08 assessments require plans, native responses
and genuinely supplied reviews. Historical API JSON is a separate historical
input, never prospective acquisition. Missing access/review remains inconclusive,
not NA or C. Correctly documented negative Google states may pass; Google PASS
alone cannot. Existing source/rendering limitations and the historical browser
block remain open and distinct. No real Edikka assessment or new remote CI inferred.

The47 original cases were frozen before the reader. The first run correctly found
a contradiction in unknown-url-no-fields: its review still claimed PASS against
native NEUTRAL. V1 stays intact. V2 changes only claimed_verdict and the undetermined
objective relation, retaining all expectations. Tests preserve that adverse history.
