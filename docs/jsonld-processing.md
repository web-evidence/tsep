# JSON-LD processing observations 1 / Observations de traitement JSON-LD 1

## Français

Cette étape prépare TS31–33. **Elle ne les implémente pas encore** et ne change
ni draft.27, ni les 12 contrôles / 33 règles exécutables. Elle traite des documents
JSON-LD fournis, avec leurs contextes locaux, pour conserver des graphes développés
et aplatis et les avertissements du processeur. Un JSON analysable ou un traitement
réussi ne prouve ni l'adéquation au contenu visible, ni l'identité des entités,
ni la validité Schema.org, ni l'éligibilité à une fonctionnalité Google.

Le processeur est **jsonld.js 9.0.0**, archive npm officielle non modifiée,
avec empreintes de chaque fichier et licence conservées. Le superviseur Python
3.9+ utilise un **Node 24 explicitement désigné**, dans un processus séparé.
Il n'installe aucun paquet. Il ne se replie pas sur un autre parseur si Node est
absent. Le vérificateur général reste indépendant de cette qualification Node.

### Entrées et portée

L'entrée possède seulement `documents`, liste de 1 à 64 documents. Chaque document
possède exactement `id`, `base_iri`, `raw_json` et `contexts` :

```json
{
  "documents": [{
    "id": "organization-source",
    "base_iri": "https://example.test/about",
    "raw_json": "{\"@context\":{\"name\":\"https://schema.org/name\"},\"@id\":\"#org\",\"name\":\"Example\"}",
    "contexts": []
  }]
}
```

`raw_json` conserve le texte d'entrée ; les noms JSON dupliqués sont refusés,
y compris dans un objet imbriqué. Il n'y a ni réparation de JSON, ni décodage
d'entités HTML : `&amp;` reste littéral. Cette étape **n'extrait pas les scripts
HTML** ; l'attribution future aux octets source, à la page et aux états rendus
reste nécessaire. La base est une IRI HTTP(S) déclarée, pas une URL visitée ni
une base HTML implicitement devinée.

Chaque contexte local possède exactement `url`, `raw_json` et `sha256` (SHA-256
des octets UTF-8 de son texte). Son objet JSON doit contenir `@context`. L'URL
est une clé de recherche exacte. Toute dépendance imbriquée doit également être
fournie. L'empreinte établit une liaison aux octets, pas leur authenticité.
Ni ces contextes, ni les identifiants des entités ne déclenchent un téléchargement.
Une racine JSON constituée d'une chaîne URL est refusée. Chaque document dispose
d'une instance et d'un cache de contextes distincts.

L'expansion et l'aplatissement utilisent JSON-LD 1.1 et la base fournie. Un `@id`
répété peut réunir des descriptions complémentaires ; plusieurs valeurs restent
présentes. Les graphes nommés et les listes sont conservés selon le processeur.
Les identifiants de nœuds anonymes sont **locaux au document** ; deux sorties
portant `_:b0` ne sont pas fusionnées. Aucune équivalence d'entités réelle n'est
déduite. Les autres syntaxes, comme Microdata et RDFa, ne sont pas analysées.

### Résultats, inconnues et bornes

| État | Signification limitée |
| --- | --- |
| `observed` | Expansion et aplatissement obtenus, avec avertissements éventuels ; aucun verdict de conformité |
| `unavailable` | Au moins un contexte demandé n'était pas fourni ; aucun graphe conclusif |
| `processor-error` | Le processeur a rejeté le document ou dépassé une borne interne ; aucun graphe conclusif |
| `json-error` | Syntaxe JSON, nom dupliqué ou constante non JSON refusée avant traitement |
| `unsupported-input` | Entrée hors profil, par exemple racine scalaire, entier non exactement représentable ou Unicode invalide |

Les avertissements conservent leur phase (`expand` / `flatten`), code, niveau et
message. Les informations omises à l'expansion peuvent produire un graphe vide :
ce n'est ni une preuve d'absence de balisage ni NA. Un même avertissement peut
apparaître aux deux phases. Une erreur d'enveloppe, de contexte fourni, de runtime
ou une expiration empêche l'observation du lot ; elle n'est jamais un succès vide.
Les commandes de qualification conservent les fichiers produits avant l'échec.

Bornes : 4 Mio pour la requête, 128 Kio UTF-8 par document, 1 Mio par contexte, 32 contextes
fournis par document, profondeur JSON 64 et 50 000 valeurs par document/contexte,
64 demandes de contexte et 128 avertissements par document, 16 Mio de sortie,
30 secondes pour le processus, 128 Mio pour son ancien espace mémoire V8.
Cette dernière limite n'est pas un plafond global de mémoire du processus.
Les entiers au-delà de ±(2^53−1), les constantes NaN/Infinity et les représentations
non finies sont refusés ; les autres nombres suivent la représentation JavaScript
du processeur. Ce n'est pas un calcul décimal exact ; le texte numérique original
reste conservé. Les nombres décimaux ne sont pas une preuve monétaire exacte.

Le processus reçoit les permissions de lecture de son seul dossier temporaire,
sans addon, génération dynamique de code ni variables `NODE_*` héritées. Un garde
interdit les points d'entrée réseau documentés utilisés par l'expérience. C'est
un garde d'API, **pas une affirmation d'isolation réseau au niveau du système**.
Les scripts des sources ne sont jamais exécutés.

### Exécuter et rejouer

```sh
python3 experiments/jsonld_processing.py input.json --node /absolute/path/to/node24 --output observation.json
python3 experiments/jsonld_processing.py observation.json --replay --node /absolute/path/to/node24 --output replay.json
python3 scripts/jsonld_processing_check.py --node /absolute/path/to/node24 --output-dir /tmp/tsep-jsonld-qualification
```

Les sorties doivent être nouvelles. Le code 0 du lecteur signifie qu'une
observation a été produite, même si certains documents sont indisponibles ; lire
leurs états. Un échec d'appel renvoie 64. La qualification renvoie 1 pour des
attentes non concordantes, 64 si elle ne peut aboutir, 0 pour un accord complet
avec ses seuls cas figés.

Le contrôle structurel vérifie l'attribution, la population, les états et les
traces ; il ne prouve pas le calcul d'un graphe. Le rejeu **relance le processeur**
hors ligne avec les mêmes pièces et compare toute la sortie, versions runtime
comprises. Une différence est conservée comme échec, jamais normalisée en silence.
Ce rejeu n'authentifie pas l'auteur des entrées ni leur origine publique.

### Preuves obtenues et suite

Le 11 octobre 2026, 40 cas rédigés et figés avant le superviseur ont tous correspondu
aux attentes. Huit cas de limites supplémentaires ont été figés ensuite, avant
leur exécution. Ils ont révélé un nom de propriété Unicode invalide qui interrompait
le lot ; la correction refuse ce document avant le processeur. Le premier échec
et les empreintes sont conservés dans la [provenance](../provenance/jsonld-processing-v1.json).
Les 48 attentes concordent après correction et les deux lots se rejouent exactement
avec Node 24.19.0. Un essai supplémentaire a utilisé le contexte officiel Schema.org
capturé le même jour (210 636 octets, 3 103 termes) avec un document fictif : il a
révélé que la borne initiale de 128 Kio par contexte était insuffisante. La borne
est passée à 1 Mio, avec refus au-delà, puis expansion attendue et rejeu exact
ont réussi. Ce test ne valide ni le vocabulaire ni une page réelle. Le fichier
officiel et l'échec initial restent conservés localement avec leurs empreintes ;
le contexte distant ne devient pas une dépendance téléchargée implicitement.
Les 27 tests Python ciblés portent sur les entrées, attributions,
refus et rejeu ; leurs observations conservées ne constituent pas une nouvelle
exécution Node. Ce corpus fini n'est ni la suite W3C complète ni une revue indépendante.

Il reste à relier ce traitement aux captures HTML/rendues, figer le vocabulaire et
les critères du consommateur, comparer les faits visibles avec des revues fournies,
examiner les identités et références sur un corpus déclaré, qualifier les rapports
de validateurs, puis intégrer les règles TS31–33 bilingues dans une nouvelle
version. Une erreur technique observée ne dispense pas de ces obligations.

## English

This optional observation prepares TS31–33; it does **not** implement those controls
or change draft.27 and its 12 executable controls / 33 atomic rules. Supplied JSON-LD
documents are expanded and flattened with the pinned unmodified jsonld.js 9.0.0
npm bundle under its retained license. Python 3.9+ supervises an explicitly selected
Node 24 subprocess. No package installation or fallback parser is used. The general
Python verifier does not implicitly run this optional Node qualification.

The input contains only `documents` (1–64). Each document has exactly `id`,
`base_iri`, `raw_json`, `contexts`. Each context has exactly `url`, `raw_json`,
`sha256`, with SHA-256 over its UTF-8 text and a JSON object containing `@context`.
Base/context identifiers must be declared absolute HTTP(S) IRIs. Context lookup
uses exact supplied keys, including nested dependencies, with a separate processor
instance/cache per document. No implicit fetch, root URL loading or entity-URL visit
occurs. Context fingerprints bind bytes; they do not authenticate their authority.

Duplicate JSON names, invalid JSON and non-JSON constants are refused. Input text
is retained without HTML entity decoding: literal `&amp;` stays literal. No HTML
extraction, effective browser base or rendered-state attribution is claimed.
JSON-LD 1.1 expansion and flattening retain named graphs, lists, complementary
descriptions with repeated IDs and multiple values. Blank-node identifiers are
document-scoped and separate documents are not silently merged. No real-world
entity equivalence follows. Microdata and RDFa are outside this reader's scope.

Statuses are `observed` (processed, possibly with warnings, never a conformity
verdict), `unavailable` (a requested context was not supplied), `processor-error`
(processor rejection/internal bound), `json-error` (syntax/duplicate names/non-JSON
constant), `unsupported-input` (outside the declared root/numeric/Unicode/depth
profile). Only `observed` carries graphs. Warnings retain phase, code, level and
message; the same warning may occur in both phases. An empty graph can result from
omitted information and proves neither absent markup nor non-applicability.
Invalid envelopes/supplied contexts, unavailable runtimes or timeouts fail the
attempt, never silently succeed with an empty batch. Qualification retains files
produced before failure.

Bounds: request 4 MiB, UTF-8 document 128 KiB, context 1 MiB, 32 supplied contexts per
document, JSON depth 64 and 50,000 values per document/context, 64 context requests
and 128 warnings per document, 16 MiB output, 30-second subprocess timeout, 128 MiB
V8 old space (not a whole-process memory cap). Integers outside ±(2^53−1),
NaN/Infinity and nonfinite representations are refused. Remaining numbers use
the processor's JavaScript representation, not exact decimal arithmetic; original
numeric text stays retained. Decimal values do not establish exact monetary facts.

Node receives temporary-directory read permission, no addons/dynamic code and no
inherited `NODE_*` variables. Documented network APIs are guarded; this is not OS
network isolation. Source scripts are never executed. Commands are shown above.
Outputs must be new. Reader exit 0 means an observation exists, not every document
succeeded. Invocation failure is 64. Qualification exits 0 for all finite frozen
expectations matching, 1 for differences and 64 when unavailable.

Shape/attribution checking alone cannot verify graph computation. Explicit replay
reruns the processor offline with identical retained sources and compares the
entire result, including runtimes. Differences fail without silent normalization.
Replay is not source or author authentication. On 2026-10-11, 40 prefrozen cases
matched; eight subsequently prefrozen boundaries exposed one invalid-Unicode-key
batch failure. After its per-document rejection fix, all 48 matched and both batches
replayed exactly on Node 24.19.0. An additional authored-document test used the
official Schema.org context captured that day (210,636 bytes, 3,103 terms), exposing
the initial 128 KiB context limit as insufficient. With a 1 MiB context bound,
the expected expansion and exact replay passed. The original refusal and official
bytes remain retained locally with fingerprints; no implicit remote dependency,
vocabulary validation or real page assessment follows. Twenty-seven Python tests cover input, attribution,
refusal and replay boundaries using retained observations, not implicit new Node
runs. The first failure remains recorded. This finite corpus is not the full W3C
suite or independent review.

Remaining obligations: attributed HTML/rendered extraction, pinned vocabulary and
consumer criteria, visible-fact comparison with supplied reviews, corpus entity
identity/reference assessment, qualified validator reports, contradictory controls
and bilingual versioned TS31–33 rules. No Schema.org/search-feature validity,
visibility, factual truth, Google eligibility, indexing, ranking or Edikka assessment
is established by this preparatory reader.

## Sources

- [JSON-LD 1.1](https://www.w3.org/TR/json-ld11/): syntax, context/base and document-scoped identifiers.
- [Schema.org data model](https://schema.org/docs/datamodel.html): multiple values and vocabulary interpretation.
- [Google structured-data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies): quality/visibility and technical validation remain distinct.
- [Pinned processor and license](../third_party/jsonld/README.md): official retained archive, exact member and capture provenance.

Primary-source excerpts were captured on 2026-10-11 with dated hashes. Scope and
retention details are in the provenance. These sources do not endorse TSEP.
