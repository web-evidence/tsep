# Experimental DOM metadata inventory / Inventaire DOM expérimental

**Observation tool 2. Unapplied to TSEP 0.1.0-draft.7.** No report outcomes,
certification, indexing or ranking inference. This implementation follows the
[design plan](proposals/rendered-metadata-inventory.md); it does not complete its
two-browser delivery criteria.

## Français

Le script `collectors/rendered_metadata.js` est une expression JavaScript de lecture
seule, à invoquer une fois après l'état prévu par la campagne. Il conserve l'arbre
accessible et une sérialisation complémentaire, sans reparsing ni nettoyage. Le
validateur `experiments/rendered_metadata.py` extrait les déclarations robots,
googlebot, canonical et base, leur emplacement, leurs attributs DOM ordonnés et
leurs URL brutes/résolues séparées. Aucun de ces résultats n'alimente l'évaluateur.

Le contrat conserve tous les nœuds traversés, y compris les composants et nœuds
auxiliaires. Un namespace étranger ne devient pas HTML. Les parents et l'ordre
préfixe doivent être cohérents ; un faux head dans body n'est pas le head du
document. Les shadow roots ouverts ont un chemin distinct ; les fermés restent
inconnus. Les documents des iframes et les fragments template ne sont pas
parcourus. Le texte de noscript n'est pas interprété comme du balisage.

Bornes v2 : 1 024 nœuds, profondeur 64, 524 288 octets UTF-8 d'arbre JSON,
262 144 octets de sérialisation, budget coopératif 2 000 ms et délai d'invocation
prévu de 5 000 ms. Le budget coopératif ne peut pas interrompre un getter bloqué.
Le résultat déclare le nombre de nœuds produit : le récepteur exige le même
nombre. Ce contrôle détecte un écart de transport ; il n'authentifie pas les
octets, les API ou l'exécution. Une API obligatoire absente donne `api-error`
et une couverture incomplète. `null` n'est jamais remplacé par une déduction.
Une structure manquante, mal formée ou incohérente est refusée par le validateur.

Les recettes [v2](../tests/fixtures/rendered-metadata-browser-v2.json) couvrent
24 pages synthétiques : 22 des 24 cas de conception, plus deux cas de réécriture
et de correction de canonique. Les deux cas de conception restants (chemin
invalide et changement de script) sont testés hors navigateur. Les recettes ne
sont pas des observations ni des verdicts. Leur v1 reste intacte. La v2 réduit
la borne de 2 048 à 1 024 après une réception limitée à 2 000 nœuds ; elle exige
le compteur et le signalement des API absentes. Aucun attendu de contenu n'a
été modifié pour faire réussir une capture. Les captures v1 restent attachées
à leurs outils d'origine ; aucune conversion automatique en v2.

### Usage et conservation

```sh
python3 examples/rendered_metadata_lab.py serve --output /tmp/nouvelle-campagne
python3 experiments/rendered_metadata.py capture.json --output inventaire.json
python3 examples/rendered_metadata_lab.py finish /tmp/nouvelle-campagne --observations observations.json --output /tmp/livraison
python3 examples/rendered_metadata_lab.py replay /tmp/livraison
```

Le serveur est exclusivement loopback. Il fige 24 pages, deux ressources de
frame, les attentes et les empreintes des outils avant les lectures navigateur.
Les observations sont fournies séparément par un opérateur autorisé. L'outil
Python ne pilote aucun navigateur. Pour chaque tâche : début de navigation,
lecture unique du script enregistré, date de réception, contexte, URL, état,
identité déclarée du navigateur, erreurs et journaux. Les captures d'écran sont
des pièces complémentaires conservées séparément ; le rejeu ne les analyse pas.

`finish` exige 24 lectures dans chaque environnement, les réponses HTTP brutes
et JSON concordantes, la chronologie déclarée et les requêtes de page/frame
correspondantes. Les UA et horodatages ne sont pas authentifiés. Les empreintes
ne résistent pas à un auteur qui réécrit toutes les pièces. Une capture partielle
reste partielle ; elle ne prouve aucune absence de métadonnée. Les erreurs de
page restent visibles indépendamment des concordances aux recettes. Le rejeu
vérifie les pièces et recalcule l'inventaire sans réseau ni exécution navigateur.
Il ne reproduit pas l'état du moteur et ne constitue pas une seconde mesure.

### État observé le 10 octobre 2026

Deux tentatives locales ont été conservées. La première n'a pas restitué d'arbre
avec la forme d'invocation initiale. La seconde conserve 24 lectures du navigateur
intégré, mais les objets reçus omettent `document.baseURI` et le namespace/nom
local des attributs. Le cas volumineux ne contient que 2 000 nœuds malgré la borne
2 048. Les 24 objets sont refusés par le contrat ; ils ne valident pas les
recettes. La cause exacte de ces omissions n'est pas établie.

L'ouverture de Chrome a dépassé le délai ; l'inventaire des surfaces a ensuite
signalé le Mac verrouillé. Aucune observation Chrome n'est revendiquée pour
cette campagne. La v2 et sa campagne complète restent à éprouver dans les deux
navigateurs. Aucune nouvelle revue de Claude n'est revendiquée à ce stade.
Les tests Python utilisent des arbres rédigés et des clients HTTP de test :
ce ne sont pas des résultats navigateur. Les anciennes preuves draft.7 restent
inchangées. Les preuves locales de ces tentatives sont privées et non incluses
dans l'archive publique des outils.

## English

Version 2 is an observation-only structured traversal and offline inventory for
robots/googlebot, canonical and base declarations. It preserves ordered DOM
attributes, topology, namespace, actual position and distinct raw/resolved URLs.
No filtering by vendor/ID and no normative evaluation. Open shadow trees have
distinct paths; closed roots are unknown. Frame documents and template fragments
are excluded; noscript text is never reparsed. The serialization is a companion,
not a source from which to reconstruct the tree.

Limits: 1,024 nodes, depth 64, 524,288 UTF-8 JSON tree bytes, 262,144 serialization
bytes, 2,000 ms cooperative budget, planned 5,000 ms invocation timeout. A blocked
getter cannot be interrupted by the cooperative budget. A declared node count
must match the returned array; this is not full transport authentication. Missing
required APIs produce an incomplete `api-error` record, never inferred values.
Malformed topology is rejected. The Python validator does not run the JavaScript.

The frozen v2 browser recipes keep v1 intact and preserve all content expectations.
The node budget changed after a 2,048-node invocation returned only 2,000 records;
explicit count and API-availability checks were added. Old captures require their
old tools; there is no silent migration. Of 24 design cases, 22 are browser recipes
and two are offline integrity tests; two additional canonical bridge recipes make
24 browser pages. These are synthetic fixtures, not observed results.

The loopback lab freezes source responses and tool fingerprints before collection.
An authorized operator separately supplies one fixed-script observation per task
and environment. Python never controls a browser. Finishing requires 48 records,
matching HTTP sidecars/JSON, declared chronology and page/frame requests. Screenshots
are separate companion evidence and not analyzed by replay. Declared UA, time,
execution context, DOM APIs and node origin are unauthenticated. Hashes provide
internal consistency, not resistance to an author rewriting every artifact.
Partial readings cannot establish absence. Page errors remain visible independently
of recipe concordance. Offline replay recalculates inventories; it does not execute
a browser or constitute an independent second observation.

Observed 2026-10-10: attempt one returned no tree using the initial invocation
form. Attempt two retained 24 integrated-browser objects, all rejected because
baseURI and attribute namespace/local-name fields were missing. Its large-tree
case returned 2,000 records. The precise cause remains unknown. Chrome creation
timed out and the next surface inventory reported a locked Mac. No Chrome
observation, complete v2 browser campaign or new Claude review is claimed. Python
tests use authored snapshots and test HTTP clients, never represented as browsers.
Private attempt evidence is retained locally, outside the public tool archive.
The normative protocol remains draft.7 and earlier reports remain unchanged.
