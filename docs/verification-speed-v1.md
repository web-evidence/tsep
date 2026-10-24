# Qualification isolée / Isolated qualification v1

## Français

Cette optimisation concerne les tests, pas le temps d'analyse d'une page. Elle
ne change aucun lecteur, règle, résultat attendu, corpus ou dépendance du moteur.
Les tests sources et ceux de l'archive restent deux suites complètes et sérielles,
dans deux processus et deux arborescences distincts. La conformité des deux
arborescences est également conservée. Aucun verdict ni préparation du moteur
n'est mis en cache.

- Développement : `python3 scripts/verify.py --quick`, cinq modules ciblés du
  lot 1. C'est un retour partiel, jamais une qualification de livraison.
- Qualification : `python3 scripts/verify.py`, deux processus indépendants au
  maximum ; `--jobs 1` permet le diagnostic séquentiel, `--jobs 4` une mesure
  explicite sur une machine adaptée. Aucun parallélisme à l'intérieur d'une suite.
- Livraison : qualification complète des sept environnements de la PR, de son
  intégration avec la branche cible, puis contrôle du commit et de l'arbre fusionnés.
  Une modification de la tête ou de la base requiert une preuve correspondante.

Les onze étapes sont conservées. La construction et la validation de l'archive
précèdent les quatre phases indépendantes ; la reconstruction et la vérification
de l'immuabilité suivent leur succès. Une erreur, un délai dépassé ou une
interruption annule les processus de phases et leurs descendants sur POSIX.
Un test ignoré, en échec attendu, absent, dupliqué ou une différence entre
inventaires sources et archive interdit un succès. Le manifeste versionné
`scripts/qualification-inventory.json` fixe l'empreinte des identifiants, les
comptes et empreintes des identifiants de conformité et des 48 cas HTTP, ainsi que le corpus complet ; toute évolution de cet inventaire
doit être revue explicitement. Aucun recalcul automatique pendant la qualification.
Les bornes de temps ne sont pas augmentées. Chaque phase dispose de son propre
répertoire temporaire ; les variables Python héritées sont retirées, les quatre
phases utilisent `-I -B -X utf8`. Les tests actuels n'utilisent pas de fichiers partagés
dans le répertoire personnel, de ports HTTP fixes ou de descendants détachés.
La garantie de nettoyage porte sur le groupe de processus POSIX ; elle ne
constitue pas un conteneur capable de retenir un futur processus qui se détacherait.
Un groupe survivant à une sortie normale est arrêté et fait échouer la phase.

Le reçu inclut les identifiants exécutés, les durées par test, le temps réel total
et le CPU du processus et de ses enfants terminés (`os.times`, résolution du
système). Le CPU n'est ni le temps réel, ni les minutes facturées par GitHub.
La somme des durées de phases parallèles n'est pas une mesure d'exécution sérielle.
Comparer des exécutions sur le même matériel et avec les mêmes versions ; publier
les limites de comparaison. Le profilage ajoute son propre coût.

GitHub qualifie les PR (checkout d'intégration par défaut), les push sur `main`
et les exécutions manuelles. Le push d'une branche de PR ne duplique plus toute
la matrice. La vérification après fusion reste complète, sans file de fusion
supposée ni changement des protections du dépôt. Le mode rapide reste local.
Aucune exécution nocturne ou publication n'est ajoutée. Un workflow préparé ne
prouve pas une réussite en CI ; conserver les reçus du commit réellement testé.

## English

This changes verification orchestration, not page-analysis performance, engine
readers, rules, expected outcomes, corpora or dependencies. Source and extracted
archive suites each retain standard serial unittest discovery in separate
processes and trees. Both full conformance passes remain. No engine preparation
or verdict cache is introduced.

`--quick` is the existing five-module lot-1 development check, explicitly partial.
Full verification defaults to two independent processes; `--jobs 1` retains a
serial diagnostic path and `--jobs 4` is opt-in for measured capable hosts.
All eleven phases remain, with build/validation before independent work and
reconstruction/immutability after it. Failures, deadlines and interruptions cancel
phase process groups on POSIX. Skipped, missing or duplicate tests and different
source/archive inventories cannot pass. Time limits are unchanged.

Receipts record individual test times and identities, total wall time and CPU
of the process plus terminated children (`os.times`, system resolution). CPU is
not wall time or billed CI minutes. Summed concurrent phase durations are not a
measured serial run. Compare like environments and disclose profiler overhead.

CI keeps all seven environments for PR integration checkouts, main pushes and
manual dispatches. Feature-branch pushes no longer duplicate the PR matrix.
Post-merge verification remains full; no assumed merge queue, branch-protection
change, nightly run or publishing is introduced. Require matching head/base
qualification and verify merged commit/tree before delivery. Prepared workflows
and old receipts do not qualify a new commit.

The versioned qualification inventory fixes test identities, conformance counts
and 48 HTTP cases; changes require explicit review, never regeneration during
qualification. Expected failures cannot pass either. Each task has a distinct
temporary directory, inherited Python variables are removed and the four phases
use `-I -B -X utf8`. Existing tests have no shared home files, fixed HTTP ports or detached
descendants. POSIX cleanup covers process groups, not a hypothetical future task
that escapes its group; this is not a container. A surviving process group after
a normal exit is killed and fails the phase. Per-test CPU is attributed when
children are waited for; setup/teardown outside individual tests belongs to the
suite total. Concurrent durations include resource contention.
