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

Migration requires new v2 intent and a new assessment. Explicit v1 intent retains
v1 interpretation; replay is never labelled a fresh collection. The TS09 reader
`url-exclusion-observed-v2` explicitly retains v1 semantics in this candidate,
avoiding an unqualified normative TS09 change.

Official source checked on 25 October 2026:
[Google robots rules](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag).
Google documents comma-separated lists and separate fields/tags. Space-only
lists remain unknown in this profile; this does not predict Google’s actual behaviour.
