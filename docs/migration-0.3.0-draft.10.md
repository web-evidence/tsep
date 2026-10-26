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
