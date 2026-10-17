# TS03-A01 — Matrice synthétique des états HTTP / Synthetic HTTP state matrix

Statut : candidat 0.1.0-draft.47. Cette règle compare des entrées rédigées à l’avance à des réponses HTTP fictives. Elle ne visite aucun site et ne constitue ni une certification ni une qualification réelle.

Status: candidate 0.1.0-draft.47. This rule compares predeclared inputs with fictional HTTP responses. It visits no site and is neither a certification nor a real-world qualification.

## Entrées et méthode / Inputs and method

Le plan intent.ts03_response déclare son périmètre, une revue d’exercice explicitement synthétique, au moins une route de chaque état existing, removed, nonexistent, les statuts permis et les marqueurs de corps. configuration.ts03_response.plan_sha256 lie le plan. content.ts03_expectations répète les attentes de corps à contrôler. http.ts03_matrix fournit un seul GET complet par route, avec date, URL, requête et réponse brutes. Les étiquettes d’hôte doivent finir par .invalid; aucun DNS, socket, compte ou client réel n’est utilisé.

The intent.ts03_response plan declares scope, an explicitly synthetic exercise review, at least one route in each existing, removed, and nonexistent state, allowed statuses and body markers. configuration.ts03_response.plan_sha256 binds the plan. content.ts03_expectations repeats the body expectations to check. http.ts03_matrix supplies one complete GET per route, with time, URL, and raw request/response. Host labels must end in .invalid; no DNS, socket, account or real client is used.

Pass requires the complete declared matrix: an existing route returns 200; removed/nonexistent routes return 404 or 410; required literal UTF-8 markers occur and forbidden markers do not. A complete status or content contradiction is fail even when other cases are incomplete. Missing or duplicate cases, 206/304, unsupported or incomplete evidence are inconclusive unless another attributable contradiction is already established.

Le pass exige toute la matrice déclarée : 200 pour une route existante ; 404 ou 410 pour une route supprimée/inexistante ; marqueurs littéraux UTF-8 requis présents et interdits absents. Une contradiction complète de statut ou de contenu reste fail malgré d’autres cas incomplets. Cas manquants ou dupliqués, 206/304 et preuves incomplètes/non prises en charge restent inconclusifs, sauf contradiction attribuable déjà établie.

## Cas contradictoires / Counterexamples

The fingerprinted fixture has 13 authored synthetic cases: complete matrix; removed route returning 200; nonexistent route returning 503; existing body mismatch; forbidden content marker; missing case; duplicated case; 206 partial response; 304 conditional response; future plan; wrong plan fingerprint; live-domain label; and a contradiction preserved despite a duplicate. Expected outcomes are frozen independently of the reader.

La fixture empreintée contient 13 cas synthétiques rédigés : matrice complète ; route supprimée en 200 ; route inexistante en 503 ; corps existant contradictoire ; marqueur interdit ; cas manquant ; cas dupliqué ; réponse partielle 206 ; réponse conditionnelle 304 ; plan futur ; mauvaise empreinte du plan ; hôte réel ; contradiction conservée malgré un doublon. Les attendus sont figés indépendamment du lecteur.

## Limites / Limits

Google’s official documentation explains how status classes affect its crawlers and notes that a 2xx response containing error-like content may be treated as a soft 404. TSEP does not implement that classification. A 200 for a declared removed/nonexistent fixture is only a contradiction to the supplied plan; it is not a finding that Google classified a real page as a soft 404. A single 5xx mismatch is point-in-time evidence, not proof of a persistent outage. Content markers are literal source-body checks, not semantic review. No inference is made about site completeness, indexing, ranking or adoption.

La documentation officielle de Google décrit les effets des classes de statuts sur ses robots et indique qu’un contenu évoquant une erreur servi en 2xx peut être traité comme soft 404. TSEP ne reproduit pas cette classification. Un 200 pour une fixture déclarée supprimée/inexistante contredit seulement le plan fourni ; il ne prouve pas que Google a classé une page réelle en soft 404. Un seul 5xx contradictoire est ponctuel, pas la preuve d’une panne persistante. Les marqueurs sont comparés littéralement au corps source, sans revue sémantique. Aucune conclusion sur l’exhaustivité, l’indexation, le ranking ou l’adoption.

Claude’s prior method comments were treated as proposals only; the cases and boundaries here were independently encoded and tested. No independent approval or actual third-party review is claimed.

Les remarques méthodologiques antérieures de Claude ont été considérées comme des propositions ; les cas et limites ont été codés et testés séparément. Aucune approbation indépendante ni revue réelle d’un tiers n’est revendiquée.
