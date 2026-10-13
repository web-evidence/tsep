# TS08 — intégration applicative / application integration

Guide et répétition **non normatifs**, version 1, 2026-10-13.
Le contrat reste [inspection-evidence.md](inspection-evidence.md), avec
[l'import existant](search-console-acquisition.md). Aucun contrôle, statut,
lecteur ou version normative n'est ajouté. Ce lot reste sur draft.31 :
15 contrôles outillés et 42 règles, sans nouvelle publication déduite.

## Français

### Répartition

L'application possède la connexion Google, l'acquisition, les formulaires de
revue et le stockage privé. Le moteur consomme un dossier fourni : aucun jeton
Google ne lui est nécessaire. La mise en forme des écrans ne doit ni décider les
résultats à sa place, ni convertir une absence de preuve en succès. L'utilisateur
n'a pas à manipuler les fichiers JSON ; l'application les prépare et les conserve.

Le premier lot peut rester local, mono-utilisateur, une propriété et une petite
sélection de une à cinq URL. Tester au moins deux URL dans un même dossier.
La gestion de clients, la facturation, les scans planifiés et un crawl global
ne sont pas des prérequis. Le dossier reste indépendant de l'application et doit
pouvoir être rejoué sans compte Google.

### Frontière déjà exécutable

| Étape applicative | Pièce ou commande existante | Décision à préserver |
| --- | --- | --- |
| Déclarer le périmètre et l'objectif | Cible `plan.json`, profil `google-inspection-evidence-v1` | Source de l'objectif, connaissances antérieures, politique de fraîcheur |
| Confirmer le plan avant acquisition | `inspection_plan_review`, lié à `{url,intent}` | Vraie revue fournie, jamais créée par l'import |
| Interroger l'API | `request.json`, `response.json`, `manifest.json` | Corps exacts, statut HTTP, provenance et date réelle ; aucun secret |
| Préparer le dossier | `inspection_intake.py prepare` | Une inspection par URL sélectionnée ; revues initialement vides |
| Recueillir l'interprétation | Copie de `review-request.json` | Auteur, assistance, portée, explication et décision réellement fournis |
| Évaluer | `inspection_intake.py build` | Nouveau dossier ; statut du contrôle et résultats atomiques lus du rapport |
| Présenter et exporter | `tsep.py html`, dossier complet et `replay.py` | Données privées, inconnues, dates et versions visibles |

Exécuter les commandes avec une liste d'arguments et des chemins contrôlés par
l'application, jamais une chaîne shell construite depuis une URL ou un formulaire.
Les noms de scripts et le Python sélectionné sont fixes. Chaque processus possède
une limite de durée ; son code de sortie, stdout et stderr sont distincts.
Un échec technique produit un état d'échec applicatif, pas un rapport TSEP fabriqué.

```sh
python3 adapters/inspection_intake.py prepare /dossier/plan.json \
  --inspection /dossier/observation --output /dossier/intake-neuf
python3 adapters/inspection_intake.py build /dossier/intake-neuf \
  --reviews /dossier/revues-fournies.json --assessor 'Évaluateur déclaré' \
  --output /dossier/rapport-neuf
python3 tsep.py validate /dossier/rapport-neuf/report.json
python3 tsep.py html /dossier/rapport-neuf/report.json --lang fr \
  --output /dossier/rapport-fr-neuf.html
python3 adapters/replay.py /dossier/rapport-neuf --output /dossier/rejeu-neuf
```

Le code 0 de `build` signifie que le dossier a été produit, pas que TS08 est C.
Lire `results` et les `atomic_results` du rapport ; conserver C, NC, NT et leur
motif. Les refus d'import (JSON tronqué, mauvaise empreinte, membre omis) restent
des erreurs documentées de préparation. Ils ne sont pas des résultats NC.
Les champs manquants d'une réponse API lisible peuvent, eux, parvenir au lecteur
et conduire à NT. Garder les tentatives avant l'import ; ne pas inventer un corps
API quand aucun corps n'a été reçu. Une nouvelle tentative crée de nouvelles pièces.

### Version du moteur et interface

Une copie de développement de draft.31 contient TS08 ; le site public initial
utilisait draft.28. La version affichée sur le site n'est donc pas automatiquement
la version à intégrer. Figer un commit ou une archive avec son empreinte, les
sources et les versions de l'interpréteur, de l'adaptateur et de l'importateur.
Conserver le runtime Python. Une mise à jour du moteur demande une décision
explicite, un nouvel essai et un nouveau dossier ; pas de mise à jour automatique
du checkout utilisé pour des dossiers historiques.

Les mécanismes existants de `intake.json` et de rejeu vérifient leurs empreintes.
Le kit les exerce mais n'introduit pas un nouveau schéma de verrou concurrent.
Les rapports JSON gardent le format contractuel ; l'application peut avoir son
propre état de travail (connexion, acquisition partielle, revue à compléter).

Présenter séparément « état rapporté par Google » et « qualification du dossier
TS08 ». `PASS` de Google n'est pas C ; un `FAIL` de Google peut accompagner un
dossier C si le périmètre, les preuves et l'interprétation sont qualifiés.
La date d'interrogation et le dernier crawl rapporté restent deux dates distinctes.
L'inspection décrit la version indexée ; elle n'est pas un test live ni TS12.

### Kit de répétition

```sh
python3 scripts/inspection_app_check.py --output-dir /tmp/tsep-app-essai-neuf
```

Le parent doit exister et la destination doit être nouvelle. Le kit réutilise douze
scénarios du corpus TS08 figé, dont il contrôle l'empreinte, et compose un treizième
avec deux URL sélectionnées ; les attentes sont écrites dans le script.
Il **construit de nouveaux exemples fictifs**, avec des dates relatives
à une ancre enregistrée. Il préserve les écarts de temps et les cas de vieillesse,
recalcule les empreintes des nouvelles pièces et lie des revues explicitement
fictives. Il ne réécrit pas les fixtures historiques, les pièces réelles ou leurs
revues. Aucune fonction de rafraîchissement d'un dossier réel n'est livrée.

Le kit exécute réellement les CLI prepare, build, validate, HTML FR/EN et replay.
Les rapports, pièces natives, demandes de revue vides et revues fictives restent
disponibles pour construire et tester les écrans de l'application.
`rehearsal.json` conserve les attentes, résultats, versions, runtime et empreintes.
Chaque commande a son journal local. Un échec laisse le diagnostic et les pièces
déjà créées, sans déclarer le parcours réussi.

Les treize parcours couvrent dossier positif et négatif documenté, revue préalable
absente, interprétation absente, contradiction de verdict, crawl ancien, erreur
API 403, URL inconnue sans champs suffisants, contradiction indépendante malgré
un crawl ancien, confusion avec un état live, valeur API inconnue, acquisition
antérieure au plan et sélection de deux URL. Quatre essais supplémentaires
doivent refuser des octets modifiés, une URL sélectionnée omise, des revues liées
à une autre entrée et l'écrasement d'un import existant.

Le test associé simule aussi une horloge de création du rapport en 2040 pour
rejouer trois dossiers historiques : positif, crawl ancien et revue manquante.
Les conclusions et observations doivent rester identiques, car la fraîcheur
s'apprécie à la date d'observation conservée dans l'entrée. Il s'agit d'une
simulation d'horloge, sans observation future ni réactualisation des preuves.

### Ce qui reste à vérifier dans l'application

Cette répétition ne qualifie ni OAuth, ni les permissions réelles, les quotas,
le stockage des jetons, les appels réseau, les annulations, les délais serveur
ou les tentatives concurrentes. L'agent applicatif doit les tester dans son propre
projet et vérifier la documentation Google actuelle. Il faut notamment distinguer
la connexion réussie, l'accès à une propriété et la qualité des pièces reçues.
Les données de compte restent `restricted`, les exemples restent `synthetic`.
Ne pas utiliser les journaux complets du kit fictif comme modèle de journalisation
de secrets en production. Une véritable acquisition et une revue fournie restent
nécessaires pour un premier essai réel ; un kit vert ne remplace pas cet essai.

## English

Non-normative guide and rehearsal version 1. The normative TS08 contract and
existing intake workflow remain unchanged, at draft.31 (15 tooled controls,
42 rules). A successful rehearsal is not a release, real assessment or OAuth test.

The application owns Google authorization, acquisition, supplied review forms
and private storage. The offline engine needs evidence, not credentials. Start
with one local user, one property and one to five selected URLs; test at least two
URLs in one bundle. Declare scope, objectives, sources,
prior knowledge and freshness policy before acquisition; obtain an actual plan
review. Retain exact request/response bodies, HTTP status and retrieval time.
The manifest's hashes bind bytes without authenticating Google or reviewers.

Use the CLI sequence above: prepare creates evidence-bound blank reviews; build
consumes actually supplied reviews and creates a new bundle; validate checks it;
HTML presents it in FR/EN; replay reproduces it offline. Invoke fixed programs
with argument arrays, application-controlled paths and process time limits, never
shell fragments from user input. Separate process failure from TSEP outcomes.
Exit 0 from build does not mean C: read report results and atomic results.
Import refusal is not NC. Retain failed/partial acquisition attempts; never invent
a response body. Retry into a new immutable attempt rather than overwriting one.

Pin the actual engine commit/archive, byte hashes, component versions and Python
runtime. The public website's draft.28 source is not a suitable substitute for the
development engine containing TS08. Update dependencies explicitly and preserve
historical bundles. Existing intake/replay checks remain authoritative; this kit
adds no competing lock schema. Application workflow states remain separate from
normative JSON outcomes. Show Google-reported indexing and dossier qualification
separately: Google PASS is not TSEP C; negative Google evidence can be documented
correctly. Retrieval time is not crawl time, and inspection is neither live nor TS12.

Run `scripts/inspection_app_check.py --output-dir NEW_DIRECTORY` to construct new,
explicitly synthetic examples from twelve fingerprint-checked frozen TS08 cases
and one newly authored two-URL scenario (thirteen in total).
Their relative chronology is preserved around a disclosed anchor; only these new
synthetic bytes/hashes/review bindings are created. No real capture or historical
fixture is refreshed. Actual prepare/build/validate/FR+EN HTML/replay subprocesses
retain their outputs and compare authored expectations. Four further refusals cover
changed native bytes, an omitted selected URL, reviews bound to another input and
overwriting an existing intake. Failures retain diagnostic evidence.
The cases include unknown API enum values and acquisition predating the plan.
The associated test also simulates a 2040 report-issuance clock while replaying
positive, stale-crawl and missing-review bundles: results and observations must
remain identical. Freshness uses the retained observation date, not the replay
date. This is a clock simulation, not future evidence or renewed acquisition.

The application must separately verify current Google documentation, consent,
permissions, quotas, revoked/expired tokens, interrupted acquisition, concurrency,
storage, privacy and hosting. Synthetic command logs are not a model for logging
production secrets. Keep real data restricted and demonstrations synthetic. A
successful real acquisition and actually supplied reviews are still required.
