# TS23 — hreflang réciproque fourni / supplied reciprocal hreflang

Candidate `hreflang-reciprocity-v1`, draft.39, interpreter38, adapter40, HTML23,
replay3. This contract is separate from observed qualification results.

## Français

Le plan `intent.hreflang` précède les captures, donne une justification,
1–16 URL de pages distinctes et1–32 associations code–URL attendues, ainsi que
le canal principal `html` ou `http-link` pour chaque page. Toutes les URL de pages
sont présentes dans les associations ; plusieurs codes peuvent désigner la même
URL. La casse des codes est comparée en ASCII. Les codes sont des jetons bornés,
pas une validation du registre linguistique. `x-default` ne reçoit aucun jugement
de rôle. Les groupes entre domaines sont admis.

Les URL sont des HTTP(S) absolues, sans identifiant ni fragment, admises par le
runtime WHATWG explicite sans changement de sérialisation. Aucune équivalence
canonical, redirection, paramètres, casse du chemin ou barre finale n’est créée.
Une cible relative reste indéterminée dans ce profil fermé ; aucune résolution
implicite ne l’ajoute au groupe. Jusqu’à32 associations extérieures explicitement
exclues restent visibles hors évaluation ; un extra non prévu est indéterminé.

Chaque canal principal doit fournir le jeu attendu complet, auto-référence
comprise. Le canal secondaire ne le remplace ni ne le complète ; aucun assemblage
de listes partielles. Un conflit qualifié reste NC. Si seul le canal secondaire
contient le jeu complet, le diagnostic l’indique : l’écart concerne le mode
principal prévu, pas une absence universelle de hreflang. Une contradiction
indépendante reste NC malgré des inconnues ailleurs.

Les documents `hreflang_documents` gardent les requêtes/réponses HTTP originales
v2 en base64 canonique avec SHA256, leur complétude et dates. Un échange GET200
sans redirection par page, demandé=final, client égal au plan, au plus30000ms,
dans une fenêtre préalable de24h au maximum, close avant `observed_at`.
Un Content-Type unique est requis. Framing/gzip natifs sont décodés sans perte.
Les en-têtes Link peuvent qualifier un document non HTML, y compris PDF binaire ;
son corps n’est pas prétendu HTML. Les originaux et contextes ne sont pas authentifiés.

HTML exige UTF-8 explicitement déclaré. Les lecteurs inchangés d’éléments et du
préfixe head lisent les mêmes octets sous deux hypothèses statiques. Les link
admis sont directement dans le head avant sa fermeture explicite, en espace de
noms HTML, `rel` contenant seulement alternate (doublons identiques admis),
avec href/hreflang uniques. `alternate stylesheet` est une feuille de style,
pas une annotation linguistique. Commentaires, textes script et templates
ordinaires ne deviennent pas des annotations actives. Aucune exécution JavaScript.

La fermeture implicite directe du head par div, img, iframe ou texte non blanc
peut établir un placement dans body si les deux hypothèses concordent sans erreur
de parseur ; le token et sa position originale sont conservés. Une divergence
noscript reste inconnue. Réinsertion après fermeture explicite, ambiguïté
attributaire, contexte étranger et autres récupérations restent hors profil.
Le placement dans body est NC seulement pour un primaire HTML ; les liens non
admis du canal secondaire restent diagnostiques. Modificateurs media/type/as et
paramètres HTTP hors rel/hreflang (anchor compris) restent indéterminés.

Les canaux pertinents sitemap/DOM fournis dans `hreflang_unsupported_channels`
restent hors profil et empêchent C, sans effacer une contradiction indépendante.
Pas de collecte réseau. TS22 (codes/indexabilité/canonical) et TS24 (rôle x-default)
restent distincts. Aucun choix de variante Google, indexation, traduction ou
conformité globale n’est déduit.

## English

The earlier `intent.hreflang` plan supplies rationale,1–16 distinct page URLs,
1–32 expected code-to-URL mappings and a primary `html` or `http-link` channel for
each page. Every page appears in the mapping; several codes may share one URL.
Use ASCII code case folding, without language registry validation or x-default
role judgment. Cross-domain groups are allowed. Exact absolute credential-free,
fragment-free HTTP(S) WHATWG URLs only, without rewriting or inferred canonical,
redirect, path-case, slash or query equivalence. Relative targets are inconclusive,
never silently resolved. Up to32 explicit excluded outside mappings remain visible;
unplanned outside annotations are inconclusive.

Every primary channel supplies the complete expected set, including self references.
Secondary channels never replace or complete it. Qualified conflicts are failures;
a complete secondary set is explicitly shown when the primary is incomplete. This
is a prior-mode mismatch, not a claim of universal hreflang absence. Independent
qualified contradictions survive unrelated unknowns.

Original v2 HTTP request/response byte containers, SHA256, completeness and dates
are retained. One unconditional GET200 exchange per page, requested=final, no
redirect, exact prior client, at most30000ms within an earlier at-most24-hour window
ending before `observed_at`. One Content-Type is required. Native framing/gzip is
losslessly decoded. HTTP Link can qualify non-HTML documents including binary PDF
without treating their body as HTML. Acquisition/context authenticity is not proved.

HTML requires declared UTF-8; unchanged element and source-head observers bind the
same bytes under two static hypotheses. Admitted links are direct HTML head children
before explicit closure, with an alternate-only ASCII relation set and unambiguous
href/hreflang. Identical relation tokens are idempotent; alternate stylesheet is not
a language annotation. Comments, script text and ordinary templates are not active
annotations. No JavaScript execution is inferred.

Direct implicit head closure by div/img/iframe or non-whitespace text can establish
body placement when both hypotheses agree without parser errors; retain native
closure token and byte position. Noscript divergence remains unknown. Reinsertion
after explicit closure, ambiguous attributes, foreign context and other recovery are
outside admission. Body placement fails only an HTML primary; non-admitted secondary
body links are diagnostic. HTML media/type/as and HTTP parameters beyond rel/hreflang,
including anchor, remain inconclusive. Relevant supplied sitemap/DOM channels are
unsupported and prevent pass unless an independent failure is established.

## Bounds and integrity / bornes et intégrité

Up to48 retained document records,128 annotations per channel/page,8MiB input JSON,
4MiB diagnostics; no truncated conclusion. Every present original self-digest is
checked before the plan, including unplanned/unsupported supplied pieces. Broken
integrity is a technical refusal. Missing originals/digests remain inconclusive;
there is no automatic NA or fabricated review. Exact input originals remain in
export and offline replay. Explicit qualified consumer import and separate app
acceptance are required. Synthetic fixtures are never real-site evidence.

## Typed boundaries / frontières typées

FR : la position du champ détermine sa garde. Un enregistrement de document
non objet donne NT avec « structure documentaire non interprétable ». Un champ
`http` absent ou nul, une requête/réponse absente ou nulle, ou une auto-empreinte
absente restent NT. Une liste HTTP contenant un échange non objet, un conteneur
requête/réponse présent non objet, un base64 présent malformé ou une auto-empreinte
fausse sont des refus techniques sans rapport. Aucun verdict n’est fabriqué après
un refus. Les contrôles historiques conservent leurs contrats propres ; cette
version ne leur applique pas rétroactivement cette nouvelle garde.

EN: field position determines the guard. A non-object document record is NT with
“uninterpretable documentary record structure”. Missing/null HTTP, request or
response and missing self-digests remain NT. A non-object exchange within the HTTP
list, a present non-object request/response payload, malformed present base64 or
contradicted self-digest is a technical refusal without a report. Historical
controls retain their own contracts; this version does not silently migrate them.

FR/EN : un Link qualifié est comparé à la table du plan préalable, indépendamment
d’une lecture HTML inconnue / a qualified Link is compared with the prior mapping
table independently of an unknown HTML reading. Le rapport dit « contradiction
avec le plan », non un conflit entre lectures / the report describes a contradiction
with the plan, not an inferred conflict between readings. URL relative : non évaluée,
hors profil / relative URL: not evaluated, outside profile. Un secondaire complet
reste visible avec le motif d’écart au canal prévu / a complete secondary is explicitly
shown alongside the prior-channel mismatch.
