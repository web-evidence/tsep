# Predeclared synthetic canonical laboratory / Laboratoire canonical synthétique prédéclaré

## English — scope and limits

Laboratory 1 collects **new synthetic browser observations**, with nine recipes
and expectations fixed in `tests/fixtures/predeclared-canonical-v1.json` before its
implementation and collection. Recipes were designed knowing candidate 1. This
checks environmental assumptions and the end-to-end evidence chain; it is **not
independent or blind validation** of interpretation rules, nor a TSEP assessment.
The protocol remains `0.1.0-draft.7`; TS01–TS44 do not change.

Inputs: the frozen recipes, inventory script 2, one environment-specific URL per
case, an explicit preferred absolute URL, canonical requirement and known integrity
history. A separate registration binds these inputs, page response bytes and
loaded tool sources before source collection. A receipt binds the registration
and HTTP source manifests before browser navigation. Hashes and locally declared
clocks establish internal consistency, not authentication or trusted timestamps.

Each page makes one synchronous traversal in its own execution realm, then posts
the raw JSON envelope to the loopback receiver. Eight recipes trigger at
`window.load`. The ninth triggers during parsing, before a trailing conflicting
link: readyState is measured by the inventory, not substituted by the expected
value. There is no second callback or resampling. API authenticity, browser
identity and execution are not attested. Both environments may share an engine;
they do not constitute independent engine validation.

Cases: baseline, identical dynamic duplicate, optional/required removal, movement
into body, leading C0 normalization, dynamic conflict, conflict before traversal
node limit, and loading before conflict. The loading case must remain undetermined;
if its state differs in an environment, retain the mismatch. The node-limited
conflict keeps both the observed contradiction and partial coverage. Removed DOM
links do not erase the retained source declaration. Body placement is ambiguous,
not an absence contradiction. Agreement uses the inherited exact-string subset;
it says nothing about indexing, ranking, Google-selected canonical or stability.

Collection retains exact source request/response sidecars, registration, receipt,
GET/POST logs, raw page envelopes and operator observations, including logs and
page-reported errors. A separate check records every planned structural/outcome
expectation. A page error makes recipe concordance false; the conditional candidate
assessment is not promoted to a successful campaign. Unexpected outcomes remain
in results. Invalid transport or chronology prevents delivery creation; preserve
its source and attempts for investigation. Unavailable environments explicitly
use `{"status":"not-collected","reason":"..."}` and cannot hide attempted requests.
All requests must have a unique attribution; duplicate navigation/POST fails.
Developer logs are retained without treating empty logs as proof of no errors.

## English — version and migration

`experiments/rendered_canonical_v2.py` is a **version 2 intent adapter** around the
unchanged candidate 1 comparison core. It supports `authored-synthetic`,
`retrospective`, and `predeclared-synthetic-laboratory`. A v2 intent contains the
v1 fields plus `registration_sha256` and `case_id`. In the new mode, these bind the
canonical JSON digest of the registration and its unique environment/case task;
intent criteria must equal that task. The record digest is attached after capture,
not presented as a prediction. The receipt separately binds registration **file
bytes**, which have a different digest from canonical JSON.

Use `upgrade_intent_v1` explicitly for old modes: it preserves criteria and adds
null registration fields. v1 inputs are rejected by v2 without this adapter. Old
observations cannot acquire predeclaration through this migration. Old kits retain
their original sources and candidate 1. No tags, artifacts or fingerprints are
replaced. Internally the adapter calls the shared core with its accepted v1 mode,
then restores the actual v2 intent and provenance; this is not a claim that a real
capture is authored. Core equivalence is checked on 69 frozen authored cases and
two later preference cases. The adapter alone does **not** verify collection;
`examples/predeclared_canonical_lab.py` performs transport and chronology checks.
No v2 standalone CLI is added: use the laboratory commands or Python interface.

```sh
python3 examples/predeclared_canonical_lab.py serve --output /tmp/new-canonical-source
# Navigate each registered task once in its declared environment. Retain each
# operator observation, visible receipt, identity, navigation and observation time.
# Stop the server after collection, retaining failed attempts rather than retrying.
python3 examples/predeclared_canonical_lab.py finish /tmp/new-canonical-source \
  --observations /tmp/observations.json --output /tmp/new-canonical-delivery
python3 examples/predeclared_canonical_lab.py replay /tmp/new-canonical-delivery
```

`observations.json` maps every environment to `status: collected` and `records`
indexed by case id, or the explicit unavailable object above. Each record carries
the payload fields `tree, script_sha256, context, url, state, errors,
capture_started_at, captured_at`, plus `page_receipt`, `navigation_started_at`,
`observed_at`, `browser: {name,version,user_agent}`, and `devLogs`. Preserve visual
operator captures separately; they are supporting material, not programmatically
authenticated evidence. `finish` refuses an existing output. `replay` checks the
explicit file manifest and recomputes without network or browser execution.
Exit 0 means both environments collected with all recipe checks matched, 2 means
retained mismatch or unavailable environment, 64 means invalid input/integrity.
Unit transport clients are labeled authored and never claimed as browsers.

## Français — périmètre, résultats et limites

Le laboratoire 1 collecte de **nouvelles observations de navigateurs sur des pages
synthétiques**. Neuf recettes et leurs attentes sont figées avant implémentation
et collecte. Elles sont conçues en connaissant le candidat 1 : vérification des
hypothèses d'environnement et de la chaîne de preuve, sans validation indépendante
ou aveugle des règles. Aucun verdict TSEP : draft.7 et TS01–TS44 restent inchangés.

Avant navigation, le registre lie chaque URL de cas/environnement à la préférence
explicite, à l'obligation de déclaration, aux incidents connus, aux octets HTTP
servis et aux outils chargés. Les sources HTTP sont ensuite collectées ; un reçu
lie leur manifeste au registre. Une empreinte et une chronologie cohérentes ne
constituent ni authentification ni horodatage de confiance.

Huit pages déclenchent une lecture synchrone après `window.load`. La neuvième lit
pendant l'analyse du document, avant une seconde canonique contradictoire. Son
`readyState` est observé et toute divergence conservée, sans nouvelle tentative.
Les API, l'identité du navigateur et l'exécution ne sont pas attestées. Les deux
environnements peuvent partager le même moteur.

Les cas couvrent témoin, doublon dynamique identique, suppression facultative ou
obligatoire, déplacement dans body, normalisation d'un C0 initial, conflit
dynamique, conflit avant limite de parcours et lecture avant conflit. Un conflit
vu dans une lecture partielle reste accompagné de cette couverture partielle.
Une suppression dans le DOM n'efface pas la canonique de la source conservée.
Un déplacement dans body entraîne une ambiguïté de placement, pas une absence.
L'accord de chaînes exactes n'établit ni indexation, classement, stabilité ou choix
de canonique par Google.

Les sources brutes, enveloppes POST, journaux GET/POST, relevés opérateur, erreurs
et dates sont conservés. Une erreur de page invalide la concordance de recette.
Un écart attendu/observé reste dans le résultat. Une intégrité ou chronologie
invalide empêche la livraison : garder les tentatives pour investigation. Une
indisponibilité est `not-collected` avec raison, sans masquer des requêtes déjà
faites. Le rejeu vérifie le manifeste explicite sans réseau ni exécution navigateur.
Les captures visuelles opérateur restent des pièces jointes, non authentifiées.

## Français — migration et vérification

Le candidat 2 adapte le contrat d'intention au mode
`predeclared-synthetic-laboratory`, en conservant `authored-synthetic` et
`retrospective`. Il réutilise les comparaisons inchangées du candidat 1. Deux
champs sont ajoutés : empreinte JSON canonique du registre et identifiant unique
environnement/cas. Le reçu conserve séparément l'empreinte des octets du fichier
registre. L'empreinte du relevé est attachée après capture, sans être une attente.

L'adaptation v1 vers v2 est explicite via `upgrade_intent_v1`, avec nouveaux champs
nuls pour les anciens modes. Elle ne transforme jamais une capture ancienne en
prédéclaration. Les anciens kits gardent leurs outils et empreintes. L'adaptation
interne vers le cœur v1 ne requalifie pas la provenance des captures réelles ;
l'intention et le mode retournés sont ceux de v2. Ce composant ne valide pas la
collecte : le laboratoire contrôle transport et chronologie. L'équivalence du
cœur est testée sur 69 cas figés et deux cas supplémentaires de préférence.
Les tests réseau utilisent des clients rédigés explicitement, sans navigateur.

Les commandes ci-dessus s'appliquent aux deux langues. Sortie existante refusée ;
code 0 pour les deux environnements concordants, 2 pour écart ou indisponibilité,
64 pour entrée ou intégrité invalide. Outils indépendants d'Edikka ; aucune
publication ou reconnaissance de standard n'est établie par cette expérience.
