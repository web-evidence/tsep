# Standalone HTML evidence report / Rapport HTML autonome

## Français

Le moteur de présentation version 4 transforme un rapport TSEP valide et ses
preuves en un fichier HTML autonome en français ou en anglais. Python 3.9+ suffit.
Il présente les résultats enregistrés, leurs règles, cibles, motifs, limites et
preuves. Il ne réévalue pas les captures et ne collecte aucune URL.

```sh
python3 tsep.py html /chemin/paquet/report.json \
  --output /chemin/rapport-fr.html --lang fr
python3 tsep.py html /chemin/nouveau/report.json \
  --compare /chemin/precedent/report.json \
  --output /chemin/comparaison-fr.html --lang fr
```

Choisir un **nouveau fichier** dans un dossier existant. `--evidence-root` et
`--compare-evidence-root` permettent de préciser les racines de preuves ; par
défaut, chacune est le dossier du rapport concerné. Le reçu JSON donne le chemin,
l’empreinte SHA-256 et la version du moteur. Succès de génération : code 0, même
pour NO_GO ; entrée invalide : 64, syntaxe CLI invalide : 2. `tsep.py gate` reste
la commande de décision. Aucun rapport source ou fichier existant n’est remplacé.

La comparaison exige le même protocole, profil, ensemble de contrôles et cibles.
Elle affiche les deux rapports et les différences atomiques, sans déclarer le
nouveau meilleur. « Même fichier de captures fourni » exige des octets identiques
pour la pièce `supplied-input` des deux paquets d’adaptateur. Sans cette preuve,
la page interdit d’attribuer les écarts au seul changement d’outil. Cette identité
ne prouve pas l’authenticité de la collecte ni l’égalité de toutes les autres pièces.

Le fichier contient les octets exacts des deux rapports et de toutes leurs preuves,
téléchargeables en local. Les aperçus sont échappés ; le HTML capturé et ses scripts
ne sont pas exécutés. Navigation et dépliage utilisent les fonctions natives du
navigateur, sans JavaScript, police distante ou ressource réseau. Une politique
CSP désactive par défaut le chargement de ressources. Les déclarations synthétiques
et restreintes des **deux** rapports sont signalées. Les pièces restreintes restent
embarquées : protéger l’accès au fichier généré autant que celui aux pièces.

La structure et les empreintes sont vérifiées avant génération ; une pièce manquante
ou altérée bloque la sortie. Borne : 32 Mio d’entrée par rapport, preuves comprises,
sans omission silencieuse ; le HTML résultant est plus volumineux (encodage base64
et aperçus). L’empreinte du reçu permet de contrôler le HTML transmis. Les dates
restent celles des rapports. Le même ensemble d’entrées et la même version du moteur
produisent les mêmes octets HTML. La lecture reste possible hors ligne après déplacement.

Limites : pas de vérification à l’ouverture, d’authentification des auteurs, de
certification ou de conformité globale. Les règles non couvertes restent visibles.
Un rapport vérifié reste un ensemble de constats à examiner. L’impression peut
omettre les détails repliés ; utiliser le fichier HTML et les paquets JSON pour
conserver toutes les preuves.

La version 2 présente aussi les échanges binaires v2 : en-têtes échappés, empreinte
et téléchargement des octets `.bin`, sans décoder les corps pour les afficher.
Le périmètre est adjacent à la décision ; l’inventaire de couverture fourni par
l’adaptateur est affiché comme une déclaration de l’outil.

La version 3 affiche aussi près des résultats TS01 l’origine déclarée des critères,
la politique, la date, l’URL/empreinte attendues et les marqueurs fournis. Ces
métadonnées ne prouvent pas une relecture humaine ; la cohérence du collecteur
est signalée selon les empreintes vérifiées lors de la collecte. L’origine absente
reste non déclarée. Le rapport rappelle que seules les exécutions fournies sont
présentées. Aucun verdict supplémentaire n’est calculé.

## English

Presentation engine version 4 turns a valid TSEP report and its evidence into one
self-contained French or English HTML file using Python 3.9+. It presents recorded
outcomes, rules, targets, reasons, limitations and evidence without reassessing
captures or fetching URLs. Use the commands above with `--lang en`.

Choose a **new file** in an existing directory. `--evidence-root` and
`--compare-evidence-root` default to each report's parent directory. The JSON receipt
gives the path, SHA-256 and engine version. Successful generation exits 0 even for
NO_GO; invalid data exits 64 and invalid CLI syntax 2. Use `tsep.py gate` for the
decision exit code. Source reports and existing files are never overwritten.

Comparison requires identical protocol, profile, selected control set and target
set. It displays both reports and atomic differences without claiming the newer
report is better. “Same supplied captures file” requires byte-identical
`supplied-input` evidence in the two adapter bundles. Otherwise the page states
that differences cannot be attributed to the tool change alone. Identity does not
authenticate collection or establish equality of every other evidence file.

Exact original bytes of both reports and all evidence are embedded and downloadable.
Previews are escaped; captured HTML/scripts never execute. Navigation and disclosure
use native browser elements without JavaScript, remote fonts or network resources.
CSP disables resource loading by default. Synthetic and restricted evidence in
**either** report is flagged. Restricted files remain embedded: preserve their
access restrictions when sharing the generated document.

Structure and fingerprints are checked before generation. Missing or altered
evidence blocks output. Input is limited to 32 MiB per report including evidence;
nothing is silently omitted. HTML is larger due to base64 encoding and previews.
The receipt fingerprints the delivered HTML. Dates are retained from source reports.
Identical inputs and engine version produce identical HTML bytes. The document
can be moved and viewed offline.

Limits: no verification at opening, author authentication, certification or global
conformity. Uncovered rules remain visible. A validated report is still a set of
findings to review. Printing may omit collapsed details; retain HTML and JSON
bundles for complete evidence.

Version 2 also presents binary v2 exchanges: escaped headers, digest and exact
`.bin` downloads, without decoding bodies for display. Scope is adjacent to the
decision; the adapter coverage inventory is labeled as tool-declared coverage.

Version 3 also places declared criteria origin, policy, date, expected URL/digest
and supplied markers beside TS01 results. This metadata does not prove human
review; collector consistency is labeled according to fingerprints checked at
collection. Missing origin remains undeclared. The report states that only
supplied runs are presented. No additional verdict is computed.

## Version 4 — préparation et média / Preparation and media

Le rapport affiche le précontrôle fourni des marqueurs de référence et la
comparaison brute des champs Content-Type à côté de TS01-A02, lorsqu’ils sont
présents. Ces éléments proviennent du contexte collecté : aucune extraction ni
nouvelle décision n’a lieu à l’affichage. Une référence indéterminée n’est pas
silencieusement validée par un résultat ultérieur fondé sur une empreinte égale.
Un écart de média est une observation à examiner, jamais un fail ajouté à draft.7.
Les anciens rapports sans ces champs restent lisibles, sans précontrôle inventé.

The report displays supplied reference marker preflight and raw Content-Type
comparison beside TS01-A02 when present. These come from collected context: no
extraction or new decision occurs at presentation time. An unavailable reference
check remains visible even if an equal digest later resolves identity. Media
changes are observations to inspect, never extra draft.7 failures. Old reports
remain readable without inventing missing preparation checks.
