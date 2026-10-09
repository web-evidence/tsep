# TS07-A03 — Source and DOM captures / Captures source et DOM

## Français

Extension de `input_version: "1"` en draft.4, seulement lorsque TS07-A03 est demandé.
Les quatre règles précédentes gardent leur entrée. Absence de plan ou de rendu
requis → inconclusive, jamais exemption implicite. L’évaluateur **ne lance aucun
navigateur ni JavaScript** : il compare des captures fournies. Les cas sont
synthétiques, avec DOM écrits à l’avance et attendus distincts de l’interpréteur.

L’objectif d’indexation et de liens reste celui de `intent`. Les en-têtes finaux
s’appliquent aussi aux DOM : modifier une meta ne retire pas X-Robots-Tag. Le
sous-ensemble Googlebot/HTML/directives est celui de [conformance.md](conformance.md).
Les objectifs d’aperçu et les syntaxes non prises en charge restent indéterminés.

### Plan préalable et captures

`intent.declared_at` précède `target.observed_at`. Ajouter un `context.id` non vide,
puis le fragment de plan suivant dans `intent` :

```json
{
  "rendering": {
    "mode": "required",
    "required_states": [
      {"id": "loaded", "interactions": [], "wait": "load + 1000 ms"},
      {"id": "expanded", "interactions": ["click #expand"], "wait": "after click + 500 ms"}
    ]
  }
}
```

Ces délais sont ceux du cas synthétique, pas une recommandation universelle.
Chaque ID est unique et la liste est non vide. La pertinence et l’exhaustivité du
plan nécessitent une revue ; deux états déclarés ne prouvent pas tous les états possibles.

`target.render` contient `browser: {"name": "…", "version": "…"}` et un tableau
`states`. Chaque état doit avoir :

| Champ | Attendu |
| --- | --- |
| `id` | Un ID prévu, exactement une capture par ID |
| `url` | URL finale exacte de la trace HTTP |
| `context_id` | Même valeur que `context.id` |
| `source_http_sha256` | Empreinte de liaison décrite ci-dessous |
| `observed_at` | Date avec fuseau, au plus tôt à la capture source |
| `complete` | `true`, DOM complet |
| `javascript_enabled` | `true`, activation déclarée dans l’environnement de capture |
| `interactions`, `wait` | Identiques au scénario prévu ; liste de chaînes et texte non blanc |
| `errors` | Liste explicitement vide ; absence ou erreur → inconclusive |
| `dom` | Sérialisation HTML brute du document, UTF-8, sans remplacer la source HTTP |

Le digest lie l’état à **tout le tableau `target.http` ordonné**, incluant requêtes,
réponses, URL et indicateurs de complétude. Convention déterministe de ce format :

```python
encoded = json.dumps(target['http'], sort_keys=True, separators=(',', ':'), ensure_ascii=False)
source_http_sha256 = hashlib.sha256(encoded.encode('utf-8')).hexdigest()
```

Il ne s’agit pas d’un horodatage de confiance ni d’une norme générale de JSON
canonique. Le paquet de rapport doit aussi hacher les fichiers contenant les
captures. Un adaptateur d’un autre langage reproduit exactement cette convention
pour les valeurs de la trace (objets, listes, chaînes, booléens).

### Décision et preuve

- Tous les états requis attribuables et compatibles, source compatible : pass.
- Un état complet, correctement attribué et incompatible : fail, même si un autre
  manque ou échoue. Le motif conserve les inconnues des autres états.
- Aucun échec établi mais état absent, tronqué, dupliqué, imprévu, non attribuable,
  scénario différent ou erreur de script : inconclusive.
- Source incompatible ou non interprétable, DOM compatibles : inconclusive pour
  A03 ; le résultat source A01 reste distinct. Notamment, retirer un noindex initial
  ne donne pas pass. La [documentation Google](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)
  explique que ce noindex peut empêcher le rendu.

Le rapport exige http, html, render et intent pour un pass A03. Il exige toujours
les trois règles TS07 par cible pour C ; leur automation reste semiAuto. Le
validateur de rapport vérifie les déclarations et pièces, pas la vérité des DOM.

### Exemption documentée

`intent.rendering` peut déclarer `mode: "exempt"` et `basis: "non-html"` ou
`"reviewed-stable"`. Le comparateur exige alors `target.exemption_review` :
`basis` identique, `reviewer`, `reason`, `observed_at` au plus tôt à la source,
`source_http_sha256` identique et `support` non vide. Chaque pièce de support
contient `name`, `content` et le SHA-256 des octets UTF-8 de ce contenu.

Pour non-html, cette implémentation reconnaît uniquement application/pdf,
image/png ou text/plain; charset=utf-8. Pour reviewed-stable, elle exige
text/html; charset=utf-8 et vérifie les pièces déclarées ; **elle ne décide pas
elle-même que la stabilité est démontrée**. La revue humaine en porte le jugement.
Conserver revue et supports dans les preuves intent/http/html de l’exemption.
Une preuve fictive doit rester synthetic, y compris le nom fictif du relecteur.

Une exemption ne peut contenir ni états requis ni DOM observés à masquer. Une
simple mention « pas de JS », une liste vide, un support altéré ou une référence
à une autre source donne inconclusive. NA atomique ne devient pas NA de tout TS07.

## English

Draft.4 extends `input_version: "1"` only when TS07-A03 is requested. The earlier
four rules retain their inputs. A missing plan or required rendering is inconclusive,
never an implicit exemption. The evaluator **runs no browser or JavaScript**: it
compares supplied captures. Fixtures contain authored synthetic DOMs and separate
expected outcomes. Final response headers still apply to every DOM. The same
Googlebot/HTML/directive subset applies; unsupported syntax and preview objectives
remain inconclusive.

Prior intent fixes `rendering.mode: "required"` and a nonempty `required_states`
array, with unique id, interactions (array of nonblank strings) and wait (nonblank
text). The example above is a synthetic schedule, not a universal waiting policy.
`context.id` is required. Plan adequacy and completeness require human review.

`target.render` has browser name/version and states. Each state declares id, exact
final url, matching context_id, source_http_sha256, zoned observed_at no earlier
than the source, complete true, javascript_enabled true, planned interactions/wait,
explicit empty errors and raw UTF-8 dom serialization. Keep source HTML separately.
The code above defines the binding digest of the entire ordered HTTP trace, using
sorted object keys, compact JSON and literal Unicode. This is a format convention,
not trusted timing or a general JSON canonicalization standard. Hash the containing
report artifacts too. Other languages must reproduce this convention for the trace's
objects, arrays, strings and booleans.

All required, attributable states and source compatible → pass. A complete,
attributable state contradiction → fail even if another state is missing or in
error; retain those gaps in the reason. Without a proven failure, missing, truncated,
duplicate, unplanned, unbound or erroneous states and changed scenarios → inconclusive.
Incompatible or uninterpretable source followed by compatible DOMs remains
inconclusive for A03; A01 keeps its source verdict. Removing initial noindex does
not pass A03, as rendering may be skipped. Local DOMs do not establish engine
rendering, indexing, TS25 or all possible states.

A03 pass needs http/html/render/intent evidence. C for TS07 still needs every rule
for every target and semiAuto review. Report validation checks declarations and
files, not DOM truth.

An exemption declares mode exempt and basis non-html or reviewed-stable, plus
`target.exemption_review` with matching basis, reviewer, reason, date no earlier
than source, matching trace hash and nonempty support. Each support record contains
name, content and its UTF-8 SHA-256. This implementation recognizes non-HTML only
for application/pdf, image/png and text/plain; charset=utf-8. A stability review
requires text/html; charset=utf-8. It checks declared records, **not the truth of
human stability judgment**. Keep review/supports in intent/http/html evidence;
fictitious evidence and reviewer names must remain synthetic.

Exemptions cannot hide planned or captured states. Unsupported “no JS” claims,
empty/tampered support or unrelated source references are inconclusive. An atomic
exemption does not exempt all TS07. [Dated source record](source-observations.md).
