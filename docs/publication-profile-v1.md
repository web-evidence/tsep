# Profil de publication draft.5 / Draft.5 publication profile — v1

FR : correction de distribution non normative depuis le candidat local qualifié
`de8d056dd3e7796c8e2bf548da30ad2bd3e49dcd`. La citation indiquait encore draft.4 ;
`CITATION.cff` indique désormais `0.3.0-draft.5`, conformément au protocole.
Le workflow CI gardait 1800 secondes par étape et 60 minutes par job, alors que
la qualification locale observée a pris 7158.327 secondes, dont 3138.704 et
3184.932 secondes pour les deux suites unitaires. Ces durées locales ne prédisent
pas les durées des runners distants.

EN: non-normative distribution correction from the locally qualified candidate
above. The citation still named draft.4; `CITATION.cff` now names
`0.3.0-draft.5`, matching the protocol. CI retained 1800 seconds per step and
60 minutes per job, whereas the observed local verification took 7158.327
seconds, including 3138.704 and 3184.932 seconds for its two unit-test suites.
These local durations do not predict remote runner durations.

FR : le workflow sélectionne désormais le profil complet déjà qualifié,
`TSEP_VERIFY_STEP_TIMEOUT=7200`, et un plafond total fini de 240 minutes par job.
Les sept combinaisons Python/OS, Node24.19.0, les actions épinglées, permissions,
étapes et gardes d'immutabilité restent identiques. Aucun test n'est retiré ni
parallélisé à l'intérieur du vérificateur. Le défaut CLI de 120 secondes et la
borne de chaque cas du corpus restent inchangés. Un plafond est une limite,
pas une durée attendue ni une réussite de CI.

EN: the workflow now selects the already qualified full profile,
`TSEP_VERIFY_STEP_TIMEOUT=7200`, with a finite 240-minute total job limit.
The seven Python/OS combinations, Node24.19.0, pinned actions, permissions,
steps and source-immutability guards remain identical. No test is removed or
parallelized within the verifier. The CLI's 120-second default and per-case
corpus limit remain unchanged. A ceiling is a limit, not an expected duration
or evidence of CI success.

FR : migration de distribution uniquement. Conserver l'archive method-corpus-v1
et ses reçus ; produire l'archive distincte
`tsep-0.3.0-draft.5-publication-v1.zip`. Les 44 contrôles, 98 règles, versions,
lecteurs, contrats, cas synthétiques et exemples restent inchangés. L'empreinte
normative reste `27fabb482d04a5604e694e7cbf155dcd674a9d7a6d05360fc45b2282145fca1d`.
Exécuter toutes les étapes de `scripts/verify.py`, contrôler la reconstruction
identique et l'archive, puis observer la CI du commit exact avant la publication
de cette préversion. Consigner séparément les résultats observés et les échecs.
Ne remplacer aucun tag ou artefact antérieur ; RC1 et l'application sont séparés.

EN: distribution-only migration. Retain the method-corpus-v1 archive and receipts;
produce the distinct `tsep-0.3.0-draft.5-publication-v1.zip` archive. All44
controls,98 rules, versions, readers, contracts, synthetic cases and examples
remain unchanged. The normative fingerprint remains the value above. Run every
`scripts/verify.py` step, inspect the identical rebuild and archive, then observe
CI for the exact commit before publishing this prerelease. Record observed
results and failures separately. Replace no earlier tag or artifact; RC1 and
the application remain separate.

FR/EN : préversion expérimentale / experimental prerelease. Les huit paires
historiques à couverture réduite restent signalées / eight historical reduced
coverage pairs remain disclosed. Aucun audit réel ni certification / no real
site audit or certification. La préparation n'est pas une publication / preparation
is not publication.
