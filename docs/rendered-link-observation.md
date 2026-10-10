# Rendered links / Liens rendus — observation expérimentale 1

## Français

Cette expérience prépare la lecture des liens rendus de TS10-A04. Elle ne change
ni draft.17, ni un verdict, ni les collecteurs et captures historiques. Ce n'est
pas encore un nouveau lecteur normatif. Les [références datées](../provenance/rendered-links-v1.json)
fondent les attentes HTML/CSP ; elles ne décrivent pas Googlebot.

Le collecteur conserve la propriété **href_property**, l'attribut href brut
(absence distincte de chaîne vide), les attributs avec namespace, node.baseURI,
ainsi que document.URL, baseURI, characterSet, contentType et readyState avant et
après le parcours. Une propriété href peut être la chaîne brute d'une URL non
analysable : l'observateur ne la nomme donc pas « URL résolue » et ne prouve pas
sa validité. Il ne remplace jamais la valeur observée par un calcul source.

Le parcours suit les enfants physiques puis chaque shadow root ouvert. Il
conserve a/area/link/base/form/template/iframe/frame dans tous les namespaces,
les input/button HTML avec formaction et les hôtes shadow ouverts. Chaque record
garde son chemin physique, ses ancêtres, son ordre et son index de visite. Seuls
a/area/link/base HTML ont une lecture de propriété href. SVG, xlink:href et
ancêtres étrangers restent identifiables sans assimilation à l'API HTML. Les
fragments template, documents de frame et affectations de slot ne sont pas
parcourus ; les racines fermées restent inconnues. Aucune origine supposée du
nœud ne provoque un filtrage silencieux.

Le collecteur ne clique pas, n'active pas de lien, ne soumet pas de formulaire,
ne reparcourt pas une sérialisation et n'émet pas de requête. Le **laboratoire**
distinct crée les documents synthétiques, applique les mutations déclarées et
exporte leurs observations vers son seul serveur local. Ce sont des fonctions
différentes. L'exécution est dans le contexte de la page : API, horloge et origine
des nœuds ne sont pas authentifiées. Des faits documentaires égaux avant/après
ne prouvent pas l'atomicité du relevé ou l'absence d'une mutation intermédiaire.
Les attributs data-probe permettent une correspondance uniquement parce que le
laboratoire les a instrumentés ; ils ne fournissent aucune méthode d'identité
source/DOM sur un site réel.

Bornes déclarées : 65 536 nœuds visités, profondeur physique 128, 8 192 records,
256 attributs par record, 256 Kio par chaîne et par record, 4 Mio pour les records,
2 secondes coopératives. Une interruption garde le préfixe et son motif, jamais
un inventaire complet. Le lecteur refuse les champs manquants, couvertures
inventées, doublons, dépassements ou surrogates isolés hors profil UTF-8 scalaire.
Ces bornes ne sont pas une isolation mémoire ni une échéance préemptive contre
des getters hostiles. L'expérience n'est pas qualifiée pour une page arbitraire.

### Laboratoire et résultat conservé du 10 octobre 2026

Les 26 recettes, avec 36 éléments instrumentés attendus, ont été figées **avant
implémentation**. Le plan et les réponses sont scellés avant navigation. Une
origine aléatoire `.localhost` liée à 127.0.0.1 reçoit 26 documents HTTP UTF-8 en
iframes, dans une seule session navigateur. Chaque document observe son propre
DOM après load ; le contrôleur conserve les messages et envoie un export local.
Les requêtes/réponses brutes sont conservées ; visites supplémentaires, exports
manquants, session/condition HTTP, changement d'outil ou de réponse sont refusés
à l'analyse. Le reçu n'est ni une signature ni un verdict. La borne de transport
de ce corpus est 2 Mio par POST, distincte de celle du collecteur général.

**Résultat observé : 25 attentes satisfaites sur 26 ; une divergence non résolue.**
Dans `invalid-base`, avec une première base `http://[` et une deuxième base
valide, l'attente initiale est le repli sur l'URL HTTP du document. Le navigateur
déclaré Chrome/155 a fourni `about:blank` pour document.baseURI/node.baseURI et
`x` pour la propriété href du lien relatif `x`. L'URL du document est restée celle
du cas HTTP. L'attendu initial, l'échec et les octets sont conservés. Aucune
correction d'oracle, aucune équivalence avec tous les navigateurs, aucune
promotion normative de ce comportement. Le rejeu de cette campagne doit
retrouver **25/26 et quitter avec le code 1**. Reproduire un désaccord n'est pas
transformer la qualification en réussite.

Les cas concordants couvrent notamment mutations de base/href, première base,
base target seul, schémas data/javascript, CSP none/self, href absent/vide/
invalide/Unicode/non HTTP, area, SVG/xlink, HTML sous SVG, template, shadow ouvert
et fermé, frames et formulaires. Les 12 essais d'API simulées ajoutés après
implémentation vérifient séparément les bornes et refus du collecteur ; ils ne
mesurent aucun navigateur. Les tests Python utilisent des records écrits à la
main et un client HTTP synthétique ; ils ne prouvent pas l'exécution du DOM.

```sh
python3 examples/rendered_links_lab.py serve --output new-campaign
# Ouvrir dans un navigateur l'URL « base » affichée ; attendre le reçu, puis Ctrl-C.
python3 examples/rendered_links_lab.py analyze new-campaign --output new-analysis.json
node scripts/rendered_links_guards.mjs
```

Le rejeu analyse les pièces sans nouvelle navigation. Une qualification sur
navigation principale, la divergence de base invalide, la validité des URL,
l'attribution d'environnement, les états interactifs et la future politique A04
restent à traiter séparément. Ni conformité d'Edikka, ni exhaustivité des liens,
ni indexation, ni classement ne découlent de cette expérience.

## English

This supplemental experiment prepares rendered A04 evidence without changing
draft.17, old collectors, snapshots or decisions. It retains **href_property**,
raw namespaced attributes (missing differs from empty), node.baseURI and document
URL/base/encoding/type/readiness before and after a bounded physical traversal.
An invalid href getter can return the raw string: no parsed-URL success is
inferred and no source calculation repairs the browser value.

Selected named elements, HTML form overrides and open-shadow hosts retain paths,
ancestors and visit order. Only HTML a/area/link/base expose an observed href
property. SVG/xlink and foreign ancestry remain distinct. Frame documents,
template fragments and slot expansion are excluded; closed shadows remain
unknown. No link activation, form submission, reparse or network call occurs in
the observer. The separate synthetic harness mutates its authored fixtures and
exports observations to its loopback receiver. Page-realm APIs, node origin and
clock are not authenticated. Equal before/after facts do not prove an atomic
snapshot. Laboratory data-probe labels do not establish real source/DOM identity.

Limits are 65,536 visited nodes, physical depth128, 8,192 records, 256 attributes,
256 KiB per string/record, 4 MiB records and a cooperative two seconds. Interrupted
prefixes never imply completeness. The reader rejects malformed coverage,
duplicates, truncation and lone surrogates outside its scalar UTF-8 profile.
This is neither memory isolation nor a preemptive hostile-getter deadline.

Twenty-six prior-authored recipes specify 36 instrumented elements. HTTP bytes,
plan, tool identities, observations and receipt are retained from one finite
UTF-8 iframe browser campaign. Extra/missing visits, session-bearing exchanges,
changed bytes and tools are refused. The corpus export is bounded to 2 MiB.
On October 10, 2026, **25/26 expectations matched**. The invalid first base
`http://[` produced document/node base `about:blank` and href property `x`, rather
than the expected HTTP document fallback. The declared client was Chrome/155;
this is not authenticated browser identity or cross-engine evidence. The initial
expectation and mismatch remain unchanged. Offline replay must reproduce 25/26
with exit1; reproducibility does not turn qualification into success.

Twelve later-authored API-double checks verify guard behavior, not browser
semantics. Python tests likewise use authored records and a synthetic HTTP
client. Main-frame qualification, the unresolved base divergence, URL validity,
environment attribution, interactive states and a future normative A04 policy
remain separate work. No real-site, indexing, ranking or certification claim.
