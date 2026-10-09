# Offline captures → evidence bundle / Captures locales → paquet de preuves

## Français

`adapters/captures.py` version 1 transforme un fichier de captures fourni en un
rapport TSEP draft.7, ses preuves, sa décision et son export EARL. Il appelle
l’interpréteur de référence existant et calcule les résultats depuis les entrées
brutes. Il ne lit pas les verdicts attendus du corpus. Ce composant interne ne
constitue pas une implémentation indépendante. Son format de paquet reste en
version 1 ; l’évaluation suit la [migration normative draft.7](migration-draft.7.md).

### Premier paquet

Depuis la racine du dépôt, avec Python 3.9+ et un dossier de destination **nouveau** :

```sh
python3 adapters/captures.py examples/captures/ts01-markers.json \
  --output-dir /tmp/tsep-capture-ts01 --assessor 'Synthetic demo author' \
  --label 'One synthetic URL' --selection-method 'Supplied synthetic fixture only' \
  --access synthetic --mode automatic --lang fr
python3 tsep.py validate /tmp/tsep-capture-ts01/report.json
python3 tsep.py gate /tmp/tsep-capture-ts01/report.json --summary --lang fr
```

Résultat : TS01 C, `GO_WITH_RESERVATIONS`, **1 contrôle sur 44 et une cible
synthétique**. L’intention et les marqueurs précèdent la capture fictive. Ce C
est limité à cette cible et aux deux règles de TS01.

Un second exemple démontre volontairement une couverture insuffisante :

```sh
python3 adapters/captures.py examples/captures/ts07-source-only.json \
  --output-dir /tmp/tsep-capture-ts07 --assessor 'Synthetic demo author' \
  --label 'Source captures only' --selection-method 'Supplied synthetic fixture only' \
  --access synthetic --mode semiAuto --lang fr
python3 tsep.py gate /tmp/tsep-capture-ts07/report.json --summary --lang fr
```

TS07-A01/A02 passent, mais A03 est omise : **TS07 NT, NO_GO**, et `gate` retourne 1.
L’adaptateur retourne 0 lorsque la conversion est valide, y compris pour NO_GO ;
utiliser `tsep.py gate` pour le code de décision. Une conversion invalide retourne
64, une syntaxe CLI invalide 2. `--json` affiche le résumé structuré au lieu du
résumé lisible ; `--lang en` sélectionne l’anglais.

`examples/captures/ts10-family.json` couvre les quatre règles TS10 ; employer
`--mode manual`. Sa revue humaine et ses captures sont **synthétiques**, déjà
fournies. La sortie est C sur TS10 seulement. Les trois entrées sont des dérivés
contrôlés du corpus, régénérés par `examples/replay.py` et vérifiés sans modifier
les sources par `scripts/verify.py`.

### Entrée et périmètre

L’objet JSON contient exactement `input_version: "1"`, `rules` et `targets`, selon
le [format d’entrée](conformance.md), le [plan source/DOM](rendered-states.md) et
les [familles canoniques](canonical-families.md). Choisir explicitement les règles
parmi TS01-A01/A02, TS07-A01/A02/A03 et TS10-A01 à A04. Fournir les échanges HTTP
complets par saut, HTML et robots.txt bruts, intention préalable, contexte et les
revues/captures supplémentaires requises. Les CRLF et champs répétés restent
dans les chaînes d’origine. Un objet de cas avec `expected` est refusé.

L’outil accepte un fichier UTF-8 d’au plus 8 Mio et 1 à 100 cibles HTTP(S)
distinctes ; aucune lecture d’une URL ou d’un chemin contenu dans le JSON. Les
clés dupliquées, valeurs JSON non finies, URLs invalides et règles inconnues sont
refusées. Les entrées structurellement mal formées peuvent être refusées ; une
preuve incomplète ou hors du sous-ensemble interprété reste inconclusive.

Le rapport est `custom` et sélectionne par défaut les parents des règles
demandées. `--controls TS01,TS07` peut ajouter des contrôles, qui restent NT et
not-started si aucune règle n’est demandée. Aucun parent demandé ne peut être
omis. `--exclude` est répétable. `--assessor`, `--label`, `--selection-method` et
`--access public|restricted|synthetic` sont obligatoires ; l’outil ne devine ni
l’échantillonnage ni la confidentialité et ne masque pas les données fournies.

`--mode` vaut manual par défaut. Un C automatic exige toutes les règles du contrôle
automatic, leur couverture complète et l’outil nommé/versionné. TS01 le permet ;
TS07 exige au moins semiAuto et TS10 manual. Les revues fournies ne sont ni
fabriquées ni authentifiées par l’adaptateur. Un mode incompatible avec un C
calculé est refusé avant livraison, sans changement silencieux du verdict.

### Fichiers produits et dates

| Fichier | Contenu |
| --- | --- |
| `input.json` | Octets d’origine exacts, conservés comme preuve |
| `import.json` | Version de l’outil/protocole, empreintes du code et de l’entrée, date d’import, accès et règles demandées/omises par contrôle |
| `assessment.json` | Résultats calculés par règle/cible, avant rattachement des preuves |
| `evidence/target-N-KIND.json` | Champs fournis, séparés par cible et type, avec base de datation explicite |
| `report.json` | Rapport format 2 validé, preuves relatives et SHA-256 |
| `gate.json` | Décision, causes bloquantes NC/NT et couverture déclarée |
| `earl.jsonld` | Assertions du contrôle et de chaque résultat atomique |
| `SHA256SUMS` | Empreinte de chaque fichier livré, sauf le manifeste lui-même |

Les types dérivés correspondent aux champs effectivement fournis : intention et
revues, HTTP, source HTML, robots, rendu, sitemaps et crawl. Pour une ressource
non HTML, la preuve `html` conserve les réponses et leur type média explicite,
conformément au contrat ; elle n’invente pas de document HTML. Aucun DOM absent,
aucune revue ou preuve d’absence n’est créé. Les preuves communes sont rattachées
à toutes les cibles ; les extraits d’une cible ne servent pas de preuve à une autre.

Chaque extrait conserve les dates originales. Sa date d’artefact est la plus
récente des dates fournies, avec la date de cible pour les champs non datés ;
`date_basis` précise cette convention d’agrégation. Si une date manque ou est
invalide, l’artefact est daté **à l’import seulement**, explicitement, sans réparer
la capture. Le calcul garde ses inconnues. Toute date fournie valide située dans
le futur est refusée. La date d’import des fichiers d’origine et de calcul ne
prouve pas une date de collecte ; aucune date déclarée n’est authentifiée.

Le paquet est validé dans un dossier temporaire avant création de la destination.
Un dossier, fichier ou lien existant n’est jamais remplacé. Le parent doit déjà
exister. Une erreur de copie retire le nouveau dossier partiellement écrit.
Déplacer le paquet complet conserve ses chemins de preuve relatifs. La date
d’import fait varier les octets de deux imports ; seuls les résultats calculés
sur une entrée et une version identiques sont reproductibles.

### Limites et validation

Une règle en échec conserve NC même si d’autres manquent. C nécessite toutes les
règles et toutes les cibles requises, au moins un pass, aucune inconnue ni aucun
fail ; des exemptions seules ne justifient pas NA au niveau du contrôle. Les
règles non demandées restent omises et visibles dans `import.json`, sans fausse
assertion d’exécution. La politique de décision reste inchangée en draft.7.

Les limites de l’interpréteur restent celles de la [conformance](conformance.md) :
pas de collecte, exécution JavaScript, observation moteur ou conformité globale.
Les attendus normatifs du corpus ne sont jamais substitués aux résultats
calculés. La recette convertit toutes les entrées brutes du corpus et vérifie intégrité,
portabilité, limites de modes, inconnues, échecs, non-écrasement et erreurs de copie.
Ce contrôle du parcours ne constitue pas une seconde interprétation normative.

## English

`adapters/captures.py` version 1 converts supplied offline captures into a TSEP
draft.7 report, evidence, decision and EARL export. It uses the existing bounded
reference interpreter and computes outcomes from raw input, without reading
conformance expectations. This internal component is neither an independent
implementation. Its bundle format remains version 1; assessment follows the
[draft.7 normative migration](migration-draft.7.md).

### First bundle

Run the commands above from the repository root with Python 3.9+, choosing a
**new** output directory and `--lang en` for the English summary. The TS01 sample
produces C and `GO_WITH_RESERVATIONS` on **1 control out of 44, one synthetic
target**. Prior intent and markers are supplied. The TS07 source-only sample has
passing A01/A02 but omits A03: **NT, NO_GO**. `tsep.py gate` deliberately exits 1.

Successful conversion exits 0 even for NO_GO; run `tsep.py gate` for the decision
exit code. Invalid conversion exits 64; malformed CLI syntax exits 2. `--json`
selects the structured summary. `examples/captures/ts10-family.json` covers all
four TS10 rules using `--mode manual`, with supplied **synthetic** human review
and captures, yielding C for TS10 only. The three raw examples are controlled
corpus derivatives, regenerated by `examples/replay.py` and checked without
source changes by `scripts/verify.py`.

### Input and scope

The JSON object contains exactly `input_version: "1"`, `rules` and `targets` in
the [input format](conformance.md), [source/DOM plan](rendered-states.md) and
[canonical family format](canonical-families.md). Explicitly select rules from
TS01-A01/A02, TS07-A01/A02/A03 and TS10-A01 through A04. Supply complete HTTP
exchanges per hop, raw HTML/robots.txt, prior intent, context and required
additional captures/reviews. Original strings retain CRLF and repeated headers.
Case wrappers with `expected` are rejected.

The UTF-8 input file is limited to 8 MiB and 1–100 distinct HTTP(S) targets; no URL
or file path inside the input is fetched. Duplicate JSON keys, nonfinite values,
invalid URLs and unknown rules are rejected. Structurally malformed inputs may
be rejected; incomplete or unsupported evidence remains inconclusive.

The `custom` report selects requested rules' parents by default. Optional
`--controls TS01,TS07` can add controls, left NT/not-started if no rule is requested,
and cannot omit requested parents. Repeat `--exclude` as needed. `--assessor`,
`--label`, `--selection-method` and `--access public|restricted|synthetic` are
required: sampling and confidentiality are not inferred, and data is not redacted.

`--mode` defaults to manual. Automatic C requires every control rule automatic,
complete coverage and tool name/version. TS01 permits it; TS07 requires at least
semiAuto and TS10 manual. Supplied reviews are not created or authenticated by
the adapter. A mode incompatible with computed C is rejected before delivery,
without silently changing the verdict.

### Output and dates

`input.json` retains the exact original bytes. `import.json` records tool/protocol
versions, code/input hashes, import time, access and requested/omitted rules per
control. `assessment.json` contains computed rule/target results before evidence
linking. `evidence/target-N-KIND.json` retains supplied fields per target/type with
an explicit date basis. `report.json` is validated format 2 with relative paths
and SHA-256; `gate.json` records decision, NC/NT blockers and coverage;
`earl.jsonld` contains control and atomic assertions. `SHA256SUMS` covers every
delivered file except itself.

Derived types match supplied intent/reviews, HTTP, HTML source, robots, rendering,
sitemaps and crawl fields. For non-HTML, the contract's `html` evidence retains
responses with their explicit media types without inventing HTML. Missing DOM,
reviews or absence evidence are never created. Shared evidence covers all targets;
target extracts never become another target's evidence.

Original dates remain in each extract. Its artifact date is the latest supplied
date, using the target observation date for undated fields; `date_basis` states
this aggregation convention. Missing/invalid dates give an explicitly
**import-time-only** artifact date, without repairing capture data or changing
unknown outcomes. Any valid supplied future date is rejected. Original-input and
computed-result artifact dates indicate import, not collection. No declared date
is authenticated.

Validation runs in staging before creating the destination. Existing files,
directories or links are never replaced; the parent must exist. A copy failure
removes the newly created partial directory. Moving the entire bundle preserves
relative evidence paths. Import time changes bytes across imports; computed
outcomes are reproducible for identical input and code versions.

### Limits and verification

A failure preserves NC despite missing rules. C requires every required rule and
target, at least one pass, no fail or unknown. All-exempt atoms alone cannot
establish whole-control NA. Omitted rules remain visible in `import.json` without
invented execution assertions. Decision policy remains unchanged in draft.7.

The [reference limits](conformance.md) still apply: no collection, JavaScript
execution, engine observation or global conformity. Normative corpus expectations
never replace computed outcomes. Tests convert every raw corpus input and verify
integrity, portability, mode constraints, unknowns, failures, non-overwrite and
copy failures. These workflow checks are not a second normative interpretation.
