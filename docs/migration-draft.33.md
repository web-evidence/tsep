# Migration draft.32 → draft.33

## Français

Candidate locale du 13 octobre 2026. TS32 ajoute trois règles semiAuto pour le
registre préalable, les identifiants/références recalculés et les revues liées aux
exports JSON-LD. Voir le [contrat bilingue](structured-identity-evidence.md).
La candidate compte 17 contrôles outillés et 48 règles ; TS33 reste à développer.
Interpréteur 32, adaptateur 33, HTML 16 et rejeu 3.

Les 44 identifiants et les règles antérieures conservent leur sens et provenance.
Les références normatives suivent cette version ; les anciens rapports, tags et
archives ne sont pas remplacés. Draft.32 est une étape locale intermédiaire, dont
la vérification générale a échoué sur des raccordements de tests ; elle n'est pas
présentée comme paquet livré. La validation finale porte sur draft.33. Le kit TS08
draft.31 déjà fourni et le moteur épinglé de l'application restent inchangés.

Créer un **nouveau dossier TS32**, avec registre et revue antérieurs aux captures,
2–16 exports natifs, bases explicites, contextes locaux et revues liées. Le CLI
`adapters/captures.py` reçoit ce dossier ; les exemples `examples/captures/ts32-*`
sont exclusivement fictifs. Aucun formulaire d'import TS32 spécialisé ni collecte
automatique de pages n'est livré dans ce lot. Ne pas transformer un ancien export
isolé en plan préalable ni remplir automatiquement les jugements. Node 24 est
explicite ; un manque reste NT. C qualifie la cohérence documentaire du corpus,
jamais une stabilité temporelle ou une identité réelle authentifiée.

49 cas initiaux et 13 cas de limites ont été figés avant leur validation. Les
1 494 cas antérieurs restent inchangés ; les 62 ajouts sont chargés depuis deux
fichiers déclarés avec empreintes. Le chargeur n'accepte que des fichiers de tests
inventoriés, sans liens symboliques ni récursion : 16 fichiers maximum, 8 Mio par
fichier, 32 Mio cumulés et 10 000 cas. La limite générale des rapports reste 8 Mio.
Le corpus étendu compte 1 556 cas / 3 305 couples règle-cible. Les résultats réels
de vérification sont conservés séparément, sans prétention d'audit Edikka ou CI distante.

## English

Local candidate dated 13 October 2026. TS32 adds three semiAuto rules for the prior
registry, recomputed IDs/references and export-bound reviews. See the
[bilingual contract](structured-identity-evidence.md). Total: 17 tooled controls,
48 rules; TS33 remains pending. Interpreter32 / adapter33 / HTML16 / replay3.

All 44 IDs, previous rule meanings and provenance remain. Normative references
follow this version; previous reports, tags and archives retain exact versions.
Draft.32 was an intermediate local candidate whose general test integration failed,
not a delivered verified package. Final verification targets draft.33. The supplied
TS08 draft.31 kit and the application's pinned engine remain unchanged.

Create a **new TS32 dossier** with a registry and review preceding acquisition,
2–16 native exports, explicit bases, local contexts and bound reviews. The existing
capture-adapter CLI accepts it; `examples/captures/ts32-*` are fictional only. This
batch includes no specialized TS32 intake form or automatic page collection.
Do not retrofit prior intent or fabricate judgments from an old isolated export.
Explicit Node24 is required; gaps stay unknown. C qualifies documentary corpus
coherence, not temporal stability or authenticated real-world identity.

49 initial and13 boundary cases were frozen before validation. All1,494 earlier
cases remain;62 additions load from two explicit fingerprinted fixture files.
Only inventoried test files are accepted, without symlinks or recursive extensions:
at most16 files,8MiB each,32MiB aggregate and10,000 cases. General report limits stay
8MiB. The expanded corpus contains1,556 cases /3,305 pairs. Observed verification
is retained separately; no actual Edikka audit or remote CI is inferred.
