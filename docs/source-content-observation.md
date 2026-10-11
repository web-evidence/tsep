# Source content observation 1 / Observation du contenu source 1

## Français

Cette expérience facultative prépare **TS44**, après TS34/TS35 (performance) et
TS42/TS43 (usages, accès et journaux des agents). Elle ajoute un lecteur structurel,
**sans modifier draft.23, ses 24 règles ni aucun verdict**. TS44 n'a pas encore de
règle atomique exécutable. Les observations ne deviennent jamais C, NC ou NA.

### Question et entrées

Un même texte peut être un fait dans le corps HTML, une chaîne dans un script,
un commentaire, un modèle inactif ou une donnée dans un arbre étranger. Une simple
recherche de caractères ne distingue pas ces situations. Le lecteur reçoit :

- les octets décompressés d'un corps complet fourni ; sa collecte et son origine
  ne sont pas authentifiées par cet outil hors ligne ;
- une unique valeur Content-Type `text/html; charset=utf-8` (profil borné existant),
  sans détection implicite ni remplacement d'octets invalides ;
- de 1 à 64 identifiants `id` littéraux, distincts, sensibles à la casse, sans espace
  ASCII, de 128 caractères au maximum ; ce ne sont pas des sélecteurs CSS ;
- un chemin explicite vers Node 24, avec parse5 8.0.1 / entities 8.0.0 épinglés
  dans l'inventaire existant. Aucun téléchargement n'est effectué.

### Observations conservées

Le parseur construit deux arbres statiques, avec l'hypothèse de scripts activés
et celle de scripts désactivés. **Aucun script n'est exécuté dans les deux cas.**
Chaque arbre complet conserve ses nœuds, parents, ordre, noms, espaces de noms,
attributs, textes et commentaires. Les contenus de template sont des fragments
séparés ; une déclaration shadow ne prouve pas son attachement. Les documents des
frames ne sont pas chargés. Les erreurs et réparations du parseur restent visibles.

Pour chaque identifiant, tous les éléments correspondants sont conservés, même
si plusieurs portent le même ID ou si un élément est dans le head, un template
ou du SVG/MathML. Aucun premier résultat n'est choisi silencieusement.

`ordinary_text` concatène dans l'ordre de l'arbre les textes descendants sous body,
en excluant les contextes head, template, script, style, étrangers et frames.
C'est une projection structurelle propre à l'expérience, **pas `innerText`, pas
une mesure de visibilité et pas une preuve de suffisance sémantique**. Aucun espace
n'est ajouté aux frontières de balises ; entités, retours à la ligne et réparations
ont les valeurs produites par le parseur. Les textes exclus restent consultables.

Les contextes `hidden`, `inert`, `aria-hidden=true`, style en ligne, details, dialog
et noscript restent attachés aux textes concernés. Un texte masqué n'est donc pas
promu en contenu admissible ; le lecteur ne décide pas cette admissibilité. La
présence d'une classe CSS, l'absence de drapeau ou un arbre complet ne prouve jamais
la visibilité. Les feuilles de style et pseudo-éléments ne sont pas évalués.

Les href des éléments a/link/area restent littéraux, avec nom/espace de noms et
contexte. Les autres attributs, y compris ceux qualifiés par un espace de noms,
restent dans l'arbre intégral. Aucune résolution d'URL, capacité d'agent, découverte
effective, accessibilité HTTP, vérité d'un fait ou cohérence de version n'est déduite.

### Attribution, cas et limites

Les positions UTF-16 du parseur sont reliées aux octets UTF-8 originaux en tenant
compte du BOM initial consommé. Chaque intervalle conservé est revérifié contre ses
octets. Pour un élément, il désigne sa balise ouvrante ; pour un texte réparé, il
peut inclure du balisage intermédiaire. L'intervalle n'est pas une correspondance
bijective entre caractères source et texte construit. Un nœud implicite peut ne
pas avoir de position. Les valeurs parsées et les octets restent distincts.

La fixture `source-content-v1.json` fige **30 documents / 60 attentes** avant le
lecteur. Elle couvre notamment scripts/commentaires, entités et Unicode avec BOM,
contextes masqués, ID dupliqués, templates/shadow déclaratif, noscript, head,
SVG/MathML, href contradictoires, récupération de table et texte de fallback iframe.
La qualification ajoute six vérifications de dépassements (deux hypothèses pour
profondeur, nœuds et erreurs). Les observations de test sont synthétiques ; Node
est réellement exécuté, mais aucun navigateur, réseau ou agent ne l'est.

Bornes : corps 8 Mio, 20 000 nœuds, profondeur 128, 1 000 erreurs, processus Node
30 secondes, old-space V8 128 Mio (pas RSS), résultat JSON attribué 32 Mio. La
projection admet au maximum 512 correspondances, 50 000 enregistrements texte/lien
et 2 097 152 caractères cumulés texte/href. Le garde d'API réseau ne constitue pas
une isolation système. Les variables NODE_* héritées sont retirées.

Un dépassement pendant le parsing ou la traversée efface tout l'arbre partiel et
garde son motif ; la sélection devient `null`, jamais une liste vide assimilée à
une absence. Un dépassement du superviseur, de la projection, un runtime absent,
un encodage non qualifié ou une attribution incohérente rendent l'observation
indisponible. Aucun lecteur de secours ne prend une décision à sa place.
La validation structurelle n'authentifie pas un fichier fourni : le rejeu sur les
octets est nécessaire, les empreintes seules ne prouvent pas une origine.

```sh
python3 scripts/source_content_check.py --node /path/to/node24 --output-dir new-qualification
python3 experiments/source_content.py body.html --content-type 'text/html; charset=utf-8' --id critical --node /path/to/node24 --output new-observation.json
```

### Intégration encore à faire

TS44 devra fixer **avant la capture** les faits, sources, liens, dates et versions
critiques, les consommateurs visés et leurs capacités documentées. Le profil de
référence proposé utilise un client sans JavaScript : une simple déclaration de
support JS ne suffira pas à rendre admissible un contenu exclusivement injecté.
Les revues devront nommer et lier exactement les représentations examinées.
Une ressource publique exige un chemin de découverte explicite et une capture
qualifiée ; sa seule existence, un HTTP 200 ou un fichier llms.txt ne suffiront pas.

Le laboratoire prévu comparera HTML serveur, contenu injecté, ressource liée de
même version et ressource liée périmée. Un éventuel DOM rédigé portera la mention
**« DOM rédigé, non observé dans un navigateur »** ; une requête HTTP réelle ne
change pas cette attribution. Aucune observation nouvelle d'Edikka, visite réelle
d'agent, promesse de citation ou nouvelle qualification du lecteur TS01 n'est faite.
La politique normative, ses cas atomiques, ses revues, son laboratoire et sa
migration bilingue restent à intégrer après cette observation.

## English

Optional experiment 1 prepares TS44 after performance and the TS42/TS43 agent
controls. Draft.23, its 24 rules and all outcomes remain unchanged. TS44 still has
no executable atomic rules. Structural observations are never C/NC/NA decisions.

Inputs are supplied decompressed body bytes, one explicitly qualified UTF-8 HTML
Content-Type and 1–64 distinct case-sensitive literal IDs (at most 128 characters,
no ASCII whitespace), plus explicit Node 24. Collection completeness and origin
are caller evidence, not authenticated by this offline tool. Pinned parse5 8.0.1
and entities 8.0.0 require no download. Both scripting hypotheses build static
trees; neither executes document scripts.

Retain complete topology, namespace-aware attributes, text/comments, separate
template fragments, parse errors, implicit/recovered nodes and exact available
source intervals. Shadow declarations do not prove attachment. Frame documents
are not loaded. Every matching ID is retained, including duplicates, head,
template and foreign contexts. No implicit first-match selection.

The experiment's `ordinary_text` joins tree-ordered descendant text under body,
excluding head/template/script/style/foreign/frame contexts. It adds no separator,
case folding or whitespace normalization beyond parser behavior. This is neither
innerText nor visibility, semantic sufficiency or agent availability. Excluded
text remains available. Hidden/inert/aria-hidden, inline styles, details/dialog and
noscript contexts are retained. Stylesheets/pseudo-elements are not evaluated;
absence of flags never proves visibility. a/link/area href values remain literal,
with namespace/context. All attributes remain in the full tree. No URL resolution,
discovery, HTTP access, fact truth, version coherence or consumer capability follows.

The supervisor maps UTF-16 spans back to exact original UTF-8 bytes, retaining BOM
consumption. Element intervals cover start tags. Recovered text intervals may span
intervening markup; parsed text and raw bytes are not asserted to correspond
bijectively. Implicit nodes may lack a location. Structural validation does not
authenticate supplied files; replay and separately established provenance matter.

The 30-document / 60-expectation synthetic oracle was frozen before implementation.
It covers source/script/comment distinctions, Unicode/BOM/entities, hidden contexts,
duplicate IDs, template/shadow declarations, noscript, head, SVG/MathML, literal or
duplicate hrefs, table recovery and iframe fallback. Six additional limit checks
exercise both hypotheses for depth, node and error limits. Node is executed; no
browser, network or real agent observation is claimed. Python integrity tests use
a separately retained actual parser output, not a browser capture.

Bounds: body 8 MiB, 20,000 nodes, depth 128, 1,000 errors; Node 30 seconds and
128 MiB V8 old-space (not RSS); attributed JSON 32 MiB. Selection: 512 matches,
50,000 text/link records, 2,097,152 aggregate text/href characters. Public-API network
guards are not OS isolation. Inherited NODE_* variables are removed. A partial
tree is discarded with its reason and null selection. Other unavailable runtime,
encoding, attribution, process/output/projection limits cause an unavailable
observation, with no fallback and no empty inventory interpreted as absence.

The commands above reproduce finite qualification or observe a supplied body.
Future TS44 integration still needs a prior critical-content inventory, exact
representation-bound reviews, explicit resource discovery/access and coherence
rules, atomic contradictory cases and bilingual migration. A reference client
without JavaScript prevents a mere asserted JS capability from qualifying an
injected-only fact. Four planned laboratory variants compare server HTML, injected
content, same-version linked resource and stale linked resource. Any authored DOM
must explicitly say it was not observed in a browser, even if HTTP was observed.
No new Edikka assessment, actual agent visit, citation promise or TS01 reader
qualification follows from this experiment.

## Sources

The [DOM text model](https://dom.spec.whatwg.org/#concept-descendant-text-content),
[HTML noscript rules](https://html.spec.whatwg.org/multipage/scripting.html#the-noscript-element)
and [parse5 parse API](https://parse5.js.org/functions/parse5.parse.html) inform
structural terminology, not SEO acceptance or agent capabilities. Dated extracted
captures, scope and fingerprints are recorded in
[provenance](../provenance/source-content-v1.json). These are bounded text extracts,
not complete original HTTP captures. / Ces sources éclairent la structure, pas
l'admissibilité SEO ; les captures conservées sont des extraits textuels bornés.
