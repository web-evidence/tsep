# Migration draft.16 — canonical source / source canonical

## Français

Interpréteur 16, adaptateur 17, rejeu 2 ; format de rapport 2, treize règles,
44 identités/provenances maintenues. Les versions atomiques se rattachent à la
nouvelle édition ; seule la portée source TS10-A01/A02 évolue ici.

Déclarer le lecteur dans intent.canonical.source_reader avant de nouvelles
captures et fournir Node 24 séparément. Lire [le contrat bilingue](source-canonical.md).
Sans sélection, les 488 anciennes entrées et sorties restent identiques. Valeur
inconnue/absente de runtime : inconclusive, pas NA ni repli favorable. TS10-A04
n'hérite pas de ce lecteur et conserve sa méthode de résolution antérieure.

Ne pas modifier une ancienne intention pour présenter un profil comme préalable.
Réserver les analyses des corps historiques à des dossiers rétrospectifs clairement
nommés. Pour rejouer un ancien dossier, utiliser ses outils originaux, dont les
empreintes restent conservées. Ne remplacer aucune archive publiée ni tag.
Les anciennes expériences de canonical rendue sont des politiques historiques :
la règle active structured-inventory-v2 traite déjà une canonical ordinaire hors
head comme fail, même de valeur égale. Aucun correctif rétroactif n'est nécessaire.

Les contrats détaillés source-directives.md et source-canonical.md entrent désormais
explicitement dans les empreintes normatives, en plus du schéma et des contrats
FR/EN. Le premier conserve ses clauses draft.15 ; cette édition répare leur absence
de la liste produite par maintain.py render, sans réécrire les éditions précédentes.
Le schéma porte l'identifiant de cette nouvelle édition. Les exemples sont régénérés
en dehors des sources avant comparaison. Toutes les revues, preuves de rendu et
restrictions de portée restent exigées ; pas de certification ni standard reconnu.

## English

Interpreter 16, adapter 17, replay 2 preserve report format 2, thirteen atomic rules
and 44 control identities/provenance. Rule versions bind the new edition; only
TS10-A01/A02 source coverage changes here. Declare the optional canonical source
reader before new captures and supply Node 24 separately. Absent selection preserves
all 488 historical inputs/computed results. Unsupported/null/unavailable profiles
remain inconclusive without fallback or NA. A04 resolution is not extended.

Never retrofit prior intent, replace published artifacts/tags or rewrite historical
outcomes. Historical-body interpretation must be labeled retrospective. Replay old
bundles with their original tools. Earlier rendered-canonical experiments differ
from active structured-inventory-v2, which already fails ordinary body canonical
even with the preferred href; no retroactive rule repair is implied.

Both detailed source policy contracts now explicitly enter normative fingerprints,
alongside the schema and FR/EN report contracts. Source-directives.md keeps its
draft.15 clauses; this edition fixes its omission from maintain.py render's list,
without modifying prior editions. The schema ID identifies the new edition.
All rendering/content reviews and scope limitations remain required. No recognized
standard, certification, whole-control conformity or Google behavior is inferred.
