# 0.3.0-draft.7 — texte HTML principal / main-document HTML text

## Français

Candidate distincte, non publiée. Seul TS01 passe à la version de règle draft.7 ;
TS02 reste draft.6 et les 42 autres contrôles conservent leur version. Toujours
44 contrôles, 98 règles. Ce document n'atteste pas une qualification réussie.

Le nouveau profil préalable `html-tree-markers-v3` compare uniquement les segments
HTML attribuables du document principal. Les profils v1, v2 et lexical restent
sélectionnables avec leur sémantique antérieure ; aucune intention ni pièce ne
migre. Adoption : nouveau dossier, référence et critères explicitement confirmés.
Les priorités URL, empreinte du corps complet et stabilité restent inchangées.

V3 exclut noscript, iframe et tout sous-arbre étranger (SVG, MathML, y compris
foreignObject) avant la projection. Chaque texte exclu conserve contexte, texte
et intervalle source exact. Un requis uniquement dans une exclusion ne satisfait
jamais le critère. Si un interdit est retrouvé dans ces exclusions, une lecture
qui aurait réussi devient inconclusive, avec les correspondances exclues ; une
contradiction dans le texte principal reste fail. Aucun segment n'est concaténé
pour chercher un marqueur. Le contenu src/srcdoc d'un iframe, les ressources
object/embed, CSS, rendu, visibilité et JavaScript ne sont pas évalués. Une absence
de correspondance dans le texte principal ne prouve pas une absence à l'écran.

Seule l'erreur parse5 `duplicate-attribute` est admise, avec positions conservées
et première valeur dans l'arbre du parseur figé. Aucune vérité sur un attribut,
une canonical ou une directive ne découle de ce profil ; TS07 et ses lecteurs
restent inchangés. Toutes les autres erreurs restent inconclusives, y compris
le pixel img dans noscript sous head qui restructure le document en mode disabled.
Les deux hypothèses sont statiques ; aucune ne simule un navigateur sans JavaScript.

Des espaces ASCII fusionnés autour de fermetures ignorées sont exclus seulement
si retirer des balises de fin span restitue exactement le texte parsé après
normalisation CRLF/CR. Les intervalles originaux sont conservés. Aucun texte
significatif, NBSP, balise ouvrante ou ambiguïté n'est ainsi accepté. Les bornes,
reconstruction, chevauchements et refus de dépassement des profils restent actifs.
Une capture réelle lue n'est ni une revue humaine ni un contrôle global C.

## English

Distinct unpublished candidate. Only TS01 becomes rule draft.7; TS02 remains
draft.6, with the other 42 controls unchanged. Still 44 controls and 98 rules.
This document does not establish successful qualification.

The prior `html-tree-markers-v3` profile compares attributable main-document HTML
segments only. V1, v2 and lexical profiles retain their semantics; no intent or
piece migrates. Adoption requires a new dossier, reference and explicit criteria.
Final URL, complete-body digest and stable-representation priorities are unchanged.

V3 excludes noscript, iframe and all foreign subtrees (SVG/MathML, including
foreignObject) before projection. Excluded text retains its context, parsed text
and exact original interval. A required marker only there cannot match. An
excluded forbidden marker changes an otherwise passing reading to inconclusive,
with explicit matches; a main-document contradiction remains fail. Segments are
never concatenated for matching. Embedded src/srcdoc documents, object/embed
resources, CSS, rendering, visibility and JavaScript are not assessed. Absence in
main-document text does not establish absence on screen.

Only parse5's `duplicate-attribute` error is admitted, retaining positions and
the pinned parser's first attribute value. This profile establishes no attribute,
canonical or directive fact; TS07 readers are unchanged. All other errors remain
inconclusive, including a head noscript img pixel restructuring the disabled tree.
Both hypotheses are static, neither simulates a browser without JavaScript.

ASCII whitespace merged across ignored closing tags is excluded only if removing
plain span end tags exactly reconstructs parsed text after CRLF/CR preprocessing.
Original intervals remain. Significant text, NBSP, start tags and ambiguity are
not admitted by this exception. Bounds, reconstruction, overlap checks and refusal
on overflow remain active. Reading a real capture is neither a human review nor
a whole-control C result.

## Conservation des diagnostics / Diagnostic storage

FR : V3 stocke sans perte les listes segments/exclusions/contextes en JSON UTF-8
compressé zlib puis base64. Avant admission, expansion intégrale comparée à la
projection native : longueur (32 Mio maximum par hypothèse), SHA-256, fin de flux
et absence d'octets résiduels obligatoires. Diagnostic final toujours limité à
4 Mio ; observation intermédiaire Python v3 à 64 Mio, parseur à 32 Mio. Les versions
zlib de compilation et d'exécution sont consignées et doivent être disponibles
pour un rejeu exactement identique. Les profils antérieurs restent inchangés.

EN: V3 losslessly stores segments/exclusions/contexts as UTF-8 JSON, zlib and
base64. Admission fully expands and compares it with the native projection:
exact length (32 MiB per hypothesis), SHA-256, end of stream and no remaining
bytes required. Final diagnostics remain capped at 4 MiB; V3's Python intermediate
observation at 64 MiB, parser at 32 MiB. Build/runtime zlib versions are recorded
and required for byte-identical replay. Earlier profiles are unchanged.

Parser evidence / Preuve parseur : parse5 8.0.1 `genericEndTagInBody` breaks on a special ancestor without calling the error callback when an unmatched span end tag is ignored. No reported error is removed. / La branche ignore cette fermeture sans callback ; aucune erreur rapportée n’est supprimée. V3 limits this whitespace exception to span; a real div/p closure still splits distinct nodes.

## UTF-8 déclaré dans le document / UTF-8 declared by the document

FR : Pour le seul en-tête HTTP text/html sans paramètre, V3 admet des octets UTF-8
stricts si un BOM UTF-8 existe ou si chaque arbre attribue exactement une meta
charset UTF-8 complète dans les 1024 premiers octets. Positions et balise originale
sont conservées à côté de l'en-tête HTTP inchangé et du décodage effectif. Autre
charset, doublon d'attribut sur cette meta, déclaration http-equiv charset, meta
absente/tardive/ambiguë : refus. Une chaîne meta dans un commentaire ne suffit pas.
Référence : https://html.spec.whatwg.org/multipage/semantics.html#charset .

EN: For HTTP text/html without parameters only, V3 admits strictly valid UTF-8
bytes with a UTF-8 BOM or exactly one complete early UTF-8 meta charset element
attributed in each tree within the first 1024 bytes. Its original tag and intervals,
unchanged HTTP header and effective decoding are retained. Other charsets, duplicate
attributes on that declaration, http-equiv charset, missing/late/ambiguous meta
are refused. A meta-looking string inside a comment is insufficient.

FR/EN : Les deux index de corpus portent la nouvelle version ; tous leurs cas, attentes et empreintes annexes restent identiques, vérifiés par une empreinte excluant seulement protocol_version. / Both corpus indexes name the new version; all cases, expectations and additional hashes remain identical, checked with a digest excluding only protocol_version.
