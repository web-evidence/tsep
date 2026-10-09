# TSEP — règles de travail

Ce dépôt est la source de développement autonome de Technical SEO Evidence
Protocol. Le site Edikka est une intégration distincte, sans dépendance d’exécution.

## Préparation et périmètre

- Lire `docs/development.md`, le contrat concerné et `git status --short` avant une
  écriture. Préserver les changements préexistants. Utiliser `codex/` pour les
  branches de travail ; intégrer séquentiellement après vérification.
- Si `.tsep-local.json` existe, lire ses références de pilotage local : elles
  désignent le suivi de l’éditeur, sans ajouter de backlog concurrent. Ce fichier
  reste ignoré et n’entre jamais dans une distribution. Son absence ne bloque
  aucun contrôle, build ou contribution externe.
- Rattacher la mission au suivi autorisé par le propriétaire. À défaut de suivi
  accessible, consigner la limite dans la réponse ; ne pas inventer une validation
  ou un accès. Une issue publique servira de référence après ouverture du dépôt.
- Ne pas modifier un autre dépôt, publier, acheter un domaine, déposer un DOI ou
  contacter un tiers sans autorisation correspondant à cette action.

## Contrats et vérité des résultats

- Préserver TS01–TS44, leurs versions et leur provenance. Ne jamais présenter ce
  candidat comme une certification ou un standard reconnu.
- Une nouvelle règle précise applicabilité, entrée, attendu, preuve, hypothèses,
  résultat indéterminé et limites. Distinguer contrôle, test atomique et observation.
- Le manque de preuve ne devient ni C ni NA. Une sonde partielle n’autorise pas un
  C global. Ne pas inférer l’indexation, le classement ou l’adoption.
- Toute évolution normative exige FR/EN, version distincte, migration explicite
  et cas contradictoires. Aucun artefact publié ou tag ne doit être remplacé.
- Les captures et rapports synthétiques restent marqués comme tels. Les noms de
  relecteurs, contributeurs, adoptants et les chiffres doivent avoir une preuve.

## Sources, dérivés et livraison

- Source bilingue : `spec/protocol.json`. Contrats : `docs/contract.*.md` et schéma
  JSON. `docs/controls.*.md` et les exemples sont des dérivés contrôlés.
- `maintain.py render` réécrit les empreintes normatives et les pages générées ;
  `examples/replay.py` réécrit les exemples, sauf `--output-dir` explicite.
  Ne jamais les lancer pour masquer un échec sans analyser le diff.
- Vérification commune : `python3 scripts/verify.py`. Elle travaille dans des
  dossiers temporaires et refuse une modification des sources. Elle utilise un
  serveur HTTP sur 127.0.0.1 pour les cas de sonde, sans collecte externe.
- Ajouter explicitement les fichiers distribués dans `release-files.json`.
  Aucun parcours récursif de tout le dépôt pour construire une archive.
- Vérifier la reconstruction depuis l’archive, la propreté Git et les écarts
  avant intégration. La CI préparée ne remplace pas une exécution distante observée.
- Pour une observation tierce nouvelle, conserver URL, date, portée et capture
  datée/empreinte ou exception motivée dans la preuve de la mission. Le suivi local
  peut imposer son gabarit ; aucune dépendance Edikka dans l’outil livré.

Les preuves de recette décrivent des résultats ; elles ne deviennent pas un
second tableau de suivi. Conserver les limites et résultats défavorables.
