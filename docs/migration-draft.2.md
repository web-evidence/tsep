# 0.1.0-draft.1 → 0.1.0-draft.2

## English

This is an unpublished normative development revision, not an editorial rename
or a certification. TS01–TS44, severities, profile membership and upstream files
remain unchanged. The original candidate remains at `v0.1.0-draft.1`; no tag or
existing archive is replaced. Other controls have no newly specified atomic rules.

TS01 now separates the final GET status from resource identity: a login screen
returning 200 cannot establish C. TS07 separates effective directives, their
accessibility and any necessary rendered states, adding `robots` to required
inputs. TS10 separates canonical declaration, destination, sitemap and internal
links. It explicitly permits declared methods other than an HTML canonical and
documented absence of a sitemap. Absolute URLs remain a TSEP criterion, not a
claim that Google cannot process relative URLs. Point-in-time consistency does
not establish future stability. These are TSEP assessment requirements; the
technical references do not approve TSEP.

Report format changes from `1` to `2`; the schema version and protocol fingerprint
also change. Do not just replace version/hash fields in an old assessment:

1. Retain the old report, evidence and matching validator without modification.
2. Initialize a new report with the new CLI, preserving the declared scope or
   explicitly recording why it changed. Link the predecessor in the reason or
   intent evidence; do not imply that historical captures were recollected.
3. Reassess TS01/07/10 against all rule/target pairs. Record authored findings in
   `atomic_results`. Missing evidence stays NT; observed contradictions stay NC.
   Reused captures retain their real observation times, provenance and limits.
4. Include the required new evidence (notably TS07 robots and any necessary DOM)
   and review NA conditions. Validate with the new CLI. Other controls retain
   their existing semantics; they do not gain automatic coverage.

Old reports are intentionally rejected by this validator. No automatic migration
can supply missing evidence. Synthetic examples are regenerated for the new
contract; the original examples remain recoverable with the original tag.

The canonical rules are rendered in [English](controls.en.md) and
[French](controls.fr.md). [Method cases](../tests/fixtures/control-cases.json)
contain synthetic inputs and bilingual reference judgments. Tests replay their
**report aggregation and evidence requirements**; they do not independently
interpret arbitrary HTTP/HTML. The historical 48 HTTP probe cases remain a
separate, bounded parser regression suite. No independent review is claimed.

Run `python3 scripts/verify.py` for the complete local verification.

## Français

Révision normative de développement non publiée. Les identifiants TS01–TS44,
sévérités, profils et fichiers historiques restent inchangés. Le tag initial
`v0.1.0-draft.1` conserve le candidat et ses exemples ; aucune archive n’est
remplacée. Les autres contrôles ne reçoivent pas de nouvelle décomposition atomique.

TS01 sépare code GET et identité de la ressource : un écran de connexion en 200
ne vaut pas C. TS07 sépare directives effectives, accès et états rendus nécessaires,
avec une nouvelle entrée requise `robots`. TS10 sépare déclaration, destination,
sitemap et liens internes. Une méthode autre qu’une balise HTML et l’absence
documentée de sitemap sont possibles. L’URL absolue reste un critère TSEP, sans
affirmer que Google ne comprend pas les URL relatives. Un instant ne démontre
pas la stabilité future. Les références techniques n’homologuent pas TSEP.

Le format de rapport passe de `1` à `2`, le schéma et l’empreinte changent. Conserver
le rapport, les preuves et le validateur anciens ; initialiser un nouveau rapport,
documenter le précédent et tout changement de périmètre. Réexaminer chaque couple
règle/cible de TS01/07/10 et renseigner `atomic_results`. Compléter les preuves
requises, revoir NA et conserver dates/provenance des captures réutilisées, sans
les prétendre recollectées. Une lacune reste NT, une contradiction reste NC.
Ne jamais migrer en remplaçant seulement version et empreinte. Les autres contrôles
conservent leur sémantique sans couverture automatique supplémentaire.

Les anciens rapports sont volontairement refusés par ce validateur ; aucune
migration automatique ne peut produire les preuves absentes. Les exemples de cette
version sont synthétiques. Les cas de méthode comportent entrées et jugements FR/EN
rédigés : les tests rejouent **l’agrégation et les exigences de preuves du rapport**,
sans interpréteur SEO général. Les 48 cas de la sonde HTTP restent une suite distincte
de non-régression limitée. Aucune revue indépendante n’est revendiquée.

Vérification locale complète : `python3 scripts/verify.py`.
