# TS01 parsed-source markers / Marqueurs source parsés TS01

Édition normative draft.6 / Normative edition draft.6 : exclusions ASCII structurelles attribuées, sans modification des octets / attributable structural ASCII exclusions, original bytes unchanged. [Contrat FR/EN](migration-0.3.0-draft.6.md).

## Français

Draft.28 ajoute le profil facultatif **`identity_reader: "html-tree-markers-v1"`**
à TS01-A02. Il doit figurer dans l'intention datée avant la capture. L'absence de
ce champ conserve le lecteur historique. Le champ `source_reader` de TS07 ne
sélectionne pas ce profil. Un nom inconnu ne déclenche aucun repli.

### Applicabilité, entrées et ordre des décisions

Le profil intervient seulement dans la branche des marqueurs : réponse HTTP
complète attribuable, intention préalable, URL finale égale à la référence valide,
empreinte de référence valide mais différente, sans `representation: "stable"`.
URL différente, empreinte complète identique et stabilité exigée conservent leurs
priorités. Le lecteur n'est pas exécuté pour ces décisions antérieures, même si
`identity_reader` serait invalide. Une politique de représentation inconnue, une
référence manquante ou une intention postérieure restent indéterminées comme avant.

Les entrées sont le corps complet après décodage HTTP, ses en-têtes finaux,
l'intention et les outils identifiés. La lecture est limitée à une unique valeur
Content-Type `text/html` avec le seul paramètre charset UTF-8 explicite, selon le
profil borné d'inventaire source. Un BOM UTF-8 initial est consommé mais reste dans
les octets conservés ; les octets invalides et les autres encodages ne sont pas
réinterprétés. `text/plain` reste disponible sous le lecteur historique ; il est
hors portée de ce profil HTML. Aucune modification du corps servant au SHA-256.

Les listes `required_markers` et `forbidden_markers` sont littérales, uniques,
non blanches et sans surrogate Unicode ; au plus 64 chaînes par liste et 4 096
caractères par chaîne. Un interdit contenu dans un requis est contradictoire.
Les critères ne sont ni normalisés ni corrigés. Pass exige au moins un requis ;
sans requis, l'absence des seuls interdits reste inconclusive, leur présence fail.

### Attendus de lecture

parse5 8.0.1 / entities 8.0.0, avec Node 24, produit deux arbres statiques du
document entier, scripting activé puis désactivé. Aucun JavaScript n'est exécuté.
Chaque hypothèse s'applique à tous les noscript ; aucun choix par élément ou par
marqueur. Le texte HTML attribuable sous head/body est comparé, y compris title,
textarea, toutes les options et le texte masqué. Commentaires, scripts/styles
HTML et SVG et contenus de template HTML inactifs sont exclus. Un texte étranger
non blanc hors contexte exclu rend la lecture indisponible ; les blancs étrangers
ne sont pas des segments HTML comparés.

Chaque segment doit correspondre à un intervalle continu des octets originaux.
Il n'est jamais joint à un autre segment à travers du balisage ou un commentaire.
Les CRLF et CR bruts sont normalisés en LF avant résolution des références de
caractères. Le noscript brut dans l'hypothèse activée ne résout pas ces références.
L'omission du LF initial de pre/textarea est conservée. Ni les autres espaces, ni
la casse, ni Unicode, ni les marqueurs fournis ne sont normalisés. Une référence
`&#13;` conserve CR dans l'arbre mais son erreur rapportée rend ce profil inconclusif.

Un requis absent ou un interdit présent fait échouer une lecture complète. Deux
lectures complètes pass donnent pass ; deux fail donnent fail avec leurs raisons.
Tout autre couple donne inconclusive, y compris fail/inconclusive. Il ne s'agit
pas de deux états rendus simultanément ni d'un vote entre des navigateurs.

### Preuves, inconnues et limites

Conserver le corps/HTTP original et l'intention, les versions et empreintes des
outils, runtime et décodage. Le diagnostic garde, pour chaque hypothèse, tous les
segments admis et exclus, texte parsé, texte source brut, positions UTF-16 et octets,
contextes, omissions de LF, marqueurs manquants/présents, premières correspondances
par segment, complétude, erreurs rapportées et raisons. Les offsets de correspondance
comptent les caractères Python du texte parsé, pas les octets ou les unités UTF-16.

Les suites de noms et espaces de noms des ancêtres consignées par la projection
sont regroupées dans `contexts` et référencées par `context_id`, sans supprimer
de segment. Ce n'est ni l'identité des éléments DOM ni une comparaison de leurs
attributs ; chaque `node_id` reste distinct. Les tables sont propres à chaque
hypothèse ; les identifiants suivent la première occurrence, segments admis puis
exclus. À chaque évaluation, développer tous les enregistrements doit restituer
exactement la projection calculée, y compris son résultat et ses métadonnées ;
une différence rend le diagnostic inconclusif. Le nombre de nœuds et l'état de chaque
arbre restent visibles ; l'arbre complet n'est pas dupliqué dans ce diagnostic.
Il est reconstructible hors ligne à partir du corps, des outils et de l'environnement
exact consigné (versions Node et V8), sous réserve de leur disponibilité. Le binaire
Node n'est pas distribué ni authentifié par cette pièce. Les attributs des ancêtres
font partie de cet arbre recalculé, pas de la table de contextes. Les arbres
seuls ne prouvent pas l'authenticité de la collecte. Le rejeu natif compare toutes
les observations ; modifier puis réempreinter un diagnostic ne suffit pas à le valider.

Toute erreur **signalée par parse5**, arbre incomplet, attribution ambiguë,
intervalle fusionné ou chevauchant, frame ou contexte brut hors portée, template
shadow/streaming et texte étranger non blanc hors contexte exclu rend la projection
entière inconclusive. Aucun préfixe déjà favorable ou défavorable ne décide alors.
L'absence d'erreurs rapportées ne prouve pas la validité HTML. Le profil refuse
iframe/frame/frameset, plaintext/xmp/noembed/noframes/listing hors contexte inactif.

Bornes : corps 8 Mio ; 20 000 nœuds et segments ; profondeur 128 ; 1 000 erreurs ;
processus Node 30 secondes et old-space 128 Mio (pas RSS) ; observation intermédiaire
32 Mio ; 50 000 correspondances marqueur/segment ; diagnostic normatif final 4 Mio.
Un dépassement, un runtime absent ou un échec d'encodage conserve inconclusive,
sans extraction de secours, résultat partiel ou absence déduite. Une projection
indisponible contient des segments `null`. Un dépassement du diagnostic conserve
un reçu de refus compact et l'entrée originale, sans verdict conclusif. Le garde
d'API réseau n'est pas une isolation système.

Ce contrôle compare à une intention fournie, dont la pertinence reste sous la
responsabilité du propriétaire. Ni visibilité, état de formulaire, DOM effectivement
rendu, vérité ou suffisance sémantique, soft 404 moteur, indexation ou classement.
Une chaîne interdite répartie entre plusieurs segments peut ne pas être trouvée
même si elle apparaît visuellement continue. A01 doit toujours être évaluée pour
conclure TS01 ; une réussite A02 isolée ne vaut pas C.

## English

Draft.28 adds optional **`identity_reader: "html-tree-markers-v1"`** to TS01-A02,
explicitly selected in intent dated before capture. Absence preserves the historical
reader; TS07's source_reader does not select it. Unknown names never trigger fallback.

Applicability is only the changed-body marker branch after attributable complete
HTTP, prior intent, matching valid final URL, valid differing reference hash and
absence of required stability. URL mismatch, equal complete hash and declared
stable representation retain precedence; the parser is not invoked for those
earlier decisions, even with an invalid reader field. Unknown representation policy,
missing references and subsequent intent remain inconclusive.

Inputs are complete HTTP-decoded bytes, final headers, intent and identified tools.
Require one text/html Content-Type with only an explicit UTF-8 charset under the
bounded source inventory profile. Consume one initial UTF-8 BOM without removing
it from retained bytes. Do not reinterpret invalid bytes or other encodings.
text/plain remains supported by the historical reader, outside this HTML profile.
Complete-body hashing is unchanged. Literal marker lists contain at most 64 unique,
nonblank strings each, at most 4,096 characters each, without Unicode surrogates.
A forbidden substring of a required marker is contradictory. Never normalize or
repair criteria. Pass requires a required marker; forbidden-only absence stays
inconclusive, while presence fails a complete reading.

Pinned parse5 8.0.1 / entities 8.0.0 on Node24 builds two complete static document
hypotheses with scripting enabled/disabled; neither executes scripts. No per-element
or per-marker mode choice. Compare attributable HTML text under head/body, including
title, textarea, all options and hidden text. Exclude comments, HTML/SVG scripts/styles
and inactive HTML template contents. Nonblank foreign text outside excluded contexts
refuses the reading; foreign whitespace is not a compared HTML segment.

Each segment must derive from one contiguous original-byte interval. Never join
across markup or comments. Raw CRLF/CR become LF before reference expansion; enabled
noscript RAWTEXT does not expand references. Preserve initial-LF omission in
pre/textarea. No other whitespace/case/Unicode or criterion normalization.
Numeric &#13; retains CR in the raw tree but its reported parse error refuses this
profile. Missing required or present forbidden text fails a complete reading.
Both complete readings pass gives pass; both fail gives fail; every other pair,
including fail/inconclusive, is inconclusive. This is no browser vote or measured DOM.

Retain original HTTP/body and intent, versions/source hashes/runtime/decoding,
every admitted/excluded segment, parsed/raw text, UTF-16 and byte intervals, contexts,
LF omissions, missing/present markers, first hit per segment, completeness, reported
errors and reasons. Match offsets count Python parsed-text characters, not bytes
or UTF-16 units. The projection's ancestor name/namespace arrays are interned in
contexts and referenced by context_id; no segment or distinct node_id is removed.
These are not DOM element identities or attribute comparisons. Tables are local to
each hypothesis; IDs follow first occurrence, admitted records then excluded records.
Every assessment expands all records and checks exact equality with the calculated
projection, including outcomes and metadata; a mismatch is inconclusive.
Node counts and tree state remain; full trees are reconstructible offline from
original bytes, exact tools and recorded Node/V8 versions, subject to availability.
The Node binary is neither distributed nor authenticated by this artifact. Ancestor
attributes belong to the recalculated tree, not the context table. Native replay
compares all observations, including coherently
rehashed tampering. This does not authenticate collection.

Any reported parse5 error, incomplete tree, ambiguous/merged/overlapping span,
unsupported frame/raw context, shadow/streaming template or nonblank foreign text
outside exclusions refuses the whole projection, regardless of an earlier apparent
contradiction. No reported errors is not HTML validity. Outside inactive contexts,
iframe/frame/frameset/plaintext/xmp/noembed/noframes/listing are unsupported.

Bounds: body8MiB; 20,000 nodes/segments; depth128; 1,000 errors; Node30s and
128MiB old-space, not RSS; intermediate observation32MiB; 50,000 marker/segment hits;
final normative diagnostic4MiB. Over-limit/runtime/encoding failures stay inconclusive,
without fallback, partial success or inferred absence. Unavailable segments are null.
Diagnostic overflow retains a compact refusal plus original input. API network
guards are not OS isolation.

Owner-supplied references/markers may be inappropriate. No visibility, form state,
actual DOM, semantic truth/sufficiency, engine soft404, indexing or ranking follows.
A forbidden string split across segments may not be found despite visually contiguous
text. A02 alone never establishes whole-control C; A01 remains required.

## Qualification and migration / Qualification et migration

The [76 authored atomic cases](../tests/fixtures/identity-markers-v1.json) and
[eight authored bundle scenarios](../tests/fixtures/identity-markers-bundles-v1.json)
are distinct from real evidence. The prior 52-document experiment and its two
explicit oracle corrections remain retained in [provenance](../provenance/source-markers-v1.json).
See [draft.28 migration](migration-draft.28.md). / Cas rédigés distincts des preuves
réelles ; aucune intention humaine ou qualification Edikka créée par migration.

```sh
python3 scripts/identity_markers_check.py --node /path/to/node24 --output-dir new-qualification
TSEP_SOURCE_NODE=/path/to/node24 python3 adapters/captures.py input.json --output-dir new-bundle --assessor 'Assessor' --label 'Declared scope' --selection-method 'Prior selection' --access synthetic
```
