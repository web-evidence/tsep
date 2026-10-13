Version 2 — [integrity and explicit migration / intégrité et migration explicite](intake-integrity-v2.md). Preserve version-1 tools and dossiers; conserver les outils et dossiers version1.

# TS31 intake v2 / import TS31 v2

Offline helper for the [TS31 contract](structured-content-evidence.md). No browser,
Google connection, native capture generation or automatic semantic judgment.

## Français

1. Avant acquisition, préparer la cible avec son intention et `jsonld.plan`. La
   commande `plan` produit uniquement une demande de revue vierge. Une vraie revue
   doit avoir lieu avant le début de fenêtre ; ne jamais antidater un avis ultérieur.
2. Fournir ensuite HTTP, contextes et états DOM natifs, la revue préalable réelle
   et les pièces de contenu visible. Dans `structured_reviews`, chaque entrée
   contient seulement surface_id et content (sans review ni entities).
3. `prepare` conserve l'entrée originale, recalcule les graphes avec Node 24
   explicite et prépare les index/empreintes des entités. Tous les jugements restent
   unknown, l'auteur/la date/la raison vides, complete=false. Aucun avis n'est créé.
4. Remplir une **copie** de review-request.json avec les revues effectivement
   réalisées. Les dates, preuves et graphes sont contrôlés par l'interpréteur.
   Le contenu d'origine et les liaisons restent inchangés. Une nouvelle pièce
   exige un nouveau dossier de préparation, jamais un remplacement silencieux.
5. `build` produit un nouveau rapport validé, avec les trois règles TS31. Une revue
   vide donne NT ; un build réussi ne signifie pas C. Le dossier réel fourni est
   déclaré restreint ; un exercice reste synthétique.

L'import ne qualifie pas une chaîne de capture réelle. Si une surface manque ou ne
se traite pas, la demande indique son indisponibilité et la conclusion reste
partielle. Une pièce de contenu manquante n'est pas inventée : la demande porte
content=null et nécessite une nouvelle préparation après acquisition. L'absence
de Node bloque la préparation des graphes ; la commande `plan` reste disponible.

## English

Before acquisition, `plan` creates a blank request bound to the prior target intent
and jsonld.plan. A genuine prior review must occur before the window; never backdate
later opinions. Then supply native HTTP, contexts and DOM states, the actual prior
review, and visible-content records. Each structured_reviews item contains only
surface_id/content, without review/entities.

`prepare` retains original input, recomputes graphs with explicit Node 24 and lists
entity indexes/hashes. Judgments stay unknown, metadata empty and complete=false.
Fill a separate copy of review-request.json with actual reviews. Content and bindings
must stay unchanged; new evidence requires a new intake. `build` emits a new validated
three-rule report. Blank reviews stay NT; successful build does not mean C. Real
supplied dossiers use restricted access, authored exercises remain synthetic.

No real capture chain is qualified. Missing/unprocessable surfaces stay unavailable.
Missing visible content remains null until a fresh intake includes it. Preparation
requires Node; planning does not. Historical replay retains original dates/tools;
build creates a new assessment date and does not rewrite an existing report.

## CLI

```sh
python3 adapters/structured_intake.py plan prior-target.json --output plan-request
# Supply the genuine prior review, then perform the planned acquisitions separately.
TSEP_SOURCE_NODE=/absolute/path/to/node24 python3 adapters/structured_intake.py prepare target.json \
  --plan-review supplied-plan-review.json --output prepared
TSEP_SOURCE_NODE=/absolute/path/to/node24 python3 adapters/structured_intake.py build prepared \
  --reviews supplied-reviews.json --assessor 'Declared assessor' --output report
python3 tsep.py html report/report.json --lang fr --output report-fr.html
```

If target.json already contains structured_plan_review, omit --plan-review. Inputs
are supplied JSON files, not files to download manually from a user-facing app.
An application can prepare these internal objects behind its capture/review flow.
