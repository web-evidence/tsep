# Migration vers draft.12 / Migration to draft.12

## Français

Draft.12 étend à TS04 la distinction déjà explicite pour TS07 entre le client
HTTP réel et la politique Googlebot interprétée. L'interpréteur passe à 12 et
l'adaptateur à 13. Le lecteur robots partagé reste en version 2 ; le format de
rapport reste 2. Les identifiants TS01–TS44 et les treize règles sont conservés.

Avant une nouvelle collecte TS04, déclarer `intent.directive_crawler: "googlebot"`,
le `crawler` réellement envoyé, et un `robots_policy` dont `product_token` est
`googlebot` sans distinction de casse. Le profil conserve ses bornes existantes.
La sélection du groupe robots utilise le produit déclaré, jamais celui du client
par repli. Les requêtes conservées doivent toujours porter le User-Agent réel.
Les contrôles TS04 et TS07 partagent la validation de cette déclaration.

Sans ce champ, les résultats historiques restent identiques, y compris le refus
d'un produit absent du User-Agent. Un champ présent nul, inconnu ou incohérent
rend l'interprétation de la politique indéterminée. Une contradiction HTTP
indépendante reste conservée. En mode explicite, un refus 401/403/429/5xx contraire
au plan est un échec **pour le client observé** ; aucun refus à Googlebot n'est
déduit. Le rapport distingue politique robots et accès HTTP. Les statuts 4xx du
fichier robots lui-même gardent la politique de leur profil, distincte de celle
des ressources attendues en 200.

L'adaptateur conserve la qualification du client dans le libellé du périmètre
et le motif TS04. Elle reste ainsi visible avec C/NC/NT, la décision `gate`,
le rapport HTML et le résultat de contrôle EARL, y compris après rejeu.

La matrice de ressources reste déclarée et non exhaustive par construction.
Une matrice dérivée de pages doit le dire ; un choix par un assistant n'est pas
une approbation du propriétaire. La revue humaine de TS04-A02 demeure obligatoire
pour établir son absence d'obstacle. Cette extension ne transforme pas des
revues absentes en réussite, ni des ressources observées en inventaire suffisant.

Conserver les anciennes captures, rapports, outils et archives. Ne pas ajouter
`directive_crawler` après coup à une ancienne intention pour obtenir une réussite.
Préparer une nouvelle intention puis de nouvelles observations ; un changement
de résultat entre les dossiers n'est pas, à lui seul, une correction du site.
Toute réévaluation rétrospective éventuelle doit être identifiée séparément et
ne peut prétendre que l'option a été déclarée avant les anciennes captures.

Les 383 cas antérieurs restent inchangés. Vingt-six cas synthétiques figés avant
code couvrent les groupes contradictoires client/Googlebot, champs absents ou
invalides, attribution des requêtes, refus HTTP, revues manquantes et sauts
intermédiaires/finals bloqués. Ce corpus ne vaut pas validation humaine ou moteur.
Aucun tag publié, ancienne archive ou source héritée n'est remplacé.

## English

Draft.12 extends TS07's explicit distinction between the actual HTTP client and
Googlebot policy to TS04. Interpreter 12, capture adapter 13, unchanged shared
robots reader 2 and report format 2; TS01–TS44 and thirteen rules are retained.

Before a new TS04 capture, declare `intent.directive_crawler: "googlebot"`, the
actual `crawler` User-Agent and an explicit `robots_policy` with case-insensitive
`googlebot` product token. Existing profile bounds remain. Select the declared
product group, never the client group as fallback. Captured requests must still
match the actual User-Agent. TS04 and TS07 share declaration validation.

Absent field preserves legacy outcomes, including a product missing from the
User-Agent. Null, unsupported or inconsistent values make policy interpretation
inconclusive. Independent HTTP contradictions are retained. A resource's
401/403/429/5xx contrary to the plan is a failure **for the observed client**,
not evidence of denial to Googlebot. Robots-file status policy remains separate
from the resource's declared terminal status. Results qualify both axes.

The adapter carries client scope in the report's scope label and TS04 reason,
keeping it visible with C/NC/NT, gate decisions, HTML and control-level EARL,
including after replay.

The resource matrix remains declared. Disclose derivation from page sources;
assistant authorship is not owner approval or an exhaustive inventory. Required
human reviews remain; the extension cannot establish access without them.
Retain earlier captures, reports, tools and archives. Do not add the field
retroactively to obtain success: declare a new intent before new observations.
Changed outcomes alone do not establish a site correction. Any retrospective
reassessment must be separate and cannot claim prior declaration of the new field.

All 383 earlier cases stay unchanged. Twenty-six prefrozen synthetic cases cover
opposing product/client groups, absent/invalid fields, request attribution,
HTTP denials, missing reviews and blocked intermediate/final hops. Tests do not
establish human or engine validation. Published tags, archives and upstream
sources remain untouched.
