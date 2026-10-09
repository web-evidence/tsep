# Interoperability / Interopérabilité

## English

The EARL JSON-LD companion uses the [W3C EARL vocabulary](https://www.w3.org/TR/EARL10-Schema/).
Its context is embedded; no network lookup is required. It is not a lossless
replacement for the report and evidence, nor W3C approval or universal consumer
compatibility. Control assertions concern the declared scope, with stable local
IDs such as `_:control_TS01` and tests `urn:tsep:0.1.0-draft.5:TS01`.

| Control result / state | EARL outcome |
| --- | --- |
| C / complete | `earl:passed` |
| NC / complete | `earl:failed` |
| NA / complete | `earl:inapplicable` |
| NT / not-started | `earl:untested` |
| NT / inconclusive | `earl:cantTell` |

Each `atomic_result` generates **one additional assertion**. Its `earl:test` is
`urn:tsep:<version>:TSxx-Ayy`, its `earl:subject` is that observation's target URL
(or declared inventory URN), and `dct:isPartOf` references the parent control
assertion. Free-text inventory labels use a deterministic SHA-256 target URN
with their original title; URL/URN targets are preserved. Two targets produce two assertions even for the same rule. The mode
comes from `assessor.mode`; date, reason and evidence IDs remain attached. No
assertion is invented for an absent atomic observation.

| Atomic outcome | EARL outcome |
| --- | --- |
| `pass` | `earl:passed` |
| `fail` | `earl:failed` |
| `not-applicable` | `earl:inapplicable` |
| `inconclusive` | `earl:cantTell` |

A passing atom does not override an inconclusive or failing parent. The exporter
runs report validation first. EARL has no TSEP gate policy; consumers must retain
TSEP scope, coverage and version semantics. TSEP's broad controls are not ACT
rules. The [ACT structure](https://www.w3.org/WAI/standards-guidelines/act/rules/about/)
informs the distinction between applicability, expectations and cases; it does
not establish ACT conformance. Integrations declare tool/version, rule and target,
inputs, covered expectation, limitations and raw outcome.

## Français

Le compagnon JSON-LD emploie le vocabulaire EARL W3C, avec contexte intégré sans
requête réseau. Il ne remplace pas le rapport et les preuves, ne vaut pas validation
W3C et ne garantit pas une compatibilité universelle. Les assertions des contrôles
portent sur le périmètre déclaré, avec IDs locaux tels que `_:control_TS01` et
tests `urn:tsep:0.1.0-draft.5:TS01`. Le premier tableau distingue C, NC, NA, NT non
commencé et NT indéterminé.

Chaque `atomic_result` produit **une assertion supplémentaire** : `earl:test` vaut
`urn:tsep:<version>:TSxx-Ayy`, `earl:subject` est l’URL cible de cette observation
(ou l’URN de l’inventaire déclaré), et `dct:isPartOf` désigne l’assertion du contrôle.
Les libellés d’inventaire sans IRI deviennent une URN déterministe fondée sur leur
SHA-256, avec titre original ; URL/URN existantes sont conservées. Deux cibles donnent deux assertions pour une même règle. Mode issu de
`assessor.mode`, date, motif et références de preuves sont conservés. Aucune
observation absente n’est inventée. Le second tableau associe exactement les quatre
verdicts atomiques aux termes EARL, notamment inconclusive → cantTell.

Un test réussi ne remplace pas un parent indéterminé ou en échec. L’export valide
d’abord le rapport. EARL ne définit pas la décision de recette TSEP : conserver
périmètre, couverture et version. Les contrôles TSEP ne sont pas des règles ACT ;
ACT inspire leur structure sans établir une conformité ACT. Une intégration déclare
outil/version, règle/cible, entrées, attendu couvert, limites et résultat brut.

References checked / Références consultées : 2026-10-09. Inspiration, not endorsement.
