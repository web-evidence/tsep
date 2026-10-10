# Source text v5 / Texte source v5

## Français

**Interpréteur 5, adaptateur 6, collecteur 5 ; protocole `0.1.0-draft.7` inchangé.**
Cette extension traite un sous-ensemble de `style` dans les icônes SVG du HTML
UTF-8. Elle applique l’exclusion du contenu des styles déjà prévue au contrat.
Les autres limites de [v4](source-text-v4.md) restent applicables. Aucun rendu,
JavaScript, chargement de ressource ou contrôle de validité CSS n’est effectué.

### Périmètre et contradictions

Dans un SVG du sous-ensemble déjà admis, à l’intérieur d’un `body` explicite et
hors `head`, `style` peut être vide, autofermé ou contenir des caractères sans
aucun `<` littéral avant sa fermeture explicite. Son contenu et ses attributs
ne fournissent aucun marqueur. Les références de caractères dans ce contenu ne
créent pas de nouvelles balises. Les segments extérieurs restent littéraux et
séparés ; les espaces extérieurs sont conservés exactement.

**SVG ne suit pas l’état RAWTEXT de `style` HTML.** Un `<p>` dans une chaîne ou un
commentaire CSS peut provoquer une sortie du contexte SVG. Tout `<` avant la
fermeture rend donc l’extraction entière indéterminée : balise imbriquée, commentaire
HTML, CDATA, instruction de traitement, fermeture d’un autre élément ou simple
comparaison CSS. Cette restriction est volontaire ; elle ne déclare pas ces
constructions invalides. Fermetures mal formées, attributs dupliqués, contexte SVG
textuel ou non admis restent aussi indéterminés, même après un interdit observé.
Les bornes v4 restent identiques.

Exemples synthétiques avec requis `Expected`, interdit `Forbidden`, corps changé :

| Construction dans un document complet accepté | Résultat atomique |
| --- | --- |
| `<svg><style>Forbidden</style></svg>Expected` | pass |
| `<svg><style>Expected</style></svg>Other` | fail : requis absent |
| `<svg><style>Other</style></svg>Expected Forbidden` | fail : interdit présent |
| `Expected<svg><style><p>Forbidden</p></style></svg>` | inconclusive |
| `Ex<svg><style>ignored</style></svg>pected` | fail : aucun segment `Expected` |

Le `noscript` contenant du balisage reste **indéterminé**, même un simple `img`
sans texte apparent. Les modes d’analyse avec et sans scripting ne traitent pas
son contenu de la même manière. Le contrat ne choisit pas ce mode. Retirer ce
contenu silencieusement pourrait ignorer un marqueur ; cette version ne tranche
pas cette question normative. `noscript` vide ou limité aux espaces ASCII conserve
son comportement v4. Tables, listes de sélection, texte SVG et autres limites
ne sont pas levés par cette extension.

### Vérification et migration

51 cas synthétiques supplémentaires ont été figés **avant** l’implémentation :
`tests/fixtures/source-text-v5-cases.json` et son manifeste SHA-256. `supersedes`
pointe vers l’empreinte du fichier v4 avec une liste de remplacements vide : les
96 anciens cas, leurs attentes et leur manifeste restent inchangés. Les 312
attentes externes de références de caractères sont conservées. Le script
`python3 scripts/source_text_check.py` contrôle les 147 cas synthétiques et les
312 attentes externes, avec empreinte des résultats et identité du runtime.
Les nouveaux cas sont internes, sans revendication de relecture indépendante.

Réévaluer une capture conservée crée un **nouveau paquet**, avec empreinte d’entrée
identique, nouveaux outils et comparaison des observations. Ne jamais réécrire
l’ancien paquet, retoucher ses critères ou appeler cette comparaison une collecte
prospective. Le rejeu historique exige l’archive historique ; une nouvelle collecte
exige une nouvelle référence/intention du collecteur 5. Intention guidée 3,
entrée binaire 2, paquet 1 et HTML 4 sont inchangés. La priorité URL/empreinte/
stabilité/marqueurs et les précontrôles restent identiques ; à empreinte égale,
les marqueurs restent non exécutés. Le diagnostic 1 conserve explicitement sa
référence de couverture **interpréteur 4** : inventaire exploratoire historique,
ni mesure de couverture de v5 ni verdict. TS07, TS10, contrats et corpus normatif
ne changent pas. Une exécution locale ne constitue pas une observation de CI distante.

## English

**Interpreter 5, adapter 6, collector 5; protocol `0.1.0-draft.7` unchanged.**
This extends the existing SVG icon subset with `style` inside an explicit HTML
`body`, outside `head`. Accept an empty/self-closing style, or character content
with no literal `<` before an explicit closing tag. Style content and attributes
supply no markers. References in style content cannot introduce markup; outside
segments, including whitespace, remain exact and separate. No CSS validity,
rendering, scripting or resource loading is assessed. All v4 bounds still apply.

SVG style does not use HTML style RAWTEXT rules. Markup inside a CSS string or
comment can leave SVG context. Any literal `<` before closure therefore makes
**the whole extraction inconclusive**, including CDATA, HTML comments, nested
markup and a literal CSS comparison. This is a tool restriction, not a declaration
that these constructs are invalid. Malformed closure, duplicate attributes,
unsupported SVG text/context and all other v4 exclusions remain unresolved,
even after finding a forbidden marker. The synthetic examples above exercise
pass, fail and inconclusive; tags never join separate marker fragments.

Markup-bearing `noscript` stays inconclusive: even an apparently text-free `img`
has different parsing treatment with scripting enabled or disabled. The contract
does not select that mode. This version makes no normative choice or silent
exclusion. Empty/ASCII-whitespace-only noscript retains v4 behavior. Tables,
select elements and SVG text are not enabled by this extension.

51 additional synthetic cases were frozen before implementation, in a separate
fixture and SHA-256 manifest. Its `supersedes` references the original v4 hash
with an empty replacement list: all 96 old cases and expectations remain intact.
The 312 independent upstream character expectations also remain unchanged.
`python3 scripts/source_text_check.py` checks 147 synthetic cases plus 312 upstream
expectations and fingerprints results/runtime. New cases are internal, not an
independent review. Full verification also checks the normative corpus, previous
TS07/TS10 results, loopback cases and archive reconstruction.

Re-evaluation creates a new bundle with the same retained input hash and distinct
tool identity; preserve original bundles, criteria and tools. Historical replay
uses its historical archive; new collection needs a collector 5 reference/intent.
Retrospective comparisons are not prospective collections. Guided intent 3, binary
input 2, bundle 1 and HTML 4 are unchanged. URL/digest/stability/marker priority
and preparation checks are unchanged; identical bodies still bypass markers.
Diagnostic 1 explicitly retains its **interpreter 4** coverage reference, as a
historical exploratory inventory, not v5 coverage or a verdict. TS07, TS10,
contracts and the normative corpus are unchanged; no new remote CI is claimed.

## Sources — 2026-10-10 UTC

Primary reading is limited to noscript parsing modes and SVG style boundaries.
Full dated page captures and URL/hash inventory are retained in the local working
evidence; they are not runtime dependencies. Lecture primaire limitée aux modes
noscript et frontières SVG ; captures datées conservées avec leurs empreintes.

| Source | UTC | SHA-256 |
| --- | --- | --- |
| [WHATWG noscript](https://html.spec.whatwg.org/multipage/scripting.html#the-noscript-element) | 06:00:57 | `7629c8213a7f5175d444f5a0eda1fcfb8c61f1eb2a21525ec174d79b0eb69529` |
| [WHATWG foreign content](https://html.spec.whatwg.org/multipage/parsing.html#parsing-main-inforeign) | 06:00:58 | `34e193906e6898ae7faf576a8d4c0f8de619a86ec99d85a3baeb2713171f1dbf` |
| [SVG style](https://svgwg.org/svg2-draft/styling.html#StyleElement) | 06:00:58 | `dbbc1f8bcb1a3b05777d1ec03dac8040738b02941142018e44e2e02dad691195` |
