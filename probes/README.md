# Bounded HTTP example / Exemple HTTP borné

`http-page.py` adapts the Edikka article's existing Python/curl example. It fetches
one configured canonical page, follows at most five redirects, caps a response at
5 MiB and the request at ten seconds. It checks the final 200, expected final URL,
HTML canonical and a limited subset of Googlebot/noindex directives. It preserves
manual-review outcomes for cases it cannot interpret.

```sh
python3 probes/http-page.py --url https://example.com/page --canonical https://example.com/page
python3 tests/legacy_http_cases.py
```

The first command makes an actual request to the URL you provide; use it only on
an authorized target. The second uses a temporary loopback HTTP server and synthetic
responses, including redirect headers, 404/500, common preview directives, scoped
robots, WordPress/preload Link headers and malformed/ambiguous cases.

Exit codes: 0 = the listed partial checks pass; 1 = an observed mismatch with this
example's assumptions; 2 = execution error or manual review. These codes are **not
the TSEP gate codes**. The output is not a full evidence bundle: temporary response
files are deleted. Capture raw responses, timestamps, environment and commands
separately before using an observation in a TSEP assessment.

| Observation | Possible contribution | Not established |
| --- | --- | --- |
| Final status and URL | TS01 / part of TS02 | All site routes, bot infrastructure |
| Source robots directives | Part of TS07 | robots.txt, rendered directives, actual indexing |
| HTML canonical | Part of TS10 | Sitemap/internal-link agreement or Google-selected canonical |
| Successful CI invocation | Part of TS41 | A complete before/after deployment test policy |

No probe result is automatically promoted to a full-control C. A failure is NC
only after matching the actual control's applicability and intended behavior.
For example, this probe expects one HTML canonical; the protocol can assess other
documented strategies. A successful historical case suite is regression evidence
for this bounded example, not a declaration that all robots/header syntax is covered.

## Français

La sonde conserve l’exemple limité de l’article : un GET, cinq redirections maximum,
5 Mio, dix secondes. Elle ne produit ni audit complet ni paquet de preuves archivé.
Ses codes 0/1/2 diffèrent de ceux de la décision TSEP. Les cas du second appel
utilisent uniquement un serveur temporaire sur 127.0.0.1, sans collecte de sites.

Le tableau indique les contributions possibles, jamais des contrôles entiers
automatiquement conformes. Un échec ne devient NC qu’après rapprochement avec
l’applicabilité et le comportement réellement attendu. Conserver séparément les
réponses brutes et les conditions pour en faire des preuves. Cette suite historique
de non-régression n’est pas la future suite de conformité des 44 contrôles.
