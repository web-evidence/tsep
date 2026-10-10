# Source-tree inventory 1 / Inventaire d’arbre source 1

**Unapplied experiment. No normative effect. / Expérience non appliquée, sans
effet normatif.** Protocol `0.1.0-draft.14`, interpreter 14 and adapter 15 remain
unchanged. This tool is never imported by the decision pipeline.

## Français

Cette expérience calcule deux arbres statiques d’un document HTML entier avec
parse5 8.0.1 : hypothèse scripting activé, puis désactivé. Elle n’exécute aucun
script et ne mesure ni navigateur, ni DOM rendu, ni Google. Elle prépare une
évolution des lecteurs TS07/TS10 ; la proposition d’extraction TS01 reste distincte.

Quatre inventaires conservent les meta `robots`/`googlebot`, liens canonical,
ancres HTML `a[href]` et éléments `base`. Les attributs interprétés, ancêtres,
position calculée head/body/autre, balise brute et positions UTF-16 sont conservés.
Les signaux des templates sont séparés. Les URL restent littérales : aucune
résolution relative, application de base ou politique SEO n’est effectuée.
Une comparaison indépendante par inventaire vaut `identical`, `different` ou
`unavailable`. Deux inventaires vides identiques ne prouvent aucune réussite.

**Position et politique sont différentes.** Google documente la prise en compte
des meta robots dans le body, tandis que son lien canonical HTML doit être dans
head : [robots](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag),
[canonical](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls).
La règle générale « hors head = ignoré » serait donc erronée. Le lecteur expose
la position ; il ne prédit pas ce qu’un moteur a fait sur une page.

### Exécution et limites

Python 3.9+ supervise un **runtime Node 24 explicitement facultatif**. Le cœur TSEP
et sa vérification habituelle conservent leurs dépendances actuelles. Les archives
officielles parse5 et entities 8.0.0, leurs empreintes et licences MIT sont livrées
sous `third_party/source-tree` et `licenses`. Pas d’installation npm, de script
d’installation, de téléchargement à l’exécution ou de chemin privé requis.

```sh
python3 experiments/source_tree.py source.html --encoding utf-8 --node node --output inventory.json
python3 scripts/source_tree_check.py --node node --output qualification.json
```

Les sorties doivent être nouvelles. L’appelant déclare le décodage UTF-8 ; le
lecteur refuse les octets invalides, conserve U+FEFF initial et les fins de ligne
de l’entrée, sans deviner en-têtes HTTP ou charset HTML. Le parseur applique
ensuite ses règles de prétraitement. Les positions sont des **unités UTF-16**
dans la chaîne exacte, pas des octets ni des indices Python. Une position absente
reste absente ; le superviseur revérifie chaque balise brute sur les octets décodés.

Bornes : 8 MiB d’entrée, 30 secondes pour le processus Node, 128 MiB d’ancien
espace V8 (pas une limite de mémoire totale), 200 000 nœuds, profondeur 256,
50 000 signaux et 1 000 erreurs par hypothèse, 32 MiB de JSON compact. Nœuds et
profondeur sont contrôlés après construction de l’arbre ; temps et V8 bornent
l’exécution du parseur. Un dépassement de lecture supprime ses signaux partiels ;
un échec de processus, une dépendance modifiée ou Node absent produit une erreur
d’expérience, jamais un repli sur l’ancien lecteur ou un résultat TSEP.

Le processus n’exécute pas les scripts de la page. Les API réseau documentées
énumérées dans sa sortie sont bloquées ; ce garde ne prétend pas être une isolation
réseau du système d’exploitation. La permission Node limite la lecture au dossier
temporaire et ne donne pas accès aux écritures de fichiers, processus enfants ou
extensions natives. `NODE_OPTIONS` et `NODE_PATH` ne sont pas hérités.

Les erreurs rapportées par parse5 restent visibles, y compris les attributs
dupliqués. `complete` signifie que l’inventaire borné est terminé ; cela ne signifie
pas HTML valide. L’absence d’erreurs rapportées ne certifie pas la validité HTML.
La qualification optionnelle Node est **séparée** de `scripts/verify.py` : le
vérificateur Python teste l’intégrité des paquets et les refus du superviseur,
sans prétendre avoir lancé Node. Une exécution Node doit être consignée séparément.

### Attendus et correction conservée

36 documents synthétiques (72 lectures) ont été figés avant comparaison avec
parse5 et html5lib 1.1. parse5 correspondait à **71/72 attendus initiaux** ;
html5lib à 65/72. Un attendu de `noscript-closing-trap`, scripting activé, était
erroné. Le fichier v1 reste intact ; v2 consigne sa correction après comparaison.
La comparaison rétrospective donne 72/72 pour parse5 et 66/72 pour html5lib.
Ces nombres ne sont ni une revue indépendante, ni une qualification de tout HTML.

Justification de la correction : dans l’hypothèse activée, noscript en head
entre en texte brut. Son premier délimiteur de fermeture approprié termine ce
texte même s’il ressemble à une valeur d’attribut. Le mode text revient au mode
in head : le meta qui suit y est inséré. Le texte non blanc résiduel ferme
ensuite head ; le canonical suivant est dans body. Voir les sections WHATWG
[in head](https://html.spec.whatwg.org/multipage/parsing.html#parsing-main-inhead),
[RAWTEXT end tag](https://html.spec.whatwg.org/multipage/parsing.html#rawtext-end-tag-name-state)
et [text](https://html.spec.whatwg.org/multipage/parsing.html#parsing-main-incdata).

12 documents supplémentaires ont été figés avant l’implémentation portable.
Ils séparent les quatre comparaisons, les templates, robots dans body, une ancre
audio dans noscript, les positions Unicode/CRLF et l’absence de résolution d’URL.
Les refus de profondeur et d’erreurs sont des tests de bornes supplémentaires.

Migration : aucune ancienne capture, règle, empreinte normative ou version de
rapport ne change. Pour promouvoir une règle de concordance vers TS07/TS10,
il faudra définir séparément admissibilité, erreurs, politique, preuve de
complétude et encodage, créer une nouvelle version bilingue et sa migration.
La qualification actuelle ne l’autorise pas implicitement ; les inconnues et
revues humaines manquantes des rapports actuels restent inchangées.

## English

This optional experiment parses the whole input twice with parse5 8.0.1 under
enabled and disabled scripting hypotheses. It never executes page scripts or
observes a browser, rendered DOM or search engine. It prepares TS07/TS10 source
reader work; TS01 extraction remains a separate proposal.

Four inventories retain robots/googlebot meta, canonical links, HTML `a[href]`
anchors and base elements, with interpreted attributes, calculated ancestors and
head/body/other context, raw start tags and exact UTF-16 source spans. Template
signals are separate. No URL resolution or SEO policy is applied. Each inventory
compares as identical, different or unavailable; identical empty lists are not
success. Google documents body robots meta support and a head requirement for
HTML canonical links in the sources above. Tree position is not engine observation.

Python 3.9+ supervises an optional **Node 24** runtime. Official pinned parse5 and
entities 8.0.0 archives, file manifests and MIT licenses ship in the package;
there is no npm install, lifecycle hook, runtime download or private infrastructure
dependency. The usual TSEP verifier does not require Node. Use the two commands
above with new output paths. Optional Node qualification is recorded separately
from the Python verifier's dependency integrity and supervisor failure tests.

The caller explicitly declares UTF-8. Invalid bytes fail; initial U+FEFF and input
newlines are retained, without HTTP/HTML charset detection. Parser preprocessing
is separate. Offsets are zero-based UTF-16 code units with exclusive end, never
UTF-8 byte or Python code-point offsets. Missing locations remain missing; Python
rechecks every available raw tag against the exact source.

Bounds are 8 MiB input, 30 seconds per Node process, 128 MiB V8 old space (not total
process memory), 200,000 tree nodes, depth 256, 50,000 signals and 1,000 errors per
hypothesis, and 32 MiB compact JSON output. Tree bounds apply after parsing; the
process deadline and V8 setting constrain parsing. Reading failures discard that
reading's partial signals. Missing Node, modified dependencies, timeout or process
failure cannot fall back to another reader or create a TSEP outcome.

Selected documented network APIs listed in the result are guarded, without an OS
network-isolation claim. Node filesystem permission permits only temporary-folder
reads, without filesystem-write, child-process or native-addon permission.
Ambient Node preload/module-path variables are removed. Page JavaScript is never
run. Parser errors, including duplicate attributes, remain visible. Complete means
the bounded inventory finished, not valid HTML; no reported errors is not a validity
certificate. The reader is not imported by the normative pipeline.

The original 36 authored synthetic cases gave parse5 71/72 matches and historical
html5lib 65/72. One enabled-scripting noscript oracle was wrong; immutable v1 and
explicitly amended v2 preserve the correction and its timing. Retrospective
comparison gives 72/72 and 66/72 respectively, without new independent expectations.
The justification follows RAWTEXT closing-token handling, restoration from text
to in-head mode, insertion of the following meta, then non-whitespace text ending
head before the canonical. The linked WHATWG sections support this reasoning.
Twelve further cases were frozen before portable implementation; two additional
bounded-refusal checks test depth and excessive parser errors. These finite checks
do not establish all-HTML support, independent review or browser equivalence.

Migration is intentionally none: draft.14 rules, normative fingerprint and earlier
reports stay unchanged. Promoting any TS07/TS10 agreement rule requires explicit
eligibility, error/encoding policy, complete evidence, a distinct bilingual version
and migration. Current unknowns and missing human reviews are not resolved here.

## Source retention / Conservation des sources

[Dated method references](../provenance/source-tree-references.json) record URL,
capture date, scope and SHA-256 for WHATWG and the three Google pages. Full captures
are retained by the development custodian, outside this distribution. Official
npm package captures are redistributed unmodified with their licenses and
[per-file provenance](../third_party/source-tree/packages.json). Archive integrity
does not authenticate a runtime or prove the truth of its output.
