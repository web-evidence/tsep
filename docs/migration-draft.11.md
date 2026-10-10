# Migration vers draft.11 / Migration to draft.11

## Français

Conserver les anciens rapports, archives, outils et tags. Une réévaluation crée
un nouveau rapport identifié `0.1.0-draft.11`, sans réécrire une ancienne preuve.
Les 338 cas précédents ne changent pas ; 15 cas figés ajoutent la séparation entre
agent HTTP et sémantique des directives, notamment un désaccord des groupes robots
Chrome et Googlebot. Ils sont rédigés synthétiquement, pas collectés sur Edikka.

L'interpréteur passe à 10, l'adaptateur de captures à 11 et le lecteur partagé
robots à 2. Le format de rapport reste 2. L'inventaire DOM 2 et les règles de
rattachement draft.10 restent applicables. Les champs historiques ne sont pas
renommés : `crawler` est toujours l'agent HTTP exact. Les entrées sans nouveau
champ conservent leurs résultats ; la couverture ne s'étend pas rétroactivement.

Pour une nouvelle collecte TS07 par navigateur, déclarer avant capture
`directive_crawler: "googlebot"` et conserver l'agent réel. Cette politique
s'applique seulement à la représentation cliente. A02 exige en plus un profil
robots explicite et concordant ; aucune substitution par le groupe du navigateur.
Un champ non pris en charge ou une preuve insuffisante donne inconclusive. Ne pas
ajouter une intention a posteriori à une ancienne capture pour obtenir un pass.

Le [laboratoire](same-navigation-laboratory.md) est un moyen de produire six cas
locaux avec source et DOM rattachés à la même navigation. Une exécution effective
exige ses propres pièces ; la présence du code ou la réussite de tests HTTP ne la
prouve pas. Les revues humaines, cas réels Edikka et Search Console restent des
travaux distincts. Cette évolution locale ne constitue aucune publication.

## English

Retain earlier reports, archives, tools and tags. Reassessment creates a fresh
report identified by draft.11. All 338 prior cases remain unchanged; 15 prefrozen
authored cases exercise transport/directive separation and conflicting Chrome/
Googlebot robots groups. Interpreter 10, capture adapter 11, shared robots reader
2; report format remains 2 and inventory 2 stays fixed.

No historical field is renamed: crawler is still the exact HTTP agent. Missing
new field retains old results, without retroactive coverage extension. Before a
new TS07 browser collection, declare directive_crawler=googlebot and keep the real
agent. These semantics concern only this client representation; A02 additionally
requires an explicit matching robots profile. Unsupported values or insufficient
evidence remain inconclusive. Never backdate intent on an earlier capture.

The same-navigation synthetic laboratory needs a separately evidenced actual
browser run; code and HTTP-client unit tests do not demonstrate one. Human reviews,
real Edikka captures and Search Console work remain distinct. This local development
change is not publication or an engine observation.
