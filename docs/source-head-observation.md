# Source/head observation 1 / Observation source et head 1

## Français

Cette expérience facultative prépare la lecture source de TS10. Elle ne change
aucune règle ni aucun verdict de draft.15. Node 24 est requis pour l'expérience,
pas pour le vérificateur Python. Aucun script du document n'est exécuté.

Une balise canonical située entre deux chaînes de caractères ressemblant à
`<head>` et `</head>` n'est pas nécessairement dans le head construit. À l'inverse,
la construction HTML peut réinsérer dans le head une balise écrite après sa
fermeture. L'expérience conserve séparément :

- l'inventaire complet de métadonnées construit dans les deux hypothèses de scripts ;
- les tokens de la source, depuis son début jusqu'au token qui construit le body
  ou frameset du document, ou jusqu'à la fin du fichier ;
- les piles ouvertes et modes d'insertion avant/après chaque token, les fermetures
  explicites du head et les balises de fermeture sans élément correspondant dans
  la pile observée depuis le dernier template.

Les tokens textuels adjacents sont regroupés uniquement si leurs piles et modes
restent identiques. Leurs types, nombre et intervalle exact restent conservés.
Commentaires et balises ne sont jamais fusionnés avec ces segments. Les offsets
UTF-16 sont reliés aux octets d'origine, après le même décodage HTTP UTF-8 explicite
que [l'inventaire HTTP](source-http-inventory.md). Le superviseur exige une couverture
contiguë du préfixe ; une lacune ou un dépassement rend l'observation indisponible.

La pile est celle du parseur, pas un DOM rendu. Les modes numériques appartiennent
aux interfaces internes de parse5 8.0.1, épinglées avec entities 8.0.0. Le proxy
observe uniquement la livraison du tokenizer au parseur : le retraitement interne
d'un token ne crée pas une nouvelle balise source. Une mise à jour du parseur
exigerait une nouvelle qualification. Les inventaires de référence sont comparés
intégralement pour vérifier que l'instrumentation ne les modifie pas.

### Cas contradictoires figés

Le corpus `tests/fixtures/source-head-v1.json` contient 32 documents synthétiques,
avec attentes écrites et empreinte avant le premier lancement du nouveau lecteur.
La qualification vérifie 64 lectures, avec les mêmes inventaires que le lecteur
antérieur. Exemples de faits attendus :

| Source synthétique | Scripts activés | Scripts désactivés |
| --- | --- | --- |
| Canonical dans un head explicite ou implicitement construit | head | head |
| `img` puis canonical dans le head écrit | body | body |
| Pixel dans `noscript`, puis canonical | head | body |
| Canonical après un `</head>` explicite, avant body | head, réinsertion observée | head, réinsertion observée |
| Faux canonical dans un script ou commentaire | aucun élément canonical correspondant | idem |
| Canonical dans un template ordinaire | contenu du template conservé | idem |
| `</div>` surnuméraire dans le head | token conservé malgré l'absence d'erreur parse5 signalée | idem |

Ces faits **ne sont pas des décisions d'admissibilité SEO**. La position de l'arbre
ne prouve pas que Google accepte une réparation ; une absence d'erreur signalée
ne prouve pas la validité du HTML. La [documentation Google sur les métadonnées](https://developers.google.com/search/docs/crawling-indexing/valid-page-metadata)
décrit une limite après les éléments invalides du head. Elle ne qualifie pas
explicitement toutes les réinsertions de la construction HTML. Les règles
[WHATWG](https://html.spec.whatwg.org/multipage/parsing.html) décrivent cette
construction, pas la sélection canonique d'un moteur. Les captures datées et
empreintes figurent dans `provenance/source-head-v1.json`.

La future politique TS10 doit encore distinguer signal hors head, signal réinséré,
conflit indépendant et contexte inconnu. Les canonical relatives ne sont pas
résolues ni promues en conformité ; les bases et modificateurs sont seulement
conservés. Aucune exemption de rendu ou revue de contenu n'est déduite. A04 et sa
résolution des liens nécessitent une qualification distincte.

### Reproduction et limites

```sh
python3 scripts/source_head_check.py --node /path/to/node24 --output-dir new-qualification
python3 experiments/source_head.py body.html --content-type 'text/html; charset=utf-8' --node /path/to/node24 --output new-observation.json
```

Bornes héritées : corps 8 Mio, 200 000 nœuds, profondeur 256, 50 000 enregistrements,
1 000 erreurs signalées, processus 30 s, old-space V8 128 Mio (pas RSS).
Le préfixe est borné à 200 000 livraisons et 50 000 segments ; le résultat attribué
formaté est limité à 32 Mio. Aucun téléchargement ou repli automatique. Le garde
réseau couvre des API Node publiques, sans constituer une isolation système.
Une lecture incomplète conserve son motif et ne fournit aucune liste partielle
permettant de conclure par absence. Les tests Python exercent attribution altérée,
préfixe incomplet et runtime absent ; ils ne remplacent pas la qualification Node.

L'application locale à trois anciennes captures Edikka est rétrospective : chaque
canonical y est observée dans le head selon les deux hypothèses. Il ne s'agit ni
d'une nouvelle visite, ni d'un plan TS10 déclaré avant ces captures, ni d'un résultat
TS10-A01. Les captures conservent leur date du 10 octobre 2026 à 19:42 UTC.

## English

Optional experiment 1 prepares TS10 source reading without changing draft.15's
rules or outcomes. Node 24 is optional to the Python core. No document scripts run.
Retain complete metadata inventories for both scripting hypotheses and a source
token prefix ending at the token constructing document body/frameset or EOF.
Observe open stacks, pinned parse5 insertion modes, explicit document-head closure
and unmatched end tags relative to the stack after the last template. These are
parser facts, not rendered DOM, HTML validity or search-engine admissibility.

The tokenizer-to-parser proxy does not observe internal reprocessing as new source
markup. Adjacent character/whitespace deliveries are coalesced only with identical
before/after stacks and modes; exact contiguous spans, kinds and counts remain.
Markup and comments are not merged into text. The UTF-8 HTTP profile and original
body-byte attribution remain unchanged. Missing span coverage is rejected.
Internal parse5 8.0.1 interfaces require requalification if changed. Complete prior
metadata inventories are compared for instrumentation noninterference.

The prefrozen 32-document synthetic oracle defines 64 expected readings. It covers
implicit heads, img/text closure, noscript pixels, after-head reinsertion, ignored
end tags, raw-text/comment decoys, ordinary/declarative templates, foreign context,
duplicates, differing/relative href values, bases and modifiers. Expected facts
are authored before execution, not extracted to match parser output. The table
above describes observations only. Google documentation and WHATWG tree construction
have different scopes; neither makes every tree repair an accepted SEO declaration.
Dated sources and fingerprints are in provenance/source-head-v1.json.

Future normative integration must separately define outside-head signals, repairs,
independent conflicts and unknown contexts. No relative canonical is resolved into
compliance. Bases/modifiers are retained without a verdict. No rendered/content
review is waived and A04 URL resolution is not upgraded. Retrospective application
to three retained October 10 19:42 UTC Edikka responses is not a prior TS10 plan,
new visit, Google observation or TS10-A01 outcome.

Commands above reproduce the qualification or inspect an explicit UTF-8 body.
Bounds: 8 MiB body, 200,000 tree nodes, depth 256, 50,000 records, 1,000 reported
errors, 30-second process deadline, 128 MiB V8 old-space (not RSS). Prefix: 200,000
deliveries and 50,000 segments. Final attributed formatted JSON: 32 MiB. Unknown
runtime/encoding, incomplete observations or exceeded bounds cannot establish
absence. Public-API network guard is not OS isolation. Python tamper/missing-runtime
tests are distinct from actual Node qualification. No automatic download/fallback.
