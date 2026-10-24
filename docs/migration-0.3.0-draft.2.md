# Migration 0.3.0-draft.1 → 0.3.0-draft.2

## Français

Préversion indépendante, non publiée. Le lot précédent TS12–TS18 reste au commit
c969f772ca0c490dafce529bf686c75787347426, issu de RC1
7b60c20e7ac572574f756ad92531e0c46f7b83e7. RC1 et ses tags/archives ne sont pas
remplacés. La finalisation RC1 est indépendante de ces travaux.

Ajout de TS09-A01, TS11-A01/A02, TS19-A01/A02, TS20-A01/A02 et TS38-A01/A02.
35 contrôles ont désormais des règles,79 règles au total ; neuf autres contrôles
restent à outiller. Les70 règles précédentes gardent exactement leurs objets et
versions :67 en0.2.0-rc.1, trois en0.3.0-draft.1. Titres, identités, provenance et
champs antérieurs des nouveaux contrôles sont conservés.

Créer un **nouveau** dossier selon [les formats](url-policy-evidence.md) et le
[contrat de preuves](evidence-dossier-v1.md). Déclarer le périmètre avant les pièces,
conserver les octets originaux, attribuer les dates et obtenir les revues liées.
Une ancienne mention C ne devient pas C selon ces règles par simple réétiquetage.
Réévaluer chaque règle/cible ; conserver le résultat historique. Une preuve
manquante donne NT ; une contradiction indépendante donne NC malgré les lacunes.
Le profil source-only-reviewed de TS11/TS38 ne qualifie pas les cas nécessitant
un rendu. Les choix humains restent fournis et non authentifiés.

Interpréteur48, adaptateur47 ; format de rapport/rejeu et HTML27 inchangés.
Les dérivés courants sont régénérés après examen du diff. La suite ajoute64 cas
bruts synthétiques figés,15 cas de méthode et des tests de transport/limites.
Le tuple CLI historique est conservé puis complété par19 cas représentatifs ;
un overlay inversible enregistre ce changement d’intégration. Les tests de
préservation évoluent seulement pour accepter les ajouts déclarés et vérifier
les70 objets de règle antérieurs. Aucun lecteur existant n’est réécrit.

Le correctif non normatif TS25 du commit7f3b0f0 précède ce lot ; il conserve
les19 recettes historiques et ajoute deux frontières calibrées au runtime réel.
Voir [la migration de test](ts25-runtime-test-portability.md). Les échecs et
résultats observés, empreintes d’archives et état Git sont consignés séparément.
Préparer une suite ou une CI ne prouve pas sa réussite. Aucune application, site,
publication, indexation, adoption ou reconnaissance internationale n’est déduite.

## English

Separate unpublished prerelease. TS12–TS18 remains at commit
c969f772ca0c490dafce529bf686c75787347426 from exact RC1
7b60c20e7ac572574f756ad92531e0c46f7b83e7. RC1 tags/archives are never replaced;
its finalization remains independent.

Adds TS09-A01, TS11-A01/A02, TS19-A01/A02, TS20-A01/A02 and TS38-A01/A02.
35 controls now have79 atomic rules; nine controls still await tooling. All70
previous rule objects and versions remain exact:67 at0.2.0-rc.1 and three
at0.3.0-draft.1. Existing titles, identities, provenance and other fields of the
newly tooled controls remain preserved.

Create a **new** dossier using the [formats](url-policy-evidence.md) and
[evidence contract](evidence-dossier-v1.md). Declare scope before observations,
retain original bytes, attribute dates and obtain bound reviews. Relabeling an
old C cannot establish new-rule C. Reassess each rule/target and keep historical
results. Missing evidence yields NT; independent contradictions yield NC despite
gaps. TS11/TS38 source-only-reviewed scope does not qualify render-dependent cases.
Human decisions remain supplied and unauthenticated.

Interpreter48, adapter47; report/replay format and HTML27 unchanged. Inspect
regenerated current derivatives. Adds64 frozen synthetic raw cases,15 method
cases and transport/boundary tests. The historical CLI tuple is retained and
extended with19 representative cases, recorded by a reversible integration
overlay. Preservation tests accommodate only declared additions and verify all70
prior rule objects. No existing reader is rewritten.

Non-normative TS25 commit7f3b0f0 precedes this batch, retaining19 historical recipes
and adding two actual-runtime boundaries; see [test migration](ts25-runtime-test-portability.md).
Observed failures/results, archive fingerprints and Git state are recorded
separately. Prepared tests or CI do not prove success. No application/site change,
publication, indexing, adoption or international recognition is inferred.
