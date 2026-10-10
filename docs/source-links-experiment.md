# Source links / Liens source — expérience 1

## Français

Cette expérience prépare TS10-A04 sans changer draft.16, ses treize règles, son
lecteur historique `urljoin` ou les lecteurs rendus. Elle calcule des faits
conditionnels, jamais pass/fail/NA ni conformité. L'oracle est écrit avant la
première implémentation : 50 URL et 22 documents HTML sous deux hypothèses.

L'entrée conserve les octets, le Content-Type UTF-8 explicite et l'URL finale
du document. L'inventaire source/head existant fournit les éléments HTML `a`
avec href, les base, les templates, erreurs et positions. Un a sans href n'est
pas résolu ; href vide l'est. Les attributs, y compris rel/nofollow, sont gardés.
Ce périmètre ne recense pas tous les hyperliens : area, liens SVG, frames et
attaches shadow restent hors couverture, sans verdict favorable implicite.

Le constructeur WHATWG URL de Node 24 calcule chaque référence décodée selon HTML.
On conserve href sérialisé, protocole, origine et copie sans fragment. On ne
supprime ni query vide, ni slash final, ni encodage de chemin pour inventer une
équivalence métier. Aucun fetch, événement ou script de la page n'est exécuté.
Une erreur de résolution reste un résultat explicite, pas un lien supprimé.

Pour chaque arbre statique, le premier base HTML avec href dans l'ordre de l'arbre
fournit une base candidate. Un href invalide ou de schéma data/javascript utilise
l'URL du document, pas le second base. Les base des templates ordinaires sont
conservés à part. Les deux hypothèses sont indépendantes ; aucune fusion de liens.
Voir [base HTML](https://html.spec.whatwg.org/multipage/semantics.html#the-base-element)
et [URL du document](https://html.spec.whatwg.org/multipage/urls-and-fetching.html#document-base-url).

La base ainsi calculée suppose l'absence de restriction CSP et de mutation par
script. Les champs CSP fournis, les meta CSP, erreurs, contextes étrangers et
déclarations shadow restent visibles avec leurs limites. La présence d'une CSP
n'est pas analysée ; son absence dans une entrée non renseignée n'est pas déduite.
Le cas synthétique base + CSP illustre donc un calcul conditionnel, pas la base
effectivement appliquée dans un navigateur. L'UTF-8 explicite évite d'inventer le
traitement d'une query sous un encodage différent. about:blank/srcdoc hors portée.

Les versions Node, V8, Ada, ICU et Unicode sont conservées. Node documente la
suppression de l'exigence ICU pour URL depuis 20.0.0/18.17.0 : enregistrer ICU ne
signifie pas lui attribuer l'algorithme IDNA actuel. Références datées et empreintes
dans [la provenance](../provenance/source-links-v1.json) ; captures dans le kit local.
L'oracle fini ne certifie pas toute la conformité WHATWG ni tous les runtimes.

Le processus URL est borné à 10 secondes, 128 Mio d'ancien tas, 50 000 requêtes,
64 Kio par chaîne, 4 Mio d'entrée et 16 Mio de sortie finale formatée. L'inventaire
source conserve ses bornes ; l'observation combinée ne dépasse pas 32 Mio. Refus
sans repli en cas de dépassement, runtime absent ou données mal formées. Le garde
d'API réseau n'est pas une isolation système. Intégrité n'est pas authenticité.

```sh
python3 scripts/source_links_check.py --node /path/to/node24 --output-dir new-qualification
python3 experiments/source_links.py body.html --content-type 'text/html; charset=utf-8' --document-url https://example.test/page --node /path/to/node24 --output new-observation.json
```

Avant une intégration normative, définir le champ de sélection préalable, la
couverture des types de liens, les inconnues CSP/base, les conflits indépendants,
le rendu et les comparaisons de famille. Une URL déclarée différente de sa propre
sérialisation ne doit pas être normalisée en silence ni devenir invisible à la
comparaison. Les fragments seuls et href vides peuvent désigner une variante
servie comme URL finale, ou la base applicable. La collecte doit garder l'URL
finale distincte de celle demandée. Ces décisions ne sont pas prises ici.

## English

This optional experiment prepares TS10-A04 without modifying draft.16 or its
legacy/source/rendered decisions. Fifty authored URL cases and 22 authored HTML
documents precede implementation. Complete source/head inventories retain HTML
a[href], base, templates, original byte positions and parse errors under two
static alternatives. Missing href is separate from empty href; rel/nofollow stays
visible without removing links. Area/SVG hyperlinks, frames and shadow attachment
are outside this finite ordinary-anchor scope, not presumed absent or conformant.

Node 24's WHATWG URL constructor retains serialized href, protocol, origin and a
fragment-free copy. Invalid resolution remains explicit. No query/path rewriting,
family normalization, source script execution, navigation or engine inference.
The first ordinary base with href supplies a conditional static base; invalid,
data or javascript first values fall back to the document URL, never the second
base. Template base declarations remain inactive in these source trees.

The calculation assumes UTF-8 and no CSP restriction or script mutation. Supplied
CSP headers/meta, parsing errors, foreign contexts and shadow declarations retain
review flags; missing CSP inputs are not interpreted as absence. A CSP test's
candidate base is explicitly conditional, not an observed browser baseURI.
The final response URL must be supplied; about:blank/srcdoc are excluded.

Node/V8/Ada/ICU/Unicode are recorded, without attributing modern URL IDNA to ICU.
The URL subprocess has a 10-second deadline, 128 MiB old-space cap, 50,000 requests,
64 KiB/string, 4 MiB input and 16 MiB formatted output. Combined source observations
are limited to 32 MiB. Refuse incomplete/bounded output or unavailable Node without
fallback. Public-API network guards are not OS isolation or authenticity guarantees.

Any future normative profile must separately specify element coverage, static
alternatives, source/rendered evidence, CSP/base unknowns, independent failures,
family URL serialization and migration. This finite experiment establishes no
TSEP verdict, browser equivalence or complete WHATWG conformance.
