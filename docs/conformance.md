# Executable conformance / Conformance exécutable

## Français

`python3 conformance/run.py` compare des résultats calculés depuis des entrées
brutes aux attendus rédigés séparément dans `conformance/cases.json`. Chaque cas
est synthétique. Aucun réseau, aucun site audité. Ce corpus est distinct des
jugements de méthode dans `tests/fixtures/control-cases.json`, qui testent la
cohérence des rapports pour les neuf règles TS01/07/10.

Le corpus lie `protocol_version` à la version livrée. Chaque cas possède `id`,
`input` et `expected`. L’interpréteur reçoit **seulement input** ; `expected` contient
un verdict par couple `rule_id`/`target`. Le comparateur exige une matrice complète,
sans doublon ni résultat supplémentaire, et pass/fail/inconclusive pour chacune
des neuf règles. Un désaccord renvoie 1, une entrée invalide 64 ; 0 signifie aucun désaccord,
avec éventuelle couverture réduite explicitement comptée.
Il n’émet ni rapport C ni conformité globale.

Pour convertir un objet `input` en rapport et preuves, voir
l’[adaptateur de captures](capture-adapter.md). Il conserve les résultats calculés,
y compris les inconnues de référence, sans leur substituer `expected`.

### Format input_version 1

Objet `{ "input_version": "1", "rules": [...], "targets": [...] }`. `rules` liste
explicitement les neuf IDs TS01-A01/A02, TS07-A01/A02/A03 et TS10-A01 à A04.
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
normalisation d’espaces ou de fins de ligne. Ce format borné accepte seulement des
corps non compressés, sans Transfer-Encoding ; il ne prétend pas capturer TLS ou
les octets HTTP/2. Les captures ambiguës, tronquées et les chaînes interrompues
restent inconclusive. Tous les sauts doivent être des GET inconditionnels et suivre
exactement Location. Aucun cookie ni Authorization dans ce sous-ensemble.

### Couverture et limites de l’interpréteur

TS01 compare le statut final, puis l’identité selon les critères préalables ci-dessus.
La branche des marqueurs prend en charge text/plain et text/html avec charset
UTF-8 explicite. Pour HTML, l’extracteur utilise le même ensemble d’éléments borné
ci-dessous, un document clos et des balises emboîtées. Les éléments vides
meta/link/br/img acceptent aussi `/>` ; une telle fermeture sur script/style ou
un autre élément non vide reste indéterminée. Déclarations autres que doctype html,
instructions de traitement et balisage dans title ne sont pas pris en charge.
Le titre et le texte caché par CSS peuvent compter : aucune visibilité rendue
n’est mesurée. `identity-marker-unsupported-element` conserve un attendu normatif
pass pour le texte d’une section valide ; la référence compte ce couple en
couverture réduite. La priorité URL/empreinte/stabilité reste inchangée.

TS07-A01 applique
la série Googlebot aux en-têtes finaux et meta robots/googlebot. Restrictions
combinées, casse, none, nofollow et aperçus sont distingués. Il accepte index,
noindex, follow, nofollow, all, none, nosnippet et les paramètres max-snippet,
max-video-preview, max-image-preview ; les aperçus ne sont pas évalués comme objectif.
Indexifembedded, unavailable_after, extension inconnue, autre moteur ou HTML
nécessitant réparation par un navigateur → inconclusive. Les seuls éléments HTML
acceptés sont html/head/body/title/meta/link/p/a/h1/div/span/script/style/br/img,
avec balises explicites correctement emboîtées. Les scripts ne sont pas exécutés.

TS07-A02 interprète un robots.txt complet en 200, text/plain UTF-8 : groupes du
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

Sans `--rules`, les neuf règles restent exigées. L’option accepte une liste non
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
Une réussite fournit `claim` : « passes TSEP 0.1.0-draft.7 conformance for
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

Input version 1 is `{ "input_version": "1", "rules": [...], "targets": [...] }`.
Rules explicitly select the nine IDs above. TS10 targets use the
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
without whitespace/newline normalization. Only uncompressed bodies without
Transfer-Encoding are supported, not TLS or HTTP/2 wire captures. Hops must be
unconditional GETs following Location exactly, without cookies/Authorization.
Ambiguous, incomplete or interrupted captures remain inconclusive.

TS01 compares final status, then identity against the prior criteria above.
The marker branch supports text/plain and text/html with explicit UTF-8 charset.
For HTML, extraction uses the same bounded element set below, a closed document
and nested tags. Void meta/link/br/img also accept `/>`; self-closing script/style
or other non-void tags remain inconclusive. Declarations other than doctype html,
processing instructions and markup inside title are unsupported. Title and
CSS-hidden text may count; rendered visibility is not measured.
`identity-marker-unsupported-element` retains normative pass for valid section
text; the reference counts this pair as reduced coverage. URL/digest/stability
precedence is unchanged.

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
command. Without this option, all nine rules remain required. The nonempty list
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
0.1.0-draft.7 conformance for TS01-A01, TS01-A02”. Accompany it with limits/reduced
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
