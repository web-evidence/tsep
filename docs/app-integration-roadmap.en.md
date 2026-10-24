# Application integration dossier — TSEP engine 0.2.0-rc.1

## Scope and versioning

This dossier sets the requested order for extending application flows beyond TS02. It does not modify the application repository, claim that new flows are available, or start a control. Priorities are TS01 and TS04, then TS07 and TS10. Reuse the existing engine rules and contracts; do not duplicate the engine or its verdicts in the application.

The application keeps its own version number. Its engine lock should separately record TSEP 0.2.0-rc.1, the imported archive digest and tool identities. Each receipt records both app and engine versions, imported bytes, scope, procedure, evidence/outputs and limitations. A draft.47 archive receipt is not an RC1 receipt.

## Order and prerequisites

| Priority | Control and existing rules | Flow prerequisites | Output and limits |
| --- | --- | --- | --- |
| 1 | TS01-A01/A02 | Dated plan for canonical URLs and collection conditions; attributable final GET, timestamp, status, redirect chain and raw body identity compared with prior criteria. Any acquisition follows an approved plan. | Assess only the received page and response. One IP or capture does not represent Googlebot; missing/ambiguous data stays NT. |
| 2 | TS04-A01/A02 | Before collection, declare origin, client/crawler and interpretation profile, route/resource matrix and expected access. Import raw robots.txt with URL/date/chain and linked resource responses. Keep policy, access and owner review distinct. | Compare policy and access only across declared cells. robots.txt is a crawl protocol, not access protection. Fixtures establish neither Google access nor agent identity. |
| 3 | TS07-A01/A02/A03 | Fix objective and target client; capture final HTTP headers, source HTML, required robots evidence and, when necessary, planned DOM states bound to the same navigation, with date, final URL, browser version and errors. | Separate source, HTTP and rendered directives. Missing or unattributable states remain inconclusive; the resource must be crawlable to read its directives. No Google visit is established. |
| 4 | TS10-A01–A04 | Declare strategy and population/family; bind final URL, HTTP/HTML canonical, sitemap, crawl links and context. Supply DOM captures when rendering changes declarations and a bound human review for A02. | Assess only the declared family’s consistency. canonical is a signal, not a guaranteed directive; a sample proves neither site completeness nor indexing. |

## Import, export and replay

Before enabling the engine, compare version, archive digest, file inventory and schema with the published RC1 archive. Check that import refuses incomplete packages or mismatched digests. Preserve originals and trace their dates and provenance. The export must include every referenced item and a verifiable manifest; offline replay should reproduce the same outcomes without network access or reading private app sources.

Control outcomes C/NC/NA/NT remain distinct from atomic pass/fail/not-applicable/inconclusive outcomes. Missing evidence does not become C or NA. Tool failure, missing review and an SEO contradiction are different facts.

## RC1 state

The documented TS03 r2 app receipt covers the 0.1.0-draft.47 archive, fully synthetic inputs and offline replay. RC1 needs its own import/export/replay receipt tied to the RC1 digest. TS01, TS04, TS07 and TS10 are a future integration plan here, not received flows. This dossier starts no new control or real-site audit.
