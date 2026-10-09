# Contributing / Contribuer

## English

Start with a reproducible ambiguity or a real integration problem. Include the
TSEP version, ID, scope, evidence, actual/expected outcome and relevant primary
reference. Remove credentials and private personal data before sharing.

A rule change must update English and French, applicability, expectations,
evidence, limitations, migration notes, and affected cases together. Add both a
positive and a contradictory case, plus a missing-evidence case where relevant.
For human-assisted controls, publish the reasoning and expected reviewer outcome;
do not present a JSON structure test as an SEO assessment test.

State which contribution is original and use the applicable package license.
Declare employer/customer or commercial interests affecting the proposal.
Do not add rankings, adoption figures, names of reviewers, DOI or certification
claims without supporting evidence and authorization where needed.

Run `python3 maintain.py render`, `python3 maintain.py check`,
`python3 examples/replay.py`, and `python3 -m unittest discover -s tests -v`.
Report limitations and adverse results. There is no CLA or promotional backlink
requirement added by this candidate. Publication channels are not live yet.
`render` binds the schema and EN/FR report-contract hashes into the canonical JSON,
then regenerates control documentation. Replay examples after any contract change.

## Français

Partir d’une ambiguïté rejouable ou d’un besoin d’intégration réel. Joindre version,
ID, périmètre, preuves, résultat observé/attendu et référence primaire pertinente.
Retirer identifiants secrets et données personnelles privées avant partage.

Une modification met à jour FR/EN, applicabilité, attendus, preuves, limites,
migration et cas associés. Ajouter un cas positif, un cas contradictoire et, si
utile, un cas de preuve manquante. Pour un contrôle humain, publier le raisonnement
attendu ; un test de structure JSON n’est pas un test du fond SEO.

Identifier le travail original, sa licence et les intérêts commerciaux concernés.
N’ajouter aucune mesure d’adoption, identité de relecteur, DOI ou affirmation de
certification sans preuve et autorisation nécessaire. Exécuter les quatre commandes
ci-dessus et conserver les résultats défavorables. Ce candidat n’ajoute ni CLA ni
lien promotionnel obligatoire. Ses canaux de publication ne sont pas encore ouverts.

## Independent verification / Vérification autonome

Run `python3 scripts/verify.py` before proposing a change. The command performs
regeneration in temporary directories, verifies package boundaries and checks
rebuilding outside the checkout. Register a new distributable source explicitly
in `release-files.json`. Do not include local tracking, credentials or raw private
evidence. See `docs/development.md` for repository and integration boundaries.

Avant toute proposition, exécuter `python3 scripts/verify.py`. Ajouter explicitement
les nouvelles sources distribuées dans `release-files.json`. Les preuves privées
et le suivi local restent hors distribution. Voir `docs/development.md`.
