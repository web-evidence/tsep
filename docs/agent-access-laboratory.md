# Controlled agent access laboratory / Laboratoire d’accès des agents

## Français

Six scénarios figés avant l’implémentation mettent TS43 à l’épreuve. Le serveur et
les documents d’opérateur sont fictifs ; les huit requêtes HTTP et les journaux
JSONL sont réellement produits sur 127.0.0.1. Aucune collecte Edikka ni visite
d’un fournisseur d’IA. Le laboratoire ne contacte pas d’autre adresse, n’utilise
ni DNS ni proxy et impose trois secondes et 16 Kio par réponse.

| Scénario | Traitement fixé avant les requêtes | Attente figée TS43 |
| --- | --- | --- |
| User-Agent seul | Accepter le client et le corps exact prévu | C pour ce test documenté |
| Filtre d’identité fictif | Refuser le client local non reconnu | C, avec réponse 403 |
| Adresse dans X-Forwarded-For | Refuser encore : le serveur compare le pair du socket | C, avec réponse 403 |
| Filtre supprimé volontairement | Le plan exige encore le refus ; le serveur laisse passer | NC |
| Identifiant ancien renvoyé par le cache | Corps attendu, mais identifiant d’une autre requête plus ancienne | NT : corrélation non établie |
| Redirection | Conserver et rapprocher les deux échanges | C pour cette chaîne |

La préparation du cache est une huitième requête, antérieure aux plans des six
scénarios, avec OtherClient/1. Les identifiants sont générés par le serveur ; dans
le scénario cache, la réponse conserve volontairement celui de cette préparation,
alors que le journal enregistre la nouvelle requête sous un nouvel identifiant.
La vérification temporelle refuse la fausse attribution avant de comparer les
clients. L’export contient les huit lignes, y compris la préparation hors fenêtre.

Les revues sont des **hypothèses synthétiques rédigées**, jamais une relecture
humaine. Pour éprouver le garde-fou temporel, le cas cache contient explicitement
un jugement fictif trop confiant sur la fraîcheur de l’identifiant. Le rapport
reste NT malgré ce jugement. Dans un dossier réel, il faudrait obtenir et conserver
les véritables qualifications de journaux et d’identité requises par le contrat.

L’autorisation fictive utilise seulement 192.0.2.0/24, qui exclut le pair loopback.
Elle démontre le comportement de ce serveur d’essai, sans qualifier une méthode
réelle d’authentification d’un opérateur ni la sécurité d’un serveur de production.
Les hypothèses de source, le plan, la commande sous forme d’appel de fonction
Python, les captures brutes, l’export natif et les trois résultats atomiques sont
retenus. Les C portent sur le périmètre du client de test ; aucun accès réel de
l’opérateur n’en découle.

Depuis une distribution extraite, choisir des sorties nouvelles :

```sh
python3 examples/agent_access_laboratory.py run --output /tmp/ts43-experiment
python3 examples/agent_access_laboratory.py replay /tmp/ts43-experiment --output /tmp/ts43-replay.json
```

La première commande ouvre un serveur loopback temporaire. Le rejeu vérifie les
empreintes, la recette, les plans, les intervalles, les captures, les journaux et
les dossiers calculés, sans réseau. Il nécessite les mêmes fichiers d’outils et
le même environnement de rejeu exact. Il ne prouve pas l’authenticité d’un dossier
entièrement réécrit et resigné. Des essais interrompus peuvent garder des fichiers
partiels ; ils ne sont pas des expériences réussies. Les pages HTML de consultation
doivent rester **à côté** des dossiers scellés, jamais ajoutées à leur contenu.

## English

Six scenarios were frozen before implementation. The site, operator documents
and supplied reviews are fictional; eight HTTP requests and native JSONL records
are actually produced on numeric 127.0.0.1. There is no Edikka collection, provider
visit, DNS or proxy. Each request is bounded to three seconds and 16 KiB.

Expected outcomes: UA-only acceptance with the exact planned body (C); denial of
the unrecognized local client by a fictional identity filter (403, C); the same
denial despite X-Forwarded-For spoofing (403, C); deliberate removal of the filter
contrary to the prior refusal plan (NC); a cached old response ID (NT); and complete
two-hop redirect correlation (C). These C outcomes describe test-client evidence,
never actual operator access. The fictional allowlist is 192.0.2.0/24; this is not
a production security assessment or a qualified provider-authentication method.

The eighth request primes the cache before the six plans using OtherClient/1.
For the later cached response, the server deliberately returns that earlier ID
while logging a fresh ID for the actual request. The log export retains all eight
records, including the primer outside the test window. Correlation checks time
before comparing client fields, so the old record cannot become an attributable
contradiction or a successful match.

All reviews are **authored synthetic assumptions, not human reviews**. The cache
case deliberately supplies an overconfident fictional per-response-ID judgment
to exercise the independent temporal guard; it still yields NT. Real use requires
the actual supplied source/log/identity qualifications described by the contract.
The plan, Python function-call invocation record, raw HTTP exchanges, native log
export and all three atomic results remain available.

The commands above require new output paths. Run opens a temporary loopback server;
replay checks hashes, recipe, plans, intervals, captures, logs and exact bundles
without network. It needs the same tool sources and exact replay environment. It
does not authenticate an entirely rewritten and rehashed dossier. Failed runs may
leave partial evidence, never a success claim. Keep consultation HTML outside
sealed bundles. [Evidence contract](agent-access-evidence.md) and
[frozen recipe](../tests/fixtures/agent-access-laboratory-v1.json).
