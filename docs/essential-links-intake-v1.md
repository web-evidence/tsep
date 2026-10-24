# TS17 — DOM self-integrity at intake / intégrité propre du DOM à l’import

Capture adapter37; protocol draft.36 / interpreter35 / HTML20 / replay3 unchanged.
This is a distinct transport correction, not a new normative control or rule.
Twenty-two contradictory inputs were authored before the change. Observed test
results and the exact candidate/archive are recorded separately.

## Français

L’adaptateur36 pouvait produire un rapport NT pour un snapshot ou un contenu de
support dont l’auto-empreinte fournie était fausse. Ce comportement ne satisfaisait
pas l’engagement de refus des originaux corrompus. Les dossiers déjà créés et la
livraison36 restent conservés avec cette limite et avec leurs outils exacts.

L’adaptateur37 vérifie chaque état DOM fourni aux demandes TS17 avant
l’interprétation : s’il existe à la fois un snapshot non nul et son empreinte
non nulle, celle-ci doit égaler le SHA-256 de la sérialisation de liaison existante
(JSON trié, séparateurs compacts, UTF-8, ensure_ascii=false). Si un contenu de
support textuel et son empreinte non nulle existent, le SHA-256 porte sur les
octets UTF-8 exacts du contenu. Aucune empreinte n’est corrigée ou inventée.
Une valeur fournie incohérente, vide ou d’un mauvais type est refusée avec le motif
`TS17 DOM integrity`, sans rapport ni répertoire de livraison réussi.

La garde examine aussi les états non prévus et les demandes sans plan ou limitées
à une seule règle TS17. Une association HTTP/DOM inconnue ne masque pas une
corruption. L’intégrité des captures HTTP reste contrôlée avant leur évaluation.
Un plan, snapshot, contenu ou hash absent/nul reste une preuve insuffisante pour
le lecteur ; il n’est pas transformé en C/NA. Une association
`acquisition.http_sha256` différente ou manquante, ou un script de capture d’une
autre version, reste une qualification indéterminée. Une auto-empreinte cohérente
n’authentifie ni le fournisseur ni l’acquisition. Les règles natives et les autres
contrôles conservent leurs comportements historiques.

Migration : garder les dossiers/exports36 avec leur moteur36 exact. Pour37,
préparer un nouveau dossier depuis les originaux réellement disponibles ; ne pas
recalculer un hash pour dissimuler une incohérence et ne pas remplacer une archive
livrée. Une association sémantique différente reste visible. L’application reçoit
un nouvel import explicite de l’archive qualifiée ; aucun correctif vendor.

## English

Adapter36 could produce an NT report for a supplied snapshot or supporting text
whose self-digest was false. That did not meet the promised refusal of corrupted
originals. Existing36 dossiers and delivery remain retained with this limitation
and their exact historical tools.

Adapter37 checks every supplied DOM state for a TS17 request before interpretation.
When both a non-null snapshot and non-null declared digest exist, the digest must
equal SHA-256 of the existing binding serialization (sorted compact JSON, UTF-8,
ensure_ascii=false). A supplied text support content and non-null declared digest
must match its exact UTF-8 bytes. Never repair or invent a digest. Inconsistent,
empty or wrong-type supplied digests refuse with `TS17 DOM integrity`, without a
successful report or delivery directory.

The guard also checks unplanned states, missing plans and partial TS17 rule
requests. Unknown HTTP/DOM association cannot mask self-corruption; HTTP capture
integrity is also checked before interpretation. Missing/null plan, snapshot,
content or digest remains insufficient evidence for the reader, never C/NA.
Different/missing acquisition.http_sha256 or another capture-script version remains
an inconclusive qualification. Internally consistent hashes authenticate neither
provider nor acquisition. Native rules and other controls retain their old behavior.

Migration: preserve36 dossiers/exports and exact engines. For37 prepare a new
dossier from actually available originals; do not recompute hashes to hide an
inconsistency or replace delivered archives. Semantic association differences remain
visible. The app needs an explicitly received newly qualified source archive, not
a vendor patch. Test results are separate from this contract description.
