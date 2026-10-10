# Paired capture diagnostic / Diagnostic de captures par paire

## Français

`diagnostics/campaign.py` version 1 compare hors ligne deux phases d’un collecteur
figé, selon une liste d’URL et des réglages enregistrés avant la première phase.
**Aucun verdict TSEP, aucune intention, aucun test de marqueurs.** Le rapport
sépare les corps décodés différents, identiques et non comparables. Seules deux
réponses finales enregistrées complètes, 200 et à la même URL finale enregistrée
sont comparées. Le diagnostic ne valide pas la chaîne complète des redirections.

```sh
python3 diagnostics/campaign.py registration.json phase-a phase-b --output-dir diagnostic
```

Chaque phase est un dossier de capture de `collectors.ts01.capture`, avec ses
fichiers bruts, `capture.json` et `SHA256SUMS`. L’enregistrement contient
`kind: "diagnostic-registration"`, `phases: 2`, `registered_at` avec fuseau,
`minimum_gap_seconds` entre 0 et 86400 et les `settings` exacts des phases. Celles-ci
peuvent être produites avec une archive antérieure conservée du collecteur.
L’outil vérifie les empreintes, la correspondance JSON/fichiers HTTP bruts, l’ordre
des 1–10 URL, les réglages, l’identité des sources entre phases et les dates.
Un délai minimal est vérifié entre la fin A et le début B. Les horodatages sont
déclarés par le collecteur : ils ne constituent pas un scellement temporel de confiance.

Chaque page expose séparément :

- la comparaison des octets décodés, avec empreintes, tailles et dates ;
- le type de média observé, y compris son absence dans une réponse complète ;
- l’inventaire exploratoire v1, **non exhaustif pour chaque page**, avec son état
  de fin de balayage ; ce dernier n’est pas une garantie d’exhaustivité ;
- la disponibilité de l’extraction complète par l’extracteur livré avec
  l’interpréteur 5, ou son **premier** motif de refus. Aucun marqueur n’est testé.

L’inventaire v1 reste relatif à l’interpréteur 4 : style SVG et texte SVG peuvent
se recouvrir, et certains styles sont désormais couverts. Le rapport ne présente
pas ces candidats comme une liste complète des blocages de l’interpréteur 5.
La matrice indique séparément leur fréquence sur toutes les pages et sur celles
dont le corps a changé. Les comptes portent sur des URL demandées, sans dédupliquer
les ressources finales. Un échantillon de convenance sur un site ne représente
ni tout le site, ni d’autres gabarits, ni le Web. Deux corps identiques ne prouvent
pas une stabilité générale ; deux corps différents ne prouvent pas un défaut SEO.

Le CLI fonctionne sans module de décision ni collecteur importé. Les seules
fonctions communes sont le décodage HTTP, l’extracteur de texte, l’inventaire et
l’identité du runtime. Le rapport HTML FR/EN reste inerte et ne reproduit pas le
corps brut ni les valeurs des champs de formulaire. Conserver les captures avec
leurs conditions d’accès ; les rendre publiques est une action distincte.

### Comparaison des médias : correction du collecteur 6

Précontrôle 2 / collecteur 6 : lorsque deux réponses sont disponibles, un
Content-Type absent d’un côté et présent de l’autre donne `raw_headers_differ: true`.
Absent des deux côtés donne false. Une réponse indisponible conserve `null` avec
un motif dans le parcours guidé. Aucun résultat normatif ne change, y compris le
pass par empreinte identique lorsque le type disparaît. Aucune validation de
marqueur n’a été changée : `text_present` et le précontrôle utilisaient déjà le
même test `strip()`. Digest/stable n’effectuent toujours pas de précontrôle de marqueurs.

Interpréteur 5, adaptateur 6, intention 3, HTML 4 et protocole draft.7 inchangés.
Les anciennes références/intentions se rejouent avec leurs archives ; toute
nouvelle collecte avec le collecteur 6 exige une nouvelle référence/intention.
La proposition [noscript](proposals/noscript-consensus.md) est non appliquée.

## English

Campaign diagnostic 1 compares two frozen-collector capture phases offline against
settings and 1–10 ordered URLs registered before phase A. **No TSEP outcome,
intent or marker test.** Only complete recorded terminal 200 responses at the same
recorded final URL enter decoded-byte comparison. Entire redirect traces are not
validated here. SHA-256 manifests, JSON/raw sidecar agreement, settings, source
continuity, timezone-aware timestamps and the declared minimum gap are checked.
Recorded dates do not provide trusted timestamping. Historical collectors remain
usable through their retained archives.

Run the command above with a registration containing kind diagnostic-registration,
phases 2, registered_at, minimum_gap_seconds (0–86400), and the exact settings.
Each phase directory supplies capture.json, raw files and SHA256SUMS. Output JSON
and inert FR/EN HTML contain hashes, sizes, dates and observed media fields, never
raw bodies or form values. Retain the access conditions of original captures.

Per page, distinguish byte comparison, the **non-exhaustive** exploratory inventory
1 and complete-extraction availability or first refusal from the source extractor
shipped with interpreter 5. Inventory completion does not establish completeness
of its candidate list. Inventory 1 still references interpreter 4; SVG style/text
candidates may overlap or no longer block extraction. No claim that all current
blockers are listed. Construction counts for all URLs and changed URLs are separate;
requested URLs are not deduplicated by final resource. Two moments and a convenience
sample cannot establish general stability, an SEO defect, whole-site coverage or
web-wide frequency. No rule evaluator or collector is imported by this CLI.

Preflight 2 / collector 6 also fix media observation: a field present on one parsed
response and absent on the other differs; absent on both does not. An unavailable
response still produces null plus a reason in the guided workflow. Normative
outcomes and equal-digest precedence are unchanged. Marker validation was already
identical in text_present and preflight; it was not changed. Digest/stable still
perform no marker preflight. Interpreter 5, adapter 6, intent 3, HTML 4 and draft.7
stay unchanged. Preserve old tools/references; new collector 6 runs need fresh
reference/intent. The linked noscript proposal is unapplied.
