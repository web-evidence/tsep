# Link elements / Éléments de liens — observation 1

## Français

Complément expérimental de l'inventaire [liens source](source-links-experiment.md),
sans changement normatif de draft.16. L'objectif est de distinguer les types
d'éléments avant de choisir lesquels une future règle A04 pourra évaluer. Un
élément présent n'est pas une navigation effectuée ou une ressource explorée.

Le lecteur conserve a, area, link, base et form dans chaque namespace ; il ajoute
les input/button HTML avec formaction et les conteneurs template. Chaque élément
garde les attributs avec namespace et préfixe, ancêtres, contexte, ordre dans
l'arbre, chemin de templates, balise brute et positions dans les octets reçus.
href et xlink:href ne s'écrasent pas. Une absence de href reste distincte d'une
valeur vide. Les jetons rel sont délimités par les espaces ASCII et leur casse
ASCII est abaissée ; ordre et doublons sont conservés. Aucune suppression selon
nofollow, download, target, ping ou une origine supposée du nœud.

La classification nomme la structure : html-a, html-area, svg-a, html-link,
html-base, html-form, html-form-override ou foreign-*. Elle ne choisit pas de
destination, n'applique pas les formulaires, événements, animations SVG, CSP,
shadow ou frames et ne garantit pas l'activation d'une zone area. Des mécanismes
de navigation comme onclick ne sont pas un inventaire complet dans ce profil.
Les erreurs signalées et les pièces originales restent disponibles.

Les fragments de template sont parcourus et marqués comme tels, sans devenir des
liens actifs du document. Les hypothèses de scripts activés/désactivés restent
séparées. Le namespace d'un élément et ceux de ses ancêtres restent tous visibles,
y compris les points d'intégration HTML sous SVG/MathML.

La qualification utilise 31 documents synthétiques écrits avant implémentation,
avec 62 projections attendues. Elle compare aussi les ancres HTML et bases,
actives ou en template, aux inventaires source/head existants. Les outils anciens
ne sont pas modifiés. La fixture d'observation Unicode est une sortie conservée
pour les tests d'attribution, pas un oracle indépendant. Les [références datées](../provenance/link-elements-v1.json)
portent sur la structure HTML/SVG, jamais sur une observation Google.

Le profil d'entrée reste le HTML UTF-8 explicite de source-http : 8 Mio maximum,
BOM initial consommé, octets invalides refusés. Node24 et parse5 8.0.1 sont
séparément identifiés. Processus : 30 secondes, ancien tas 128 Mio, 200 000 nœuds,
profondeur 256, 50 000 records, 1 000 erreurs ; sortie formatée 32 Mio maximum.
Un inventaire interrompu ne conserve pas de liste partielle permettant d'inférer
une absence. Le garde API réseau n'est pas une isolation système.

```sh
python3 scripts/link_elements_check.py --node /path/to/node24 --output-dir new-qualification
```

L'intégration A04 devra encore fixer le périmètre des types de liens et les
inconnues, le choix préalable du lecteur, l'URL finale, la base et le rendu,
la comparaison des URL de famille déjà sérialisées, les exceptions documentées,
les contradictions indépendantes et la migration. Cet observateur ne donne
aucun pass/fail de règle, aucune conformité globale ni validité HTML complète.

## English

This supplemental observer prepares A04 element coverage without changing
draft.16 or existing source/head readers. It retains a/area/link/base/form in
all namespaces, HTML input/button formaction and template containers, with
namespaced attributes, ancestors, tree order, template paths and original bytes.
Plain href and xlink:href remain distinct; missing and empty values differ.
ASCII rel token folding retains order/duplicates. No nofollow/download/target
annotation removes an element from the evidence.

The labels identify structures, not activated links. Templates remain marked,
foreign ancestry is retained and both static scripting alternatives are separate.
No form submission, SVG animation, event, CSP, shadow attachment, frame visit or
complete interaction inventory is inferred. Parse errors and original bodies
remain review inputs; classification is not HTML validity or a TSEP decision.

Thirty-one prior-authored documents specify 62 expected projections. Existing
HTML anchor/base observations, including inert templates, are compared unchanged.
A separate retained Unicode output supports transport guards, not an independent
oracle. Bounded explicit UTF-8 input, pinned parser, Node24, 30-second deadline,
128 MiB old space, 200,000 nodes, depth256, 50,000 records, 1,000 parse errors and
32 MiB formatted output apply. Incomplete inventories expose no partial lists.
Network API guards are not OS isolation; integrity is not authentication.

Future A04 policy still needs explicit element scope, prior reader selection,
base/rendered evidence, family serialization, unknowns and independent failures,
exceptions, bilingual normative versioning and migration before any promotion.
