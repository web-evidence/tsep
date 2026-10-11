# Agent usage policy / Politique des usages agents — version 1

## Français

Draft.22 ajoute TS42-A01/A02/A03. Le profil préalable `agent-governance-v1`
vérifie une politique déclarée sur une URL et un inventaire explicite de mécanismes.
**C décrit la cohérence documentaire et la traduction du choix fourni dans ce
périmètre. Il ne prouve aucune visite réelle, identité, utilisation du contenu,
conformité d'un opérateur, indexation, citation ou performance commerciale.**
Les intitulés TS01–TS44 restent stables. TS43 (accès et journaux) et TS44 (contenu
accessible) sont distincts et ne gagnent pas de couverture par ce contrôle.

### Trois actes distincts

- **A01 — documenter les usages** : relier opérateur, type d'acteur, jeton de
  contrôle, mécanisme et finalités à des sources conservées. Une revue fournie
  atteste l'interprétation et sa complétude dans le périmètre. Le logiciel ne
  déduit pas les usages à partir du nom du robot ou de mots présents dans le texte.
  Une contradiction signalée par une revue liée donne fail ; source absente,
  trop ancienne, ambiguë ou revue non liée donne inconclusive.
- **A02 — décider** : chaque couple mécanisme/finalité a un choix allow/deny et
  un motif. Une décision séparée, fournie par le responsable ou un délégué nommé
  dans le plan, accepte ou refuse l'ensemble. Un refus lié donne fail ; absence,
  date incohérente ou auteur non déclaré donne inconclusive. La lecture de la
  documentation ne vaut jamais autorisation du responsable.
- **A03 — comparer** : pour chaque jeton, confronter la décision effective au
  robots.txt capturé, uniquement lorsque la source et sa revue qualifient ce
  mécanisme Allow/Disallow. Accord donne pass, contradiction donne fail, preuves
  manquantes ou mécanisme non qualifié donne inconclusive. Un échec indépendant
  demeure malgré une lacune sur un autre jeton. Aucune exemption atomique automatique.

Un mécanisme peut être `crawler`, `user-action` ou `control-token` (sans client
HTTP propre). Les finalités sont `search`, `training`, `user-action`, `advertising`,
`grounding`, `other` ; `other` exige une explication `other_purpose`. Il n'existe
pas de registre fournisseur implicite ou mis à jour en ligne. Les correspondances
et les capacités sont fournies, revues et liées à leur source datée.

### Format et liaisons

Entrée captures 1/2 : `url`, `observed_at` (évaluation), `context` habituel et
`intent.declared_at`. `intent.agent_policy` contient :

- `reader: agent-governance-v1`, `robots_profile: rfc9309-bounded-v1`,
  `max_source_age_days` (entier 0–3660), `owner`, `delegates` (liste explicite) ;
- `mechanisms` : `id`, `operator`, `actor_kind`, `product_token`, `purposes`,
  `mechanism` (`robots-txt` ou `other`), `source_ids` ;
- `decisions` : `mechanism_id`, `purpose`, `choice`, `reason` ;
- `arbitrations` : liste explicite, éventuellement vide.

`agent_documents` conserve pour chaque source `id`, `source_url`, `observed_at`
(acquisition), `raw_text` UTF-8 exact et son `sha256`. L'URL HTTP(S) ne contient
ni identifiants de connexion ni espaces/contrôles. L'âge est la différence de
**dates UTC calendaires** entre acquisition et évaluation, pas une durée exacte.
Une empreinte lie les octets fournis ; elle n'authentifie pas leur acquisition.

`agent_reviews` contient, par mécanisme, `mechanism_id`, `reviewer`, `provenance`,
`assistance`, `observed_at`, `mapping` (`supported`, `contradiction`, `unknown`),
`complete` booléen, `robots_applicable` booléen, `reason`, `binding_sha256`.
L'empreinte porte sur le JSON canonique de :

```json
{"mechanism": "objet complet du mécanisme", "documents": ["id, source_url, observed_at, sha256 de chaque source référencée"]}
```

Les sources référencées restent dans l'ordre de `agent_documents`. Canonisation :
JSON UTF-8, clés triées, aucune échappée ASCII forcée, séparateurs `,` et `:` sans
espaces. La revue est postérieure ou égale à toutes ses acquisitions et antérieure
ou égale à l'évaluation. `supported` nécessite complétude et applicabilité explicites.
La contradiction liée reste visible même si la complétude n'est pas établie.

`agent_decision` contient `author`, `provenance`, `assistance`, `observed_at`,
`accepted` booléen, `reason`, `binding_sha256`. Sa liaison porte sur
`{"url": target.url, "intent": target.intent}` entier, avec la même canonisation.
L'auteur doit correspondre exactement au responsable ou à un délégué déclaré.
La décision suit le plan et précède l'évaluation ; si une capture robots est
fournie, elle suit aussi la décision. Les rôles sont distincts, même si une personne
les cumule. Aucune identité ou délégation réelle n'est authentifiée par ces chaînes.

Provenances : `human`, `human-assisted`, `synthetic-exercise`. L'import refuse de
présenter une revue/décision synthétique comme publique ou restreinte réelle, ou
une revue dite humaine dans un dossier entièrement synthétique. L'assistance est
explicite ; aucune revue ou décision manquante n'est créée automatiquement.

### Finalités couplées et arbitrage

Les mécanismes partageant un même `product_token` (sans tenir compte de la casse)
sont regroupés, même si les identifiants ou noms d'opérateurs diffèrent. Les
renommer ne permet pas de séparer artificiellement un seul contrôle robots.
Des choix compatibles produisent une décision effective. Des choix opposés
peuvent être correctement documentés en A02 mais rendent A03 indéterminé.

Le responsable peut fournir un arbitrage : `product_token`, `choice`, `reason`
et `affected_pairs` listant exactement tous les couples `mechanism_id`/`purpose`
concernés. Il doit résoudre un conflit réel, sans masquer les souhaits initiaux.
Cet arbitrage fait partie du plan lié à la décision acceptée. A03 compare alors
le robots capturé à ce choix explicite, avec le compromis conservé. Le logiciel
ne choisit jamais quel usage sacrifier.

### Frontière de la première comparaison robots

`intent.crawler` désigne le client HTTP de collecte complet ; le jeton évalué
reste séparé. `robots` contient `observed_at` et les échanges HTTP bruts complets,
selon le [lecteur robots](robots-policy-experiment.md). L'origine de la cible,
le contexte, la chaîne, le client et les dates doivent être attribuables.
Seul un HTTP final 200 sous le profil RFC borné est qualifié. Les règles
Allow/Disallow, groupes et commentaires sont lus ; toute ligne que ce lecteur
ignore rend A03 indéterminé, y compris un champ Sitemap, Crawl-delay ou Host.
Cette limite volontaire évite de qualifier des usages sur un champ non interprété.
Content-Signal, TDMRep et autres mécanismes ne sont pas interprétés. Leur présence
ne devient ni preuve de protection, ni preuve d'absence de protection.

La réponse analysée est celle fournie au client de test. Appliquer un jeton à son
texte ne démontre pas ce que reçoit l'agent réel. Les tests d'accès, journaux,
vérifications d'identité et contenus rendus appartiennent aux étapes suivantes.

Bornes : 1–32 mécanismes ; 1–16 sources référencées chacun ; 64 documents et
64 revues maximum ; 256 Kio UTF-8 par source, sous la limite globale 8 Mio ;
32 délégués et 32 arbitrages ; 192 décisions ; identifiants ASCII alphanumériques,
tiret/tiret bas, 1–80 caractères ; jetons ASCII lettres/tiret/tiret bas, 1–128 ;
textes ordinaires non vides limités à 8192 caractères. Entrées malformées ou hors
bornes restent indéterminées. Voir les [52 cas figés](../tests/fixtures/agent-policy-v1.json),
qui utilisent uniquement des opérateurs, sources et décisions fictifs.

## English

Draft.22 adds TS42-A01/A02/A03 under the prior `agent-governance-v1` profile, for
one target URL and an explicitly scoped inventory. **C describes documented
policy consistency and implementation of supplied choices. It establishes no
actual visit, identity, content use, provider compliance, indexing or citation.**
TS43 access/logs and TS44 accessible content remain separate, without new coverage.

A01 binds the declared operator, actor type, token, mechanism and purposes to dated
retained sources and a supplied interpretation review. The tool never infers a
purpose from a bot name or keyword. A bound contradiction fails; missing, stale,
ambiguous or unbound evidence is inconclusive. A02 requires a reasoned allow/deny
choice for every declared mechanism/purpose and a separate owner/delegate decision.
A bound rejection fails; missing decision, wrong author or dates is inconclusive.
A03 compares qualified robots Allow/Disallow to the effective accepted choice.
Agreement passes, contradiction fails, unsupported/missing evidence is inconclusive.
An independent failed token survives a gap on another token. No atomic exemption.

Actor kinds: crawler, user-action, control-token (no HTTP client implied). Purposes:
search, training, user-action, advertising, grounding, other; other requires
other_purpose. There is no built-in or live provider registry. Supplied mappings
and capabilities require review against their dated sources.

Captures 1/2 retains url, assessment observed_at, context and intent.declared_at.
intent.agent_policy contains reader, robots_profile (rfc9309-bounded-v1), integer
max_source_age_days (0–3660), owner, explicit delegates, mechanisms, decisions and
arbitrations. Each mechanism has id, operator, actor_kind, product_token, purposes,
mechanism (robots-txt/other) and source_ids. Decisions have mechanism_id, purpose,
choice and reason. Sources in agent_documents have id, HTTP(S) source_url without
credentials/whitespace/control characters, acquisition observed_at, exact UTF-8
raw_text and sha256. Age is the UTC calendar-date difference, not elapsed duration;
acquisition cannot follow assessment. Hashes bind bytes, not authentic acquisition.

Each agent_reviews record has mechanism_id, reviewer, provenance, assistance,
observed_at, mapping (supported/contradiction/unknown), complete, robots_applicable,
reason and binding_sha256. Its hash binds the complete mechanism object and a
list of source id/source_url/observed_at/sha256 objects, in agent_documents order.
Canonical JSON uses sorted keys, ensure_ascii=false and comma/colon separators
without spaces, then UTF-8 SHA-256. Review dates follow every acquisition and do
not postdate assessment. Supported requires explicit true completeness and boolean
robots applicability. A bound contradiction survives unknown completeness.

agent_decision has author, provenance, assistance, observed_at, boolean accepted,
reason and binding_sha256 over the complete {url: target.url, intent: target.intent}
object with the same canonicalization. The author must exactly match the declared
owner or a named delegate. Decision follows intent and precedes assessment and
any supplied robots capture. These roles stay separate even for one person; string
matching authenticates neither the person nor their authority. Provenance is human,
human-assisted or synthetic-exercise. Import requires synthetic provenance exactly
when evidence access is synthetic. Assistance stays explicit; absent records are
never supplied by the tool.

Equal product tokens are grouped case-insensitively across operator names and IDs.
Compatible choices yield an effective choice. Opposing wishes can pass A02 but
leave A03 inconclusive. An owner arbitration may resolve this: product_token,
choice, reason, and affected_pairs enumerating exactly all mechanism_id/purpose
pairs. It must resolve a real conflict, retain initial wishes and be included in
the bound accepted plan. A03 then compares the captured policy with that adopted
choice. The software never decides which use to sacrifice.

intent.crawler is the full collection client; product_token is separate. robots
contains acquisition observed_at and full raw HTTP exchanges under the existing
bounded robots reader, with attributable origin, client, trace and context. Only
final HTTP 200 under the RFC profile is qualified. Allow/Disallow, groups and
comments are parsed; any ignored line makes A03 inconclusive, including Sitemap,
Crawl-delay or Host. Content-Signal, TDMRep and other mechanisms are not interpreted;
unsupported evidence proves neither protection nor lack of protection. Applying a
product token to the test client's representation says nothing about the real
agent's response. Access, logs, identity and rendered content need separate evidence.

Bounds: 1–32 mechanisms; 1–16 source references each; 64 documents/reviews each;
256 KiB UTF-8/source within global 8 MiB; 32 delegates/arbitrations; 192 decisions;
ASCII alphanumeric/hyphen/underscore IDs 1–80; ASCII letter/hyphen/underscore tokens
1–128; ordinary nonempty text ≤8192 characters. Malformed/out-of-bound inputs are
inconclusive. The 52 frozen examples contain fictitious sources and people only.

## Provenance and migration / Provenance et migration

[Operator documentation research](../provenance/agent-usage-policy-v1.json) informs
the distinction of purposes and control tokens, not an automated provider registry.
Les exigences de revue, liaison et arbitrage sont des choix éditoriaux TSEP.
Review, binding and arbitration requirements are TSEP editorial policy.
[Migration draft.22](migration-draft.22.md).
