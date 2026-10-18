# Supplied evidence dossier v1 / Dossier de preuves fourni v1

Normative for the new rules that explicitly select this profile, from
0.3.0-draft.2. Existing readers and rules are unchanged.
Normatif uniquement pour les nouvelles règles sélectionnant ce profil, dès
0.3.0-draft.2. Les lecteurs et règles existants restent inchangés.

## Français

Une cible porte `url`, `observed_at`, `context` (id, tool, tool_version, bounds),
`intent.declared_at`, le client HTTP exact `intent.crawler` et les plans sous
`intent.evidence_checks[TSxx]`. Un plan possède reader, scope_reason et 1–32 items
avec id unique (128 octets maximum). Les pièces se trouvent sous
`evidence_checks[TSxx]` : synthetic booléen explicite, records, documents et reviews
(trois listes requises, 128 éléments maximum chacune). La taille du dossier est
bornée à 8 Mio. Aucune découverte implicite, interprétation de verdict importé,
collecte ni exécution de commande présente dans une pièce.

Un record contient id, kind, observed_at, context_id, native. Ce dernier a exactement
raw_base64, sha256, encoding, complete : base64 canonique des octets originaux,
SHA-256 exact, encoding identity, complete true pour une interprétation positive.
Le lecteur d'intégrité historique des fichiers sitemap est réutilisé sans changer
son comportement. Un original présent corrompu est un refus technique, distinct
de NT. Un record absent, incomplet, compressé ou dépassant 1 Mio est indéterminé.
Le JSON est UTF-8, avec format explicite ; clés dupliquées et nombres non finis
sont refusés par la lecture, sans réparation ni conclusion d'absence.

Un document contient url, observed_at, context_id et http : 1–12 échanges natifs
au format historique. Le lecteur HTTP existant contrôle requête, client, réponse,
complétude, URL et redirections. Le corps utilisé est limité à 1 Mio. La lecture
HTML source réutilise le sous-ensemble strict historique `canonical.html` ; elle
n'émule pas un navigateur et ne récupère pas les contextes non pris en charge.
Les originaux restent conservés même lorsqu'ils ne sont pas interprétables.

Toutes les pièces portent le même context_id que la cible et sont datées entre
la déclaration du plan et l'évaluation. Les dates sont fournies, non authentifiées.
Une review identifie subject=`TSxx-Ayy:item_id`, reviewer, reason, judgment
(supported ou contradicted), reviewed_at, provenance et binding_sha256. Elle est
bornée à 32 Kio ; reviewer/reason sont non blancs et limités à 8 192 octets UTF-8.
Sa date suit **toutes** les pièces records/documents liées et précède l'évaluation.
Provenance vaut synthetic-exercise pour un dossier synthétique, sinon human ou
human-assisted. Aucune revue produite par le lecteur.

L'empreinte de revue est SHA-256 du JSON UTF-8 canonique (clés triées,
ensure_ascii=false, séparateurs virgule/deux-points sans espaces, nombres finis)
de `{target:url, observed_at, intent, context, control:TSxx, evidence:dossier_sans_reviews}`.
Les empreintes lient les pièces sans authentifier acquisition, dates, contenu ou
identité humaine. Une revue contradictoire ne produit fail que si ses préalables
natifs sont qualifiés ; elle ne résout pas une preuve manquante. Une contradiction
native indépendante survit aux autres inconnues.

Pour une règle : tout fail qualifié entraîne fail ; sinon toute inconnue ou
population vide entraîne inconclusive ; sinon pass. Aucune NA atomique. Le rapport
exige toutes les règles/cibles avant C, préserve NC malgré les lacunes et produit
NT pour les preuves insuffisantes. Il garde les types réellement fournis, sans
inventer une preuve absente. Les documents sources peuvent servir de contenu ou
de corpus de liens explicitement étiqueté ; cela ne prétend pas à un crawl réel.
Le transport refuse de réétiqueter un dossier ou une revue synthétique comme réel.

## English

A target supplies url, observed_at, context (id, tool, tool_version, bounds),
intent.declared_at, exact HTTP intent.crawler and plans under
intent.evidence_checks[TSxx]. Each plan has reader, scope_reason and1–32 items with
unique IDs of at most128 bytes. Evidence lives under evidence_checks[TSxx]: explicit
boolean synthetic plus required records, documents and reviews lists, each bounded
to128 entries. Dossiers are limited to8MiB. No implicit discovery, acceptance of
imported verdicts, collection or execution of commands found in evidence.

Records contain id, kind, observed_at, context_id and native. The latter has exactly
raw_base64, sha256, encoding, complete: canonical original-byte base64, exact SHA-256,
identity encoding and complete=true for positive interpretation. The unchanged
historical sitemap original-byte integrity reader is reused. A corrupt present
original is a technical refusal, distinct from NT. Missing, incomplete, compressed
or over1MiB evidence is inconclusive. JSON must be UTF-8 with an explicit format;
duplicate keys and nonfinite values cannot be repaired into an absence conclusion.

Documents contain url, observed_at, context_id and1–12 historical native HTTP
exchanges. The existing HTTP reader checks request/client/response/completeness/URL
and redirects. Used body is bounded to1MiB. Source HTML reuses strict historical
canonical.html; it does not emulate a browser or recover unsupported contexts.
Originals remain retained even when uninterpretable.

Every record/document shares the target context_id and is dated between prior
plan declaration and assessment. Supplied dates are not authenticated. Reviews
contain subject=TSxx-Ayy:item_id, reviewer, reason, judgment (supported/contradicted),
reviewed_at, provenance and binding_sha256. Reviews are bounded to32KiB, reviewer
and reason to8192 nonblank UTF-8 bytes each. Review date follows **all** bound
records/documents and precedes assessment. Provenance is synthetic-exercise for
synthetic dossiers, otherwise human/human-assisted. No reviewer judgment is generated.

The review fingerprint is SHA-256 of canonical UTF-8 JSON (sorted keys,
ensure_ascii=false, compact comma/colon separators, finite numbers) for
{target:url, observed_at, intent, context, control:TSxx, evidence:dossier_without_reviews}.
Hashes bind evidence without authenticating acquisition, dates, content or humans.
A contradictory review yields fail only with qualified native prerequisites;
it cannot resolve missing evidence. Independent native failures survive other gaps.

Any qualified fail dominates; otherwise any unknown or empty population is
inconclusive; otherwise pass. No atomic NA. Reports require all rule/target pairs
for C, retain NC despite gaps and use NT for insufficient evidence. Export keeps
actually supplied evidence kinds and never creates missing proof. Source documents
may form explicitly labeled content or internal-link corpora without claiming a
real crawl. Transport refuses relabeling synthetic dossiers/reviews as real.
