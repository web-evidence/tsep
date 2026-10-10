# Revue et rejeu des preuves / Evidence review and replay

## Français

Ce parcours complète les commandes d'import existantes pour TS01, TS07 et TS10.
Il ne change ni le protocole draft.7 ni les verdicts de l'interpréteur. Le collecteur
TS01 garde son parcours référence → intention → mesure ; TS07/TS10 fonctionnent
par **import de captures fournies**, selon leurs plans et limites documentés.
Les outils n'inventent ni observation, ni revue, ni état rendu manquant.

### Rejouer un paquet d'import

Depuis l'archive d'outils qui a produit le paquet :

```sh
python3 adapters/replay.py /chemin/paquet --output /chemin/rejeu-nouveau
```

`paquet` contient input.json, report.json, import.json, assessment.json, gate.json,
earl.jsonld et SHA256SUMS. La commande contrôle l'intégrité, le protocole, les
sources exactes de l'adaptateur/interpréteur et les résultats conservés. Elle
réinterprète les octets de input.json dans un nouveau paquet, sans réseau.
Un ancien paquet demande ses anciens outils ; un changement de version est une
réévaluation distincte, pas un rejeu historique. Les versions de Python peuvent
différer, mais cette différence est signalée et les résultats doivent rester identiques.

Le code 0 signifie « mêmes observations atomiques, résultats de contrôle et décision ».
Il peut accompagner NO_GO ou NT : reproduire un échec ne l'efface pas. Code 64 :
entrée invalide, intégrité, outils incompatibles ou divergence. Une divergence
calculée conserve sa sortie et replay.json pour examen. Un paquet d'entrée invalide
est refusé avant création de la sortie. Aucune conclusion d'indexation, aucune
certification et aucune validation de la vérité des captures ne sont déduites.

### Préparer une revue sans proposer sa conclusion

```sh
python3 adapters/review.py prepare /chemin/paquet --output /chemin/revue-nouvelle
```

La version 1 prépare les revues fournies d'accès **TS07-A02** et de contenu
**TS10-A02**, uniquement si ces règles ont été demandées dans l'entrée. Elle ne
prépare pas les plans de rendu, les exemptions ou les preuves d'absence de sitemap.
Ces autres tâches suivent [états rendus](rendered-states.md) et
[familles canoniques](canonical-families.md).

Le dossier contient les octets d'entrée originaux, une pièce JSON par tâche,
request.json, une fiche response-template.json et READ-ME.txt. Les questions,
URLs et empreintes sont fixées ; nom, date, justification, assistance et décisions
sont **vides**. Une revue déjà présente reste visible dans les données historiques,
mais sa réponse n'est jamais copiée dans la nouvelle fiche.

Le relecteur copie la fiche **hors du dossier scellé**, examine les pièces, puis
renseigne lui-même les champs. `examined_evidence` cite les objets path/sha256
exacts des pièces examinées. `provenance` vaut human ou human-assisted ; assistance
décrit l'aide réellement reçue, ou « aucune ». Sur preuves synthétiques, seule
synthetic-exercise est admise. Un exercice ne devient pas une relecture réelle.
Les empreintes et déclarations ne prouvent pas l'identité ni la sincérité du relecteur.

Accès TS07 : no-obstacle ou unresolved-challenge, avec motif. Un doute, un obstacle
non résolu ou une autre situation hors interpréteur reste indéterminé ; le simple
statut 200 ne fournit jamais la revue. Contenu TS10 : compatible, incompatible ou
inconclusive, avec motif pour chaque membre comparé à la préférence déclarée.

### Importer la réponse réellement renseignée

```sh
python3 adapters/review.py import /chemin/revue-nouvelle \
  --response /chemin/reponse-remplie.json --output /chemin/evaluation-nouvelle
python3 adapters/replay.py /chemin/evaluation-nouvelle/bundle \
  --output /chemin/rejeu-de-la-revue
```

Champs vides, date antérieure à la demande ou future, pièces divergentes, changement
des questions/populations, provenance incompatible et réponse destinée à une autre
demande sont refusés. Les sources du workflow et le protocole doivent correspondre
à la demande. Conserver l'archive utilisée lors de sa préparation.

Le nouveau dossier garde original-input.json, request.json, completed-response.json,
les pièces examinées, reviewed-input.json, receipt.json et le nouveau bundle/.
**Conserver le dossier entier** : le sous-dossier bundle suffit au rejeu calculé,
mais la demande de revue et ses pièces historiques se trouvent au niveau parent.
Les captures et l'intention restent identiques. Pour TS10, observed_at ferme la
nouvelle période d'évaluation à la date de revue ; l'ancienne borne est conservée
et les dates des sources/DOM ne changent pas. Pour TS07, la date de capture reste
inchangée et la revue ultérieure porte sa propre date.

Les champs de revue normative sont remplis depuis la réponse fournie, sans modifier
leurs décisions. Les autres règles sont réévaluées normalement. Une revue positive
ne compense pas un DOM manquant, un lecteur HTML hors portée, une politique robots
ambiguë ou une contradiction. Les limites TS01 noscript et TS07/TS10 documentées
restent visibles ; ces commandes ne finalisent pas un audit réel à elles seules.

### Portabilité et preuve d'usage

Python 3.9+, bibliothèque standard. Aucun compte, service Edikka, réseau, navigateur
ou outil privé requis. Répertoires de sortie nouveaux uniquement ; chemins relatifs
et manifestes, aucun lien symbolique. Bornes de lecture du workflow : 1 024 fichiers,
32 Mio par fichier, 128 Mio par paquet ; input JSON conserve la limite de 8 Mio.

Les tests couvrent fiches vides, contradictions, dates, pièces et sources changées,
revues synthétiques distinctes, absence de rendu, rejeu sans réseau, fichiers non
listés et divergences conservées. Ils n'établissent **pas** qu'un utilisateur a
réalisé le parcours. Une recette utilisateur consigne séparément : problème compris,
preuve retrouvée, correction à demander, commande relancée et difficulté rencontrée.

## English

These workflow version 1 commands add offline replay and blank, evidence-bound
review forms to existing TS01/TS07/TS10 capture imports. Protocol draft.7 and
interpreter semantics are unchanged. TS01 retains its guided collector;
TS07/TS10 are **supplied-capture imports** with declared plans and existing limits.

Replay checks manifests, report/EARL consistency, protocol and exact interpreter/
adapter source hashes before interpreting the same input into a new bundle.
Historical replay requires historical tools; a new tool assessment is distinct.
Runtime differences are disclosed. Exit 0 requires matching atoms, control results
and gate, even for NC/NT/NO_GO. Exit 64 reports invalid inputs, incompatible tools
or discrepancies; calculated discrepancies retain outputs for inspection.
No network, collection or search-engine inference occurs.

Review preparation supports requested TS07-A02 access reviews and TS10-A02 content
reviews only. It supplies exact original input and per-task JSON evidence, immutable
questions/URLs/hashes, a README and a response template. Decisions, reviewer,
review date, reasons and assistance are blank; previous supplied reviews remain
historical evidence, never copied into new answers. Rendering plans, exemptions
and sitemap-absence reviews use their existing separate documented formats.

The reviewer copies the template outside the sealed request folder, examines the
proofs, and supplies their own judgments. Evidence references must match exactly.
Human or human-assisted provenance is required for non-synthetic evidence, with
assistance disclosed (including none). Synthetic evidence accepts synthetic-exercise
only. This does not authenticate identity, attendance or judgment truth.

Import rejects blank decisions, missing reasons, changed evidence/questions/URLs,
stale requests, incompatible provenance, changed workflow/protocol, and dates before
the request or in the future. It preserves original input, request, exact response,
examined evidence, a new reviewed input, receipt and bundle. Keep the **whole output
folder**: bundle/ alone replays decisions, while historical review evidence remains
in the parent. TS10's assessment end advances to the review date with the prior end
retained; capture/DOM dates remain unchanged. TS07 capture dates remain unchanged.

Access choices: no-obstacle or unresolved-challenge; an unresolved obstacle is
inconclusive, and HTTP 200 does not supply human review. Content choices:
compatible/incompatible/inconclusive for every declared family member. Missing
render states, unsupported parsing or contradictory directives remain unresolved
or failed even with positive supplied review. These tools alone do not complete
a real site assessment or prove actual human use.

All commands above use Python 3.9+ and its standard library, new output folders,
relative manifest paths, no symlinks, no external account or infrastructure.
Bounds: 1,024 files, 32 MiB per file, 128 MiB per package; input JSON stays bounded
at 8 MiB. Tests cover adverse/partial cases, offline replay and retained mismatch;
a user acceptance trial separately records understanding, evidence retrieval,
requested correction, replay and practical friction.


## Revue version 2 — TS04 / Review version 2 — TS04

Draft.9 ajoute les ressources nécessaires TS04-A02 au même parcours : questions
vides par URL, réponses réellement fournies, liaison aux traces et contexte,
conservation de l'entrée initiale. L'exemption d'inventaire préalable n'est pas
fabriquée par une revue après collecte. [Format](robots.md). Les anciennes demandes
restent avec leurs outils et leur version historiques.

Draft.9 adds required-resource TS04-A02 reviews to this workflow: blank per-URL
questions, supplied decisions, bindings and retained original input. Prior
inventory exemptions are not fabricated after capture. Historical requests keep
their pinned original tools.
