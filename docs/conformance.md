# Executable conformance / Conformance exécutable

<a id="draft20-runtime-coverage"></a>

## Current draft.20 runtime coverage / Couverture courante — 2026-10-11

Protocol **0.1.0-draft.20**, interpreter **20**: **775 authored synthetic cases**,
**1,144 rule/target pairs**. The core result is retained from the successful
preview-intent verification; the optional-runtime result is a new full-corpus run
on the same unchanged executable sources, inputs and expectations. Exact outputs,
source hashes and their different acquisition origins are preserved in the
[observation record](../provenance/runtime-coverage-draft20-2026-10-11/observation.json).

| Configuration | Exact agreements / Accords | Reduced pairs / Réduits | Conclusive expectations resolved / Attendus conclusifs résolus | Disagreements / Désaccords |
| --- | ---: | ---: | ---: | ---: |
| Without optional Node / sans Node optionnel | 1,033 | 111 | 600 / 711 | 0 |
| Explicit Node 24.19.0 / explicite | 1,136 | 8 | 703 / 711 | 0 |

FR : **433 attendus indéterminés** font partie des accords. Le runtime optionnel
résout 103 couples dont les profils sont déjà fixés dans les entrées ; 1 041
résultats restent identiques et aucune conclusion ne devient une autre conclusion.
Les huit couvertures réduites suivent des lecteurs historiques non migrés. Leur
maintien n'annule pas les nouveaux profils et leur suppression n'est pas un
critère d'achèvement. TS01 noscript et les preuves réelles manquantes restent
hors de ce simple décompte. Aucune note SEO, validation Google ou revue humaine.

EN: agreements include **433 normatively inconclusive expectations**. Explicit
Node resolves 103 pairs under their already-selected profiles; 1,041 outcomes
are unchanged and no conclusive outcome changes to another conclusion. The eight
remaining legacy-reader limits are retained without silent migration. They are
not an exhaustive inventory of method limitations; eliminating them is not a
completion criterion. See [current readiness](control-implementation-status.md).

Reproduce the current corpus / Rejouer le corpus courant :

```sh
env -u TSEP_SOURCE_NODE python3 -B conformance/run.py
TSEP_SOURCE_NODE=/path/to/node24 python3 -B conformance/run.py
```

The draft.18 observation below is historical; rerunning these commands on current
sources produces the current edition, not its old numbers. Use the archived tools
for a historical reproduction. / Les chiffres draft.18 ne sont pas ceux du code
courant ; utiliser les outils archivés pour reproduire cette mesure historique.

Earlier draft.19 added optional prior [http-link-context-v1](http-canonical-context.md) for TS10-A01/A02.
Sixty-one additional authored cases retain all 640 historical inputs/outcomes; [migration](migration-draft.19.md).
FR : 61 nouveaux cas synthétiques, anciens lecteurs et leurs limites conservés ; aucune note SEO.

<a id="current-runtime-coverage--couverture-selon-le-runtime--2026-10-11"></a>

## Draft.18 runtime coverage / Couverture selon le runtime — 2026-10-11

Draft.18, interpreter 18: the same **640 synthetic cases and 1,009 rule/target
pairs** were executed in two configurations. Inputs, expected outcomes and prior
reader selections were unchanged. Retained outputs and source fingerprints are in
[the observation record](../provenance/runtime-coverage-2026-10-11/observation.json).

| Configuration | Exact agreements / Accords exacts | Reduced coverage / Couverture réduite | Resolved conclusive expectations / Attendus conclusifs résolus | Disagreements / Désaccords |
| --- | ---: | ---: | ---: | ---: |
| `TSEP_SOURCE_NODE` unset / absent | 900 | 109 | 520 / 629 (82.67%) | 0 |
| Explicit Node 24.19.0 / Node 24.19.0 explicite | 1,001 | 8 | 621 / 629 (98.73%) | 0 |

FR : les **640 cas synthétiques et 1 009 couples règle/cible** sont identiques
dans les deux exécutions. Le lecteur Node optionnel résout 101 couples dont le
profil était déjà déclaré dans les entrées. Sans ce runtime, ils restent
indéterminés ; aucun lecteur de repli ne les fait réussir. Les 380 attendus
normativement indéterminés comptent dans les accords exacts, hors du dénominateur
des 629 attendus conclusifs. Un exit 0 signifie zéro désaccord interdit, pas la
résolution de tous les cas. Ces pourcentages ne mesurent ni 44 contrôles achevés,
ni la qualité SEO d'un site, ni une qualification indépendante.

EN: the optional runtime resolves 101 pairs whose source profiles were already
declared in the inputs. Without that runtime, those pairs remain inconclusive;
there is no favorable fallback. Exact agreements include 380 normatively
inconclusive expectations, excluded from the 629 conclusive-expectation denominator.
Exit 0 means no disallowed disagreement, not complete implementation coverage.
These percentages do not measure completion of 44 controls, site SEO quality or
independent qualification.

Across all 1,009 pairs, 908 outcomes are unchanged and 101 move from inconclusive
to their declared conclusive expectation; no conclusive outcome changes to a
different conclusion. The remaining eight stay inconclusive in both runs.
Sur les 1 009 couples, 908 résultats restent identiques et 101 passent
d'indéterminé à l'attendu conclusif ; aucune conclusion ne devient une conclusion
différente. Les huit limites restantes sont indéterminées dans les deux cas.

Reproduce with Python 3.9.6 and the explicitly selected Node 24.19.0 used in this
observation / Reproduction dans les versions observées :

```sh
env -u TSEP_SOURCE_NODE python3 -B conformance/run.py
TSEP_SOURCE_NODE=/path/to/node24 python3 -B conformance/run.py
```

The eight remaining pairs and their exact reasons are retained in the observation
record. They cover historical robots matching, presentation intent, a rendered
directive, canonical source/HTTP contexts and a sitemap DTD. Installing Node does
not silently migrate a legacy reader. This finite corpus also does not cover all
known tool boundaries, such as TS01's unresolved nonempty noscript proposal.

Les huit limites restantes et leurs motifs exacts sont conservés dans le relevé :
matching robots historique, intention de présentation, directive rendue, contextes
canonical source/HTTP et DTD de sitemap. Installer Node ne migre pas les profils
historiques. Ce corpus fini ne représente pas toutes les limites connues, dont la
proposition noscript non vide de TS01, toujours non promue.

The milestones below are historical / Les jalons suivants sont historiques.

Earlier tool coverage: interpreter 14, 451 raw cases (427 retained + 24 sitemap-location cases),
820 rule/target pairs, including eight explicitly reduced-coverage pairs. Protocol draft.14.
FR : lecteur sitemap préalable, annotations séparées, profils historiques conservés.
[Method / Méthode](sitemap-locations.md), [migration](migration-draft.14.md).

Earlier tool coverage: interpreter 12, 409 raw cases (383 retained + 26 TS04 client/product cases). Protocol draft.12.
Couverture de ce jalon : portée du client TS04 explicite, 26 nouveaux cas synthétiques,
aucune revue humaine ou visite de moteur déduite. [Migration](migration-draft.12.md).
Earlier named milestones below retain their historical scope.
Couverture de ce jalon : [attributs de canonical](canonical-attribute-coverage.md), lecteur historique conservé, migration explicite.

Historical: draft.11, interpreter 10, 353 raw cases (338 retained + 15 transport/directive cases).
Actuel : draft.11 ; [navigation attribuée](same-navigation-laboratory.md), sémantique sur représentation cliente et [migration](migration-draft.11.md). Earlier named milestones below remain historical.

Historical: draft.10, interpreter 9, 338 raw cases (299 retained + 39 structured rendered cases).
Actuel : draft.10 ; [lecture structurée](structured-rendering.md), bornes, provenance et [migration](migration-draft.10.md). Earlier named milestones below remain historical.

# Executable conformance / Conformance exécutable

## Français

`python3 conformance/run.py` compare des résultats calculés depuis des entrées
brutes aux attendus rédigés séparément dans `conformance/cases.json`. Chaque cas
est synthétique. Aucun réseau, aucun site audité. Ce corpus est distinct des
jugements de méthode dans `tests/fixtures/control-cases.json`, qui testent la
cohérence des rapports pour les treize règles TS01/02/04/07/10.

Le corpus lie `protocol_version` à la version livrée. Chaque cas possède `id`,
`input` et `expected`. L’interpréteur reçoit **seulement input** ; `expected` contient
un verdict par couple `rule_id`/`target`. Le comparateur exige une matrice complète,
sans doublon ni résultat supplémentaire, et pass/fail/inconclusive pour chacune
des treize règles. Un désaccord renvoie 1, une entrée invalide 64 ; 0 signifie aucun désaccord,
avec éventuelle couverture réduite explicitement comptée.
Il n’émet ni rapport C ni conformité globale.

L’interpréteur version 3 accepte également l’[entrée binaire v2](guided-capture.md),
avec base64/SHA-256, décodage gzip/deflate borné et empreinte sur octets de contenu.
La version 1 ci-dessous et le corpus historique restent conservés.

Pour convertir un objet `input` en rapport et preuves, voir
l’[adaptateur de captures](capture-adapter.md). Il conserve les résultats calculés,
y compris les inconnues de référence, sans leur substituer `expected`.

### Format input_version 1 (historique)

Objet `{ "input_version": "1", "rules": [...], "targets": [...] }`. `rules` liste
explicitement les treize IDs TS01-A01/A02, TS02-A01/A02, TS04-A01/A02, TS07-A01/A02/A03 et TS10-A01 à A04.
Les cibles TS10 suivent le [format famille](canonical-families.md) ; les champs
ci-dessous décrivent les cibles TS01/07. Chaque cible TS01/07 contient :

| Champ | Contenu |
| --- | --- |
| `url` | URL HTTP(S) exacte, sans fragment ni authentification |
| `observed_at` | Date de l’observation avec fuseau |
| `context` | `network`, `bounds`, `tool`, `tool_version`, déclarations non vides |
| `intent` | Objet ci-dessous, fixé avant la mesure |
| `http` | Tableau ordonné des échanges, un par saut |
| `robots` | `observed_at` et `http` pour le robots.txt de l’origine finale |
| `access_review` | `observed_at`, `outcome`, `reason` : revue d’accès au plus tôt à la date de la capture |

Intention : `declared_at`, `public_canonical: true`, `crawler`,
`expected_final_url`, `expected_body_sha256`, `indexing` (`allow`/`exclude`),
`following` optionnel (`allow`/`disallow`/`unspecified`),
`access_basis: "test-client-only"`. La revue distincte `access_review` consigne
`outcome: "no-obstacle"` et son motif après examen de la capture ; elle ne fait
pas partie de l’intention préalable et n’est pas inférée d’un 200.
Une intention absente ou postérieure donne inconclusive. Une intention de
présentation (`presentation`) nécessite une revue hors de cet interpréteur.

Identité TS01-A02 : `expected_final_url` et `expected_body_sha256` restent les
références préalables. URL différente → fail ; URL et empreinte identiques → pass.
Sur empreinte différente, `representation: "stable"` → fail ; sinon les listes
optionnelles `required_markers` et `forbidden_markers` décident : requis manquant
ou interdit présent → fail. Pass exige au moins un requis et aucune violation.
Interdits seuls absents → inconclusive. Chaînes UTF-8 uniques non blanches,
sensibles à la casse et littérales dans le texte source extrait. Pour HTML,
entités décodées ; commentaires, script/style, balises et attributs exclus ;
aucune concaténation entre segments séparés par une balise ou un commentaire.
Pour text/plain, corps complet sans interprétation HTML. Aucun regex ni
normalisation des espaces. Un interdit contenu dans un requis est contradictoire.
Listes absentes/vides/invalides → inconclusive ;
une politique de représentation autre que stable n’est pas prise en charge.
Sans empreinte valide à URL identique, les marqueurs ne suffisent pas. Voir l’ordre
normatif et les limites dans le [contrat](contract.fr.md#automatisation-et-identité-de-représentation).

Content-Type : type/sous-type, noms des paramètres et valeur charset sont comparés
sans casse ; paramètres quotés acceptés. HTML exige text/html avec charset UTF-8 ;
robots.txt exige text/plain et accepte l’absence de charset (UTF-8 imposé par RFC
9309 §2.3). Les autres encodages, types ambigus, champs ou paramètres répétés
restent inconclusive. Les valeurs des autres paramètres gardent leur casse.

Chaque échange contient `url`, `complete` booléen, `request` et `response` :
chaînes brutes avec lignes CRLF et séparation en-têtes/corps CRLF CRLF. Les en-têtes
répétés sont conservés. Le HTML source est le corps de la réponse finale ; robots.txt
est le corps de sa propre réponse. Exemple de requête :
`GET /page HTTP/1.1\r\nHost: example.com\r\nUser-Agent: googlebot\r\n\r\n`.
Le corps est du texte UTF-8 ; son SHA-256 porte sur ses octets exacts, sans
normalisation d’espaces ou de fins de ligne, après décodage de transfert. Avec
l’interpréteur historique version 2, ce format borné accepte les corps non compressés sans
Transfer-Encoding et un sous-ensemble HTTP/1.1 `chunked`, sans extensions ni trailers.
Les tailles comptent les octets et la terminaison complète est obligatoire ;
Transfer-Encoding avec Content-Length reste inconclusive. Il ne capture ni TLS
ni les octets HTTP/2. [Couverture et migration de l’outil](http-transfer-v2.md).
Les captures ambiguës, tronquées et les chaînes interrompues
restent inconclusive. Tous les sauts doivent être des GET inconditionnels et suivre
exactement Location. Aucun cookie ni Authorization dans ce sous-ensemble.

### Couverture et limites de l’interpréteur

TS01 compare le statut final, puis l’identité selon les critères préalables ci-dessus.
La branche des marqueurs prend en charge text/plain et text/html avec charset
UTF-8 explicite. L’interpréteur 6 utilise un [extracteur TS01 distinct](source-text-v6.md),
avec document clos, balises équilibrées, segments séparés par le balisage,
éléments ordinaires, titre RCDATA et icônes SVG dans une liste bornée, incluant
les styles SVG sans `<` littéral avant leur fermeture, select/options et tableaux
explicitement structurés. Noscript non vide reste indéterminé.
Les zones ambiguës ou non prises en charge rendent toute l’extraction indéterminée.
Le titre et le texte caché par CSS peuvent compter : aucune visibilité rendue
n’est mesurée. `identity-marker-unsupported-element` conserve son attendu normatif
pass et est maintenant résolu. La priorité URL/empreinte/stabilité ne change pas.
La couverture source/rendu TS07 ci-dessous reste distincte ; draft.9 ajoute les profils robots explicites.

TS07-A01 applique
la série Googlebot aux en-têtes finaux et meta robots/googlebot. Restrictions
combinées, casse, none, nofollow et aperçus sont distingués. Il accepte index,
noindex, follow, nofollow, all, none, nosnippet et les paramètres max-snippet,
max-video-preview, max-image-preview ; les aperçus ne sont pas évalués comme objectif.
Indexifembedded, unavailable_after, extension inconnue, autre moteur ou HTML
nécessitant réparation par un navigateur → inconclusive. Les seuls éléments HTML
acceptés sont html/head/body/title/meta/link/p/a/h1/div/span/script/style/br/img,
avec balises explicites correctement emboîtées. Les scripts ne sont pas exécutés.

Le profil historique fixe legacy-exact-v1 de TS07-A02 interprète un robots.txt complet en 200, text/plain UTF-8 : groupes du
robot exact ou `*`, fusion des groupes correspondants, chemins ASCII littéraux,
préfixe le plus long, égalité départagée par Allow. Sitemap est ignoré. Motifs
`*`/`$`, encodage `%`, extension inconnue ou réponse robots autre que 200 →
inconclusive, sans conclure que le RFC impose ce verdict. Ce n’est pas une
implémentation complète du [RFC 9309](https://www.rfc-editor.org/rfc/rfc9309).
Aucun passage ne prouve un accès réel du moteur ou l’indexation.

Une implémentation externe reçoit le même input JSON sur stdin et renvoie un tableau
`[{"rule_id":"TS01-A01","target":"https://example.com/page","outcome":"pass","reason":"…"}]`
sur stdout, couvrant tous les couples demandés. Le comparateur vérifie les verdicts,
pas le texte libre des motifs. Invocation sans shell, avec délai borné :

```sh
python3 conformance/run.py --command 'python3 conformance/evaluate.py'
```

Pour une implémentation partielle, déclarer les règles effectivement testées :

```sh
python3 conformance/run.py --rules TS01-A01,TS01-A02 --command 'python3 mon_adaptateur.py'
```

Sans `--rules`, les treize règles restent exigées. L’option accepte une liste non
vide d’identifiants atomiques connus, sans doublon ; elle restreint `input.rules`
et la matrice attendue, sans transmettre `expected`. Les cas sans règle sélectionnée
ne sont pas exécutés. Toutes les cibles de chaque cas retenu restent obligatoires.
Les résultats supplémentaires, y compris sur une règle non demandée, restent des
erreurs ; les sorties ne sont jamais filtrées pour masquer un désaccord.

`rules` expose la sélection, `available_rules` et `omitted_rules` sa portée ;
`cases`/`rule_target_pairs` comptent les comparaisons exécutées, les champs
`total_*`, `skipped_cases` et `omitted_rule_target_pairs` comptent le reste.
Le corpus complet reste validé (version, matrices, cas contradictoires).
`coverage.by_rule` contient accords, désaccords, couverture réduite, numérateur,
dénominateur et pourcentage des attendus conclusifs pour chaque règle sélectionnée.
Une réussite fournit `claim` : « passes TSEP 0.1.0-draft.9 conformance for
TS01-A01, TS01-A02 ». Publier cette formulation avec les limites/couvertures
réduites, jamais comme conformité globale, d’un profil, d’un contrôle ou d’un site.
Un échec donne `claim: null`. Réussir A01 seule ne valide pas TS01.

Les attendus représentent la vérité normative de ces cas, jamais la sortie
souhaitée du parseur livré. `expected_origin` décrit cette origine rédactionnelle,
sans prétendre à une validation indépendante. Un cas hors sous-ensemble porte
`reference_limit: true`, et chaque couple concerné le répète avec un `basis` motivé.
Le marquage au niveau du cas ne relâche pas les autres couples.

- Accord exact : compté dans `agreements`, y compris un indéterminé normatif.
- Attendu conclusif marqué + résultat inconclusive : accepté mais compté dans
  `coverage.reduced_pairs` et détaillé dans `reduced_coverage`, jamais comme accord.
- Tout autre écart : `disagreements` et `failures`, notamment pass/fail contraire,
  NA contraire, omission, cible supplémentaire ou indéterminé non marqué.

`coverage.percent` = attendus conclusifs correctement résolus / attendus conclusifs
(pass, fail, not-applicable). Les indéterminés normatifs sont exclus de ce ratio ;
ils restent obligatoires et comparés exactement. Les comptes par règle sont dans
`coverage.by_rule`. Une exécution réussie peut donc couvrir moins de 100 % des
attendus conclusifs ; elle ne déclare aucune conformité de contrôle ou de site.
Un adaptateur plus complet peut obtenir l’accord exact là où la référence déclare
une limite. Exemple : `unsupported-robots-wildcard` attend TS07-A02 pass, car `/*?`
ne correspond pas à `/page` (RFC 9309 §2.2.2–2.2.3) ; l’inconclusive de la référence
compte seulement en couverture réduite. TS07-A03 compare maintenant des captures source/DOM fournies selon le
[format de rendu](rendered-states.md). La suite n’émet pas de rapport C : la couverture
des trois règles TS07 et la revue semiAuto restent nécessaires. Les quatre règles TS10 utilisent le [format famille](canonical-families.md), avec
revue humaine du contenu et rapprochement des populations déclarées.

## English

`python3 conformance/run.py` compares computed outcomes from raw inputs against
separately authored expectations in `conformance/cases.json`. All cases are
synthetic; no collection occurs. The historical nine-rule judgment fixtures remain
separate report-consistency tests. Cases declare `id`, `input`, `expected` and a
version-pinned corpus. Only `input` reaches the interpreter. Expected and actual
rule/target matrices must match exactly, without missing, extra or duplicate pairs.
Each rule has pass/fail/inconclusive cases. Exit codes: 0 no disagreements (possibly reduced coverage), 1 difference,
64 invalid input/execution. No C report or global conformity is generated.

To convert one `input` object into a report and evidence, see the
[capture adapter](capture-adapter.md). It retains computed outcomes, including
reference unknowns, without substituting `expected` verdicts.

Interpreter version 3 also accepts [binary input v2](guided-capture.md), with
base64/SHA-256, bounded gzip/deflate decoding and exact content-byte digests.
The historical input v1 and corpus remain preserved.

Input version 1 is `{ "input_version": "1", "rules": [...], "targets": [...] }`.
Rules explicitly select the thirteen IDs above. TS10 targets use the
[family format](canonical-families.md); the fields below describe TS01/07.
Each TS01/07 target has exact HTTP(S) `url`
(no fragment/credentials), zoned `observed_at`, context strings `network`, `bounds`,
`tool`, `tool_version`, structured `intent`, ordered `http` hops, and `robots`
with its own `observed_at` and `http` trace from the final origin's robots.txt.
Separate `access_review` records `observed_at`, `outcome` and `reason`; it must
not predate the HTTP capture.

Intent fields: prior `declared_at`, `public_canonical: true`, `crawler`,
`expected_final_url`, `expected_body_sha256`, `indexing` allow/exclude, optional
`following` allow/disallow/unspecified and `access_basis: "test-client-only"`.
The separate access review records `outcome: "no-obstacle"` and its reason after
examining the capture, outside prior intent; 200 alone does not supply it. Missing/late intent is inconclusive. A `presentation` objective
requires assessment outside this interpreter.

TS01-A02 identity retains prior `expected_final_url` and `expected_body_sha256`.
A different URL fails; matching URL and digest pass. With a changed digest,
`representation: "stable"` fails; otherwise optional `required_markers` and
`forbidden_markers` arrays decide: missing required or present forbidden marker
fails. Pass requires at least one required marker and no violation; absent
forbidden-only markers are inconclusive. Unique nonblank UTF-8 strings are matched
literally and case sensitively in extracted source text. HTML character references
are decoded; comments, script/style, tags and attributes are excluded, without
joining segments across tags or comments. text/plain uses the complete body
without HTML interpretation. No regex or whitespace normalization. A forbidden
marker inside a required one makes intent contradictory. Missing/empty/invalid lists are inconclusive;
representation policies other than stable are unsupported. At the same URL,
markers cannot replace a missing valid digest. See the ordered normative checks
and limits in the [contract](contract.en.md#automation-and-representation-identity).

Content-Type type/subtype, parameter names and charset values are case insensitive;
quoted parameters are accepted. HTML requires text/html with UTF-8 charset;
robots.txt requires text/plain and accepts absent charset (RFC 9309 §2.3 requires
UTF-8). Other encodings, ambiguous types, repeated fields/parameters remain
inconclusive. Other parameter values retain their case.

Each hop has `url`, boolean `complete`, raw `request` and `response` strings using
CRLF lines and a CRLF CRLF boundary. Preserve repeated headers. Source HTML and
robots.txt are their response bodies. The SHA-256 covers exact UTF-8 body bytes,
without whitespace/newline normalization, after transfer decoding. Historical interpreter
version 2 supports uncompressed bodies without Transfer-Encoding and bounded
HTTP/1.1 `chunked` messages without extensions or trailers. Sizes count bytes and
complete termination is required; Transfer-Encoding with Content-Length remains
inconclusive. TLS and HTTP/2 wire captures are unsupported. See
[tool coverage and migration](http-transfer-v2.md). Hops must be
unconditional GETs following Location exactly, without cookies/Authorization.
Ambiguous, incomplete or interrupted captures remain inconclusive.

TS01 compares final status, then identity against the prior criteria above.
The marker branch supports text/plain and text/html with explicit UTF-8 charset.
Interpreter 6 uses a [separate TS01 extractor](source-text-v6.md): closed document,
balanced tags, markup-separated segments, ordinary elements, RCDATA title and
SVG icons in a bounded allowlist, including SVG styles with no literal `<` before
closure, explicit select/options and explicitly structured tables. Nonempty noscript remains unresolved. Ambiguous or unsupported contexts make
the whole extraction inconclusive. Title and CSS-hidden source text may count;
rendered visibility is not measured. `identity-marker-unsupported-element` keeps
its normative pass expectation and is now resolved. URL/digest/stability precedence
is unchanged. The TS07 coverage below remains separate and unchanged.

TS07-A01 implements a
Googlebot subset over final headers and robots/googlebot meta tags: restrictive
combination, case, none, nofollow and previews remain distinct. Supported tokens
are index/noindex/follow/nofollow/all/none/nosnippet and max-snippet,
max-video-preview, max-image-preview parameters; preview objectives are not assessed.
Indexifembedded, unavailable_after, unknown extensions, another engine and HTML
requiring browser recovery are inconclusive. Accepted HTML elements are only
html/head/body/title/meta/link/p/a/h1/div/span/script/style/br/img with explicit,
properly nested tags. Scripts are not executed.

TS07-A02 supports complete 200 text/plain UTF-8 robots responses, exact crawler
or `*` groups, merging matching groups, ASCII literal paths, longest-prefix matching
and Allow on ties. Sitemap is ignored. Path `*`/`$`, percent encoding, unknown
extensions or non-200 robots responses are inconclusive as implementation limits,
not a claim that RFC 9309 mandates that verdict. This is not a complete RFC
implementation and does not establish actual engine access or indexing.

An external adapter receives one input object on stdin and returns an array of
rule_id/target/outcome/reason objects on stdout. The comparator checks outcomes,
not free-text reasons. Use the command above (or your own adapter); argv is parsed
without a shell, with bounded execution.

For a partial implementation, use `--rules TS01-A01,TS01-A02` with the adapter
command. Without this option, all thirteen rules remain required. The nonempty list
must contain unique known atomic IDs. It restricts `input.rules` and the expected
matrix; `expected` is never sent. Cases without a selected rule are skipped.
All targets in retained cases remain required. Additional outputs, including
unrequested rules, still fail; actual results are never filtered to hide differences.

`rules` lists the selection; `available_rules` and `omitted_rules` expose its scope.
`cases`/`rule_target_pairs` count executed comparisons; `total_*`, `skipped_cases`
and `omitted_rule_target_pairs` expose the remainder. Full corpus validation
(version, matrices, contradictory cases) still runs. `coverage.by_rule` provides
agreements, disagreements, reduced coverage, conclusive numerator/denominator and
percentage per selected rule. Successful output includes `claim`: “passes TSEP
0.1.0-draft.9 conformance for TS01-A01, TS01-A02”. Accompany it with limits/reduced
coverage; never claim global, profile, control or site conformity. Failure gives
`claim: null`. Passing A01 alone does not pass TS01.

Expectations are normative truth for these cases, not the reference parser's
preferred output. `expected_origin` states editorial authorship, not independent
validation. Cases outside the reference subset have `reference_limit: true`;
each affected expected pair repeats that flag and supplies a reasoned `basis`.
A case-level flag never relaxes other pairs.

Exact outcomes count as `agreements`, including normative inconclusive outcomes.
A marked conclusive expectation with an inconclusive result is accepted only as
`coverage.reduced_pairs`, detailed in `reduced_coverage`, never as an agreement.
All other differences count as `disagreements` and `failures`: contrary pass/fail,
contrary NA, missing/extra pairs or unmarked inconclusive results. Duplicates are
invalid. `coverage.percent` divides correctly resolved conclusive expectations by
all conclusive expectations (pass/fail/not-applicable). Normative unknowns are
excluded from that ratio but must still match exactly. Per-rule counts appear in
`coverage.by_rule`. Success may therefore have less than 100% conclusive coverage;
it does not establish control/site conformity. A broader adapter can agree where
the reference cannot decide. `unsupported-robots-wildcard` expects TS07-A02 pass:
`/*?` does not match `/page` under RFC 9309 §2.2.2–2.2.3; reference inconclusive
counts only as reduced coverage.

TS07-A03 now compares supplied source/DOM captures using the
[rendered-state format](rendered-states.md). The suite does not emit a C report:
all three TS07 rules and semiAuto review remain necessary. The four TS10 rules use the [family format](canonical-families.md), supplied
human content review and reconciliation of declared populations.

[Dated reference fingerprints / Empreintes datées des références](source-observations.md).

## TS02 — draft.8

Two additional rules use [the redirect-plan format](redirects.md), with 38 prefrozen contradictory cases. Deux règles supplémentaires utilisent le [format de plan](redirects.md), avec 38 cas contradictoires figés avant code. The prior 216 cases remain unchanged apart from the corpus version.


## TS04 / shared robots — draft.9

TS04 adds a prior origin/profile/resource matrix and required-resource access with
bound supplied reviews. TS07-A02 uses the same reader; absent profile retains the
fixed historical subset. See [format, profiles and bounds](robots.md) and
[migration](migration-draft.9.md). The full corpus now contains 299 cases: all 254
previous cases and 45 prefrozen additions, covering thirteen rules.

TS04 ajoute matrice préalable et accès aux ressources avec revues fournies. Le
lecteur est commun à TS07-A02. Les 299 cas comprennent les 254 cas antérieurs et
45 ajouts figés ; aucune observation réelle du moteur n'est revendiquée.
