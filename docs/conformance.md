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
des neuf règles. Une divergence renvoie 1, une entrée invalide 64, un accord 0.
Il n’émet ni rapport C ni conformité globale.

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

TS01 compare le statut final, puis l’URL et l’empreinte attendues. TS07-A01 applique
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

Les décisions attendues incluent les limites du sous-ensemble livré. Passer cette
suite établit un accord avec ces cas/version, pas la capacité à analyser toute
page. Un adaptateur plus étendu documente ses différences. TS07-A03 compare maintenant des captures source/DOM fournies selon le
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
Each rule has pass/fail/inconclusive cases. Exit codes: 0 agreement, 1 difference,
64 invalid input/execution. No C report or global conformity is generated.

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

Each hop has `url`, boolean `complete`, raw `request` and `response` strings using
CRLF lines and a CRLF CRLF boundary. Preserve repeated headers. Source HTML and
robots.txt are their response bodies. The SHA-256 covers exact UTF-8 body bytes,
without whitespace/newline normalization. Only uncompressed bodies without
Transfer-Encoding are supported, not TLS or HTTP/2 wire captures. Hops must be
unconditional GETs following Location exactly, without cookies/Authorization.
Ambiguous, incomplete or interrupted captures remain inconclusive.

TS01 compares final status, then exact expected URL/digest. TS07-A01 implements a
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
without a shell, with bounded execution. Passing establishes agreement for this
version's bounded cases only. Extended implementations document differences.
TS07-A03 now compares supplied source/DOM captures using the
[rendered-state format](rendered-states.md). The suite does not emit a C report:
all three TS07 rules and semiAuto review remain necessary. The four TS10 rules use the [family format](canonical-families.md), supplied
human content review and reconciliation of declared populations.

[Dated reference fingerprints / Empreintes datées des références](source-observations.md).
