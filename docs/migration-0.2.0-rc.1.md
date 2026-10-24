# Migration — TSEP 0.2.0-rc.1

## Français

Cette préversion est une édition distincte de 0.1.0-draft.47. Elle conserve les identifiants TS01–TS44 et tout le travail déjà présent dans cette archive. Elle n’ajoute aucun contrôle ni aucune règle atomique : le périmètre reste 28 contrôles à règles exécutables et 67 règles. TS03-A01 reste une vérification semi-automatique d’une matrice HTTP synthétique .invalid, avec 13 cas contradictoires figés.

Ne réécrivez pas les rapports, exports ou reçus historiques. Ils restent liés à leur version, leur empreinte, leurs outils et leurs entrées d’origine. Un rapport RC1 doit annoncer 0.2.0-rc.1 et l’empreinte de sa source protocol.json RC1 ; ne remplacez pas la version ou l’empreinte des dossiers draft.47. Importez l’archive RC1 dans l’application comme moteur séparé ; l’application conserve sa propre version. Vérifiez la provenance et l’empreinte avant l’évaluation, exportez le dossier, contrôlez le manifeste et les sommes, puis rejouez cet export hors application. Enregistrez un reçu RC1 distinct des reçus draft.47.

Pour TS03, le plan préalable, sa liaison de configuration, les trois états de route, les captures GET complètes et les marqueurs UTF-8 littéraux restent requis. Une contradiction complète est fail ; les informations manquantes, ambiguës, dupliquées, partielles 206/304 ou un plan invalide restent inconclusive, sauf contradiction complète déjà établie. Une matrice synthétique .invalid ne qualifie ni l’existence réelle d’une URL, ni la disponibilité persistante, ni une classification soft 404 de Google, ni l’exhaustivité d’un site, l’indexation ou le ranking.

RC1 est une préversion. Les résultats de vérification logicielle et l’intégration app attestent uniquement les octets, tests et parcours explicitement consignés. Les parcours applicatifs futurs TS01 et TS04, puis TS07 et TS10, sont un plan d’intégration séparé ; ils ne sont ni implémentés ni reçus par cette migration.

## English

This prerelease is a distinct edition from 0.1.0-draft.47. It retains TS01–TS44 and all work already present in that archive. It adds no control or atomic rule: the scope remains 28 controls with executable rules and 67 rules. TS03-A01 remains a semi-automated check over a synthetic .invalid HTTP matrix, with 13 frozen contradictory cases.

Do not rewrite historical reports, exports or receipts. They remain bound to their original version, fingerprint, tools and inputs. An RC1 report must declare 0.2.0-rc.1 and the fingerprint of the RC1 protocol.json source; do not replace the version or fingerprint in draft.47 records. Import the RC1 archive into the application as a separate engine; the application keeps its own version. Verify provenance and the fingerprint before assessment, export the dossier, check its manifest and digests, then replay that export outside the application. Record an RC1 receipt distinct from draft.47 receipts.

For TS03, the prior plan, bound configuration, three route states, complete GET captures and literal UTF-8 markers remain required. A complete contradiction is fail; missing, ambiguous, duplicated, partial 206/304 information or an invalid plan remain inconclusive unless a complete contradiction is already established. A synthetic .invalid matrix establishes neither a real URL’s existence nor persistent availability, Google soft-404 classification, site completeness, indexing or ranking.

RC1 is a prerelease. Software verification results and app integration attest only the exact bytes, tests and flows recorded. Future application flows for TS01 and TS04, then TS07 and TS10, are a separate integration plan; they are neither implemented nor received by this migration.
