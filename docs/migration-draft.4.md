# Migration 0.1.0-draft.3 → 0.1.0-draft.4

## Français

Jalon TS07-A03 uniquement, sans publication. Identifiants TS01–TS44, titres hérités,
sévérités, profils et sources 1.1 inchangés. Format du rapport toujours `2` ;
`input_version: "1"` de conformance étendu sans changer l’entrée des quatre règles
précédentes. Conserver les anciens paquets et leurs empreintes.

- Un pass TS07-A03 exige maintenant http et html, en plus de render et intent.
  Réexaminer les anciennes conclusions dont A03 ne référençait pas la source.
- Préciser les états requis avant la capture ; relier chaque DOM à sa cible, sa
  trace source, son contexte et son scénario. Métadonnées ou capture manquantes :
  inconclusive, pas de C TS07 par simple succès d’A01/A02.
- Conserver fail lorsqu’un état complet attribuable contredit l’objectif, même si
  un autre état manque. Un retrait de noindex initial laisse A03 indéterminé si
  aucun état n’établit une autre contradiction ; A01 conserve le résultat source.
- Une exemption nécessite une revue documentée et ses pièces ; aucun NA à partir
  de « pas de JS » ou d’une liste vide. La suffisance du plan et la revue humaine
  maintiennent A03 en semiAuto, même lorsque le comparateur est exécuté par logiciel.
- Créer un nouveau rapport avec version/empreinte draft.4 après réévaluation, puis
  régénérer EARL. Ne pas seulement remplacer l’empreinte d’un ancien rapport.

La suite ajoute les captures source/DOM synthétiques et des tests d’intégration
vers le rapport et EARL. L’interpréteur ne lance pas JavaScript ou un navigateur.
TS10 et l’adaptateur de production vers le rapport restent des jalons séparés.
Voir [format](rendered-states.md) ; vérifier avec `python3 scripts/verify.py`.

## English

TS07-A03 milestone only, unpublished. TS01–TS44 identities, inherited titles,
severities, profiles and grid 1.1 sources are unchanged. Report format remains `2`;
conformance input_version 1 is extended without changing the earlier four rules'
inputs. Retain old bundles and their fingerprints.

- A TS07-A03 pass now requires http/html as well as render/intent. Reassess old
  conclusions where A03 did not reference its source.
- Fix required states before capture; bind every DOM to its target, source trace,
  context and scenario. Missing metadata/captures mean inconclusive; A01/A02 alone
  cannot yield C for TS07.
- Keep fail when a complete attributable state contradicts intent despite other
  missing states. Removing initial noindex leaves A03 inconclusive unless a state
  establishes another contradiction; A01 retains its source outcome.
- Exemptions need a documented review and supporting records, not “no JS” or an
  empty list. Plan adequacy and human review keep A03 semiAuto even when software
  executes the comparator.
- After reassessment, create a new report pinned to draft.4 and regenerate EARL.
  Merely replacing an old report's hash is not migration.

The suite adds synthetic source/DOM captures and integration tests through report
validation and EARL. The interpreter does not run JavaScript or a browser. TS10 and
the production report adapter remain separate milestones. See the [format](rendered-states.md)
and run `python3 scripts/verify.py`.
