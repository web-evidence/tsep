# Report workflow / Parcours de rapport

## Français

Pour calculer les résultats à partir de captures structurées déjà fournies,
utiliser le [parcours captures → paquet](capture-adapter.md). Le parcours ci-dessous
enregistre les résultats explicitement fournis par l’évaluateur.

La CLI ne collecte aucune URL. `init` écrit sur stdout. `add-evidence` et `record`
mettent à jour **le rapport existant sur disque**, seulement après validation du
rapport et de toutes ses preuves ; conserver une copie avant réévaluation. En cas
d’échec, le fichier reste inchangé. `--evidence-root` vaut par défaut son répertoire.

Démonstration reproductible avec preuves et jugements synthétiques déjà fournis :

```sh
mkdir -p /tmp/tsep-demo
cp examples/pass/http.txt examples/pass/intent.txt /tmp/tsep-demo/
python3 tsep.py init --target https://example.com/page --controls TS01 \
  --assessor 'Demo author' --label 'One synthetic URL' \
  --selection-method 'Synthetic fixture only' > /tmp/tsep-demo/report.json
python3 tsep.py add-evidence /tmp/tsep-demo/report.json --id intent --path intent.txt \
  --kind intent --target https://example.com/page --observed-at 2026-10-09T10:00:00Z \
  --access synthetic --description 'Authored synthetic intent'
python3 tsep.py add-evidence /tmp/tsep-demo/report.json --id http --path http.txt \
  --kind http --target https://example.com/page --observed-at 2026-10-09T10:00:00Z \
  --access synthetic --description 'Authored synthetic exchange'
python3 tsep.py record /tmp/tsep-demo/report.json --control TS01 --status C \
  --reason 'Two authored passing judgments; synthetic TS01 only' \
  --procedure 'Replay supplied synthetic judgments, no live assessment' \
  --target https://example.com/page --evidence http --evidence intent \
  --atomic '{"rule_id":"TS01-A01","target":"https://example.com/page","outcome":"pass","reason":"Synthetic complete final 200","evidence_ids":["http","intent"]}' \
  --atomic '{"rule_id":"TS01-A02","target":"https://example.com/page","outcome":"pass","reason":"Synthetic URL and body digest match prior intent","evidence_ids":["http","intent"]}'
python3 tsep.py gate /tmp/tsep-demo/report.json --summary --lang fr
```

`add-evidence` et `record` affichent par défaut un reçu de deux lignes ; `--json`
rétablit le résumé structuré complet (décision, causes bloquantes et couverture).
Le rapport complet reste dans le fichier indiqué, jamais remplacé par ce reçu.

`add-evidence` calcule le SHA-256 du fichier local existant. Répéter `--target` pour
plusieurs cibles. IDs/chemins en doublon, preuve hors racine, empreinte modifiée,
date postérieure à l’émission ou rapport utilisé comme sa propre preuve sont refusés.
`--kind webmaster-tools` exige `--engine` ; Google seul satisfait la série normative
Search Console existante. `--access` explicite public/restricted/synthetic.

`record` remplace uniquement le contrôle sélectionné et son tableau atomique ;
aucune fusion implicite de constats anciens. Répéter `--evidence` et `--target`.
Deux modes exclusifs : répéter `--atomic` avec un objet JSON explicite par
règle/cible, comme ci-dessus, ou utiliser un fichier `--atomic-results` qui contient un tableau d’objets avec `rule_id`, `target`,
`outcome`, `reason`, `evidence_ids`. Aucun rattachement implicite de preuves. Omettre le tableau ne permet pas de déclarer C
sur TS01/07/10. `--state` vaut complete pour C/NC/NA, inconclusive pour NT ;
`--state not-started` exige l’absence de cibles évaluées, preuves et observations.

Pour un outil qui a réellement exécuté toutes les règles automatiques :
`init --mode automatic --tool NOM --tool-version VERSION` avec les autres arguments.
Le nom/version ne transforme pas des jugements manuels en mesure automatique.
`gate --summary` est lisible, `--lang fr` traduit son texte ; sans option, la sortie
reste JSON. Les codes de sortie restent identiques : GO 0, NO_GO 1,
INCOMPLETE/REVIEW 2, données invalides 64 (syntaxe CLI invalide : 2).

## English

To compute outcomes from supplied structured captures, use the
[captures → bundle workflow](capture-adapter.md). The workflow below records
outcomes explicitly supplied by the assessor.

The CLI never collects URLs. `init` writes stdout; `add-evidence` and `record`
update the existing report **in place** only after validating it and every artifact.
Retain earlier assessments before reassessment; failed edits leave the file intact.
The default evidence root is the report's directory. The commands above replay
supplied synthetic judgments; they are not automatic observations of a live site.
Use `--summary` without `--lang fr` for the English gate summary.

`add-evidence` and `record` print a two-line receipt by default; `--json` restores
the full structured summary, including decision, blocking causes and coverage.
The complete report remains in the named file; the receipt never replaces it.

`add-evidence` hashes an existing local file and records ID, relative path, kind,
repeated target, zoned observation date, access and description. Duplicate IDs/paths,
files outside the evidence root, changed hashes, future evidence and self-evidence
are rejected. `--kind webmaster-tools` requires `--engine`; only Google satisfies
the existing Search Console normative series. Access is explicit.

`record` replaces only the selected control and its entire atomic array, without
merging old findings. Repeat `--evidence` and `--target`. Either repeat `--atomic`
with one explicit JSON object per rule/target or supply an `--atomic-results` JSON
array file; these modes are mutually exclusive. Each object contains rule_id, target, outcome, reason, evidence_ids. Omitting it
cannot yield C on TS01/07/10. State defaults to complete for C/NC/NA, inconclusive
for NT. Evidence is never linked implicitly. Explicit not-started requires no evaluated targets, evidence or observations.

An implementation that actually executed all automatic rules can initialize with
`--mode automatic --tool NAME --tool-version VERSION` alongside required arguments.
Tool metadata does not turn manual judgments into automatic observations. Default
gate output remains JSON; `--summary` is readable. Exit codes are unchanged:
GO 0, NO_GO 1, INCOMPLETE/REVIEW 2, invalid data 64 (malformed CLI syntax: 2).
