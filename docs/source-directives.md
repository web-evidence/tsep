# Source directives / Directives source — html-tree-directives-v1

## Français

Ce profil facultatif de draft.15 étend TS07-A01 et le préalable source de TS07-A03.
Il ne change ni le lecteur DOM choisi, ni l’accès A02, ni les revues nécessaires.
Déclarer `intent.source_reader = "html-tree-directives-v1"` avant la capture,
avec le robot sémantique, le client HTTP, l’objectif et le contexte habituels.
Sans ce champ, conserver le lecteur historique. Champ nul/inconnu ou lecteur
indisponible : inconclusive, sans repli, jamais NA. Les 44 contrôles restent candidats.

### Entrées et procédure

Conserver la trace complète de GET, ses octets et dates, l’intention préalable,
les en-têtes finaux, le corps après décodage HTTP et le contexte. Les conditions
HTTP existantes restent obligatoires. Lire uniquement `text/html` avec une seule
valeur Content-Type, dont l’unique paramètre est `charset=utf-8` (casse ASCII,
espaces et valeur UTF-8 entre guillemets admis). Autres encodages, alias, paramètres
ou répétitions : inconclusive. Consommer exactement un BOM UTF-8 initial ; ne pas
remplacer les octets invalides, normaliser les retours de ligne ou inférer l’encodage.
Les déclarations d’encodage internes sont conservées, sans remplacer celui du HTTP.

Le lecteur épinglé parse5 8.0.1 / entities 8.0.0 construit deux arbres du document
complet, hypothèses de scripts activés et désactivés. Il n’exécute aucun script.
Leurs directives ne sont **jamais fusionnées** : ce sont des interprétations
alternatives, pas deux états rendus observés simultanément.

Pour chaque lecture complète :

1. Une erreur **signalée** par le parseur rend cette lecture indéterminée. Certaines
   réparations ne sont pas signalées ; leur arbre construit reste utilisé. Ce
   critère n’établit donc ni validité HTML ni absence de réparation.
2. Tout template HTML déclarant shadowrootmode open/closed, même vide, ou un
   attribut `for`, rend la lecture indéterminée. Aucune attache shadow n’est inférée.
   Le contenu des templates ordinaires reste conservé et exclu des directives actives.
3. Retenir les meta HTML name robots/googlebot (casse ASCII indifférente), dans
   head ou body, sans ancêtre de namespace étranger. Content absent, contexte
   étranger ou rôle mixte (`http-equiv`, `charset`, `itemprop`) : inconclusive.
4. Refuser les formes approchantes suivantes, sans leur inventer un effet :
   http-equiv robots/googlebot/x-robots-tag après suppression des espaces de bord,
   name x-robots-tag, name robots/googlebot entouré d’espaces. Les autres noms de
   metadata/robots restent visibles, hors de l’objectif Googlebot textuel déclaré.
5. Combiner ces valeurs avec les X-Robots-Tag finaux selon le vocabulaire historique :
   index/noindex, follow/nofollow, all/none, nosnippet et les syntaxes max-preview
   déjà prises en charge. L’objectif de présentation reste hors couverture. Les
   directives inconnues, dont indexifembedded, rendent la lecture indéterminée,
   même en présence de noindex. Aucun en-tête seul ne remplace un HTML illisible.

Deux pass donnent pass ; deux fail donnent fail ; toute autre combinaison donne
inconclusive. Un désaccord d’inventaires reste visible, même si les deux décisions
concordent parce que la différence est hors de l’objectif (par exemple nofollow
avec following unspecified). Une contradiction appartenant à une seule hypothèse
ne devient pas un échec établi dans toutes les interprétations. Cette règle ne
remplace pas la priorité d’une contradiction dans un **état réellement fourni** A03.

### Preuves, environnement et limites

Les artefacts `observations/source-observation-N.json`, liés au rapport, conservent
les deux listes complètes de meta (y compris templates), leurs attributs, namespaces,
ancêtres, tags bruts et intervalles d’octets dans le corps original ; templates,
mode de document, erreurs signalées, décodage, empreintes des outils et versions
Node/V8/Python suivent aussi. Il s’agit d’un calcul daté à l’import, pas d’une
capture de moteur. L’adaptateur compare les sources avant/après. Le rejeu compare
également ces observations ; changer de runtime peut empêcher une identité exacte.
Les empreintes assurent une intégrité vérifiable, pas l’authenticité du déclarant.

Node 24 est facultatif pour le cœur Python, mais nécessaire à ce profil. Le chemin
peut être fourni par `TSEP_SOURCE_NODE`, sinon `node` est recherché sur PATH. Aucun
 téléchargement, npm, repli ou installation automatique. Corps maximal 8 Mio,
200 000 nœuds, profondeur 256, 50 000 enregistrements, 1 000 erreurs par lecture,
30 secondes par processus, old-space V8 128 Mio (pas une borne RSS), sortie
32 Mio et diagnostic retenu 4 Mio par évaluation. Dépassement : inconclusive sans
tronquer une liste pour conclure par absence. Le garde réseau limite des API Node
publiques ; ce n’est pas une isolation réseau du système d’exploitation.

Une réussite A01 ne prouve ni TS07 entier, ni indexation, classement, accès ou
rendu Google. Les scripts, interactions, autres moteurs, shadow et syntaxes non
couvertes nécessitent d’autres preuves. Ne pas déduire une exemption de rendu.
Les pages réelles testées doivent conserver leur taux d’indétermination et les motifs.

### Qualification et correction d’attentes

Le premier oracle indépendant `source-directives-v1.json` a obtenu 30/32 accords.
Deux attentes supposaient à tort une erreur signalée : sortie du SVG lors d’un meta,
et fermeture div surnuméraire. La v2 conserve la politique et corrige ces deux
attentes à partir de l’arbre effectivement construit ; v1, son empreinte et l’échec
restent conservés. Cinq cas distincts vérifient ensuite le préalable source A03,
les états manquants, l’échec rendu prioritaire et l’absence d’extension du DOM
sérialisé. Les 37 cas sont synthétiques ; la qualification Node est une commande
séparée, et le vérificateur Python peut annoncer une couverture réduite si Node
24 manque. Ne pas présenter une réduction de couverture comme 37 accords observés.

```sh
python3 scripts/source_directives_check.py --node /path/to/node24 --output qualification.json
TSEP_SOURCE_NODE=/path/to/node24 python3 adapters/captures.py --help
TSEP_SOURCE_NODE=/path/to/node24 python3 adapters/replay.py bundle --output new-replay
```

Sources primaires observées le 10 octobre 2026 :
[Google — meta robots](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag)
pour head/body, portée des noms et combinaison ;
[WHATWG — construction d’arbre](https://html.spec.whatwg.org/multipage/parsing.html)
pour contextes HTML et contenu étranger. Captures, empreintes et limites sont
référencées dans `provenance/source-directives-v1.json`. La décision d’unanimité
est une politique explicite TSEP ; aucune source ne l’attribue à Google.

## English

Draft.15's optional prior `intent.source_reader="html-tree-directives-v1"` extends
TS07-A01 and A03's source prerequisite only. Absent field preserves legacy behavior;
null/unknown/unavailable profiles stay inconclusive without fallback or NA.
Existing HTTP attribution, prior intent, exact client, directive crawler and
indexing/following objectives remain mandatory. Access, DOM readers and required
human/rendering reviews are unchanged.

Use a complete retained GET trace, final headers and decompressed body. Accept one
Content-Type text/html whose only parameter is charset=utf-8, ASCII case-insensitive,
with whitespace/quoted UTF-8 allowed. Other parameters, aliases, encodings or repeats
are unsupported. Consume one initial UTF-8 BOM; no invalid-byte replacement, newline
normalization or encoding sniffing. Retain internal encoding declarations without
overriding the certain HTTP encoding.

Pinned parse5 8.0.1 / entities 8.0.0 constructs the whole document with scripting
enabled and disabled, without executing scripts. Assess the two **alternative**
hypotheses separately, never merge their directives. For each complete reading:

1. Any **reported** parse error means inconclusive. Some repairs are not reported;
   their constructed trees remain usable. This is not an HTML validity check.
2. Any HTML template declaring open/closed shadowrootmode, including empty ones,
   or a `for` attribute is unsupported. Never infer attachment. Ordinary template
   contents remain retained and excluded from active directives.
3. Read HTML meta name robots/googlebot, ASCII case-insensitively, in head/body
   with no foreign-namespace ancestors. Missing content, foreign context or mixed
   roles (http-equiv/charset/itemprop) are inconclusive.
4. Treat these near forms as unsupported, not invented restrictions: trimmed
   http-equiv robots/googlebot/x-robots-tag, name x-robots-tag, padded name
   robots/googlebot. Other metadata/crawler names remain recorded outside the
   declared Googlebot text-results objective.
5. Combine active values with final X-Robots-Tag using the unchanged bounded
   vocabulary: index/noindex, follow/nofollow, all/none, nosnippet and existing
   max-preview forms. No presentation objective is assessed. Unknown directives,
   including indexifembedded even alongside noindex, are inconclusive. Unreadable
   HTML cannot yield a header-only pass.

Two pass yield pass, two fail yield fail, every other pair yields inconclusive.
Retain inventory differences even if irrelevant to the objective and both outcomes
agree. Failure in one alternative is not an established failure in all alternatives.
A03's priority for contradictions in supplied rendered states remains unchanged.

Report-linked observations/source-observation-N.json retains both complete meta
inventories, attributes, namespace ancestry, original tags/body-byte spans,
templates, document mode, reported errors, decoding, source fingerprints and
Node/V8/Python versions. Calculation time is import time, not capture time. Sources
are checked before/after. Replay also compares these diagnostics; runtime changes
can prevent exact identity. Integrity is not evidence-provider authentication.

Optional Node 24, via TSEP_SOURCE_NODE or node on PATH, is required for this profile,
not the Python core. No automatic installation/download/fallback. Bounds: 8 MiB
body, 200,000 nodes, depth 256, 50,000 records, 1,000 reported errors per reading,
30-second process deadline, 128 MiB V8 old-space (not RSS), 32 MiB parser output,
4 MiB retained diagnostics per assessment. Exceeding a bound is inconclusive;
never truncate a list to claim absence. The Node public-API network guard is not
OS network isolation. A01 success is not whole TS07, actual indexing/ranking,
Google rendering or an exemption from rendering review. Retain real-campaign
inconclusive counts and reasons.

The first independent oracle matched 30/32. v2 corrects two mistaken assumptions
about **reported** errors (foreign-meta breakout and stray div end tag) without
changing the interpreter to obtain agreement. Original v1 and its failure are
retained. Five A03 cases add source, missing-state, rendered-failure priority and
legacy-DOM checks. All 37 cases are synthetic; actual Node qualification is separate
from reduced coverage permitted when Node 24 is unavailable. Commands above replay
the profile. October 10 primary-source captures/fingerprints are recorded in
provenance/source-directives-v1.json. Unanimity is a TSEP policy, not Google behavior.
