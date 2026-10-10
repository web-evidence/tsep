# Canonical state sequences / Séquences d’états canonical

## Français

**Expérience 1, non normative.** Le protocole `0.1.0-draft.7`, les candidats
canonical 1 et 2 et leurs captures précédentes restent inchangés. Ce lot ajoute
un registre ordonné de résultats individuels, **sans résultat global de séquence**.
Un dernier accord ne supprime ni un écart antérieur, ni un état manquant ou
indéterminé. Trois captures ne démontrent pas une stabilité continue.

### Applicabilité et critères fixés avant collecte

Quatre recettes synthétiques sont figées dans
`tests/fixtures/canonical-state-sequences-v1.json` et son empreinte adjacente,
avant le code du laboratoire et avant sa collecte. Elles sont conçues en
connaissant les comparaisons existantes, sans validation indépendante des règles.
Chaque environnement possède une URL par recette, ouverte une seule fois.
Trois états sont prévus : `initial`, `after-action-1`, `after-action-2`.

| Recette | Initial | Après action 1 | Après action 2 |
| --- | --- | --- | --- |
| Témoin inchangé | Accord | Accord | Accord |
| Canonique différente puis retour | Accord | Contradiction | Accord |
| Déplacement dans body puis retour dans head | Accord | Indéterminé | Accord |
| Changement construit entre captures | Accord | Accord | Accord |

Ces issues sont les attentes **expérimentales dans les relevés**, jamais des
verdicts TSEP. Le dernier cas introduit puis retire une valeur dans le même
traitement synchrone avant la lecture : il illustre par construction une limite,
sans observer la transition ni démontrer son exécution à partir des captures.
La source complète et les scripts de recette restent des pièces distinctes.

La première capture est synchrone dans le gestionnaire `load`. Les deux suivantes
sont synchrones après la mutation de recette, dans le gestionnaire du bouton
`#advance`, avant tout `await`. Aucun délai arbitraire ni nouvelle tentative.
Le bouton reste désactivé jusqu’au reçu de la capture précédente. En cas de
mutation échouée, POST absent/refusé ou reçu mal formé, la séquence s’arrête ;
conserver les tentatives et déclarer les états suivants non reçus. Un résultat
inattendu n’autorise pas à rejouer la recette ni modifier ses attentes.

### Entrées, liaison et couverture

Le registre générique `predeclared-canonical-laboratory`, version 1, est spécialisé
par `method: canonical-state-sequence-v1`. Il fixe pages, tâches ordonnées, actions,
attentes, préférence explicite, obligation de canonique, historique déclaré,
octets HTTP servis et empreintes des outils. Chaque tâche garde un identifiant
unique environnement/recette/état, même lorsque plusieurs états partagent une URL.
Le candidat 2 compare chaque relevé à son intention liée à cette tâche ; ses
règles et son format ne changent pas.

Une collecte HTTP source par page précède toute navigation. Un reçu lie le registre
aux manifestes source. Chaque POST de page contient l’état, l’index de séquence,
l’action et l’empreinte du reçu précédent (nulle au premier état). Une seule
navigation et un POST unique par état reçu sont admis. Le récepteur conserve les
octets des enveloppes et de ses réponses ; le rejeu contrôle aussi le reçu renvoyé.
La chronologie impose navigation → action → capture → POST → observation, avec
l’observation précédente avant l’action suivante. Le marqueur `#lab-state` présent
dans l’arbre est comparé à l’état prévu comme une vérification de recette.

Ces liaisons vérifient une cohérence interne. Elles ne signent ni n’authentifient
l’arbre, les API, l’identité du navigateur, l’action, la causalité ou les horloges.
Deux environnements peuvent partager un moteur. La couverture du lecteur reste
bornée et toutes ses limites demeurent dans chaque résultat individuel.

`experiments/canonical_sequence.py` accepte le registre, une page et exactement
une entrée par tâche : `{snapshot, missing_reason}`. Un relevé reçu utilise le
format du candidat 2 avec raison nulle. Un relevé absent exige `snapshot: null`
et une raison explicite. Une structure invalide est refusée. Le registre rendu
expose la liste ordonnée des résultats, les identifiants d’écarts, d’indéterminés
et d’absences, ainsi que le **dernier état prévu**, même s’il manque. Aucun champ
`outcome` global, aucune étiquette « corrigée » ou « stable » n’est produit.
Le comparateur seul ne vérifie ni transport ni exécution.

### Collecte, rejeu et migration

```sh
python3 examples/canonical_sequence_lab.py serve --output /tmp/new-sequence-source
# Une navigation par page, deux clics prévus après réception de chaque reçu.
# Arrêter le serveur après collecte ; ne pas refaire un état manquant.
python3 examples/canonical_sequence_lab.py finish /tmp/new-sequence-source \
  --observations /tmp/sequence-observations.json --output /tmp/new-sequence-delivery
python3 examples/canonical_sequence_lab.py replay /tmp/new-sequence-delivery
```

L’objet observations contient chaque environnement : `{status: collected, pages}`
ou `{status: not-collected, reason}`. Une page, indexée par recette, porte
`navigation_started_at`, `observed_at`, `browser: {name, version, user_agent}` et
`states`. Chaque état reçu conserve les champs du payload, `page_receipt`,
`action_started_at`, `observed_at` et `devLogs` ; un état absent est
`{missing_reason: "..."}`. Après un état manquant, les suivants doivent aussi
être manquants. Les requêtes déjà tentées ne peuvent être masquées par ce statut.
Les journaux développeur sont conservés, sans preuve d’absence générale d’erreurs.

Un écart d’attente est livré et reste faux dans les vérifications de recette.
Une erreur de page rend leur concordance fausse. Une incohérence de transport,
de chaîne ou de chronologie refuse la livraison, sans supprimer ses entrées.
Un état manquant donne une chaîne incomplète, jamais un accord implicite.
Le rejeu est sans réseau et sans navigateur. Codes : 0 si tous les états prévus
sont reçus et concordants, 2 si écart ou absence conservés, 64 si entrée invalide.
Une sortie existante n’est jamais écrasée. Les fichiers livrés sont explicitement
listés dans un manifeste ; garder séparément les captures visuelles opérateur.

Migration additive : nouveaux outils et recette, aucune conversion automatique
des anciennes observations en séquence. Garder les kits précédents avec leurs
outils d’origine. Les tests de transport utilisent des arbres rédigés et clients
HTTP étiquetés comme tels, pas des navigateurs. Ils éprouvent reçus réutilisés,
ordre, mutation des liaisons avec empreintes recalculées, états manquants,
marqueur divergent, rejeu hors réseau et conservation d’un écart avant accord.

## English

**Non-normative experiment 1.** Protocol draft.7 and canonical candidates 1/2
remain unchanged. This adds an ordered ledger of individual outcomes, **no
sequence-level outcome**. A later agreement never erases an earlier contradiction,
an undetermined record or a missing state. Three snapshots do not prove stability.

Four synthetic recipes and expectations were frozen before this laboratory code
and collection, with knowledge of the existing comparison rules. Expected triples
are agreement/agreement/agreement for the unchanged and constructed-between-captures
recipes, agreement/contradiction/agreement for a value change and return, and
agreement/undetermined/agreement for movement into body and back into head. The
transient change is constructed and removed inside one handler before capture:
it illustrates a sampling limit, but its intermediate DOM or execution is not
established by the snapshots. Keep the original served source and recipe code.

Each environment/case has one URL and one navigation. Initial capture runs
synchronously in load; two next captures run synchronously after planned mutations
inside the click handler, before any await. The next action requires the prior
receipt. Failed mutation, missing/rejected POST or malformed receipt stops the
sequence without retry; retain attempts and mark later states missing. No timers,
implicit resampling or rewritten expectations.

The generic registration version 1 is specialized by
`method: canonical-state-sequence-v1`, with explicit ordered task ids for each
page, actions, intent, expectations, exact served HTTP bytes and tool fingerprints.
Source collection and its receipt precede navigation. Candidate 2 interprets each
snapshot with its registered task intent, without changing its comparison rules.
The ordered ledger accepts exactly one `{snapshot, missing_reason}` entry per task.
Missing snapshots require a reason; received ones require a null missing reason.
It retains individual outcomes, contradiction/unknown/missing ids and the last
**planned** state even if missing. It emits no overall outcome or corrected/stable
label. The pure comparison function does not validate execution or transport.

The laboratory validates one GET per page and one POST per received state. POSTs
bind the state, sequence index, action and previous receipt (initially null); exact
receiver responses are retained and checked. Dates link navigation, action,
capture, POST and operator observation, including prior observation before the
next action. The in-tree state marker is a separate recipe check. Hash chains
and clocks establish internal consistency, not authentication, causal proof or
trusted timing. Page APIs, browser identity and execution remain unattested.
Inventory coverage limits remain explicit. Environments may share an engine.

Use the commands above. Observation input maps environments to collected pages
or an explicit unavailable reason. A page records browser identity, navigation
and observation times, and all planned states. A received state retains payload
fields, its receipt, action/observation times and developer logs; a missing state
has only a missing reason. Later captures after a gap are rejected. Missing records
cannot conceal requests already made. Recipe mismatches and page errors remain
visible; transport/chronology violations reject delivery while retaining inputs.
Empty logs do not establish absence of errors. Offline replay uses the explicit
manifest without network or browser execution and refuses unexpected files.
Exit codes: 0 for all states received and recipe checks matched, 2 for retained
mismatch/absence, 64 for invalid inputs. Existing outputs are never overwritten.

Migration is additive, with no conversion of old captures into sequences and no
normative change. Preserve older kits and their original tools. Transport tests
use labeled authored trees and HTTP clients, not browsers. They cover missing
states, duplicate/rebound receipts and requests, coherent rehashing of changed
chain/action/index, mismatched in-tree marker, offline replay and preserved earlier
contradictions. No indexing, ranking, engine canonical selection, certification
or independent validation follows from this experiment.
