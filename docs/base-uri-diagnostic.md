# Diagnostic de base invalide / Invalid-base isolation

## Français

Ce diagnostic explique les limites de l'[expérience de liens rendus](rendered-link-observation.md).
Il a été conçu **après** son premier résultat 25/26, puis figé avant ce nouveau
harnais. Ce n'est pas une nouvelle qualification indépendante préenregistrée.
Il conserve le collecteur, l'oracle et les résultats antérieurs sans modification.
Draft.17, A01/A02 et A04 ne sont pas modifiés par ce diagnostic.

Six cas sont comparés en navigation principale et en iframe, avant/après une
mutation prévue : sans base, base valide, base invalide seule, première base
invalide avant une valide, insertion d'une base invalide après load, remplacement
d'une base invalide par une valide. Les documents UTF-8 sont servis par une origine
aléatoire `.localhost` liée à 127.0.0.1. Le plan, les réponses HTTP, les sources des
outils, les lectures directes, les relevés du collecteur et les exports locaux sont
conservés. Aucun lien observé n'est activé. Les attributs de test sont instrumentés.

### Résultat observé le 10 octobre 2026 UTC

| Situation | Navigation principale et iframe, dans la session observée |
| --- | --- |
| Sans base ou avec une base valide | Base et propriété href correspondent aux attentes |
| Première base `http://[` non analysable | document.baseURI et node.baseURI valent `about:blank` ; href_property de `x` vaut `x` |
| Seconde base valide après celle invalide | Même résultat, aucune sélection de la seconde base observée |
| Insertion de la base invalide après load | Passage de l'URL HTTP du document à `about:blank` |
| Remplacement par `https://example.test/repaired/` | Base valide et href_property `https://example.test/repaired/x` |

Les **12 états témoins ou réparés sur 24** correspondent aux attentes ; les 12
états avec base invalide conservent le désaccord avec l'attendu HTML initial.
Deux phases d'un même document ne sont pas deux navigations indépendantes.
Les 12 documents ont produit 12 exports, plus une visite du contrôleur : 25
échanges HTTP. Le client déclaré est Chrome/155 dans une seule session. Cela
n'authentifie pas un build, ne couvre pas un autre moteur et ne prouve pas un
comportement de Googlebot. L'origine du désaccord dans l'implémentation demeure
inexpliquée ; il n'est plus limité au seul contexte iframe de notre premier essai.

Les getters lus directement et le collecteur concordent pour les 24 relevés,
dans le même contexte de page. Une contre-lecture read-only de l'outil sur le
témoin principal invalide retrouve href=`x` et l'URL du document, mais n'expose
pas document.baseURI ou node.baseURI. Ces champs restent indisponibles : aucune
valeur n'est reconstruite. Ce n'est pas un deuxième moteur de navigateur.

Le résolveur Node24 extérieur à la page retrouve **48/48 analyses URL/base
explicites** : `x` est analysable contre l'URL HTTP du document et ne l'est pas
contre `about:blank`. Ce contrôle ne choisit pas la base effective du navigateur.
Il n'efface donc pas les 12 divergences de sélection de base. La propriété
base.href reste distincte de la base figée ; un échec d'analyse peut restituer
l'attribut brut dans ce getter.

### Sources et portée de la suite

Les [pièces WPT datées](../provenance/base-uri-diagnostic-v1.json) sont épinglées
à `9ec154ff43db468923997c08bb08f905ceab62a5`. Quatre fichiers ont été lus :
`base_href_invalid.html` teste le getter d'une base détachée ; `base_multiple.html`
teste une navigation avec plusieurs bases ; `base_about_blank.html` une base
relative dans un document about:blank ; `Node-baseURI.html` des nœuds sans base
déclarée. Aucun de ces quatre tests n'établit notre cas exact. Ce constat n'est
pas un inventaire exhaustif de WPT. Aucun résultat d'exécution WPT n'a été obtenu.

La suite envisagée est une évolution **versionnée d'A04 seulement** : ne plus
déduire une destination déterminée d'une référence dépendante lorsque la première
base échoue à l'analyse WHATWG. Garder les URL strictement indépendantes, les deux
hypothèses source séparées, les anciennes versions, les bases vides/blanches et
les autres cas de repli distincts. A01 compare déjà les canonical littéralement,
sans résolution par base ; A02 reste une revue manuelle. Ce diagnostic ne leur
ajoute pas de test de destination, de 404 ou de redirection.

```sh
python3 examples/base_uri_diagnostic.py serve --output new-diagnostic
# Ouvrir l'URL « base » pour les iframes et chaque URL top du plan ; conserver les reçus.
# Arrêter le serveur avec Ctrl-C, puis analyser sans nouvelle navigation :
python3 examples/base_uri_diagnostic.py analyze new-diagnostic --output new-analysis.json
python3 scripts/base_uri_compare.py new-diagnostic --node /path/to/node24 --output new-node-check.json
```

Le CLI d'analyse retourne 1 lorsque des attentes restent insatisfaites. Le CLI
Node peut réussir pour les mêmes inputs explicites tout en gardant 12/24 pour les
attentes navigateur. Le rejeu vérifie réponses, outils, phases, contexte, requêtes
sans session et chronologie ; il ne garantit pas leur authenticité. Les tests
Python emploient des records écrits à la main, pas des mesures navigateur.

## English

This isolation diagnostic was designed **after** the first rendered-link 25/26
observation, then frozen before its own harness. It is not an independent
preregistered qualification. Old collector, recipe, observations and draft.17
decisions remain unchanged. Six cases compare top-level and iframe documents,
before/after a declared mutation, with prior HTTP bytes and local exports.

In the observed single session (declared Chrome/155), twelve control/repaired
states match expectations and twelve invalid-base states disagree. An invalid
first base `http://[` yields document/node base `about:blank` and href property
`x`; a later valid base does not change that. Insertion after load produces the
same effect; replacement by a valid base restores an absolute property value.
The discrepancy therefore is not confined to iframes in this environment.
Two phases are not independent navigations. Twelve visits/exports plus one
controller yield 25 HTTP exchanges. No link activation or Google observation.

Direct page getters and the collector agree for all24 snapshots. A tool-scope
cross-read confirms raw/property href `x` but does not expose either baseURI;
missing APIs stay missing. Node24 outside the page agrees on48 explicit URL/base
parses, without deciding which base the browser selects. Neither comparison
erases the twelve original expectation mismatches or proves cross-engine behavior.

Four pinned WPT sources were read, not executed. They cover detached base.href,
multiple-base navigation, about:blank relative bases and nodes without a base;
none of those four asserts this exact invalid first-base document.baseURI case.
This is not an exhaustive WPT search or a known browser-bug attribution.

The proposed next step is a separately versioned A04 policy for base-dependent
references under an unparseable first base, retaining independent URLs, both
source hypotheses and old versions. A01 already compares canonical values
literally; A02 remains manual. This diagnostic adds no canonical destination,
404 or redirect test. The browser analysis exits1 for mismatches; a successful
explicit-input Node comparison does not change that outcome. Replay checks
integrity, context and chronology, not authenticity. Python tests use authored
records rather than actual browser measurements.
