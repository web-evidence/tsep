# Corrections partielles d’une famille / Partial family repairs

## Français

Laboratoire synthétique **version 1**, sous le contrat inchangé draft.18.
La recette de douze phases est figée dans
`tests/fixtures/canonical-partial-repair-v1.json`, empreinte voisine `.sha256`.
Elle a été écrite après un diagnostic de six entrées rédigées, avant
l’implémentation de ce laboratoire et sa collecte navigateur. Ce n’est pas une
qualification indépendante. Les anciennes recettes et captures sont conservées.

Une famille garde la même préférence `/product` et le même membre concurrent
`/product?color=blue`. `/catalog` est l’unique source de liens prévue, et
`/sitemap.xml` l’unique racine sitemap. L’URL `/landing` n’appartient pas à la
famille : elle rend visible une destination incorrecte, sans changer l’intention.

Les défauts sont précis : la variante se déclare canonical ; la préférence
répond 302 vers `/landing`, qui répond 200 ; le sitemap réintroduit la variante ;
le lien catalogue vise la variante. Une redirection de la préférence affecte
A01 et A02. Aucun jugement de compatibilité du contenu n’est fourni.

| Phase prévue | A01 | A02 | A03 | A04 | TS10 prévu |
| --- | --- | --- | --- | --- | --- |
| Témoin technique | pass | inconclusive | pass | pass | NT |
| Canonical seule incorrecte | fail | inconclusive | pass | pass | NC |
| Destination seule en redirection | fail | fail | pass | pass | NC |
| Sitemap seul contradictoire | pass | inconclusive | fail | pass | NC |
| Lien seul contradictoire | pass | inconclusive | pass | fail | NC |
| Défauts combinés | fail | fail | fail | fail | NC |
| Destination corrigée | fail | inconclusive | fail | fail | NC |
| Canonical corrigée | pass | inconclusive | fail | fail | NC |
| Sitemap corrigé | pass | inconclusive | pass | fail | NC |
| Lien corrigé | pass | inconclusive | pass | pass | NT |
| Variante réintroduite dans le sitemap | pass | inconclusive | fail | pass | NC |
| Régression corrigée | pass | inconclusive | pass | pass | NT |

Ce tableau est un **attendu**, pas la déclaration d’une observation réalisée.
Chaque résultat produit expose séparément attendu, constat calculé et accord.
Un désaccord conservé n’est pas corrigé en modifiant l’attente ou en remesurant.
Le passage NC → NT signifie que les contradictions détectées ont disparu dans
le périmètre prévu, tandis que la revue de contenu reste absente. Il ne signifie
ni conformité du site, ni validation de contenu, ni changement d’état Google.

### Collecte attribuée

`examples/canonical_partial_lab.py` réutilise le transport HTTP brut du
[laboratoire de navigation](same-navigation-laboratory.md), avec un serveur
limité à 127.0.0.1 et une origine unique sous `.localhost` par défaut. Une
calibration préalable conserve l’agent réellement reçu. L’agent n’est jamais
renommé Googlebot. Une calibration conditionnelle ou portant une session est
refusée ; ne jamais retirer ces en-têtes des preuves pour la faire accepter.

Le scellement fixe avant mesure les 36 tâches, les URL répétées, les identifiants
de navigation, l’intention, les lecteurs et les octets de chaque réponse. Pour
chaque phase, visiter dans l’ordre préférence, variante, catalogue. La navigation
préférée conserve ses deux sauts lorsqu’elle redirige. Le script de chaque page
exporte un seul état rendu avec l’inventaire 2 complet et sa sérialisation.
L’HTML source et le DOM proviennent de cette même navigation.

Le catalogue effectue exactement un fetch du sitemap de la même origine, après
load et avant l’inventaire. Ce GET emploie le client navigateur réel, sans cache
ni credentials. Le serveur conserve requête/réponse exactes ; la page fournit
aussi URL, statut et SHA-256 du corps reçu. Ces valeurs doivent concorder. Ce
fetch XML est une collecte auxiliaire déclarée, pas un DOM de sitemap.

L’identifiant de navigation, qui inclut la phase, figure aussi dans un span du
DOM. Le vérificateur exige un témoin unique et sa valeur exacte dans l’arbre
conservé, au-delà de l’enveloppe d’export. Un arbre d’une phase antérieure reste
refusé même avec une enveloppe et des empreintes nouvelles.

Les connexions TCP anticipées qui n’envoient **aucun octet HTTP** restent dans
le journal avec leurs pièces brutes. Le laboratoire les compte séparément :
requête de zéro octet, erreur de fermeture/en-tête vide ou délai, et réponse
diagnostique exacte doivent concorder. Elles ne sont ni des GET ni des preuves
SEO. Un seul octet reçu, une session, un agent divergent ou une véritable requête
malformée reste refusé. Le premier essai navigateur refusé pour cette raison est
conservé ; le nouveau classement ne réécrit pas ce résultat historique.

Toutes les tentatives restent dans le journal. Erreur de transport, URL hors ordre, export
absent ou doublé, agent divergent, pièce modifiée, chronologie incohérente ou
requête inexpliquée empêchent la finalisation. Le rejeu vérifie aussi que les
octets réellement servis correspondent aux octets planifiés, même si un journal
modifié a été réempreinté. Les empreintes ne prouvent pas l’authenticité de la
collecte ; un ensemble cohérent pourrait être fabriqué.

### Commandes et limites

```sh
python3 examples/canonical_partial_lab.py serve --output /tmp/family-capture
# Visiter calibration_url une fois dans le navigateur choisi.
python3 examples/canonical_partial_lab.py seal /tmp/family-capture \
  --browser-name NOM_OBSERVE --browser-version VERSION_OBSERVEE
# Visiter les 36 tâches dans leur ordre et conserver leurs reçus affichés.
# Arrêter ce serveur par Ctrl-C afin de fermer le journal.
TSEP_SOURCE_NODE=/chemin/vers/node24 python3 examples/canonical_partial_lab.py finish \
  /tmp/family-capture --observations /tmp/family-observations.json --output /tmp/family-delivery
TSEP_SOURCE_NODE=/chemin/vers/node24 python3 examples/canonical_partial_lab.py replay /tmp/family-delivery
```

Chaque dossier de sortie doit être neuf. Le fichier d’observations contient pour
chaque identifiant de tâche `navigation_started_at`, `observed_at` (ISO avec
fuseau, réellement relevés) et `receipt` (SHA affiché sans le préfixe). Ne pas
inventer des horaires rétrospectifs. Le navigateur et sa version sont déclarés
par l’opérateur ; leur sincérité et l’intégrité des API ne sont pas authentifiées.

Les profils source préalables sont `html-tree-canonical-v1` et
`html-tree-links-v2`, les états `structured-inventory-v2`. Node 24 doit être fourni
séparément pour les sources ; aucune installation automatique ou repli après
échec. L’absence de runtime produit des inconnues conservées. Le rejeu conserve
les versions exactes des pièces et de l’environnement. Le lecteur n’exécute
aucun navigateur au rejeu ; les observations originales ne sont pas une
simulation du rendu d’un moteur. Un état load ne couvre pas les autres états.

La livraison contient douze entrées natives, leurs bundles et rejeux, ainsi
qu’une demande finale de revue **vide**. `REVIEW.fr-en.md` pose la question,
`review-pages.json` regroupe les deux pages et leurs états ; la demande garde
les pièces et empreintes auxquelles une réponse fournie devra être liée. Le
contenu source capturé est une preuve à lire, pas du code à exécuter.

Les tests unitaires utilisent des clients et arbres **rédigés**. Ils vérifient
le transport, la conservation des refus/inconnues et l’import/rejeu hors réseau ;
ils ne constituent pas la campagne navigateur réelle. Aucune revue humaine,
recette visuelle des rapports, collecte Edikka, Search Console ou certification
n’est déduite de ces tests. Ce laboratoire local n’est pas un collecteur Web
public : son instrumentation suppose des pages synthétiques sous son contrôle.

## English

Synthetic laboratory **version 1** applies unchanged draft.18 to one fixed family
through twelve predeclared phases. The neighboring SHA-256 pins the JSON recipe.
Expectations were authored after a six-input engineering diagnostic and before
this implementation and actual browser collection; they are not independently
validated. Earlier recipes and captures remain intact.

The preferred `/product`, variant `/product?color=blue`, one link source
`/catalog` and sitemap `/sitemap.xml` stay fixed. Faults are a self-canonical
variant, preferred 302 to an out-of-family `/landing` returning 200, a competing
sitemap entry and a competing catalog link. A preferred redirect can fail both
A01 and A02. Isolated faults precede combined faults and sequential repairs;
a sitemap regression follows convergence. Expected statuses are in the table
and recipe, separate from measured outcomes. No content judgment is supplied,
so complete technical convergence still ends in NT, not C.

The loopback-only server uses a unique `.localhost` origin by default. A prior
calibration records the actual HTTP User-Agent; session/conditional calibration
is rejected without stripping headers. Sealing freezes exact response bytes,
intent, source/DOM profiles, 36 ordered HTML navigations and navigation IDs.
Each actual browser visit captures every redirect hop and one complete inventory
2 tree/serialization from that same navigation. The catalog page performs one
declared same-origin, credential-free, no-store sitemap fetch before its snapshot.
Its reported URL/status/body hash must match the retained raw browser HTTP request
and XML response. That auxiliary XML fetch is not a sitemap DOM observation.

The unique navigation ID includes the phase and appears in a DOM span. Offline
validation requires its exact value in the retained tree, not merely the export
envelope. An older phase tree is rejected even under a new envelope and receipt.

Anticipatory TCP connections sending zero HTTP bytes remain in the log and are
counted separately. Exact empty request, known idle/empty-header error and diagnostic
response are checked. These are not GETs or SEO evidence; a single received byte
still prevents this classification. The first refused browser calibration is
retained, not retrospectively renamed successful.

All attempts remain logged. Unplanned/reordered requests, missing/duplicate exports,
changed agents/evidence, incorrect times or unexplained requests prevent completion.
Offline derivation compares served bytes with the frozen plan, even after a log
is rehashed. Hashes and coherent bindings do not authenticate collection. Browser
identity is operator-declared; API integrity is not attested.

Use the commands above with new folders. Record real zoned start/observation
timestamps and the displayed receipt per task; stop the server before finishing.
Supply Node 24 explicitly for the declared source profiles, without automatic
installation or fallback. Missing runtime remains inconclusive; expected/actual
mismatches are retained. Replay validates the raw acquisition, regenerates native
inputs and replays all bundles without rerunning a browser or external collection.

The final blank review includes the exact compatibility question, two complete
page records, original evidence and bound empty response fields. Neither a test
fixture nor an AI discussion fills a human judgment. Unit HTTP clients and trees
are authored tests, not real browser observations. A load state does not establish
all future states, Google rendering/indexing/ranking, site conformity or real
Edikka repairs. This instrumented synthetic server is not a public arbitrary-URL
collector. Normative rules, versions and historical results do not change.
