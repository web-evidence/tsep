# Reference preparation and coverage inventory / Préparation des références

## Français

**Draft.7, interpréteur 4 et adaptateur 5 inchangés.** Ce lot ajoute deux outils de
préparation distincts des règles TS01 : un inventaire de constructions HTML et un
précontrôle de marqueurs au scellement. Aucun rapport historique n’est remplacé.

### Inventorier avant d’étendre

```sh
python3 diagnostics/coverage.py /chemin/input.json --output-dir /tmp/tsep-diagnostic
```

Choisir un dossier neuf, parent existant. Entrées de captures v1/v2, au plus 16 Mio
et 100 cibles. Le diagnostic lit la dernière réponse conservée de chaque cible,
pour la mesure et la référence si fournie. Il ne valide pas la chaîne HTTP,
l’intention ou la règle TS01. Décodage HTTP borné existant ; HTML uniquement avec
un Content-Type unique text/html et charset UTF-8 explicite. Encodage ou intégrité
non exploitables : motif « indisponible », sans inventer de résultat.

Sorties : entrée exacte `input.json`, `diagnostic.json`, HTML autonomes FR/EN et
SHA256SUMS explicite. Les pages contiennent seulement compteurs, positions et
métadonnées ; elles n’exécutent ni n’incorporent le texte/les attributs du HTML
capturé. L’entrée originale reste dans le dossier et conserve ses restrictions.

L’inventaire utilise HTMLParser, indépendamment du code de décision et de
l’extracteur TS01. Il poursuit après une limite candidate et compte notamment
tableaux, select/option, zones noscript/template/textarea non vides, SVG hors du
sous-ensemble, scripts échappés et structures nécessitant réparation. Un même
bloc peut produire plusieurs catégories : **ne pas additionner ces catégories
comme autant de défauts distincts**. Comptes par cible demandée, pas par URL
finale dédupliquée ; une redirection peut répéter la même ressource.

Les positions sont des lignes/colonnes de l’inventaire Python. Limites : 8 Mio de
caractères, profondeur 256, 100 000 événements. Runtime et empreintes des sources
sont enregistrés. Des divergences avec le tokeniseur TS01 et entre Python restent
possibles, surtout sur du HTML cassé. **L’inventaire n’est pas exhaustif ; une liste
vide ne prouve jamais l’évaluabilité ou la conformité.** `scan_completed` signifie
uniquement que le balayage s’est terminé dans ses bornes. Fréquence sur cet
échantillon, pas prévalence sur le Web. Aucun marqueur n’est testé, aucun verdict
C/NC/NA/NT ou pass/fail n’est produit. Ne pas injecter ce diagnostic comme résultat
atomique dans un rapport. Code 0 = inventaire produit, 64 = entrée/exécution invalide.

### Précontrôler la référence

Le **collecteur 4** réutilise l’extraction bornée de TS01 pour tester les marqueurs
sur la référence avant `seal`, sans appeler la décision d’identité ni profiter de
l’égalité du digest :

- `matches` : tous les requis sont présents et aucun interdit n’est trouvé sur
  une extraction complète prise en charge. Ce n’est pas une validation humaine
  de la pertinence du contenu ou une observation TS01 sur une nouvelle mesure.
- `contradiction` : requis absent ou interdit présent ; scellement refusé, sans
  fichier d’intention ni nouvelle requête de mesure. Corriger les critères ou
  choisir consciemment une autre référence, puis recommencer explicitement.
- `unavailable` : extraction non prise en charge ; scellement permis avec un
  avertissement explicite dans le reçu et l’intention. Aucun test partiel ne donne
  « matches » ou « contradiction ».
- `not-requested` : politique digest/stable ; marqueurs non demandés, sans
  approbation implicite du contenu.

Le dossier de référence reste intact. L’intention guidée **version 3** conserve
le précontrôle, l’empreinte du corps et les champs Content-Type de référence.
Avant la mesure, le collecteur recalcule ce précontrôle et vérifie l’identité URL /
empreinte ; un enregistrement incohérent bloque avant le réseau. Cela détecte les
incohérences accidentelles, pas une falsification complète ou une signature absente.

**La priorité normative URL / digest / stabilité / marqueurs reste inchangée.**
Une mesure à empreinte égale peut toujours donner pass sans tester ses marqueurs,
même si le précontrôle était indisponible. Le rapport HTML 4 conserve cet
avertissement à côté du résultat. Les anciens paquets sans précontrôle ne sont pas
rétroactivement labellisés vérifiés.

### Observer le type de média

Le collecteur conserve les valeurs Content-Type de référence et de mesure dans
`context.media_comparison`. L’écart compare les champs bruts : casse ou paramètres
peuvent suffire à différer sans incompatibilité sémantique. Champ manquant ou trace
inexploitable : comparaison non établie. HTML 4 affiche cette observation sans
nouvelle décision. Draft.7 ne lie pas l’identité à un type média attendu ; un même
corps servi en text/html puis text/plain peut donc garder le résultat de digest.
Changer cette règle exigerait une décision normative distincte, pas un correctif
silencieux. Pour text/plain, les marqueurs restent recherchés dans tout le corps,
même s’il ressemble à du balisage, conformément au contrat existant.

### Migration et tests

Collecteur 3 → 4 ; intention 2 → 3 ; HTML 3 → 4 ; diagnostic nouveau, version 1.
Interpréteur 4, adaptateur 5, entrée binaire 2, format de paquet et protocole restent
inchangés. Nouvelle collecte guidée = nouvelle référence/intention avec collecteur 4.
Les archives précédentes continuent leur rejeu avec leurs anciens outils. Les
comparaisons HTML historiques restent possibles ; nouveaux champs absents = non
fournis, jamais synthétisés.

Les tests vérifient refus de références contradictoires, précontrôle indéterminé
visible malgré un digest égal, refus avant réseau d’un précontrôle modifié, média
modifié sans nouveau verdict, diagnostic sans import du module d’évaluation et
HTML inerte. Exécuter `python3 scripts/verify.py`. Les captures réelles utilisées
pour un inventaire ne sont pas de nouveaux tests normatifs ni une campagne élargie.

## English

**Draft.7, interpreter 4 and adapter 5 are unchanged.** Diagnostic 1 inventories
candidate HTML limitations independently from decision code. Run the command
above on retained input v1/v2, with a new destination. Bounds: 16 MiB JSON, 100
targets, 8 Mi characters/source, depth 256 and 100,000 scanner events. Only the
last recorded response is inspected; no HTTP trace, intent or TS01 assessment is
established. Explicit single text/html UTF-8 content type is required. Unavailable
or invalid evidence retains its reason without a fabricated outcome.

Outputs are exact input, diagnostic JSON, inert FR/EN HTML and an explicit hash
manifest. HTML exposes counts/positions/metadata, not captured text or attribute
values; original input still requires its original access restrictions. HTMLParser
provides a separate exploratory inventory, which continues after candidate limits.
It can recover or tokenize differently from the interpreter, especially on broken
markup or another Python version. Runtime and source hashes are recorded.
**Candidates are not exhaustive; an empty list never establishes evaluability.**
Completed scanning means only completion within bounds. Categories can overlap;
do not add them as separate defects. Counts are per requested target, without
final-URL deduplication, and describe this sample only. No markers or verdicts are
computed. Never import diagnostics as atomic rule outcomes. Exit 0 = inventory
produced; 64 = invalid input/execution.

Collector 4 preflights reference markers at seal time with the unchanged bounded
extractor, without invoking identity decisions or an equal-digest shortcut:
`matches` = supported complete extraction satisfies markers; `contradiction` =
missing required/present forbidden marker, seal refused; `unavailable` = warning
retained while sealing is permitted; `not-requested` = digest/stable policy.
No partial extraction is conclusive. This is preparation, not semantic correctness,
TS01 assessment or human approval. References stay unchanged. Guided intent 3
records preflight, body hash and media headers; evaluation recomputes preparation
and checks reference URL/digest before network. This detects inconsistencies,
not a forged environment or complete tampering.

URL/digest/stability/marker precedence is unchanged. Equal digest can still pass
without evaluation markers; HTML 4 keeps an unavailable preflight visible beside
the result. Missing historical preflight is never invented. Raw Content-Type
fields are compared separately; spelling/parameters may differ benignly. Missing
or unusable evidence leaves the comparison unestablished. HTML 4 does not turn a
media difference into fail. Binding identity to expected media type would require
a separate normative decision. Text/plain still uses the entire body, even when
it resembles markup.

Migration: collector 3 → 4, guided intent 2 → 3, HTML 3 → 4, new diagnostic 1.
Interpreter 4, adapter 5, binary input 2 and protocol stay unchanged. Start a new
reference/intent for new guided collection. Replay historical bundles with their
historical archives. Tests cover contradictory/unavailable references, modified
preflight before network, media changes with unchanged outcomes, evaluator-free
diagnostics and inert HTML. Run `python3 scripts/verify.py`. Real-capture inventory
is neither a normative test result nor a wider collection campaign.
