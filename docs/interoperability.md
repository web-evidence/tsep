# Interoperability / Interopérabilité

## English

EARL is a W3C Working Group Note that provides reusable evaluation terms.
TSEP exports an EARL JSON-LD companion; it does not claim W3C approval or
compatibility with every EARL consumer. The context is embedded, requiring no
network lookup. Assertions concern the declared scope as a whole, not an
invented per-URL pass. The original report and evidence bundle remain necessary
for replay: the EARL companion is not a lossless replacement.

| TSEP | Evaluation state | EARL outcome |
| --- | --- | --- |
| C | complete | `earl:passed` |
| NC | complete | `earl:failed` |
| NA | complete | `earl:inapplicable` |
| NT | not-started | `earl:untested` |
| NT | inconclusive | `earl:cantTell` |

The draft draws on ACT's separation of applicability, expectations and test
examples. Its 44 broad controls are **not ACT rules** and are not covered by 44
automated implementations. A partial probe may expose a failure but a pass does
not automatically satisfy the parent control. An integration should identify:
tool/version, atomic test ID, mapped TSEP version/ID, input conditions, covered
expectation, known limitations and raw outcome. Do not map every crawler warning
directly to NC without establishing applicability and a contradictory observation.

## Français

EARL est une note de groupe de travail W3C proposant un vocabulaire d’évaluation.
L’export TSEP utilise ce vocabulaire sans revendiquer de validation W3C ni une
compatibilité universelle avec les outils. Le contexte est inclus, sans requête
réseau. L’assertion porte sur le périmètre déclaré entier. Conserver le rapport
TSEP et ses preuves : l’export EARL complémentaire ne les remplace pas.

Le tableau distingue bien NT non commencé (`untested`) et NT indéterminé
(`cantTell`). Les 44 contrôles s’inspirent de la structure ACT sans devenir des
règles ACT. Réussir une sonde partielle ne valide pas automatiquement son contrôle
parent. Pour intégrer un outil, déclarer version, test atomique, ID TSEP/version,
entrées, attendu couvert, limites et résultat brut. Un avertissement ne devient
NC qu’après vérification de son applicabilité et d’une contradiction observée.

References: [EARL 1.0 Schema](https://www.w3.org/TR/EARL10-Schema/),
[About ACT Rules](https://www.w3.org/WAI/standards-guidelines/act/rules/about/).
Checked 2026-10-09; this is design inspiration, not endorsement.
