# HTTP-source inventory 1 / Inventaire de source HTTP 1

**Unapplied experiment; no normative effect. / Expérience non appliquée, sans
effet normatif.** Draft.14, source-tree experiment 1 and their retained results
are unchanged. This reader is not imported by the decision pipeline.

## Français

Le [laboratoire navigateur](source-browser-qualification.md) a montré pourquoi
une chaîne Unicode ne suffit pas à représenter le décodage d’une réponse HTTP.
Ce profil facultatif apporte un lien contrôlé entre corps reçu, chaîne analysée
et inventaires. Il prépare TS07/TS10 ; il ne prononce aucun verdict de ces contrôles.

### Entrées et frontières du profil

L’appelant fournit le corps **déjà décompressé** et toutes les valeurs conservées
du champ Content-Type. `html-http-utf8-v1` exige une seule valeur `text/html`,
un unique paramètre `charset=utf-8` et aucun autre paramètre. Casse ASCII,
espaces/tabulations autour des séparateurs et guillemets autour de `utf-8` sont
acceptés. Charset absent, champ répété, paramètre supplémentaire, autre média,
repli de ligne et alias tel que `utf8` sont **hors couverture**, même lorsque le
navigateur pourrait les lire. C’est un profil étroit déclaré, pas un parseur MIME
général. Les limites sont testées et ne deviennent ni défaut SEO ni non-applicabilité.

Le lecteur consomme exactement un BOM UTF-8 initial. Un second U+FEFF, un BOM
après un espace et les fins de ligne restent dans la chaîne donnée au parseur.
Des BOM UTF-16/32 et tout octet UTF-8 invalide sont refusés. Le remplacement des
octets invalides effectué par un navigateur n’est pas reproduit. Le profil
n’effectue aucune détection heuristique du charset ni reprise depuis une meta.
Il conserve séparément empreinte du corps, empreinte UTF-8 de la chaîne analysée,
nombre d’octets consommés et valeurs Content-Type originales.

La déclaration HTTP prise en charge est certaine pour cette lecture. Les meta
charset et http-equiv Content-Type sont inventoriées, même lorsqu’elles déclarent
autre chose, sans changer le décodage. Le lecteur ne démontre pas l’origine HTTP,
la décompression, la complétude ou l’association du corps à son en-tête : ces
preuves appartiennent au dossier de capture.

### Positions, templates et mode du document

Les quatre inventaires robots, canonical, ancres et base restent distincts.
Chaque balise conserve ses attributs interprétés, contexte calculé, ancêtres et
plage dans la chaîne en unités UTF-16. Le superviseur associe cette plage aux
**octets du corps d’origine**, en tenant compte du BOM consommé et des caractères
hors BMP. Il vérifie de nouveau la balise brute ; une coupure dans une paire de
surrogates est refusée. Les erreurs du parseur conservent leurs offsets et, quand
ces positions existent, leur plage d’octets. Les offsets sont à base zéro, borne
finale exclusive. Une position manquante n’est pas inventée.

Tous les templates HTML conservent leurs attributs, parent calculé et chaîne
d’indices des templates englobants. Les signaux de leur contenu pointent vers
ces mêmes indices. `shadowrootmode` est relevé comme absent, invalide, open ou
closed, selon sa valeur interprétée et sans sensibilité à la casse ASCII.
**Reconnaître cette valeur n’affirme pas qu’une racine a été attachée.** Le lecteur
n’évalue ni capacité de l’hôte, ni racine déjà attachée, ni attachement effectif.
Il ne transforme jamais « closed » en absence de contenu. Les attributs dupliqués
restent visibles dans la balise brute et les erreurs, même si l’arbre garde la
première valeur. Les comparaisons de templates et de déclarations d’encodage sont
séparées des quatre inventaires SEO.

Chaque lecture conserve aussi le mode no-quirks, limited-quirks ou quirks fourni
par le parseur. Les cas figés vérifient notamment qu’un second BOM avant le doctype
reste significatif et que la présence d’un paragraphe parmi les ancêtres d’une
table diffère selon le mode. Il s’agit d’une qualification statique, pas d’une
nouvelle observation navigateur de ces cas.

### Exécution et qualification

```sh
python3 experiments/source_http.py body.bin --content-type 'text/html; charset=utf-8' --node node --output inventory.json
python3 scripts/source_http_check.py --node node --output qualification.json
```

Répéter `--content-type` si le champ est répété : le profil le refusera explicitement.
Utiliser des sorties neuves. Python 3.9+ et Node 24 facultatif sont requis pour
l’inventaire ; les paquets parse5 8.0.1 et entities 8.0.0 épinglés sont ceux déjà
livrés. Aucun téléchargement, npm ou script d’installation à l’exécution.

Bornes : corps 8 MiB, processus Node 30 s, ancien espace V8 128 MiB (pas mémoire
totale), 200 000 nœuds, profondeur 256, 50 000 records cumulés par lecture,
1 000 erreurs et JSON compact 32 MiB avant et après attribution. Nœuds et
profondeur sont contrôlés après construction. Un inventaire incomplet ne livre
aucun signal partiel. Le garde d’API réseau et les permissions Node sont ceux de
l’expérience 1 ; ils ne constituent pas une isolation réseau système.

Les 27 cas de décodage et 14 documents de templates ont été figés avant leur
implémentation. Quatre documents de mode ont été ajoutés après le retour de Claude,
avant leur qualification. Les 63 comparaisons explicites correspondent aux
attendus : 27 décodages/refus et 36 lectures statiques de 18 documents. Les tests
Python de refus et d’attribution ne prétendent pas exécuter Node ; sa qualification
reste une commande distincte. Ces corpus finis ne prouvent pas tout HTML.

Migration : conserver les outils et sorties de l’expérience 1. Recalculer dans
un nouveau dossier avec en-têtes et corps liés, sans remplacer les anciennes
empreintes. L’inventaire enrichi ne suffit toujours pas pour promouvoir une règle :
politique par signal, erreurs admises, URL/base, hypothèses alternatives, rendu
attribuable et revues nécessaires restent à définir ou à satisfaire.

## English

This optional profile links supplied decompressed body bytes, declared HTTP
decoding and static signal inventories. It changes no draft.14 outcome and does
not replace source-tree experiment 1. The normative pipeline never imports it.

`html-http-utf8-v1` accepts exactly one Content-Type value: text/html with only
charset=utf-8. ASCII case, surrounding space/tab and quoted UTF-8 are accepted.
Other labels (including the browser-supported utf8 alias), parameters, duplicate
fields, missing charset, folded values or other media remain outside this narrow
profile. They are not SEO faults or positive non-applicability. The caller supplies
all values and proves body/header association, decompression and completeness.

Exactly one leading UTF-8 BOM is consumed. A second U+FEFF, embedded BOM and input
newlines remain. UTF-16/32 BOMs and invalid UTF-8 are refused, without browser-style
replacement or encoding sniffing. Body and parser-input hashes are separate.
Encoding meta declarations are retained without overriding this certain HTTP
decoding. This is not a general browser decoder or MIME parser.

Robots, canonical, anchors and base inventories remain separate. Raw tags and
UTF-16 spans are attributed back to exact original body bytes, including consumed
BOM and non-BMP characters. Surrogate splits are rejected. Parser errors also
receive byte spans where positions exist; absent positions stay absent. All spans
are zero-based with exclusive end. Python rechecks raw tags against original bytes.

Every HTML template retains attributes, calculated parent, nested-template path
and related signals. Shadow mode values are classified absent, invalid, open or
closed using ASCII-insensitive matching. This never asserts root attachment or
host capability, and never treats closed content as absent. Duplicate attributes
remain in raw tags and parser errors. Encoding/template comparisons are separate
from the four signal groups. Each reading retains the parser's document mode.

The commands above need Python 3.9+ and optional Node 24, with shipped pinned
parse5/entities archives. There is no runtime download. Limits are 8 MiB body,
30-second Node deadline, 128 MiB V8 old space (not total memory), 200,000 nodes,
depth 256, 50,000 combined records per reading, 1,000 errors and 32 MiB compact
JSON before/after attribution. Tree bounds apply after parsing. Partial readings
discard all signals. The existing network-API guard is not OS isolation.

The frozen corpus has 27 decoder cases, 14 template documents and four document-mode
cases added after Claude's method feedback, before qualification. All 63 explicit
comparisons matched: 27 decoding/refusal cases and two readings of 18 documents.
Python guard tests do not run Node; optional qualification does. This is finite
static evidence, without a new browser experiment or search-engine observation.

Migration keeps previous tools/results intact. Recompute into a new directory
using attributed headers and bytes. Before normative promotion, signal policies,
error eligibility, URL/base handling, alternative hypotheses and required rendered
or human evidence must still be addressed. Inventory equality is not a pass.

## References / Références

[HTML input decoding](https://html.spec.whatwg.org/multipage/parsing.html#determining-the-character-encoding),
[template declarations](https://html.spec.whatwg.org/multipage/scripting.html#attr-template-shadowrootmode),
[Encoding hooks](https://encoding.spec.whatwg.org/#utf-8-decode), and
[table insertion and document mode](https://html.spec.whatwg.org/multipage/parsing.html#parsing-main-inbody).
[Dated captures](../provenance/source-http-v1.json) retain URL, date, scope and hashes;
full source captures remain with the development custodian.
