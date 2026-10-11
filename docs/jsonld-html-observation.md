# HTML JSON-LD observation 1 / Observation JSON-LD HTML 1

## Français

Cette méthode facultative prépare **TS31–33** en reliant les blocs JSON-LD aux
octets HTML qui les contiennent, puis en traitant leur document combiné. Elle ne
modifie pas draft.27, ses 12 contrôles outillés ou ses 33 règles. Un résultat
`processed` signifie que la transformation a abouti **sous les hypothèses
déclarées** ; il ne valide ni Schema.org, ni les faits visibles, ni l'éligibilité
Google, ni un contrôle TSEP.

### Entrées et attribution

`experiments/source_scripts.py` lit un corps décompressé et son Content-Type
conservé. Il réutilise le profil `html-http-utf8-v1` : un unique
`text/html; charset=utf-8`, UTF-8 strict, un éventuel BOM initial consommé.
Les autres encodages, les octets invalides et les médias ambigus sont refusés.
Le corps doit provenir d'une capture dont la complétude et l'attribution sont
établies séparément ; ce lecteur ne collecte pas le réseau.

Le parseur épinglé parse5 8.0.1 produit deux lectures statiques, JavaScript activé
et désactivé dans le parseur. Aucun script de la page n'est exécuté. L'observation
conserve tous les éléments `script`, leurs attributs parsés, identifiants de
nœuds, espaces de noms, ancêtres, fragments de template, balises de début/fin,
segments textuels et erreurs HTML. Les éléments HTML `base` et `meta` sont
également conservés pour les examens ultérieurs du contexte.

Une localisation comporte les offsets UTF-16 du parseur **et** l'intervalle
d'octets du corps original, BOM compris. Le texte brut de chaque intervalle est
vérifié contre le corps. Le texte parsé reste distinct : CRLF devient LF et un
NUL HTML peut devenir U+FFFD. Le texte `&amp;` à l'intérieur d'un script HTML reste
littéral. Une balise de fin prématurée n'est pas réparée. Les IDs HTML répétés
ne réduisent jamais la population à un seul bloc.

Les templates restent inventoriés mais hors de la sélection ordinaire. Un
script SVG reste un script étranger ; un script HTML dans `foreignObject` garde
son propre espace de noms. Les documents des frames et les racines shadow
attachées ne sont pas lus. Une déclaration de shadow dans un template ne prouve
pas son attachement. Aucune visibilité CSS n'est déduite.

### Sélection et combinaison explicites

`experiments/jsonld_html.py` emploie le profil
`html-jsonld-exact-type-all-supplied-base-v1` : tous les scripts de l'arbre HTML
ordinaire dont l'attribut parsé `type` vaut exactement `application/ld+json`.
Les variantes de casse, espaces et paramètres reconnaissables restent
`selection-unresolved`, sans être déclarées invalides ou absentes. Les autres
types, les templates et les espaces de noms étrangers sont explicitement
exclus. Ce profil fini ne prétend pas décrire tous les consommateurs.

Chaque bloc sélectionné reçoit un diagnostic JSON strict. Les clés répétées,
commentaires JSON, constantes non JSON, entiers hors de la plage exacte
JavaScript, Unicode non représentable et limites structurelles restent visibles.
Un bloc vide est présent mais illisible. Une URL scalaire en racine ne déclenche
aucun chargement. Le profil du processeur accepte des racines objet/tableau ;
les autres valeurs sont explicitement non prises en charge.

Les objets de tous les scripts sont ensuite réunis ; les tableaux racines sont
concaténés sur un niveau. Cette opération a lieu **avant** expansion et
aplatissement JSON-LD. Deux blocs avec le même identifiant explicite `_:x`
décrivent donc le même nœud dans ce document. Deux nœuds sans identifiant restent
distincts. Les contextes locaux restent dans leurs objets ; ils ne deviennent
pas un contexte global pour les blocs suivants. Les deux hypothèses HTML et les
documents distincts gardent chacun leur espace de noms de nœuds anonymes.
La forme tableau s'applique aussi à un script unique. Un objet racine `@graph`
peut alors conserver un conteneur de graphe après aplatissement : il n'est pas
déballé pour obtenir artificiellement une seule liste d'entités. Les descriptions
dans chaque graphe restent attribuées ; une même IRI ne devient pas une nouvelle
ressource simplement parce qu'elle apparaît dans un autre graphe. Les étiquettes
anonymes produites sont comparées lors du rejeu exact, sans devenir des identifiants
métier stables entre documents ou versions.

Un bloc sélectionné illisible/non pris en charge empêche le graphe combiné,
même si les autres blocs sont lisibles. Leurs diagnostics restent disponibles.
Une erreur de traitement ou un contexte non fourni garde les graphes à `null`.
Un tableau JSON-LD vide peut au contraire produire un graphe vide : son statut
reste différent de l'absence de scripts. `absent` ne justifie pas NA : Microdata,
RDFa, rendu et autres populations ne sont pas évalués par ce profil.

### Base et contextes : paramètres, pas observations navigateur

Le champ obligatoire `base_iri` est une **hypothèse de calcul fournie**. Le lecteur
ne déduit pas encore la base effective à partir du premier élément `base`, de
CSP, de la navigation ou du DOM rendu. Les `base` et `meta` conservés permettent
d'identifier ce travail restant. Une URL fournie comme base ne devient pas une
mesure `document.baseURI`. Un éventuel `@base` JSON-LD est ensuite traité par le
processeur épinglé dans son contexte local.

Les contextes sont fournis sous forme `{url, raw_json, sha256}` et ne sont jamais
téléchargés implicitement. Leur empreinte établit l'identité des octets fournis,
pas l'autorité de la source. L'attribut HTML `src` est conservé et ne provoque
aucune requête. Le ciblage par fragment, les profils de sélection alternatifs,
XHTML et l'exécution navigateur ne sont pas implémentés ici.

### Exécution, limites et rejeu

L'entrée du workflow est un objet JSON avec exactement quatre champs :

```json
{
  "body_base64": "BASE64_CANONIQUE_DU_CORPS_HTML",
  "content_types": ["text/html; charset=utf-8"],
  "base_iri": "https://example.test/page",
  "contexts": []
}
```

```sh
python3 experiments/source_scripts.py body.html \
  --content-type 'text/html; charset=utf-8' --node /path/to/node24 \
  --output new-inventory.json
python3 experiments/jsonld_html.py request.json --node /path/to/node24 \
  --output new-observation.json
python3 experiments/jsonld_html.py new-observation.json --replay \
  --node /path/to/node24 --output new-replay.json
python3 scripts/jsonld_html_check.py --node /path/to/node24 \
  --output-dir new-qualification-directory
```

Les sorties existantes ne sont pas remplacées. Le code 0 indique une observation
produite, qui peut contenir une absence, une erreur ou une inconnue ; 64 indique
un échec d'invocation. Le qualificatif retourne 1 pour une différence attendue/
observée et conserve ses sorties et erreurs. Node 24 est explicitement requis
par ces commandes ; la vérification générale garde ses tests Python sans lancer
Node implicitement.

Le rejeu recalcule l'extraction et le traitement avec les sources conservées,
puis compare toute l'observation, versions des runtimes comprises. La validation
de forme et des intervalles ne prouve pas à elle seule que le parseur a réellement
calculé le texte ou inventorié tous les nœuds. Le rejeu est nécessaire pour
vérifier ces calculs ; ni empreintes ni rejeu n'authentifient une collecte distante.

Bornes : corps 8 Mio, 20 000 nœuds, profondeur 128, 1 000 erreurs HTML, 512 scripts,
512 éléments de contexte, 20 000 segments et 8 Mio de texte extrait. Un dépassement
annule la population de la lecture concernée ; un préfixe n'est pas publié comme
une page complète. Sortie inventaire 32 Mio. Le traitement JSON-LD conserve ses
[propres limites](jsonld-processing.md), notamment 128 Kio par document combiné
et 1 Mio par contexte. Requête du workflow 16 Mio, observation 64 Mio. Chaque
enfant Node a un délai de 30 s, 128 Mio de V8 old-space et des permissions fichier
limitées au dossier temporaire. La garde réseau est une garde d'API, pas une
isolation réseau du système ; old-space n'est pas une limite mémoire totale.

### Qualification et suite

Les 34 cas HTML étaient figés avant l'extracteur ; les 24 cas de combinaison
étaient figés avant le workflow. Cinq cas supplémentaires de graphes ont été
figés avant leur exécution, après observation de conteneurs dans les captures
réelles. Les exécutions ont retrouvé les **126 lectures attendues**, rejoué
**63 observations** et refusé les **10 lectures dépassant les bornes**.
Trois autres cas de frontières HTML figés ont donné six lectures concordantes.
Ces cas sont rédigés et ne sont pas des audits Edikka. Les sorties
historiques distribuées conservent leurs sources et runtimes. Les tests Python
vérifient ces pièces sans se faire passer pour de nouvelles exécutions Node.
Voir [provenance](../provenance/jsonld-html-v1.json).

Restent nécessaires pour TS31–33 : extraction des états rendus attribués, base
effective qualifiée, vocabulaire épinglé, critères précis du consommateur,
rapports de validateurs liés aux entrées, faits visibles et revues motivées,
identités/références à l'échelle du corpus, puis règles atomiques bilingues et
migration explicite. Cette observation est un composant de cette méthode.

## English

This optional method prepares TS31–33 by attributing HTML scripts to original
body bytes and processing their combined document. Draft.27, its 12 executable
controls and 33 rules are unchanged. `processed` means that transformation
completed under supplied hypotheses; it establishes no vocabulary validity,
visible-fact truth, Google eligibility or TSEP outcome.

The source reader accepts the existing strict UTF-8 HTTP-body profile, retains
all scripts, base/meta elements, parsed attributes, namespaces, template paths,
ancestry, start/end tags, text segments and parser errors under two distinct
static scripting hypotheses. It executes no page script. Original byte spans
(including the consumed BOM) and parser UTF-16 offsets are distinct. Raw text
and parsed text remain separate through CRLF/NUL normalization. HTML script
entities stay literal; premature closing tags are not repaired. Duplicate IDs
do not collapse the script population. Templates and foreign scripts remain
inventoried; frame documents, attached shadow roots and CSS visibility are not
observed.

The explicit profile selects every ordinary HTML script whose parsed type is
exactly `application/ld+json`. Recognizable case/space/parameter variants stay
unresolved, rather than invalid or absent. Other types, foreign namespaces and
templates are excluded explicitly. Each selected script gets a strict JSON
diagnostic. Empty scripts are invalid JSON; duplicate keys, unsupported root
scalars, non-JSON constants, unsafe integers, invalid Unicode and resource
limits are retained. All valid roots are combined before JSON-LD processing,
concatenating root arrays one level. Explicit blank IDs are shared within this
document, while unnamed nodes remain distinct. Local contexts do not leak into
following roots. Different representations and documents keep separate blank
node namespaces. Any selected invalid/unsupported script prevents a combined
graph. Missing contexts and processing errors retain null graphs. A processed
empty array remains distinct from absent scripts. `absent` does not establish
NA or absence of rendered markup, Microdata or RDFa.

The mandatory `base_iri` is a supplied calculation hypothesis, **not** a measured
document base URI. HTML base selection, CSP and attributed rendered/navigation
context remain to establish; retained base/meta elements expose that work.
JSON-LD local `@base` is processed by the pinned processor. Context URL/text/SHA
triples are supplied offline and never fetched implicitly; their hashes do not
prove authority. HTML `src` is retained but never fetched. Fragment targeting,
alternate extraction profiles, XHTML and browser execution are outside this
method.

The array procedure also applies to a single script. Root `@graph` objects can
therefore retain named graph containers after flattening; these are not unwrapped
into a manufactured entity list. Descriptions stay attributed to their graphs;
the same IRI does not become a different resource in another graph. Generated
blank labels remain part of exact replay, not stable business identifiers across
documents or versions.

Use the commands and four-field request above with an explicit Node 24 path.
Existing output paths are refused. Exit 0 means an observation was produced,
including negative or unknown outcomes; 64 means invocation unavailable. The
qualifier exits 1 on mismatches and retains failed attempts. Replay recalculates
both extraction and processing and compares the entire observation, including
runtime versions. Structural validation alone cannot prove extraction or
completeness; replay is required to check those calculations. Neither hashes
nor replay authenticate a remote capture.

Bounds are 8 MiB body, 20,000 tree nodes, depth 128, 1,000 parse errors, 512
scripts, 512 context elements, 20,000 payload segments and 8 MiB payload text.
A failed reading clears its population, never a falsely complete prefix.
Inventory output is capped at 32 MiB, workflow request at 16 MiB and observation
at 64 MiB. Processor limits include a 128 KiB combined document and 1 MiB context.
Each Node child has a 30-second deadline, 128 MiB V8 old-space and temporary-folder
file permission. The API network guard is not OS network isolation, and V8
old-space is not total memory. General verification does not silently run Node.

34 source cases and 24 processing cases were frozen before their respective
implementations. Five additional graph cases were frozen before their execution,
after graph containers were observed in real captures. Actual Node qualification
matched 126 readings, replayed 63 observations and rejected 10 over-limit readings.
Three additional frozen HTML boundaries yielded six matching readings. All fixtures are authored;
retained outputs keep their original source/runtime fingerprints. Python checks
of them do not constitute new Node executions or Edikka assessments. Rendered
states, effective bases, pinned vocabulary, precise consumer-feature criteria,
bound validator output, visible-fact reviews, corpus identity/reference review
and versioned bilingual atomic integration remain required for TS31–33.

## Technical references / Références techniques

- [W3C JSON-LD 1.1, embedding in HTML](https://www.w3.org/TR/json-ld11/#embedding-json-ld-in-html-documents)
- [W3C JSON-LD 1.1 API, HTML content algorithms](https://www.w3.org/TR/json-ld11-api/#html-content-algorithms)

Retrieved excerpts and dated fingerprints are retained in the local development
record identified by provenance. The narrower exact-type/supplied-base profile
is declared here; the references do not establish full API implementation or a
recognized TSEP standard.
