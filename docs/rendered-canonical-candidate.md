# Rendered canonical candidate 1 / Candidat canonical rendu 1

**Non-normative experiment. TSEP remains 0.1.0-draft.7.**

## Français

Cette brique compare les déclarations canonical d'un **seul arbre enregistré** à
une chaîne de référence explicite. Elle ne décide ni TS10-A01 ni un contrôle TSEP.
L'arbre provient du contrat d'[inventaire DOM 2](rendered-metadata-inventory.md).
Elle n'agrège pas les réponses HTTP, la source HTML, les robots, les autres états,
les familles d'URL ou les observations d'un moteur. Un accord ici ne les efface pas.

### Entrées, hypothèses et preuves

Le snapshot a exactement `script_sha256` et `tree`. Le script doit être celui
de l'inventaire 2 ; l'arbre doit passer son validateur sans réparation. Le fichier
d'intention porte exactement `format: rendered-canonical-intent`, `version: 1`,
`mode`, `state_label`, `document_url`, `preferred_url`, `html_canonical_required`,
`known_integrity_issues` et `record_sha256`. Les modes acceptés sont
`authored-synthetic` et `retrospective` : cette version n'atteste aucun protocole
prospectif. Une intention nulle est admise et donne indéterminé. Dans un objet,
chaque champ est requis mais les six derniers peuvent être nuls (preuve manquante).

L'empreinte lie l'intention à la représentation JSON du snapshot : clés triées,
séparateurs `,` et `:`, Unicode UTF-8 non échappé, nombres non finis interdits,
sans saut de ligne final. Les empreintes des fichiers bruts sont aussi conservées
par la CLI. Cette liaison est une cohérence interne, sans authentification.
`state_label` décrit l'état attribué par l'opérateur ; le digest ne prouve pas
que cet état a réellement été atteint. `ready_state` et les limites du relevé
restent visibles. Aucun effet après l'instant enregistré n'est couvert.

Le périmètre d'URL de référence est volontairement étroit : HTTP(S) ASCII avec
hôte DNS/IPv4 lexical, port numérique 1–65535 facultatif, chemin/requête ASCII,
échappements `%HH` complets, sans userinfo, fragment, antislash ou espace. IPv6,
IRI et autres formes donnent indéterminé, sans les déclarer invalides pour le Web.
La comparaison des valeurs est **exacte** : aucune résolution, normalisation,
suppression de paramètre, équivalence de cible ou règle Google n'est déduite.
Une préférence non normalisée peut donc empêcher l'accord : préférence avec
hôte en majuscules et brut normalisé = écart de chaîne ; brut identique à cette
préférence mais résolu en minuscules = indéterminé. Ce choix d'intention peut
expliquer le résultat sans défaut de page. L'outil ne normalise pas l'intention.

La liste `known_integrity_issues` conserve les anomalies connues déclarées. Nulle,
elle signale une histoire inconnue ; vide, seulement aucune anomalie déclarée.
Elle ne certifie jamais les API. Un auteur peut falsifier de façon cohérente toutes
les valeurs, y compris une contradiction. L'outil ne sait pas le détecter.

### Priorité des règles candidates

1. Un arbre, snapshot ou objet d'intention mal formé est **rejeté**. Une version
   ou un script différents sont rejetés : aucune conversion silencieuse.
2. Une intention/liaison manquante, une URL hors périmètre ou ne correspondant
   pas au document, une anomalie connue, une erreur API ou un head réel absent/
   ambigu donne `undetermined`. Le vrai head est l'unique élément HTML head,
   enfant direct de l'élément HTML du document ; un head imbriqué ne le remplace pas.
3. Pour chaque canonical HTML observée, une propriété résolue manquante bloque
   la conclusion. Si le brut commence par `http://` ou `https://` (casse ignorée,
   après retrait des caractères U+0000–U+0020 périphériques et suppression de
   TAB/LF/CR dans une copie utilisée pour ce repérage seulement, sans modifier
   la chaîne comparée)
   et diffère du résolu, le résultat est aussi indéterminé. Cette **différence non
   interprétée** inclut des normalisations légitimes : ni falsification ni défaut
   SEO ne sont affirmés. Le résolu ne remplace jamais le brut pour gagner un accord.
4. Sans ces blocages, une canonical dans le DOM ordinaire dont le brut manque,
   est vide ou diffère de la référence donne `contradiction-in-record`, même
   dans un préfixe incomplet. C'est une contradiction au critère de chaîne déclaré,
   pas une preuve que les URL désignent des ressources différentes pour un moteur.
   Toutes les déclarations et leurs positions restent présentes, sans déduplication.
5. Sinon, un état `ready_state: loading`, un parcours incomplet, une canonical hors enfant direct du vrai head,
   ou une canonical observée dans un shadow ouvert donne `undetermined`.
   La position ambiguë n'est pas assimilée à une prise en compte par un moteur.
   Le shadow ouvert reste observé mais ne fournit pas de contradiction de cible.
6. Sans canonical observée et avec parcours complet : `contradiction-in-record`
   si la présence HTML était requise, `no-declaration-in-record` sinon. Ce dernier
   constate une absence dans ce périmètre, jamais une non-applicabilité TSEP.
7. Sinon : `agreement-in-record`, seulement si toutes les déclarations observées
   sont enfants directs du head, bruts exactement égaux et parcours complet.
   Les doublons identiques restent visibles et sont admis par ce critère candidat.

Les diagnostics de valeur sont conservés même lorsqu'un blocage empêche de conclure.
La couverture reste séparée du résultat : une contradiction sur préfixe n'est
jamais présentée comme un parcours complet. Le namespace SVG ne devient pas HTML ;
noscript texte n'est pas reparsé. Les documents frame, fragments template et shadow
fermés ne sont pas évalués. Le résultat est conditionnel aux octets et API déclarés.
Les raisons sont des codes stables ; aucun code C/NC/NA/NT n'est produit.

### Rejeu, cas et migration

```sh
python3 experiments/rendered_canonical.py snapshot.json --intent intent.json --output analyse.json
python3 -m unittest discover -s tests -p test_rendered_canonical.py -v
```

La CLI n'importe aucun évaluateur normatif, ne collecte rien et refuse de remplacer
un fichier existant. Bornes : snapshot 4 Mio, intention 64 Kio, chaînes 4 096
caractères, au plus 64 anomalies déclarées. Le snapshot reste soumis aux bornes
plus étroites de l'inventaire. Les entrées ne sont jamais modifiées.

Les arbres et attentes du fichier `rendered-canonical-v1-cases.json` sont rédigés
et figés avant le code candidat ; ils ne sont pas des captures navigateur. Ils
couvrent notamment les doublons, préfixes, API trompeuses, normalisations, attributs
vides/manquants, faux head, namespaces, shadow, liaison, intention et priorités.
Le contrôle brut/résolu est motivé par la recette déjà observée `page-api-override`.
Les règles de couverture sont motivées entre autres par `truncated-tree`.
Deux situations supplémentaires de préférence non normalisée ont été ajoutées
après la revue de conception et le premier code ; elles ne font pas partie des
59 cas figés au préalable. Les attentes initiales ne sont pas réécrites.
Cinq autres cas sont figés après la première implémentation mais avant sa correction :
chargement en cours avec accord apparent ou contradiction, état interactive,
espaces ASCII avant/autour du href. La revue a révélé que l'état loading et les
espaces initiaux n'étaient pas couverts. Les premières sorties sont conservées ;
ces corrections ne changent aucune des 48 issues rétrospectives (relevés complete).
Cinq cas supplémentaires, figés avant une dernière extension du garde-fou,
couvrent C0 périphériques, TAB/LF/CR dans le préfixe et la limite NBSP. Ce repérage
reprend seulement le prétraitement initial du [parseur URL WHATWG](https://url.spec.whatwg.org/#concept-basic-url-parser),
consulté le 10 octobre 2026. Un [extrait daté](sources/url-parser-preprocessing-2026-10-10.json)
et son empreinte sont conservés. Ce n'est pas une implémentation du parseur URL.

Une application aux 48 relevés déjà examinés est **rétrospective**. Écrire ses
prédictions avant l'exécution de ce code ne rend pas ces relevés nouveaux ou
indépendants. La référence choisie après collecte doit être déclarée comme telle.
Une nouvelle collecte avec critères enregistrés auparavant est une étape distincte.

Application locale du 10 octobre 2026 : référence uniforme `/product`, choisie
après collecte pour les 24 recettes de chaque environnement. Les 48 prédictions
écrites avant cette exécution concordent : **26 accords dans les relevés,
14 contradictions de chaîne, 8 indéterminés** (13/7/4 par environnement).
Les quatre indéterminés par environnement sont la canonical dans body de même
valeur, la canonical shadow ouverte, le préfixe tronqué et l'API altérée.
Ce n'est ni un taux de qualité SEO ni un test indépendant. La chaîne initiale de
48 relevés et 118 vérifications de recettes se rejoue à l'identique, sans nouvelle
capture. Les traces, entrées, prédictions et échanges Claude sont conservés dans
un kit local privé. La revue Claude est une lecture du code/bilan transmis,
sans exécution indépendante et sans relecture humaine.

Cette version ajoute un outil autonome. Elle ne convertit aucun rapport, inventaire
ou verdict ancien ; conserver les outils et empreintes d'origine avec les preuves.
Une promotion normative nécessiterait une version distincte du protocole, ses
contrats FR/EN, migration et cas contradictoires. Aucune publication ni CI distante
n'est établie par ce document.

## English

Candidate 1 compares canonical declarations in **one recorded tree** with an
explicit reference string. It does not evaluate TS10-A01 or a TSEP control. It
does not combine HTTP Link, source HTML, robots, other states, URL families or
engine observations. Agreement cannot override their evidence or earlier results.

Inputs are an exact `{script_sha256, tree}` snapshot using inventory 2 and an
intent with exactly `format: rendered-canonical-intent`, `version: 1`, `mode`,
`state_label`, `document_url`, `preferred_url`, `html_canonical_required`,
`known_integrity_issues`, `record_sha256`. Modes are `authored-synthetic` or
`retrospective`; prospective status is not supported. Null intent is undetermined.
The last six fields may be null to expose missing evidence, but must be present.
The digest binds sorted-key UTF-8 JSON, unescaped Unicode, compact separators,
no final newline and no non-finite numbers. The CLI additionally records input
file digests. This is internal consistency, not authentication or proof that the
operator's named state was attained. Recorded readiness and coverage stay visible.

Reference URLs use a narrow ASCII HTTP(S) subset: lexical DNS/IPv4 host, optional
numeric port 1–65535, ASCII path/query, complete `%HH` escapes, no userinfo,
fragment, backslash or space. Unsupported IPv6/IRI forms are undetermined, not
asserted invalid on the Web. Comparison is exact, without resolution, normalization,
parameter removal, resource-equivalence or Google interpretation. A null issue list
means unknown history; an empty list means no declared known issue, never trusted
APIs. Coherently fabricated values, including fabricated contradictions, can evade
all these checks.
An unnormalized preference can itself prevent agreement: normalized raw host vs
uppercase preferred host is a string contradiction; uppercase raw matching that
preference vs lowercase resolved host is undetermined. This can reflect the intent
choice without any page defect. The tool does not normalize intent. Two additional
tests of these situations were added after design review and initial implementation;
they are not part of the 59 prefrozen authored cases.

Decision order:

1. Reject malformed inputs, incompatible versions/scripts and invalid trees;
   never repair or migrate implicitly.
2. Missing intent/binding/state, unsupported or mismatched document URL, unsupported
   preference, unknown requirement/history, known issue, API error or absent/ambiguous
   real document head yields `undetermined`.
3. Missing resolved canonical property also blocks. An HTTP(S)-prefixed raw value
   (case-insensitive, trimming peripheral U+0000–U+0020 and removing TAB/LF/CR
   in a copy for prefix detection only, preserving the raw comparison string)
   differing from its resolved property blocks as an **uninterpreted difference**.
   Legitimate normalization may trigger this conservative guard. It asserts neither
   tampering nor SEO invalidity; resolved values never substitute for raw values.
4. Otherwise, a missing, empty or different raw canonical value in ordinary DOM
   yields `contradiction-in-record`, including in a partial prefix. This concerns
   the declared string criterion, not engine target equivalence. Keep all duplicates.
5. Otherwise, `ready_state: loading`, incomplete traversal, non-direct-head placement or observed open-shadow
   canonical yields `undetermined`. Shadow canonical remains visible but does not
   establish a target contradiction. Placement does not imply engine processing.
6. Complete traversal without canonical yields `contradiction-in-record` if required,
   otherwise `no-declaration-in-record`. The latter is scoped absence, never TSEP NA.
7. `agreement-in-record` requires complete traversal and all canonical declarations
   directly in the real head with raw values exactly equal. Identical duplicates
   are retained and allowed under this candidate criterion.

Value diagnostics survive guards. Coverage is separate from outcome. Foreign
namespaces are not HTML, noscript text is not parsed, frame documents/template
fragments/closed shadow are outside scope. All outcomes are conditional on supplied
records and APIs, never C/NC/NA/NT. The CLI imports no normative evaluator, performs
no collection, preserves inputs and refuses output overwrite. Bounds: 4 MiB snapshot,
64 KiB intent, 4,096-character strings, 64 declared issues, plus inventory bounds.

The frozen authored fixture file predates candidate code, not a browser campaign.
The raw/resolved guard was motivated by the previously observed API-override recipe;
coverage guards include the observed node-limit case. Applying this tool to 48
previously examined observations is retrospective even if predictions are written
before this implementation is run. A reference chosen afterwards is explicitly
post-collection. A new pre-registered collection remains a separate step.
Five additional cases were frozen after initial implementation but before correction:
loading with apparent agreement or contradiction, interactive state, leading and
surrounding ASCII whitespace. Static review exposed the missing loading gap and
prefix detection for leading whitespace. Initial outputs are retained; these fixes
do not change the 48 retrospective outcomes (all recorded as complete).
Five further cases were frozen before the final prefix guard extension: peripheral
C0, TAB/LF/CR inside the prefix and the NBSP boundary. Only the initial preprocessing
of the [WHATWG URL parser](https://url.spec.whatwg.org/#concept-basic-url-parser)
is used for prefix detection. The 2026-10-10 dated excerpt and fingerprint are
retained under `docs/sources/`; no full URL parser implementation is claimed.

Observed locally on 2026-10-10: the uniform `/product` reference was chosen after
collection for all 24 recipes per environment. All 48 pre-execution retrospective
predictions match: **26 record agreements, 14 string contradictions, 8 undetermined**
(13/7/4 per environment). Undetermined cases are same-value body placement, open
shadow canonical, truncated prefix and altered API. These are neither SEO quality
rates nor independent validation. The original 48 records and 118 recipe checks
replay unchanged, with no new capture. Inputs, predictions, traces and Claude
exchanges are retained in a private local kit. Claude reviews supplied code and
accounts, without independent execution or human review.

Migration: add this standalone experiment, preserving original tools, fingerprints,
inventories and normative results. No conversion into draft.7. Promotion would
require a distinct protocol version, bilingual contracts, migration and contradictory
cases. No publication or remote CI result is established here.
