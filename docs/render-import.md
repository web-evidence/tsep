# Browser state import / Import d’états navigateur

## Français

L’outil `adapters/rendered.py` version **1** prépare puis importe des sérialisations
DOM fournies pour TS07-A03. Il applique **draft.7 sans modification normative**.
L’évaluateur ne lance toujours aucun navigateur. Ce nouveau parcours est limité
au laboratoire synthétique contrôlé sur `127.0.0.1` : deux acquisitions distinctes,
client HTTP puis navigateur, reçoivent exactement la même réponse HTTP complète.
Ce rapprochement ne convient pas automatiquement à un site public variable.

1. Déclarer intention, contexte et états requis avant la collecte HTTP source.
2. `python3 adapters/rendered.py prepare source.json --output receipt.json`
   fige les octets du fichier source, la trace, la réponse finale, le plan, le
   contexte et les empreintes des outils. Le reçu précède les navigations/DOM.
3. Observer les états dans un navigateur réel par le parcours déclaré. Conserver
   les sérialisations `document.documentElement.outerHTML`, leur date de lecture,
   le navigateur/version observables, le JavaScript et les erreurs explicitement
   recueillies. Ne pas remplacer une erreur absente par une liste vide supposée.
4. `python3 adapters/rendered.py import source.json --receipt receipt.json
   --browser browser.json --server-log requests.jsonl --output nouveau-dossier` conserve les originaux,
   dérive l’entrée et construit le rapport synthétique. Rejeu sans réseau :
   `python3 adapters/rendered.py replay nouveau-dossier`.

Le fichier navigateur déclare `capture_version: "1"`, `receipt_sha256`,
`server_log_sha256`, `method`
(nom/version/description), `browser` (nom/version/`user_agent`), et `states`. Chaque
élément cite `log_index` (base zéro) et `log_line_sha256` (ligne avec sa fin de
ligne). Il a
`state` suivant [le contrat existant](rendered-states.md), plus `navigation` : URL,
`observed_at`, `complete: true` et `response` (octets HTTP encodés v2 ou texte v1).
La réponse de navigation provient ici du journal serveur, pas d’une interception
réseau du navigateur. Le rapprochement utilise URL de campagne, agent et dates.
Le journal est figé après arrêt du serveur ; la ligne citée doit correspondre
exactement à la navigation, au pair 127.0.0.1 et à l’agent navigateur déclaré,
distinct du client googlebot. Les marqueurs DOM du laboratoire doivent confirmer
l’état, JavaScript exécuté, le contexte, l’agent, les erreurs et la date d’action.
Une capture avant clic étiquetée après clic perd ainsi son attribution.
Les requêtes demeurent distinctes ; l’UA du client littéral `googlebot` ne prouve
pas une visite de Googlebot. Une version issue de l’UA est déclarée comme telle.

Une mauvaise réponse, URL, chronologie ou liaison supprime **seulement dans
l’entrée dérivée** le digest d’attribution de cet état. `browser.json` reste
inchangé et `association.json` explique la transformation. Les états manquants,
erreurs et contradictions restent visibles. Un échec attribuable dans un autre
état n’est pas effacé. Le comparateur actif produit le verdict, pas le scénario
attendu. Sans revue d’accès, A02 demeure indéterminé : aucune conclusion C.

`examples/rendered_ts07_lab.py --output nouveau-laboratoire` démarre cinq pages,
collecte leurs sources et prépare les reçus, puis attend l’opérateur navigateur.
Ctrl-C arrête le serveur. Les attentes et contre-exemples ont été gelés avant
l’implémentation dans `tests/fixtures/render-import-cases.json`. Aucun DOM n’est
créé par ce serveur. Scripts et styles sont en ligne, aucune sous-ressource
attendue, CSP restrictive, URL de campagne unique, `no-store`, sans compression.
Le journal conserve toutes les réponses servies, y compris hors périmètre.

Limites : aucune preuve d’indexation, de classement ou de comportement moteur ;
plan limité à deux états ; sérialisation DOM plutôt qu’octets source ; journal
serveur et UA déclaratifs ; instrumentation des erreurs limitée au laboratoire.
Les empreintes détectent des incohérences, elles ne signent ni l’auteur ni la date
ni l’exécution. Une falsification cohérente de tous les fichiers n’est pas exclue.
Les fixtures unitaires restent des DOM écrits, jamais des exécutions navigateur.

## English

Tool format **1**, `adapters/rendered.py`, imports supplied DOM serializations
without changing draft.7. It does not execute a browser. Scope is a controlled
synthetic loopback laboratory with immutable uncompressed responses: the source
client and browser are **separate acquisitions**, associated by campaign URL,
recorded agent/time and exact full HTTP response bytes from the server log.
This is not a generic provenance claim for changing public sites.

Declare intent/required states before source collection, run `prepare` before
browser navigation, retain real read-only DOM serialization observations, then
`import` and `replay` using the commands above. The browser envelope declares
capture_version, exact receipt SHA-256, explicit method name/version/description,
browser name/version/user_agent, server_log_sha256 and states. Each item cites
a zero-based log_index and SHA-256 of the exact log line including its newline.
The frozen server log is supplied with --server-log; its cited record must match
the navigation, declared browser agent (not googlebot) and loopback peer.
Laboratory DOM markers must confirm state, executed JS, context, agent, errors
and event time, so a pre-click capture cannot be labelled post-click. Each item
has the existing contract's `state`
and a `navigation` containing url, observed_at, complete and raw encoded response.
Version derived from a visible User-Agent must be labelled UA-reported.

Bad response, chronology or attribution revokes only that state's binding in the
derived input; original bytes and reasons are preserved. Missing states/errors
are never repaired, and a separately attributable failure is retained. Active
reference evaluation supplies outcomes. No access review is invented; this tool
rejects source inputs containing reviews or pre-existing render/exemption data.
No whole-control C can result from this workflow.

The laboratory command starts five prefrozen synthetic scenarios, collects source
HTTP and prepares receipts, then waits for a browser operator; Ctrl-C stops it.
All scripts/styles are inline, no expected subresources, unique campaign URLs,
no-store and restrictive CSP. Every served request is logged. It does not create
DOM captures. Unit DOM fixtures remain authored, not browser executions.

Local timestamps, hashes, supplied browser metadata and server logs are not
signed execution evidence. The bounded two-state plan, DOM serialization and
laboratory error instrumentation cannot establish engine rendering, indexing,
ranking, comprehensive JS health or independent validation. Replay is offline;
record runtime differences rather than claiming environmental equivalence.
