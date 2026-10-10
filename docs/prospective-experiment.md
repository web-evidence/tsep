# Prospective comparison experiment 1 / Comparaison prospective expérimentale 1

## English

`experiments/prospective.py` connects guided collector 6 to the **separate**
noscript experiment 4. The active protocol remains **0.1.0-draft.7**. TS01–TS44,
report schema, interpretation and gate are unchanged. No normative migration.
Older captures keep their pinned tools; this workflow requires new references,
a version 3 intent and its own receipt.

Before measurement, `prepare` checks the complete reference trace, decoded body
digest, declared final URL, active preflight, criteria and collector settings.
Marker policies additionally require **both complete reference readings to pass**
the experimental criteria. The receipt retains original intent, reference and
loaded source hashes. Missing, contradictory or unsupported experimental
reference evidence refuses preparation. This command never fetches.

After measurement, `compare` rechecks those bindings, including raw sidecars,
input/reference/evaluation correspondence, collection context and local time
ordering. It replays the original draft.7 report offline, keeping its atomic
observations unchanged. Experimental markers run only for a complete HTTP 200,
the expected final URL, changed decoded bytes and an explicit marker policy.
Equal digests need no marker probe. A non-200, wrong URL or changed stable-policy
body cannot become an experimental success. Incomplete or unsupported readings
remain inconclusive/unavailable. The experiment binds its UTF-8 source hash to
**the same decoded body bytes** as the active assessment.

The result is not a TSEP report or an upgraded control verdict. Local files and
clock ordering are **not a trusted timestamp, signature, independent attestation
or human approval**. Coordinated rewriting of all local evidence is outside this
integrity check. Assessor identity, authorized scope, criterion suitability and
campaign completeness remain declarations. A short interval does not establish
longitudinal stability, browser rendering, indexability, ranking, certification
or adoption. The source reader's documented limits, including exact CRLF and
whitespace handling, continue to apply.

## Français

`experiments/prospective.py` relie le collecteur guidé 6 à l'expérience noscript 4
**séparée**. Le protocole actif reste **0.1.0-draft.7** ; TS01–TS44, contrat,
schéma, interprétation et décision du rapport ne changent pas. Aucune migration
normative. Les anciennes captures gardent leurs outils figés ; cette chaîne exige
une nouvelle référence, une intention version 3 et son propre reçu.

Avant mesure, `prepare` vérifie la trace complète de référence, son empreinte
décodée, l'URL finale déclarée, le précontrôle actif, les critères et les réglages.
En politique marqueurs, il exige la réussite des **deux lectures complètes de
référence** du prototype. Le reçu conserve les empreintes des sources chargées,
de l'intention et de la référence. Contradiction, preuve absente ou lecture
expérimentale non prise en charge refusent la préparation. Aucun accès réseau.

Après mesure, `compare` vérifie à nouveau ces liens, fichiers bruts, entrée de
rapport, contexte et ordre des dates locales. Il rejoue le rapport draft.7 hors
ligne et conserve ses observations atomiques. Les marqueurs expérimentaux ne
s'exécutent que pour un HTTP 200 complet, à l'URL attendue, avec octets décodés
modifiés et politique marqueurs explicite. Une empreinte égale n'a pas besoin de
cette sonde. Statut non-200, mauvaise destination et corps modifié déclaré stable
ne deviennent pas des réussites expérimentales. Lecture partielle ou refus reste
indéterminé/indisponible. L'empreinte UTF-8 du prototype doit correspondre aux
**mêmes octets décodés** que ceux de l'évaluation active.

La comparaison ne remplace aucun rapport ou verdict TSEP. Fichiers et horloge
locale ne prouvent **ni horodatage indépendant, ni signature, ni attestation tierce,
ni approbation humaine**. La réécriture coordonnée de toutes les preuves locales
reste hors de portée de ce contrôle d'intégrité. Identité de l'opérateur,
autorisation, pertinence des critères et exhaustivité de la campagne restent des
déclarations. Un essai court ne démontre pas une stabilité sur plusieurs jours,
le rendu navigateur, l'indexabilité, le classement, une certification ou une
adoption. Les limites documentées du lecteur source restent applicables,
notamment les espaces et CRLF exacts.

## Commands / Commandes

Collect authorized references and seal explicit criteria using [guided capture](guided-capture.md).
Après collecte de référence autorisée et scellement de critères explicites via
la [chaîne guidée](guided-capture.md) :

```sh
python3 experiments/prospective.py prepare --reference first/reference --intent intent.json --output receipt.json
python3 collectors/ts01.py evaluate --reference first/reference --intent intent.json --output assessment
python3 experiments/prospective.py compare --reference first/reference --assessment assessment --receipt receipt.json --output comparison.json
```

Only `evaluate` in this block performs network requests. The other two commands
are offline; existing output files are refused. Keep `assessment/report-fr.html`
as the active report, beside the experimental JSON, never replaced by it.
Seul `evaluate` effectue des requêtes réseau dans ce bloc. Les deux autres sont
hors ligne et refusent les sorties existantes. Conserver le rapport actif
`assessment/report-fr.html` à côté du JSON expérimental, sans le remplacer.

The laboratory needs Python 3.9+ and a loopback listener. It retains all captures,
with 19 HTTP requests on 127.0.0.1 and **zero external requests**.
Le laboratoire exige Python 3.9+ et l'écoute loopback ; 19 requêtes sur 127.0.0.1,
**aucune requête externe**, toutes les captures sont conservées :

```sh
python3 examples/prospective_ts01.py --output /tmp/new-synthetic-lab
python3 scripts/verify.py
```

The nine expectations and their SHA-256 were committed before implementation.
They distinguish digest priority, simple markers, noscript agreement, absent
required markers, forbidden markers, unsupported reading, changed final URL,
HTTP error and stable-policy change. Tests reject altered intent, late receipt,
changed sources, raw/JSON disagreement, mismatched assessment bindings and
fabricated reference probes. Runtime differences are disclosed, while normative
and experimental outcomes must replay unchanged.

Les neuf attentes et leur SHA-256 ont été enregistrés dans Git avant le code :
priorité à l'empreinte, marqueurs simples, accord noscript, requis absent,
interdit présent, lecture refusée, mauvaise destination, erreur HTTP et politique
stable. Les tests refusent intention modifiée, reçu tardif, sources modifiées,
désaccord brut/JSON, entrée mal reliée aux captures et précontrôle expérimental
falsifié. Les différences de runtime sont explicites ; les résultats normatifs
et expérimentaux doivent rester identiques au rejeu.
