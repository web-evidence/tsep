# TS13 / TS14 — supplied sitemap quality / qualité sitemap fournie

TSEP 0.3.0-draft.1. Readers `supplied-sitemap-quality-v1` and
`supplied-sitemap-lastmod-v1`, version 1. Interpreter 47, adapter 46, HTML 27;
replay 3 unchanged. This is a bounded editorial proposal, not certification.

## Français

### Périmètre et entrées communs

Ces trois nouvelles règles évaluent les fichiers et pages **fournis dans une
population déclarée**. Elles ne découvrent aucun sitemap et ne collectent aucun
site. Le plan et les originaux utilisent sans modification le [format TS15](sitemap-files-evidence.md) :
`input_version=2`, `rules`, `targets`, `sitemap_synthetic`, `context`,
`intent.declared_at`, `intent.sitemap_files` et `sitemap_files`.
Une cible est la première racine déclarée. Le plan précède la fenêtre de captures,
au plus 24 heures, qui précède `target.observed_at`. Les racines, documents,
contexte, exclusions implicites de la population et raison de sélection sont
fournis, jamais authentifiés. `context.id` est requis pour rapprocher les pages.
Toutes les entrées de pages des fichiers déclarés sont examinées ; aucune sélection
silencieuse d’URL n’est permise. Le périmètre ne s’étend pas au site entier.

Les fichiers `native={raw_base64,sha256,encoding,complete}` sont conservés octet
pour octet. Le lecteur TS15 existant qualifie UTF8, structure minimale, gzip et
relations racine/enfant avant leur lecture. Ses règles et verdicts restent séparés :
une impossibilité structurelle donne ici NT, pas un nouveau verdict TS15.
Un fichier qualifié conserve son `loc`, sa position à partir de zéro et son
`lastmod` éventuel. Les occurrences identiques restent visibles ; elles ne prouvent
pas à elles seules un doublon canonique incorrect. Les comparaisons d’URL sont
littérales, sans normalisation, équivalence ni résolution d’URL relative.

Bornes de ce profil : 16 fichiers déclarés, 128 entrées de pages au total,
2 Mio XML décompressés par fichier, 128 pages et 128 événements, 32 Kio par événement
JSON UTF8 ou revue. Les URL natives sont bornées par les feuilles à 4096 caractères.
Les limites TS15 de transport (5 Mio bruts) et de l’enveloppe JSON (8 Mio) restent
applicables. Dépassement du profil, XML incomplet, DTD, enfant absent, fichier
ambigu ou hors fenêtre : inconclusive, sans pass inventé. Une contradiction déjà
établie sur un autre fichier ou une autre page reste fail. Aucun accès réseau,
chargement de DTD/XSD ou exécution de navigateur n’a lieu.

### TS13-A01 — population native et URL absolues

Entrées requises : `sitemap`, `intent`. Méthode automatique bornée.
Rapprocher les fichiers et enfants déclarés, lire les `loc` des seuls `urlset`,
puis exiger des URL absolues HTTP(S), sans identifiants, fragment, espace,
contrôle, port invalide, antislash ni échappement pourcent mal formé.
Une contradiction native complète donne fail. Pass exige la couverture de tous
les fichiers déclarés et de toutes leurs entrées. Racines non découvertes,
malformation empêchant la lecture ou couverture partielle : inconclusive.
Aucune exemption atomique. Aucun résultat sur la canonical ou l’indexation
n’est déduit de cette règle seule.

### TS13-A02 — pages, stratégie et revue

Entrées : `sitemap`, `http`, `html`, `intent`. Méthode semi-automatique.
`intent.sitemap_quality={reader:"supplied-sitemap-quality-v1", pages:[...]}`
fixe avant les captures, pour chaque URL distincte, `url`, `preferred_url`,
`indexing` (`allow`/`exclude`), `useful` booléen, `rendering` (`source-only` pour
le seul profil qualifié). Une page est fournie dans `documents` avec URL exacte,
`observed_at`, `context_id`, une liste `http` de requêtes/réponses originales et
`quality_review`. Le client HTTP est fixé par `intent.crawler`.

Lire une requête GET inconditionnelle attribuée, sa réponse complète et le statut
direct. Redirection ou statut final complet hors 200 donne fail ; 206/304 et
réponse incomplète restent inconclusive. Pour 200, rapprocher les canonical HTTP
et HTML de l’URL native, et les directives de l’intention indexable pour Googlebot.
Les lecteurs historiques `exchange`, `header_canonicals`, `canonical.html` et
`directive_values` restent inchangés. Leur sous-ensemble HTML exige UTF8 explicite,
structure complète sans récupération navigateur ; base/template/noscript et autres
contextes non pris en charge restent inconnus. Les règles Googlebot sont appliquées
à la représentation du client fourni, sans preuve de visite réelle Googlebot.

Une canonical explicite divergente, hors head, un noindex qualifié ou une stratégie
revue qui préfère une autre URL, exclut l’indexation ou déclare la page inutile
établit fail. Les canonical identiques répétées restent visibles. L’absence de
canonical explicite reste inconclusive : elle n’est pas à elle seule un défaut SEO.
La revue fournie doit qualifier la stratégie, l’utilité et la suffisance du mode
source-only, liée à toutes les pièces exactes. Elle ne remplace jamais une surface
native inconnue. Un rendu requis ou non qualifié reste NT ; une contradiction
source indépendante conserve NC. Pass n’affirme pas le choix canonique de Google,
une indexabilité complète (robots/accès moteur notamment) ni l’indexation effective.

### TS14-A01 — traçabilité de lastmod

Entrées : `sitemap`, `change-history`, `intent`. Méthode semi-automatique.
`intent.sitemap_lastmod={reader:"supplied-sitemap-lastmod-v1", date_basis:"UTC"}`
fixe la comparaison. Seuls les lastmod des entrées de pages sont visés ; ceux des
index décrivent des fichiers et restent hors périmètre.
Chaque `change_history` contient `file_url`, `entry_index` entier à partir de zéro,
`url`, `event` natif et `review`. `event` conserve les champs du record native,
avec `encoding=identity`, `complete=true`, un JSON UTF8 original attribué comportant
`url`, `change_id`, `changed_at`, `kind` (`content`/`file-generation`) et `description`.
Aucun texte de revue ni événement n’est fabriqué par le lecteur.

Le profil de dates est fermé : `YYYY-MM-DD` valide, ou horodatage zoné
`YYYY-MM-DDTHH:MM:SS[.fraction](Z|±HH:MM)`, fraction de 1 à 6 chiffres, décalage
maximal ±14:00. Les événements exigent un instant zoné. Une date calendaire impossible dans une forme prise en charge ou une valeur vide
donne fail. Une syntaxe, un fuseau absent ou une précision hors profil reste
inconclusive : aucune date erronée n’est déduite de cette limite de preuve.
Ce choix éditorial ne prétend pas implémenter toutes les syntaxes ISO8601.
Un événement sans instant qualifié reste également inconclusive. Comparer les instants en UTC, ou le jour UTC de l’événement pour
lastmod au jour, sans inventer un fuseau local. Une date lastmod future par rapport
à la capture du fichier, une différence de date/instant ou la seule génération du
fichier établit fail. Une revue liée `contradicted` établit aussi fail ; revue
absente/unknown ou événement absent, ambigu, mal attribué, incomplet ou futur : NT.
Un écart de dates attribué survit à une revue manquante. Une date égale exige
encore une revue `supported` de modification significative pour passer.

L’absence de lastmod lue dans une entrée complète est `not-applicable` atomique,
avec preuves `sitemap` et `intent` ; elle n’est pas un défaut. Si toutes les entrées
sont exemptées, l’adaptateur rend le contrôle NT, sans C ni NA automatique.
Un NA du contrôle entier reste une décision distincte étayée par l’inventaire
complet et le contrat de rapport. Une absence de fichier ne vaut jamais exemption.

### Liaison, provenance et restitution

Une revue comporte `evidence_sha256`, `reviewer`, `reason`, `provenance`,
`reviewed_at`, `judgment` (`supported`, `contradicted`, `unknown`). Les deux textes
sont non blancs, chacun au plus 8192 octets UTF8. La revue vient après les pièces
examinées et au plus tard à la date de la cible. Provenance : `synthetic-exercise`
pour l’exercice synthétique ; sinon `human`/`human-assisted`, toujours fournie.
Le SHA-256 porte le JSON compact UTF8, clés triées, sans espaces, de
`{target,observed_at,intent,context,sitemap_files,subject}`. `subject` est la page
sans `quality_review`, ou l’événement enveloppé sans `review`. Aucune signature,
identité de personne, réalité de changement ou capture n’est authentifiée.

L’import refuse les originaux dont le base64, l’empreinte ou le type natif est
corrompu ; aucun rapport n’est créé. Une preuve absente dans un dossier intègre
reste indéterminée. Les diagnostics conservent entrées, résultats par sujet,
inconnues et limites ; l’adaptateur garde les originaux dans input.json et les
artefacts. Une demande partielle de règle ne peut établir TS13 C. Les exemples,
revues et événements du corpus sont explicitement synthétiques, sans audit de site.

## English

### Shared scope, input and assumptions

The three new rules cover only a **declared population of supplied files and
pages**. There is no sitemap discovery, collection or site-wide claim. They reuse
the unchanged [TS15 input contract](sitemap-files-evidence.md): input version 2,
explicit rules/targets, synthetic boolean, context, prior intent, declared roots
and documents, native file records. The target is the first root. The prior plan
precedes a capture window of at most 24 hours, ending no later than the target
observation. Dates, scope, selection and provenance are supplied, unauthenticated.
All page entries in the declared files are examined; no silent URL sampling.

Native base64/SHA-256/encoding/completeness preserve exact bytes. The unchanged
TS15 reader qualifies UTF8, minimal structure, gzip and root/child coverage before
entries are read. TS15 outcomes remain separate: unreadable structure is unknown
here, not a newly issued TS15 verdict. Entry positions are zero-based; repeated
locations remain visible and do not alone prove an incorrect canonical duplicate.
URL comparison is literal, without normalization, equivalence or relative resolution.

Bounds: 16 declared files, 128 total page entries, 2 MiB decompressed XML per file,
128 page records/events, 32 KiB per original UTF8 JSON event/review and 4096-character
native leaves. Existing 5 MiB raw-file and 8 MiB input-envelope limits also apply.
Profile limits, incomplete XML, DTD, missing/ambiguous child or out-of-window files
are inconclusive, while independent contradictions elsewhere survive. No network,
DTD/XSD fetch or browser execution. Context.id binds supplied page observations.

### TS13-A01 — native population and absolute locations

Automatic bounded rule. Inputs: sitemap and intent. Reconcile declared roots and
children, read page locations from qualified urlsets, require absolute HTTP(S)
without credentials, fragment, whitespace, controls, invalid port, backslash or
malformed percent escape. Complete native contradiction fails. Pass needs every
declared file and page entry qualified. Missing discovery/coverage or unreadable
files stay unknown. No atomic exemption or inferred canonical/indexing result.

### TS13-A02 — pages, strategy and review

Semi-automated. Inputs: sitemap, HTTP, HTML and intent. Prior
`intent.sitemap_quality` selects `supplied-sitemap-quality-v1` and `pages` listing
each distinct URL, preferred_url, indexing allow/exclude, useful boolean and
rendering source-only. `documents` supplies exact URL, observed_at, context_id,
original HTTP exchange list and quality_review. intent.crawler fixes the client.

Check an attributed unconditional GET and complete direct status. Redirect or
complete non-200 fails; 206/304 or incomplete response stays unknown. For 200,
compare HTTP/HTML canonical declarations literally with the native URL and check
Googlebot indexing directives. Existing exchange, header_canonicals, canonical.html
and directive_values remain unchanged. Their bounded source reader needs explicit
UTF8 and complete structure without browser recovery; unsupported base/template/
noscript or other contexts remain unknown. Applied Googlebot directive semantics
never establish an actual Googlebot representation or visit.

A different/out-of-head canonical, qualified noindex, reviewed strategy preferring
another URL, excluding indexing or denying usefulness fails. Identical repeated
canonicals remain visible. No explicit canonical is inconclusive, not by itself
an SEO defect. An evidence-bound supplied review must qualify strategy, usefulness
and source-only sufficiency; it cannot qualify unknown native surfaces. Required
or unqualified rendering remains NT; independent source contradictions survive.
Pass establishes neither Google's canonical choice nor complete indexability
(including robots/engine access) nor actual indexing.

### TS14-A01 — lastmod traceability

Semi-automated. Inputs: sitemap, change-history and intent. Prior
`intent.sitemap_lastmod` selects `supplied-sitemap-lastmod-v1` and UTC date_basis.
Only page lastmod is assessed; index lastmod concerns files and stays out of scope.
Each change_history item identifies file_url, integer zero-based entry_index, url,
native event and review. The identity-encoded complete UTF8 JSON event retains
original bytes/SHA-256, url, change_id, changed_at, kind (content/file-generation)
and description. The reader never authors missing events or reviews.

The closed date syntax accepts valid YYYY-MM-DD or zoned
YYYY-MM-DDTHH:MM:SS[.fraction](Z|±HH:MM), 1–6 fractional digits and offsets up to
±14:00. Events require zoned instants. An impossible calendar date in a supported form or an empty value fails.
Unsupported syntax, missing timezone or precision outside this profile remains
inconclusive; no erroneous date is inferred from this evidence limit. This profile
does not implement all ISO8601 syntaxes. Unqualified event timestamps stay unknown. Compare UTC instants, or UTC
event dates for day precision; never invent a local timezone. Future lastmod relative
to the supplied file capture, traceable mismatch, file generation alone or a bound
contradicted review fails. Missing/unknown review or absent, ambiguous, incomplete,
unattributed/future event is inconclusive. An attributed date mismatch survives a
missing review. Equal dates still require a supported significance review to pass.

Native absence of lastmod in a complete entry yields atomic not-applicable with
sitemap and intent evidence; it is not a defect. All-exempt populations yield NT
in the adapter, never C or automatic whole-control NA. Whole-control NA remains a
separate evidenced decision under the report contract. Missing files never exempt.

### Review binding, evidence, unknowns and limits

Reviews supply evidence_sha256, reviewer, reason, provenance, reviewed_at and
judgment (supported/contradicted/unknown). Reviewer/reason must be nonblank and each
at most 8192 UTF8 bytes. Reviews follow the examined evidence and do not postdate
the target. Provenance is synthetic-exercise for synthetic input, otherwise supplied
human/human-assisted. Hash compact UTF8 JSON with sorted keys and no spaces for
{target,observed_at,intent,context,sitemap_files,subject}; subject is the complete
page minus quality_review, or history item minus review. Hashes do not authenticate
identity, actual change, significance or acquisition. Matching dates are insufficient
without the supplied judgment, whose truth the software does not establish.

Import rejects corrupt native base64/hash/type and creates no report. Missing evidence
in an intact dossier stays unknown. Diagnostics retain native entries, per-subject
outcomes, gaps and limitations; input.json and evidence artifacts preserve originals.
Partial rule requests cannot establish TS13 C. Corpus pages, reviews and events are
explicitly synthetic, never a real-site audit, certification or recognized standard.

## Provenance / Provenance

No new third-party observation was collected. The existing captured TS15 references
remain at research/sitemap-files-2026-10-14. This extension operationalizes the RC1
TS13/TS14 editorial expectations; it does not claim external endorsement.
55 authored synthetic cases precede implementation. The initial authored fixture is retained separately. A binding correction and a one-day
shift of fictional dates for the historical import clock are documented in
provenance/sitemap-quality-v1-correction.json; one explicitly documented expectation changes from fail to inconclusive for
an unzoned lastmod. Every other expectation is unchanged.
Les 55 cas initiaux sont conservés ; corrections de liaison et de calendrier fictif
documentées ; une attente sans fuseau passe explicitement de fail à inconclusive.
Toutes les autres attentes et les tests historiques sont conservés.
