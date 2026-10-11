# Supplied rendered JSON-LD 1 / JSON-LD rendu fourni 1

## Français

Cette couche facultative conserve le JSON-LD du HTML reçu et celui d'états DOM
structurés **fournis**, puis compare leurs textes sélectionnés. Elle prépare
TS31–33 sans modifier draft.27, les 12 contrôles outillés ou leurs 33 règles.
Elle ne lance ni navigateur ni collecte HTTP. Les arbres rédigés restent
`authored-synthetic` ; une attribution `same-navigation` fournie ne devient pas
une navigation authentifiée.

### Parcours et plan

`experiments/jsonld_rendered.py` prend un objet avec exactement `plan`, `http`,
`http_received_at`, `contexts` et `states`. Les dates comportent un fuseau.
Le plan contient exactement :

- `format: "jsonld-rendered-plan"`, `version: "1"` ;
- `declared_at`, `window_start`, `window_end`, avec déclaration au plus tard au
  début de fenêtre, puis réception HTTP dans cette fenêtre ;
- `start_url`, `final_url`, `crawler`, `source_base_iri` ;
- `states`, de 1 à 16 objets `{id, browser, browser_version, scenario}`.

Le scénario est une chaîne exacte décrivant attente et interactions prévues.
Le lecteur vérifie la concordance avec la chaîne fournie par l'état ; il ne
l'exécute pas et n'en authentifie pas l'exécution. Les identifiants d'états sont
uniques dans le plan. Les dates du plan sont déclarées, pas attestées par un tiers.

`http` est la trace native du lecteur borné existant : jusqu'à 20 échanges GET
HTTP/1.1, sans authentification, cookies, requête conditionnelle ou Range ; Host,
User-Agent et chaîne de redirections sont vérifiés. La réponse finale doit être
un 200 complet à l'URL prévue, avec le profil explicite HTML UTF-8 du lecteur
source. Les entrées textuelles historiques et les messages base64/SHA sont lus
selon leur contrat, sans correction de leurs octets. Les autres transports et
types de réponse ne sont pas déclarés invalides sur le Web : ils sont hors profil.

Chaque état fourni contient `id`, `observed_at`, `complete`, `errors`,
`javascript_enabled`, `browser`, `browser_version`, `scenario`, `structured_dom`,
et éventuellement `dom`. Aucun autre champ n'est ignoré silencieusement. La date
doit être postérieure ou égale à la réception HTTP et dans la fenêtre. Une capture
complète, JavaScript activé et une liste d'erreurs explicitement vide sont requis.
Un état attendu absent, dupliqué ou de contexte différent reste indisponible.
Un état imprévu est conservé dans l'entrée et signalé séparément, jamais substitué.
Les états sont indépendants : un état inutilisable n'empêche pas l'examen du suivant.
Ce format ne prouve ni continuité entre états ni stabilité temporelle.

### Arbre fourni, texte et base

L'enveloppe [structured-inventory-v2](structured-rendering.md) et le collecteur
`collectors/rendered_metadata.js` restent inchangés. Le lecteur exige le script
exact, l'empreinte du snapshot, une arborescence complète, une sérialisation
compagnon, l'URL du document, une liaison HTTP/navigation/client et les pièces
d'acquisition avec leurs empreintes. Les inconnues d'intégrité et erreurs API
interdisent l'usage de la surface. Un auteur peut fabriquer des pièces cohérentes :
ces vérifications ne prouvent pas leur authenticité.

Tous les scripts sont inventoriés avec espace de noms, attributs, position,
chemin dans l'arbre et fragments de texte. Pour un élément script, les nœuds Text
descendants sont concaténés en ordre d'arbre, selon `textContent` employé par
l'API JSON-LD §9.5. Les commentaires sont exclus. Le lecteur ne reparse pas
`outerHTML`, ne décode pas les entités et ne normalise pas les textes fournis.
Une donnée textuelle `null` est inconnue, jamais remplacée par une chaîne vide.
Un élément enfant de script créé dans le DOM contribue donc par son texte
descendant ; le comportement « texte des seuls enfants directs » serait différent.

Les bords shadow ne sont pas parcourus pour concaténer le texte ordinaire et les
slots ne sont pas aplatis. Les scripts du shadow ouvert sont inventoriés mais
exclus du profil de traitement ordinaire. Les documents des frames, fragments
template et shadow fermés restent hors couverture ; leur absence d'inventaire
n'est pas une absence de données structurées. Les scripts étrangers restent
distincts, y compris d'un script HTML situé dans `foreignObject`.

La base du traitement rendu provient de `tree.base_uri`, liée à l'empreinte du
snapshot. C'est la valeur de `document.baseURI` **fournie pour cet état** ; les API,
la CSP, la chronologie interne de la capture et cette valeur ne sont pas
indépendamment authentifiées. Elle n'est pas remplacée par l'URL finale, ni
recalculée naïvement depuis une balise base. Une base différente de l'URL du
document est conservée. Une base hors du profil HTTP(S), notamment `about:blank`,
rend la surface indisponible : ce n'est pas une erreur JSON-LD imputée à la page.
La base hypothétique de la source reste séparée.

### Traitement et comparaison

Le profil `structured-rendered-jsonld-exact-type-v1` reprend la sélection
`application/ld+json` exacte et l'assemblage tableau du [lecteur HTML](jsonld-html-observation.md).
Les variantes de type reconnaissables restent indéterminées. Chaque état conserve
ses diagnostics, documents combinés, expansion, graphes aplatis et espaces de
nœuds anonymes. Les contextes sont fournis hors réseau. Une erreur dans un bloc
sélectionné empêche le graphe complet de cet état, sans effacer les autres états
ou les constats indépendants du HTML source.

La comparaison porte sur la **séquence exacte des textes sélectionnés** du HTML
déjà parsé et du DOM fourni. Les deux hypothèses source restent distinctes. Le
nombre de scripts, les empreintes/multiplicités ajoutées ou retirées, un éventuel
changement d'ordre seul et l'égalité des paramètres de base sont conservés.
Les offsets bruts source restent consultables séparément. Ainsi, CRLF dans les
octets source, devenu LF au parsing, et LF dans le DOM donnent des textes égaux.
CRLF réellement fourni dans les nœuds DOM reste au contraire une différence.

`equal` ne signifie ni équivalence de graphes ni conformité : une base différente
peut modifier les IRI malgré un texte identique. `different` n'établit ni défaut
SEO, ni cause JavaScript, ni identité entre deux éléments. Un ID HTML identique
ou répété ne prouve pas qu'il s'agit du même nœud entre états. Les changements
d'attributs restent dans les inventaires ; aucun appariement de nœuds n'est inventé.
`absent` reste borné au profil sélectionné et ne justifie pas NA.

### Exécution et preuve de calcul

```sh
python3 experiments/jsonld_rendered.py request.json --node /path/to/node24 \
  --output new-observation.json
python3 experiments/jsonld_rendered.py new-observation.json --replay \
  --node /path/to/node24 --output new-replay.json
python3 scripts/jsonld_rendered_check.py --node /path/to/node24 \
  --output-dir new-qualification
```

Les sorties existantes sont refusées. Code 0 : observation produite, y compris
inconnues ou erreurs de données ; code 64 : invocation/plan/entrée indisponible.
Le qualificatif retourne 1 si un attendu diverge et conserve les tentatives.
Le rejeu recalcule toute l'observation à mêmes entrées, sources et runtimes,
sans nouvelle navigation ; il n'authentifie pas la collecte originale.

Bornes supplémentaires : entrée 32 Mio, sortie 128 Mio, 16 états au plus. Le
transport conserve 1 024 nœuds, profondeur 64, 512 Kio pour l'arbre et 256 Kio
pour sa sérialisation. Les limites source et JSON-LD restent celles de leurs
lecteurs. Chaque état est traité séparément avec ses contextes, notamment les
limites processeur de 128 Kio par document combiné, 1 Mio par contexte, 4 Mio par
requête et 30 s par enfant Node. Pas d'isolation réseau OS revendiquée.

29 cas de surface et 23 workflows ont été figés avant implémentation ; 8 frontières
de revue puis 3 cas issus de la discussion de méthode ont été figés avant leur
exécution. Tous sont rédigés. Les premiers tests ont détecté un format erroné des
fichiers d'empreinte ; seule cette présentation a été corrigée, sans modifier les
cas. Les exécutions et limites sont conservées dans la [provenance](../provenance/jsonld-rendered-v1.json).
Ces tests n'établissent pas une capture réelle Edikka ou une revue humaine.

## English

This optional layer compares selected JSON-LD text in parsed HTTP source and
supplied structured DOM states. It changes neither draft.27 nor its 12 controls
and 33 rules. It runs no browser or network collector. Authored inputs remain
synthetic; supplied same-navigation attribution is not authentication.

The five-field request contains `plan`, `http`, `http_received_at`, `contexts`
and `states`. The exact plan fields listed above declare a prior time window,
start/final URLs, actual client, a supplied source-base hypothesis and 1–16 named
browser/version/scenario states. Dates and scenario execution are supplied, not
attested. The bounded native HTTP reader checks complete anonymous GET exchanges,
redirects, client, final 200 and explicit HTML UTF-8. Other protocols remain outside
the profile. Missing, repeated or mismatched required states stay unavailable;
unexpected states remain separately recorded. States are independent, not a proof
of temporal continuity or stability.

The unchanged structured inventory 2 contract binds the exact collector, complete
topology, snapshot fingerprint, serialization companion, final document URL,
native HTTP, agent and supporting acquisition records. Known/unknown integrity
issues and API errors prevent interpretation. Coherently fabricated inputs can
pass structural checks. Null character data is not replaced by empty text.

All scripts retain namespaces, attributes, paths, positions and text parts.
DOM `textContent` concatenates descendant Text nodes in tree order, including text
inside element children, excluding comments. No serialization reparsing, entity
decoding, string normalization, shadow-edge traversal or slot flattening occurs.
Open-shadow scripts remain separately inventoried and excluded from the ordinary
profile; frames, template fragments and closed shadow remain outside coverage.

The processor uses the supplied snapshot's `base_uri`, attributed but not
authenticated, without substituting the final URL or recalculating it from base
elements. A changed HTTP(S) base is retained. Opaque/non-HTTP(S) bases make the
surface unavailable, not the page's JSON-LD invalid. Source-base hypotheses remain
separate. JSON-LD exact-type selection, all-script array combination, context
inputs, notices, errors and graph boundaries use the existing offline processor.
Separate states keep separate blank-node scopes. A failed state never erases
source diagnostics or other states.

Comparison uses parsed source text, not raw source bytes. Source CRLF normalized
to LF and supplied DOM LF compare equal; actual CRLF in a supplied DOM remains a
difference. Counts, added/removed payload hashes and multiplicities, order-only
changes and base-parameter equality remain explicit. Equality is not semantic or
factual equivalence. Differences do not establish cross-state node identity,
JavaScript causality or an SEO defect. Repeated HTML IDs do not identify a node
across states. No TSEP, Schema.org, Google eligibility or whole-page absence claim.

Commands, exit meanings and bounds are listed above. Exact replay recomputes the
entire observation using retained inputs, source and runtime identities; it is
not a new browser visit. 29 supplied-surface cases and 23 workflows were frozen
before implementation; eleven later review boundaries were frozen before their
execution. All are authored. The first targeted run failed because checksum
sidecars used the wrong text format; fixtures and expectations stayed unchanged.

## References / Références

- [JSON-LD 1.1 API §9.5: extraction uses textContent](https://www.w3.org/TR/json-ld11-api/#html-content-algorithms)
- [DOM: descendant text content](https://dom.spec.whatwg.org/#concept-descendant-text-content)
- [HTML: document base URLs](https://html.spec.whatwg.org/multipage/urls-and-fetching.html#document-base-url)

Dated retrieved excerpts and their fingerprints are retained in the development
record identified by provenance; these references do not certify this method.
