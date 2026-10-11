# Performance intake / Import de mesures — workflow 1

## Français

Ce parcours **hors ligne** prépare les entrées TS34/TS35 de draft.21 à partir de
fichiers natifs. Il ne collecte aucune page, n’installe pas Lighthouse et ne modifie
pas les règles du [contrat de performance](performance-evidence.md). Protocole,
interpréteur 21, adaptateur 22 et rejeu 3 restent inchangés. L’outil d’import possède
sa propre version 1 et ses empreintes. Les anciens dossiers restent associés à
leurs outils exacts ; aucune migration automatique ni remplacement d’archive.

### Parcours concret

Exécuter les commandes depuis la racine de l’archive TSEP extraite, avec Python
3.9+. Le répertoire `work` doit déjà exister. Les noms ci-dessous sont des exemples
à adapter à vos fichiers et à votre URL ; ils n’effectuent aucune requête réseau.
Utiliser `public` ou `restricted` pour de vraies pièces, `synthetic` pour des exercices.

**Terrain CrUX.** Conserver le corps JSON original de la requête sans clé API, par
exemple `{"url":"https://example.com/product","formFactor":"PHONE"}`. Une cohorte
historique reste historique : le plan ne préenregistre pas les visites.

```sh
python3 adapters/performance_intake.py plan-field \
  --target https://example.com/product --granularity url --form-factor PHONE \
  --request-file crux-request.json --max-age-days 7 \
  --operator 'Nom de l’opérateur' --access public \
  --selection-reason 'Page produit, mobile, périmètre explicitement choisi' \
  --output work/field-plan
python3 adapters/performance_intake.py record work/field-plan --slot 1 \
  --file crux-response.json --source-url https://chromeuxreport.googleapis.com/v1/records:queryRecord \
  --output work/field-recorded
python3 adapters/performance_intake.py finalize work/field-recorded --output work/field-intake
```

Le format accepté est le record CrUX natif, pas le rapport PSI combiné, un export
Search Console ou une synthèse manuelle. Un appareil ou une origine différents de
la population prévue ne remplacent pas silencieusement la cohorte demandée.

**Laboratoire Lighthouse.** Le plan adopte explicitement la configuration d’un
rapport de calibration conservé, antérieur au plan. Ce fichier doit contenir le
mode `navigation`, la version, les agents hôte/réseau et tous les réglages requis
par draft.21. Ses audits de performance peuvent être absents : c’est une référence
de réglages, jamais une mesure de la nouvelle série. Les futures exécutions doivent
être réalisées après le plan, avec la configuration déclarée.

```sh
python3 adapters/performance_intake.py plan-lab \
  --target https://example.com/product --final-url https://example.com/product \
  --calibration calibration.json --run-count 3 --max-age-days 1 \
  --operator 'Nom de l’opérateur' --access public \
  --selection-reason 'Trois passages navigation sur la page produit' \
  --output work/lab-plan
python3 adapters/performance_intake.py record work/lab-plan --slot 1 \
  --file lighthouse-1.json --source-url https://example.com/product --output work/lab-1
python3 adapters/performance_intake.py record work/lab-1 --slot 2 \
  --file lighthouse-2.json --source-url https://example.com/product --output work/lab-2
python3 adapters/performance_intake.py record work/lab-2 --slot 3 \
  --file lighthouse-3.json --source-url https://example.com/product --output work/lab-3
python3 adapters/performance_intake.py finalize work/lab-3 --output work/lab-intake
```

Si le deuxième passage n’a produit aucun original disponible, remplacer **seulement
la commande qui l’enregistre** par la déclaration suivante, avec le motif réel :

```sh
python3 adapters/performance_intake.py record work/lab-1 --slot 2 \
  --missing-reason 'Le navigateur a quitté avant de produire le rapport' \
  --error-file lighthouse-2-error.txt --output work/lab-2
```

`--error-file` est facultatif ; sa sortie texte doit rester UTF-8. Un rapport natif
avec `runtimeError` se conserve avec `--file`, sans fabriquer une absence. Le
prochain enregistrement utilise le prochain emplacement. On ne remplace pas un
passage raté par un meilleur : une nouvelle campagne exige un nouveau plan.

### Dossier produit et revue

- `session/` : plan, demande CrUX ou calibration, originaux, reçus numérotés et
  empreintes des états précédents. Les octets UTF-8, BOM, fins de ligne et propriétés
  natives inconnues sont conservés. Le JSON invalide est conservé comme tentative
  indéterminée ; un encodage non UTF-8 ou un fichier vide est refusé explicitement.
- `overview.txt` et `overview.json` : passages fournis, indisponibles ou jamais
  enregistrés, dates d’import et dates natives distinctes. Chaque environnement
  Lighthouse natif, dont un éventuel `benchmarkIndex`, est visible sans verdict sur
  la machine. Une réutilisation de la calibration est signalée et conservée.
- `bundle/` : rapport TSEP, sources et rejeu existant. Une revue manquante laisse
  le contrôle NT. Les autres contradictions peuvent établir NC.
- `request.json` et `response-template.json` : pièces exactes à examiner et fiche
  vide. Aucune classification, hypothèse ou limite d’interprétation n’est approuvée
  par défaut. Copier le modèle **hors du dossier scellé**, puis remplir les réponses.

La réponse doit donner le véritable auteur déclaré, la date avec fuseau,
`provenance` (`human`, `human-assisted` ou `synthetic-exercise`), l’aide réellement
utilisée dans `assistance`, les objets `path`/`sha256` des pièces effectivement
examinées et toutes les décisions. Une réponse générée par IA ne constitue pas une
revue humaine. Pour un exercice, la provenance reste `synthetic-exercise`.

```sh
python3 adapters/performance_intake.py review work/lab-intake \
  completed-response.json --output work/lab-reviewed
python3 adapters/replay.py work/lab-reviewed/bundle --output work/lab-replayed
```

La commande conserve la réponse originale et crée une nouvelle évaluation datée,
sans modifier les dates du plan, des mesures ou de leur import. Elle vérifie les
liaisons, la complétude et la chronologie, pas l’identité ni la justesse du jugement.
Une classification fausse ou l’assimilation de TBT à INP reste dans le dossier et
peut établir NC. Une revue positive ne comble pas un passage ou une métrique absent.
**C qualifie la documentation et la méthode, pas de bonnes performances.**

### Limites opérationnelles

Chaque commande exige un nouveau dossier. Le journal détecte les incohérences
internes de fichiers, reçus et états précédents. Il ne signe ni les dates ni les
preuves. On peut créer une autre branche depuis un ancien dossier ; il n’existe
aucun registre global empêchant cette sélection. Les passages jamais fournis sont
indétectables. L’affectation d’un original à un emplacement est déclarée par
l’opérateur, non authentifiée. Un import peut donc être traçable sans être une
collecte indépendante. Les originaux peuvent contenir des informations sensibles :
choisir leur accès en conséquence avant diffusion.

La calibration fixe des réglages, sans qualifier la comparabilité matérielle, la
charge de l’hôte ni la reproductibilité statistique. Le workflow n’ajoute aucun
seuil de benchmark, identifiant HTTP variable ou nouveau critère de conformité.
Finaliser une série partielle reste permis pour rendre les lacunes visibles ; les
passages non enregistrés ne sont pas déclarés comme des tentatives effectuées.
Aucune médiane d’un sous-ensemble réussi ne clôt une série incomplète.

Maximum : 4 Mio par original UTF-8 et 8 Mio pour l’entrée captures assemblée
(échappements JSON inclus). Un dépassement refuse le nouveau paquet sans modifier
les pièces d’entrée. Des fichiers Lighthouse volumineux peuvent donc dépasser la
limite globale même si chaque original est admissible ; ne pas les tronquer pour
forcer une conclusion. Ce lecteur ne compare pas deux campagnes avant/après,
ne dérive pas le terrain depuis le laboratoire et ne déduit aucun résultat SEO.

## English

Workflow 1 imports supplied native performance files offline under the unchanged
draft.21 contract (interpreter 21, capture adapter 22, replay 3). It performs no
collection, installation or automatic migration. Keep each package with its exact
tool archive. Use the commands above from that archive with Python 3.9+, an existing
`work` directory and your actual paths, URL, operator, access and selection reason.

`plan-field` freezes a URL/origin, device, maximum age and original credential-free
CrUX request body. It does not preregister historical visits. Import native CrUX
records, not combined PSI, Search Console or a manually summarized response.
`plan-lab` explicitly adopts an older navigation calibration report's version,
full collection settings and host/network user agents. Performance audits are not
needed in that reference. Calibration is not a run in the new series. Future runs
must follow the plan and retain their intended configuration.

`record` appends exactly the next numbered slot into a **new** directory, retaining
UTF-8 original bytes including BOM, CRLF and unknown properties. Invalid JSON is
retained for an inconclusive assessment. Empty files and non-UTF-8 input are refused;
declare an unavailable slot if appropriate, retaining an optional UTF-8 error file.
Keep native runtime-error reports as files. Missing slots and never-recorded slots
are different. No silent replacement, deletion or extra slot is accepted within
that journal. A new campaign needs a new plan.

`finalize` may deliver an incomplete series to expose its gaps. `session/` contains
the plan, references, originals, ordered receipts and earlier manifests.
`overview.txt`/`.json` show each slot, local import/native dates and native host
metadata including any benchmark index, without evaluating host comparability.
Calibration reuse is retained and identified. `bundle/` contains the existing
replayable capture report. No review is invented; gaps remain NT and independent
contradictions may yield NC. Incomplete series do not get a flattering median
from a selected successful subset.

Copy `response-template.json` **outside** the sealed intake directory. The supplied
response must bind `request.json` and every exact evidence path/hash, declare the
author, timestamp, actual assistance and provenance (`human`, `human-assisted` or
`synthetic-exercise`), and fill every requested decision. An AI-generated answer is
not a human review. Synthetic examples must stay synthetic. No opinions or boolean
claim limits are pre-approved. The `review` command keeps the exact response and
original intake, creating a new assessment date while preserving intent, native
and acquisition dates. It checks chronology, bindings and completeness, not the
reviewer's identity or judgment. Wrong classifications or lab-to-field/INP claims
are retained and can produce NC. Positive reviews do not fill missing evidence.
**C means conforming documentation/method, not good measured performance.**

Limits: original-to-slot assignment and local timestamps are declared, not
authenticated. Internal manifest/receipt consistency is checked, but hashes are not
signatures. An older package can start an alternative branch; there is no global
journal and unreported attempts remain undetectable. Native originals may contain
sensitive information; choose the evidence-access classification accordingly before
sharing them. Identical declared settings do not establish comparable hardware,
host load or statistical reproducibility. No benchmark threshold or variable HTTP
header is introduced. No before/after, field-from-lab, ranking or site-wide result
is inferred. Maximum 4 MiB per native UTF-8 original and 8 MiB for assembled capture
JSON, including escaping. Oversize input fails before publishing a new package;
never truncate originals to obtain a favorable conclusion.

## Verification / Vérification

The 31-scenario authored matrix `tests/fixtures/performance-intake-v1.json` was
frozen before implementation. `tests/test_performance_intake.py` exercises native
byte preservation, missing/invalid/contradictory evidence, supplied and blank
reviews, retained failures, chronology, no replacement, integrity drift, size
limits, offline operation and portability. These are synthetic workflow tests,
not real Edikka performance measurements or an independent human review.

La matrice de 31 scénarios est figée avant implémentation. Les essais synthétiques
vérifient le parcours, pas les performances réelles d’Edikka. La vérification
complète reste `python3 scripts/verify.py`, avec reconstruction et essais extraits.
