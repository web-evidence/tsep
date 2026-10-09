# Migration — 0.1.0-draft.6 → 0.1.0-draft.7

## Français

Draft.7 corrige R-024 et R-026 sur l’identité TS01-A02 et ajoute la sélection de
règles de conformance R-025. TS01–TS44, leur provenance, le format de rapport 2,
les profils, les sévérités, l’automatisation et la politique de décision restent
inchangés. Les méthodes TS07 et TS10 ne changent pas. Les versions de contrat,
schéma, corpus et empreintes évoluent ensemble ; les archives antérieures restent
distinctes et ne doivent pas être remplacées.

### Identité : preuve positive et portée des marqueurs

URL différente → fail, empreinte identique à la même URL → pass et stabilité
déclarée avec empreinte différente → fail gardent leur priorité. Les changements
ci-dessous portent sur la comparaison par marqueurs d’un corps différent :

| Situation | Draft.6 | Draft.7 |
| --- | --- | --- |
| Interdits seuls, tous absents | pass | inconclusive, TS01 NT/NO_GO si A01 passe |
| Au moins un interdit présent | fail | fail |
| Requis absent | fail | fail |
| Requis uniquement dans commentaire/script/style/attribut | pouvait passer | non compté ; requis absent → fail |
| Au moins un requis, tous présents et interdits absents | pass | pass si trouvé dans le texte extrait |

Pour HTML, les marqueurs portent sur les segments de texte source avec entités
décodées, sans commentaires, contenu script/style, balises ou attributs. Les
segments séparés par du balisage ou un commentaire ne sont pas concaténés. Pas de
normalisation d’espaces ou de casse, regex, CSS ou JavaScript. Le titre et le
texte caché par CSS peuvent compter : ce n’est pas une mesure de visibilité.
Pour text/plain, le corps décodé entier est utilisé sans interprétation HTML.
Le SHA-256 reste celui du corps complet original ; seule la recherche de marqueurs
utilise l’extraction. La référence exige UTF-8 explicite et son sous-ensemble HTML
documenté. Une extraction indéterminée reste inconclusive.

Les deux soft 404 contradictoires sont dans le corpus : interdits seuls absents
→ inconclusive, requis absent → fail. Commentaire, script, style, attribut,
frontières textuelles, entités, espaces, texte brut et captures inexploitées ont
des contre-exemples distincts. Un élément section valide conserve l’attendu pass,
avec `reference_limit: true` pour l’extracteur borné ; sa limite ne réécrit pas la
vérité normative. Le cas existant `identity-only-forbidden-markers` change de pass
à inconclusive. Le cas réussi et l’exemple adaptateur restent C : le marqueur
synthétique `<title>Reference</title>` devient le texte `Reference`. Leurs octets
ne sont donc pas présentés comme inchangés.

Conserver rapports, intentions et preuves draft.6. Réévaluer selon les intentions
réellement fixées avant capture, dans un nouveau rapport avec version/empreinte
draft.7. **Ne pas ajouter rétrospectivement un requis ni modifier une intention
réelle pour faire passer un ancien résultat.** Des marqueurs de balisage peuvent
désormais échouer ; fixer une nouvelle intention et refaire une observation si
nécessaire. Les fixtures synthétiques sont des exemples éditoriaux, pas des
intentions réelles que l’on aurait rétrodatées. Une référence erronée ou un
marqueur trop général reste une limite humaine ; ce correctif ne détecte pas
toutes les soft 404 ni leur classification par un moteur.

### Conformance par règles déclarées

```sh
python3 conformance/run.py --rules TS01-A01,TS01-A02 --command 'python3 mon_adaptateur.py'
```

Sans option, les neuf règles restent exigées. Avec option, seules les règles
choisies sont envoyées et comparées ; toutes leurs cibles restent requises. Les
cas sans règle choisie sont sautés, les sorties supplémentaires restent des
désaccords et les doublons restent invalides. Le corpus complet demeure validé.
Un adaptateur TS01 seul peut réussir la sélection et échouer sans option ; un
mauvais résultat TS01 échoue dans les deux modes.

`rules` contient désormais la sélection, `available_rules` et `omitted_rules`
exposent le reste. `cases` et `rule_target_pairs` portent sur l’exécution ;
`total_cases`, `skipped_cases`, `total_rule_target_pairs` et
`omitted_rule_target_pairs` empêchent de confondre sélection et corpus complet.
`coverage.by_rule` ajoute numérateur, dénominateur et pourcentage conclusifs.
La couverture réduite n’est toujours ni un accord ni une réussite d’évaluation.

Formulation limitée : « passes TSEP 0.1.0-draft.7 conformance for TS01-A01,
TS01-A02 », accompagnée des limites et comptes de couverture. Cela ne produit
aucun C de contrôle, profil ou site. Régénérer les exemples/EARL après validation,
puis exécuter `python3 scripts/verify.py`. Le format du paquet de l’adaptateur
reste en version 1 ; ses empreintes de code et le protocole identifient ce calcul.

## English

Draft.7 fixes R-024/R-026 identity assessment in TS01-A02 and adds R-025 rule
selection for conformance. TS01–TS44, provenance, report format 2, profiles,
severities, automation and decision policy remain unchanged. TS07/TS10 methods
are unchanged. Contract, schema, corpus versions and hashes move together;
earlier archives remain distinct and must not be overwritten.

### Positive identity evidence and marker scope

Different URL → fail, matching digest at the same URL → pass and changed stable
representation → fail retain precedence. For marker comparison of a changed body,
pass now requires at least one required marker, all required markers present and
every forbidden marker absent. Absent forbidden-only markers change from pass to
inconclusive (TS01 NT/NO_GO if A01 passes). A present forbidden marker or missing
required marker still fails.

HTML markers use source-text segments with character references decoded, excluding
comments, script/style content, tags and attributes. Never concatenate segments
across markup/comments; no whitespace/case normalization, regex, CSS or JavaScript.
Title and CSS-hidden text may count; visibility is not measured. text/plain uses
the entire decoded body without HTML interpretation. The digest still covers the
complete original body. Only marker matching uses extraction. The reference
requires explicit UTF-8 and its documented HTML subset; unresolved extraction
stays inconclusive.

The corpus includes both soft-404 counterexamples: absent forbidden-only markers
→ inconclusive; absent required marker → fail. Comments, script, style, attributes,
text boundaries, entities, spaces, plain text and unusable captures have distinct
cases. Valid section text retains normative pass with `reference_limit: true` for
the bounded extractor. The existing forbidden-only case now expects inconclusive.
The passing case and adapter sample retain C, replacing the synthetic markup
marker `<title>Reference</title>` with text `Reference`; their bytes have changed.

Retain draft.6 reports, intent and evidence. Reassess with intent actually fixed
before capture and create a new draft.7 report pinned to version/hash. **Never
add a required marker retrospectively or alter real prior intent to obtain pass.**
Markup markers may now fail; fix new intent and make a new observation as needed.
Synthetic fixture revisions are editorial examples, not backdated real intent.
Wrong references or overly generic markers remain human limitations; this fix
does not detect every soft 404 or establish an engine's classification.

### Conformance for declared rules

Use the command above with your adapter. Without `--rules`, all nine rules remain
required. With it, only selected rules are sent/compared; all their targets remain
required. Cases without selected rules are skipped, extra outputs still disagree,
and duplicates remain invalid. The full corpus is still validated. A TS01-only
adapter can pass the selected subset and fail without the option; wrong TS01
outcomes fail both modes.

`rules` now lists the selection, with `available_rules` and `omitted_rules` exposing
the remainder. `cases`/`rule_target_pairs` count execution; `total_cases`,
`skipped_cases`, `total_rule_target_pairs` and `omitted_rule_target_pairs` expose
the full corpus and omitted work. `coverage.by_rule` adds conclusive numerator,
denominator and percentage. Reduced coverage remains neither agreement nor a
successful assessment.

Use the narrow statement “passes TSEP 0.1.0-draft.7 conformance for TS01-A01,
TS01-A02”, accompanied by limits and coverage counts. It does not produce control,
profile or site C. Regenerate examples/EARL after validation, then run
`python3 scripts/verify.py`. Adapter bundle format remains version 1; code hashes
and pinned protocol identify this assessment.
