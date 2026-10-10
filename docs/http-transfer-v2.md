# Interpreter 2: HTTP transfer coverage / Couverture HTTP de l’interpréteur 2

## Français

L’interpréteur borné et l’adaptateur de captures passent en **version d’outil 2**.
Le protocole reste **0.1.0-draft.7**, son empreinte, ses règles TS01–TS44, le format
de rapport 2, le format d’entrée 1 et la politique de décision restent inchangés.
TS01-A02 exigeait déjà une empreinte après décodage de transfert et de contenu.
Il s’agit d’une extension de couverture de l’outil, pas d’une nouvelle exigence.

La version précédente rendait inconclusive toute réponse avec Transfer-Encoding.
La version 2 interprète les réponses HTTP/1.1 portant un unique champ
`Transfer-Encoding: chunked`, sans compression de contenu, avec tailles
hexadécimales (1 à 16 chiffres), données et CRLF complets, zéro terminal et ligne
vide finale. Les tailles sont comptées en **octets**. Seuls les encadrements de
transfert sont retirés : le SHA-256 du corps décodé conserve tous ses espaces,
fins de ligne et octets UTF-8. La capture d’origine n’est jamais réécrite.

Restent indéterminés : troncature, taille invalide, CRLF absent, octets après la
terminaison, Transfer-Encoding avec Content-Length, champs de transfert répétés,
codages multiples, compression gzip/br, extensions de chunks, trailers et
Transfer-Encoding sur HTTP/1.0. Certains sont valides en HTTP mais hors couverture
de cet outil. Le format d’entrée exige une chaîne UTF-8 valide pour le message
brut entier ; il ne représente pas les coupures de chunks à l’intérieur d’une
séquence UTF-8. Aucun décodage avec remplacement n’est utilisé. La borne du corps
de transfert est 8 Mio ; l’adaptateur borne aussi son fichier JSON entier à 8 Mio.

**Migration :** conserver ancien outil, entrée et rapport ; importer l’entrée
inchangée avec l’adaptateur 2 dans un nouveau dossier. `import.json` nomme
l’adaptateur et l’interpréteur, et conserve les empreintes du code. Comparer les
résultats, pas les octets des rapports émis à des dates différentes. Un résultat
ancien inconclusive peut devenir pass **ou fail** selon le contenu réellement
décodé. Aucune conversion automatique d’un ancien NT en C. L’outil HTTP partagé
est aussi employé par TS07 et TS10 ; cette extension n’exécute pas leurs revues
humaines ni leurs captures de rendu manquantes.

`tests/test_http_transfer.py` couvre préservation des octets, Unicode, tailles,
terminaisons, ambiguïtés et conservation de pass/fail/inconclusive avec et sans
encadrement. Ces données de test sont synthétiques. Le corpus normatif existant
n’est pas modifié. La référence technique est
[RFC 9112 §7.1](https://www.rfc-editor.org/rfc/rfc9112.html#section-7.1), avec
[capture datée](source-observations.md#http-transfer--2026-10-10) ; aucune
conformité HTTP complète n’est revendiquée.

## English

The bounded interpreter and capture adapter advance to **tool version 2**.
Protocol **0.1.0-draft.7**, its fingerprint, TS01–TS44, report format 2, input
format 1 and decision policy are unchanged. TS01-A02 already requires a digest
after transfer/content decoding. This extends tool coverage, not requirements.

Previously any Transfer-Encoding response was inconclusive. Version 2 reads
HTTP/1.1 responses with one `Transfer-Encoding: chunked` field, no content
compression, hexadecimal sizes (1–16 digits), complete data and CRLF, a terminal
zero and final empty line. Sizes count **bytes**. Only transfer framing is removed;
the decoded body digest retains all whitespace, line endings and UTF-8 bytes.
Original captures are never rewritten.

Truncation, invalid sizes, missing CRLF, trailing bytes, Transfer-Encoding with
Content-Length, repeated transfer fields, multiple codings, gzip/br, chunk
extensions, trailers and HTTP/1.0 transfer coding remain inconclusive. Some are
valid HTTP outside this tool's coverage. Input v1 requires the entire raw message
to be a valid UTF-8 string; chunks splitting inside a UTF-8 sequence cannot be
represented. No replacement decoding is used. Transfer bodies are bounded at
8 MiB; the adapter also bounds the entire input JSON file at 8 MiB.

**Migration:** retain the old tool, input and report; import identical input
with adapter 2 into a new directory. `import.json` names both tools and records
source fingerprints. Compare outcomes, not report bytes emitted at different
times. An earlier inconclusive may become pass **or fail**, depending on decoded
content. Old NT reports are never automatically promoted to C. Shared HTTP
interpretation also serves TS07/TS10; missing human reviews or rendered captures
are not supplied by this extension.

`tests/test_http_transfer.py` covers exact bytes, Unicode, sizes, termination,
ambiguities and unchanged pass/fail/inconclusive semantics across framing. These
fixtures are synthetic; the existing normative corpus is unchanged. The technical
reference is [RFC 9112 §7.1](https://www.rfc-editor.org/rfc/rfc9112.html#section-7.1),
with a [dated capture](source-observations.md#http-transfer--2026-10-10).
No complete HTTP compliance is claimed.
