# Migration 0.1.0-draft.4 → 0.1.0-draft.5

## Français

Jalon local TS10-A01 à A04, sans publication. Identifiants TS01–TS44, titres
hérités, sévérités, profils et sources 1.1 inchangés. Format de rapport `2` et
entrée de conformance `1` conservés ; la forme des cibles TS10 est documentée
séparément. Les entrées des cinq règles TS01/07 précédentes restent compatibles.

- Réexaminer A01 avec l’inventaire de famille, les méthodes requises et le plan de
  rendu préalables. Lier captures source/DOM et revues d’exemption aux traces,
  contextes et dates. Conserver les déclarations répétées, même identiques.
- Réexaminer A02 : 200 direct, absence de chaîne canonical et **revue humaine** de
  chaque membre comparé à la préférence, avec auteur, date, motif et empreinte des
  pièces examinées. L’interpréteur ne calcule aucune similarité de contenu et ne
  prouve pas la véracité du jugement. La règle reste manual.
- Réconcilier tous les index/enfants de sitemaps pour A03, les pages sources/états
  nécessaires pour A04. Une capture manquante empêche pass ; une contradiction
  attribuable reste fail. Une omission ne devient fail qu’après examen complet.
- L’absence de sitemap nécessite stratégie, inventaire et record de revue positifs.
  A03 not-applicable n’exempte pas A01/A02/A04. Les exceptions aux entrées/liens
  identifient précisément leur objet et leur motif.
- Après réévaluation, créer un nouveau rapport avec version/empreinte draft.5 et
  régénérer EARL. Conserver les anciens paquets ; remplacer une empreinte seule
  n’est pas une migration. Les exemples livrés sont régénérés volontairement.

La suite ajoute 80 cas synthétiques TS10 et des tests de passage au rapport/EARL.
Elle compare les neuf règles atomiques bornées, pas 44 contrôles automatiques.
Elle ne collecte pas de site et n’exécute pas JavaScript. Un C partiel ou automatique
TS10 reste refusé. L’adaptateur vers un rapport de production reste un jalon distinct.
Voir [format et limites](canonical-families.md) et `python3 scripts/verify.py`.

## English

Local TS10-A01 through A04 milestone, unpublished. TS01–TS44 identities, inherited
titles, severities, profiles and grid 1.1 sources are unchanged. Report format 2
and conformance input version 1 remain; TS10 target shape is documented separately.
The earlier five TS01/07 rules' inputs remain compatible.

- Reassess A01 with prior family inventory, required methods and rendering plan.
  Bind source/DOM captures and supported exemption reviews to traces, contexts and
  dates. Preserve repeated declarations, including identical ones.
- Reassess A02: direct 200, no canonical chain, and **human review** of each member
  against the preference, with author, date, reasoning and fingerprinted examined
  records. The interpreter calculates no content similarity and does not establish
  judgment truth. The rule remains manual.
- Reconcile all sitemap index children for A03 and required source pages/states for
  A04. Missing evidence prevents pass; attributable contradiction remains fail.
  An omission fails only after complete examination.
- Sitemap absence needs a positive strategy, inventory and review record. A03
  not-applicable does not exempt A01/A02/A04. Entry/link exceptions identify their
  exact subject and reason.
- After reassessment create a new draft.5-pinned report and regenerate EARL. Retain
  older bundles; replacing only a hash is not migration. Bundled examples are
  deliberately regenerated.

The suite adds 80 synthetic TS10 cases and report/EARL integration tests. It compares
nine bounded atomic rules, not 44 automated controls. No site collection or
JavaScript execution occurs. Partial or automatic TS10 C remains forbidden. The
production report adapter is a separate milestone. See the [format](canonical-families.md)
and run `python3 scripts/verify.py`.
