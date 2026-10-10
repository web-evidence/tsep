# Attributs de canonical — couverture d’outil / Canonical attribute coverage

## Français

Interpréteur **11**, adaptateur **12**, lecteur DOM structuré **2**, laboratoire
**2** ; protocole **0.1.0-draft.11 inchangé**. Cette évolution applique les règles
existantes avec une classification commune des attributs. Elle n'ajoute pas de
contrôle, ne modifie pas la préférence déclarée et ne rend pas le protocole stable.

Le lecteur source TS10 et le lecteur DOM structuré emploient
`conformance/canonical_attributes.py`, version 1 : `rel` et `href` portent la
déclaration ; `id`, `class` et les noms satisfaisant
`(?:data|aria)-[a-z][a-z0-9_.-]*` sont conservés mais ne modifient pas son extraction.
C’est un choix borné d’interprétation fondé sur leur rôle HTML, pas une garantie
que Google ou un script ne les utilise jamais. Les exigences de rendu restent
présentes. Les noms du DOM doivent être sans namespace ; les attributs source
sont normalisés par le parseur HTML. Les doublons restent refusés.

Les attributs `lang`, `hreflang`, `media`, `type` restent indéterminés sur cette
surface : Google documente un traitement différent de ces annotations. Aucun
signal simple ne leur est substitué. Tous les autres attributs, dont `itemprop`,
les gestionnaires d’événement et les namespaces, restent hors couverture. Un
modificateur n'efface pas une contradiction établie sur une autre surface. Les
refus source gardent leur motif historique ; les refus structurés distinguent
modificateurs documentés et attributs inconnus. Il ne s'agit pas d'un validateur
général HTML/ARIA ni d'une preuve du comportement d’un moteur.

Le lecteur source reconnaît les tokens rel séparés par les seuls espaces HTML
ASCII ; une espace insécable ne découpe pas deux tokens. Le lecteur DOM sérialisé
historique reste fixe et ne reçoit pas cette extension. Les autres limites source
(éléments, structure complète, absence de réparation) sont conservées.

### Vérification et migration

Les 30 cas synthétiques de `canonical-attributes-v1-cases.json` ont été rédigés et
empreintés avant la modification des lecteurs. Ils gardent les issues observées
avec l'interpréteur 10. Sur ces nouveaux cas, 15 issues changent : 5 lectures source
avec attributs ordinaires deviennent compatibles, 1 contradiction source devient
lisible, 9 anciennes lectures DOM trop permissives deviennent indéterminées. Ce
sont des cas rédigés, pas des visites navigateur. Les 353 cas antérieurs restent
inchangés. Les tests supplémentaires couvrent le lecteur historique, les doublons,
HTML non pris en charge et les espaces de rel.

Conserver les paquets et outils d'origine. Une réévaluation avec l’adaptateur 12
crée un nouveau paquet, même si les octets d’entrée sont inchangés ; ce n’est pas
une nouvelle collecte. Une ancienne issue pass du lecteur structuré 1 portant
un modificateur ne prouve plus que la surface est entièrement interprétée par la
version 2. Ne pas rejouer un ancien paquet avec les nouveaux outils en prétendant
avoir reproduit son ancienne décision. Aucun résultat ou tag n’est remplacé.

### Démonstration de correction

Le laboratoire 2 conserve les six cas initiaux et ajoute le plan figé
`repair-navigation-lab-v1.json`. `serve --recipe repair` prépare trois ressources,
chacune avec trois phases **sur la même URL** : témoin, défaut injecté, correction
simulée. Les neuf réponses et mutations sont prévues avant les visites. Un reçu
est exigé avant la phase suivante, et l’analyse vérifie l’ordre des observations.
Ces transitions programmées ne sont pas des corrections d’Edikka.

```sh
python3 examples/same_navigation_lab.py serve --recipe repair --output /tmp/tsep-repair-source
```

La calibration, le scellement, les reçus, la fermeture et le rejeu suivent le
[guide du laboratoire](same-navigation-laboratory.md). Recharger l'URL pour les
phases successives d'une même ressource. Les rapports ne valident que les tests
sélectionnés ; la conformité entière, les revues humaines et la couverture réelle
restent distinctes.

## English

Interpreter 11, adapter 12, structured reader 2 and laboratory 2 retain protocol
draft.11. The shared attribute classifier extends source coverage and corrects
permissive structured readings without changing the declared preference or adding
a control. rel/href carry the declaration; id/class and the documented bounded
ASCII data-/aria- names remain in evidence but do not alter extraction. This is an
implementation inference from their HTML roles, not guaranteed engine behavior
or absence of script effects. Rendering requirements remain necessary.

lang/hreflang/media/type remain inconclusive under the documented Google-policy
boundary. Other unknown or namespaced attributes, itemprop and event handlers are
also unsupported. Duplicate attributes remain refused. Source rel tokens use
HTML ASCII whitespace. The historical serialized DOM reader stays fixed. Other
source structure/element limits remain unchanged. An unknown surface cannot erase
an attributable contradiction on another surface.

Thirty authored cases were frozen before implementation with their previous
interpreter-10 outcomes. Fifteen newly covered/corrected outcomes are explicit;
all 353 prior cases remain unchanged. Reassessment with new tools creates a fresh
bundle, never a replacement report or a new observation. Old replay needs its
exact original tools. Structured-reader-1 success on a modifier is not evidence
of complete interpretation under version 2.

Laboratory 2 adds an explicitly preplanned repair recipe: baseline, injected fault
and simulated repair for three resources, each retaining its URL across phases.
A receipt is required before the next visit, and phase chronology is checked.
These are programmed synthetic transitions, not fixes to Edikka. Execute and replay
as described in the laboratory guide. Atomic compatibility does not complete a
control or replace human review.

## Sources et portée / Sources and scope

Consultées le 10 octobre 2026. Captures textuelles datées et empreintes conservées
par le contributeur dans le dossier local de cette étape ; elles ne sont pas des
captures HTTP brutes. Ces références justifient la distinction des attributs ;
la liste exacte prise en charge et les issues TSEP restent un choix d’outil.

- [Google — annotations canonical](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls) : portée des quatre modificateurs, sans inférence d’ingestion d’une page donnée.
- [HTML — attributs globaux](https://html.spec.whatwg.org/multipage/dom.html) : identifiants, classes, données de page et annotations d’accessibilité. Le rôle HTML de ces attributs ne démontre pas leur effet sur un moteur.
