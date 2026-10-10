# Sitemap locations / URL des pages dans les sitemaps

## Français

Draft.14 ajoute à TS10-A03 le lecteur facultatif `sitemap-locations-v1`, version 1.
Le choisir **avant les captures** dans `intent.canonical.sitemaps.reader`.
Champ absent : lecteur historique inchangé. Valeur inconnue ou `null` :
indéterminé, sans repli. Les autres règles, populations, revues et conditions de
non-applicabilité restent exigées ; A03 seule ne donne jamais C à TS10.

Seul un `loc` directement sous `url`, dans le namespace exact
`http://www.sitemaps.org/schemas/sitemap/0.9`, désigne une URL de page. Sous
`sitemap`, il désigne un document enfant à examiner. Les préfixes XML sont libres,
les URI des namespaces doivent correspondre exactement. Un XML sans namespace
ou avec un namespace différent reste indéterminé. Les entités XML sont décodées ;
seuls espace, tabulation, CR et LF autour du `loc` sont retirés. Aucune autre
normalisation : casse, encodage d’URL et barre finale restent significatifs.
Les URL de page/enfant doivent être HTTP(S), absolues, sans fragment ni identifiants.

Le lecteur reconnaît les feuilles ordinaires `lastmod`, `changefreq`, `priority`
sous `url`, et `lastmod` sous `sitemap`, au plus une fois chacune. Leurs valeurs
sont relevées, sans validation de date, fréquence ou priorité. La seule propriété
de racine admise est `xsi:schemaLocation` dans le namespace XML Schema Instance ;
sa valeur est conservée, sans chargement ni validation du schéma.

Deux annotations sont reconnues sous `url` seulement :

- `link` du namespace `http://www.w3.org/1999/xhtml`, sans enfant ni texte non
  blanc, avec exactement `rel="alternate"`, `hreflang` et `href` non blancs ;
- `image` du namespace `http://www.google.com/schemas/sitemap-image/1.1`, sans
  attribut ni texte non blanc, avec exactement un `image:loc` non blanc. Les
  feuilles `caption`, `geo_location`, `title`, `license` peuvent être relevées au
  plus une fois, sans attribut ni enfant. Ces quatre métadonnées sont dépréciées
  dans la documentation Google ; leur lecture n’en recommande pas l’usage.

Les attributs/valeurs complets sont conservés avec leur position d’entrée et leur
nom étendu. Aucun `href` de traduction ni `image:loc` n’est une entrée de page.
Cette reconnaissance de structure ne valide ni hreflang, ni URL d’image, ni valeur
de métadonnée, ni traitement par Google. Le lecteur ne revendique pas une
validation XML Schema complète. Commentaires et instructions de traitement ne
sont pas interprétés ; les octets d’origine restent dans les captures.

Élément/attribut inconnu, extension news/video, `xml:base`, extension dans un
index, doublon de feuille, texte mixte, structure ambiguë, XML mal formé,
DTD/déclaration d’entité ou borne dépassée rendent le document entier indéterminé.
Pas de récupération partielle d’un document refusé. Bornes : 8 Mio après décodage
UTF-8, 200 000 éléments, profondeur 8 racine comprise, 50 000 entrées et
1 000 blocs image par entrée. Les limites HTTP et de collecte restent distinctes.

La règle conserve les limites de parcours existantes : captures attribuables,
au plus 100 documents fournis, profondeur d’index bornée, cycles refusés. Une
omission n’est établie qu’après examen complet de tous les index/enfants déclarés.
Un concurrent dans un autre document entièrement lu reste un échec malgré une
branche manquante. Le motif affiche le profil et le nombre d’annotations, avec
au plus seize aperçus de 160 caractères chacun, troncatures et surplus signalés.
Les valeurs complètes restent dans les captures et la sortie du lecteur.

Les 52 cas XML et 24 cas de contrôle ont été rédigés et figés avant le lecteur ;
ils sont synthétiques. Les 427 entrées antérieures et leurs résultats complets
sont vérifiés par empreinte. Cela ne constitue ni revue humaine indépendante,
ni validation d’Edikka, ni observation d’indexation.

## English

Draft.14 adds optional TS10-A03 reader `sitemap-locations-v1`, version 1. Declare
`intent.canonical.sitemaps.reader` before capturing. Absence retains the fixed
legacy reader; unknown or null values are inconclusive, with no fallback. Other
rules, populations, human reviews and positive absence conditions remain required.
Passing A03 alone never establishes whole-control C.

Only a direct `loc` under `url` in the exact Sitemaps 0.9 namespace listed above
is a page URL. Under `sitemap`, it identifies an expected child document. Prefixes
are arbitrary; namespace URIs must match exactly. Missing/wrong namespaces are
inconclusive. Decode XML entities and trim only surrounding XML space, tab, CR
and LF; compare literally, without URL case, escaping or trailing-slash
normalization. Page/child URLs must be absolute HTTP(S), without fragment or credentials.

Recognize optional base leaves lastmod/changefreq/priority under url, lastmod under
sitemap, at most once each. Retain their values without substantive validation.
The only accepted root attribute is XML Schema Instance schemaLocation: retain,
never fetch or validate its schema. Recognize under url only the exact XHTML link
and image:image namespaces/shapes listed above. XHTML link requires exactly rel
equal to alternate and nonblank hreflang/href, no children or non-whitespace text.
An image block has no attributes/non-whitespace text, exactly one nonblank image
loc, and optional caption/geo_location/title/license leaves at most once, without
attributes/children. Those four metadata fields are deprecated by Google; reading
them does not recommend their use. Preserve expanded names, entry positions and
complete attributes/values separately. Alternate href and image loc never count
as page entries. No hreflang, image URL, metadata value or engine assessment; not
full XML Schema validation. Comments/processing instructions are not interpreted;
original bytes remain in the captures.

Unknown names/attributes, news/video extensions, xml:base, index extensions,
duplicate leaves, mixed text, ambiguous structures, malformed XML, DTD/entity
declarations or exceeded bounds make the whole document inconclusive. No partial
recovery. Limits: 8 MiB of decoded UTF-8, 200,000 elements, depth 8 including the
root, 50,000 entries and 1,000 image blocks per entry. HTTP/collection limits are
separate. Existing attributed-capture, 100-document, bounded-index-depth and cycle
checks remain. Omission requires complete traversal; a competitor in another fully
read document remains fail despite a missing branch. Rule reasons name the profile,
count annotations and preview at most 16 records of 160 characters, explicitly
marking truncation/remaining records. Full values remain in captures/reader output.

The 52 XML cases and 24 control cases were frozen before implementation and are
synthetic. All 427 prior inputs and computed results are fingerprint-checked.
This does not establish independent human review, Edikka conformity or indexing.

## Sources

The namespace and entry model follow [Sitemaps protocol](https://www.sitemaps.org/protocol.html).
Extension separation follows [Google's combined sitemap examples](https://developers.google.com/search/docs/crawling-indexing/sitemaps/combine-sitemap-extensions),
[image sitemap documentation](https://developers.google.com/search/docs/crawling-indexing/sitemaps/image-sitemaps)
and [localized-version documentation](https://developers.google.com/search/docs/specialty/international/localized-versions).
Dated captures and fingerprints: [provenance](../provenance/sitemap-locations-v1.json).
These sources inform a deliberately bounded TSEP reader; they are not an
endorsement, implementation equivalence claim or new SEO criterion.
