# Declared source perturbations / Perturbations déclarées — experiment 1

## English

`experiments/perturbations.py` applies a bounded, fingerprinted mutation plan to
one retained UTF-8 source, using unchanged marker criteria and noscript experiment
4. It produces **no TSEP report**, no HTTP response and no normative change.
Draft.7 remains active. This tests sensitivity to specified changes, not parser
qualification, browser equivalence, functional correctness or semantic identity.

The plan fixes original body/criteria SHA-256, a timezone-aware local registration
date, and 1–12 named cases. Each case contains a label, explanation, synthetic flag,
0–8 edits and authored expectations for enabled/disabled/consensus candidates.
Each edit gives `start`, `end` (exclusive Unicode code-point positions), exact
`before` and replacement `after`. Ordered, separate, nonoverlapping original-source
ranges are required. Edits are applied backwards to preserve offsets. CRLF and all
other untouched bytes survive UTF-8 roundtripping. A case with edits must be labeled
synthetic. A case without edits only reproduces the supplied body; its provenance
still requires the original capture. Marker lists never change between cases.

Outputs retain every mutated body as inert `.source.txt`, full per-mode evidence,
expected and actual outcomes separately, fingerprints and a manifest. Unexpected
outcomes are retained with exit 1, never silently made expected. Invalid inputs
fail with exit 64; a new destination is required. Offline replay uses the same
source, criteria, plan and pinned tools. Source origins and hashes are checked.
Runtime differences must be disclosed when comparing runs on different Python
versions. No network, JavaScript, CSS, HTTP interpretation or form submission.

A matching result only means agreement with author-written expectations. A literal
heading change may contradict criteria even when editorially intended. Removing a
form may leave criteria satisfied when their texts occur elsewhere. A two-mode
disagreement or incomplete reading remains inconclusive. These facts must be
visible in any demonstration; mutations must not be attributed to the live site.
Local dates/hashes are not independent timestamps, signatures or human approval.
Existing evidence stays unchanged; keep old tool versions and results. No report
migration or normative promotion follows from this experiment.

## Français

`experiments/perturbations.py` applique à une source UTF-8 conservée un plan borné
et lié par empreintes, avec les mêmes marqueurs et l'expérience noscript 4.
**Aucun rapport TSEP**, aucune réponse HTTP et aucun changement normatif ne sont
produits. Draft.7 reste actif. La sensibilité à des modifications précises ne
qualifie pas le parseur, le rendu navigateur, le fonctionnement ou l'identité
sémantique de la page.

Le plan fixe les empreintes du corps et des critères, une date locale avec fuseau,
et 1–12 cas. Chaque cas contient libellé, explication, caractère synthétique, 0–8
modifications et attentes rédigées pour les deux hypothèses et leur consensus.
Chaque modification donne `start`, `end` exclusif (positions Unicode), `before`
exact et `after`. Les plages ordonnées, séparées et sans chevauchement portent sur
la source originale. Application en ordre inverse ; CRLF et octets non touchés
sont préservés. Toute modification exige l'étiquette synthétique. Sans modification,
le corps fourni est reproduit ; sa provenance exige encore la capture d'origine.
Les critères restent identiques entre cas.

Les sorties conservent corps `.source.txt` inertes, preuves des deux hypothèses,
attentes et observations séparées, empreintes et manifeste. Un écart d'attente est
conservé et renvoie 1 ; il n'est jamais corrigé artificiellement. Entrée invalide :
64. Destination nouvelle obligatoire. Rejeu hors ligne avec les mêmes entrées et
outils figés ; origines des modules et empreintes contrôlées. Déclarer les écarts
de runtime entre Python. Aucun réseau, JavaScript, CSS, traitement HTTP ou envoi
de formulaire.

Un accord avec les attentes de l'auteur ne constitue pas une validation externe.
Un titre réécrit volontairement peut contredire les marqueurs. Un formulaire retiré
peut laisser les critères satisfaits si leurs textes sont ailleurs. Désaccord des
hypothèses ou lecture incomplète restent indéterminés. Ces limites doivent être
visibles ; ne jamais attribuer les mutations au site réel. Dates et empreintes
locales ne sont ni horodatage indépendant, ni signature, ni approbation humaine.
Les anciennes preuves, versions et résultats sont conservés. Aucune migration de
rapport ni promotion normative ne découle de cette expérience.

## Command / Commande

```sh
python3 experiments/perturbations.py --source source.txt --criteria criteria.json --plan plan.json --output new-results
```

The retained Contact demonstration's authored plan hash is recorded separately in
`tests/fixtures/contact-demo-plan-freeze.json`; the private source is not distributed
in the protocol package. Public unit tests use only independent synthetic inputs.
L'empreinte du plan Contact est enregistrée dans ce fichier ; les captures privées
ne sont pas distribuées dans le paquet du protocole. Les tests publics utilisent
uniquement leurs propres entrées synthétiques.
