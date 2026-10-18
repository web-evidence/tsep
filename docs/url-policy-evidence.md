# URL policies and variants / Politiques et variantes d’URL

Normative profile `url-policy-v1`, reader1, protocol0.3.0-draft.2.
The [shared dossier contract](evidence-dossier-v1.md) defines original-byte
integrity, chronology, human-review binding, bounds and precedence.
Le [contrat commun](evidence-dossier-v1.md) définit intégrité, dates, liaison des
revues humaines, bornes et priorité des contradictions. Chaque règle ci-dessous
garde un verdict distinct ; aucun test partiel ne clôt un contrôle.

## Formats / Formats

FR : les objets JSON natifs sont des documents fournis, pas des observations
serveur authentifiées. Le champ format est obligatoire. Les exemples ci-dessous
sont des schémas de champs ; toutes les fixtures distribuées sont synthétiques.
EN: native JSON objects are supplied documents, not authenticated server
observations. The format field is required. The following are field schemas;
all distributed fixtures are synthetic.

- `exclusion-register-v1`: families=[{id, mechanism, owner, reason, review_date}].
  Plan item: id, record, mechanism. Dates de calendrier ISO / ISO calendar dates.
- `url-pattern-config-v1`: patterns=[{id, max_combinations, navigation, indexing}].
  Plan item: id, configuration, crawl, urls, max_combinations, navigation, indexing,
  trap_decision. URLs:1–128, exactes et uniques / exact unique.
- `url-crawl-v1`: rows=[{key,url}],1–128 lignes/rows, key unique.
- `url-shape-config-v1`: items reprend les objets du plan / exact plan items.
  Plan item: id, before, after, case (lower-path/preserve), allow_fragment bool,
  stability=stable, decisions=[{key,before,after,reason}]. Le record de configuration
  se nomme `policy` / configuration record is named `policy`.
- TS11 plan item: id, left, right, relation (duplicate/distinct),
  rendering=source-only-reviewed. Les pièces content sont les originaux HTML et
  revues fournis / content evidence consists of supplied HTML originals and reviews.
- TS38 plan item: id, variants (1–32), preferred, equivalence (equivalent/distinct),
  rendering=source-only-reviewed, sitemap (record ID), link_sources (1–32).
  Sitemap: complete native XML urlset, at most128 entries,1MiB; indexes are
  inconclusive. Les liens sont lus dans chaque source complète prévue, même sans
  lien pertinent / every planned complete source is read, including zero-link cases.

## Portée du rendu / Rendering scope

FR : TS11/TS38 qualifient seulement un périmètre source-only-reviewed déclaré
avant les pièces. La revue humaine liée doit justifier que ces sources suffisent
pour le cas choisi. Dès que le contenu ou les signaux nécessitent le rendu,
utiliser une évaluation humaine complète ou un futur profil de rendu ; ce lecteur
reste NT. Aucune supposition automatique selon l’absence d’un script, ni transfert
d’un pass TS10/TS17/TS25. Les URL sont comparées littéralement après résolution
relative des déclarations ; ni équivalence de casse, ni choix du moteur inférés.
TS20 contrôle une syntaxe bornée, pas toutes les équivalences WHATWG/serveur ;
percent-encoding non UTF-8 et caractères de contrôle encodés sont indéterminés.
EN: TS11/TS38 qualify only a prior source-only-reviewed scope. The bound human
review must justify source sufficiency for the selected case. If content/signals
require rendering, use a complete human assessment or a future rendering profile;
this reader remains NT. It makes no script-absence assumption and borrows no
TS10/TS17/TS25 pass. URLs compare literally after relative declaration resolution;
case equivalence and engine selection are not inferred. TS20 checks bounded syntax,
not all WHATWG/server equivalences; non-UTF8 percent encoding and escaped control
characters are inconclusive.

## TS09-A01

### Français

**Registre des exclusions et responsabilités**

Entrées : configuration, intent.

**Périmètre** — Éléments explicitement sélectionnés du contrôle TS09 ; profil url-policy-v1 décrit dans docs/url-policy-evidence.md.

**Procédure** — Lire le registre natif JSON exclusion-register-v1 ; rapprocher chaque famille sélectionnée du mécanisme préalable, puis vérifier propriétaire, motif et date de revue. Exiger une revue liée au dossier.

**Attendus** — Les mécanismes concordent et chaque famille a ses informations de gouvernance ; la revue fournie confirme le périmètre. Une divergence de mécanisme échoue.

**Preuves** — Plan préalable, octets originaux et SHA-256, dates/contexte, observations atomiques, revue humaine motivée liée à tout le dossier. Types : configuration, intent.

**Hypothèses** — Population et provenance fournies ; la revue assume la suffisance du périmètre et le jugement métier. Aucun contenu, verdict importé ou hash ne prouve l’authenticité.

**Indéterminés** — Un champ absent ou ambigu, un registre manquant ou une revue non liée donne indéterminé. La date de revue est une date de calendrier déclarée, pas une preuve de réalisation.

**Non-applicabilité** — Aucune exemption atomique dans ce profil. Population vide ou preuve absente : NT, jamais NA automatique.

**Limites** — Lecture hors ligne bornée, sans collecte, navigateur exécuté, jugement humain produit ni audit réel. Périmètre source revu uniquement ; aucune complétude du site, indexation, classement ou causalité déduite.

### English

**Exclusion register and ownership**

Inputs: configuration, intent.

**Scope** — Explicitly selected TS09 items; url-policy-v1 profile defined in docs/url-policy-evidence.md.

**Procedure** — Read the native exclusion-register-v1 JSON register; compare each selected family with its prior mechanism, then require owner, rationale and review date. Require an evidence-bound review.

**Expectations** — Mechanisms agree and every family has governance information; supplied review supports the scope. A mechanism mismatch fails.

**Evidence** — Prior plan, original bytes and SHA-256, dates/context, atomic observations, reasoned human review bound to the entire dossier. Kinds: configuration, intent.

**Assumptions** — Supplied population and provenance; review assumes scope sufficiency and business judgment. Content, imported verdicts or hashes never prove authenticity.

**Inconclusive** — Missing or ambiguous fields, missing register or unbound review are inconclusive. Review date is a declared calendar date, not evidence that review occurred.

**Non-applicability** — No atomic exemption in this profile. Empty population or absent evidence: NT, never automatic NA.

**Limitations** — Bounded offline reading, without collection, browser execution, generated human judgment or real audit. Reviewed source scope only; no site completeness, indexing, ranking or causality inferred.

## TS11-A01

### Français

**Comparaison éditoriale des variantes**

Entrées : http, html, content, intent.

**Périmètre** — Éléments explicitement sélectionnés du contrôle TS11 ; profil url-policy-v1 décrit dans docs/url-policy-evidence.md.

**Procédure** — Pour chaque paire déclarée duplicate ou distinct, lire les deux réponses HTML UTF-8 complètes et conserver leurs empreintes. Exiger la revue comparative liée, y compris la suffisance du périmètre source.

**Attendus** — Les deux contenus sont disponibles et la revue éditoriale étaye la relation déclarée. Une revue contradictoire échoue ; égalité ou similarité textuelle ne crée pas cette revue.

**Preuves** — Plan préalable, octets originaux et SHA-256, dates/contexte, observations atomiques, revue humaine motivée liée à tout le dossier. Types : http, html, content, intent.

**Hypothèses** — Population et provenance fournies ; la revue assume la suffisance du périmètre et le jugement métier. Aucun contenu, verdict importé ou hash ne prouve l’authenticité.

**Indéterminés** — Contenu absent, format HTML non pris en charge, comparaison dépendante du rendu ou jugement manquant : indéterminé.

**Non-applicabilité** — Aucune exemption atomique dans ce profil. Population vide ou preuve absente : NT, jamais NA automatique.

**Limites** — Lecture hors ligne bornée, sans collecte, navigateur exécuté, jugement humain produit ni audit réel. Périmètre source revu uniquement ; aucune complétude du site, indexation, classement ou causalité déduite.

### English

**Editorial comparison of variants**

Inputs: http, html, content, intent.

**Scope** — Explicitly selected TS11 items; url-policy-v1 profile defined in docs/url-policy-evidence.md.

**Procedure** — For each declared duplicate or distinct pair, read both complete UTF-8 HTML responses and retain fingerprints. Require a bound comparative review including source-scope sufficiency.

**Expectations** — Both contents are available and the supplied editorial review supports the declared relation. Contradictory review fails; text equality or similarity never supplies that review.

**Evidence** — Prior plan, original bytes and SHA-256, dates/context, atomic observations, reasoned human review bound to the entire dossier. Kinds: http, html, content, intent.

**Assumptions** — Supplied population and provenance; review assumes scope sufficiency and business judgment. Content, imported verdicts or hashes never prove authenticity.

**Inconclusive** — Missing content, unsupported HTML, render-dependent comparison or missing judgment: inconclusive.

**Non-applicability** — No atomic exemption in this profile. Empty population or absent evidence: NT, never automatic NA.

**Limitations** — Bounded offline reading, without collection, browser execution, generated human judgment or real audit. Reviewed source scope only; no site completeness, indexing, ranking or causality inferred.

## TS11-A02

### Français

**Convergence sans absorption de pages distinctes**

Entrées : http, html, content, intent.

**Périmètre** — Éléments explicitement sélectionnés du contrôle TS11 ; profil url-policy-v1 décrit dans docs/url-policy-evidence.md.

**Procédure** — Lire séparément canonical HTTP et HTML des deux membres. Un doublon désigne la préférence ; une page distincte se désigne elle-même. Exiger la revue de la décision et du périmètre source.

**Attendus** — Toutes les déclarations qualifiées concordent avec la relation éditoriale préalable ; une déclaration contraire échoue, même si une autre surface manque.

**Preuves** — Plan préalable, octets originaux et SHA-256, dates/contexte, observations atomiques, revue humaine motivée liée à tout le dossier. Types : http, html, content, intent.

**Hypothèses** — Population et provenance fournies ; la revue assume la suffisance du périmètre et le jugement métier. Aucun contenu, verdict importé ou hash ne prouve l’authenticité.

**Indéterminés** — Aucune canonical explicite, source non interprétable ou rendu nécessaire non fourni : indéterminé, sans choix du moteur inféré.

**Non-applicabilité** — Aucune exemption atomique dans ce profil. Population vide ou preuve absente : NT, jamais NA automatique.

**Limites** — Lecture hors ligne bornée, sans collecte, navigateur exécuté, jugement humain produit ni audit réel. Périmètre source revu uniquement ; aucune complétude du site, indexation, classement ou causalité déduite.

### English

**Convergence without absorbing distinct pages**

Inputs: http, html, content, intent.

**Scope** — Explicitly selected TS11 items; url-policy-v1 profile defined in docs/url-policy-evidence.md.

**Procedure** — Read HTTP and HTML canonicals separately for both members. A duplicate points to the preference; a distinct page points to itself. Require review of the decision and source scope.

**Expectations** — Every qualified declaration agrees with the prior editorial relation; a conflicting declaration fails even if another surface is unavailable.

**Evidence** — Prior plan, original bytes and SHA-256, dates/context, atomic observations, reasoned human review bound to the entire dossier. Kinds: http, html, content, intent.

**Assumptions** — Supplied population and provenance; review assumes scope sufficiency and business judgment. Content, imported verdicts or hashes never prove authenticity.

**Inconclusive** — No explicit canonical, uninterpretable source or required rendering unavailable: inconclusive, without inferring engine selection.

**Non-applicability** — No atomic exemption in this profile. Empty population or absent evidence: NT, never automatic NA.

**Limitations** — Bounded offline reading, without collection, browser execution, generated human judgment or real audit. Reviewed source scope only; no site completeness, indexing, ranking or causality inferred.

## TS19-A01

### Français

**Politique bornée par motif combinatoire**

Entrées : configuration, intent.

**Périmètre** — Éléments explicitement sélectionnés du contrôle TS19 ; profil url-policy-v1 décrit dans docs/url-policy-evidence.md.

**Procédure** — Comparer les axes max_combinations, navigation et indexing du fichier natif url-pattern-config-v1 à chaque motif préalable ; exiger la revue du choix de bornes.

**Attendus** — Chaque axe fourni correspond au plan fini sélectionné. Une valeur contradictoire, notamment une limite nulle contraire au plan positif, échoue.

**Preuves** — Plan préalable, octets originaux et SHA-256, dates/contexte, observations atomiques, revue humaine motivée liée à tout le dossier. Types : configuration, intent.

**Hypothèses** — Population et provenance fournies ; la revue assume la suffisance du périmètre et le jugement métier. Aucun contenu, verdict importé ou hash ne prouve l’authenticité.

**Indéterminés** — Axe ou configuration manquant, borne non entière ou hors 1–128, revue absente : indéterminé.

**Non-applicabilité** — Aucune exemption atomique dans ce profil. Population vide ou preuve absente : NT, jamais NA automatique.

**Limites** — Lecture hors ligne bornée, sans collecte, navigateur exécuté, jugement humain produit ni audit réel. Périmètre source revu uniquement ; aucune complétude du site, indexation, classement ou causalité déduite.

### English

**Bounded combinatorial-pattern policy**

Inputs: configuration, intent.

**Scope** — Explicitly selected TS19 items; url-policy-v1 profile defined in docs/url-policy-evidence.md.

**Procedure** — Compare max_combinations, navigation and indexing in native url-pattern-config-v1 with each prior pattern; require review of the chosen bounds.

**Expectations** — Every supplied axis matches the selected finite plan. A conflicting value, including zero against a positive planned limit, fails.

**Evidence** — Prior plan, original bytes and SHA-256, dates/context, atomic observations, reasoned human review bound to the entire dossier. Kinds: configuration, intent.

**Assumptions** — Supplied population and provenance; review assumes scope sufficiency and business judgment. Content, imported verdicts or hashes never prove authenticity.

**Inconclusive** — Missing axis/configuration, non-integer bound outside1–128 or absent review: inconclusive.

**Non-applicability** — No atomic exemption in this profile. Empty population or absent evidence: NT, never automatic NA.

**Limitations** — Bounded offline reading, without collection, browser execution, generated human judgment or real audit. Reviewed source scope only; no site completeness, indexing, ranking or causality inferred.

## TS19-A02

### Français

**Population observée et décision sur les pièges**

Entrées : crawl, intent.

**Périmètre** — Éléments explicitement sélectionnés du contrôle TS19 ; profil url-policy-v1 décrit dans docs/url-policy-evidence.md.

**Procédure** — Lire url-crawl-v1, compter les URL distinctes et les comparer à la liste finie et à sa borne ; conserver la décision motivée sur les pièges/cycles et sa revue.

**Attendus** — Les URL observées appartiennent à la population prévue, leur nombre respecte la borne et les pièges sont expliqués. Une URL extérieure ou un dépassement échoue.

**Preuves** — Plan préalable, octets originaux et SHA-256, dates/contexte, observations atomiques, revue humaine motivée liée à tout le dossier. Types : crawl, intent.

**Hypothèses** — Population et provenance fournies ; la revue assume la suffisance du périmètre et le jugement métier. Aucun contenu, verdict importé ou hash ne prouve l’authenticité.

**Indéterminés** — Crawl fourni incomplet, identités ambiguës, liste ou décision absente : indéterminé. Un échantillon fini ne prouve jamais la finitude de tout le site.

**Non-applicabilité** — Aucune exemption atomique dans ce profil. Population vide ou preuve absente : NT, jamais NA automatique.

**Limites** — Lecture hors ligne bornée, sans collecte, navigateur exécuté, jugement humain produit ni audit réel. Périmètre source revu uniquement ; aucune complétude du site, indexation, classement ou causalité déduite.

### English

**Observed population and trap decision**

Inputs: crawl, intent.

**Scope** — Explicitly selected TS19 items; url-policy-v1 profile defined in docs/url-policy-evidence.md.

**Procedure** — Read url-crawl-v1, count distinct URLs and compare with the finite list and bound; retain the reasoned trap/cycle decision and its review.

**Expectations** — Observed URLs belong to the planned population, their count respects the bound and traps are explained. An outside URL or exceeded bound fails.

**Evidence** — Prior plan, original bytes and SHA-256, dates/context, atomic observations, reasoned human review bound to the entire dossier. Kinds: crawl, intent.

**Assumptions** — Supplied population and provenance; review assumes scope sufficiency and business judgment. Content, imported verdicts or hashes never prove authenticity.

**Inconclusive** — Incomplete supplied crawl, ambiguous identities, absent list or decision: inconclusive. A finite sample never proves whole-site finiteness.

**Non-applicability** — No atomic exemption in this profile. Empty population or absent evidence: NT, never automatic NA.

**Limitations** — Bounded offline reading, without collection, browser execution, generated human judgment or real audit. Reviewed source scope only; no site completeness, indexing, ranking or causality inferred.

## TS20-A01

### Français

**Forme des URL selon la politique fournie**

Entrées : crawl, configuration, intent.

**Périmètre** — Éléments explicitement sélectionnés du contrôle TS20 ; profil url-policy-v1 décrit dans docs/url-policy-evidence.md.

**Procédure** — Lire la capture après et url-shape-config-v1. Vérifier espaces/contrôles, antislash, échappements percent, fragments et casse de chemin selon les choix préalables ; revue humaine de lisibilité.

**Attendus** — La configuration correspond au plan et chaque URL respecte ses axes lexicaux. Une divergence qualifiée échoue. Aucun changement implicite de casse ou de décodage.

**Preuves** — Plan préalable, octets originaux et SHA-256, dates/contexte, observations atomiques, revue humaine motivée liée à tout le dossier. Types : crawl, configuration, intent.

**Hypothèses** — Population et provenance fournies ; la revue assume la suffisance du périmètre et le jugement métier. Aucun contenu, verdict importé ou hash ne prouve l’authenticité.

**Indéterminés** — URL/autorité non prise en charge, politique inconnue, capture ou revue manquante : indéterminé.

**Non-applicabilité** — Aucune exemption atomique dans ce profil. Population vide ou preuve absente : NT, jamais NA automatique.

**Limites** — Lecture hors ligne bornée, sans collecte, navigateur exécuté, jugement humain produit ni audit réel. Périmètre source revu uniquement ; aucune complétude du site, indexation, classement ou causalité déduite.

### English

**URL shape under supplied policy**

Inputs: crawl, configuration, intent.

**Scope** — Explicitly selected TS20 items; url-policy-v1 profile defined in docs/url-policy-evidence.md.

**Procedure** — Read the later capture and url-shape-config-v1. Check spaces/controls, backslashes, percent escapes, fragments and path case against prior choices; require human readability review.

**Expectations** — Configuration matches the plan and every URL satisfies its lexical axes. A qualified mismatch fails. No implicit case change or decoding.

**Evidence** — Prior plan, original bytes and SHA-256, dates/context, atomic observations, reasoned human review bound to the entire dossier. Kinds: crawl, configuration, intent.

**Assumptions** — Supplied population and provenance; review assumes scope sufficiency and business judgment. Content, imported verdicts or hashes never prove authenticity.

**Inconclusive** — Unsupported URL/authority, unknown policy, missing capture or review: inconclusive.

**Non-applicability** — No atomic exemption in this profile. Empty population or absent evidence: NT, never automatic NA.

**Limitations** — Bounded offline reading, without collection, browser execution, generated human judgment or real audit. Reviewed source scope only; no site completeness, indexing, ranking or causality inferred.

## TS20-A02

### Français

**Stabilité temporelle et décisions de variation**

Entrées : crawl, configuration, intent.

**Périmètre** — Éléments explicitement sélectionnés du contrôle TS20 ; profil url-policy-v1 décrit dans docs/url-policy-evidence.md.

**Procédure** — Comparer deux captures ordonnées url-crawl-v1 ayant les mêmes identités ; toute URL changée doit avoir une décision unique avant/après avec motif, dans le plan lié à la revue.

**Attendus** — Les URL sont égales aux deux dates, ou leur variation est explicitement décidée et revue. Un changement observé sans décision échoue.

**Preuves** — Plan préalable, octets originaux et SHA-256, dates/contexte, observations atomiques, revue humaine motivée liée à tout le dossier. Types : crawl, configuration, intent.

**Hypothèses** — Population et provenance fournies ; la revue assume la suffisance du périmètre et le jugement métier. Aucun contenu, verdict importé ou hash ne prouve l’authenticité.

**Indéterminés** — Une seule date, dates inversées/égales, identité manquante ou revue absente : indéterminé. La stabilité future reste inconnue.

**Non-applicabilité** — Aucune exemption atomique dans ce profil. Population vide ou preuve absente : NT, jamais NA automatique.

**Limites** — Lecture hors ligne bornée, sans collecte, navigateur exécuté, jugement humain produit ni audit réel. Périmètre source revu uniquement ; aucune complétude du site, indexation, classement ou causalité déduite.

### English

**Temporal stability and variation decisions**

Inputs: crawl, configuration, intent.

**Scope** — Explicitly selected TS20 items; url-policy-v1 profile defined in docs/url-policy-evidence.md.

**Procedure** — Compare two ordered url-crawl-v1 captures with matching identities; every changed URL requires one reasoned before/after decision in the reviewed plan.

**Expectations** — URLs match at the two dates or their variation is explicitly decided and reviewed. An observed change without a decision fails.

**Evidence** — Prior plan, original bytes and SHA-256, dates/context, atomic observations, reasoned human review bound to the entire dossier. Kinds: crawl, configuration, intent.

**Assumptions** — Supplied population and provenance; review assumes scope sufficiency and business judgment. Content, imported verdicts or hashes never prove authenticity.

**Inconclusive** — One date, reversed/equal dates, missing identity or review: inconclusive. Future stability remains unknown.

**Non-applicability** — No atomic exemption in this profile. Empty population or absent evidence: NT, never automatic NA.

**Limitations** — Bounded offline reading, without collection, browser execution, generated human judgment or real audit. Reviewed source scope only; no site completeness, indexing, ranking or causality inferred.

## TS38-A01

### Français

**Trajectoires et canonical des variantes équivalentes**

Entrées : http, html, content, intent.

**Périmètre** — Éléments explicitement sélectionnés du contrôle TS38 ; profil url-policy-v1 décrit dans docs/url-policy-evidence.md.

**Procédure** — Exiger l’équivalence revue puis lire chaque trajectoire native : un seul saut depuis chaque variante, réponse directe 200 pour la préférence, canonical HTTP/HTML vers elle.

**Attendus** — Chaque variante converge en un saut et chaque canonical qualifiée concorde. La fusion déclarée de ressources distinctes ou une divergence native échoue.

**Preuves** — Plan préalable, octets originaux et SHA-256, dates/contexte, observations atomiques, revue humaine motivée liée à tout le dossier. Types : http, html, content, intent.

**Hypothèses** — Population et provenance fournies ; la revue assume la suffisance du périmètre et le jugement métier. Aucun contenu, verdict importé ou hash ne prouve l’authenticité.

**Indéterminés** — Trace manquante, canonical absente, équivalence non décidée ou rendu nécessaire : indéterminé.

**Non-applicabilité** — Aucune exemption atomique dans ce profil. Population vide ou preuve absente : NT, jamais NA automatique.

**Limites** — Lecture hors ligne bornée, sans collecte, navigateur exécuté, jugement humain produit ni audit réel. Périmètre source revu uniquement ; aucune complétude du site, indexation, classement ou causalité déduite.

### English

**Trajectories and canonicals of equivalent variants**

Inputs: http, html, content, intent.

**Scope** — Explicitly selected TS38 items; url-policy-v1 profile defined in docs/url-policy-evidence.md.

**Procedure** — Require reviewed equivalence and read every native trajectory: one hop from each variant, direct200 preferred response, HTTP/HTML canonical pointing to it.

**Expectations** — Every variant converges in one hop and every qualified canonical agrees. Declared merging of distinct resources or native disagreement fails.

**Evidence** — Prior plan, original bytes and SHA-256, dates/context, atomic observations, reasoned human review bound to the entire dossier. Kinds: http, html, content, intent.

**Assumptions** — Supplied population and provenance; review assumes scope sufficiency and business judgment. Content, imported verdicts or hashes never prove authenticity.

**Inconclusive** — Missing trace/canonical, undecided equivalence or necessary rendering: inconclusive.

**Non-applicability** — No atomic exemption in this profile. Empty population or absent evidence: NT, never automatic NA.

**Limitations** — Bounded offline reading, without collection, browser execution, generated human judgment or real audit. Reviewed source scope only; no site completeness, indexing, ranking or causality inferred.

## TS38-A02

### Français

**Signaux internes des variantes**

Entrées : sitemap, html, crawl, content, intent.

**Périmètre** — Éléments explicitement sélectionnés du contrôle TS38 ; profil url-policy-v1 décrit dans docs/url-policy-evidence.md.

**Procédure** — Lire le urlset natif complet sélectionné et toutes les sources de liens prévues. Exiger la présence de la préférence dans ce sitemap, aucune variante non préférée dans sitemap/liens et la revue d’équivalence/périmètre.

**Attendus** — Sitemap et liens du périmètre concordent avec la préférence ; une divergence ou fusion de pages distinctes échoue. Zéro lien reste une observation du corpus complet fourni.

**Preuves** — Plan préalable, octets originaux et SHA-256, dates/contexte, observations atomiques, revue humaine motivée liée à tout le dossier. Types : sitemap, html, crawl, content, intent.

**Hypothèses** — Population et provenance fournies ; la revue assume la suffisance du périmètre et le jugement métier. Aucun contenu, verdict importé ou hash ne prouve l’authenticité.

**Indéterminés** — Index XML, fichier tronqué, source de liens manquante, population ou revue ambiguë : indéterminé ; aucune absence globale inférée.

**Non-applicabilité** — Aucune exemption atomique dans ce profil. Population vide ou preuve absente : NT, jamais NA automatique.

**Limites** — Lecture hors ligne bornée, sans collecte, navigateur exécuté, jugement humain produit ni audit réel. Périmètre source revu uniquement ; aucune complétude du site, indexation, classement ou causalité déduite.

### English

**Internal signals for variants**

Inputs: sitemap, html, crawl, content, intent.

**Scope** — Explicitly selected TS38 items; url-policy-v1 profile defined in docs/url-policy-evidence.md.

**Procedure** — Read the selected complete native urlset and every planned link source. Require the preference in that sitemap, no nonpreferred variant in sitemap/links, and equivalence/scope review.

**Expectations** — Sitemap and scoped links agree with the preference; disagreement or merging distinct pages fails. Zero links remains an observation of the complete supplied corpus.

**Evidence** — Prior plan, original bytes and SHA-256, dates/context, atomic observations, reasoned human review bound to the entire dossier. Kinds: sitemap, html, crawl, content, intent.

**Assumptions** — Supplied population and provenance; review assumes scope sufficiency and business judgment. Content, imported verdicts or hashes never prove authenticity.

**Inconclusive** — XML index, truncated file, missing link source, ambiguous population/review: inconclusive; no global absence inferred.

**Non-applicability** — No atomic exemption in this profile. Empty population or absent evidence: NT, never automatic NA.

**Limitations** — Bounded offline reading, without collection, browser execution, generated human judgment or real audit. Reviewed source scope only; no site completeness, indexing, ranking or causality inferred.

