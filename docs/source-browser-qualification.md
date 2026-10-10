# Browser/source qualification 1 / Qualification navigateur-source 1

**Synthetic laboratory, no normative effect. / Laboratoire synthétique, sans
effet normatif.** Protocol draft.14 and the optional source-tree experiment 1
remain unchanged. This is not an Edikka assessment or a search-engine visit.

## Français

La comparaison entre deux bibliothèques ne suffisait pas à documenter les écarts
entre chaîne source et document chargé. Ce laboratoire confronte les 36 documents
figés de l’[expérience d’arbre source](source-tree-experiment.md) à des **DOM de
cadres iframe** dans le navigateur disponible. Il ne prétend pas observer une
navigation de premier niveau ou tous les navigateurs.

Le plan [source-browser-v1](../tests/fixtures/source-browser-v1.json), figé avant
mesure, conserve les 36 empreintes source et leurs attendus pour deux configurations :
`sandbox="allow-same-origin"`, puis `sandbox="allow-same-origin allow-scripts"`.
L’accès au DOM par le parent reste possible dans les deux cas. Deux documents de
calibration, distincts des 72 lectures comparées, vérifient une exécution de script
et la présence ou l’absence d’un élément situé dans noscript. Leur mutation de
texte n’entre jamais dans la comparaison au parseur statique.

Les 36 documents restent octet pour octet identiques au corpus précédent. Leurs
scripts ne comportent pas de modification du DOM : chaînes de faux balisage ou
syntaxe de test. Les erreurs d’exécution éventuelles de ces fragments ne sont pas
un verdict de parsing. Les configurations sont relevées pour chaque cadre ;
l’exécution d’un témoin n’est établie que sur les deux documents de calibration,
pas sur un témoin ajouté à chaque source. Ce dernier ajout changerait le corpus.

Le serveur est lié à 127.0.0.1 et emploie une origine localhost unique. Toutes les
réponses HTML ont un UTF-8 explicite, longueur exacte, cache désactivé et CSP fixe.
La CSP autorise les scripts en ligne et empêche les connexions externes et les
sous-cadres des documents testés ; le contrôleur peut charger les cadres prévus
et envoyer leur relevé au serveur local. Ces restrictions font partie du contexte
de l’essai. Elles ne sont pas une reproduction de l’environnement d’un moteur.

Le contrôleur parcourt le DOM après l’événement load, relève les attributs bruts
du DOM, namespaces, contextes head/body/template/shadow, sérialisation, charset et
URL. Il conserve les templates et les **racines shadow ouvertes** séparément.
Il ne fournit pas de positions dans le code source. Les racines fermées ne sont
pas qualifiées par ce corpus ; l’absence de `shadowRoot` lisible ne prouve jamais
l’absence d’une racine fermée. Les 36 sources ne déclarent aucune racine fermée.

### Mesure observée le 10 octobre 2026

La campagne de développement a conservé 76 échanges HTTP entre
18:55:40.483295 et 18:55:42.247011 UTC : contrôleur, 74 cadres et export. Le navigateur
disponible dans Codex déclarait le token User-Agent `Chrome/155.0.0.0` ; ce n’est
pas une attestation indépendante de son identité. Les deux calibrations ont
correspondu aux attentes. Les 72 lectures ont correspondu aux projections prévues.

La comparaison des champs type de signal, contexte, attributs et namespace avec
les sorties statiques précédemment conservées donne **68 accords sur 72**. Les
quatre écarts prévus sont maintenus, pas assimilés à des erreurs à effacer :

| Document synthétique | Inventaire statique 1 | Cadre navigateur observé, dans les deux configurations |
| --- | --- | --- |
| BOM UTF-8 initial | U+FEFF conservé en entrée Unicode, meta placé dans body | BOM consommé au décodage HTTP, meta dans head |
| Template avec shadowrootmode=open | Métadonnée dans le contenu du template | Métadonnée dans une racine shadow ouverte, template consommé |

Ces écarts justifient deux exigences avant une évolution normative : distinguer
les octets HTTP de la chaîne donnée au parseur, puis définir explicitement la
portée des déclarations shadow. Un inventaire égal ne suffit pas à établir une
conséquence SEO. Les politiques robots, canonical et liens restent séparées ;
la règle de concordance entre hypothèses n’est toujours pas appliquée à TSEP.

### Refaire ou rejouer

```sh
python3 examples/source_browser_lab.py serve --output /tmp/tsep-source-browser-new
```

Ouvrir uniquement l’URL du contrôleur affichée par cette commande dans le
navigateur choisi. Un dossier neuf est obligatoire. Attendre le reçu des
74 observations ; conserver l’état affiché. Arrêter ensuite le serveur avec
Ctrl-C pour fermer le journal, puis analyser hors ligne :

```sh
python3 examples/source_browser_lab.py analyze /tmp/tsep-source-browser-new --output /tmp/tsep-source-browser-result.json
```

Le plan, les réponses prévues, les requêtes et réponses brutes, leurs empreintes,
la chronologie, les paramètres des cadres et l’export sont vérifiés. Doublons,
observations manquantes, sessions/conditions HTTP, octets différents et outils
modifiés empêchent la validation du dossier. Les désaccords aux attendus sont
des données conservées ; ils ne sont pas cachés par une nouvelle tentative.

Le rejeu analyse l’export enregistré, il ne rouvre pas le navigateur et ne prouve
pas la véracité des observations. Des captures et scripts d’une exécution ancienne
nécessitent leurs outils exacts. Les tests Python emploient des relevés rédigés
explicitement synthétiques pour éprouver ces refus : **ils ne sont pas des mesures
navigateur supplémentaires**. Aucune CI distante n’est établie par ces tests locaux.

## English

This synthetic laboratory compares the 36 frozen source documents with observed
**iframe DOMs**, under two predeclared sandbox configurations: allow-same-origin
and allow-same-origin plus allow-scripts. It is not a top-level-navigation or
all-browser comparison. Two separate calibration documents check script execution
and noscript element presence; their DOM mutation is outside the 72 corpus readings.
The original document bytes are unchanged. Their test scripts contain inert-markup
strings or syntax tests, not DOM mutations. Calibration does not claim a separate
executed canary in every source document.

The server binds 127.0.0.1 on a unique localhost origin. Prior exact UTF-8 HTTP
responses retain length, cache policy and CSP. Inline scripts are allowed; external
connections and nested frames in test documents are blocked. The controller can
load declared frames and post the collected evidence locally. These restrictions
are part of the laboratory context, never an engine-environment claim.

The controller traverses each loaded document and retains DOM attributes,
namespaces, head/body/template/shadow contexts, serialization, charset and URL.
Templates and open shadow roots are separate. It does not recover source offsets.
Closed shadow roots are outside this corpus: an unreadable shadowRoot never proves
absence of a closed root. No case declares a closed root.

On October 10, 2026, the development campaign retained 76 HTTP exchanges between
18:55:40.483295 and 18:55:42.247011 UTC: controller, 74 frames and export. The Codex
browser reported Chrome/155.0.0.0 in its User-Agent; this is not independently
authenticated identity. Both calibration observations and all 72 authored browser
projections matched the predeclared expectations.

Comparing signal type, context, attributes and namespace to the earlier retained
static-parser results gives **68/72 matching projections**, with four predicted
differences retained: the HTTP UTF-8 decoder consumes a leading BOM, while static
experiment 1 retains U+FEFF as Unicode input; declarative open shadow content moves
from template content into an instantiated shadow root in both browser configurations.
The experiment, protocol and prior reports remain unchanged. Before normative
promotion, decoding and shadow scope need explicit policies; neither matching
inventories nor one browser measurement establishes a Google or TSEP result.

Use the commands above with new paths. Visit only the emitted controller URL,
retain its completion receipt, stop the server with Ctrl-C, then analyze offline.
Analysis verifies prior bytes, raw exchanges, fingerprints, chronology, settings,
export binding and tool continuity. Missing/duplicate observations, session or
conditional requests, changed bytes or changed tools fail attribution checks.
Expected-result disagreements are retained as data. Offline replay checks the
recorded export, without browser execution or observation authentication. Old
campaigns require their exact tools. Python transport tests use explicitly authored
synthetic records and cannot establish additional real browser observations or CI.

## Reference / Référence

[WHATWG sandboxing](https://html.spec.whatwg.org/multipage/browsers.html#sandboxing)
documents the configuration mechanism. Its dated full capture is retained by the
development custodian; URL, scope, date and SHA-256 are in
[provenance](../provenance/source-browser-v1.json). Parsing references and earlier
oracle corrections remain in the source-tree experiment documentation.
