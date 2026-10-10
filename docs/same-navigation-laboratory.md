Current laboratory: version 2. Le [parcours de correction](canonical-attribute-coverage.md) ajoute neuf phases sur trois URL ; les six recettes initiales restent conservées.

# Navigation attribuée — laboratoire synthétique / Same-navigation laboratory

## Français

Draft.11 conserve `intent.crawler` comme User-Agent HTTP exact, comparé à la
requête conservée. Pour TS07, `intent.directive_crawler: "googlebot"`, facultatif
et déclaré avant capture, choisit la sémantique bornée des directives. Ce sont les
règles appliquées **à la représentation reçue par ce client**, pas une observation
de Googlebot. L'agent de navigation n'est ni remplacé ni rebaptisé Googlebot.

Sans le champ, les résultats historiques restent fixes. Une valeur explicite
inconnue ou nulle reste indéterminée. Pour TS07-A02, la nouvelle voie exige un
`robots_policy` explicite avec `product_token` égal à googlebot, sans distinction
de casse. Le profil choisit ce produit même si l'agent HTTP est Chrome. Un groupe
Chrome ne remplace pas le groupe Googlebot. Le refus HTTP 401/403 attribuable garde
sa priorité. TS04 conserve sa voie existante. Aucune permission robots ne prouve
l'accès réel d'un moteur ; l'examen des autres obstacles reste requis.

### Ce que le laboratoire collecte

`examples/same_navigation_lab.py` écoute uniquement sur 127.0.0.1 et sert six pages synthétiques. Par défaut, chaque
campagne utilise un nom unique sous .localhost, résolu localement par le navigateur,
pour ne pas réutiliser les cookies d’une autre application locale. Aucun cookie
utilisateur n’est supprimé. Une calibration avec cookie, authentification ou
en-tête conditionnel est conservée mais ne peut pas être scellée ; les captures
ne sont jamais nettoyées pour obtenir une requête anonyme.
Une navigation de calibration préalable relève l'agent HTTP réel, sans contrôle
SEO. Avant toute navigation de mesure, `seal` fige six recettes, intentions,
identités de navigation, réponses et empreintes des outils. Les scénarios sont
un témoin, un noindex ajouté par JavaScript, un noindex HTTP, une canonical modifiée,
un lien interne divergent et un arbre dépassant la borne. Ce plan n'est pas une
expérience aveugle ni indépendante de l'auteur.

Chaque visite conserve les octets reçus de la requête et ceux envoyés dans la
réponse HTTP/1.1. Au chargement, le script applique la mutation prévue puis exécute
une seule fois le collecteur d'inventaire version 2, sans enlever les nœuds ajoutés
par le navigateur. L'export conserve arbre, sérialisation, dates, agent, erreurs,
identités et empreinte du script. Un POST local transmet cet export et affiche
son reçu ; l'opérateur conserve ce reçu et ses horaires de navigation/observation.
Les empreintes relient les pièces : elles n'authentifient pas leur auteur.

`finish` exige une unique navigation et un unique export par cas, l'agent calibré,
une chronologie cohérente et les réponses préalablement figées. Toute tentative
supplémentaire reste dans le journal. Les erreurs, captures manquantes, doublons,
pièces modifiées ou hors inventaire ne deviennent pas des réussites. Un écart aux
attendus est conservé dans les résultats : il n'autorise pas à retoucher la capture
ou à sélectionner une deuxième tentative. Toute réparation nécessite une nouvelle
campagne distincte, en conservant l'échec de la précédente.

La livraison contient les entrées natives, évaluations, rapports, pièces source,
reçus et manifeste. `replay` reconstruit les entrées et résultats hors réseau avec
les outils exacts. Il ne relance pas le navigateur. Les tests unitaires utilisent
des clients HTTP et des arbres rédigés : **ces tests ne sont pas des visites d'un
navigateur**. L'exécution dans un véritable navigateur doit être documentée
séparément avec sa date, son plan et ses pièces.

### Utilisation

Depuis une archive extraite avec Python 3.9+, choisir des dossiers nouveaux :

```sh
python3 examples/same_navigation_lab.py serve --output /tmp/tsep-navigation-source
# Ouvrir une seule fois l'URL de calibration affichée, dans le navigateur choisi.
python3 examples/same_navigation_lab.py seal /tmp/tsep-navigation-source --browser-name NOM --browser-version VERSION
# Ouvrir chaque URL du plan une fois. Conserver horaires et reçu visible.
# Arrêter le serveur avec Ctrl-C après les observations pour fermer le journal.
python3 examples/same_navigation_lab.py finish /tmp/tsep-navigation-source --observations /tmp/observations.json --output /tmp/tsep-navigation-delivery
python3 examples/same_navigation_lab.py replay /tmp/tsep-navigation-delivery
```

`observations.json` est un objet indexé par les six identifiants du plan. Chaque
valeur porte `navigation_started_at`, `observed_at` (dates ISO avec fuseau) et
`receipt` (SHA-256 affiché, sans le préfixe `received:`). Une saisie a posteriori
ne doit pas inventer des horaires. L'identité/version du navigateur est déclarée
par l'opérateur ; l'agent est lu dans la requête de calibration.

### Portée et limites

Les scénarios sont synthétiques, même si le navigateur et les requêtes sont réels.
Ce laboratoire local instrumente ses propres réponses ; il n'est pas un collecteur
universel pour un site tiers et ne recolle jamais une réponse curl à un autre DOM.
La capture se produit à un état déclaré de chargement ; elle ne couvre pas tous
les états, interactions, effets tardifs, moteurs ou réseaux. Les horloges doivent
être cohérentes. Le script est exécuté dans la page, dont les API ne sont pas
cryptographiquement authentifiées. Le journal serveur n'est pas une attestation
indépendante ; une écriture terminée ne démontre pas à elle seule une lecture.

L'inventaire garde ses bornes (1024 nœuds, profondeur 64, sérialisation 256 Kio,
transport/nœuds 512 Kio, durée coopérative 2 s). Un arbre incomplet reste
indéterminé. Les limites du lecteur HTML source, les revues d'accès et de contenu,
et les obligations de plan restent applicables. Un pass atomique ne finalise pas
TS07 ou TS10 ; aucun résultat de ce laboratoire ne prouve une conformité Edikka,
un crawl Google, une indexation ou un gain SEO. La Search Console apportera une
observation distincte et datée, sans transformer ces pages locales en URL indexées.

## English

Draft.11 retains `intent.crawler` as the exact HTTP User-Agent. Optional prior
`directive_crawler: "googlebot"` selects the bounded directive semantics for
TS07, applied only to the captured client representation. It never establishes
what Googlebot receives. Missing field preserves historical behavior; unsupported
explicit values remain inconclusive. TS07-A02 requires an explicit matching
robots product profile; it must not select the Chrome group instead. Attributable
HTTP 401/403 denial keeps precedence. TS04's existing path is unchanged.

The stdlib server binds only 127.0.0.1. Its CLI uses a fresh .localhost name per
campaign; the browser must resolve it locally. It never clears user cookies or
strips recorded headers. Calibration carrying session/conditional headers is
retained and refused before sealing. The stdlib loopback laboratory first calibrates the real HTTP agent, then freezes
six recipes, response bytes, tool hashes, intent and navigation IDs before any
control navigation. Each page is visited once. Its load handler performs the
planned mutation, runs inventory 2 once and posts the export to the local server.
Exact received requests, sent responses, serialized DOM, tree, errors, identities,
timestamps and operator-observed receipts are retained. Duplicate/missing exports,
agent mismatch, incoherent clocks, modified evidence or unlisted requests prevent
completion. Expected/actual disagreements remain recorded, without resampling.
A repair requires a distinct campaign retaining the earlier failure.

Use the commands above with new folders. The observation file maps every task ID
to ISO-with-zone `navigation_started_at`, `observed_at` and the displayed receipt
SHA-256 without its prefix. Do not invent past timings. Stop the server after all
observations to close its log. Finish builds native inputs, bundles, reports and
replays; offline replay regenerates inputs/results without executing a browser.
HTTP clients and authored trees in unit tests are not actual browser observations.

The pages are synthetic even with an actual browser. This is a locally instrumented
server, not a general collector for external sites. No curl response is attached
to a separate DOM. One load state does not exhaust later effects or interactions.
Browser identity is operator-declared, API integrity is not authenticated, and
server logs/digests are not independent attestation. Inventory 2 bounds, source
HTML limitations, required human reviews and plans still apply. Partial captures
remain inconclusive. Atomic success does not complete a control or establish
Edikka conformity, engine access, indexing or ranking. Search Console observations
remain separate and dated; localhost pages are not treated as indexed URLs.
