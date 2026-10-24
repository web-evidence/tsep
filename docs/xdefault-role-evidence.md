# TS24 — rôle x-default fourni / supplied x-default role

Candidate `xdefault-role-v1`, draft.41, interpreter40, adapter41, HTML24,
replay3. One semi-automatic rule TS24-A01. These definitions are not a receipt
of full engine or application qualification.

## Français

Le groupe et les canaux sont déclarés avant les captures selon le contrat TS23.
TS24 relit ses observations natives et leurs originaux exacts ; il ne reprend
jamais le verdict global TS23 comme verdict de rôle. Une seule destination
x-default est attendue par la politique préalable du groupe. La politique
explicite si elle est requise, son rôle `selector` ou `default-variant`, la
variante assumée éventuelle, une exigence éventuelle de distinction des URL,
l’auteur fourni attendu pour la revue et la justification du contexte de requête.

Un contexte unique, fourni et motivé est traité : client exact, en-têtes
Accept-Language et Accept exacts ou explicitement absents. Seuls Host,
User-Agent, Accept-Language et Accept sont admis. Cookie, condition de cache,
autre en-tête, redirection ou contexte différent ne permettent pas de qualifier
cette requête. Aucun public représentatif, pays, géolocalisation ou traitement
de toutes les langues n’est déduit. Un choix motivé d’une langue du groupe
reste seulement ce contexte déclaré, pas une preuve des autres visiteurs.

La présence est lue séparément dans le canal principal prévu et dans le canal
secondaire, sans assembler des preuves d’absence. Les deux hypothèses HTML
doivent s’accorder. Une absence qualifiée de x-default dans un primaire requis
est une contradiction avec cette politique, même si le secondaire en contient.
Toute cible qualifiée différente de la destination unique prévue est une
contradiction de politique, sur la même page ou une autre, même si la bonne cible
est aussi présente. Plusieurs cibles empêchent une qualification positive du rôle
mais ne suppriment pas cette contradiction indépendante. Le conflit TS23 reste
visible séparément : réciprocité et politique de destination sont deux attentes
distinctes, sans comptage de défauts global ni copie aveugle de son NC. Les
occurrences strictement identiques sont idempotentes.

Une occurrence qualifiée de la cible prévue et un original complet de sa
requête exacte permettent d’examiner sa disponibilité dans ce seul contexte.
HTTP404/410 établissent un défaut borné ; HTTP200 permet de poursuivre la revue.
Les autres statuts, redirections et captures incomplètes restent indéterminés.
Une404 sans occurrence x-default qualifiée n’est pas un défaut TS24 déduit du
seul plan. HTTP200 ne détecte pas une page d’erreur ou soft404, ne prouve ni
identité du contenu ni qualité sémantique. Aucune heuristique de texte n’est utilisée.

Le rôle et le contenu dépendent d’une revue réellement fournie, datée après la
fenêtre et avant l’observation du dossier, liée aux originaux, au contexte, au
groupe, à la politique et aux deux lecteurs natifs identifiés. Elle ne prouve
pas l’identité de son auteur ni la validité de son raisonnement. L’outil ne
rédige pas cette revue. Le premier profil exige exactement une revue courante
de l’auteur nommé au préalable. Plusieurs revues sont conservées et signalées
comme contestées sans remplacement ; aucune préférence pour la plus récente.
Une revue favorable manquante ou non qualifiée ne produit pas C. Une revue de
défaut unique correctement liée peut produire NC malgré une autre page inconnue.
Un défaut natif indépendant reste NC si les revues sont contestées.

Une exigence explicite de destination distincte est contredite si la cible
x-default partage exactement l’URL d’une variante observée. Sans cette exigence,
une URL partagée ne révèle ni neutralité ni défaut sémantique. Le rôle
default-variant nomme une variante du plan dont l’URL égale exactement la cible.

C exige toutes les surfaces et le contexte qualifiés, une occurrence non ambiguë
de la cible attendue, son original200 et la revue fournie `consistent` liée.
NC exige une contradiction indépendante documentée ci-dessus. Sinon NT.
Aucune NA native, même pour une absence optionnelle ; aucun remplacement manuel
du verdict natif. Les dossiers manuels historiques restent séparés. Une preuve
manquante n’est jamais une preuve d’absence ou de non-applicabilité.

## English

The prior group and channels use the TS23 contract. TS24 consumes its native
observations and exact originals, never the whole TS23 verdict as its role
verdict. The prior policy names one expected x-default destination, whether it
is required, selector or default-variant role, optional declared variant,
explicit URL-distinctness requirement, supplied reviewer and request-context
rationale. Exact prior client, Accept-Language and Accept (or explicit absence)
define one motivated supplied context. Only Host, User-Agent, Accept-Language
and Accept are admitted. Cookies, cache conditions, other headers, redirects
or a differing context leave the request unqualified. No representative audience,
country, geolocation or coverage of all languages is inferred. An explicitly
motivated in-group language remains that context only.

Primary and secondary native annotations stay separate; two HTML hypotheses
must agree. Qualified absence in an expressly required primary channel is a
bounded policy contradiction, even if the secondary contains x-default. Any qualified target differing from the unique prior destination is a policy
contradiction, on the same or another page, even if the expected target is also
present. Multiple targets prevent positive role binding but cannot erase that
independent contradiction. TS23 reciprocity and the role destination policy are
separate expectations, with no global defect count or copied verdict. Repeated
identical occurrences are idempotent.

An unambiguous qualified occurrence of the expected destination plus its exact
complete original request permits context-specific availability assessment.
HTTP404/410 establish bounded failure; HTTP200 allows the supplied role review.
Other statuses, redirects and incomplete originals remain unknown. A404 with no
qualified x-default occurrence cannot be assigned to TS24 from policy alone.
HTTP200 does not detect error templates or soft404s or establish content identity
or semantic validity. No text heuristic is used.

Exactly one supplied review must match the prior named reviewer, fall after the
capture window and before dossier observation, and bind policy, group, context,
originals and the two identified native readers. Neither reviewer identity nor
reasoning is authenticated. No review is fabricated. Concurrent reviews remain
visible and contested without replacement; most-recent does not win. A missing
or unqualified favorable review never produces C. An independently bound single
role-defect review can produce NC despite another unknown source; independent
native failure survives disputed reviews. Explicit URL distinctness is contradicted
by an observed exact shared variant URL; absent that requirement, shared URLs
prove neither neutrality nor semantic failure. A default-variant role must name
an exact mapped variant at the policy destination.

C requires every relevant surface/context qualified, an unambiguous expected
occurrence, its original200 and one bound supplied consistent review. NC requires
an independently evidenced contradiction above; otherwise NT. No native NA,
including optional absence, and no manual override inside this profile. Historical
manual dossiers remain separate. Missing proof is not absence or non-applicability.

## Closed input / entrée fermée

Existing input_version2 envelope, rule TS24-A01 and targets. Each target retains
url, observed_at, named context, intent.crawler/declared_at, the exact
intent.hreflang plan, hreflang_documents and hreflang_unsupported_channels.
xdefault_synthetic and hreflang_synthetic are equal booleans.

intent.xdefault has exactly: reader=`xdefault-role-v1`, recorded_at (no later than
window_start), hreflang_plan_sha256, target, requirement=`required|optional`,
role=`selector|default-variant`, variant (code or null), distinct_from_variants
(boolean), reviewer, accept_language (string or null), accept (string or null),
context_reason (nonblank string). Named strings are bounded to4096 characters.
Target is an exact absolute credential/fragment-free WHATWG HTTP(S) URL in the
prior group. No URL equivalence or language-registry claim. Variant is null for
a selector; default-variant requires its prior exact URL and distinctness=false.

xdefault_reviews is a list of at most8 retained objects. For qualification one
object has exactly: subject=`x-default-role`, binding_sha256, reviewer, reviewed_at,
disposition=`consistent|defect|unresolved`, rationale (nonblank), synthetic(boolean).
Its binding hashes canonical UTF-8 JSON (sorted keys, no whitespace, literal
Unicode, no nonfinite numbers) containing profile, reader_sources, policy,
hreflang_plan, request_context, crawler, original_documents, unsupported_originals.
reader_sources fingerprints conformance/hreflang_native.py and
conformance/hreflang_reciprocity.py. The complete interpreting engine/runtime
identity is recorded separately in the dossier, export and replay receipt.

FR : les noms de champs ci-dessus font partie du format fermé. La revue porte
sur les pièces exactes et le choix de contexte motivé, pas sur des visiteurs
observés. Toute modification impose une nouvelle revue fournie explicitement ;
aucune empreinte n’est réparée pour conserver une ancienne approbation.

EN: changes require a newly supplied bound review; never repair a digest to keep
an old approval. A future observation is refused by capture intake using the real
clock, separately from the native rule's chronological qualification.

## Bounds, integrity and limits / bornes, intégrité et limites

Inherited prior group1–16pages,1–32mappings, at most48original records and128
annotations per channel/page; at most24h window, exact single unconditional GET,
duration<=30000ms. Total input<=8MiB and diagnostics<=4MiB; no truncated conclusion.
Present corrupted/malformed original transport is refused before interpretation,
including unsupported/unplanned pieces or absent policy. Missing/null pieces or
self-digests remain NT. No acquisition occurs. Explicit Node24 is required.

FR : les limites et inconnues de TS23 sont conservées pour les surfaces, sans
transformer son verdict entier en jugement TS24. DOM/sitemaps pertinents fournis
restent non examinés et empêchent C, sans effacer un défaut indépendant. Aucune
authenticité, traduction, exhaustivité du site, visite/indexation Google ou
conformité globale. Références techniques datées et capturées héritées de TS23 ;
les choix TSEP sont éditoriaux. Claude a proposé des contre-cas, sans approbation
humaine ni exécution de tests par lui. Scénarios synthétiques explicitement marqués.

EN: relevant supplied unsupported DOM/sitemaps prevent C without erasing an
independent failure. No authenticity, translation, site completeness, Google visit
or indexing, or global conformity is inferred. Dated captured technical references
are inherited from TS23; TSEP requirements are editorial choices. Claude supplied
method proposals, not human approval or executed tests. Synthetic cases are labeled.

## Public CLI boundary / frontière CLI publique

FR : `python3 -m conformance.evaluate` retourne des observations atomiques
brutes, pas un dossier ni une décision de livraison. Une provenance contradictoire
y reste inconclusive. La CLI publique de production de rapport,
`python3 -m adapters.captures --access synthetic ...`, exige la provenance
cohérente et refuse avec sortie64 avant toute création de dossier. Une application
doit utiliser cette admission et ne pas transformer la sortie brute en rapport.
EN: `python3 -m conformance.evaluate` emits raw atomic observations, not a report
or delivery decision. Contradictory provenance remains inconclusive there. The
public report CLI, `python3 -m adapters.captures --access synthetic ...`, refuses
inconsistent provenance with exit64 before any dossier is created. An app must use
that intake, never a direct promotion of raw observations.
