# Agent access evidence / Preuves d’accès agents — version 1

## Français

Draft.23 ajoute TS43-A01/A02/A03 avec le profil préalable `agent-access-v1`.
Il rapproche un **client de test initié par l’évaluateur**, sa chaîne HTTP et les
journaux fournis. **C décrit le traitement de ce client conformément au plan et
la documentation de ses traces ; il ne prouve pas l’accès réel de l’opérateur.**
Une imitation refusée peut être le résultat attendu d’une politique qui vérifie
l’identité. Un 200 ne prouve ni l’identité ni le contenu attendu. Aucune conformité
SEO globale, sécurité, visite opérateur ou citation ne découle de ce contrôle.

### Règles et interprétation

- **A01 — client documenté et réponse prévue** : conserver une source datée et
  une revue fournie de la chaîne User-Agent complète ; vérifier les échanges GET
  attribués, redirections et dates ; comparer la réponse au traitement prévu du
  client de test. Une revue liée contradictoire ou une réponse contraire au plan
  échoue ; l’absence de revue, une trace incomplète ou une portée inconnue restent
  indéterminées. Une contradiction HTTP qualifiée survit à une revue absente.
- **A02 — rapprochement** : chaque échange doit avoir un identifiant serveur
  unique dans la couche et la fenêtre prévues, puis méthode, URL, User-Agent et
  statut concordants. Une contradiction sur une ligne attribuée échoue, même si
  un autre saut manque de preuve. Identifiant seul, doublon, date hors fenêtre,
  cache ambigu, couche différente ou journal absent restent indéterminés.
- **A03 — attribution honnête** : conserver la commande et le reçu d’exécution,
  ainsi qu’une qualification fournie, datée et liée. Le test reste initié par
  l’évaluateur et l’identité opérateur non vérifiée. Une affirmation liée de visite
  réelle ou d’identité vérifiée échoue ; qualification absente ou non liée reste
  indéterminée. Une IP ou une chaîne User-Agent ne transforme jamais ce test en
  visite réelle, même si l’adresse figure dans une plage d’un opérateur.

Aucun résultat atomique NA automatique. Un jeton sans client HTTP, une visite
spontanée d’un opérateur, une méthode DNS/IP d’authentification d’un visiteur ou
une autre forme de preuve restent hors de ce premier lecteur. Leur absence de
prise en charge ne prouve ni une anomalie du site ni leur inexistence. TS42 et
TS44 gardent leurs objets propres. Une réussite de TS43 ne les clôt pas.

### Plan et captures

Entrée captures 1/2 habituelle : `url`, `observed_at` (évaluation), `context` avec
network/bounds/tool/tool_version, `intent.declared_at` puis `intent.agent_access` :

- `reader: agent-access-v1` ; `client` contient operator, actor_kind (crawler ou
  user-action), product_token, full_user_agent et source_ids. Aucun User-Agent
  n’est construit à partir d’un jeton de contrôle ;
- `operator_access: allow` fixe l’accès souhaité de l’opérateur séparément ;
  `test_access` fixe action (allow/deny), policy_basis (ua-only/identity-gated/other),
  reason, status et final_url. Le fondement est déclaré, pas prouvé par un test.
  Allow qualifie ici HTTP 200 avec expected_body_sha256 du corps complet prévu.
  Deny qualifie 401/403 ; un hash facultatif impose aussi cette référence exacte.
  Autres conventions, contenu variable sans référence stable et challenge 200
  à interpréter comme refus restent à qualifier. Une réponse 200 différente du
  corps préalablement fixé est une contradiction, pas une réussite d’accès ;
- origins (1–16 origines HTTP(S) exactes terminées par /), log_layer, id_header
  en minuscules, window_start/window_end, clock_skew_ms (0–30000),
  max_duration_ms (1–60000), max_source_age_days (0–3660).

Le plan précède la fenêtre, longue d’au plus 24 heures, qui précède l’évaluation.
Chaque saut de `http` garde les champs bruts habituels plus sent_at/received_at.
Les intervalles sont ordonnés, compris dans la fenêtre et la durée par échange
ne dépasse pas la borne. Chaque origine doit avoir été déclarée. Le lecteur HTTP
historique impose GET sans authentification, cookies, requête conditionnelle ou
Range, Host et User-Agent exacts, réponses complètes, 20 sauts maximum et ses
limites de décodage. Les redirections interorigines sont admises si leurs origines
étaient déclarées et couvertes par le même export de journaux qualifié.

### Source du client et revue

`client_documents` : id, source_url HTTP(S), observed_at d’acquisition, raw_text
UTF-8 exact et sha256. Les URL n’ont pas d’identifiants de connexion, espaces ou
contrôles ; les ports doivent être valides. Âge : différence des dates UTC
calendaires acquisition/évaluation, sans source future. Chaque source référencée
est unique et présente. Les empreintes lient les octets sans les authentifier.

`client_review` contient reviewer, provenance, assistance, observed_at, reason,
full_user_agent (`supported`, `contradiction`, `unknown`) et binding_sha256.
La revue suit toutes les acquisitions référencées et précède l’évaluation.
Sa liaison porte sur `{client: plan.client, documents: [...]}`, les documents
référencés gardant l’ordre de client_documents et uniquement leurs champs id,
source_url, observed_at, sha256. La revue fournie qualifie la chaîne complète
contre les sources ; la présence de mots dans le texte ne vaut pas revue.

### Journal brut et corrélation

`logs` contient reader `tsep-request-log-v1`, format `native-jsonl`, raw_jsonl et
sha256, observed_at (export), window_start/end, complete, origins et layer.
La fenêtre complète déclarée couvre celle du plan et se termine avant l’export,
lui-même antérieur à l’évaluation. Origines (ordre compris) et couche correspondent
exactement au plan. Un export agrégé peut couvrir plusieurs origines ; cela reste
une déclaration qualifiée par la revue. Format converti, journaux Apache/Nginx
ordinaires ou fournisseur non qualifié : indéterminé, sans conversion implicite.

Chaque ligne JSON native est un objet avec request_id, request_at, method, url
absolue, user_agent, status entier et layer. Les autres champs, dont IP ou en-têtes
forwarded, restent dans l’original sans qualification d’identité. Clés dupliquées,
valeurs non finies, ligne vide/incomplète ou syntaxe invalide rendent la lecture
indéterminée. request_id est un identifiant ASCII de 1–80 caractères (lettres,
chiffres, tiret, tiret bas). La méthode est un mot ASCII majuscule de 1–20 lettres.

`log_review` contient les champs de revue habituels, binding_sha256 et cinq
booléens explicitement vrais : server_generated_id, per_request_id, client_facing,
clock_bound_confirmed, complete. Le relecteur qualifie l’origine et la fraîcheur
par réponse de l’identifiant, la couche comparable à la réponse cliente, la borne
d’horloge et l’exhaustivité de l’export fourni. Une seule égalité d’identifiant
n’établit pas ces propriétés. La revue suit l’export et le dernier échange.
La liaison porte sur `{url, intent, http, logs}` complets et exacts.

L’en-tête d’identifiant doit être unique dans chaque réponse et absent de la
requête. Un identifiant répété entre sauts rend leur corrélation indéterminée.
Chercher exactement une ligne ayant cet identifiant dans la couche prévue,
puis exiger request_at dans [sent_at − tolérance, received_at + tolérance].
**Vérifier cette fenêtre avant de comparer les autres champs** : un ancien
identifiant de cache avec un autre client est une attribution refusée, pas une
contradiction attribuable au test courant. Dans une ligne qualifiée, toute
différence de méthode, URL littérale, chaîne client ou statut donne fail. L’absence
de ligne reste indéterminée, même si l’export est déclaré complet ; elle ne prouve
pas une panne du site. Conserver les sauts manquants et les contradictions distincts.

### Exécution et attribution

`execution` garde origin `assessor-test`, initiator, command (liste des arguments,
conservée sans exécution), started_at/ended_at. Il suit le plan, contient tous les
échanges et précède l’évaluation. C’est un reçu fourni, pas une authentification
de la personne ou de l’exécution par le validateur.

`attribution` porte reviewer, provenance, assistance, observed_at, reason,
request_origin `assessor-test`, operator_identity `not-verified`,
claims_operator_visit false et binding_sha256. Liaison : `{url, intent, http,
logs, execution}`, avec null pour un champ absent. Sa date suit l’exécution et
précède l’évaluation. Une revendication vraie de visite, une identité « verified »
ou une origine « operator » contredisent le test initié par l’évaluateur.

Toutes les liaisons utilisent SHA-256 du JSON UTF-8 aux clés triées, séparateurs
`,`/`:` sans espaces, sans échappée ASCII forcée. Provenance des revues : human,
human-assisted ou synthetic-exercise. L’import impose la cohérence avec l’accès
synthétique/réel du dossier ; il ne crée pas de revue absente. Auteur et contenu
des jugements ne sont pas authentifiés. Pour les performances, les sources et les
visites réelles, conserver les autres contrôles et leurs limites.

Bornes : 64 documents, 16 références au plus par client, 256 Kio UTF-8 par source,
User-Agent ASCII imprimable de 1–2048 caractères, jeton de 1–128 lettres/tirets/
tirets bas ; journal 1 Mio et 10 000 lignes ; 128 arguments au plus ; textes non
vides de 8192 caractères maximum ; entrée globale 8 Mio. Hors bornes : inconnu.
Les [71 cas figés](../tests/fixtures/agent-access-v1.json) sont synthétiques.
La recette de laboratoire fixe ses attendus avant son implémentation ; ses
exécutions et rapports doivent rester identifiés comme expérience contrôlée.

## English

Draft.23 adds TS43-A01/A02/A03 using the prior agent-access-v1 profile. It reconciles
an **assessor-initiated test client**, its full HTTP chain and supplied server logs.
**C describes that client's treatment under the declared plan and its documented
trace, not actual operator access.** Denying an impersonating client can be the
intended outcome of identity enforcement. HTTP 200 establishes neither identity
nor expected content. No global SEO, security, actual visit or citation assurance.

A01 binds the exact full HTTP client to dated sources and a supplied review, checks
the attributable complete GET chain, then compares the response to the planned
test treatment. A bound review contradiction or contrary response fails. Missing
review/incomplete scope stays unknown; an independent HTTP contradiction survives
missing review. A02 requires one server-ID candidate per exchange in the declared
layer/time window and matching method, URL, full UA and status. Attributable
contradictions fail alongside other missing hops. ID alone, duplicates, stale cache
IDs, other layers or absent logs are inconclusive. A03 retains an execution receipt
and supplied bound attribution. Assessor tests remain tests with unverified
operator identity. A bound real-visit/verified-identity claim fails; missing or
unbound attribution is inconclusive. Even a matching provider IP does not turn an
assessor-initiated request into an operator visit.

No automatic atomic exemptions. Control-only tokens, spontaneous operator visits,
DNS/IP visitor-authentication methods and other evidence formats are unqualified
in this first reader, not proven absent or faulty. TS42/TS44 remain separate.

Captures 1/2 uses url, observed_at assessment, context (network/bounds/tool/version),
intent.declared_at and intent.agent_access. The plan contains reader; client with
operator, actor_kind crawler/user-action, product_token, full_user_agent and
source_ids; separate operator_access allow; and test_access with action allow/deny,
policy_basis ua-only/identity-gated/other, reason, exact status/final_url. The basis
is declared, not established by a single test. Allow qualifies HTTP 200 with a
prior complete expected_body_sha256; deny qualifies 401/403, with an optional body
hash imposing an exact reference too. Other conventions, variable content without
a fixed reference and interpreting a 200 challenge as denial remain unqualified.
A 200 whose body differs from the fixed reference is a contradiction.

Also declare 1–16 exact origins ending in /, log_layer, lowercase id_header,
window_start/end, integer clock_skew_ms 0–30000, max_duration_ms 1–60000 and
max_source_age_days 0–3660. The intent precedes a ≤24-hour window ending before
assessment. Every raw HTTP hop adds sent_at/received_at, ordered and within the
window and per-exchange duration. Origins must be declared. Existing HTTP bounds
apply: complete unconditional unauthenticated GET, exact Host/UA, no cookies or
Range, supported encodings and at most 20 hops. Cross-origin redirects are supported
when all origins and logs belong to the qualified declared scope.

client_documents retains unique referenced id, HTTP(S) source_url, acquisition
observed_at, exact UTF-8 raw_text and sha256. No credentials/whitespace/control
characters or invalid ports in source URLs. Age is the UTC calendar-date difference;
sources cannot be future-dated. Hashes bind bytes without authenticating sources.
client_review has reviewer, provenance, assistance, observed_at, reason,
full_user_agent supported/contradiction/unknown, binding_sha256. Date follows all
referenced acquisitions and precedes assessment. Binding includes the complete
client object and referenced documents' id/source_url/observed_at/sha256, in source
array order. Source keywords never substitute for a supplied semantic review.

logs uses reader tsep-request-log-v1, format native-jsonl, exact raw_jsonl/hash,
export observed_at, window_start/end, complete, origins and layer. The declared
complete window covers the planned window and ends before export/assessment.
Origin list/order and layer exactly match the plan; aggregation remains a supplied
reviewed claim. Converted JSONL, ordinary Apache/Nginx and unqualified provider
formats stay inconclusive. Each line contains request_id, request_at, method,
absolute url, user_agent, integer status and layer. Other fields, including peer
or forwarded addresses, are retained without identity inference. Duplicate JSON
keys, nonfinite values, blank/incomplete/invalid lines are inconclusive. Request
IDs use 1–80 ASCII alphanumeric/hyphen/underscore characters; methods use 1–20
uppercase ASCII letters.

log_review has the common review fields, binding_sha256, and explicitly true
server_generated_id, per_request_id, client_facing, clock_bound_confirmed, complete.
The supplied reviewer qualifies ID origin/per-response freshness, client-facing
layer, clock bound and export completeness. ID equality cannot establish these
properties. Review date follows export and the last exchange. Binding covers the
complete {url,intent,http,logs}. The response must contain one ID header, absent
from the request, and not reused across test hops. Find one ID candidate in the
specified layer, then enforce [sent_at−skew,received_at+skew] **before** comparing
fields. An old cached ID with another client is unestablished correlation, not
an attributable contradiction. A qualified record's differing method, literal URL,
UA or status fails. No matching line remains unknown even for a declared complete
export, without inferring a site outage; preserve other failures and gaps.

execution retains origin assessor-test, initiator, command argument list (never
executed by the reader), started_at/ended_at. It follows intent, contains all HTTP
intervals and precedes assessment. This supplied receipt does not authenticate
execution or a person. attribution retains common review fields, request_origin
assessor-test, operator_identity not-verified, claims_operator_visit false and a
binding over {url,intent,http,logs,execution}, using null for absent fields. It
follows execution and precedes assessment. A true operator-visit claim, verified
identity or operator origin contradicts the assessor-initiated test.

Bindings use SHA-256 over UTF-8 JSON with sorted keys, ensure_ascii=false and comma/
colon separators without spaces. Review provenance human/human-assisted or
synthetic-exercise must agree with bundle access. No missing review is created;
neither judgment nor identity is authenticated. Bounds: 64 source documents,
16 source references, 256 KiB/source, full printable ASCII UA 1–2048, token 1–128
ASCII letters/hyphens/underscores, logs ≤1 MiB/10000 lines, ≤128 command arguments,
nonempty ordinary strings ≤8192 characters and global 8 MiB input. Unsupported
inputs are unknown. All 71 frozen raw cases are synthetic. A separate prefrozen
loopback recipe supports controlled observed experiments, never actual operator visits.

## Provenance / Sources

This is an editorial TSEP evidence method, using the retained HTTP reader and
supplied operator sources. No built-in provider identity registry is added.
Méthode éditoriale ; aucun registre d’identité opérateur implicite.
[Research context](../provenance/agent-usage-policy-v1.json),
[migration](migration-draft.23.md).
