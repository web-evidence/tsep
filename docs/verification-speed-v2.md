# Répétitions de conformité / Repeated conformance work v2

## Français

Cette évolution non normative réduit le travail du test
`Draft3.test_raw_conformance_and_contradictory_expected_outcome`. Il interprétait
deux fois tout le corpus pour vérifier une seule attente contredite. Il exécute
désormais le véritable interpréteur sur la règle de cette attente, dérivée de la
paire modifiée. Il exige un résultat positif, puis exactement la divergence
attendue, le nombre de cas exécutés, le corpus total, les règles omises et
l'absence de revendication après l'échec. Le corpus complet reste validé, même
quand certaines règles ne sont pas interprétées.

Les interprétations intégrales de `Draft6`, l'intégration de tous les cas dans
`CaptureAdapter` et les deux conformités CLI (sources et archive) sont conservées.
Deux négatifs complets distincts sont conservés :

- `Draft3.test_external_adapter_receives_inputs_only_and_cannot_omit_results`
  refuse les résultats absents : un échec par cas, aucun cas omis, aucune revendication.
- `Draft7.test_ts01_external_adapter_passes_only_declared_subset_and_wrong_results_fail`
  utilise le vrai CLI et refuse les valeurs présentes mais contradictoires en mode
  complet, avec les variantes `(False, '', 1)` et `(False, '--wrong', 1)`.

Ne réduire aucun de ces deux tests à une sélection sans conserver un négatif
complet équivalent. La réduction retire deux interprétations natives complètes
par suite, soit quatre par qualification. L'adaptateur de Draft3 conserve ses
2 362 sous-processus par suite pour le corpus actuel.

Les gardes existantes de `Draft7` et `SitemapFiles` contrôlent les matrices et la
couverture contradictoire des règles non sélectionnées, les résultats réels en
trop, manquants ou étrangers, et les dénominateurs du résultat partiel. Le refus
d'une limite de référence non booléenne sur un cas non sélectionné est renforcé.
Ce sont des tests du mécanisme de conformité, distincts de l'intégration native :
`Draft7.test_selection_does_not_hide_corrupt_corpus`,
`Draft7.test_scoped_reference_reports_exact_denominators_and_omissions`,
`Draft7.test_extra_missing_and_foreign_pairs_are_not_filtered_from_actual` et
`SitemapFiles.test_missing_declared_outcome_coverage_is_rejected`. Le dernier retire
notamment un résultat requis de TS01-A01 alors que seule TS15-A03 est sélectionnée.

Les 1 306 identifiants de tests, les corpus, attentes, règles et lecteurs sont
inchangés. Aucune préparation ni verdict n'est mis en cache. Les onze étapes,
l'archive reproductible et les sept environnements restent requis. Cette
préparation ne constitue pas une qualification réussie ; les preuves doivent
porter sur le candidat exact.

Mesurer le test réellement modifié en trois paires alternées, même machine et
mêmes versions : durée, CPU et nombre d'appels réels à l'interpréteur. Le coût
d'instrumentation et la charge de la machine font partie des limites. Ne pas
extrapoler le gain de ce test à la durée complète ; mesurer aussi la qualification
complète. Ne pas relancer trois fois des suites lourdes inchangées seulement pour
relire leur preuve. Les profils rapides restent explicitement partiels.

## English

This non-normative change removes two full-corpus interpretations from
`Draft3.test_raw_conformance_and_contradictory_expected_outcome`. The test now
uses the real interpreter on the rule derived from the changed expectation. It
requires a passing result, then exactly the intended contradictory pair, correct
executed/total case counts, omitted rules and no success claim after failure.
The runner still validates the entire corpus before accepting a scoped result.

Full native interpretation in `Draft6`, full corpus bundle integration in
`CaptureAdapter`, and both source/archive CLI conformance passes remain. The
Draft3 external-adapter test retains a full-mode missing-result negative,
requiring one failure per case, no omitted cases and no claim. The Draft7 external
adapter/CLI test cited above retains full-mode present-but-contradictory values,
through both unscoped variants. Do not narrow either test without retaining an
equivalent full-mode negative. Two full native interpretations are removed per
suite, four per qualification; Draft3's external adapter still launches 2,362
subprocesses per suite with the current corpus.

Existing `Draft7` and `SitemapFiles` guards check malformed unselected cases,
missing contradictory coverage for unselected rules, extra/missing/foreign
actual pairs and scoped denominators. A non-boolean reference limit in an
unselected case now has an explicit rejection check. Runner-contract tests are
distinct from native integration tests.

All 1,306 test identities, corpus expectations, rules and engine readers remain.
There is no preparation/verdict cache, skipped qualification phase or reduced
environment matrix. Reproducible distribution and exact-candidate qualification
are still required; this document is not evidence of a passing run.

Measure the changed test in three alternating pairs on the same machine and
runtime versions, recording wall time, CPU and real interpreter call counts.
Disclose instrumentation and host load; do not equate a single-test gain with a
full verification gain. Measure full verification separately, without running
unchanged expensive suites three times merely to reread their evidence. Quick
profiles remain explicitly partial.
