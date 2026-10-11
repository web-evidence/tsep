# Source-marker readings 1 / Lectures des marqueurs source 1

## Français

Expérience **facultative, non appliquée**, préparant la branche des marqueurs de
TS01-A02. **Draft.27, ses 12 contrôles exécutables et ses 33 règles restent
inchangés.** Aucun rapport historique ne sélectionne ce lecteur. Un résultat
expérimental `pass`, `fail` ou `inconclusive` n'est pas un verdict TS01.

### Ce que cette lecture apporte

Le lecteur historique refuse notamment un noscript non vide. La précédente
[proposition lexicale](proposals/noscript-consensus.md) conservait les fins de ligne
source exactes ; elle reste non appliquée. Cette expérience définit explicitement
une **autre interprétation : des segments de texte parsé**, chacun relié à un
intervalle continu du corps original. Elle ne prétend pas qualifier l'ancienne
proposition ni reproduire un navigateur.

Entrées : corps décompressé fourni, Content-Type HTML UTF-8 qualifié selon
l'[inventaire HTTP](source-http-inventory.md), Node 24 explicite et, facultativement,
deux listes littérales `required_markers` / `forbidden_markers`. Les chaînes sont
sensibles à la casse, sans normalisation des critères. Aucune intention réelle
préalable, complétude HTTP, origine ou pertinence de ces marqueurs n'est authentifiée.

Le parseur épinglé parse5 8.0.1 construit deux arbres du **document entier** :
scripting activé et désactivé. Aucun script ni ressource distante n'est exécuté.
Le contenu de noscript peut être brut dans une hypothèse et balisé dans l'autre.
Les arbres, erreurs signalées, valeurs, contextes et positions restent conservés.

Pour chaque lecture complète :

- retenir les textes HTML attribuables sous head/body, y compris title, textarea,
  toutes les options et les textes masqués ; aucune visibilité n'est déduite ;
- exclure commentaires, scripts et styles HTML/SVG, et contenus de template HTML
  inactifs ; les textes exclus restent présents dans l'observation ;
- ne pas fusionner des segments séparés par des balises ou commentaires :
  `Ex<b>pected</b>` n'établit pas le marqueur `Expected` ;
- vérifier chaque intervalle contre le texte parsé : CRLF et CR bruts deviennent
  LF **avant** expansion des références de caractères, sauf que les références ne
  sont pas développées dans le noscript brut ; conserver l'omission éventuelle du
  LF initial de pre/textarea ;
- comparer les marqueurs littéralement dans chaque segment, sans joindre plusieurs
  segments ni choisir une hypothèse différente pour chaque marqueur.

Deux lectures pass donnent un accord pass, deux fail un accord fail ; tout autre
couple donne inconclusive. Sans critères, chaque résultat et l'accord sont `null`.
Sans marqueur requis, l'absence des seuls interdits ne suffit pas à pass ; un
interdit présent reste fail dans une lecture complète. Un texte masqué, une valeur
de formulaire ou une chaîne dans noscript n'établit pas l'identité sémantique d'une
page : le sens et la suffisance du choix des marqueurs restent à justifier.

### Refus et limites

Le premier profil refuse toute **erreur rapportée par parse5**, tout arbre
incomplet, intervalle non attribuable, fusionné ou chevauchant, tout texte étranger
non blanc hors contexte exclu, les frames et contextes bruts non qualifiés, ainsi
que les templates shadow/streaming. Une erreur de projection rend toute la lecture
indisponible, y compris après une contradiction apparente ; aucun préfixe n'est
promu en décision. Les motifs restent visibles, les segments deviennent `null`.

L'absence d'erreur rapportée n'est **pas une preuve de validité HTML** : le cas
SVG avec sortie vers un paragraphe HTML est parsé sans erreur signalée dans la
version épinglée. Le texte de ce paragraphe n'est pas exclu comme du CSS. Les
critères contenant CR restent autorisés littéralement ; `&#13;` conserve CR dans
l'arbre mais provoque `control-character-reference`, donc cette projection reste
indisponible. Il ne faut ni remplacer ce CR par LF ni ignorer l'erreur pour passer.

Bornes héritées : corps 8 Mio, 20 000 nœuds, profondeur 128, 1 000 erreurs,
processus 30 secondes, V8 old-space 128 Mio (pas RSS), résultat complet 32 Mio.
Bornes propres : 20 000 segments, 64 marqueurs par liste, 4 096 caractères par
marqueur, 50 000 correspondances marqueur/segment. Seule la première occurrence
par segment est localisée ; ce n'est pas un décompte de toutes les occurrences.
Les offsets dans le texte parsé sont distincts des positions UTF-16 et octets
source. Le garde d'API réseau n'est pas une isolation système.

Un encodage/runtime indisponible ou un dépassement du superviseur rend toute
l'observation indisponible. Aucun lecteur lexical de secours ni conversion en
absence de marqueur. Le rejeu exige les mêmes octets, outils, critères, types et
résultat complet, y compris les versions d'exécution conservées.

### Preuves conservées

Deux jeux rédigés avant leurs implémentations figent **44 + 8 documents, 104
attentes de lecture**. Deux corrections séparées conservent les attentes initiales :
le CR numérique devait rester inconclusive à cause de l'erreur rapportée ; la
sortie SVG vers HTML devait conserver le paragraphe interdit, sans inventer une
erreur du parseur. La qualification r4 observe **104/104 accords corrigés,
100/104 accords initiaux et 52 rejeux exacts**, sous Node 24.19.0. Le jeu distribué
d'arbres réellement produits reste séparé des attentes rédigées. Ce sont des
documents synthétiques, sans observation navigateur.

Un diagnostic distinct retraite les captures historiques du 10 octobre 2026 de
l'accueil Edikka, de contact et de l'insight « seo-technique-fondations ». Les
corps sont vérifiés contre les chaînes HTTP conservées. Les six lectures finales
sont complètes, sans erreur parse5 rapportée, avec trois rejeux exacts. Le premier
essai de projection refusait les styles SVG ; cette observation et la correction
restent conservées. Aucun critère d'identité n'est fourni à ce diagnostic :
**aucun accord pass/fail, nouveau verdict TS01 ou contrôle global Edikka n'en
découle**. Ce n'est ni une collecte fraîche ni une intention antérieure aux captures.

```sh
python3 scripts/source_markers_check.py --node /path/to/node24 --output-dir new-qualification
python3 experiments/source_markers.py body.html --content-type 'text/html; charset=utf-8' --node /path/to/node24 --output new-observation.json
python3 experiments/source_markers.py body.html --content-type 'text/html; charset=utf-8' --node /path/to/node24 --criteria criteria.json --output new-comparison.json
python3 experiments/source_markers.py body.html --content-type 'text/html; charset=utf-8' --node /path/to/node24 --replay new-comparison.json --output new-replay.json
```

Avant intégration normative : version distincte, contrat et migration bilingues,
profil explicitement choisi avant capture, cas atomiques contradictoires et preuve
de conservation des anciennes décisions. Les priorités URL finale, référence
complète identique et stabilité exigée doivent être conservées. Cette expérience
n'active pas `identity_reader` dans le protocole et ne modifie aucun site.

## English

Optional, **unapplied** experiment 1 prepares TS01-A02's marker branch. Draft.27,
12 executable controls and 33 atomic rules remain unchanged. No historical bundle
selects this reader; candidate pass/fail/inconclusive is not a TS01 outcome.
The historical lexical noscript proposal remains unapplied. This experiment
explicitly uses parsed text with HTML input preprocessing, a different contract.
It neither qualifies the old lexical proposal nor establishes browser equivalence.

Inputs are supplied decompressed bytes, a qualified UTF-8 HTML Content-Type,
explicit Node 24 and optional literal required/forbidden lists. Prior real intent,
HTTP completeness/origin and semantic sufficiency are not authenticated. Pinned
parse5 8.0.1 constructs two whole-document static scripting hypotheses without
executing scripts or loading resources. Trees, reported errors, values, contexts
and source locations remain available.

Retain attributable HTML text under head/body, including title, textarea, every
option and hidden text. Exclude comments, HTML/SVG scripts/styles and inactive
HTML template content. Excluded text remains available. Do not join segments
across markup/comments. Each contiguous interval must explain the parsed text:
normalize raw CRLF/CR to LF before character-reference expansion; noscript RAWTEXT
does not expand references. Retain any initial LF omission in pre/textarea.
Marker strings themselves are never normalized, folded or combined across modes.

Both complete hypotheses pass gives candidate pass; both fail gives fail; all
other combinations are inconclusive. Missing criteria gives null. With no required
marker, absent forbidden markers cannot establish pass; a present forbidden marker
still fails a complete reading. Text visibility, form state, actual DOM, semantic
identity and marker sufficiency remain unassessed.

Any reported parse5 error, incomplete tree, unattributable/merged/overlapping span,
nonblank foreign text outside excluded contexts, frame/unsupported raw context,
declarative shadow or streaming template refuses the whole projection, even after
an apparent contradiction. No partial prefix becomes a decision; segments are
null with a reason. No reported errors does not prove valid HTML: the retained SVG
breakout case has no reported error and contains an HTML forbidden paragraph.
Literal CR criteria are allowed. Numeric &#13; preserves CR in the raw tree but
reports control-character-reference, so this first projection is unavailable.

Inherited bounds: body 8 MiB; 20,000 nodes; depth 128; 1,000 errors; 30 seconds;
128 MiB V8 old-space, not RSS; complete output 32 MiB. Projection bounds: 20,000
segments, 64 markers per list, 4,096 characters each, 50,000 marker/segment hits.
Only the first occurrence per segment is located. Parsed-text offsets, UTF-16
source positions and byte intervals are distinct. Network API guards are not OS
isolation. Runtime, decoding or supervisor failures make the observation unavailable,
without lexical fallback or inferred absence. Replay requires exact input bytes,
tools, criteria, content types and full result including retained runtime versions.

Two authored, prefrozen sets contain 44 + 8 documents and 104 expectations. Two
explicit amendments preserve their original expectations: numeric CR's reported
error, and SVG breakout's retained HTML paragraph without an invented parse error.
Qualification r4 observes 104/104 corrected matches, 100/104 original matches and
52 exact replays on Node 24.19.0. Actual retained parser inventories are distributed
separately from authored expectations. These are synthetic sources, not browser
observations. The commands above qualify, observe, compare or replay into new files.

Separate retrospective processing verifies three historical October 10 Edikka
bodies against their retained HTTP traces. All six final projections complete
without reported parse5 errors and all three replay exactly. The earlier SVG-style
refusal remains retained. No marker criteria were supplied: there is no candidate
pass/fail, new TS01 result, fresh capture, prior real intent or whole-site assessment.

Normative integration still requires a distinct version, bilingual contract and
migration, explicit pre-capture profile selection, contradictory atomic cases and
preservation of legacy outcomes. Final-URL, equal complete reference and required
stability precedence must remain. This experiment activates no identity_reader
protocol field and changes no website.

## Sources and provenance / Sources et provenance

[HTML input preprocessing](https://html.spec.whatwg.org/multipage/parsing.html#preprocessing-the-input-stream),
[noscript](https://html.spec.whatwg.org/multipage/scripting.html#the-noscript-element),
[numeric references](https://html.spec.whatwg.org/multipage/parsing.html#numeric-character-reference-end-state)
and [parse5 options](https://parse5.js.org/interfaces/parse5.ParserOptions.html)
inform parsing semantics, not the TSEP agreement policy or any SEO conclusion.
[Provenance](../provenance/source-markers-v1.json) retains dates, scopes, fingerprints,
oracle corrections and finite observations. Local captures and AI discussion are
not runtime dependencies, human review, endorsement or independent code audit.
