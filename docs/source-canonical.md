# Canonical source policy / Politique canonical source — html-tree-canonical-v1

## Français

Profil facultatif de draft.16, choisi avant les captures par
`intent.canonical.source_reader="html-tree-canonical-v1"`. Il étend la source de
TS10-A01, celle de TS10-A02 et la disponibilité des sources pour sa revue de contenu.
A03, A04, TS01, TS07 et les lecteurs DOM ne changent pas. Champ absent : chemin
historique fixe. Valeur nulle/inconnue ou Node 24 indisponible : inconclusive sans
repli. Le choix du profil ne vaut ni exemption de rendu ni revue humaine.

### Entrées, hypothèses et preuve

Conserver famille, préférence absolue HTTP(S) sans fragment, méthodes nécessaires,
plan de rendu, contexte et dates préalables, traces GET complètes et octets. Les
conditions de rattachement existantes restent obligatoires. Seul le profil HTTP
UTF-8 explicite de [source-head](source-head-observation.md) est lu : une valeur
Content-Type `text/html; charset=utf-8`, casse/espaces/guillemets permis, aucun autre
paramètre. Consommer un BOM initial ; pas de remplacement d'octets ou de détection
d'encodage. Le non-HTML `text/plain` garde son exemption documentée antérieure.

Deux arbres complets parse5 8.0.1 / entities 8.0.0 sont construits sous les
hypothèses de scripts activés/désactivés, sans exécution. Le préfixe des tokens
conserve les balises, segments textuels, piles avant/après, fermetures explicites
et offsets d'octets. Ces hypothèses sont alternatives, pas des états rendus observés.
Les attributs sont décodés selon HTML ; aucune URL n'est résolue ni normalisée.
Chaque valeur est comparée littéralement à la préférence déclarée.

### Décision pour chaque hypothèse

1. Inventaire incomplet : inconclusive, sans conclure à une absence.
2. Conserver les limites : erreurs signalées, fermeture sans élément correspondant,
   second début html/head et élément du head hors du registre ci-dessous. Un
   template déclarant shadow open/closed ou un attribut `for` ajoute une inconnue.
   Le contenu des templates ordinaires reste dans les pièces, hors des signaux
   actifs. Une déclaration shadow invalide reste une valeur conservée de template
   ordinaire ; aucune attache shadow n'est inférée.
3. Examiner chaque link HTML dont rel contient le token canonical. Un ancêtre de
   namespace étranger, une position inconnue, des attributs dupliqués signalés sur
   cette balise ou un attribut hors du [registre existant](canonical-attribute-coverage.md)
   rendent ce signal inconclusive. Un élément link de namespace non HTML n'est pas
   une déclaration HTML ; une canonical HTML sous un point d'intégration étranger
   reste inconnue. Les octets originaux restent disponibles dans les deux cas.
4. Dans le head, exiger un enfant direct et une position source antérieure à sa
   fermeture explicite. Un descendant indirect ou une réinsertion après fermeture
   reste inconclusive, sans affirmer ce que Google en fait. Dans le body ordinaire,
   la canonical est une contradiction TSEP même si son URL égale la préférence.
5. Pour un signal ainsi qualifié, un href absent, relatif, avec fragment ou différent
   de la préférence est fail. Une contradiction qualifiée reste fail malgré une
   autre inconnue dans l'hypothèse ; les attributs/contextes inconnus ne produisent
   pas eux-mêmes cette contradiction. Sinon, toute inconnue empêche pass. Sans
   inconnue, l'absence de canonical donne fail si HTML est une méthode requise ;
   sinon les valeurs convergentes, doublons conservés, donnent pass.

Le registre des éléments permis dans le préfixe du head est base, link, meta,
noscript, script, style, template et title ; les transitions html/body normales ne
sont pas des éléments de métadonnées inconnus. Les contenus de template ne sont
pas évalués comme le head du document. Cette frontière ne valide pas tout HTML.
Les erreurs signalées empêchent une réussite, mais n'effacent pas une contradiction
qualifiée indépendante ; un doublon d'attribut affectant la canonical la rend
inconnue. Une canonical correcte suivie d'un préfixe non qualifié ne suffit pas à pass.

Deux pass donnent pass, deux fail donnent fail, sinon inconclusive. Une différence
dans une seule hypothèse ne devient pas un fail établi pour les deux. L'agrégation
avec HTTP Link, redirections, autres membres et états DOM demeure distincte : une
contradiction attribuable sur ces surfaces subsiste malgré un type de contenu ou
plan de rendu illisible. Un header convergent ne remplace jamais la source inconnue.
A02 reste manual ; une source inconnue empêche de déclarer sa revue complète et
aucun jugement de compatibilité n'est calculé par ce lecteur.

### Conservation, limites et migration

Les observations liées au rapport retiennent URL du document, digest du corps,
valeurs canonical et base, templates et signaux inertes, préfixe, erreurs, décodage,
mode, sources/runtime, les deux décisions et motifs. Le calcul est daté à l'import,
pas présenté comme une capture moteur. Le rejeu recalcule ces observations et les
compare. Les limites du lecteur source/head restent applicables ; le diagnostic
final formaté est borné à 4 Mio par source. Dépassement : inconclusive avec motif,
sans liste tronquée ni conclusion d'absence. Le corps complet reste conservé.

Node 24 est fourni séparément via TSEP_SOURCE_NODE ou PATH, sans installation/repli
automatique. Le garde d'API Node n'est pas une isolation réseau système. Les
empreintes vérifient l'intégrité, pas l'authenticité des pièces ou jugements.
Les contrôles restent candidats ; aucun état Google, gain de classement, certification
ou conformité TS10 entière ne découle d'un pass isolé. Voir [migration](migration-draft.16.md).

53 cas synthétiques sont figés avant leurs implémentations respectives. Quatre
cas supplémentaires vérifient les conflits HTTP indépendants ; trois ont d'abord
révélé une perte de contradiction. Les échecs sont conservés dans
`provenance/source-canonical-signal-correction.json`, les attentes n'ont pas changé.
Deux cas ajoutés après relecture verrouillent les niveaux d’agrégation sans changer
la politique : contradiction dans les deux lectures malgré une inconnue, puis fail
contre inconclusive. La qualification Node porte donc sur 55 cas et vérifie aussi
les 488 entrées/sorties historiques. La limite de diagnostic annule également une
contradiction calculée de la source si sa pièce complète ne peut pas être conservée ;
un conflit HTTP indépendant reste exploitable. Les deux côtés du seuil sont testés.

```sh
python3 scripts/source_canonical_check.py --node /path/to/node24 --output new-qualification.json
TSEP_SOURCE_NODE=/path/to/node24 python3 adapters/captures.py --help
```

## English

Draft.16's optional prior intent.canonical.source_reader="html-tree-canonical-v1"
extends TS10-A01/A02 source decisions and A02 source availability for supplied content
review. A03/A04, TS01/TS07 and DOM readers are unchanged. Absent field preserves
legacy behavior; null/unknown/unavailable selection is inconclusive without fallback.
Existing family, absolute HTTP(S) fragment-free preference, required methods,
rendering plan, dates/context, complete GET trace and review bindings remain required.

Use one explicit UTF-8 HTML Content-Type with no other parameters; ASCII case,
whitespace and quoted UTF-8 are allowed. Consume one BOM; no invalid-byte replacement,
sniffing or URL normalization/resolution. Existing documented text/plain exemption
is retained. Pinned parse5 builds both complete static scripting hypotheses, never
executes scripts. HTML attribute decoding is preserved; compare the resulting href
literally, retain original tags/byte offsets and base declarations without resolving.

For each hypothesis: incomplete inventory is inconclusive. Record reported errors,
unmatched prefix end tags, repeated html/head starts, unsupported head elements and
declared open/closed shadow or template for. Ordinary template contents are retained
but inactive; invalid shadow declarations do not assert attachment. Qualified HTML
canonical links must have no foreign namespace ancestry or duplicate-attribute error
affecting that tag, and satisfy the existing attribute registry. Foreign-namespace
link elements are not HTML declarations; HTML integration-point declarations remain
unknown. Original bytes are retained.

In head, require direct parentage and source position before explicit closure;
indirect or reinserted declarations remain unknown without a Google claim. Ordinary
body canonical is a TSEP contradiction even for the preferred URL. Missing/relative/
fragment/different href is fail for a qualified signal. Independent qualified
contradictions survive other unknowns; unknown attributes/contexts do not themselves
establish fail. Otherwise any unknown blocks pass. In a complete qualified inventory,
required HTML absence fails; optional absence or all identical preferred values pass.

The prefix registry is base/link/meta/noscript/script/style/template/title, with normal
html/body transitions permitted and template contents separate. This is not full HTML
validity. Reported errors prevent pass without erasing independent qualified failures.
Two pass yield pass, two fail yield fail, otherwise inconclusive. Do not treat these
alternative hypotheses as simultaneously observed DOM states. Independent final HTTP
Link/redirect/member/DOM contradictions survive unsupported media or rendering plans.
Convergent headers cannot replace unknown source. A02 remains manual, with unknown
source preventing complete review inputs; no compatibility judgment is computed.

Report-linked diagnostics retain document URL, body hash, canonical/base records,
templates, prefix, errors, decoding, mode, tool/runtime identity and both decisions.
They are calculations at import, not engine captures, and are compared during replay.
Source/head bounds apply, plus 4 MiB final formatted diagnostics per source. Excess
is inconclusive without truncated absence claims; full input is retained. Node 24
via TSEP_SOURCE_NODE/PATH is separate and optional to core Python, without download.
API network guard is not OS isolation; integrity is not evidence authentication.
No full-control conformity, engine selection, ranking or certification is implied.

The 49-case authored oracle and four later independent-signal cases precede their
respective implementations. Three initial implementation failures are retained with
unchanged expectations. Optional Node qualification checks 55 cases (including two post-review aggregation cases with no policy change)
and exact 488-case historical behavior. The diagnostic limit also refuses a computed
source failure if its complete artifact cannot be retained; independent HTTP failures
remain usable. Both sides of that boundary are tested. Missing Node is explicitly reduced coverage, not
observed agreement. Migration preserves historical plans, reports, archives and tags.
