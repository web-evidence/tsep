# Canonical laboratory / Laboratoire canonique

## Français

`examples/canonical_laboratory.py`, outil version **1**, compose les règles TS10
existantes de draft.7 avec une collecte HTTP réelle sur `127.0.0.1` et des
sérialisations DOM fournies. Il ne modifie ni le protocole, ni l’interpréteur,
ni les attentes du corpus. Les douze attentes du nouveau laboratoire sont figées
séparément avant l’implémentation. Le site est synthétique : ses défauts sont
construits, même lorsque les échanges et le navigateur sont réels.

### Ce que les scénarios montrent

Une famille explicite contient `/product` et `/product?color=blue`, avec
`/product` préféré. Chaque scénario dispose de sa propre base immuable, comportant
port éphémère et identifiant de campagne. La substitution de `{base}` est conservée
avant collecte, ainsi que membres, méthodes attendues, état `loaded`, contexte,
source de liens et racines sitemap. Aucun regroupement d’URL n’est deviné.

La référence et la correction attendent pass/inconclusive/pass/pass pour
A01/A02/A03/A04 : les déclarations, sitemaps et liens concordent, mais la comparaison
humaine des contenus manque. Les conflits HTTP Link/HTML, la réécriture JS,
la préférence redirigée ou 404, la variante dans le sitemap et le lien concurrent
établissent des échecs locaux. Un canonical relatif échoue au **critère TSEP
d’URL absolue** ; ce n’est pas une assertion selon laquelle tous les moteurs
ignorent toute URL relative.

Une omission est établie seulement dans un sitemap intégralement examiné. Les
scénarios avec index déclarent deux enfants ; le second existe dans la configuration
du serveur mais n’est volontairement **pas collecté**. Cela rend l’omission
indémontrable, sans effacer une variante concurrente déjà observée dans le premier
enfant. Ni 404, ni fichier inexistant, ni couverture complète ne sont inventés.

### Exécution et rejeu

```sh
python3 examples/canonical_laboratory.py serve --output /tmp/nouveau-laboratoire
```

Le serveur collecte les 12 scénarios, conserve leurs octets HTTP et prépare 35
reçus avant les navigations. `browser-tasks.json` énumère les URL finales et
contextes à observer. La préférence 404 n’a pas de représentation navigateur ;
son état requis reste absent. Scripts et styles sont en ligne, réponses non
compressées, `no-store`, CSP restrictive, aucune sous-ressource attendue. Le
journal conserve toutes les requêtes servies. Ctrl-C arrête le serveur et fige
le journal ; l’outil ne lance aucun navigateur lui-même. Toute requête imprévue
ou recharge invalide le bilan : conserver l’échec et recommencer une campagne
neuve. Le navigateur ouvre directement l’URL finale ; une éventuelle redirection
est mesurée par le client HTTP, pas parcourue dans le navigateur.

L’opérateur navigateur conserve un objet JSON indexé par ID de tâche, avec :
`url`, `dom` (sérialisation `document.documentElement.outerHTML`), `state`, `js`,
`agent`, `context`, `errors` (liste signalée par la page), `readyState`,
`observed_at`, `devLogs` (journal développeur complémentaire), et `browser`
(`name`, `version`, `user_agent`). Toute version dérivée de l’UA doit être qualifiée
comme déclarée par l’UA. Relever le DOM après le marqueur visible `loaded`, sans
le modifier ; conserver l’instant de lecture. Les erreurs de console, CSP et
réseau ne sont pas assimilées à un bilan exhaustif par les écouteurs de la page.

```sh
python3 examples/canonical_laboratory.py finish /tmp/nouveau-laboratoire \
  --observations /tmp/observations.json --capture-kind observed-browser \
  --output /tmp/nouvelle-livraison
python3 examples/canonical_laboratory.py replay /tmp/nouvelle-livraison \
  --output /tmp/nouveau-rejeu.json
```

`authored-fixture` est obligatoire pour les observations de test écrites à la
main ; elles ne prouvent pas une exécution navigateur. `observed-browser` est une
déclaration de provenance de l’opérateur, pas une authentification. Les originaux
et les lacunes sont conservés. Le rejeu ne collecte rien et ne réexécute pas JS.
Une différence aux attentes est conservée et fait échouer la commande de bilan.

### Composition des preuves

Le contrôle de liaison de `adapters/rendered.py` version 1 est réutilisé par
document. Son format exige un conteneur TS07 : celui-ci reste **inerte**, avec
`public_canonical: false`, politiques `transport-not-declared`, mention
`DO NOT EVALUATE`, même plan d’états TS10 et empreinte du plan de famille. Il
n’émet aucun verdict, rapport ou EARL TS07 dans ce parcours. Un appel manuel
à l’évaluateur générique peut produire inconclusive : le conteneur n’est pas un
nouveau format refusé par tous les outils. Seuls les états attribués par
`derive()` rejoignent la famille TS10. Le rejeu reconstruit exactement les
conteneurs depuis les captures et l’intention TS10, refuse des artefacts
supplémentaires et vérifie le rapport TS10 et ses dérivés.

URL, agent, pair loopback, dates, réponse complète, ligne exacte du journal,
marqueurs d’état, URL du document réellement chargée (`location.href`), rôle et contexte lient les acquisitions distinctes. Une unique
navigation navigateur par document est exigée. Les agents contenant `googlebot`
sont refusés pour le navigateur ; le client HTTP envoie ce littéral uniquement
comme contexte de test. Aucun Googlebot authentifié n’est observé.

Sans revue de contenu fournie, le résultat global reste NT ou NC, jamais C.
Aucune preuve d’indexation, de canonique choisie par un moteur, de classement,
d’exhaustivité d’un site ou de validation indépendante. Les dates et empreintes
locales ne sont pas des signatures. Les versions Python et empreintes du runtime
HTML sont enregistrées ; des résultats identiques ne prouvent pas l’identité
des environnements.

### Limite observée dans le navigateur intégré

La campagne du 10 octobre 2026 a conservé 35 DOM réellement observés. Le navigateur
intégré ajoutait un `div` vide `codex-browser-sidebar-comments-root` directement
sous `html`, après `body`. Le parseur TS10 strict les refuse avec
`Unsupported HTML root child`. Les associations restent attribuables, mais les
réussites DOM attendues ne sont **pas obtenues** dans cette campagne. Les captures
et le bilan divergent des attentes figées et restent conservés. Un diagnostic de
lecture avant snapshot/capture visuelle a trouvé le même nœud ; aucun élément n’a
été retiré et aucun attendu adapté.

« Lecture sans écriture » décrit la lecture effectuée, pas une garantie que
l’environnement navigateur n’ajoute rien. Toute nouvelle méthode doit être
annoncée avant collecte, sans reprises choisissant le moment donnant un pass.
Les résultats d’un autre navigateur appartiennent à une campagne distincte.
Le comportement face aux nœuds hors head/body reste une limite de l’interpréteur,
pas un défaut SEO automatiquement attribué au site.

## English

Tool version **1** composes existing draft.7 TS10 rules with real bounded loopback
HTTP and supplied DOM serializations. Twelve expectations are frozen separately
before implementation. No protocol, active interpreter or existing corpus change. Unexpected requests or
reloads invalidate the campaign; retain the failure and start a new one. Browser
navigations open final URLs directly; redirects are measured by the HTTP client.
The site and faults are synthetic; transport/browser executions may be real.

Each explicitly inventoried two-member family has an immutable per-scenario base.
The symbolic `{base}` substitution, ephemeral port, campaign ID, preferred URL,
member methods, loaded state, link population and sitemap roots are registered
before capture. No family grouping or exceptions are inferred.

Baseline/correction expect pass/inconclusive/pass/pass: manual content comparison
is absent, so no whole-control C. Contradictions include HTTP versus HTML, a JS
canonical rewrite, redirected/404 preference, competing sitemap and internal-link
URLs. Relative canonical failure is the TSEP absolute-URL criterion, not a claim
that every search engine rejects relative canonicals. Complete sitemap omission
fails. With an intentionally uncollected child, omission is inconclusive but an
observed competing URL still fails. The uncollected child is configured to exist;
missing evidence is not presented as a missing file or complete coverage.

Use `serve`, record the 35 tasks from browser-tasks.json in a real browser, stop
the listener, then `finish` and `replay` as above. One required 404 state remains
absent. Inline scripts/styles, no-store, uncompressed immutable responses and
restrictive CSP keep subresources out of scope. All served requests are logged.
The CLI does not execute a browser. Observation fields are documented above;
errors are page-reported, developer logs are supplementary, and UA-derived browser
versions must be labelled as reported. Authored unit DOMs use authored-fixture;
observed-browser is an operator assertion, not execution authentication.

Transport-only TS07 containers reuse rendered v1 attribution without producing
TS07 outcomes or reports. They explicitly carry undeclared policies, false
applicability, the exact TS10 state plan and family-plan digest. Replay reconstructs
them and the family input, rejects unexpected files, and validates TS10 report,
EARL, gate and calculated results. Only derived render records enter TS10.

Exact server-log rows, bytes, peer, agent, dates, context, document URL/role witnesses and DOM markers associate
separate acquisitions. A unique browser navigation per document is required;
browser agents containing googlebot are rejected. The source client's literal
header is not an authenticated engine. Replay has no network or JS execution.
Local hashes and dates are unsigned; no indexing, ranking, selected engine
canonical, exhaustive site assessment or independent validation is established.

The 10 October 2026 integrated-browser campaign retained 35 real DOMs containing
an auxiliary empty codex-browser-sidebar-comments-root DIV directly under HTML.
The strict TS10 parser returned Unsupported HTML root child; expected rendered
passes were not obtained. Attribution succeeded, but interpretation remained
inconclusive. Captures/results are retained without removing the node or changing
expectations. A pre-snapshot diagnostic also found the node. Read-only collection
does not guarantee a browser free of injected UI. Any new method/environment
requires a separate campaign; do not resample timing until a pass appears.
