# Profil de publication draft.5 / Draft.5 publication profile — v2

FR : correction non normative après l'arrêt observé du profil
[publication-v1](publication-profile-v1.md). Le 19 octobre 2026, le
[run GitHub 39212359059](https://github.com/web-evidence/tsep/actions/runs/39212359059)
du commit `a958994e061d751c545fa183d7ba87163483397f` a terminé ses six jobs
Ubuntu avec succès. Le job macOS a été annulé à son plafond de quatre heures ;
l'annotation GitHub indique un dépassement de durée maximale. Aucun rapport
final de vérification macOS n'a été reçu. Les réussites Ubuntu et locale ne
remplacent pas ce résultat manquant. Le ZIP des journaux capturés a pour SHA-256
`0e17752a586a600bee17eead9252360116d3ccf43eac34790f8900b4dd8781af`.

EN: non-normative correction after the observed publication-v1 interruption.
On 19 October 2026, the linked GitHub run for the commit above completed all six
Ubuntu jobs successfully. The macOS job was cancelled at its four-hour ceiling;
the GitHub annotation reports that the maximum execution time was exceeded.
No final macOS verifier report was received. Local and Ubuntu successes do not
replace that missing result. The captured log ZIP has the SHA-256 shown above.

FR : le plafond total du job passe à 360 minutes. Le délai de 7200 secondes par
étape reste inchangé, ainsi que les sept combinaisons, Node 24.19.0, les actions
épinglées et tous les contrôles. Le vérificateur écrit désormais sur stderr le
début et la fin de chaque étape, ou son dépassement de délai ; le JSON final
reste sur stdout. Ces messages permettent de situer une interruption, sans
constituer une réussite complète ni révéler les sorties des cas en cours.
Un plafond plus élevé ne corrige pas un défaut de test et ne garantit pas la
réussite du prochain passage. Aucun test n'est retiré, réduit ou parallélisé.

EN: the total job ceiling becomes 360 minutes. The 7200-second per-step deadline,
all seven combinations, Node 24.19.0, pinned actions and every check remain
unchanged. The verifier now writes each step's start and end, or its timeout,
to stderr; the final JSON remains on stdout. These messages locate an
interruption without establishing complete success or exposing in-flight case
output. A higher ceiling does not fix a failing test or guarantee the next run
will succeed. No test is removed, reduced or parallelized.

FR : migration de distribution uniquement. Conserver publication-v1, ses
résultats locaux, ses six succès CI et son arrêt macOS. Construire l'archive
distincte `tsep-0.3.0-draft.5-publication-v2.zip`, inspecter ses entrées et sa
reconstruction, puis exécuter intégralement `scripts/verify.py` et la matrice CI
sur le nouveau commit avant publication. Les 44 contrôles, 98 règles, versions,
lecteurs, contrats, tests, cas et exemples sont inchangés. L'empreinte normative
reste `27fabb482d04a5604e694e7cbf155dcd674a9d7a6d05360fc45b2282145fca1d`.
RC1, ses tags et l'application restent séparés et inchangés.

EN: distribution-only migration. Retain publication-v1, its local results,
six successful CI jobs and macOS interruption. Build the distinct
`tsep-0.3.0-draft.5-publication-v2.zip`, inspect its entries and identical rebuild,
then execute every verifier step and the complete CI matrix on the new commit
before publication. All 44 controls, 98 rules, versions, readers, contracts,
tests, cases and examples are unchanged. The normative fingerprint remains the
value above. RC1, its tags and the application remain separate and unchanged.

FR/EN : préversion expérimentale / experimental prerelease. Exemples synthétiques,
preuves insuffisantes NT, huit paires historiques réduites / synthetic examples,
insufficient evidence NT, eight historical reduced pairs. Aucun audit réel,
conformité globale ou certification / no real audit, global conformity or
certification. Les résultats du nouveau candidat doivent être observés séparément
/ results for the new candidate must be observed separately.
