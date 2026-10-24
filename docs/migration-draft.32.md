# Migration draft.31 → draft.32

Metadata erratum / correctif de métadonnées (2026-10-13): the original frozen TS31
fixtures omitted `basis` on rows already marked `reference_limit`. Their original
bytes/hashes and outcomes remain unchanged. The additive
`tests/fixtures/structured-content-reference-limits-v1.json` supplies the mandatory
runtime-limit explanation in the executable corpus. Le correctif ajoute uniquement
l'explication obligatoire de la limite Node déjà déclarée, sans modifier les
verdicts attendus ni remplacer les deux fichiers figés. The first full verification
was intentionally interrupted before correction; it is not a successful run.

## Français

Édition locale candidate du 13 octobre 2026. TS31 reçoit trois règles semiAuto :
périmètre préalable, lecture JSON-LD native et revues par entité liées au contenu.
Voir le [contrat bilingue](structured-content-evidence.md). Total : 16 contrôles
outillés, 45 règles atomiques ; TS32 et TS33 restent distincts et non implémentés.
Interpréteur 31, adaptateur 32, présentation HTML 15, rejeu 3.

Les 44 identifiants et le sens des 42 règles antérieures restent conservés. Leur
référence de paquet normative suit draft.32 ; leurs anciens rapports, tags et
archives gardent leurs versions et empreintes exactes. Ne pas remplacer le kit
TS08 draft.31 fourni à l'application. Aucune mise à jour automatique du moteur
épinglé de TSEP App n'est effectuée.

Pour TS31, créer un **nouveau dossier** : plan préalable, captures HTTP et DOM,
contextes JSON-LD locaux, références datées et contenu visible fourni, puis revues
humaines liées aux graphes. Les exemples historiques JSON-LD restent des observations
facultatives sans verdict TS31 ; ne pas leur ajouter rétroactivement de plan ou de
jugement. Node 24 doit être explicitement fourni pour ce profil. Aucun runtime,
contexte, rendu ou jugement manquant ne se transforme en succès ou NA.

49 cas /147 couples ont été rédigés et figés avant le nouveau lecteur ; 10 cas /30 couples de limites supplémentaires ont été figés avant leur vérification. Ils sont
synthétiques, ne prouvent aucun usage réel sur Edikka. Les résultats de vérification
sont enregistrés séparément après exécution, jamais déduits d'une CI préparée.

## English

Local candidate dated 13 October 2026. TS31 gains three semiAuto rules: prior scope,
native JSON-LD reading and entity-bound supplied content review. See the
[bilingual contract](structured-content-evidence.md). Total: 16 tooled controls,
45 atomic rules; TS32 and TS33 remain separate and unimplemented. Interpreter 31,
adapter 32, HTML presentation 15, replay 3.

All 44 IDs and the previous 42 rules' semantics remain. Their normative package
reference follows draft.32, while previous reports, tags and archives retain exact
versions/fingerprints. Keep the supplied TS08 draft.31 application kit unchanged.
This work does not automatically update TSEP App's pinned engine.

Create a **new dossier** for TS31: prior plan, HTTP/DOM captures, offline JSON-LD
contexts, dated guidance and supplied visible content, followed by graph-bound
human reviews. Historical optional JSON-LD observations do not acquire a TS31
verdict or retrofitted intent/reviews. Explicit Node 24 is required for this profile.
Missing runtime, context, rendering or judgments remain unknown, never pass or NA.

49 cases /147 pairs were authored and frozen before the new reader; 10 additional boundary cases /30 pairs were frozen before their validation. They are
synthetic and do not establish actual Edikka use. Verification results are recorded
separately after execution; prepared CI is not an observed success.
