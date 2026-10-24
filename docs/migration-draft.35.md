# Migration draft.34 → draft.35

FR : TS15 reçoit trois règles sur les fichiers natifs fournis et leur jeu déclaré.
19 contrôles outillés /54 règles,44 identifiants conservés. Le texte descriptif TS15
est précisé pour distinguer population fournie, structure minimale et validité complète.
La grille1.1 historique dans upstream reste intacte ; cette divergence éditoriale est
explicite. Le site public draft.28 garde sa copie jusqu’à une publication distinctement
autorisée. [Contrat FR/EN](sitemap-files-evidence.md).

EN: TS15 adds three rules for supplied native files and their declared set.19 tooled
controls /54 rules; all44 IDs retained. TS15's description is narrowed to distinguish
supplied population/minimal structure from complete validity. Historical upstream1.1
is unchanged; this editorial divergence is explicit. The public draft.28 site retains
its own copy until a separately authorized publication.

FR : nouveaux dossiers uniquement, plan préalable et originaux base64/SHA-256 exigés.
Un ancien résultat TS10, une URL, un compteur ou fichier transformé ne devient pas une
preuve TS15 native. Pas de conversion automatique des verdicts, pas de NA inventé.
Conserver les moteurs exacts des anciens dossiers et leurs archives. L’import d’un
moteur dans l’app exige une livraison vérifiée distincte et une recette export/rejeu.
Les imports TS02/TS08 et le gel de démonstration ne changent pas.

EN: New dossiers require a prior plan and original base64/SHA-256 files. Earlier TS10
results, URLs, counters or transformed files are not native TS15 evidence. No automatic
verdict conversion or invented NA. Preserve exact historical engines and archives.
An app engine import requires a separate verified delivery and export/replay acceptance.
Historical TS02/TS08 imports and the frozen demo remain unchanged.

Interpreter34 /adapter35 /HTML19 /replay3. TS15 needs no Node; existing controls retain
their runtime requirements. Input file5MiB/whole JSON8MiB transport limits differ from
52,428,800-byte decompressed protocol limit. Later larger-file intake requires a distinct
version and acceptance. No0.2 version, tag, publication, deployment or certification.

### Closed outcome domain / Issues fermées — TS15-A03

FR : la règle TS15-A03 déclare dans spec/protocol.json
`allowed_outcomes: ["pass", "inconclusive"]`. Aucun fail ni not-applicable n'est
admis pour cette règle, y compris dans un rapport fourni. Le banc exige au moins
un cas pour chacune de ces deux issues. Toutes les autres règles gardent leurs
issues historiques et l'exigence pass/fail/inconclusive du banc. Supprimer une
classe du corpus ne réduit jamais cette exigence. Le profil ne contient aucune
affirmation déclarative de lien parent/enfant : un fichier déclaré orphelin donne
inconclusive. Une future assertion de parent contradictoire exigerait une autre
version ; elle ne doit pas être déduite de la déclaration de population.

EN: TS15-A03 declares `allowed_outcomes: ["pass", "inconclusive"]` in the canonical
protocol. Neither fail nor not-applicable is accepted for that rule, including
in supplied reports. The corpus must contain each of its two declared outcomes.
Every other rule retains its historical domain and required pass/fail/inconclusive
coverage. Removing a class from the corpus never weakens this requirement.
The profile has no declared parent/child assertion: an orphan declared file stays
inconclusive. A future contradicted parent assertion would require another version;
it must not be inferred from the population declaration.


FR : une mesure de dépassement sans racine Sitemaps0.9 attribuée reste descriptive
et inconclusive. Les défauts d’encodage demandent une attribution secondaire de
racine bornée à65 536 octets, sans accepter UTF-16 ni réécrire les originaux. Les
cas RSS/binaire/DTD restent hors profil ; aucune archive historique n’est recalculée.
EN: excess bytes without an attributed Sitemaps0.9 root remain descriptive and
inconclusive. Encoding failures require bounded65,536-byte secondary root attribution,
without accepting UTF-16 or rewriting originals. RSS/binary/DTD remain outside the
profile; historical archives are never silently recalculated.
