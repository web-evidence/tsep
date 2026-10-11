# Controlled critical-content laboratory / Laboratoire de contenu critique

## Français

Ce laboratoire applique les trois règles TS44 de draft.24 à **quatre variantes
prévues avant l’exécution**. Les six échanges HTTP et les journaux du serveur sont
réellement produits sur une origine numérique 127.0.0.1 temporaire. Le contenu,
les revues et les états de comparaison sont fictifs : **DOM rédigé, non observé
dans un navigateur**. Aucune collecte Edikka ni visite d’un fournisseur d’IA.

| Variante | Pièce réellement servie | Attente TS44 avec lecteur qualifié |
| --- | --- | --- |
| HTML serveur | Fait, référence, date et version présents dans le HTML | C, sous les hypothèses de revue fictives |
| Fait injecté | Bloc du fait vide ; sa valeur apparaît seulement dans un script | NC : chemin sans JS incomplet ; cohérence indéterminée |
| JSON lié | Page reliant explicitement une ressource complète et cohérente | C, sous les hypothèses de revue fictives |
| JSON périmé | Ressource complète, mais version r1 au lieu de la version r2 prévue | NC : accès réussi, cohérence échouée |

Les six réponses sont HTTP 200. Les résultats différents proviennent du contenu
et de ses relations, pas du seul statut HTTP. La valeur fictive « 1.8 s » n’est
pas une mesure de performance. La référence de citation utilise un domaine
réservé à l’exemple et n’est jamais récupérée. L’exécution n’établit ni vérité du
fait, ni lecture réelle d’un agent, ni équivalence d’un vrai rendu navigateur.

### Recette et exécution

`tests/fixtures/critical-content-laboratory-v1.json` conserve la recette figée le
11 octobre 2026, après qualification des règles TS44 mais avant implémentation
du laboratoire. Son SHA-256 est
`337c3c2922a86e0847e42ab309ae699307c2040a3519013f5c4f3d7f198a2169`.
Les quatre templates héritent de cas rédigés antérieurs ; leurs dates fictives
ne sont pas réutilisées comme dates de collecte. Les URL de test sont rattachées
au port local réellement ouvert. Inventaires, chemins, corps attendus, fenêtre
et revue synthétique du plan sont enregistrés **avant la première requête**.

Le serveur et le client n’utilisent ni DNS, ni proxy, ni destination externe.
Chaque requête anonyme GET est bornée à trois secondes et 16 Kio de réponse.
Le serveur attribue un identifiant par requête ; le journal retient heure,
URL, client, pair, code et empreinte du corps. Les octets HTTP complets sont
conservés sans nouvelle mesure lors du rejeu. Les réponses et les journaux sont
comparés à la recette, à la fenêtre déclarée et à leur ordre d’exécution.

Le DOM rédigé est créé après les échanges de sa variante et lié à sa réponse
page ; il conserve cette provenance même si le transport HTTP est observé.
Les revues de contexte restent des jugements synthétiques, distincts d’une
relecture humaine. La fenêtre dure deux secondes ; interprétation et revues
synthétiques suivent sa clôture. Un dépassement ou une interruption conserve
les échanges déjà obtenus et un reçu d’échec ; aucun dossier incomplet ne passe
pour un laboratoire réussi.

### Utilisation et rejeu

Python 3.9+ suffit pour le transport. Le lecteur HTML/URL de TS44 nécessite un
Node 24 explicitement fourni pour couvrir les attentes conclusives. Aucune
installation, recherche automatique de runtime ou collecte extérieure :

```sh
TSEP_SOURCE_NODE=/absolute/path/to/node24 python3 examples/critical_content_laboratory.py run --output /tmp/ts44-experiment
TSEP_SOURCE_NODE=/absolute/path/to/node24 python3 examples/critical_content_laboratory.py replay /tmp/ts44-experiment --output /tmp/ts44-replay.json
```

Choisir des sorties nouvelles et un parent existant. `run` ouvre le serveur
temporaire ; `replay` vérifie la recette, les plans, captures, journaux, liaisons,
dossiers et résultats **sans réseau**. Il faut conserver les outils et le
runtime exacts du dossier. Le code de sortie est 0 si toutes les attentes sont
retrouvées, 2 pour une exécution complète qui ne les retrouve pas, 1 pour une
erreur. Sans Node qualifié, les inconnues restent visibles ; les attentes figées
ne sont pas réécrites et la réussite complète n’est pas annoncée.

Les empreintes détectent les modifications des pièces mais n’authentifient pas
un dossier entièrement fabriqué puis resigné. Les tests comprennent des corps,
journaux, plans, provenances ou attributions modifiés et une interruption après
la première requête. Les rapports HTML doivent être placés **hors des dossiers
scellés**. Ce laboratoire ne change aucune règle normative et ne clôt pas
l’application réelle à Edikka ni la qualification des états navigateur.

## English

Four prefrozen variants apply draft.24 TS44. Six HTTP exchanges and native server
records are actually produced on a temporary numeric IPv4 127.0.0.1 origin.
Content, reviews and comparison DOMs remain fictional: **authored DOM, not observed
in a browser**. No Edikka collection or provider visit is established.

Expected outcomes with the qualified reader: complete server HTML C; a fact only
present in a script NC (no-JS delivery fails, coherence remains unknown); coherent
explicitly linked JSON C; stale linked JSON NC (access passes, version coherence
fails). All six responses are HTTP 200. C is conditional on fictional supplied
reviews, not human validation or factual truth. The example value 1.8 s is not a
performance measurement; its reserved example citation URL is never fetched.

The recipe file and fingerprint above were frozen after TS44 method qualification
but before laboratory implementation. Prior authored template dates are not reused
as collection dates. Test URLs are bound to the actual local port. Plans, inventory,
delivery paths, expected bodies, window and synthetic scope review are recorded
before the first request. Server and client use no DNS, proxy or external address.
Each anonymous GET has a three-second total timeout and a 16-KiB response bound.
Per-request server IDs, times, URLs, clients, peers, status and body fingerprints
are retained alongside complete HTTP exchanges and execution intervals.

The authored DOM is created after its variant's exchanges and bound to the page
response, retaining its synthetic provenance. Synthetic context judgments follow
the two-second evidence window; no human review is invented. Interrupted or late
collection retains available exchanges and an error receipt rather than a success
claim. The commands above require new outputs with existing parents. Python 3.9+
supports transport; explicit Node 24 is needed for conclusive HTML/URL coverage.
No automatic runtime discovery or installation occurs.

Offline replay checks source/recipe identities, prior plans, requests, responses,
native logs, time bounds, input bindings and exact bundle observations/results.
It does not reconnect. Keep the original exact tools/runtime. Exit 0 means all
fixed expectations matched; exit 2 means complete execution without full agreement,
including an unavailable optional runtime; exit 1 reports an error. Missing Node
does not rewrite expected results or become conclusive success.

Integrity checks do not authenticate an entirely fabricated and rehashed dossier.
Tests alter bodies, logs, plans, provenance and attribution, and interrupt after the
first request. Keep rendered HTML outside sealed bundles. No normative rule changes,
real-browser qualification, real agent behavior or Edikka conformity follow merely
from this experiment.
