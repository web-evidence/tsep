# Noscript experiment 4 / Expérience noscript 4

**UNAPPLIED / NON APPLIQUÉE.** This tool tests a proposal; it cannot emit a TSEP
report, replace an assessment or alter the active `0.1.0-draft.7` contract.
It is separate from interpreter 5, the adapter, collector and campaign diagnostic.

Version 2 corrects experiment 1's overbroad list-item refusal: a nested ul/ol/menu
starts a new item scope. Six additional synthetic expectations were frozen before
the fix; the initial 68 expectations and v1 observations are preserved. This is
an experimental coverage correction, with no normative effect. / La version 2
corrige le refus excessif des listes imbriquées : ul/ol/menu ouvre une portée
distincte pour les li. Six cas supplémentaires ont été figés avant ce correctif,
après constat sur captures conservées ; les 68 attentes et résultats v1 restent
conservés. Ce changement ne produit aucun effet normatif.

Version 3 adds a strict select/optgroup/option subset and **literally empty**
textarea. All option text counts, including disabled/unselected options; label/value
attributes do not. Comments split segments; NBSP stays distinct. The 96 additional
cases were frozen before code. The v1/v2 fixture files remain byte-identical; the
v3 fixture records one explicit v1 expectation delta (`select`). No normative effect.

La version 3 ajoute select/optgroup/option bornés et textarea **littéralement vide**.
Le texte de toute option compte, même désactivée/non sélectionnée ; pas label/value.
Les commentaires séparent les segments ; NBSP reste distinct. 96 cas figés avant
code ; fichiers v1/v2 intacts, un écart v1 explicite (`select`) dans le fichier v3.

Version 4 adds [explicit tables](table-experiment-v4.md), with 103 expectations
frozen before implementation. Direct rows, nested tables, fostered text and missing
closes remain refused. The only new prior expectation delta is an empty table
after select; the original direct-row table case stays inconclusive.

La version 4 ajoute les [tableaux explicites](table-experiment-v4.md) : 103 cas
figés avant code, un seul écart d'attente antérieure et aucune modification du
protocole actif. Les réparations d'arbre ne sont pas ajoutées.

## Français

### Objectif et entrée

Éprouver la [proposition de concordance](proposals/noscript-consensus.md) sur des
documents entiers, avec deux hypothèses globales. Entrée : un fichier HTML UTF-8
intégral, jamais une tranche découpée autour de noscript ; facultativement un JSON
contenant exactement `required_markers` et `forbidden_markers`. Ces critères sont
expérimentaux. Leur fourniture après une capture ne crée pas une intention préalable.

```sh
python3 experiments/noscript.py source.html --criteria criteria.json --output experiment.json
```

La sortie doit être nouvelle. Sans `--criteria`, seule la disponibilité des deux
lectures est mesurée : `candidate_consensus` vaut null, jamais pass implicite.
L’outil ne lit pas de rapport TSEP, ne valide pas HTTP, ne compare pas les URL ou
empreintes de référence et n’exécute ni réseau, ni CSS, ni JavaScript.

### Frontières lexicales de cette expérience

Le prototype exige une racine html unique, un head puis un body explicites et
uniques, ainsi que toutes les fermetures. Les balises doivent être correctement
imbriquées ; aucune correction d’arbre n’est effectuée. La liste positive des
éléments admis est publiée dans `experiments/noscript.py` (`HEAD`, `HEAD_NOSCRIPT`,
`BODY`, `SVG`). Elle est plus restrictive que l’extracteur actif sur certains cas.
Une lecture dite complète signifie uniquement que **toute la source a été traitée
dans ce sous-ensemble lexical**. Ce n’est pas une certification de conformité HTML5,
une construction de DOM, ni une garantie sur les réparations d’un navigateur.

- Hypothèse activée : noscript utilise un état brut jusqu’au premier délimiteur
  de fermeture approprié, même si celui-ci apparaît dans une pseudo-valeur
  d’attribut, un pseudo-commentaire ou du code. Tout son contenu compte comme texte
  littéral, sans décodage des références de caractères. La suite du document est
  ensuite analysée dans la même hypothèse globale.
- Hypothèse désactivée : le contenu de noscript est analysé comme du balisage.
  Dans head, seuls espaces HTML, commentaires et link/meta/style sont admis.
  Un autre contenu, un noscript imbriqué ou une situation nécessitant un
  retraitement de jeton refuse la lecture. Dans body, les limites ordinaires
  du prototype s’appliquent. Les attributs et commentaires ne deviennent pas du texte.
- Les textes DATA et title décodent les références de caractères. Script/style
  sont exclus. Le sous-ensemble SVG conserve les limites de style de l’interpréteur 5.
- Aucun assemblage à travers balise/commentaire, aucune normalisation des espaces,
  CRLF, Unicode ou casse. Ce choix conserve le contrat de texte source de TSEP et
  **diffère du prétraitement HTML5 des fins de ligne**. Les lectures ne sont donc
  pas présentées comme deux sorties exactes d’un navigateur.
  Le saut de ligne initial de pre est lui aussi conservé. Les gardes de fermeture
  implicite ne constituent pas une implémentation exhaustive des règles d’arbre :
  par exemple p/li et p/summary correctement imbriqués lexicalement peuvent être
  acceptés même lorsqu’un navigateur réorganiserait les éléments.
- Select : option directement sous select/optgroup ; optgroup directement sous
  select. Seulement des blancs HTML littéraux entre ces éléments ; références de
  caractères à cet endroit, texte non blanc, fermeture implicite, select imbriqué,
  datalist et tout enfant complexe (y compris hr/script/template/button) sont refusés.
  Option contient seulement du texte et des commentaires, sans enfant élément.
  Les mêmes règles s'appliquent sous noscript désactivé ; sous noscript activé,
  son contenu reste intégralement brut. Aucune lecture de la valeur sélectionnée.
- Textarea : zéro caractère brut entre ouverture et fermeture explicites. Espace,
  saut de ligne, entité ou commentaire à l'intérieur refuse la lecture entière.
  Cette borne est volontairement plus stricte que l'interpréteur actif ; aucun
  comportement RCDATA non vide ou saut de ligne initial n'est ajouté.
- Tableaux hors du [sous-ensemble explicite v4](table-experiment-v4.md), iframe, textarea non vide, template, MathML, autres contextes
  non listés, déclarations ambiguës, script échappé, doublons d’attributs et certaines
  fermetures implicites (p, a, form, button, listes, titres) sont refusés.
- Bornes : 8 388 608 caractères Unicode, 100 000 étapes de scan, profondeur 256,
  balise limitée par le lecteur commun à 65 536 caractères. Les critères admettent
  au plus 64 marqueurs par liste et 4 096 caractères par marqueur. Une borne atteinte
  empêche toute utilisation du préfixe extrait.

### Preuves et règle candidate

Chaque lecture complète conserve ses segments avec début inclusif et fin exclusive
dans la source originale, mesurés en **caractères Unicode Python**, pas en octets
UTF-8 ni en positions DOM. Le texte décodé et son mode de décodage sont conservés.
Une correspondance indique l’indice du segment et la première position du marqueur
dans son texte décodé ; elle ne prétend pas fournir une bijection caractère/octet
après décodage d’entités. L’empreinte UTF-8 du corps complet reste distincte.

Les listes doivent être uniques, non blanches, sans interdit inclus dans un requis.
Sur une lecture complète : requis manquant ou interdit présent donne un candidat
fail ; tous les requis présents et interdits absents donnent pass s’il existe au
moins un requis ; sinon inconclusive. Les raisons et correspondances de chaque
lecture sont conservées.

Deux candidats pass donnent un consensus candidat pass ; deux fail donnent fail,
même pour des raisons différentes. Toute autre combinaison donne inconclusive,
y compris fail avec une lecture incomplète. Pas d’union des marqueurs entre modes,
pas de choix favorable par élément. Une lecture refusée rend **zéro segment** et
indique le motif et la position du contexte de refus ; cette position ne prétend
pas localiser exactement tous les caractères responsables.

La sortie contient `kind: unapplied-noscript-experiment`, `normative_effect: none`,
version de l’expérience, empreinte du corps, empreintes des dépendances locales
utilisées et identité de runtime. Ces empreintes ne sont pas une authentification
de l’exécution. Les segments peuvent reproduire des données privées : traiter la
sortie selon les mêmes règles d’accès que la source.

### Tests, migration et décision

68 documents synthétiques et leurs segments/résultats attendus par mode ont été
figés avant le code, avec une empreinte séparée. Les attentes ont été rédigées par
l’auteur, pas obtenues d’un navigateur ou d’une relecture indépendante. Elles
couvrent attributs, entités, commentaires, CSS, contextes head/body, délimiteurs
piégés, plusieurs noscript, résultats divergents et refus après un préfixe.
Les tests supplémentaires vérifient positions Unicode, limites, absence de verdict
sans critères, isolation du CLI et conservation du refus de l’extracteur actif.

Aucune migration de rapport : les anciens paquets, outils et verdicts restent
inchangés. Cette expérience ne débloque pas normativement Edikka. Une promotion
exigerait une version normative distincte, contrats/source bilingues, migration,
preuves intégrées et cas de conformance contradictoires. Avant cela, la portée des
lectures doit être revue : le prototype est lexical et ne démontre pas toutes les
règles de construction d’arbre HTML5. Une concordance expérimentale seule ne
justifie pas cette promotion.

## English

Experiment 4 takes a complete UTF-8 HTML source and optional exact marker lists.
It applies enabled and disabled scripting hypotheses to the entire unchanged
document. Enabled noscript is literal RAWTEXT; disabled noscript is tokenized,
with a head subset limited to HTML whitespace, comments, link/meta/style. Trapped
closing delimiters affect the rest of each whole-document reading. No partial
prefix can establish a candidate result.

This is a bounded lexical experiment, **not two certified HTML5/browser parses**.
It requires explicit, unique html/head/body and balanced supported tags. Positive
element lists and recovery guards are in the source. Tables outside the [explicit v4 subset](table-experiment-v4.md),
iframe, nonempty textarea, template, foreign content and ambiguous structures refuse the
whole reading. Existing SVG-style bounds are retained. Character references are
decoded in DATA/title and left literal in enabled noscript. Script/style and
comments are excluded when parsed as such. No joining across markup or normalization
of spaces, Unicode, case or CRLF; preserved line endings differ from HTML5 input
preprocessing. Bounds: 8 Mi Unicode characters, 100,000 scan steps, depth 256,
65,536-character tags; at most 64 markers per list, 4,096 characters each.

Complete readings retain source ranges in zero-based Unicode code points (exclusive
end), decoded text and decoding mode. Marker evidence identifies the first match
per segment in decoded-text coordinates, not a decoded-to-source byte mapping.
Refusals retain no prefix segments, only a reason/context offset. Full source hash,
selected tool source hashes and runtime identity are recorded separately.

Each complete reading proposes pass/fail/inconclusive under the existing literal
marker criteria. Both pass proposes pass; both fail proposes fail with separate
reasons; everything else is inconclusive, including failure plus an incomplete
reading. No cross-mode union or per-element choice. Without criteria the candidate
consensus is null. This tool does not validate HTTP, intent, URL/digest precedence,
DOM visibility or semantic identity; it emits no TSEP verdict. Criteria supplied
retrospectively do not become prospective intent. Output can contain private source
text and must retain the source's access restrictions.

68 authored synthetic cases were frozen before implementation; they are neither
normative conformance cases nor an independent browser oracle. CLI isolation,
source offsets, bounds and the unchanged active extractor are checked separately.
Draft.7, interpreter 5, collectors, adapters and existing reports remain unchanged.
No report migration applies. Any future normative promotion requires a distinct
version, bilingual contracts/source, migration and contradictory conformance cases,
plus a justified boundary for HTML tree-processing behavior. Experimental agreement
alone is insufficient.
The initial newline in pre is also preserved. Implicit-closing guards are not a
complete tree builder: lexically balanced p/li and p/summary may be accepted even
when a browser would reorganize those elements, without establishing DOM agreement.

### Version 3 scope and migration

Only direct option/optgroup children of select, and direct option children of
optgroup, are supported. Between choices, only literal HTML whitespace is admitted
(no encoded whitespace). Options have text/comments only. Complex children,
including hr/script/template/button, omitted closes, nesting and datalist contexts
are refused. All option text counts regardless of selection/disabled state;
attributes never contribute. Global noscript modes continue across this subset.
Textarea must have exactly zero raw characters between explicit tags: whitespace,
entities and comments inside it remain unsupported. No nonempty RCDATA extension.

For the experiment CLI, migrate by using version 3 and its new source hashes.
Keep v1/v2 tools and outputs for their original expectations. V3 retains the 68
initial and six list cases, adds 96 cases, and explicitly supersedes only the
initial `select` case's disabled reading and resulting candidate agreement. No
frozen fixture is rewritten. Experimental coverage does not migrate TSEP reports.

### Differential reference / Référence différentielle

A separate private runner compared unchanged synthetic inputs with **html5lib 1.1**,
loading pinned official PyPI wheels locally (html5lib 1.1, six 1.17.0,
webencodings 0.5.1). They are not dependencies of this tool or its distribution.
It independently projects text from the returned tree, excluding comments and
script/style, without normalizing or aligning segments to our reader. Both scripting
modes are compared, including all refusals and differences. This historical parser
is not a contemporary browser, and its projection is authored for this experiment.
It does not establish current customizable-select behavior or independent review.

Un lecteur externe historique est comparé aux mêmes sources synthétiques, dans les
deux modes. Tous les écarts restent visibles. La projection de son arbre n'est pas
le contrat de segments source TSEP : notamment CRLF devient LF en HTML5, ce qui peut
changer un résultat de marqueur exact. Les lectures refusées ne comptent jamais
comme accords. Une telle comparaison est une preuve différentielle limitée ; elle
ne suffit pas à promouvoir la proposition ni à revendiquer deux lectures navigateur.
Les résultats datés et empreintes appartiennent au dossier privé de l'exécution,
pas à une certification du protocole.

## Sources

The [noscript element](https://html.spec.whatwg.org/multipage/scripting.html#the-noscript-element)
and [head-noscript parsing rules](https://html.spec.whatwg.org/multipage/parsing.html#parsing-main-inheadnoscript)
inform the two hypotheses; consensus is a TSEP proposal, not a WHATWG requirement.
Full dated captures retained on 2026-10-10 at 06:00:57–58 UTC, SHA-256:
`7629c8213a7f5175d444f5a0eda1fcfb8c61f1eb2a21525ec174d79b0eb69529`
(scripting) and `34e193906e6898ae7faf576a8d4c0f8de619a86ec99d85a3baeb2713171f1dbf`
(parsing). These are the retained references used for this implementation's scope.

The [select, option and textarea definitions](https://html.spec.whatwg.org/multipage/form-elements.html)
were captured on 2026-10-10 at 06:13:28 UTC, SHA-256
`26b487a39e8c9b2a8db51643dbee4c253c91819c3067608495c9366aa6788da2`.
[html5lib parse documentation](https://html5lib.readthedocs.io/en/latest/html5lib.html)
was read on the same date; its direct archive request returned HTTP 403 (no bypass).
Official PyPI metadata and wheels are retained with URL/date/fingerprints in the
private differential-reference evidence. Neither source prescribes TSEP consensus.
