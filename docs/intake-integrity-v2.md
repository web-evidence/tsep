# TS12, TS31, TS36 — intake 2 / import 2

## Français

Les CLI `comparison_intake`, `structured_intake` et `monitoring_intake` passent
de la version 1 à la version 2. Le protocole draft.33 et ses règles ne changent
pas. Cette correction porte sur la cohérence du dossier d'import fourni ; elle
ne modifie pas la signification normative de C, NC ou NT.

La version 1 comparait la liaison de la revue au pointeur global du manifeste
sans comparer ce pointeur aux octets d'entrée. TS12 et TS36 permettaient aussi
d'omettre `input.json` de l'inventaire. Des dossiers fictifs ont conservé C
malgré ces contradictions internes. TS31 imposait déjà cette entrée à l'inventaire,
mais acceptait le pointeur global faux. Les observations et le premier essai TS31
avec une horloge de test inadéquate sont conservés dans les preuves de livraison.

Le lecteur commun `adapters/intake_integrity.py` exige les fichiers attendus,
leur inventaire exact, des chemins ASCII canoniques et des SHA-256 hexadécimaux
minuscules de 64 caractères. Aucun lien symbolique, fichier non inventorié,
alias de chemin ou original manquant n'est accepté. Les bornes sont 68 fichiers
déclarés, 100 entrées parcourues, 8 Mio par fichier et 128 Mio au total ; TS12
accepte au plus 16 inspections. Les bornes normatives restent distinctes.

Le même tampon fournit les octets hachés puis analysés. `input_sha256` désigne
les octets bruts d'`input.json`, pas une nouvelle sérialisation. Inventaire,
pointeur global, demande vide et revue fournie doivent s'y rapporter. Les
projections sont comparées au plan et aux observations conservés : corps natifs
et documents TS12, cible et éventuelle revue préalable TS31, plan et échéances
TS36. Une incohérence refuse la construction avant toute sortie (CLI 1), sans
rapport NC/NT de substitution.

Les demandes vierges sont contrôlées séparément des revues effectivement fournies.
TS36 conserve sa clôture distincte liée aux revues d'étapes ; ses dates et
qualifications existantes restent celles du contrat. Une revue sémantiquement
périmée dans un dossier cohérent peut toujours conduire à NT. TS31 vérifie aussi
la préparation des surfaces ; si la disponibilité du traitement change, préparer
explicitement un nouveau dossier au lieu de remplacer la demande conservée.

### Migration

Conserver chaque dossier v1 avec ses outils exacts. Les nouveaux outils refusent
les formats v1, y compris les revues/clôtures et demandes préalables TS31. Ne pas
modifier seulement le champ `version` d'un ancien fichier. Préparer un dossier
neuf depuis les originaux, puis fournir les avis réellement disponibles et liés
aux bonnes pièces. Aucun auteur, avis préalable, date ou clôture n'est inventé,
antidaté ou renouvelé automatiquement. Une liaison différente nécessite une
nouvelle revue effectivement fournie.

`build` effectue une nouvelle évaluation datée : sa fraîcheur peut donc différer.
Le rejeu historique garde son entrée, sa date d'observation et son moteur exact.
Aucune acquisition ni échéance future n'est rafraîchie par cette migration.
Les copies applicatives ne changent que par import explicitement décidé.

Les empreintes contrôlent la cohérence interne, pas l'identité d'un auteur,
l'authenticité de Google ou une chronologie externe. Un ensemble entièrement
réécrit avec des empreintes cohérentes n'est pas authentifié par ce mécanisme.
Les résultats observés de vérification sont consignés dans la livraison ;
cette description n'affirme pas qu'une CI distante ou un audit réel a eu lieu.

## English

`comparison_intake`, `structured_intake` and `monitoring_intake` become tool
version 2. Protocol draft.33 and normative outcome rules remain unchanged.
Version 1 compared supplied review pointers with the manifest pointer without
binding that pointer to actual input bytes. TS12/TS36 also allowed `input.json`
to be omitted from their inventory. Synthetic contradictory intakes could still
produce C. TS31 required that inventory entry but accepted the false global
pointer. Retained delivery evidence includes the initial TS31 harness clock
mistake; it is not counted as a successful integrity check.

The shared reader requires complete exact inventories, canonical ASCII paths,
lowercase 64-character SHA-256 hashes and regular contained files. Symlinks,
unlisted/missing files and aliases are refused. Bounds are 68 declared files,
100 traversed entries, 8 MiB per payload and 128 MiB total; TS12 permits at most
16 inspections. Normative bounds remain separately applicable.

Each payload is read once, hashed and parsed from the same buffer. The global
pointer refers to raw `input.json` bytes, not reserialized JSON. Inventory,
manifest, blank request and supplied review must bind those bytes. Prepared
content must match retained original plans, native bodies/documents, target and
optional prior review, or monitoring evidence as applicable. Inconsistency
refuses construction before output (CLI 1), without substituting an NC/NT report.

Blank requests remain separate from genuinely supplied reviews. TS36 keeps its
stage-bound separate closure and existing chronology semantics; stale semantic
reviews may still produce NT. TS31 checks prepared surfaces too: if processing
availability changes, explicitly prepare a new intake rather than replacing its
retained blank request.

Keep v1 dossiers and exact tools. Version 2 refuses v1 intakes and supplied
review/closure formats, including TS31 prior-plan requests. Never migrate by
editing a version marker. Prepare a new directory from retained originals, then
supply only actual reviews with matching scope and bindings. A different binding
requires an actually supplied new review; never invent/backdate an author, prior
opinion, stage or closure.

Build is a new dated assessment and may change freshness. Historical replay uses
the retained input, observation anchor and exact engine. No acquisition or future
checkpoint is refreshed. Application imports remain explicit and separate.
These self-declared hashes check internal consistency, not author/Google identity
or external chronology. A fully coherent rewrite is not authenticated. Actual
verification results belong in delivery evidence, with no remote-CI or real-audit
claim inferred from these expected-behavior instructions.
