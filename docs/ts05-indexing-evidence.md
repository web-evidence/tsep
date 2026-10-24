# TS05-A01 — policy map evidence / preuve de carte de politique

**TSEP 0.1.0-draft.45 · semiAuto · synthetic mechanism qualification**

## Scope and inputs / Portée et entrées

This reader checks one declared policy map against one supplied configuration
record. The minimum raw input is configuration plus intent. The target intent
contains ts05_policy, dated no later than observed_at, with applicability, scope,
separate crawl, indexing and protection decisions, actual_index_state set to
not-observed, and one deindex and one confidentiality claim with a level and
basis. The configuration declares crawl method and effect, indexing method, and
protection method. Both records must be linked to the same report target.

The finite reader accepts a bounded vocabulary. Unsupported or missing detail is
inconclusive. An atomic exemption is not supported; whole-control NA is separate
and requires a complete, reasoned intent inventory dated before assessment.

## Procedure and outcomes / Procédure et issues

The reader compares the supplied crawl method/effect, indexing objective/method
and visibility of meta noindex or X-Robots-Tag, protection method/objective, and
the declared bases for deindexing and confidentiality claims. It checks the
policy-map date and explicit configuration agreement. It does not retrieve or
interpret robots.txt, HTML, headers, login responses, crawler visits, removals or
search-index state.

A pass means only that the supplied plan is internally consistent for this
synthetic rule. A configuration contradiction or a fetchable noindex directive
against an inclusion goal is fail. A deindexing guarantee resting only on robots
Disallow is fail; a blocked noindex directive cannot establish exclusion. A
noindex directive or removal request with no observed completion does not prove
an actual index change, so the result remains inconclusive when the claim requires
that conclusion. Private content with no declared server-side access control is
fail; robots directives alone do not provide confidentiality. Missing, future,
unsupported or incomplete plans are inconclusive. NA requires positive, dated,
scope-wide inventory review, not missing evidence.

## Contradictory cases / Contre-cas

The frozen corpus includes a consistent, separated plan (pass), a Disallow/noindex
and robots-only privacy guarantee (fail), a missing map (inconclusive), and a
positive non-applicability inventory (NA). Unit tests also perturb a fetchable
noindex directive against an include goal, block a noindex directive with
Disallow, mismatch configuration and intent, change the asserted index state,
use unsupported mechanisms, duplicate claim axes, and move a policy/review date
past observation. These are authored synthetic tests, not observations of a live
site.

## Procedure for reuse / Réutilisation

Use the exact TS05-A01 identifier and draft.45 reader. Preserve original inputs,
dates and source evidence. Run python3 -B -m unittest tests/test_ts05_indexing.py
-v, then the full python3 scripts/verify.py profile documented in
docs/development.md. Application import/reception, browser inspection, downloaded
archive validation and replay outside the application are separate qualification
steps; this source change alone does not complete them.

## Limits and sources / Limites et sources

The claim inventory and configuration are supplied and unauthenticated. The
reader cannot establish whether records describe the deployed service or whether
a crawler can fetch the same representation. It does not measure current
indexing, prove a request was fulfilled, or establish privacy. A blocked URL may
remain known and appear without a snippet. Official source pages and the
date-bounded selected excerpts are preserved in the linked
source-captures/ts05-google-search-central-2026-10-16.md file; the paired SHA-256
file fingerprints that exact capture.

---

## Version française

**TSEP 0.1.0-draft.45 · semiAuto · qualification synthétique du mécanisme**

### Périmètre et entrées

Le lecteur compare une carte de politique déclarée à un record de configuration
fourni. L’entrée brute minimale est configuration et intent. La cible porte
intent.ts05_policy, datée au plus tard à observed_at, avec l’applicabilité, le
périmètre, des décisions distinctes crawl, indexing et protection,
actual_index_state réglé à not-observed, ainsi qu’une affirmation deindex et une
affirmation confidentiality, chacune avec niveau et base. La configuration
déclare la méthode et l’effet d’exploration, la méthode d’indexation et la méthode
de protection. Les deux records sont reliés à la même cible du rapport.

Le lecteur fermé accepte un vocabulaire borné. Les informations absentes ou non
prises en charge restent inconclusives. Il n’existe pas d’exemption atomique ;
NA du contrôle entier est distinct et requiert un inventaire d’intention complet,
motivé et antérieur à l’évaluation.

### Procédure et résultats

Le lecteur rapproche la méthode et l’effet d’exploration, l’objectif et la méthode
d’indexation, la visibilité de meta noindex ou X-Robots-Tag, la méthode et
l’objectif de protection, puis les bases des affirmations de désindexation et de
confidentialité. Il contrôle la date de la carte et l’accord déclaré avec la
configuration. Il ne récupère ni n’interprète robots.txt, HTML, en-têtes, réponses
d’authentification, visites de robots, demandes de retrait ou état de l’index.

Pass signifie seulement que le plan fourni est cohérent pour cette règle
synthétique. Une contradiction configuration/intention ou une directive noindex
accessible opposée à l’objectif d’inclusion donne fail. Une garantie de
désindexation reposant seulement sur Disallow donne fail ; un noindex bloqué ne
prouve pas l’exclusion. Une directive ou une demande de retrait sans exécution
observée ne prouve pas un changement réel de l’index ; le résultat reste
inconclusif quand l’affirmation exige cette conclusion. Un contenu privé sans
contrôle d’accès serveur déclaré donne fail ; les seules directives robots ne
protègent pas la confidentialité. Les plans absents, futurs, incomplets ou non
pris en charge restent inconclusifs. NA demande une revue d’inventaire positive,
datée et couvrant le périmètre.

### Contre-cas et limites

Le corpus figé comprend un plan séparé cohérent (pass), une garantie Disallow/noindex
et confidentialité par robots seulement (fail), une carte absente (inconclusive)
et un inventaire positif de non-applicabilité (NA). Les tests perturbent aussi un
noindex accessible contraire à l’objectif d’inclusion, un noindex bloqué par
Disallow, un désaccord configuration/intention, un état d’index affirmé, des
méthodes non prises en charge, des axes d’affirmation dupliqués et des dates
postérieures à l’observation. Ce sont des cas synthétiques rédigés, pas des
observations d’un site réel.

Les affirmations et la configuration sont fournies et non authentifiées. Le
lecteur ne prouve ni leur correspondance au service déployé ni l’accès du robot à
la même représentation. Il ne mesure pas l’indexation actuelle, n’atteste pas
l’exécution d’un retrait et n’établit pas la confidentialité. Une URL bloquée peut
rester connue et apparaître sans extrait. Les sources officielles et les extraits
datés figurent dans la capture liée, empreintée par SHA-256.
