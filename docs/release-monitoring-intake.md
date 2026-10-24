Version 2 — [integrity and explicit migration / intégrité et migration explicite](intake-integrity-v2.md). Preserve version-1 tools and dossiers; conserver les outils et dossiers version1.

# TS36 — Import, revues et clôture / Intake, reviews and closure

## Français

Parcours hors ligne sous le [contrat TS36](release-monitoring.md). Avant acquisition,
conserver le plan et sa revue préalable effectivement fournie. plan.json est une
cible captures2 avec intent.inspection/monitoring, contexte, provenance explicite
inspection_synthetic et monitoring_plan_review ; sans dossiers acquis ni revues finales.

Conserver evidence.json : monitoring_deployment et monitoring_checkpoints, avec
requêtes/réponses API exactes et logs normalisés complets, dates réelles et empreintes.
Le format normalisé n'authentifie ni serveur, opérateur, horloge ou déploiement.
Dater chaque échéance à son moment réel. Ne pas fabriquer J+7/J+30 pour finir un essai.
Les JSON API suivent la [procédure d'acquisition](search-console-acquisition.md).

```sh
python3 adapters/monitoring_intake.py prepare plan.json --evidence evidence.json --output intake-new
python3 adapters/monitoring_intake.py build intake-new --reviews intake-new/review-request.json \
  --assessor 'Évaluateur réel' --output blank-new
# Copier la demande et renseigner seulement les revues effectivement fournies.
python3 adapters/monitoring_intake.py closure-request intake-new --reviews supplied-reviews.json \
  --output closure-new
# Renseigner séparément la clôture ; une demande vide n'est jamais une approbation.
python3 adapters/monitoring_intake.py build intake-new --reviews supplied-reviews.json \
  --closure supplied-closure.json --assessor 'Évaluateur réel' --output bundle-new
python3 tsep.py html bundle-new/report.json --lang fr --output report-fr.html
python3 adapters/replay.py bundle-new --output replay-new
```

Les outils préparent des demandes vides, pas des décisions. La clôture est séparée
pour lier exactement les revues déjà fournies. Une modification ultérieure de celles-ci
invalide cette liaison. Les fichiers d'origine, entrées, empreintes et outils sont
conservés ; une destination existante n'est pas remplacée. L'évaluation globale est
datée à l'import/calcul réel, sans déplacer les dates historiques de chaque échéance.
Un dossier ouvert reste utile avec NT et les constats disponibles. Les contradictions
indépendantes peuvent établir NC malgré des échéances futures. Aucun suivi automatique,
collecte, authentification Google ou transmission externe n'est lancé.

Exercices distribués : ts36-complete (C), ts36-adverse (C documentaire avec constats
défavorables), ts36-pending (NT), ts36-false-closure (NC), dans examples/captures.
Tous les comptes, journaux, déploiements et revues y sont fictifs. Compte réel restricted.

## English

Offline workflow under the TS36 contract linked above. Before acquisition retain
plan.json with captures2 intent.inspection/monitoring, context, inspection_synthetic
and genuinely supplied monitoring_plan_review, without acquired records/final reviews.
Supply evidence.json containing monitoring_deployment and monitoring_checkpoints,
exact native API bodies, complete normalized logs, actual timestamps and hashes.
Normalization does not authenticate server/operator/clocks/releases. Never invent
D+7/D+30 observations. Follow the linked TS08 acquisition procedure for native API.

Commands above prepare blank stage requests, allow an incomplete bundle, then prepare
a separate blank closure bound to the exact supplied stage reviews. Supply genuine
closure separately before a complete build. Later stage-review edits invalidate its
binding. Preserve originals/inputs/hashes/exact tools; no existing destination is
replaced. Overall assessment uses actual computation time; historical stage dates
remain unchanged. Open dossiers retain NT and available findings; independent
contradictions may establish NC despite future stages. No scheduled execution,
collection, Google authentication or external transmission is initiated.

The four named examples are fictional throughout: complete C, adverse documentary C,
pending NT and false-closure NC. Real account evidence remains restricted.
