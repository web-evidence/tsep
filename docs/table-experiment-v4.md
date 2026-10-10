# Explicit tables / Tableaux explicites — experiment 4

**UNAPPLIED / NON APPLIQUÉ.** Extension of the isolated lexical experiment,
not a TSEP rule, browser parser or report verdict. Draft.7 and interpreter5 stay
unchanged. The two global noscript hypotheses and all earlier limits still apply.

## Français

### Finalité et périmètre

Lire intégralement davantage de sources contenant des tableaux, tout en refusant
les constructions hors périmètre. Edikka est un terrain de réapplication de
captures conservées ; la disponibilité du lecteur n'est pas un audit SEO, une
identité de page démontrée ou une conformité globale. La finalité reste une chaîne
critères préalables → captures → contrôle borné → preuves rejouables. Cette brique
n'ajoute pas de critères rétrospectifs aux captures et ne produit aucun verdict réel.

### Entrées, attentes et limites

L'entrée reste un document UTF-8 entier, avec html/head/body explicites. Les
positions, marqueurs, exclusions et bornes sont ceux de l'[expérience](noscript-experiment.md).
Dans le mode où il est analysé comme balisage, un tableau respecte ces limites :

- Un caption facultatif en premier, puis zéro ou plusieurs colgroup, un thead
  facultatif, zéro ou plusieurs tbody, enfin un tfoot facultatif. Un tableau vide
  est accepté. L'ordre est une restriction de l'outil, pas une règle nouvelle TSEP.
- col seulement sous colgroup ; tr seulement sous thead/tbody/tfoot ; td/th
  seulement sous tr. Toutes les fermetures non void sont explicites et équilibrées.
  Un tr directement sous table reste refusé : l'outil n'insère pas de tbody.
- Table, colgroup, thead, tbody, tfoot et tr admettent seulement leurs enfants
  structurels directs, des commentaires non ambigus et des blancs HTML littéraux.
  Un texte déplacé, même un requis déjà reconnu ailleurs, refuse le document entier.
  Une référence de caractères encodant un espace y reste hors périmètre.
- Caption et cellules admettent les descendants ordinaires déjà pris en charge.
  Script/style y restent exclus du texte, les attributs n'y contribuent pas, les
  cellules/commentaires/balises ne sont jamais concaténés pour créer un marqueur.
  colspan, rowspan, scope, hidden ou CSS ne modifient pas cette lecture textuelle.
- Les tableaux imbriqués, même en cellule/caption, sont refusés. Aucun placement
  automatique hors du tableau (foster parenting), fermeture implicite ou reprise
  d'arbre HTML5. Table dans un p ouvert est refusé. Aucun calcul de grille,
  d'association des en-têtes, d'accessibilité ou de visibilité.
- Noscript activé reste brut : les pseudo-balises de son contenu ne sont pas des
  tableaux analysés. Noscript désactivé applique le même sous-ensemble au document
  entier. Un désaccord ou un mode refusé conserve le consensus indéterminé.

L'outil conserve les segments seulement si la lecture entière aboutit. Le succès
sur une cellule, un tableau ou un préfixe ne suffit jamais. Les segments gardent
leurs positions source Unicode ; aucune normalisation de CRLF, espaces ou casse.

### Cas, preuves et migration

103 cas synthétiques ont été rédigés et figés avant le code : texte présent/absent/
interdit, attributs, séparation entre cellules, entités, caption, colonnes, sections,
ordre, fermetures, texte déplacé, imbrication, contextes étrangers, noscript et refus
tardif après un marqueur. Ce sont des attentes rédigées, pas une validation humaine.

Les 68 + 6 + 96 cas antérieurs restent conservés octet pour octet. Le fichier v4
contient les empreintes de ces fichiers et un seul changement d'attente v3 : un
**tableau vide après select** devient lisible. Le cas initial table/tr/td sans
section explicite reste indéterminé. Ne pas relire les anciens résultats comme
s'ils avaient été produits par v4 ; conserver leurs outils et empreintes.

Pour le CLI expérimental, utiliser la version4 et enregistrer ses nouvelles
empreintes. Aucune migration de rapports TSEP ni réévaluation normative n'est
introduite. La comparaison différentielle avec html5lib1.1 reste une référence
historique limitée ; ses écarts sont conservés sans aligner les sorties pour créer
un accord. Les observations de captures et vérifications appartiennent à leurs
exécutions datées, pas à une promesse générale de conformité HTML5.

## English

Version4 extends the isolated whole-source reader with explicit table structure.
This supports source-text experiments, not SEO assessment, DOM equivalence, page
identity or a normative TSEP result. Inputs, bounds, Unicode source ranges,
criteria validation, global noscript modes and whole-reading refusal are unchanged.

Supported order: optional first caption, column groups, optional head, body groups,
optional last foot. Empty tables are accepted. Only col under colgroup, tr under
explicit thead/tbody/tfoot, and td/th under tr are supported. All non-void tags must
be explicitly balanced. Containers allow their structural children, unambiguous
comments and literal HTML whitespace only; encoded whitespace is outside scope.
Caption/cells allow ordinary supported content. Attributes, script/style and
comments do not contribute text, and markup/cell boundaries never join segments.
No grid, header-association, span, accessibility, CSS or visibility assessment.

Direct rows requiring implicit tbody, nested tables, fostered text, omitted closes,
unsupported section order, and table inside open p are refused. Enabled noscript
keeps its contents literal; disabled noscript applies the same table subset. A
partial prefix or one completed mode never resolves the candidate consensus.

103 authored counterexamples were frozen before implementation. Prior 68+6+96
fixture files remain byte-identical. The v4 fixture records their hashes and one
explicit v3 delta: an empty table after select becomes readable. The original
noscript table with a direct tr stays inconclusive. Preserve v1–v3 tools/results.
Use the v4 experimental CLI and its source hashes for new experiments; no protocol
or report migration applies. A separately loaded historical html5lib1.1 comparison
is limited differential evidence, not a current browser or independent human review.

## Primary references / Références primaires

[Tables](https://html.spec.whatwg.org/multipage/tables.html) and
[table parsing](https://html.spec.whatwg.org/multipage/parsing.html#parsing-main-intable)
were retained on 2026-10-10 at 07:30:10–12 UTC. SHA-256 respectively:
`769e9afab8720b2c762fbe060ae2b5a15bfe84e202f7a043414e732cf9ff910a` and
`34e193906e6898ae7faf576a8d4c0f8de619a86ec99d85a3baeb2713171f1dbf`.
They document browser behavior. The stricter subset above is an experimental tool
boundary, not an attribution of that subset or TSEP consensus to WHATWG.
