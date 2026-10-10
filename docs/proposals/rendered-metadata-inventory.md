# Rendered metadata inventory / Inventaire des métadonnées rendues

**Unapplied experiment plan 2, 2026-10-10. No implementation or new TSEP rule.**
**Plan expérimental 2 non appliqué. Aucun nouveau verdict ni version normative.**
The active protocol remains `0.1.0-draft.7`. This plan concerns observations only.

Implementation follow-up (2026-10-10): an [experimental inventory](../rendered-metadata-inventory.md)
now exists separately. The plan below is retained as written. A distinct page
instrumentation method has 48 recorded observations across two browsers; the
linked implementation document states partial coverage and API limitations.
/ Un inventaire séparé est implémenté. Le plan ci-dessous reste conservé. Une
méthode instrumentée distincte conserve 48 observations dans deux navigateurs ;
ses couvertures partielles et limites d'API sont détaillées dans le document lié.

## Français

### Pourquoi cette étape

Deux campagnes complètes du laboratoire TS10 ont conservé chacune 35 lectures
réelles du DOM et 86 requêtes au serveur loopback. Le navigateur intégré ajoutait
un enfant sous `html` ; Chrome présentait aussi des éléments personnalisés dans
`body`. Les deux campagnes obtiennent la même matrice atomique : 8 NC, 4 NT,
aucun C, et `all_expectations_matched=false`. Aucun nœud n'a été retiré, aucune
attente changée. Les refus effectifs du parseur diffèrent : `Unsupported HTML
root child` et `Unsupported HTML element/context`. Le défaut JS est visible dans
les captures mais TS10-A01 reste inconclusive ; la correction DOM n'est pas
validée. Les défauts HTTP, sitemap et liens source déjà établis restent valables.

Le relevé `document.documentElement.outerHTML` est conservé intégralement, mais
ce n'est pas une capture exhaustive de tous les arbres associés au document.
Les résultats ne prouvent ni absence de shadow root fermé ni absence de trafic
réseau des extensions. Le journal ne compte que le serveur loopback. Des IDs
différents selon le navigateur n'authentifient pas l'origine des nœuds.

### Prochain livrable concret

Construire un **inventaire expérimental sans verdict**, limité aux métadonnées
`meta[name=robots]`, `meta[name=googlebot]`, `link[rel~=canonical]` et aux `base`
nécessaires à leur lecture. Ne pas élargir à TS01, au texte visible ou aux liens
internes. Aucune entrée de cet inventaire ne peut alimenter silencieusement
l'évaluateur draft.7 ni être appelée pass, fail, C, NC ou NT.

Le script de lecture sera versionné et figé avant de nouvelles navigations. Il
relèvera en une invocation synchrone l'arbre DOM accessible, sans modification,
sans reparsing HTML et sans téléchargement. Il conservera les sérialisations
comme pièces complémentaires. Les bornes de nœuds, profondeur, octets et temps
seront déclarées avant collecte ; une borne atteinte donnera une couverture
incomplète, sans résultat favorable déduit du préfixe capturé.

Pour chaque nœud pertinent et son chemin : type, espace de noms, nom local,
parents et ordre, attributs dans leur ordre avec valeurs exactes, URL résolue
séparément étiquetée, `document.URL` et `document.baseURI`, emplacement réel
(enfant direct de head, descendant de head, body, hors head/body, shadow ouvert).
Les attributs DOM sont les valeurs de l'arbre, **pas les octets des attributs
source**. Une URL résolue ne remplace jamais un attribut relatif pour le critère
TSEP d'URL absolue. Aucun filtrage par ID, marque d'extension ou auteur présumé.

Conserver les doublons et contradictions. Un élément personnalisé n'est pas
écarté : inspecter les descendants accessibles sans attribuer une fonction SEO
à son nom. Un élément SVG nommé `link` n'est pas assimilé à un `link` HTML.
Une canonique sous un conteneur auxiliaire reste relevée à son emplacement ;
le conteneur n'est pas une exemption. Ne pas chercher un navigateur donnant
un résultat favorable ni retirer ses extensions pour réparer les preuves.

### Frontières de couverture

- Shadow ouvert : arbre distinct, chemin passant par son hôte, jamais aplati
  dans head/body. Shadow fermé : couverture inconnue ; `shadowRoot === null`
  ne prouve pas son absence. Ne pas annoncer avoir détecté tous les fermés.
- Iframe : document distinct, jamais mélangé au parent. Première étape : relever
  l'élément et déclarer son document non capturé, y compris même origine et
  `srcdoc`. Aucun accès supplémentaire ni navigation de frame par l'outil.
- Template : fragment inerte distinct, couverture explicitement exclue dans
  cette première étape ; ne pas convertir son texte ou ses attributs en signaux.
- Noscript : relever le type de nœud réellement obtenu et le mode de scripting
  déclaré. Ne pas traiter une chaîne ressemblant à une balise comme un élément.
- L'origine page/extension est inconnue. Un changement entre deux campagnes
  peut justifier une investigation, pas une attribution causale ni un filtre.
- Source HTTP et état rendu restent deux pièces distinctes. L'inventaire ne
  supprime jamais un noindex source ni une contradiction précédemment établie.
- Selon le contexte d'exécution, les API consultées peuvent être redéfinies
  par la page. Consigner ce contexte comme connu ou inconnu et éprouver ce cas.
  L'empreinte du script ne garantit pas l'intégrité des API ou l'authenticité
  de l'arbre. Un contrôle par `Function.prototype.toString` n'est pas une
  garantie. Aucune autre voie d'automatisation n'est autorisée par ce plan.

### Cas à figer et critères de livraison

Le plan bilingue [JSON v2](../../tests/fixtures/rendered-metadata-plan-v2.json)
énumère 24 cas adverses et leur observation attendue. La v1 de 23 cas reste
intacte ; la v2 ajoute la redéfinition d'API signalée en revue. Son empreinte est dans
le fichier `.sha256` adjacent. **Ce sont des attentes de conception, pas des
tests exécutés, des résultats navigateur ou un nouveau corpus normatif.**

Ordre de réalisation : (1) contrat d'inventaire et bornes ; (2) script immuable
et tests des cas adverses ; (3) nouvelles captures dans les deux environnements
avec la même méthode, toutes conservées ; (4) rejeu de l'inventaire et comparaison
explicite source/DOM/environnements ; (5) revue des écarts. Les anciennes captures
ne sont pas transformées en arbres structurés ni relabellisées comme complètes.

Après seulement, décider si une évolution normative est justifiée. Elle exige
une version distincte, source FR/EN, contrats, migration, cas contradictoires et
nouvelles évaluations. Ne pas réécrire les rapports draft.7 ou les anciennes
archives. Une nouvelle capture reste une observation d'un site synthétique,
sans moteur authentifié, revue humaine de contenu, indexation ou classement.

## English

Two complete synthetic TS10 campaigns, integrated browser and Chrome, each retain
35 browser observations and 86 loopback requests. Auxiliary root children and
custom elements exceed the active lexical reader's subset. Both retain eight NC,
four NT and `all_expectations_matched=false`; no cleanup or changed expectations.
The JS rewrite is visible but A01 remains inconclusive. The server log does not
measure extension traffic, and outerHTML does not establish exhaustive tree coverage.

Next implement an **observation-only** rendered metadata inventory for robots,
googlebot, canonical and base elements. No TS01, visible text, anchor assessment
or draft.7 verdict integration. Freeze the read-only synchronous traversal script
and node/depth/byte/time limits before collection. Retain original serialization,
node type, namespace, local name, ordered exact DOM attributes, parent/path/order,
raw and separately labelled resolved URLs, document URL/baseURI and actual position.
DOM attribute values are not original source bytes. Never turn a relative raw href
into an absolute declaration by substituting its resolved property.

No ID/vendor/origin allowlist. Traverse accessible custom-element descendants;
retain duplicates, foreign namespaces and declarations outside head. Open shadow
trees have separate paths. Null shadowRoot cannot establish no closed tree.
Frame documents, including same-origin and srcdoc, are not captured in step one;
record their elements and that boundary without flattening. Template fragments
are explicitly excluded, and noscript text is never reparsed into metadata.
Page versus extension origin remains unknown; differences suggest investigation,
not attribution. Preserve HTTP-source contradictions independently of the DOM.

Depending on execution context, page code may override DOM APIs used by the
reader. Record that context as known or unknown and test this threat. A script
fingerprint or native-code-looking toString result is not API integrity or tree
authentication. This plan authorizes no alternative automation channel.

The linked frozen bilingual v2 plan contains 24 **unexecuted design expectations**;
v1's 23 cases remain unchanged, and v2 adds the API-override scenario. These are
not browser results or normative cases. Implement bounded capture and adversarial
tests, then collect fresh campaigns in both environments with the same fixed
method, replay the inventory and review differences. Never reconstruct structured
trees from old serializations or claim those trees were observed. Any subsequent
normative promotion requires a distinct version, bilingual contracts, migration,
contradictory cases and new reports. Draft.7 and old evidence stay unchanged.

## References / Références

Consulted 2026-10-10: [WHATWG HTML parsing and serialization](https://html.spec.whatwg.org/multipage/parsing.html#serialising-html-fragments)
and [DOM shadowRoot getter](https://dom.spec.whatwg.org/#dom-element-shadowroot).
Scope: tree/serialization distinction and the getter's null result for absent
or closed roots. These sources do not prescribe this TSEP experiment. Dated
reference notes and reason for no full-page capture are retained in the local
Chrome campaign evidence. Claude's review was of the supplied account only;
no independent execution or human review is claimed.
