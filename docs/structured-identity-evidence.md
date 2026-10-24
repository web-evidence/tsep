# TS32 — declared JSON-LD identity corpus v1 / corpus d'identités JSON-LD déclaré v1

Prepared 2026-10-13 before reader implementation. Candidate draft.33; observed verification is recorded separately. TS31 visibility/type review stays separate.

## Français

Le premier profil semiAuto `jsonld-identity-corpus-v1` compare les identifiants dans
2–16 **exports JSON-LD fournis**, pas dans des pages ou navigateurs collectés par
l'interpréteur. L'unité est le corpus de graphes sélectionné ; l'URL cible en est
l'ancre documentaire, égale à la base du premier document. La complétude des
exports et leur lien aux sources sont fournis et revus, jamais authentifiés par
une empreinte. Le profil établit une cohérence des identifiants dans ce corpus et cette fenêtre ;
la stabilité temporelle, la résolution HTTP et l’identité réelle restent hors profil.

### Plan préalable

La cible contient identity_synthetic booléen, context (network/bounds/tool/
tool_version), observed_at, intent.declared_at et intent.structured_identity.
Ce dernier contient reader, selection_reason, population, window_start/window_end
(au plus 24 h, terminées à l'évaluation), `entities` et `documents`.

entities contient 1–64 objets {key,iri,reason}. Les clés sont uniques ; chaque clé
désigne une entité déclarée distincte. Les IRI attendues sont absolues HTTP(S),
fragment possible. Deux clés distinctes partageant la même IRI contredisent ce
registre. Les autres schémas d'IRI ne sont pas invalides : hors de ce premier profil.
Un entity doit être prévu dans au moins un document. Un seul constat reste étiqueté
comme tel, sans prétention de répétition observée.

documents contient 2–16 objets {id,base_iri,source,entities,auxiliary_ids,
external_refs}. source explique l'origine/portée de l'export ; entities nomme les
clés requises. auxiliary_ids contient des IRI secondaires explicitement justifiées
par {iri,reason}, sans revendication de stabilité entre documents. external_refs
contient les mêmes objets pour les références volontairement hors du corpus.
Les listes sont uniques et disjointes des identifiants requis. Les nœuds anonymes
auxiliaires restent propres au document ; deux étiquettes blank identiques dans
des documents distincts ne prouvent jamais une même entité.

identity_plan_review lie exactement {url,intent}. Elle est réalisée entre la
déclaration et le début de fenêtre, avec qualifications population, mapping et
references (supported/contradiction/unknown). Toutes les revues exigent complete,
reviewer, assistance, reason, observed_at, binding_sha256 et une provenance
human/human-assisted/synthetic-exercise cohérente avec identity_synthetic. Une vraie
revue manquante ne peut être remplacée par un jugement automatiquement rempli.

### Pièces natives et A02

identity_documents contient une pièce par id : {id,observed_at,raw_json,sha256,
contexts}. Le JSON natif strict, son empreinte et les contextes locaux suivent le
lecteur JSON-LD 1.1/jsonld.js 9.0.0 existant, sous Node 24 explicitement déclaré,
sans réseau ni contexte téléchargé. Date dans la fenêtre ; les limites natives
restent inchangées. Un document est traité indépendamment des autres. Aucune
fusion inter-documents ne masque les différences ; les nœuds anonymes gardent
leur portée locale. Graphes nommés, notices, graphes vides, syntaxe ambiguë, contexte
absent, erreur ou borne restent inconnus dans ce profil ; ce ne sont pas des preuves
d'instabilité. Maximum 256 nœuds aplatis par document.

Un nœud défini possède @id et au moins une autre entrée après aplatissement,
y compris @type seul ; une référence réduite à @id ne suffit pas.
A02 constate la présence d'un nœud défini sous chaque IRI requise, compare les
identifiants littéraux après expansion et inventorie les références. Une IRI requise
absente dans un graphe complet et non vide est une contradiction du plan fourni.
Une IRI non prévue ou une référence non résolue/non explicitement externe reste
inconclusive. Les références vers les nœuds définis connus du corpus sont résolues
documentairement ; les blank nodes uniquement dans leur document. Les littéraux
JSON @value ne sont jamais parcourus comme références. Les types de vocabulaire
ne sont pas des références d'entité à résoudre. Aucune URL n'est visitée.
Un document manquant n'efface pas une absence requise établie sur un autre graphe.

### A01, A03 et décision

A01 exige un registre cohérent et la revue préalable supported. Deux entités
déclarées distinctes partageant une IRI échouent même si une revue manque.

A03 exige une revue par document qualifié. Chaque entrée de identity_reviews
contient document_id, les métadonnées de revue, covered_nodes (empreintes de tous
les nœuds aplatis, exactement une fois), mapping, duplicate_qualification et
reference_meaning. La liaison porte sur {url,intent,document,graph}, avec le document
natif exact et le tableau flattened recalculé. Les qualifications couvrent le JSON
brut et les nœuds, y compris des déclarations réunies par le processeur sous un @id :
la fusion technique ne démontre ni doublon nuisible ni absence de collision réelle.
La revue qualifie les correspondances avec le registre, les répétitions légitimes
et les doublons injustifiés, ainsi que le sens des références. Une propriété ayant
plusieurs valeurs n'est pas automatiquement un défaut. Un jugement contradictoire
lié est conservé, y compris si une autre qualification ou pièce manque.

C requiert les trois règles sur le corpus entier déclaré. NC exige une contradiction
liée ; sinon NT. Pas de NA automatique, d'assimilation lexicale entre entités, de
normalisation d'URL ajoutée à JSON-LD, de validation Schema.org, de résultat enrichi,
d'indexation, de certification ou d'usage réel Edikka déduit.

## English

The first semiAuto `jsonld-identity-corpus-v1` profile compares 2–16 supplied JSON-LD
exports, not pages/browsers collected by the interpreter. Scope is the selected
graph corpus; target URL is a documentary anchor equal to the first document base.
Export completeness and source attribution are supplied/reviewed, not authenticated
by hashes. This profile establishes identifier coherence across this corpus/window;
temporal stability, HTTP resolution and real-world identity remain outside scope.
TS31 remains separate.

The target contains boolean identity_synthetic, context (network/bounds/tool/
tool_version), observed_at, intent.declared_at and intent.structured_identity. The
plan contains reader, selection_reason, population, window_start/window_end (at most
24 hours ending by assessment), entities and documents. entities has 1–64 distinct
{key,iri,reason} records, with expected absolute HTTP(S) IRIs, fragments allowed.
Two declared distinct keys sharing an IRI contradict this registry. Other IRI
schemes are outside this first profile, not invalid. Every registered entity must
be planned in a document; one observation is explicitly not observed repetition.

documents has 2–16 {id,base_iri,source,entities,auxiliary_ids,external_refs} records.
source describes export origin/scope; entities lists required registry keys.
auxiliary_ids lists justified {iri,reason} secondary IDs without cross-document
stability claims; external_refs lists intentional out-of-corpus references in the
same shape. Lists are unique/disjoint from required IDs. Auxiliary blank nodes
remain document-local; equal labels across documents never identify one entity.

identity_plan_review binds {url,intent}, between declaration and window start,
with population/mapping/references judgments (supported/contradiction/unknown).
All reviews require complete, reviewer, assistance, reason, observed_at, exact
binding_sha256 and human/human-assisted/synthetic-exercise provenance consistent
with the target. No human judgment is fabricated by the reader.

identity_documents contains exactly one {id,observed_at,raw_json,sha256,contexts}
record per planned ID. Dates must fit the window. The unchanged pinned offline
JSON-LD 1.1/jsonld.js 9.0.0 reader runs under explicit Node 24 with supplied local
contexts and native limits. Documents are processed independently, never merged
across the corpus. Named graphs, notices, empty graphs, ambiguous JSON, missing
contexts, errors/bounds remain unknown, not proof of unstable identity. Maximum
256 flattened nodes per document.

A defined node has @id and at least one other entry after flattening, including
@type alone; an @id-only reference is not a definition. A02 checks required
defined-node IDs after expansion and inventories references.
A required IRI missing in a complete nonempty graph contradicts the supplied plan.
Unplanned IDs and unresolved/non-explicitly-external references stay inconclusive.
References to known defined corpus nodes resolve documentarily, blank nodes only
inside their own document. JSON @value literals are not traversed as references;
vocabulary types are not entity references requiring resolution. No URL is fetched.
Independent known contradictions survive another missing document.

A01 requires a consistent registry and supported prior review. A known collision
between distinct declared registry entities fails even if a review is absent.

A03 requires one qualified review per processed document. identity_reviews records
contain document_id, review metadata, covered_nodes (every flattened-node digest
exactly once), mapping, duplicate_qualification and reference_meaning. Binding is
{url,intent,document,graph}, using exact native input and recomputed flattened graph.
Judgments cover raw JSON and all nodes, including descriptions technically merged
under one @id. Merging proves neither harmful duplication nor absence of real entity
collision. Reviews qualify registry mapping, legitimate repetition/unjustified
duplication and reference meaning. Multiple property values are not automatically
errors. Bound contradictions survive unrelated missing evidence/judgments.

All three rules are required for C across the declared corpus. Evidenced contradiction
gives NC, otherwise gaps remain NT. No automatic NA, lexical entity matching,
additional URL normalization, Schema.org validation, rich result, indexing,
certification or actual Edikka adoption is inferred.

## Primary references / références primaires

- [Schema.org data model](https://schema.org/docs/datamodel.html): identifiers, flexible types/properties and multiple values.
- [W3C JSON-LD 1.1](https://www.w3.org/TR/json-ld11/): node identifiers and document-scoped blank nodes.

Consulted/captured 2026-10-13, with fingerprints in `research/structured-identity-2026-10-13/provenance.json`.
TSEP requirements are editorial proposals, not endorsement by either publisher.
