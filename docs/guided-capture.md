# Guided TS01 collection / Collecte guidée TS01

## Français

Le collecteur version 2 réalise des GET anonymes sur **1 à 10 URL explicitement
choisies et autorisées**, puis utilise l’interpréteur version 3, l’adaptateur version 4 et le
rapport HTML version 3. Python 3.9+, bibliothèque standard. Protocole draft.7,
TS01–TS44, contrat du rapport et corpus normatif inchangés. Cette couverture
d’outil n’est ni une certification, ni une observation d’indexation/classement.

### Une référence, des critères préalables, puis une mesure

Les chemins de sortie doivent être nouveaux et leurs parents exister. Remplacer
l’URL d’exemple par une page publique autorisée. `reference` et `evaluate` font
de vraies requêtes ; `seal` et `replay` restent hors ligne.

```sh
python3 collectors/ts01.py reference --target https://example.com/ \
  --output /tmp/tsep-reference --network 'Poste et connexion réellement utilisés' \
  --selection-method 'Une URL choisie explicitement ; échantillon non représentatif' \
  --access public
python3 collectors/ts01.py seal --reference /tmp/tsep-reference/reference \
  --output /tmp/tsep-intent.json --assessor 'Auteur de la recette' \
  --label 'TS01 sur une URL' --policy digest
python3 collectors/ts01.py evaluate --reference /tmp/tsep-reference/reference \
  --intent /tmp/tsep-intent.json --output /tmp/tsep-evaluation --lang fr
python3 tsep.py gate /tmp/tsep-evaluation/bundle/report.json --summary --lang fr
python3 collectors/ts01.py replay /tmp/tsep-evaluation \
  --output /tmp/tsep-rejeu --lang fr
```

**Examiner la référence avant `seal`** : un 200 n’établit pas que la ressource
est celle souhaitée. La commande vérifie les empreintes et recalcule la référence
à partir des octets, puis enregistre l’intention choisie avant l’évaluation.
Les horodatages viennent de l’horloge locale ; ni signature, ni horodatage de
confiance, ni garantie d’auteur. Les fichiers existants ne sont pas remplacés,
mais un opérateur peut les modifier : conserver/protéger les empreintes reçues.

| Politique | Corps identique | Corps différent |
| --- | --- | --- |
| `digest` | Identité établie si URL finale identique | Indéterminé |
| `stable` | Identité établie si URL finale identique | Échec : stabilité explicitement attendue |
| `markers` | Identité établie si URL finale identique | Test des marqueurs préalables, sinon indéterminé si interprétation impossible |

Ces politiques appliquent TS01-A02 existante ; une URL finale différente échoue.
Pour `markers`, fournir `--policy markers --criteria /tmp/criteres.json` lors de
`seal`. Chaque cible exige au moins un marqueur requis. Exemple à adapter **avant**
la mesure, après examen de la référence :

```json
{
  "https://example.com/": {
    "expected_final_url": "https://example.com/",
    "required_markers": ["Titre attendu"],
    "forbidden_markers": ["Service indisponible"]
  }
}
```

Les marqueurs sont des littéraux sensibles à la casse dans le texte source UTF-8
extrait, selon le [contrat d’entrée](conformance.md). Pas de rendu navigateur,
regex ou normalisation d’espaces. Les commentaires et script/style sont exclus ;
le parseur HTML conserve son sous-ensemble borné. Ne pas choisir les critères
après avoir vu la mesure pour obtenir un résultat favorable. Une référence
incomplète/non-200 ne peut pas être scellée ; toute tentative reste conservée.

### Origine des critères et cohérence des outils

Sans `expected_final_url` dans le fichier de critères, l’URL finale et l’empreinte
sont **dérivées de la référence et adoptées lors de `seal`**. Ce choix ne prouve pas
une intention indépendante ni une validation humaine. Le champ facultatif
`expected_final_url` déclare explicitement l’URL attendue : une différence avec
la référence bloque le scellement. L’empreinte reste issue de la capture.
Le rapport affiche cette origine, la politique, la date et les littéraux près des
résultats TS01. Une empreinte identique ne teste pas les marqueurs. `stable` est
un choix explicite ; un nonce ou une date changeante suffit alors à échouer.

Avant scellement et avant toute requête de mesure, le collecteur vérifie sa
version et les empreintes des sources contre la référence. Il vérifie aussi les
origines `__file__`/`__spec__.origin` des modules locaux inventoriés et leurs
empreintes avant/après l’opération. L’adaptateur fait le même contrôle autour de
l’interprétation. Une collecte dont les fichiers changent conserve les tentatives
brutes sans émettre d’évaluation. Ces contrôles détectent notamment un mélange
accidentel de copies ; ils n’authentifient pas l’exécution Python et ne constituent
pas une attestation du code en mémoire ou de l’auteur. Le paquet présente les
exécutions fournies, pas une preuve de campagne exhaustive.

**Migration collecteur 1 → 2 / adaptateur 3 → 4 / HTML 2 → 3** : le protocole,
l’interpréteur 3 et l’entrée binaire 2 ne changent pas. L’intention guidée passe à
`intent_version: "2"`, avec origine des critères et empreintes de la référence.
Ne pas réétiqueter les anciens fichiers : conserver leur archive d’outil et leurs
rapports pour les rejouer. Préparer une nouvelle référence puis une nouvelle
intention avec le collecteur 2 avant une nouvelle mesure. Une référence collectée
par un autre code est refusée, même si son numéro de version paraît identique.
Le format du paquet adaptateur reste 1 ; sa nouvelle identité de code apparaît
dans `import.json`. Les anciens HTML restent consultables.

### Octets et limites de collecte

Le worker conserve les octets HTTP/1.1 après déchiffrement TLS, pas les paquets
réseau/TLS. En HTTPS, chaîne de confiance et nom d’hôte sont vérifiés. Chaque saut
retient la requête prévue, la réponse reçue (ou son préfixe), dates, complétude,
erreur, adresse du pair et données TLS disponibles. Une requête prévue n’est pas
une preuve de transmission si la connexion échoue. DNS est contrôlé avant connexion
à une adresse numérique vérifiée ; les adresses non publiques sont refusées.
`--allow-loopback` autorise uniquement la boucle locale pour une recette synthétique.

Valeurs par défaut : agent `TSEP-TS01-collector/2`, `Accept-Encoding: gzip, deflate`,
10 secondes par saut, 512 Kio de réponse par saut, 3 redirections. Bornes configurables :
0,1–30 secondes, 1 Kio–1 Mio, 0–5 redirections. Le superviseur ajoute au plus une
seconde au délai pour borner aussi DNS/processus. Maximum de **2 Mio de réponses
par phase**, 2 phases conservées. La requête demande `Connection: close` ; un
serveur qui ne ferme pas la connexion avant le délai laisse la collecte incomplète,
même si un encadrement aurait permis de déterminer sa fin plus tôt.

Les origines des cibles sont autorisées ; une autre origine exige `--allow-origin
https://autre.example`. Aucun saut vers HTTP depuis HTTPS. Aucune exploration de
liens, authentification, cookie, proxy applicatif, HTTP/2 ou exécution JavaScript.
Le protocole et l’agent choisis ne simulent pas Googlebot. Chaque erreur, plafond,
redirection non suivie et limite d’interprétation est conservé ; rien n’est
transformé en réussite. Une capture terminée peut rester ininterprétable.

### Entrée binaire version 2 et migration

L’objet conserve les champs `rules` et `targets` ; `input_version` devient `"2"`.
Dans les tableaux `http` (y compris référence, robots et documents), chaque
`request`/`response` peut être la chaîne UTF-8 historique ou cet objet exact :

```json
{"base64": "AA==", "sha256": "6e340b9cffb37a989ca544e6bb780a2c78901d3fb33738768511a30617afa01d"}
```

Cet exemple encode un seul octet NUL, **pas un message HTTP valide**. Base64 doit
être canonique et SHA-256 correspondre aux octets décodés. Une erreur d’intégrité
bloque l’entrée (64), sans fabriquer de rapport NT. Maximum : 8 Mio par message
brut, 64 Kio d’en-têtes, 8 Mio après décompression ; l’adaptateur conserve sa borne
plus stricte de **8 Mio pour le fichier JSON complet**.

Ordre d’interprétation : encadrement HTTP, décodage du transfert chunked, décodage
du contenu gzip (un membre) ou deflate enveloppé zlib, puis SHA-256 des octets du
contenu. Content-Length mesure les octets avant décompression. Aucun réencodage
du contenu pour calculer son empreinte. Pas de remplacement silencieux de texte
invalide ; le corps non UTF-8 peut être comparé par empreinte, pas par marqueurs.

La version d’entrée 1 reste acceptée. Ne pas réécrire les captures historiques :
garder leur rapport/version d’outil, produire un nouveau paquet sous une nouvelle
identité. Un outil 2 ne lit pas les objets binaires v2. Convertir une chaîne v1
en UTF-8/base64 n’invente pas les octets perdus lors de la collecte. Ne pas convertir
silencieusement une capture liée à une revue humaine TS07/TS10 : son empreinte de
liaison changerait ; toute nouvelle liaison exige une revue appropriée.

### Sorties, rejeu et CI

L’évaluation contient `input.json` (référence et mesure brutes), `intent.json`,
`evaluation/` (fichiers `.bin`, métadonnées et manifeste), `bundle/` (rapport,
preuves, résultats, décision, EARL) et le HTML. Les manifestes SHA256SUMS utilisent
des inventaires explicites. Le rejeu vérifie l’intégrité, recalcule les mêmes
observations/décision et vérifie les empreintes des sources interpréteur/adaptateur,
sans réseau. Utiliser la même archive d’outil, identifiée par son SHA-256, après
déplacement ; ni dépôt Git, ni infrastructure privée n’est nécessaire.

Le code 0 de `evaluate` signifie que le paquet a été produit, même pour NO_GO.
`tsep.py gate` fournit le code de décision ; 64 indique une entrée invalide,
2 une erreur de syntaxe CLI. Le [workflow consommateur](../examples/ts01-consumer.yml)
est un **exemple préparé, non activé et non observé en CI distante**. Il exige une
copie figée des outils dans `vendor/tsep/`, une référence et une intention antérieures
commises à côté. Vérifier l’archive et son SHA-256 avant installation ; conserver
le ZIP choisi et son empreinte. Adapter la déclaration réseau à l’environnement
réel du runner lors de la préparation des références ; elle est figée avec les critères.
Ne pas refaire la référence dans le job de mesure. Inspecter les pièces et leur
accès avant de conserver des artefacts CI. Le workflow garde les preuves en cas
d’échec et appelle explicitement la décision TSEP.

### Couverture actuelle

| État | Périmètre |
| --- | --- |
| Pris en charge | Octets binaires v2, v1 historique, transfert chunked borné, gzip/deflate, collecte prospective TS01, rapport/rejeu hors ligne |
| Différé / indéterminé | Brotli, gzip multiple, deflate brut, extensions/trailers chunked, réponses intermédiaires multiples, HTTP/2 brut, texte non UTF-8 pour marqueurs, HTML hors sous-ensemble |
| Hors couverture | TS02–TS44 dans ce parcours, rendu navigateur, revues humaines manquantes, authenticité de collecte, stabilité dans le temps, indexation/classement/adoption |

La décision reste adjacente au nombre de cibles et aux contrôles sélectionnés dans
le HTML ; l’inventaire de couverture est déclaré par l’outil, sans validation externe.

## English

Collector version 2 performs anonymous GET requests for **1–10 explicitly selected,
authorized URLs**, using interpreter 3, adapter 4 and HTML engine 3.
Python 3.9+ standard library only. Protocol draft.7, TS01–TS44, the report contract
and normative corpus are unchanged. This is tool coverage, not certification or
evidence of indexing/ranking.

Use the commands above with real network/selection/assessor descriptions and
`--lang en`. Outputs must be new and parent directories must exist. `reference`
and `evaluate` make real network requests; `seal` and `replay` are offline.
**Examine the reference before sealing**: HTTP 200 alone does not establish the
intended resource. The tool checks integrity, recomputes the baseline from raw
bytes and freezes operator-selected criteria before evaluation. Local timestamps
are neither trusted timestamps nor signatures. Existing files are not overwritten,
but operators can edit them: preserve and protect the received fingerprints.

Identity follows existing TS01-A02. A different final URL fails; identical final
URL and body digest pass. With a changed digest, `digest` is inconclusive and
`stable` fails. `markers` evaluates previously selected literals; unavailable
interpretation remains inconclusive. Use `--policy markers --criteria file.json`
at `seal`, with the per-URL object shown above and at least one required marker
per target. Markers are case-sensitive UTF-8 source-text literals, without regex,
space normalization or browser rendering. Comments and script/style are excluded;
the HTML parser remains a bounded subset. Do not choose criteria after seeing
the evaluation. Incomplete/non-200 references cannot be sealed; attempts remain.

Without `expected_final_url` in the criteria file, final URL and digest are
**derived from the reference and adopted at `seal`**. This proves neither
independent intent nor human validation. The optional field declares an expected
final URL; any difference from the reference blocks sealing. The digest still
comes from capture. The report places origin, policy, date and literal markers
beside TS01 results. Matching digests do not test markers. `stable` is explicit:
even a changing nonce or timestamp fails under that policy.

Before sealing and before evaluation requests, the collector checks its version
and source fingerprints against the reference. It also checks the inventoried
local modules’ `__file__`/`__spec__.origin` and hashes before/after the operation.
The adapter checks around interpretation. A collection whose sources change keeps
raw attempts without issuing an assessment. These checks detect accidental mixed
checkouts; they do not authenticate Python execution, attest in-memory code or
identify the author. Bundles present supplied runs, not an exhaustive campaign.

**Migration collector 1 → 2 / adapter 3 → 4 / HTML 2 → 3**: protocol, interpreter 3
and binary input 2 are unchanged. Guided intent becomes `intent_version: "2"`,
recording criteria origin and reference sources. Do not relabel old files: retain
their tool archive and reports for replay. Collect a new reference and seal a new
intent with collector 2 before evaluation. Different source fingerprints reject
a reference even when the version number looks identical. Adapter bundle format
remains 1; `import.json` records its new code identity. Old HTML remains readable.

The worker retains HTTP/1.1 bytes after TLS, not network/TLS packets. HTTPS verifies
certificate trust and hostname. Each hop retains its planned request, received
response/prefix, dates, completion, errors and available peer/TLS data. A planned
request does not prove transmission when connection fails. All DNS answers must
be public, then a checked numeric address is used; `--allow-loopback` permits
loopback only for synthetic local tests. Default agent `TSEP-TS01-collector/2`,
Accept-Encoding `gzip, deflate`, 10 seconds/hop, 512 KiB/response, 3 redirects.
Configurable bounds: 0.1–30 seconds, 1 KiB–1 MiB, 0–5 redirects. The supervisor
allows at most one extra second to bound DNS/process time. **2 MiB response total
per phase**, both phases retained. `Connection: close` is requested: failure to
close before the deadline leaves collection incomplete even if framing could
have established completion earlier.

Target origins are allowed; add another explicitly with `--allow-origin`.
HTTPS-to-HTTP downgrade is refused. No crawling, authentication, cookies,
application proxy, HTTP/2, JavaScript or Googlebot simulation. Every error, bound,
unfollowed redirect and interpretation limit is retained, never converted to pass.
A completed capture can remain uninterpretable.

Input version `"2"` retains `rules` and `targets`. HTTP request/response values,
including reference/robots/documents, accept legacy UTF-8 strings or an exact
`base64`/`sha256` object as shown above (that example is one NUL, not valid HTTP).
Base64 must be canonical and SHA-256 match decoded bytes. Integrity errors reject
the input with 64, rather than fabricating an NT report. Bounds: 8 MiB/raw message,
64 KiB/headers, 8 MiB/decoded content; the adapter also limits **the entire JSON
file to 8 MiB**. Framing and chunked transfer are decoded before gzip (one member)
or zlib-wrapped deflate. Content-Length counts compressed bytes. Content SHA-256
uses exact decoded bytes, never reencoded text. Non-UTF-8 bodies support digest
comparison, not markers; no replacement decoding.

Input v1 remains accepted. Preserve historical captures, reports and tool identity;
create new bundles under new identities. Tool 2 cannot consume binary v2 records.
UTF-8/base64 conversion cannot recover bytes already lost in collection. Do not
silently convert captures bound to TS07/TS10 human reviews: changed binding hashes
require appropriate review.

Evaluation outputs `input.json` (both raw phases), `intent.json`, `evaluation/`
(raw `.bin`, metadata, manifest), `bundle/` (report, evidence, assessment, gate,
EARL) and HTML. Manifests enumerate files explicitly. Offline replay verifies
integrity, repeats atomic observations and gate, and checks interpreter/adapter
source fingerprints. Use the same SHA-256-identified tool archive after moving
the bundle; no Git or private infrastructure is required. Successful collection
exits 0 even for NO_GO: use `tsep.py gate` for the decision. Invalid data exits 64,
CLI syntax errors 2.

The [consumer workflow](../examples/ts01-consumer.yml) is **prepared, not activated
or observed on remote CI**. Supply frozen tools under `vendor/tsep/` (verify the
chosen archive and SHA-256 before installation; retain both), plus a committed
prior reference and intent. Describe the actual runner network when preparing
that reference; the declaration is frozen with criteria. Never refresh the
baseline inside the evaluation job. Inspect evidence and access restrictions
before uploading CI artifacts. The example keeps failed evidence and explicitly
invokes the TSEP decision.

Implemented: binary v2/legacy v1, bounded chunked/gzip/deflate decoding, prospective
TS01 collection, offline reporting/replay. Deferred/inconclusive: Brotli, multiple
gzip members, raw deflate, chunk extensions/trailers, multiple interim responses,
raw HTTP/2, non-UTF-8 markers and HTML outside the subset. Outside this workflow:
TS02–TS44, browser rendering, missing human reviews, collection authenticity,
long-term stability, indexing/ranking/adoption. HTML places scope next to the
decision and displays tool-declared coverage without external validation.
