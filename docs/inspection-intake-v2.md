# TS08 intake 2 — integrity / intégrité

## Français

L'importeur CLI `adapters/inspection_intake.py` passe à la version **2**. Le
protocole draft.33, le lecteur TS08 et ses trois règles ne changent pas. Il s'agit
d'une vérification du dossier d'import, pas d'une nouvelle définition de C/NC/NT.

La version 1 vérifiait les entrées présentes dans `intake.files`, mais ne rendait
pas obligatoire celle d'`input.json`. Elle comparait également la liaison de la
revue à `intake.input_sha256` sans comparer séparément cette dernière aux octets
réels de l'entrée. Deux contradictions synthétiques ont reproduit cette lacune :
une entrée modifiée dont l'empreinte avait été retirée de l'inventaire, et une
fausse empreinte globale identique dans le manifeste et la revue. Un rapport
pouvait alors être produit malgré ces contradictions internes. Les empreintes
auto-déclarées n'ont jamais authentifié l'auteur ou Google.

La version 2 exige l'inventaire complet des fichiers produits par `prepare` :
plan, entrée, demande de revue vide et originaux numérotés. Aucun fichier
supplémentaire, lien symbolique, chemin non canonique ou empreinte autre qu'un
SHA-256 hexadécimal minuscule de 64 caractères n'est admis. Les noms ont un
vocabulaire ASCII exact ; alias de casse ou de normalisation Unicode refusés.
Les bornes sont 16 inspections, 67 fichiers déclarés, 100 entrées parcourues,
8 Mio par fichier et 128 Mio au total. Les bornes normatives du lecteur TS08
restent applicables séparément.

Chaque fichier est lu dans un tampon borné, contrôlé puis analysé depuis ce
même tampon. `input_sha256` désigne les **octets bruts** d'`input.json`, pas une
nouvelle sérialisation JSON. Inventaire, liaison globale, demande de revue vide
et revue fournie doivent désigner ces mêmes octets. Le plan et les corps natifs
doivent aussi correspondre à leurs projections dans l'entrée ; seule la date
`observed_at` de préparation diffère normalement du plan. Une incohérence est
un refus de construction avant toute sortie, avec code CLI 1 ; ce n'est ni NC
ni NT. Une entrée cohérente avec preuves insuffisantes peut toujours produire NT.

### Migration explicite

Conserver le dossier version 1 et son moteur exact. Ne pas réécrire sa version,
son manifeste, ses originaux, ses revues ou son ancien rapport. `build` version 2
refuse un import version 1. Pour une nouvelle évaluation, appeler explicitement
`prepare` version 2 avec le plan original et les observations conservées, vers
un dossier neuf. Conserver la nouvelle demande de revue vide et fournir les
revues réellement disponibles dans une copie séparée. Une revue antérieure ne
peut être réutilisée que si sa portée et sa liaison aux pièces restent exactes ;
ne pas inventer, antidater ou renouveler une décision pour obtenir un résultat.
Une liaison différente demande une nouvelle revue effectivement fournie.

La nouvelle date d'évaluation peut changer la qualification de fraîcheur ; elle
ne rafraîchit ni une acquisition ni le crawl rapporté. Le rejeu d'un ancien rapport
reste effectué avec son moteur exact et sa date d'observation conservée. Aucun
réimport ou changement de dépendance n'est automatique. Les intégrations choisissent
séparément leur archive ; ce correctif ne remplace pas leurs copies existantes.

La vérification porte sur la cohérence des pièces fournies, pas leur authenticité.
Un auteur capable de réécrire toutes les pièces et empreintes de façon cohérente
n'est pas authentifié ou détecté par un manifeste auto-déclaré. Aucun accès réel
Google, acquisition Edikka ou avis humain n'est établi par ces essais fictifs.
Les résultats observés des tests sources/archive figurent dans le bilan de
livraison, pas dans cette description des attentes.

## English

CLI `adapters/inspection_intake.py` becomes **version 2**. Protocol draft.33,
the TS08 reader and its three rules are unchanged. This verifies intake-package
integrity; it does not redefine C/NC/NT.

Version 1 checked entries that appeared in `intake.files` without requiring
`input.json`. It compared the supplied review binding to `intake.input_sha256`
without separately comparing that pointer with the actual input bytes. Two
synthetic contradictions reproduced this gap: changed input omitted from the
inventory, and an equally false global pointer in the manifest and review. A
report could be produced despite these internal contradictions. Self-declared
hashes have never authenticated the author or Google.

Version 2 requires the exact generated inventory: plan, input, blank review
request and numbered originals. Extra files, symlinks, noncanonical paths and
digests other than 64 lowercase hexadecimal SHA-256 characters are refused.
Paths use an exact ASCII vocabulary; case and Unicode-normalization aliases are
unsupported. Bounds are 16 inspections, 67 listed files, 100 traversed entries,
8 MiB per file and 128 MiB total. The separate normative TS08 bounds still apply.

Each payload is read once into a bounded buffer, hashed and parsed from that
same buffer. `input_sha256` denotes the **raw bytes** of `input.json`, not a new
JSON serialization. Inventory, global pointer, blank request and supplied review
must bind those same bytes. Original plan/native bodies must match their input
projections; only preparation `observed_at` normally differs from the plan.
Inconsistency refuses construction before any output with CLI exit 1, not an NC
or NT result. Consistent input with insufficient evidence can still produce NT.

Preserve version-1 intakes, their exact tools, native files, reviews and reports.
Version-2 build refuses version 1; never edit an old version marker to migrate it.
Explicitly prepare a new intake from the retained original plan and observations,
then supply genuinely available reviews in a separate copy of the new blank
request. Reuse a prior review only when its scope and evidence binding still match;
a different binding requires an actually supplied new review. Never invent,
backdate or renew a decision to obtain a desired outcome.

New assessment time may affect freshness qualification; it does not refresh the
acquisition or crawl. Replay historical reports with their exact tools and retained
observation time. No automatic reimport or dependency migration occurs; integrations
select their archives separately. This fix does not replace existing copies.

This checks consistency, not authenticity against an author coherently replacing
every file and hash. Synthetic tests establish no actual Google/Edikka acquisition
or human review. Observed source/archive verification belongs in the retained
delivery evidence, not in these expected-behavior instructions.
