# TSEP 0.2.0-rc.1 — Release candidate / Préversion

## Français

Préversion destinée à la préparation du lancement du 19 octobre 2026. Elle fige le périmètre intégré complet TS01–TS44 à partir de v0.1.0-draft.47 ; ce n’est pas une version stable, une certification ni une norme reconnue. Le protocole conserve 44 contrôles, dont 28 avec 67 règles atomiques exécutables. Les autres contrôles, documents, outils et limites restent inclus dans le périmètre livré.

La règle la plus récemment ajoutée, TS03-A01 (draft.47), est conservée sans extension : comparaison semi-automatique de réponses HTTP fournies pour un plan synthétique préalable .invalid et de marqueurs littéraux de corps. Sa fixture spécialisée contient 13 cas contradictoires. L’import/export/rejeu app r2 a été reçu séparément pour l’archive draft.47 : 12 anciens succès conservés sans relance, un cas additionnel évalué inconclusive, contrôle agrégé NT. Tout reçu RC1 est distinct et lié au SHA exact de l’archive importée ; son état est indiqué dans le dossier de release, hors de l’archive elle-même. Aucun résultat réel de site n’est prétendu.

La matrice distingue les règles exécutables, les corpus synthétiques, l’usage réel vérifié et l’intégration applicative. Les tests synthétiques vérifient des mécanismes et des bornes. Les exercices localhost/loopback ne sont pas des visites de production. Aucune conformité globale, identité d’agent, crawl, indexation, ranking ou adoption n’est déduite.

La préversion conserve les résultats négatifs et indéterminés. Voir la [migration](migration-0.2.0-rc.1.md), le [tableau des 44 contrôles](control-implementation-status.md) et le [dossier d’intégration applicative](app-integration-roadmap.fr.md). Les instructions de collecte n’autorisent pas à contacter un site sans plan approuvé. La version de l’application est indépendante de celle du moteur TSEP.

Les résultats de vérification locale et CI distante seront publiés comme faits seulement après observation du commit et des runs correspondants.

## English

Prerelease intended to prepare for the 19 October 2026 launch. It freezes the complete integrated TS01–TS44 scope from v0.1.0-draft.47; it is not a stable release, certification or recognized standard. The protocol retains 44 controls, including 28 with 67 executable atomic rules. The remaining controls, documents, tools and limitations stay within the delivered scope.

The most recently added rule, TS03-A01 (draft.47), is carried forward without extension: a semi-automated comparison of supplied HTTP responses against a prior synthetic .invalid plan and literal body markers. Its dedicated fixture has 13 contradictory cases. The app r2 import/export/replay was separately received for the draft.47 archive: 12 earlier successes retained without rerun, one additional case assessed as inconclusive, aggregate control NT. Any RC1 receipt is separate and bound to the exact SHA of the imported archive; its status is stated in the release record, outside the archive itself. No real-site result is claimed.

The matrix distinguishes executable rules, synthetic corpora, verified real use and application integration. Synthetic tests check bounded mechanisms. Localhost/loopback exercises are not production-site visits. No global conformity, agent identity, crawl, indexing, ranking or adoption is inferred.

The prerelease retains negative and indeterminate results. See the [migration](migration-0.2.0-rc.1.md), [44-control status table](control-implementation-status.md), and [application integration dossier](app-integration-roadmap.en.md). Collection instructions do not authorize a site contact without an approved plan. The application version is independent from the TSEP engine version.

Local verification results and remote CI runs will be stated as facts only after observing the corresponding commit and runs.
