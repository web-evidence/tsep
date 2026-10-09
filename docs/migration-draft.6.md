# Migration — 0.1.0-draft.5 → 0.1.0-draft.6

## Français

Nouvelle version normative non publiée. Format de rapport `2`, identifiants
TS01–TS44 hérités de la grille 1.1, identifiants atomiques, profils, sévérités et
politique de décision sont conservés. Les règles TS01-A01/A02 restent automatic ;
les classifications TS07/TS10 ne changent pas. Ne pas remplacer un tag ou rapport
historique par une version réécrite.

### R-019 — identité de TS01-A02

Une variation d’empreinte seule donne désormais inconclusive. L’intention préalable
peut exiger `representation: "stable"` ou définir `required_markers` et
`forbidden_markers`. URL différente : fail, prioritaire sur une empreinte identique.
À URL identique, empreinte identique : pass. Sur variation, stable : fail ; sinon
marqueurs valides non vides : tous respectés pass, violation fail ; sinon inconclusive.
Le [contrat FR](contract.fr.md#automatisation-et-identité-de-représentation) fixe
ordre, formats, références manquantes, marqueurs invalides et limites.

| Cas synthétique obligatoire | TS01-A02 | TS01 | Gate |
| --- | --- | --- | --- |
| Corps horodaté, sans marqueurs ni stabilité | inconclusive | NT | NO_GO |
| Corps horodaté, marqueurs respectés | pass | C | GO_WITH_RESERVATIONS |
| Marqueur interdit présent | fail | NC | NO_GO |
| Représentation déclarée stable modifiée | fail | NC | NO_GO |

A01 est pass dans ces quatre cas. Un C concerne exclusivement la cible et TS01,
jamais les 44 contrôles. Le gate ajoute `blocking_causes: [{control_id, status}]`
sans retirer `blocking` ; les résumés FR/EN affichent NC ou NT. Ni décision ni code
de sortie modifiés. Un NT bloquant ne devient pas une autorisation de livraison.

### R-020 / R-021 — conformance et types de contenu

Les `expected` sont normatifs, indépendants des limites de l’évaluateur. Le champ
`reference_limit` identifie le cas **et les couples concernés**, avec `basis`.
Un inconclusive face à un attendu conclusif marqué compte en couverture réduite,
sans désaccord et sans accord exact. Toute autre divergence échoue. Les autres
couples restent stricts, y compris ceux du même cas. `expected_origin` ne revendique
aucune validation indépendante.

`unsupported-robots-wildcard` attend désormais pass pour TS07-A02 (RFC 9309
§2.2.2–2.2.3). Les autres attendus corrigés et justifications sont dans le corpus :
présentation sans restriction requise, indexifembedded seul, base avec canonical
absolue, annotation canonical typée ignorée par Google, rel Link répété, contexte
anchor distinct et DTD locale inutilisée. Les cas dont la preuve reste ambiguë
conservent un attendu inconclusive ; le marquage ne permet pas un pass arbitraire.

Content-Type : type/sous-type, nom de paramètre et charset UTF-8 sans casse ;
valeurs quotées admises. robots.txt text/plain accepte l’absence de charset ; HTML
exige un charset UTF-8 explicite. Les autres encodages et ambiguïtés restent des
limites. Les cas TS01/TS07/TS10 couvrent formes équivalentes et contre-exemples.

### R-023 / R-022 — interfaces

`add-evidence` et `record` produisent deux lignes par défaut. Ajouter `--json` aux
scripts qui lisaient leur ancien résumé JSON. `gate` reste JSON par défaut ; le
résumé anglais écrit `Targets:`. `record --atomic` accepte un objet JSON explicite
par couple, répétable et exclusif de `--atomic-results`. Le parcours documenté
n’exige plus de Python intégré. Les preuves restent explicitement rattachées.

EARL : le test du contrôle devient `earl:TestRequirement`, celui de la règle
`earl:TestCase` avec `dct:isPartOf` vers le test du contrôle. Le lien entre assertions,
les sujets par cible et les quatre verdicts restent conservés.

### Réévaluer avant migration

Conserver le rapport draft.5 et ses preuves. Créer un rapport draft.6 lié à sa
version et son empreinte, puis réévaluer les captures selon l’intention réellement
fixée avant mesure. Ne jamais antidater des marqueurs ou une exigence de stabilité
pour changer un verdict. Si les nouvelles exigences d’intention n’existaient pas,
conserver inconclusive ou effectuer une nouvelle observation. Un changement de
casse dans les en-têtes ne dispense pas de recalculer les empreintes des captures
et des revues qui en dépendent. Régénérer l’export EARL après validation.

Exécuter `python3 conformance/run.py` pour publier les comptes d’accords,
désaccords et couverture, puis `python3 scripts/verify.py`. Un succès avec couverture
réduite ne démontre ni une implémentation complète des RFC ni une conformité globale.

## English

This is a new unpublished normative version. Report format `2`, permanent grid 1.1
TS01–TS44 IDs, atomic IDs, profiles, severities and decision policy are retained.
TS01-A01/A02 remain automatic; TS07/TS10 classifications are unchanged. Never
replace historical tags or reports with rewritten artifacts.

R-019: a changed digest alone is now inconclusive. Prior intent may specify
`representation: "stable"` or `required_markers` / `forbidden_markers`. Different
final URL fails before digest equality; same URL and digest pass. On a changed
digest, stable fails; otherwise valid nonempty markers all satisfied pass, any
violation fails; otherwise inconclusive. The [English contract](contract.en.md#automation-and-representation-identity)
defines order, formats, missing references, invalid markers and limits.

The four mandatory cases above have passing A01: timestamped body without criteria
→ A02 inconclusive / TS01 NT / NO_GO; respected markers → pass / C /
GO_WITH_RESERVATIONS; forbidden marker or changed stable representation → fail /
NC / NO_GO. C covers only the declared target and TS01. JSON adds
`blocking_causes: [{control_id, status}]` while retaining `blocking`; FR/EN summaries
show NC or NT. Decisions and exit codes are unchanged; blocking NT still prevents go.

R-020: `expected` is normative truth, independent of parser coverage. Both case and
affected pairs carry `reference_limit`, with `basis`. Inconclusive against a marked
conclusive expectation counts only as reduced coverage, neither disagreement nor
exact agreement. Every other difference fails; unmarked pairs remain strict even
within that case. `expected_origin` makes no independent-validation claim.
`unsupported-robots-wildcard` now expects TS07-A02 pass (RFC 9309 §2.2.2–2.2.3).
Other corrected expectations have reasons in the corpus: missing required preview
restriction, indexifembedded alone, base with absolute canonical, typed canonical
ignored by Google, repeated Link rel, different anchor context and unused local DTD.
Ambiguous evidence retains normative inconclusive; flags never allow arbitrary pass.

R-021: Content-Type type/subtype, parameter names and UTF-8 charset are case
insensitive; quoted values are accepted. text/plain robots.txt accepts absent
charset; HTML needs explicit UTF-8. Other encodings and ambiguities remain limits.
TS01/TS07/TS10 cases cover equivalent forms and counterexamples.

R-023: add `--json` to scripts parsing the former add-evidence/record JSON summary;
the new default is a two-line receipt. Gate remains JSON by default; English
summary uses `Targets:`. Repeated `record --atomic` takes explicit JSON objects,
mutually exclusive with `--atomic-results`. The documented workflow needs no
embedded Python. Evidence links remain explicit. R-022 specializes control tests
as `earl:TestRequirement` and atoms as `earl:TestCase`, with test-level dct:isPartOf.
Assertion links, target subjects and all four outcome mappings are retained.

Retain draft.5 reports and evidence. Create a draft.6 report pinned to its new
version/hash; reassess captures against intent actually fixed before measurement.
Never backdate markers/stability to change a verdict. If absent, retain inconclusive
or make a new observation. Header-case changes still require refreshed capture and
review bindings. Regenerate EARL after validation. Run `python3 conformance/run.py`
to report agreements, disagreements and coverage, then `python3 scripts/verify.py`.
Success with reduced coverage proves neither full RFC implementation nor global
conformity.
