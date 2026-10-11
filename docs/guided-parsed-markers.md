# TS01 guided parsed markers / Marqueurs parsés guidés TS01

## Français

Collecteur **8**, précontrôle **3**, intention guidée **4**. Ce parcours utilise
le profil normatif facultatif de [draft.28](source-markers.md), sans modifier
ses règles, ses priorités ni les rapports historiques.

Après une nouvelle `reference`, sélectionner le profil dans les critères de
chaque URL, avant `seal` puis `evaluate` :

```json
{
  "https://example.com/": {
    "policy": "markers",
    "identity_reader": "html-tree-markers-v1",
    "required_markers": ["Ressource attendue"],
    "forbidden_markers": ["Service indisponible"]
  }
}
```

Fournir Node 24 par `TSEP_SOURCE_NODE=/chemin/vers/node` pour `seal`, `evaluate`
et `replay`, ou disposer de Node 24 dans PATH. Les paquets parse5/entities restent
ceux de l'archive TSEP ; aucune installation de dépendance ni requête externe
n'est effectuée par ces lectures. L'absence du champ conserve l'ancien lecteur.
Un champ null/inconnu, ou ce profil avec digest/stable, est refusé à la préparation.
Les limites de critères sont vérifiées avant les comparaisons et le parseur.

Le précontrôle examine réellement la référence sans raccourci par égalité
d'empreinte. Une sonde locale minimale doit établir la disponibilité du parseur
et de Node 24. Absence ou échec de cette sonde refuse le scellement. Chaque
hypothèse complète qui contredit les critères refuse aussi le scellement, même
si le consensus normatif aurait été indéterminé. Cette décision de préparation
est volontairement plus stricte que TS01-A02 ; elle ne change pas son consensus.
Une lecture documentaire indisponible sans contradiction complète reste un
avertissement, conservé dans l'intention et le rapport. Une empreinte identique
peut ensuite établir l'identité malgré cet avertissement : les marqueurs ne sont
alors pas présentés comme établis. Le responsable doit apprécier leur pertinence.

Le reçu garde les résultats/complétudes par hypothèse, nombres de marqueurs
manquants/interdits, versions Node/V8, empreintes des sources et SHA-256 du
diagnostic complet calculé. Ce SHA porte sur le JSON UTF-8, ensure_ascii=False,
clés triées, séparateurs `(',', ':')`, sans saut final. Le diagnostic du
précontrôle est **reconstructible**, pas stocké intégralement dans ce reçu ;
les HTTP originaux et critères sont conservés. La raison est bornée à 4 096
caractères avec un indicateur explicite de réduction ; aucun verdict n'est tiré
de ce texte abrégé. Les diagnostics normatifs de mesure restent conservés par
l'adaptateur. Node n'est ni distribué ni authentifié ; ses versions ne prouvent
pas l'identité de son binaire.

Avant toute requête de mesure, recalculer le reçu doit donner exactement la même
valeur. Un changement de lecteur, runtime consigné, référence ou sources bloque
la mesure ; préparer une nouvelle référence/intention, jamais réécrire l'ancienne.
Les sources transitives du parseur et ses paquets sont liées au collecteur.
Le rejeu hors ligne recontrôle intention/référence et précontrôle, compare les
résultats atomiques, le gate, les résultats du rapport et tous les diagnostics
source, y compris leurs noms. Les écarts calculés sont conservés dans la sortie
de rejeu ; aucune réussite n'est émise. Les différences du runtime Python du
superviseur sont affichées séparément ; les diagnostics doivent rester exacts.

**Migration 7 → 8** : conserver les anciens dossiers et leurs outils exacts.
Collecter une nouvelle référence avec le collecteur 8, créer une intention 4,
puis une nouvelle mesure. Aucun re-étiquetage ni réévaluation rétrospective
présentée comme une collecte prospective. Les pages du laboratoire sont rédigées
et les intentions synthétiques ; seul le transport HTTP local est réellement
exécuté. Les scénarios figés v1 sont conservés ; v2 documente le durcissement des
contradictions partielles et de l'absence de runtime après critique de méthode.
Ni validation humaine, ni visibilité rendue, ni conformité d'Edikka n'en découle.

Laboratoire CLI reproductible (sortie neuve ; huit scénarios, dont deux refus
attendus avant mesure ; captures HTTP et erreurs conservées) :

```sh
python3 scripts/guided_profile_check.py --node /chemin/vers/node \
  --output /tmp/tsep-guided-profile-lab
```

Le script fournit un garde des appels réseau Python pendant scellement/rejeu ;
le garde d'API Node reste distinct. Aucun de ces gardes n'est une isolation système.

## English

Collector **8**, preflight **3**, guided intent **4** integrate the optional
[draft.28 parsed marker profile](source-markers.md) without changing its normative
precedence, consensus, rules or historical reports. After a fresh reference,
select `identity_reader: "html-tree-markers-v1"` per URL with markers policy,
positive required markers and optional forbidden markers, before seal/evaluate.
Set `TSEP_SOURCE_NODE` to Node 24 or supply Node 24 in PATH for seal/evaluate/replay.
Archived parser packages are used offline. Absence retains the legacy reader;
null, unknown names and this profile with digest/stable are configuration errors.
Validate marker bounds before substring comparisons or parser execution.

Preflight reads the reference without a digest shortcut. A minimal local parser
probe must succeed; unavailable Node/parser refuses sealing. Any **complete fail
hypothesis** also refuses sealing, even where normative consensus is inconclusive.
This stricter preparation rule does not alter TS01-A02. An unavailable document
reading without a complete contradiction remains a visible warning. Equal body
hash may later establish identity while the marker warning remains; it does not
establish those markers or their semantic appropriateness.

The receipt retains per-hypothesis completeness/outcome, missing/forbidden marker
counts, Node/V8 versions, source hashes and a SHA-256 of the full calculated
diagnostic. Hash UTF-8 JSON with ensure_ascii=False, sorted keys, separators
(',', ':') and no final newline. The full preflight diagnostic is reconstructible
from original HTTP, criteria, exact tools and recorded runtime, not stored in
full inside the receipt. Reason text is limited to 4,096 characters with an
explicit reduction flag; no decision depends on that shortened text. The adapter
still stores normative measurement diagnostics. Node is not distributed or
authenticated; version strings do not establish binary identity.

Recalculate the exact receipt before any evaluation request. Changed reader,
recorded runtime, reference or transitive source/package hashes prevents evaluation.
Offline replay verifies intent/reference bindings and preparation, then exact
atomic results, gate, report results and every source diagnostic, including file
names. Retain calculated mismatches without replay success. Python supervisor
runtime differences are disclosed separately; diagnostics must still match exactly.

**Migration 7 → 8:** retain historical packages with their original tools.
Acquire a fresh collector-8 reference, seal intent 4, then acquire a new evaluation.
Never relabel old dossiers or describe retrospective reassessment as prospective.
Frozen authored scenarios v1 remain available; v2 records the stricter partial
contradiction/runtime prerequisites following methodological criticism. Laboratory
pages/intent are synthetic; loopback HTTP transport is actually executed. No human
approval, rendered visibility, Edikka conformity, indexing or ranking is established.
The CLI laboratory command above uses eight frozen scenarios, including two
expected refusals before evaluation, retaining HTTP captures and command errors.
Its Python socket/DNS guard for seal/replay and the separate Node API guard are
not OS network isolation. Supply your own Node path and a new output directory.
