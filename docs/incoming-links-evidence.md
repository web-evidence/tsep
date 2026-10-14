# TS16 — supplied incoming links / liens entrants fournis

Profile `incoming-document-links-v1`, proposed draft.37 / interpreter36 /
adapter38 / HTML21 / replay3. One atomic rule, TS16-A01. Source is prepared
separately; observed qualification and application delivery require separate receipts.

## Français

Population préalable de pages importantes et de sources internes fournie, datée et bornée. Le caractère important et la complétude du choix sont déclarés, non authentifiés.

Pour chaque destination importante, au moins un témoin a/href résoluble provenant d’un autre document interne qualifié, dans la source HTML ou un DOM déclaré sans interaction. Les originaux de la source et de la destination sont conservés.

Un témoin indépendant qualifié suffit pour cette destination ; une autre source inconnue ne l’annule pas. Chaque destination doit néanmoins disposer de son original HTTP qualifié.

Fail seulement si toutes les surfaces éligibles de toutes les sources de l’inventaire préalable sont qualifiées et ne fournissent aucun témoin pour une destination. Le résultat nomme cette population, sans qualifier la page d’orpheline du site. Une absence ainsi établie reste fail si l’original de destination manque : afficher conjointement cette absence, l’original/statut non archivés et l’identité de la destination non vérifiée. Cela peut révéler une erreur de plan, sans prouver un défaut du site.

Sans plan/inventaire qualifié, original de destination, témoin ou preuve bornée d’absence, résultat indéterminé. Aucune NA automatique. Un fail indépendant déjà établi survit aux autres destinations inconnues.

Sans interaction est une déclaration du fournisseur, pas une navigation observée. Un état après interaction ou non classé reste diagnostic ; il ne crée pas de témoin dans ce profil. Le profil ne décrit pas le comportement universel des robots.

Aucune exhaustivité du site, authenticité, interaction observée, visibilité, importance éditoriale, qualité d’ancre, suivi effectif de lien, visite Google, indexation ou classement. Un statut404 conservé ne devient pas à lui seul un défaut TS16.

Une destination demandée distincte dont la chaîne archivée retourne au document source ne fournit pas de témoin qualifié pour cette paire. Cette paire reste indéterminée ; une autre source indépendante peut suffire. Dates, URL demandées/finales et chaîne sont conservées.

## English

Prior supplied, dated and bounded important-page and internal-source populations. Importance and selection completeness are declared, not authenticated.

Each important destination has at least one resolvable a/href witness from a distinct qualified internal document, in source HTML or provider-declared no-interaction DOM. Original source and destination evidence is retained.

One independently qualified witness suffices for that destination; another unknown source does not negate it. Every destination still requires its qualified original HTTP evidence.

Fail only when all eligible surfaces of every prior inventory source are qualified and none provides a witness for a destination. Name that bounded population, without declaring a site-wide orphan. Such established absence remains fail if the destination original is missing: display bounded absence together with unarchived destination/status and unverified destination identity. This may reveal a plan error without proving a site defect.

Without a qualified plan/inventory, destination original, witness or bounded absence proof, remain inconclusive. No automatic NA. An independently established failure survives other unknown destinations.

No-interaction is a provider declaration, not observed navigation. After-interaction or unclassified states remain diagnostic and cannot provide a witness in this profile. This profile does not describe universal crawler behavior.

No site completeness, authenticity, observed interaction, visibility, editorial importance, anchor quality, actual link following, Google visit, indexing or ranking. Retained404 status is not by itself a TS16 defect.

A distinct requested destination whose archived chain returns to this source document supplies no qualified witness for that pair. The pair remains inconclusive; another independent source may suffice. Dates, requested/final URLs and chains are retained.

## Input contract / Contrat d’entrée

**envelope** — Existing input_version2, explicit rules and targets; target.url identifies the scope entry document, not necessarily every destination.

**provenance** — Boolean incoming_links_synthetic plus existing named context; retain this flag even if the plan is absent. App synthetic evidence is explicit; human reviews are never generated.

**prior_plan** — intent.crawler, declared_at and intent.incoming_links {reader, origin, selection_reason, inventory_sha256, window_start, window_end, max_duration_ms, sources, destinations}.

**inventory** — Original UTF-8 line-delimited source URL inventory; bytes/base64/hash and supplied observed_at retained. Exact one URL per line; optional final newline only, no comments, blank rows or silent normalization. Its ordered URLs must match prior sources. Missing/ambiguous evidence remains unknown; corrupt transport bytes are refused.

**sources** — 1–16 distinct {url,final_url,states} entries. states declares1–16 {id,browser,browser_version,scenario,interaction} per source; at least one no-interaction state per source; at most64 declared states over all sources. after-interaction states remain diagnostic.

**destinations** — 1–32 distinct {url,reason} important destinations; reasons supplied before capture. Source and destination populations may intersect; self-document links never witness an incoming link.

**documents** — incoming_links.documents contains at most48 unique {url,http,render} records for the union of source and destination URLs. Records shared by both roles keep one original. Missing records are not synthesized. Extra/duplicate records remain explicit and cannot supply an unplanned witness.

**http** — Existing native original request/response transport2,1–16 complete trace exchanges per document, named client, exact URLs and chronology. Source final200 required for HTML/DOM reading. Destination complete terminal HTTP result is retained as evidence;404 may coexist with a qualifying witness. Unfinished redirect/304/partial evidence cannot substitute an original representation.

**dom** — Existing structured_dom2 with exact HTTP/client association and acquisition provenance; no serialized HTML replacement. Actual state id/browser/version/interaction declarations must match prior state. No-interaction qualification remains documentary.

**bounds** — Entire input<=8MiB; inventory<=131072bytes; source/DOM existing bounded readers apply. Inventory observed_at<=plan declared_at<=window_start<=window_end<=observed_at; each qualified capture inside window, window<=24h. Per-exchange duration0..max_duration_ms with integer bound1..30000.

**url** — Exact WHATWG pre-serialized credential/fragment-free HTTP(S). Same serialized origin only; no registrable-domain inference. Source requested/final and destination requested/final remain within origin. Resolve a/href and remove fragment only; query/canonical/redirect alternatives are not equivalent. A destination capture that ends at this source final URL makes the literal non-self URL pair inconclusive, not a witness; another independent source may satisfy the destination. Keep requested/final URLs, chain and dates, without global equivalence.

## Français — structure, transport et limites précises

Entrée2 : rules et targets ; chaque cible contient url, observed_at,
incoming_links_synthetic booléen, context(network,bounds,tool,tool_version),
intent.crawler et intent.declared_at. intent.incoming_links contient reader,
origin, selection_reason, inventory_sha256, window_start, window_end,
max_duration_ms, sources et destinations. L’inventaire original UTF-8 contient une
URL de source par ligne dans l’ordre du plan ; seul un LF final est facultatif.
Aucun commentaire, BOM, doublon, ligne vide ou normalisation silencieuse.
Conserver label, base64 canonique, sha256 et observed_at. L’inventaire précède ou
égale le plan ; le plan précède ou égale la fenêtre des captures, au plus24h,
terminée avant observed_at de la cible. Durée d’échange bornée0..max_duration_ms,
entier1..30000.

Sources :1–16 objets {url,final_url,states}, avec1–16 états par source et64 au total.
Chaque état préalable est {id,browser,browser_version,scenario,interaction},
interaction valant none ou after-interaction ; au moins un none par source.
Destinations :1–32 objets {url,reason} distincts. Les deux populations peuvent
partager un document ; le conserver une fois. incoming_links.documents contient
au plus48 objets {url,http,render}. Un document dupliqué ne devient pas un témoin ;
une source supplémentaire non prévue ne modifie pas le plan. Les états après
interaction restent diagnostiques. Aucune interaction réelle n’est authentifiée.

Les URL demandées et finales doivent déjà égaler leur sérialisation WHATWG,
HTTP(S), sans identifiants ni fragments, avec la même origine exacte que le plan.
La source finale doit être le200 complet attendu. Conserver1–16 échanges natifs,
leurs octets, dates et agent. Une redirection inachevée, une304 ou une206 ne
constitue pas l’original terminal exigé. Le statut terminal d’une destination
peut être404 sans créer, à lui seul, un défaut TS16. Aucun diagnostic de soft404
n’est déduit d’un200 ni de son contenu.

Un a/href HTML du document principal doit résoudre exactement la destination
après retrait du fragment seulement. Aucune équivalence canonical, redirection,
barre finale, casse ou requête n’est ajoutée. Source : les deux hypothèses statiques
doivent être qualifiées et s’accorder pour cette destination ; leur désaccord sur
une autre destination n’efface pas ce témoin. DOM : snapshot original v2,
auto-empreinte, support, identité d’état et association HTTP/client qualifiés.
Une base active, un contexte étranger/shadow non qualifié, une récupération de
parsing ou une preuve incomplète reste inconclusive pour la surface. Une autre
surface indépendante qualifiée peut néanmoins fournir le témoin.

L’import vérifie les auto-empreintes fournies de l’inventaire, de chaque snapshot
et de ses supports textuels, y compris documents/états non prévus ou plan absent.
Un conteneur HTTP non nul est une liste d’objets ; conteneur invalide, base64
invalide/excessif/non canonique ou auto-empreinte incohérente est refusé
techniquement avant tout rapport réussi. Aucune empreinte n’est réparée. Champ
absent/nul et association sémantique différente restent des preuves insuffisantes
pour le lecteur, jamais une preuve de conformité. Les octets d’entrée et pièces
imbriquées sont conservés sans inventer une capture HTTP de la cible de périmètre.

Entrée JSON<=8Mio, inventaire<=131072octets, lecteurs source/DOM bornés existants,
Node24 explicitement sélectionné. Aucune collecte réseau. Un diagnostic calculé
au-delà de4Mio rend le profil inconclusive plutôt que de tronquer une conclusion.
Les limites du site, l’authenticité, l’importance et la qualité éditoriale, la
visibilité, le suivi effectif des liens et l’indexation restent hors preuve.

## English — additional intake and reading boundaries

Two qualified static scripting hypotheses must agree for the particular destination;
unrelated destination disagreement does not erase its independent witness.
Qualified v2 DOM states retain their original snapshot, self-digest, support,
state identity and HTTP/client association. Active base, unsupported foreign/shadow
context, parse recovery and incomplete evidence leave that surface inconclusive.
Another independent qualified surface may still witness presence. HTTP200 never
establishes semantic page validity or excludes a soft404.

Check supplied inventory, every snapshot and textual support self-digests before
interpretation, including unplanned documents/states and missing plans. Non-null
HTTP is a list of objects. Malformed/excessive/noncanonical byte containers or
inconsistent self-digests refuse transport, with no successful report. Never repair
a hash. Missing/null fields or different semantic associations remain evidence
qualification concerns, not conformity. Preserve original input/nested pieces;
never invent top-level HTTP for the scope target. Explicit Node24, existing bounded
source/DOM readers and8MiB input apply. Diagnostics above4MiB make the profile
inconclusive instead of truncating a conclusion. No external acquisition occurs.

## Review and migration / Revue et migration

Existing dated public references are retained in
`research/essential-links-2026-10-14/provenance.json`. They explain technical HTML
links/URLs, not approval of this profile. Claude’s method comments were proposals,
not human approvals or executed tests. Synthetic cases stay marked. TS01–TS44,
upstream provenance and previously delivered tools remain preserved.
See migration-draft.37.md for explicit new-dossier migration. This candidate is
not a certification, recognized standard, whole-site or global conformity claim.

FR : références publiques datées déjà conservées pour TS17 ; aucune nouvelle
observation d’un tiers ou approbation ne découle de ce profil. Commentaires de
Claude = propositions, pas tests exécutés ni approbation humaine. Cas synthétiques
marqués ; TS01–TS44, provenance et livraisons antérieures conservés. Migration
explicite dans un nouveau dossier ; aucune certification ou conformité globale.

## Source identity boundary / Limite d’identité de la source

FR : l’identité du contenu attendu de la source n’est pas évaluée par TS16. Une
page d’erreur répondant HTTP200 peut fournir un témoin de navigation qualifié ;
le lecteur ne détecte pas les soft404. Le rapport conserve explicitement cette
limite. Une éventuelle vérification d’identité appartient à un autre contrôle et
ne doit pas être inventée à partir du seul statut HTTP ou du texte de la page.

EN: TS16 does not assess expected source-content identity. An HTTP200 error
template can supply a qualified navigation witness; the reader does not detect
soft404s. The report explicitly retains this limitation. Any source identity
assessment belongs to another control and is not inferred from HTTP status or
page text alone.

## Conditional DOM evidence / Preuve DOM conditionnelle

FR : les entrées communes obligatoires sont HTTP, HTML source, inventaire et
intention. Le plan nomme les états requis ; le DOM original reste conditionnel
à la surface utilisée. Un témoin HTML source indépendant peut établir pass sans
DOM fourni. Son absence reste conservée, aucun artefact render n’est inventé.
En revanche, conclure à une absence bornée exige toutes les surfaces éligibles
prévues ; un DOM manquant sans témoin indépendant laisse inconclusive.

EN: Common required inputs are HTTP, source HTML, inventory and intent. The plan
names required states; original DOM evidence is conditional on the surface used.
An independent source HTML witness can establish pass without supplied DOM. Its
absence is retained; no render artifact is invented. Bounded absence still
requires every planned eligible surface; missing DOM without an independent
witness remains inconclusive.
