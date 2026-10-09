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
capture adapter has its own tool version and code fingerprints; adding this
workflow does not change the draft.6 normative contract.
It refuses source-file changes during verification. No Edikka environment,
credentials, package installation, browser or public-site collection is needed.
If a sandbox forbids a loopback listener, report that limitation; do not silently
skip the HTTP tests and claim the full verification passed.

Git is needed for development, not for using a downloaded package. Start work on
a `codex/` branch. Keep generated files in sync through deliberate, reviewed
regeneration. The canonical report contract and JSON did not change during the
repository split; distribution boundaries and verification were strengthened.

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
The workflow is prepared but has not run on GitHub. Only the locally observed
Python/OS results are claimed in the migration recipe; Windows support is not
claimed as tested by this migration.

Keep external contribution discussions in the eventual repository's issues/PRs.

## Français

Ce dépôt devient l’unique source de développement TSEP. Le premier commit et le
tag `v0.1.0-draft.1` conservent les 40 fichiers importés sans changement. Les
commits d’infrastructure suivants ne remplacent ni ce tag ni une publication.
La provenance est dans `provenance/import.json`. Aucun historique privé Edikka
n’est importé, aucun domaine, organisation ou DOI n’est nécessaire pour avancer.

La commande `python3 scripts/verify.py` vérifie contrat, tests, conformance sur entrées brutes, exemples temporaires,
sonde HTTP locale et archive reconstruite à l’identique. Elle exige Python 3.9+
et curl, sans dépendance Python externe ni accès à Edikka. Une restriction de
sandbox sur 127.0.0.1 reste une limite à signaler, jamais un test réussi.

Les tests couvrent aussi la conversion hors ligne captures → paquet, l’intégrité
et la couverture partielle ; les exemples de captures sont régénérés avec les
rapports. L’adaptateur possède sa version d’outil et ses empreintes de code ; ce
parcours ne modifie pas le contrat normatif draft.6.

Le constructeur utilise une liste explicite `release-files.json`, pas tous les
fichiers du répertoire. Les fichiers privés non listés restent exclus. Cette
frontière ne remplace pas une revue des sources avant publication. Une archive
de développement porte son empreinte ; elle ne doit pas usurper une version
publiée.

La copie `tools/tsep` dans Edikka est gelée. Toute évolution se fait ici ; le site
intégrera une version choisie avec empreinte et recette propres. Aucune synchronisation
bidirectionnelle, aucun lien symbolique ou historique Git partagé.

La CI couvre Linux/Python 3.9, 3.10, 3.11, 3.12, 3.13 et 3.14 et macOS/Python 3.14,
avec dépendances figées, droits de lecture et sans publication. Elle n’a pas été exécutée sur GitHub. La recette distingue toujours
les validations locales des validations distantes. Les futurs tickets publics
accueilleront les contributions.
