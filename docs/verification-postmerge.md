# Contrôle après fusion / Post-merge qualification

## Français

Les PR et les déclenchements manuels conservent les sept environnements complets.
Sur un push ordinaire de `main`, le job **Post-merge identity** peut réutiliser
leur qualification, sans prétendre avoir réexécuté les tests. Il ne modifie
aucune protection du dépôt, règle SEO, attente de corpus ou version normative.

La décision exige une PR fusionnée unique, deux parents ordonnés, et un push dont
`before` est le premier parent et `after` le commit fusionné. Les push forcés,
squash/rebase, push directs et états ambigus reviennent au complet. Le `main`
courant est vérifié avant et après la lecture des preuves.

Un seul run de ce workflow doit correspondre à la tête de PR, en succès dès sa
première tentative et terminé depuis moins de 24 heures. Les sept jobs nommés
doivent avoir exécuté les deux étapes de vérification et de préservation des
sources. Le SHA lu dans la section de l’action checkout doit correspondre à
l’identité structurée ajoutée au reçu par `scripts/ci_qualify.py`. L’objet Git
réellement exécuté doit avoir exactement l’arbre complet et les parents du merge.
Cette identité inclut le workflow, les tests, le manifeste et leurs entrées.

Le contrôle compare les deux inventaires unitaires, les onze phases, les deux
conformités complètes, les 48 cas HTTP et les empreintes du manifeste courant.
Aucun test ignoré, échec attendu, résultat manquant, phase annulée ou processus
survivant n’est accepté. La distribution courante est reconstruite rapidement,
puis comparée aux archives des sept reçus ; leurs sources doivent être intactes.
Les reçus mal formés, doublons JSON et valeurs non finies sont refusés.

Les API sont en lecture seule. Seul le job court reçoit les droits temporaires
`contents: read`, `actions: read`, `pull-requests: read`. Le token n’est pas
transmis à la destination signée des journaux. Les appels et tailles sont bornés ;
les journaux restent des données et ne sont jamais exécutés. Le reçu indique le
run réutilisé, ses jobs, leurs versions et empreintes, l’arbre et les parents.

Au moindre manque de preuve, erreur réseau, expiration ou contradiction,
`reuse=false` sélectionne automatiquement les sept qualifications complètes.
Si le job court échoue ou dépasse cinq minutes, la matrice s’exécute également.
Seuls un job court réussi et la sortie exacte `reuse=true` dispensent de la
répétition. Le résumé GitHub distingue réutilisation et nouvelle exécution.
L’annulation explicite du run reste possible (`!cancelled()`) ; elle n’est jamais
assimilée à un succès. Une PR remplacée peut ainsi arrêter sa campagne précédente.

Cette méthode réutilise les environnements consignés avant fusion. Elle ne prouve
pas le comportement sur une nouvelle image ni l’absence de tests intermittents.
Un échec ou une relance pour la même tête n’est pas masqué. Une nouvelle tête est
qualifiée intégralement avant de pouvoir être réutilisée. Le workflow manuel
permet toujours une campagne complète, même sur un merge déjà qualifié.

La première fusion de ce mécanisme doit montrer un chemin court réellement
observé dans GitHub. Les contre-exemples locaux vérifient les refus ; une
préparation de workflow ne vaut pas une observation distante. Toute différence
de fichiers interdit la réutilisation des anciennes preuves. L’ancien profil
documenté dans `verification-speed-v1.md` exécutait systématiquement la matrice
après fusion ; ce document le remplace pour ce seul déclenchement.

## English

PRs and manual dispatches retain all seven full environments. A normal main push
may reuse their recorded qualification only after a successful **Post-merge
identity** job. It must establish the unique merged PR, ordered parents, matching
push before/after, unchanged current main, and the complete identical Git tree.
Direct, forced, squash/rebase or ambiguous pushes require full verification.

The unique matching workflow run must pass on its first attempt within 24 hours.
All seven named jobs and verification/preservation steps must pass. The pinned
checkout action's logged SHA is compared with the structured receipt identity,
actual Git tree/parents and current workflow fingerprint. Both unit inventories,
all eleven phases, both conformance inventories, HTTP cases, immutable sources
and the newly rebuilt distribution must match all seven receipts. Missing,
skipped or expected-failing tests, duplicate JSON keys, nonfinite values and
incomplete phases cannot qualify.

Only the short job receives temporary read-only contents/actions/pull-request
permissions. Tokens do not follow signed log redirects. Requests and response
sizes are bounded; fetched evidence is never executed. Failure, missing evidence,
expired qualification or API errors select the full matrix. Even a failed or
timed-out short job does not skip it: only a successful job AND the exact string
`reuse=true` can do so. The GitHub summary and receipt identify reused results,
not a newly executed matrix. No repository protection is disabled.
Explicit workflow cancellation remains effective (`!cancelled()`), including
superseded PR runs; cancellation never establishes qualification.

This retains evidence from recorded environments; it does not test new runner
images or establish freedom from intermittent behavior. Failed/retried runs for
the same head are not hidden. New heads always receive full PR qualification.
Manual dispatch always remains full. The first merged workflow must demonstrate
the short path on GitHub; local refusal tests are separate evidence. This
supersedes only the unconditional post-merge repetition documented in v1.
