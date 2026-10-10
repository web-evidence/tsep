# TS07 change/correction laboratory / Laboratoire de modification et correction TS07

## Français

Ce laboratoire version **1** exécute quinze scénarios sur un **site synthétique**,
avec de vraies requêtes HTTP vers un serveur temporaire sur `127.0.0.1`. Il ne
collecte aucun site externe. Les réponses, requêtes, dates, paramètres et empreintes
sont conservés. Les attentes sont enregistrées avant l’implémentation dans
`tests/fixtures/ts07-laboratory-cases.json`, lié au fichier d’empreinte adjacent.
Ce corpus rédigé en interne n’est pas une validation indépendante.

```sh
python3 examples/ts07_laboratory.py run --output /tmp/tsep-ts07-laboratory
python3 examples/ts07_laboratory.py replay /tmp/tsep-ts07-laboratory --output /tmp/tsep-ts07-replay.json
```

Les destinations doivent être nouvelles. Python 3.9+, aucune installation ; le
premier appel exige l’autorisation système d’écouter en loopback. Le rejeu ne
collecte rien, ne lance aucun navigateur et ne demande pas au serveur de rester
actif. Conserver le dossier complet et les outils dont il enregistre les empreintes.
Le code de sortie 0 signifie que les **attentes du laboratoire** concordent, jamais
qu’un site est conforme ou publiable. Un écart donne 2 et reste dans les résultats ;
une erreur donne 64. Une exécution interrompue conserve ses pièces déjà écrites ;
elle ne produit pas de bilan complet. Recommencer dans une nouvelle destination.

### Ce que l’on peut montrer

Le cas central conserve exactement le HTML initial mais ajoute `X-Robots-Tag:
noindex` : l’inventaire lexical ne change pas, alors que TS07-A01 détecte une
contradiction avec l’objectif préalable `allow`. La correction supprime ce fail.
Les autres cas montrent un noindex HTML, une interdiction robots, sa correction,
un changement éditorial sans nouvelle directive, une limite de lecture, une
contradiction robots malgré cette limite, la portée par robot et un robots.txt
indisponible. Une série **distincte** déclare `exclude` avant toute collecte :
noindex correspond alors à l’objectif A01, mais Disallow contredit l’accès A02.
Cette intention n’est pas ajustée après observation pour faire réussir un cas.

Le serveur reçoit littéralement `User-Agent: googlebot` ; le client est le
collecteur local TSEP, pas Googlebot authentifié. Cette chaîne est imposée par le
format borné actif, qui lie robot évalué et en-tête de requête. Aucune séparation
normative implicite n’est ajoutée ici. La politique robots est observée, puis la
page est récupérée même lorsqu’elle interdit le robot : **le client diagnostique
n’est pas un crawler qui applique robots.txt**, et le rapport conserve l’obstacle.

### Décisions et preuves manquantes

Les trois règles actives de draft.7 calculent leurs résultats sur les captures,
sans recevoir les attentes du corpus. Chaque état produit un paquet validé par
l’adaptateur, dont les preuves sont déclarées `synthetic` et l’assesseur `automatic`.
Aucune personne n’est présentée comme ayant réalisé une revue.

A03 reste inconclusive : un état est prévu, mais aucune capture navigateur n’est
fournie. A02 reste inconclusive quand l’accès n’est pas explicitement interdit,
car aucune revue d’accès n’est inventée. Un fail prouvé donne NC malgré ces lacunes ;
après correction, NT reste NT. Le récit est donc **NT → NC → NT**, pas C ou GO.
L’objectif n’est ni une preuve d’indexation, ni une recommandation de déploiement.
Le délai du plan de rendu est un scénario de laboratoire non exécuté, pas une
recommandation générale ou une preuve de suffisance des états.

L’expérience `seo_signals.py` relève séparément la source avec ses deux hypothèses.
Son désaccord sur noscript est visible dans deux cas synthétiques, tandis que le
lecteur actif refuse cette source. Aucun résultat expérimental ne remplace ce refus.
Elle ne lit pas les en-têtes, robots.txt ou un DOM. L’absence de signal lexical ne
signifie pas l’absence de directive dans la réponse HTTP.

### Conservation et rejeu

`registration.json` conserve avant les captures les deux intentions, la séquence,
les paramètres et les empreintes des outils. Chaque sous-dossier contient la
collecte brute et ses fichiers binaires, `input.json`, `observations.json` et un
`bundle/` TSEP. `results.json` confronte résultats calculés et attentes initiales ;
`README-fr.txt` donne une lecture par scénario. `requests.json` conserve les trente
requêtes reçues par le serveur local. Les manifestes relient les fichiers.
Le journal des requêtes est vérifié dès l'exécution : une requête inattendue reste
conservée et empêche l'émission du bilan de réussite. Le rejeu vérifie également
l'adresse du pair enregistrée et l'identité synthétique de chaque rapport.

Le rejeu vérifie les manifestes, les octets bruts face au JSON, les paramètres et
la chronologie enregistrée ; il reconstruit les entrées depuis les captures et
les intentions. Il recalcule les résultats atomiques, valide rapports et décisions,
et recalcule l’inventaire expérimental. Seuls les champs `runtime` sont exclus de
la comparaison des résultats ; une différence d’environnement est annoncée à part.
Les tests interdisent sockets, DNS et sous-processus pendant le rejeu. Ces dates
et empreintes locales ne constituent ni signature, ni horodatage de confiance,
ni authentification d’une exécution face à une falsification coordonnée.

Aucun contrôle TS01–TS44, contrat, version normative ou outil actif n’est modifié.
Aucune donnée Edikka n’est distribuée avec ce laboratoire. L’import de véritables
états rendus et une revue réellement effectuée restent des travaux distincts.

## English

Version **1** runs fifteen prefrozen authored cases against a synthetic site using
actual HTTP requests to a temporary `127.0.0.1` server. No external collection,
browser execution or human access review occurs. Run and replay with the commands
above, using new destinations and Python 3.9+. Exit 0 means the authored laboratory
expectations match, **not** conformity or deployment approval; mismatch is 2 and
error is 64. Partial attempts remain on disk; restart in a new directory.

The main demonstration adds an HTTP `X-Robots-Tag: noindex` without changing the
HTML. The lexical inventory remains identical while active TS07-A01 contradicts
the previously declared allow intent. Other cases cover HTML noindex, robots
blocking/correction, an editorial change, source-reader refusal, a robots failure
surviving that refusal, crawler scope and unavailable robots. A separate exclude
intent, also registered before every capture, has compatible noindex but blocked
access. It is not a post-observation change to the original intent.

The client sends the literal `googlebot` User-Agent only to loopback, as required
by the current bounded format. This is a diagnostic client, not an authenticated
engine and not a crawler enforcing robots.txt; it fetches the page even when the
observed policy disallows it, retaining the contradiction. No claim about actual
engine access, rendering or indexing follows.

All three existing draft.7 rules evaluate raw input without corpus expectations.
Each state gets a validated bundle with synthetic evidence and an automatic
assessor. A03 remains inconclusive for missing rendering; no access review is
invented to pass A02. Proven failures yield NC; correction restores **NT, not C**.
The planned rendering delay is an unexecuted laboratory scenario, not a general
recommendation or a reviewed completeness claim. The separate lexical experiment
can disagree on synthetic noscript while the active reader remains inconclusive;
its result never replaces a normative decision.

The registration, thirty server request records, raw capture sidecars, input,
observations, bundles and summary are retained with manifests. Offline replay
checks settings, chronology, bytes/JSON consistency and source fingerprints,
reconstructs inputs, recalculates atoms and lexical observations, and validates
reports/gates. Only runtime fields are excluded from result equality; runtime
differences are disclosed separately.
The request log is checked during collection too: unexpected requests are retained
and block the success summary. Replay also checks recorded loopback peers and each
report's exact synthetic identity.
Tests forbid sockets, DNS and subprocesses
during replay. Local hashes and times are integrity checks, not signatures,
trusted timestamps or protection against coordinated forgery. Keep the exact
recorded tools with the complete evidence directory. No TS01–TS44 rule, normative
version, active evaluator or Edikka integration is changed. Real rendering imports
and actual human review remain separate future work.
