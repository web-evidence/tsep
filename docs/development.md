# Independent development / Développement autonome

## English

This repository is TSEP's development source. It is independent of the Edikka
website, CMS, database, server configuration and deployment process. Its initial
commit imports the 40 source files of `0.1.0-draft.1` byte-for-byte. The annotated
tag `v0.1.0-draft.1` preserves that unpublished candidate. Provenance is recorded
in `provenance/import.json`; no older Git history or private project files were imported.

The protocol is still a draft. Infrastructure commits after the import do not
rewrite the baseline tag or make a public release. A development archive is a
snapshot identified by its checksum; do not redistribute it under an existing
released archive's identity. Public repository, organization, domain and DOI are
not required to develop or validate the package locally.

### One verification command

Python 3.9+ and curl are required for the full local suite. The CLI itself only
uses Python's standard library. From the repository root:

```sh
python3 scripts/verify.py
```

It validates the contract, runs report/distribution tests and the raw-input
conformance suite, regenerates synthetic examples outside the source tree, runs the bounded HTTP cases on loopback,
builds an archive, extracts it and checks that rebuilding yields identical bytes.
The tests include offline capture-to-bundle conversion, file integrity and partial
coverage; raw capture examples are regenerated alongside report examples. The
capture adapter has its own tool version and code fingerprints. It uses the
pinned normative protocol; draft.7 changes identity assessment, as documented
in its migration, without changing the adapter's bundle format.
It refuses source-file changes during verification. No Edikka environment,
credentials, package installation, browser or public-site collection is needed.
If a sandbox forbids a loopback listener, report that limitation; do not silently
skip the HTTP tests and claim the full verification passed.

Each subprocess step has a **120-second default deadline**, including each unit
test run. Set `TSEP_VERIFY_STEP_TIMEOUT` to a finite number of seconds greater than
zero and at most 86400 (fractions allowed), for example on a slower runner:

```sh
TSEP_VERIFY_STEP_TIMEOUT=300 python3 scripts/verify.py
```

The effective deadline is recorded as `step_timeout_seconds` in the JSON result.
Invalid values fail before any checks. A timeout fails verification and retains
the step name, duration, limit and partial output; it never skips a check or
turns it into success. The limit applies per step, not to the entire command;
the conformance adapter's own 15-second per-case limit remains separate.

The draft.7 external CLI test uses 15 named corpus cases, asserting pass/fail/
inconclusive coverage for all nine rules. They also include multiple targets and
a reference limit; the test rejects wrong verdicts and extra output. This reduces
adapter startups from 604 to 45. **Both conformance steps still run all 216 cases**
in the source tree and extracted archive; the corpus is unchanged. The unit-step
target is under 60 seconds, leaving at least the same amount of margin under the
default deadline. Actual timings depend on Python, machine load and hardware;
record the measured environment rather than asserting an unobserved CI result.

Git is needed for development, not for using a downloaded package. Use descriptive
branches in the form `<type>/<short-description>`, where type is `feat`, `fix`,
`docs`, `test` or `chore` (for example, `docs/contributor-guidance`). Integrate
changes sequentially after verification. Keep generated files in sync through
deliberate, reviewed regeneration. The canonical report contract and JSON did not
change during the repository split; distribution boundaries and verification
were strengthened.

### Distribution and integration boundaries

`release-files.json` is the explicit distribution inventory. The builder rejects
missing files, duplicates, unsafe paths, symlinks and common private file paths.
Unlisted local files cannot enter an archive. This is a packaging boundary, not
a guarantee against secrets deliberately written inside an allowed source file:
review source and Git diffs before publication.

`maintain.py build --output /tmp/tsep-development.zip` refuses an existing output
and creates deterministic bytes with a SHA256SUMS manifest. `.git`, environment files, Git bundles and working evidence stay outside the package.

Edikka's original `tools/tsep` is frozen, with a migration notice. Future changes
belong here. Edikka should consume a chosen release plus checksum through its own
reviewed integration. Do not symlink the repositories, synchronize both directions,
share `.git`, or couple a website build to TSEP's working tree.

### CI and public contributions

The GitHub workflow runs the same command on Linux/Python 3.9, 3.10, 3.11, 3.12,
3.13 and 3.14 and on macOS/Python 3.14. Action dependencies are pinned to verified commit hashes;
permissions are read-only and checkout does not persist credentials. It has no
deploy, release, secret, `pull_request_target` or automatic publication step.
The repository is [web-evidence/tsep](https://github.com/web-evidence/tsep), hosted
under [Web Evidence](https://github.com/web-evidence). It is private as of
9 October 2026; repository, issue, pull-request and CI links require access.
Edikka remains the current steward; hosting does not establish independent governance.
Use the repository's issues/PRs when you have access. Public contributions will
use the same channels after a separately authorized public opening.

### First observed CI run

On 9 October 2026, [run 1, attempt 1](https://github.com/web-evidence/tsep/actions/runs/37962185984)
completed successfully on commit `253b0a13389af53d50245f874f6bdcdb2b570a68`.
All seven jobs passed: Linux/Python 3.9, 3.10, 3.11, 3.12, 3.13 and 3.14,
and macOS/Python 3.14. Each job ran 152 unit tests and all 216 conformance cases
in both the checkout and the extracted archive, plus 48 loopback HTTP cases.
Each conformance run retained 454 agreements, zero disagreements and nine reduced
coverage pairs out of 463 rule/target pairs; reduced coverage is not a pass.
All fourteen unit-test steps stayed below 60 seconds; the longest took 49.354 seconds
including process startup, with the default 120-second step deadline unchanged.

The runner images and Python patch versions observed in the logs were:

| Runner label | Image and build | Python versions |
| --- | --- | --- |
| `ubuntu-latest` | `ubuntu-24.04`, `20261004.327.1` | 3.9.25, 3.10.22, 3.11.17, 3.12.15, 3.13.16, 3.14.8 |
| `macos-latest` | `macos-26-arm64`, `20260907.0351.1` | 3.14.7 |

The `-latest` labels can resolve to different images in later runs.

All seven archives and their rebuilds matched the archive built locally from
the same commit before push:
`4f8bc1575fa5591dc6fdbbbcbbaac97620e9e81e57d7de749223631f4685dafa` (SHA-256).
The maintainer retained the complete log ZIP for this attempt, SHA-256
`5e799a49546ec74a15f829dd1a6aab6b95168ac61d0598264632433c7fcc75d0`.
Logs are accessible through the private run until the GitHub retention period
expires ([90 days by default](https://docs.github.com/en/organizations/managing-organization-settings/configuring-the-retention-period-for-github-actions-artifacts-and-logs-in-your-organization));
the effective repository setting was not checked. The retained ZIP identified
above is the durable reference after that expiry. This is an observed remote
execution, not yet a publicly inspectable or independently reviewed result.
Windows was not tested.

These results and archive hashes belong to that commit, which predates this
documentation update. Later revisions, including documentation-only changes,
need their own verification and produce a different archive when packaged bytes
change. The protocol remains `0.1.0-draft.7`; the initial tag is not replaced.

## Français

Ce dépôt devient l’unique source de développement TSEP. Le premier commit et le
tag `v0.1.0-draft.1` conservent les 40 fichiers importés sans changement. Les
commits d’infrastructure suivants ne remplacent ni ce tag ni une publication.
La provenance est dans `provenance/import.json`. Aucun historique privé Edikka
n’est importé, aucun domaine, organisation ou DOI n’est nécessaire pour avancer.

Git sert au développement, pas à l’utilisation d’une archive téléchargée. Utiliser
des branches descriptives de la forme `<type>/<short-description>`, avec `feat`,
`fix`, `docs`, `test` ou `chore` comme type (par exemple,
`docs/contributor-guidance`). Intégrer les changements séquentiellement après
vérification. Régénérer les dérivés délibérément et relire leurs écarts.

La commande `python3 scripts/verify.py` vérifie contrat, tests, conformance sur entrées brutes, exemples temporaires,
sonde HTTP locale et archive reconstruite à l’identique. Elle exige Python 3.9+
et curl, sans dépendance Python externe ni accès à Edikka. Une restriction de
sandbox sur 127.0.0.1 reste une limite à signaler, jamais un test réussi.

Le délai maximal par étape de sous-processus vaut **120 secondes par défaut**,
y compris chaque exécution unitaire. `TSEP_VERIFY_STEP_TIMEOUT` accepte un nombre
fini de secondes strictement positif et inférieur ou égal à 86400, fractions
admises. Exemple pour une machine plus lente :
`TSEP_VERIFY_STEP_TIMEOUT=300 python3 scripts/verify.py`.
La sortie JSON expose la valeur effective dans `step_timeout_seconds`. Une valeur
invalide échoue avant les contrôles. Un dépassement fait échouer la vérification
et conserve nom de l’étape, durée, limite et sorties partielles ; aucun contrôle
n’est omis ou déclaré réussi. Ce délai s’applique à chaque étape, pas à la commande
entière ; les 15 secondes par cas d’adaptateur de conformance restent distinctes.

Le test CLI externe draft.7 utilise 15 cas nommés du corpus et vérifie la présence
de pass/fail/inconclusive pour chacune des neuf règles. Il conserve plusieurs
cibles, une limite de référence, les mauvais verdicts et les sorties en trop.
Les lancements d’adaptateur passent de 604 à 45. **Les deux étapes de conformance
exécutent toujours les 216 cas**, depuis les sources et l’archive extraite ; le
corpus reste inchangé. L’objectif unitaire est inférieur à 60 secondes, laissant
au moins autant de marge sous le délai par défaut. Les durées dépendent de Python,
du matériel et de sa charge ; ne revendiquer que les environnements mesurés.

Les tests couvrent aussi la conversion hors ligne captures → paquet, l’intégrité
et la couverture partielle ; les exemples de captures sont régénérés avec les
rapports. L’adaptateur possède sa version d’outil et ses empreintes de code. Il
utilise le protocole normatif figé ; draft.7 modifie l’évaluation d’identité selon
sa migration, sans changer le format du paquet de l’adaptateur.

Le constructeur utilise une liste explicite `release-files.json`, pas tous les
fichiers du répertoire. Les fichiers privés non listés restent exclus. Cette
frontière ne remplace pas une revue des sources avant publication. Une archive
de développement porte son empreinte ; elle ne doit pas usurper une version
publiée.

La copie `tools/tsep` dans Edikka est gelée. Toute évolution se fait ici ; le site
intégrera une version choisie avec empreinte et recette propres. Aucune synchronisation
bidirectionnelle, aucun lien symbolique ou historique Git partagé.

### CI et contributions publiques

La CI couvre Linux/Python 3.9, 3.10, 3.11, 3.12, 3.13 et 3.14 et macOS/Python 3.14.
Les dépendances d’actions sont figées sur des empreintes de commit vérifiées ;
les droits sont en lecture seule et le checkout ne conserve pas les identifiants.
Le workflow n’a ni déploiement, ni release, ni secret, ni `pull_request_target`,
ni étape de publication automatique.
Le dépôt [web-evidence/tsep](https://github.com/web-evidence/tsep) est hébergé sous
[Web Evidence](https://github.com/web-evidence). Il est privé au 9 octobre 2026 ;
les liens vers le dépôt, les issues/PR et la CI nécessitent un accès.
Edikka reste le responsable actuel ; l’hébergement ne crée pas une gouvernance indépendante.
Utiliser les issues/PR avec un accès au dépôt. Les contributions publiques
emploieront les mêmes canaux après une ouverture publique autorisée séparément.

### Première CI observée

Le 9 octobre 2026, le [run 1, tentative 1](https://github.com/web-evidence/tsep/actions/runs/37962185984)
a réussi sur le commit `253b0a13389af53d50245f874f6bdcdb2b570a68`.
Les sept jobs ont réussi : Linux/Python 3.9, 3.10, 3.11, 3.12, 3.13 et 3.14,
et macOS/Python 3.14. Chaque job a exécuté 152 tests unitaires et les 216 cas de
conformance dans les sources puis l’archive extraite, ainsi que 48 cas HTTP sur loopback.
Chaque passage de conformance conserve 454 accords, aucun désaccord et neuf
couples de couverture réduite sur 463 couples règle/cible ; une couverture réduite
n’est pas un pass. Les quatorze étapes unitaires sont restées sous 60 secondes ;
la plus lente a duré 49,354 secondes, démarrage du processus compris, sans modifier
le délai par défaut de 120 secondes par étape.

Les images des runners et les versions correctives de Python observées dans les
journaux étaient :

| Étiquette du runner | Image et build | Versions de Python |
| --- | --- | --- |
| `ubuntu-latest` | `ubuntu-24.04`, `20261004.327.1` | 3.9.25, 3.10.22, 3.11.17, 3.12.15, 3.13.16, 3.14.8 |
| `macos-latest` | `macos-26-arm64`, `20260907.0351.1` | 3.14.7 |

Les étiquettes `-latest` peuvent désigner d’autres images lors de runs suivants.

Les sept archives et leurs reconstructions ont la même empreinte que l’archive
construite localement depuis ce même commit avant l’envoi :
`4f8bc1575fa5591dc6fdbbbcbbaac97620e9e81e57d7de749223631f4685dafa` (SHA-256).
Le responsable a conservé le ZIP complet des journaux de cette tentative, SHA-256
`5e799a49546ec74a15f829dd1a6aab6b95168ac61d0598264632433c7fcc75d0`.
Les journaux sont accessibles depuis le run privé jusqu’à l’expiration de la
rétention GitHub ([90 jours par défaut](https://docs.github.com/en/organizations/managing-organization-settings/configuring-the-retention-period-for-github-actions-artifacts-and-logs-in-your-organization)) ;
le réglage effectif du dépôt n’a pas été vérifié. Le ZIP conservé, identifié
ci-dessus, est la référence durable après cette expiration. Cette exécution
distante observée n’est pas encore une preuve consultable publiquement ni une
revue indépendante. Windows n’a pas été testé.

Ces résultats et empreintes appartiennent à ce commit, antérieur à cette mise à
jour documentaire. Toute révision suivante, même documentaire, exige sa propre
vérification et produit une autre archive si les octets distribués changent.
Le protocole reste `0.1.0-draft.7` ; le tag initial n’est pas remplacé.
