# Draft.10 — automatisation bornée / bounded automation

Candidat local non publié / Unpublished local candidate. No qualification or release is claimed here.

FR : TS03-A01 et TS06-A01 conservent leur interprétation synthétique historique. Les nouvelles A02 comparent des sondes réelles à un plan préalable explicite. Une réussite A02 ne valide pas le contrôle complet : la matrice historique, les critères de contenu, les rôles et le cache restent séparés. Aucun dossier ancien n’est réécrit. Un nouveau rapport emploie cette édition explicitement ; sa portée reste affichée.

EN: TS03-A01 and TS06-A01 retain their historical synthetic interpretation. New A02 rules compare real probes with an explicit prior plan. A02 success does not validate the entire control: the historical matrix, content criteria, roles and cache remain separate. No old dossier is rewritten. A new report explicitly uses this edition and displays its scope.

FR : TS07-A02 ajoute un profil préalable pour une preuve Inspection Google brute, liée à l’URL et à une propriété autorisée, ou une déclaration explicite liée à la réponse. Le passage Google antérieur à la réponse observée reste une information historique, jamais une preuve actuelle automatique. Sans preuve suffisante : NT. TS07-A03 conserve le lecteur structuré et ses bornes : un navigateur de l’application peut fournir son état, mais ne représente jamais le rendu de Google.

EN: TS07-A02 adds a prior profile for raw Google Inspection evidence bound to the URL and an authorized property, or an explicit response-bound declaration. A Google crawl predating the observed response remains historical information, never automatic current evidence. Insufficient evidence: NT. TS07-A03 retains the structured reader and bounds: an application browser can supply its state, never Google's rendering.

FR : le lecteur des journaux CI accepte uniquement les BOM placés avant l’horodatage GitHub exact, conserve les empreintes et vérifie la réversibilité. Les reçus et validateurs ne changent pas. Les anciens journaux réellement réussis servent de témoins, sans relancer les tests. La réussite du contrôle court sur un nouveau main reste à observer après qualification et fusion.

EN: CI log reading accepts only BOMs before the exact GitHub timestamp, retains digests and verifies reversibility. Receipts and validators remain unchanged. Previously successful actual logs are witnesses without rerunning tests. A short-check success on a new main remains to be observed after qualification and merge.

## Sources consultées / consulted sources — 2026-10-26

- https://developers.google.com/crawling/docs/troubleshooting/http-status-codes — status codes do not establish indexing or Google's soft-404 classification.
- https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics — crawling, rendering and indexing are separate.
- https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect — indexed version only, no live inspection; exact URL/property required.

FR/EN : pages lues via l’outil de recherche ; pas de capture complète redistribuée (documentation tierce). Les liens, date et portée ci-dessus constituent la trace documentaire ; aucun changement de standard externe revendiqué. / Pages read through the search tool; no full capture redistributed (third-party documentation). URLs, date and scope above retain the documentary record; no external standard change claimed.

## Corrections de contre-revue / counter-review corrections

FR : TS03-A02 se limite aux deux routes existante et générée ; les anciennes pages déplacées ne sont pas jugées par cette sonde. TS06 : 404 reste NT, les paramètres de retour de connexion sont ignorés sans être conservés, et un défi sans paramètres est reconnu. Les données sources de draft.9 sont conservées dans une baseline explicite ; la garde historique applique un inverse vérifiable pour le seul raccord TS07. Les attentes atomiques historiques restent inchangées ; les deux cas de méthode A01 seul passent explicitement de C global à NT dans cette édition. Cette nouvelle édition exige toujours toutes ses règles pour un C global ; la sonde seule reste partielle.

EN: TS03-A02 is limited to the existing and generated routes; formerly moved pages are not assessed by this probe. TS06: 404 remains NT, login return parameters are ignored without retention, and a parameterless challenge is recognized. Draft.9 source controls are retained in an explicit baseline; the historical guard applies a verifiable inverse for the sole TS07 hook. Historical atomic expectations stay unchanged; the two A01-only method cases explicitly migrate from whole-control C to NT in this edition. This new edition still requires all its rules for whole-control C; the probe alone remains partial.

FR : changement normatif explicite : un C global sur TS03 ou TS06 exige désormais A01 **et** la sonde A02. Sous le nouveau profil d’accès TS07, un refus 401/403 adressé au seul client de test reste NT ; un Disallow prouvé reste NC. Les attentes atomiques des profils historiques sont conservées ; le statut global des deux cas de méthode A01 seuls devient NT en draft.10.

EN: explicit normative change: whole-control C for TS03 or TS06 now requires A01 **and** probe A02. Under the new TS07 access profile, a 401/403 denial to the test client alone stays NT; a proven Disallow stays NC. Historical profiles retain their atomic expectations; the whole-control status of the two A01-only method cases becomes NT in draft.10.

## Inventaire préalable / Prequalification inventory

FR : 1 398 tests découverts, 2 588 cas de conformité et 4 961 paires pour 100 règles. Les 21 cas supplémentaires de cette édition figurent dans le corpus distribué ; les 2 567 cas antérieurs sont conservés. Cet inventaire décrit ce qui doit être exécuté, sans annoncer une qualification réussie. L’horloge fixe d’import passe au 27 octobre, après la dernière observation synthétique du 26 octobre à 00:00:05 UTC ; son inverse de provenance conserve l’ancrage historique et les attentes.

EN: 1,398 discovered tests, 2,588 conformance cases and 4,961 pairs across 100 rules. This edition’s 21 additional cases belong to the distributed corpus; all 2,567 prior cases remain. This inventory describes required execution, not a successful qualification. The fixed import clock advances to 27 October, after the last synthetic observation on 26 October at 00:00:05 UTC; its provenance inverse preserves the historical anchor and expectations.

## Intégration et non-applicabilité / integration and non-applicability

FR : les 194 cas de méthode précédents conservent leurs preuves et résultats atomiques. Seuls deux statuts globaux C deviennent NT, car A02 n’est pas fourni ; huit cas de méthode supplémentaires couvrent A02 seul (pass/fail/indéterminé) et A01+A02 complet pour TS03 et TS06. Un inverse contrôlé restaure exactement le corpus précédent. Les gardes historiques utilisent une projection contrôlée de l’ensemble des 44 contrôles vers draft.9 ; toute modification non déclarée est refusée.

EN: the 194 previous method cases retain their evidence and atomic outcomes. Only two whole-control C statuses become NT because A02 is absent; eight additional method cases cover A02 alone (pass/fail/inconclusive) and complete A01+A02 for TS03 and TS06. A checked inverse restores the exact previous corpus. Historical guards use a checked projection of all 44 controls to draft.9; undeclared changes are rejected.

FR : le NA synthétique de TS06 reste possible par une revue d’inventaire positive, complète, datée et liée pour chaque cible. Aucune sonde A02 ne peut être sélectionnée ou fournie dans ce périmètre sans zone sensible. Une sonde ou un plan public contradictoire rend cette conclusion d’inventaire indéterminée ; une contradiction HTTP indépendante et étayée reste un échec. L’absence de preuve ne vaut jamais NA. Les anciennes archives et dossiers restent intacts.

EN: synthetic TS06 whole-control NA remains possible through a positive, complete, dated and bound inventory review for every target. No A02 probe may be selected or supplied within this no-sensitive-route scope. A conflicting public probe or plan makes that inventory conclusion inconclusive; an independently evidenced HTTP contradiction remains a failure. Missing evidence never means NA. Prior archives and dossiers remain intact.
