# Plan préalable TS02 / Prior TS02 owner plan

## Français

Workflow **1**, protocole `0.1.0-draft.11` inchangé. Le parcours rend utilisable
la validation préalable TS02-A01 déjà définie : préparer, importer la décision
fournie, puis associer les captures. Il ne collecte rien et ne répond jamais au
nom du responsable. Python 3.9+, bibliothèque standard, hors réseau.

### Préparer

Rédiger un JSON avec `kind: "tsep-redirect-plan"`, `access` (`public`, `restricted`
ou `synthetic`), `selection_reason` et `targets`. Chaque cible contient uniquement
`url`, `context` et `intent`. Le contexte décrit réseau, bornes, outil et version.
L'intention contient `declared_at`, le client HTTP exact `crawler` et le
[`redirect_plan` TS02](redirects.md). Aucun `http`, `observed_at` de capture ou
`redirect_review` ne doit être présent. Exemple distribué :
`examples/redirect-plan.json`, explicitement synthétique, sans revue.

```sh
python3 adapters/redirect_plan.py prepare examples/redirect-plan.json --output /tmp/ts02-request
```

Le dossier neuf contient les octets du plan, request.json, une fiche HTML lisible,
une réponse vide et SHA256SUMS. Examiner les destinations **et leur pertinence**,
les codes, les bornes et le contexte. Aucun seuil de sauts n'est un seuil universel
SEO. L'outil peut vérifier la forme du plan, pas la pertinence métier d'une URL.
La fiche HTML est autonome, sans script ni ressource distante.

### Importer une réponse réellement donnée

Copier `response-template.json` hors du dossier scellé. Le responsable fournit
pour chaque cible : nom, date avec fuseau, `approved` ou `rejected`, motif et aide
reçue (`assistance`, y compris « aucune »). Provenance : `human` ou `human-assisted`
pour des preuves réelles, `synthetic-exercise` seulement pour un exercice.
Les identifiants, empreintes et rôle `responsible-owner` restent ceux de la fiche.

```sh
python3 adapters/redirect_plan.py import-response /tmp/ts02-request \
  --response /tmp/ts02-response.json --output /tmp/ts02-reviewed
```

Une réponse vide, d'une autre demande, future ou antérieure à la demande est
refusée. Modifier une destination ou un contexte exige une nouvelle demande et
une nouvelle décision. Un refus motivé est conservé ; il ne devient pas une
autorisation de déploiement. Le programme ne prouve pas l'identité, la lecture
effective, la sincérité ni la date réelle de la décision.

### Associer une collecte ultérieure et rejouer

La collecte reste un travail distinct : produire une entrée captures 1 ou 2 avec
les deux règles TS02, les cibles dans le même ordre, les intentions et contextes
exacts du plan **sans revue**, puis ajouter seulement `observed_at` et `http`.
Conserver les requêtes et réponses brutes, y compris les échecs ou interruptions.
Une entrée préparatoire n'est pas une capture. L'outil refuse de remplacer une
revue déjà présente ou d'adapter le plan au résultat observé.

```sh
python3 adapters/redirect_plan.py attach /tmp/ts02-reviewed \
  --captures /tmp/ts02-captures.json --output /tmp/ts02-assessment
python3 adapters/replay.py /tmp/ts02-assessment/bundle --output /tmp/ts02-replay
```

Cette voie exige une date de capture **postérieure ou égale à l'import** de la
réponse. C'est une contrainte prospective du workflow, plus stricte que la seule
chronologie normative déclaration → revue → capture. Elle ne réécrit pas les
anciennes évaluations et ne transforme pas des captures antérieures en collecte
préalablement approuvée. Les dates et pièces restent déclaratives : ce rapprochement
ne constitue pas une authentification indépendante de leur acquisition.

Conserver le dossier entier : plan et réponse historiques, captures originales,
nouvelle entrée avec la revue fournie, reçu et `bundle/` natif. Les réponses HTTP
et leurs dates ne sont pas modifiées. Rejet A01 ou contradiction A02 donnent NC ;
une trajectoire inachevée sans contradiction reste NT malgré une revue positive.
Le rejeu reproduit aussi les échecs. Aucun contenu équivalent, mécanisme JavaScript,
indexation ou résultat global d'Edikka n'est déduit.

Bornes : 1–100 cibles ; JSON 8 Mio ; limites de paquet communes au
[parcours de revue](review-and-replay.md). Sorties neuves, fichiers ordinaires,
manifestes contrôlés, questions et HTML recomparés au plan. Les empreintes des
outils et du protocole doivent correspondre : conserver l'archive exacte. Cette
version ajoute un parcours sans changer l'interpréteur ni migrer les verdicts.
Les tests automatisés sont des exercices synthétiques, pas des validations humaines.

## English

Workflow **1** implements the existing prior TS02-A01 owner-review process without
changing protocol draft.11 or interpreter semantics. The commands above prepare
a sealed plan, import a supplied decision, and attach later supplied captures.
They never collect, infer intended destinations, or fill in a human judgment.

The plan has kind `tsep-redirect-plan`, evidence `access`, a `selection_reason`,
and 1–100 unique targets containing only URL, context and intent. Intent contains
declared_at, exact HTTP crawler and the documented redirect_plan. No capture date,
HTTP trace or prior review is accepted. The distributed example is synthetic.
The readable self-contained HTML and blank response are bound to the same plan.

Copy the response outside the sealed request. Supply an actual owner name,
timestamp, approved/rejected decision, reason and assistance for every target.
Human/human-assisted provenance is required for real evidence; synthetic-exercise
is exclusive to synthetic inputs. Empty decisions, wrong bindings/populations,
future dates and reviews predating the request are rejected. Changed plans need
new requests and decisions. Hashes authenticate neither identity nor judgment.

The attach command requires a captures v1/v2 input containing exactly both TS02
rules and the same ordered targets, unreviewed intentions and contexts. Only
observed_at and raw http are added. Capture timestamps must follow **response
import**, a stricter workflow condition than the normative declaration → review
→ capture ordering. Historical evaluations remain unchanged; earlier captures
cannot be silently retrofitted. Timestamps/acquisition are supplied, not independently
authenticated. Existing reviews are never overwritten.

Keep the whole result directory: original plan/response, original captures,
reviewed input, receipts and native replayable bundle. A refusal or HTTP
contradiction remains NC; an unfinished trace remains NT without a proven failure.
No content equivalence, client navigation, indexing or whole-site claim follows.
Use the exact historical tools/protocol for later processing. New output directories
only, 8 MiB JSON and shared package bounds. Tests are synthetic exercises and do
not establish actual human use. No migration of previous verdicts is needed.
