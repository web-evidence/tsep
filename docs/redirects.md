# TS02 — trajectoires HTTP / HTTP trajectories

## Français

Draft.8 ajoute deux règles : A01 conserve la validation préalable du responsable,
A02 interprète la trajectoire HTTP par rapport au plan. Le contrôle est manuel
assisté par logiciel ; aucun C automatique n'est admis. Il porte sur les anciennes
URL explicitement choisies, pas toutes les redirections d'un site.

Chaque cible du format captures 1 ou 2 contient `url`, `observed_at`, `context`
(`network`, `bounds`, `tool`, `tool_version`) et `http`, dans le format existant.
`intent` contient `declared_at`, `crawler` et :

```json
{
  "redirect_plan": {
    "mechanism": "http",
    "source_url": "https://example.com/old",
    "expected_final_url": "https://example.com/new",
    "min_redirects": 1,
    "max_redirects": 1,
    "redirect_statuses": [301, 308],
    "terminal_statuses": [200]
  }
}
```

Le responsable examine le plan et le contexte **avant** la collecte. Sa réponse
fournie dans `intent.redirect_review` contient `reviewer`, `role` égal à
`responsible-owner`, `observed_at`, `outcome` (`approved` ou `rejected`), `reason`,
`assistance`, `provenance` (`human` ou `human-assisted`) et `plan_sha256`.
Tous les textes doivent être renseignés. L'empreinte porte sur le JSON
`{"url": ..., "intent": ..., "context": ...}`, sans `intent.redirect_review` :
UTF-8, `ensure_ascii=False`, clés triées, séparateurs `(',', ':')`, sans saut final.
Elle ne prouve ni identité ni sincérité. La commande d'import n'invente pas cette
réponse. Les preuves synthétiques exigent `synthetic-exercise` ; cette provenance
est refusée pour un import déclaré public ou restreint. Les exemples ne sont pas
des validations de Bertrand.

Le plan peut autoriser 302/303/307 s'il s'agit du comportement voulu : un code
temporaire n'est pas intrinsèquement un échec. Un retrait prévu peut attendre
410 ; cela ne satisfait pas TS01. Un seuil de sauts exprime une décision de projet,
pas une limite universelle de Google. Pour des trajectoires directes, fixer 1.

Un maximum dépassé ou une boucle prouvée sont des contradictions, même sans
réponse terminale. Une collecte arrêtée avant toute contradiction reste
indéterminée. Une approbation A01 absente n'efface pas un échec A02 ; A02 pass seul
ne suffit pas à C. Aucun statut 200 ne prouve à lui seul la bonne destination.

La référence accepte GET HTTP/1.1 sans conditions, identifiants ni cookies,
20 échanges au plus et un plan de 0 à 19 redirections. Elle suit 301/302/303/307/308,
résout les Location relatives et compare les URL exactes, sans assimiler casse,
slash, paramètres ou variantes encodées. Une URL doit être HTTP(S), ASCII (les
caractères non ASCII peuvent être encodés), sans fragment, espaces ou identifiants.
Une Location manquante dans une réponse complète est une contradiction ; plusieurs
Location restent ambiguës. HTTP/2 brut, mécanismes JavaScript/meta refresh,
Refresh HTTP et syntaxe URL hors portée ne donnent pas une réussite implicite.
Les restrictions de décodage HTTP existantes restent applicables.

38 attentes synthétiques ont été figées avant l'implémentation dans
`tests/fixtures/redirect-cases-v1.json`. Le corpus de conformance en conserve une
copie identique. Il couvre accords, contradictions et inconnues par règle, y
compris une preuve de contradiction avant une réponse manquante. Ce corpus n'est
pas une observation réelle, ni une preuve de pertinence métier des destinations.

L'import utilise `adapters/captures.py`, le rapport `reports/html.py` et le rejeu
`adapters/replay.py`, avec les outils de la même version. La revue TS02 préalable
utilise désormais [`adapters/redirect_plan.py`](redirect-plan-workflow.md) : fiche,
réponse vide, import fourni puis liaison aux captures ultérieures. `adapters/review.py`
reste le parcours distinct des revues après capture TS04/TS07/TS10.

## English

Draft.8 adds A01 supplied prior owner approval and A02 observed HTTP trajectory
comparison. TS02 remains human-assisted: A02 success alone cannot establish C,
and absent approval cannot erase an observed A02 contradiction. Inputs use the
existing captures v1/v2 format. The plan/approval fields and canonical JSON digest
are specified above. Approval must fall between intent declaration and capture.
Synthetic records require synthetic-exercise and cannot be imported as public or
restricted evidence. Neither the supplied identity nor judgment is authenticated.

The plan explicitly chooses destination, redirect statuses, terminal statuses and
minimum/maximum redirect counts. Temporary redirects can be intentional; a planned
410 does not satisfy TS01. Project hop limits are not asserted Google limits.
Complete attributable prefixes can prove forbidden types, exceeded limits, missing
Location or loops. Unfinished collection without contradiction stays inconclusive.

Reference bounds: unconditional unauthenticated HTTP/1.1 GET, 20 exchanges,
0–19 redirects, 301/302/303/307/308, relative Location resolution, exact URL
comparison. ASCII HTTP(S) URLs without fragments, whitespace or userinfo; encoded
non-ASCII is retained without equivalence inference. Repeated Location is ambiguous.
Raw HTTP/2, client-side navigation and Refresh HTTP are outside successful coverage.
Existing HTTP decoding bounds apply. No semantic equivalence, live crawler cache,
indexing or ranking conclusion is made.

The 38 prefrozen synthetic expectations are copied unchanged into conformance.
Capture import, HTML reporting and offline replay use the current pinned tool
archive. [Prior-plan workflow 1](redirect-plan-workflow.md) prepares blank TS02
owner decisions and binds supplied responses to later captures; the separate
TS04/TS07/TS10 post-capture review workflow remains unchanged.
