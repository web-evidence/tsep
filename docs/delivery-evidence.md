# Delivery evidence / Preuves de diffusion — version 1 (draft.27)

## Français

Le profil `delivery-evidence-v1` de TS39 compare une matrice préalable de clients,
régions déclarées, appareils, négociation et cache à une politique explicite. Il
réutilise l’observateur HTTP/Vary 1 et les lecteurs TS07/TS10. Trois règles semiAuto :
A01 matrice/configuration et revue ; A02 signaux et contenu par cellule ; A03
attribution des contextes/mécanismes et des réutilisations du cache déclarées.
Une différence légitime n’est pas un défaut ; des octets identiques ne suffisent
pas à qualifier la langue, le contenu ou l’accès de Googlebot.

### Entrée et politique préalables

La cible captures usuelle contient URL de périmètre, observed_at, context (network,
bounds, tool, tool_version), intent.declared_at et un booléen delivery_synthetic.
intent.delivery contient reader, window_start/end, cells, pairs, mechanisms et
cache_checks. Fenêtre de 24 h maximum, close avant l’évaluation. Le plan précède
la fenêtre ; 1–32 cellules, 64 paires/checks maximum. Les mécanismes admis sont
negotiation, geolocation, cache, device, edge-routing. Aucun mécanisme absent n’est
inventé ; les exemptions de contrôle demandent un dossier positif distinct.

Chaque cellule reprend id, url, user_agent, request_fields, context_claims de
l’observateur, plus context_id, mode, expectation et seo_intent. Les dates et
empreintes sont fournies, pas authentifiées. Au moins une cellule représente une
page complète ; une cellule déclare explicitement Accept-Language absent. Ce
minimum ne prouve pas la représentativité, qui reste soumise à revue.

- mode representation : expectation a status 200, final_url, language et content
  (références textuelles non vides). seo_intent fixe les intentions natives TS07 et
  TS10, le client exact et la date préalable. Un seul membre canonical, l’URL de
  cette cellule, dans ce premier profil ; les relations entre variantes relèvent
  de la politique et des revues. Les profils source/rendu existants restent explicites.
- mode non-representation : status attendu 401/403/404/410/451, final_url, reason
  et accessible_via (autre cellule representation). Une revue doit justifier ce
  traitement et l’accès de la variante par l’autre cellule. Ce n’est jamais une
  dispense implicite d’accessibilité de Googlebot. seo_intent est vide.

delivery_configuration conserve raw_text UTF-8 (≤256 Kio), sha256, source_uri et
observed_at antérieur à la fenêtre. Ce texte peut être un export de configuration
et sa documentation associée ; le lecteur n’exécute ni ne devine sa sémantique.
delivery_plan_review lie {url,intent,delivery_configuration}, entre déclaration/
capture de configuration et début de fenêtre. Son jugement supported doit aussi
qualifier representative et operator_policy_supported. Cette dernière atteste la
politique d’accès de Googlebot sur les variantes déclarées, sans prétendre observer
une visite réelle. Une politique contradictoire revue donne fail ; absence = inconclusive.

### Captures et signaux — A02

delivery_observations conserve cell_id, http et native. Chaînes de 20 sauts maximum,
GET HTTP/1.1 bruts, datés et attribués comme dans l’observateur. Les champs natifs
supplémentaires servent aux revues, robots et rendus TS07/TS10. Leur url, intent,
http et context.id doivent correspondre exactement à la cellule/trace prévue.
Le document canonical principal possède exactement la même trace HTTP. Ses dates,
et celles des captures/rendus supplémentaires, restent dans la fenêtre.

Le statut et l’URL finale sont comparés à la politique. Un noindex HTTP complet
peut contredire une intention allow malgré un corps tronqué ; on ne reconstruit
pas une page complète pour lui faire réussir les autres tests. Pour les cellules
representation, TS07-A01, TS07-A02, TS07-A03 et TS10-A01 sont recalculés sur native.
Les inconnues restent inconnues. Seule l’exemption positive vérifiée TS07-A03 peut
satisfaire l’obligation de rendu ; son résultat natif not-applicable reste visible.
Les règles ne sont pas renommées « contrôles entièrement réussis ».

delivery_semantic_reviews contient une revue par cellule, liée à
{url,intent,cell,observation}. Après la capture et avant évaluation, elle confronte
language, content et accessibility à la politique (supported/contradiction/unknown).
Pour non-representation, seul accessibility est requis. Le corps doit être complet
pour qualifier ces jugements ; Content-Language n’est pas une preuve de la langue
du texte. L’accès par accessible_via exige une autre capture complète HTTP 200.
Une revue ne supprime jamais une contradiction native indépendante.

### Attribution et cache — A03

delivery_sources : 1–64 pièces id, source_uri, observed_at, raw_text, sha256,
≤256 Kio chacune. Une revue de contexte par cellule dans delivery_context_reviews
référence source_ids distincts et lie {url,intent,cell,observation,sources} avec les
pièces référencées dans leur ordre. Elle est postérieure aux pièces et à la capture.
context, mechanism et operator_policy sont des jugements séparés ; supported ne
qualifie que les pièces fournies. actual_context doit égaler context_claims pour
un jugement context supported. Toutes les captures sont des tests de l’évaluateur ;
claims_operator_visit doit rester false. User-Agent, IP déclarée, Age ou HIT seuls
n’authentifient jamais une région, un POP, une visite ou une action du cache.

Si cache figure dans mechanisms, au moins un cache_check est obligatoire. Un check
nomme id, stored_cell, served_cell, layer, clock_skew_ms (0–30000) et
transformation:"none". Il qualifie une réutilisation sans transformation ; d’autres
transformations nécessitent un profil explicite ultérieur. Les deux URL finales
sont identiques. Le Vary de la réponse stockée s’applique, jamais leur union.

delivery_cache_records fournit par check id, raw_jsonl, sha256, exported_at et review.
Ce premier format natif comporte exactement deux événements ordonnés store puis
serve. Chacun conserve event_id, kind, cell_id, entry_id, layer, at,
request_sha256, response_sha256 et body_sha256. Les octets et l’heure de chaque
événement sont liés à la réponse terminale correspondante ; entry_id et layer
concordent, store précède serve. Deux empreintes ou en-têtes HIT ne remplacent pas
ces événements. Ce journal fourni reste soumis à une revue de sa provenance réelle.

La revue du check référence source_ids (politique de fraîcheur et référence
qualifiées, origine du journal, couche et horloge) et lie
{url,intent,check,record,sources}, record sans sa revue. Après export et pièces,
elle qualifie linkage, clock, no_transform et freshness séparément. Attribution
absente : inconclusive, aucune accusation du cache. Après attribution qualifiée,
Vary nonmatching ou octets incompatibles avec l’entrée sans transformation donnent
fail. Vary matching/unconstrained ne suffit pas : freshness doit aussi être supported.
Une péremption conclue par revue exige référence, instant et politique associés ;
ETag/Last-Modified différents seuls ne la prouvent pas. Une contradiction Vary
établie survit à une fraîcheur inconnue. Aucune implémentation générale de cache,
de revalidation ou de stale-while-revalidate n’est prétendue.

### Revues, résultats et limites

Chaque revue conserve reviewer, assistance, reason, provenance
(human|human-assisted|synthetic-exercise), observed_at, binding_sha256 et complete.
Les liaisons utilisent JSON UTF-8 compact trié ; aucune identité de relecteur n’est
authentifiée. Les jeux fictifs et leurs revues imposent une livraison synthetic.
Un jugement supported ne remplace pas une pièce manquante. Des copies ambiguës,
cellules absentes/hors plan et données hors bornes restent visibles/inconclusives.

La taille totale d’une cible est bornée à 4 Mio. Chaque attendu conserve ses lignes :
fail prioritaire, sinon inconclusive pour toute lacune, sinon pass. Aucun NA atomique
automatique. C exige les trois règles et toutes les cellules déclarées, sans devenir
une mesure de l’ensemble des routes, POP, visiteurs ou dates. Les anciens contrôles
et leurs inconnues ne sont pas clos par ce résultat. Pas d’indexation, classement,
cloaking, adoption, vérité du contenu ou accès réel Googlebot déduit.

## English

`delivery-evidence-v1` assesses a prior delivery matrix against explicit policy:
A01 reviewed matrix/configuration; A02 status, native SEO signals and semantic
reviews; A03 attributed contexts/mechanisms and declared cache reuse. All three
are semiAuto. Legitimate variation is not failure; equal bytes are not proof of
language, content quality or Googlebot access.

The captures target has scope URL, observed_at, collection context, prior
intent.declared_at and delivery_synthetic. intent.delivery declares reader, a
closed ≤24-hour window, 1–32 cells, ≤64 pairs/cache checks and mechanisms from
negotiation/geolocation/cache/device/edge-routing. Each cell extends observer-1
fields with context_id, mode, expectation and seo_intent. At least one complete
representation and one explicitly absent Accept-Language case are required, but
do not themselves establish representative coverage.

representation expects status200, final_url and nonempty language/content
references, with exact prior native intent/client and a singleton canonical member
at the cell URL. non-representation expects401/403/404/410/451, final_url, reason,
accessible_via another representation cell, and empty seo_intent. It needs a bound
accessibility review and an observed complete200 route through that cell.

delivery_configuration retains raw_text, SHA-256, source_uri and a date before the
window. delivery_plan_review binds {url,intent,delivery_configuration} before
collection. supported also requires representative and operator_policy_supported:
reviewed policy must keep declared variants accessible to Googlebot. Test requests
do not establish an actual operator visit or authenticate a supplied policy.

delivery_observations retain cell_id/http/native, ≤20 raw GET HTTP/1.1 hops with
observer-1 chronology and attribution. Native url/intent/http/context.id must
match the declared cell; its singleton canonical document has the exact same HTTP.
Additional captures and rendered states remain within the window. Status/final URL
are compared directly; attributable HTTP noindex can contradict allow even when
the body is incomplete. Complete representation cells recalculate TS07-A01/A02/A03
and TS10-A01. Only a verified positive A03 rendering exemption can satisfy that
obligation while retaining its native not-applicable result. No underlying whole
control completion is inferred.

delivery_semantic_reviews bind {url,intent,cell,observation}, after capture and
before assessment. They judge language/content/accessibility separately against
prior expectation; only accessibility applies to non-representation. They require
a complete body. Content-Language is not proof of the actual text language.
Independent native failures survive missing semantic reviews.

delivery_sources retain1–64 id/source_uri/observed_at/raw_text/sha256 records,
each≤256KiB. delivery_context_reviews bind {url,intent,cell,observation,sources}
using ordered source_ids, after sources/capture. Context, mechanism and
operator_policy judgments remain distinct; supported context also requires exact
actual_context equality with the planned claims. Assessor tests must retain
claims_operator_visit:false. Supplied regions, IPs, User-Agent and Age/HIT headers
do not independently authenticate those facts.

Cache mechanisms require at least one declared check: id, stored_cell, served_cell,
layer, clock_skew_ms0–30000, transformation:none. Same final URI is required.
delivery_cache_records retain id/raw_jsonl/sha256/exported_at/review. The first
native JSONL profile has exactly store then serve events, each with unique event_id,
kind, cell_id, entry_id, layer, at and terminal request/response/decoded-body hashes.
Entry/layer agree and ordered event times match the corresponding HTTP intervals
within prior clock uncertainty. These records are supplied, not self-authenticating.

The cache review binds {url,intent,check,record,sources}, record without review,
after export/sources. source_ids retain qualified policy/reference, journal layer
and clock evidence. linkage/clock/no_transform/freshness judgments are separate.
Without attributable linkage there is no accusation of cache behavior. With
qualified linkage, stored-side Vary nonmatching or incompatible bytes under the
no-transform policy fail. matching/unconstrained alone cannot pass: freshness
must also be supported. A validator difference alone never establishes staleness.
Independent Vary failure survives unknown freshness. No general cache simulator,
revalidation or stale-while-revalidate implementation is claimed.

Reviews retain reviewer, assistance, reason, provenance human/human-assisted/
synthetic-exercise, observed_at, binding_sha256 and complete. Bindings are sorted
compact UTF-8 JSON. Missing, ambiguous or unbound evidence stays inconclusive;
fictional reviews/inputs require synthetic delivery. Total target≤4MiB.
Each rule retains all its rows: any failure wins, otherwise gaps are inconclusive,
otherwise pass. No automatic atomic NA. C needs all three rules and declared cells;
it proves neither whole-site/POP coverage nor actual Googlebot access, indexing,
ranking, cloaking, adoption or content truth. Native reader boundaries and missing
optional runtimes stay explicit. Provider-specific logs need qualified adapters.
