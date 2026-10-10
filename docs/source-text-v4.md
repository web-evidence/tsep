# Source text v4 / Texte source v4

## Français

**Changement d’outil, protocole `0.1.0-draft.7` inchangé.** L’interpréteur 4 isole
l’extraction des marqueurs TS01-A02 dans `conformance/source_text.py`. Le parseur
Meta de TS07 et les règles TS10 ne changent pas. Ce composant interne n’est ni une
implémentation indépendante de TSEP ni un parseur HTML5 complet.

### Ce qui est évalué

La priorité reste : URL finale, égalité exacte de l’empreinte du corps décodé,
stabilité explicitement requise, puis marqueurs préalables. **À empreinte égale,
les marqueurs ne sont pas exécutés.** L’extracteur intervient seulement dans la
branche des marqueurs HTML UTF-8 ; text/plain reste le corps entier.

Les chaînes sont littérales et sensibles à la casse. Les références de caractères
sont décodées sans normaliser espaces, retours à la ligne ou Unicode. Le décodage
numérique conserve les contrôles et non-caractères que `html.unescape` supprimerait ;
NUL, substituts et points hors Unicode deviennent U+FFFD, et les remplacements C1
suivent la table HTML. Les balises/commentaires séparent les segments : on ne
reconstitue jamais un marqueur coupé par du balisage. Attributs, commentaires,
script et style sont exclus. Titre et texte caché par CSS peuvent compter ; aucune
visibilité, exécution JavaScript ou identité sémantique générale n’est établie.

Éléments ordinaires équilibrés, dont header/nav/main/section/article/aside/footer,
form/fieldset/legend/label/button, figure/details et éléments personnalisés :
frontières de segments. Éléments vides HTML : area/base/br/col/embed/hr/img/input/
link/meta/param/source/track/wbr. Le titre suit un état RCDATA : balises littérales
jusqu’à sa fermeture délimitée, références de caractères décodées. Script/style
s’arrêtent à leur première fermeture HTML délimitée, sans analyser JavaScript/CSS.

Icônes SVG sans texte : svg/g/path/rect/circle/ellipse/line/polyline/polygon/use/
symbol/defs/clipPath/mask/linearGradient/radialGradient/stop/animate/animateTransform/
set, avec balises équilibrées et autofermetures admises. Ce sous-ensemble ne prouve
ni rendu correct ni absence de texte dans le rendu de ressources référencées.

**Toute zone non prise en charge invalide toute l’extraction**, même après un
marqueur requis déjà trouvé : noscript/template/textarea non vides (seuls les
espaces ASCII sont admis), texte/titre/foreignObject/CDATA/script SVG, MathML,
table et descendants, select/option/optgroup, iframe et anciens contextes bruts,
script contenant `<!--`, commentaires ambigus, instructions de traitement,
déclarations autres que le doctype HTML simple, balises non fermées ou mal emboîtées,
attributs dupliqués/mal formés, NUL littéral et `<` littéral hors syntaxe acceptée.
Ce sont des limites de cet outil, pas des échecs SEO de la page. Le contrôle garde
NT si une observation nécessaire reste inconclusive. Pas de réparation d’arbre,
validation de tout HTML ni déduction de conformité globale.

Bornes : 8 Mio de caractères, 64 Kio par balise, profondeur 256, 100 000 unités de
balayage. Les limites HTTP/décompression préexistantes s’appliquent aussi. Un
dépassement rend l’extraction indéterminée. Les contextes exclus peuvent être
couverts dans une future version d’outil après de nouveaux cas contradictoires.

### Vérification et migration

96 cas synthétiques et 312 attentes externes de références de caractères ont été
figés avant l’implémentation (`tests/fixtures/source-text-freeze.sha256`). Les tests
comparent les segments exacts et les résultats atomiques, pas seulement un total.
Les 312 cas viennent de trois fichiers html5lib-tests : état DATA, sorties texte,
aucun état initial particulier ni balisage `<` littéral, erreurs limitées aux
points de contrôle et points-virgules manquants. Les autres exclusions figurent
dans la fixture. Cette sélection n’est pas une réussite du corpus HTML5 complet.

`python3 scripts/source_text_check.py` émet l’empreinte des résultats de cette
sélection, les versions Python et les empreintes de html/html.entities/html.parser.
`python3 scripts/verify.py` vérifie aussi le corpus normatif, les sorties TS07/TS10
antérieures, les limites, les cas loopback et l’archive reconstruite. Ne pas
confondre tests locaux observés et CI distante simplement préparée.

Adaptateur 4 → 5, collecteur 2 → 3, interpréteur 3 → 4. Entrée binaire 2, format de
paquet 1, intention guidée 2 et HTML 3 restent inchangés. `import.json` ajoute
`runtime` et l’empreinte du nouveau module. Les sources HTML Python sélectionnées
sont hachées avant/après évaluation ; `null` signifie source indisponible. Cela
n’authentifie ni l’exécution ni tout l’environnement Python. Le rejeu guidé exige
les mêmes sources et résultats, mais expose séparément `same_recorded_runtime`.

Conserver les anciennes captures, paquets et archives d’outils. Leur rejeu utilise
leur ancienne archive. Réévaluer avec l’adaptateur 5 produit **un nouveau paquet**
à partir de l’entrée exacte conservée ; annoncer le changement d’outil et comparer
l’empreinte d’entrée. Ne pas modifier les critères pour obtenir une réussite.
Une nouvelle collecte guidée exige sa propre référence/intention avec collecteur 3.
Une comparaison rétrospective ne devient pas une nouvelle collecte prospective.

## English

**Tool change; protocol `0.1.0-draft.7` remains unchanged.** Interpreter 4 isolates
TS01-A02 marker extraction in `conformance/source_text.py`. TS07's Meta parser and
TS10 rules do not change. This internal component is neither an independent TSEP
implementation nor a complete HTML5 parser.

Precedence is unchanged: final URL, exact decoded-body digest, explicitly required
stability, then prior markers. **Equal digest bypasses markers.** The extractor
only runs in the HTML UTF-8 marker branch; text/plain remains the entire body.
Strings are case-sensitive literals. Character references are decoded without
whitespace, newline or Unicode normalization. Numeric controls/noncharacters that
Python unescape drops are preserved; NUL, surrogates and overflow become U+FFFD,
with HTML C1 replacements retained. Markup/comments separate segments; no marker
is joined across them. Attributes, comments, script and style are excluded. Title
and CSS-hidden source text can count; no visibility, JavaScript execution or
general semantic identity is established.

Balanced ordinary elements, including modern structural/form elements and custom
elements, are segment boundaries. HTML void elements and the exact text-free SVG
icon allowlist are enumerated above and in the source. Title uses RCDATA: literal
markup until its delimiter-aware end tag, with character references decoded.
Script/style end at the first delimiter-aware HTML closing tag, without parsing
JavaScript/CSS. SVG references do not establish rendered output or its text.

Unsupported regions abort the **whole extraction**, including after a matching
marker: nonempty noscript/template/textarea (only ASCII whitespace permitted), SVG
text/title/foreignObject/CDATA/script, MathML, table and its descendants,
select/option/optgroup, iframe/legacy raw contexts, scripts containing `<!--`,
ambiguous comments, processing instructions, non-simple declarations, incomplete
or misnested tags, duplicate/malformed attributes, literal NUL and unsupported
literal `<`. These are tool limitations, not page SEO failures. A necessary
inconclusive observation leaves the control NT. No tree repair, full HTML validity
or global conformity claim. Bounds: 8 Mi characters, 64 Ki characters/tag, depth
256 and 100,000 scanning units; existing HTTP/decompression bounds also apply.

96 synthetic counterexamples and 312 upstream character-reference expectations
were frozen before implementation. Exact segments and outcomes are checked. The
upstream selection uses DATA text cases, no special initial state or literal `<`,
and only specified parse errors/exclusions; it is not full HTML5 conformance.
`python3 scripts/source_text_check.py` fingerprints selected results and records
Python/html/html.entities/html.parser identities. `python3 scripts/verify.py`
also checks normative cases, unchanged TS07/TS10 outputs, bounds, loopback and
archive reconstruction. Prepared CI is not an observed remote run.

Adapter 4 → 5, collector 2 → 3, interpreter 3 → 4. Binary input 2, bundle format 1,
guided intent 2 and HTML 3 stay unchanged. `import.json` adds `runtime` and the new
module fingerprint. Selected Python HTML sources are hashed before/after
interpretation; null means unavailable. This is not execution/environment
authentication. Guided replay requires identical tool sources and outcomes while
separately disclosing `same_recorded_runtime`.

Keep original captures, bundles and tool archives; replay each with its own tools.
Re-evaluation with adapter 5 creates a **new bundle** from the exact retained input.
Disclose the changed tools and compare input hashes; do not retune criteria for a
pass. New guided collection requires a collector 3 reference/intent. Retrospective
comparison does not become a new prospective collection.

## Sources observées / Observed sources — 2026-10-10 UTC

Primary reading: [WHATWG tokenization](https://html.spec.whatwg.org/multipage/parsing.html#tokenization)
(04:42:32Z; page SHA-256 `34e193906e6898ae7faf576a8d4c0f8de619a86ec99d85a3baeb2713171f1dbf`)
and [Python HTMLParser](https://docs.python.org/3/library/html.parser.html)
(04:42:33Z; SHA-256 `b76c68e45978a82e2df4f0583ad1191e560e1c303a5a613af475cad7903649a2`).
Scope: lexical states, character references and Python callback behavior only.
Dated full-page captures and their URL/hash inventory are retained in the local
working evidence, not required at runtime and not redistributed with the tools.

External expectations: [html5lib-tests tokenizer at immutable commit
c777c408](https://github.com/html5lib/html5lib-tests/tree/c777c408b61078ea2eb4acefc2535f54dbc8b28a/tokenizer),
observed 04:44:08–09Z. Original file URLs and SHA-256 values are included in
`tests/fixtures/html5-character-cases.json`; selected input/output pairs are
unchanged. [MIT license](../licenses/html5lib-tests.txt) and attribution retained.
These expected strings are independent of the new extractor; selection and the
96 synthetic cases were prepared internally. This is not a third-party review.

Lecture primaire limitée aux états lexicaux, références de caractères et rappels
Python. Captures datées complètes et inventaire URL/empreinte conservés dans les
preuves locales, sans dépendance privée pour l’exécution des outils. La sélection
html5lib conserve entrées/sorties, URL immuables, empreintes et licence MIT. Les
attentes externes sont indépendantes du nouvel extracteur ; la sélection et les
96 cas synthétiques sont internes. Aucune relecture externe n’est revendiquée.
