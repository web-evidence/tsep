# TSEP 0.3.0-draft.9 — candidat R-077 / R-077 candidate

## Français

Candidat local du 25 octobre 2026, non publié et non qualifié pour diffusion.
Seul TS07-A01 change normativement ; TS07 porte la version de règle draft.9.
Les tests ciblés ne constituent pas la qualification complète. Aucun tag,
archive publiée ou dossier existant n’est remplacé.

Les nouvelles attentes peuvent déclarer `directive_policy=google-indexing-2026-10-v2`.
Ce profil sépare les règles par virgules, ou combine des champs/balises distincts.
Une liste telle que `noindex nofollow` reste entière et est signalée comme
« syntaxe non documentée ». Seule preuve disponible : NT, jamais un C ou NC
inféré en inventant les séparateurs. Un `noindex` valide dans un autre champ
reste décisif : NC pour une page destinée à apparaître, C sur le seul critère
d’exclusion pour une page destinée à être exclue. Les critères d’accès A02 et
de rendu A03 restent indépendants et ne sont jamais déduits de ce constat.

Les espaces dans les paramètres valides et les dates restent autorisés. La
virgule d’une date RFC 822/850 est conservée seulement dans `unavailable_after`.
La comparaison utilise la date de capture. Une règle ajoutée à une date sans
virgule ne devient pas une date valide. Les portées de robots et leurs changements
restent explicites ; une règle propre à un autre robot ne s’applique pas à Googlebot.

Limites assumées : même `index follow` reste NT sans preuve indépendante ; aucune
seconde lecture n’invente des séparateurs par espaces. Une portée telle que
`otherbot: noindex googlebot: noindex` reste inconnue avant de filtrer les autres
robots. Les appels internes doivent fournir le profil explicitement.

Le lecteur v2 consomme la valeur entière des dates. Il prend en charge les dates
ISO étendues `AAAA-MM-JJ`, avec heure facultative `HH:MM[:SS[.fraction]]` (six
décimales au maximum), puis `Z` ou un décalage `±HH:MM` facultatif ; et les formes
RFC à jour/mois anglais/année, séparées par espaces ou tirets, avec heure, secondes
facultatives et fuseau UTC/GMT/UT, américain fixe ou `±HHMM`. Les douze mois
anglais sont seuls reconnus ; une autre abréviation plausible reste NT.
Toute année RFC à deux chiffres reste hors du profil v2 (NT), même si le jour
de semaine ou le calendrier paraît lever l’ambiguïté, et même pour `31 Feb 50`.
Seules les années à quatre chiffres sont évaluables. Le lecteur ne simule ni
choix de siècle ni comportement permissif/strict attribué à Google. Un `noindex`
valide indépendant conserve sa valeur probante. Cette limite volontaire remplace
les hypothèses des candidats non publiés précédents ; les quinze attentes
révisées sont détaillées dans `provenance/ts07-draft9-review3-expectation-delta.json`,
avec entrées inchangées et empreintes avant/après.
Une date sans fuseau reste NT à moins de 24 heures de la capture. Une date
calendaire impossible est ignorée ; un format plausible non pris en charge
(`20201021`, décalage ISO `+0000`, semaine ISO), un suffixe ou un saut de ligne
reste NT. Cela ne prétend pas que Google ignore ces formats. Le parseur v1 reste
inchangé, y compris ses limites historiques ; il n’est pas un lecteur v2.
Les secondes intercalaires, l’heure ISO 24:00, l’année zéro et un jour de semaine
contradictoire restent hors périmètre (NT). Les décalages `-0000` (RFC5322 §3.3)
et `-00:00` (RFC3339 §4.3) désignent un instant UTC connu ; seul le décalage local
est inconnu. La date expire strictement après l’instant indiqué : l’égalité avec
la capture ne constitue pas une expiration. Un profil non pris en charge reste
NT, y compris dans le raccourci de lecture des en-têtes HTTP.

Migration explicite : créer une nouvelle attente v2, puis une nouvelle évaluation.
Les attentes v1 restent interprétées selon v1 lorsqu’elles le déclarent ; aucune
relecture automatique de leurs preuves n’est présentée comme une nouvelle collecte.
Le lecteur TS09 `url-exclusion-observed-v2` reste lié à v1 dans ce candidat pour
ne pas introduire un changement normatif TS09 non qualifié.

Source officielle consultée le 25 octobre 2026 :
[Google, directives robots](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag).
Google documente les listes à virgules et les champs/balises séparés ; le traitement
de listes à espaces seuls reste inconnu dans ce profil. Il ne s’agit pas d’une
affirmation sur ce que Google fera réellement d’une syntaxe non documentée.

## English

Local candidate dated 25 October 2026, unpublished and not release-qualified.
Only TS07-A01 changes normatively; TS07 uses rule version draft.9. Targeted tests
are not full qualification. No published tag, archive or existing evidence is replaced.

New intent may declare `directive_policy=google-indexing-2026-10-v2`. Rules are
comma-separated or supplied in separate fields/tags. A list such as
`noindex nofollow` remains one item and is reported as undocumented syntax.
As the only evidence it yields NT, without inventing separators to produce C or NC.
An independently valid `noindex` remains decisive: NC for intended appearance,
or C for the exclusion criterion only. Access A02 and rendering A03 remain separate.

Valid parameter/date spaces are retained. An RFC 822/850 weekday comma is retained
only inside `unavailable_after`; dates are compared with capture time. A rule
appended to a date without a comma does not become a valid date. Crawler scopes
and scope switches remain explicit; another crawler’s rules do not govern Googlebot.

Declared limitations: even `index follow` stays NT without independent evidence;
no second reading invents whitespace separators. A header such as
`otherbot: noindex googlebot: noindex` remains unknown before foreign crawler
filtering. Internal calls must supply the profile explicitly.

The v2 date reader consumes the entire value. It supports extended ISO dates
`YYYY-MM-DD`, optional `HH:MM[:SS[.fraction]]` time (up to six decimals), and optional
`Z` or `±HH:MM` zone; RFC forms with English day/month/year, spaces or hyphens,
time, optional seconds and UTC/GMT/UT, fixed US or `±HHMM` zones. Only the twelve
English month abbreviations are recognized; other plausible months remain NT.
Every two-digit RFC year is outside profile v2 (NT), even if a weekday or calendar
check appears to resolve it, and even for `31 Feb 50`. Only four-digit years are
assessable. No century choice or permissive/strict Google parser is simulated.
Independent valid `noindex` remains decisive. This deliberate limitation replaces
earlier unpublished candidate assumptions; the fifteen revised expectations are
listed in `provenance/ts07-draft9-review3-expectation-delta.json`, with unchanged
inputs and before/after fingerprints. Zoneless dates remain NT within 24 hours of capture. Impossible
calendar dates are ignored; plausible unsupported formats (`20201021`, ISO
`+0000` offsets, ISO weeks), suffixes and line breaks remain NT. This does not
claim Google ignores those formats. The v1 parser retains its historical behavior
and limitations; it is not silently promoted to v2.
Leap seconds, ISO 24:00, year zero and contradictory weekdays are outside the
supported subset (NT). Negative zero `-0000` (RFC5322 §3.3) and `-00:00`
(RFC3339 §4.3) represent a known UTC instant; only the local offset is unknown.
Expiration requires strictly later capture time; equality does not establish
expiration. An unsupported profile remains NT, including the HTTP-header shortcut.

Migration requires new v2 intent and a new assessment. Explicit v1 intent retains
v1 interpretation; replay is never labelled a fresh collection. The TS09 reader
`url-exclusion-observed-v2` explicitly retains v1 semantics in this candidate,
avoiding an unqualified normative TS09 change.

Official source checked on 25 October 2026:
[Google robots rules](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag).
Google documents comma-separated lists and separate fields/tags. Space-only
lists remain unknown in this profile; this does not predict Google’s actual behaviour.

## Date references / Références des dates

- [RFC5322 §3.3 and §4.3](https://www.rfc-editor.org/rfc/rfc5322): mail-date offsets and two-digit-year convention / décalages et années des dates de courriels.
- [RFC9110 §5.6.7](https://www.rfc-editor.org/rfc/rfc9110.txt): a different rolling HTTP rule for rfc850 dates / règle HTTP glissante différente.
- [RFC3339 §4.3](https://www.rfc-editor.org/rfc/rfc3339): known UTC instant with unknown local offset / instant UTC connu et décalage local inconnu.

These references explain the bounded choices; they do not establish Google's
actual parser. / Ces références expliquent les choix bornés, sans démontrer le
parseur réellement employé par Google.
