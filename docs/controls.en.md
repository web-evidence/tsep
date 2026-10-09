# TSEP 0.1.0-draft.6 — Controls

Generated from `spec/protocol.json` / Généré depuis `spec/protocol.json`.

Draft / Version de travail. See / Voir [contract](contract.en.md).

## TS01 — The final page returns an actionable HTTP status code.

**Severity**: blocking. **Unit**: page.

**Required inputs**: http, intent.

**Applicability.** Public pages designated as canonical.

**Method.** Send a GET request, follow redirects and record the final status code.

**Acceptance.** Each GET reaches a final 200 response for the expected resource; retain timestamp and redirect chain.

**Evidence.** Intent, complete GET trace and retained body; reasoned findings for A01–A02.

**When NA is allowed.** No public canonical page in the declared scope.

**Limits.** A test from one IP does not prove the response received by Googlebot.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability. TSEP note: the criterion is a final 200; the permanent title inherited from grid 1.1 is broader.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://www.rfc-editor.org/rfc/rfc9110](https://www.rfc-editor.org/rfc/rfc9110)

### TS01-A01 — Final GET returns 200

`TSEP@0.1.0-draft.6:TS01-A01`

**Required inputs**: http, intent.

**Automation / Automatisation**: `automatic`.

**Applicability.** Each public page designated canonical, in the declared request context.

**Method.** Perform a GET without conditional caching; record every hop and final response. Declare agent, headers, cookies/authentication, network, time and time/size/redirect bounds.

**Acceptance.** A complete final 200 response is observed. An observed final 204, 206, 4xx or 5xx contradicts this expectation; HEAD alone or 304 without a representation is insufficient.

**Evidence.** Intent per URL; command and tool version; dated GET trace, URLs and statuses of every hop, final headers and truncation indicators.

**Assumptions.** Request context and bounds are declared before the test; 200 is a TSEP requirement for this population.

**Inconclusive.** Timeout, DNS/TLS failure, interrupted chain, reached bound, incomplete capture, HEAD only or 304 without a retained body: inconclusive, without an inferred SEO fault.

**When NA is allowed.** No atomic exemption when the control applies.

**Limits.** Neither continuous availability nor an actual Googlebot response. An observed chain does not validate TS02.

### TS01-A02 — Expected final resource

`TSEP@0.1.0-draft.6:TS01-A02`

**Required inputs**: http, intent.

**Automation / Automatisation**: `automatic`.

**Applicability.** Each final response whose content can be compared to intent.

**Method.** First compare the final URL with expected_final_url, then the complete body SHA-256 with expected_body_sha256. Fix these references and, if needed, representation: stable or required_markers / forbidden_markers arrays in intent before measurement. No implicit normalization.

**Acceptance.** Different final URL: fail. At the same URL, identical digest: pass. Otherwise, representation: stable requires fail. Otherwise, valid marker lists containing at least one marker yield pass when every required marker is present and every forbidden marker absent, fail otherwise. Without markers or declared stability: inconclusive. HTTP status does not replace this comparison.

**Evidence.** HTTP trace, complete body and dated prior intent containing URL, reference digest and any markers/stability policy; computed values and tool/version. Hash after transfer and content decoding, before any other transformation. Literal case-sensitive UTF-8 markers are searched in the decoded body without DOM extraction or regular expressions.

**Assumptions.** The owner fixes a reference representation before collection; its business relevance remains their responsibility. Comparison is automatic; defining intent is not.

**Inconclusive.** Missing/truncated capture, unknown decoding, missing/invalid reference URL or subsequent intent: inconclusive. At an identical URL, missing/invalid reference digest: inconclusive. If digests differ without declared stability, absent, empty, malformed or contradictory markers: inconclusive. A different URL remains fail even without a reference digest.

**When NA is allowed.** No atomic exemption when the control applies.

**Limits.** A changed digest alone does not prove wrong content. Markers measure neither semantic similarity nor visibility: the owner is responsible for their choice and the reference. Wrong intent can validate wrong content. No engine soft-404 classification, indexing or assessment of undeclared routes.

## TS02 — Redirects are intentional, direct and loop-free.

**Severity**: major. **Unit**: url-set.

**Required inputs**: http, intent.

**Applicability.** Variants and legacy URLs with a declared expected behavior.

**Method.** Test HTTP/HTTPS, host, trailing-slash and legacy URL variants, including the redirect count.

**Acceptance.** Each tested variant follows the approved destination and hop count without a loop; the owner confirms intent.

**Evidence.** One final destination, documented chain and no loop.

**When NA is allowed.** No redirects or expected variants, supported by an inventory.

**Limits.** A valid redirect does not prove the semantic relevance of its destination.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/crawling-indexing/301-redirects](https://developers.google.com/search/docs/crawling-indexing/301-redirects)

## TS03 — Server errors and soft 404s do not replace an explicit response.

**Severity**: major. **Unit**: url-set.

**Required inputs**: http, content, intent.

**Applicability.** Existing, removed and nonexistent routes in scope.

**Method.** Test an existing page, a removed URL and a non-existent URL; compare status and content.

**Acceptance.** Status and content match the three declared cases; tested error pages do not return 200.

**Evidence.** Consistent 4xx/5xx responses and an error template that does not return 200 by default.

**When NA is allowed.** Scope contains no HTTP routing, with a justification.

**Limits.** The final soft-404 classification remains a search-engine decision.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/crawling-indexing/http-network-errors](https://developers.google.com/search/docs/crawling-indexing/http-network-errors)

## TS04 — The effective robots policy matches declared intent.

**Severity**: blocking. **Unit**: host.

**Required inputs**: http, robots, intent.

**Applicability.** Hosts and agents for which a crawl policy is assessed.

**Method.** Fetch robots.txt for each origin; retain status, effective target-bot rules and expected policy. Review errors against the bot documentation without treating every absence as failure.

**Acceptance.** Effective rules and resource access match the declared policy; documented intentional absence may be compatible, without universally requiring 200.

**Evidence.** Origin, bot, status, observed rules or absence, tested resources and expected policy.

**When NA is allowed.** No crawlable host in scope.

**Limits.** robots.txt is a crawling protocol, not an access-control mechanism.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://www.rfc-editor.org/rfc/rfc9309.html](https://www.rfc-editor.org/rfc/rfc9309.html)

## TS05 — A Disallow rule is never presented as a guarantee of deindexing.

**Severity**: blocking. **Unit**: policy.

**Required inputs**: configuration, intent.

**Applicability.** Crawling or exclusion policies in scope.

**Method.** Compare the robots policy, indexing requirements and meta/X-Robots-Tag directives.

**Acceptance.** Crawling, indexing and protection have distinct mechanisms and objectives; no deindexing guarantee relies only on Disallow.

**Evidence.** Separate decisions for crawling, indexing and protection.

**When NA is allowed.** No relevant policy, with scope and decision documented.

**Limits.** A blocked URL may remain known and appear without a snippet.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/crawling-indexing/robots/intro](https://developers.google.com/search/docs/crawling-indexing/robots/intro)

## TS06 — Sensitive areas genuinely deny access at server level.

**Severity**: blocking. **Unit**: route-set.

**Required inputs**: configuration, http, intent.

**Applicability.** Routes declared private or sensitive.

**Method.** Test private routes without a session and verify authentication, authorisation and caching.

**Acceptance.** No sensitive content is delivered to tested anonymous or unauthorized roles, including from cache; list covered routes and roles.

**Evidence.** A 401/403 response or authentication redirect, with no sensitive content delivered.

**When NA is allowed.** An authorized inventory attests to the absence of private routes.

**Limits.** Absence from the index is not proof of confidentiality.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://www.rfc-editor.org/rfc/rfc9110](https://www.rfc-editor.org/rfc/rfc9110)

## TS07 — Robots meta directives and X-Robots-Tag match the page objective.

**Severity**: blocking. **Unit**: page.

**Required inputs**: http, html, intent, robots.

**Applicability.** Documents and resources with a declared indexing objective.

**Method.** Review final headers, source HTML, access and required rendered states under A01–A03.

**Acceptance.** Effective target-bot directives in final headers and HTML match that objective; unknown directives and any necessary rendered states are reviewed.

**Evidence.** One directive or a compatible combination, with no accidental noindex.

**When NA is allowed.** No resource subject to an indexing policy in scope.

**Limits.** The engine must be allowed to crawl the resource to read the directive.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal. Sources checked on 2026-10-09; dated capture fingerprints recorded in docs/source-observations.md.

**References**: [https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag); [https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics); [https://developers.google.com/search/docs/crawling-indexing/block-indexing](https://developers.google.com/search/docs/crawling-indexing/block-indexing); [https://www.rfc-editor.org/rfc/rfc9309](https://www.rfc-editor.org/rfc/rfc9309)

### TS07-A01 — Effective directives and objective

`TSEP@0.1.0-draft.6:TS07-A01`

**Required inputs**: http, html, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Each document with a declared indexing objective, for an explicitly named crawler and context.

**Method.** Inventory all final X-Robots-Tag headers and robots/target-crawler meta tags in source HTML, separate from redirect hops. Apply documented crawler semantics, including duplicates, scope, case, parameters and ignored rules.

**Acceptance.** Combined effects match the declared indexing objective and declared presentation/link restrictions. For Google: an applicable restriction prevails over permission, none includes noindex/nofollow; nofollow or a preview limit alone does not mean noindex. Missing directives are not failure when intent permits indexing.

**Evidence.** Raw repeated headers, source HTML, token/crawler/effect table and dated technical reference. For non-HTML, the html-kind record documents why this surface does not apply, with Content-Type, without inventing HTML.

**Assumptions.** Intent and crawler fixed before review; do not extrapolate Google rules to another engine. For indexifembedded or unavailable_after, include the required embedding context and date.

**Inconclusive.** Missing objective, unknown syntax/scope, partial capture or missing context: inconclusive. A documented ignored directive is recorded, not automatically treated as an error.

**When NA is allowed.** No atomic exemption when the control applies.

**Limits.** Assesses observed declarations, not ingestion or actual indexing. A01 alone does not cover access or rendering. Automation is semiAuto: the bounded interpreter does not cover every syntax, crawler or context; unsupported inputs remain inconclusive and require review.

### TS07-A02 — Access to the directive

`TSEP@0.1.0-draft.6:TS07-A02`

**Required inputs**: http, robots, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Every resource for which directive effects are assessed.

**Method.** Compare effective robots policy and access conditions for the target crawler; distinguish the test client response, explicit blocking and unobserved crawler access.

**Acceptance.** No observed obstacle prevents reading the directive in the declared context. An explicit robots disallow contradicts a strategy relying on reading noindex.

**Evidence.** Robots capture and interpretation for URL/crawler, HTTP trace and access assumptions documented in intent.

**Assumptions.** Effective policy is interpreted under TS04; its HTTP status alone is insufficient. The test context is bounded and does not simulate Googlebot authentication.

**Inconclusive.** Unavailable or ambiguous policy, unresolved challenge, missing capture: inconclusive, never NA for missing access.

**When NA is allowed.** No atomic exemption when the control applies.

**Limits.** No evidence of an actual engine visit; TS04 and other access controls are not globally validated. Automation is semiAuto: the bounded interpreter does not cover every syntax, crawler or context; unsupported inputs remain inconclusive and require review.

### TS07-A03 — Required rendered states

`TSEP@0.1.0-draft.6:TS07-A03`

**Required inputs**: http, html, render, intent.

**Automation / Automatisation**: `semiAuto`.

**Atomic exemption inputs**: intent, http, html.

**Applicability.** Pages whose scripts or states can affect directives, or whose stability is not established.

**Method.** Fix required states, interactions and waiting conditions before capture. Compare final headers and source HTML with each DOM, declaring browser/version, enabled scripts, time, errors and context. Bind each capture to the source response and target. Do not assume the engine renders initially noindex HTML.

**Acceptance.** All required states are documented and compatible with intent in the declared context. A contradiction in a complete, attributable state is fail even if other states are missing. Removing initial noindex with JavaScript does not yield pass: A03 remains inconclusive unless a required state supplies another contradiction; A01 retains its own source verdict.

**Evidence.** Retained headers/source HTML, prior plan, dated raw DOMs with binding digest of the HTTP trace, final URL, context, browser/version, script state, interactions, waiting conditions and errors. Reasoned comparison and limitations; no simulated engine capture.

**Assumptions.** Required states are listed before the test; local and engine rendering remain distinct.

**Inconclusive.** Missing required plan/capture, truncated state, script error, inconsistent source/target/context binding, invalid chronology, uninterpretable directive or late removal of initial noindex: inconclusive without an inferred pass. An established contradiction in another attributable state remains fail.

**When NA is allowed.** Non-HTML or directive stability demonstrated by documented review; intent evidence references this justification and supporting records. No unsupported “no JS” assertion.

**Limits.** semiAuto: the plan and sufficiency of observations require review. The interpreter compares supplied captures; it does not execute JavaScript or establish exhaustive states, TS25, engine rendering or indexing.

## TS08 — The actual indexing status is checked in Search Console.

**Severity**: major. **Unit**: url-set.

**Required inputs**: search-console, intent.

**Applicability.** URLs whose Google indexing state must be established.

**Method.** Use URL Inspection on a representative sample and retain the export or screenshot.

**Acceptance.** Inspection is dated for each selected URL; actual state, crawl access and canonical are recorded against intent, with discrepancies explained.

**Evidence.** Known URL, crawling permission, indexing state and Google-selected canonical documented.

**When NA is allowed.** Google is explicitly out of scope; lack of access alone is insufficient.

**Limits.** A public audit cannot establish this status without property access.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://support.google.com/webmasters/answer/9012289](https://support.google.com/webmasters/answer/9012289)

## TS09 — Intentional exclusions have an owner and a rationale.

**Severity**: minor. **Unit**: policy.

**Required inputs**: configuration, intent.

**Applicability.** Intentionally excluded page families.

**Method.** Tie each excluded family to a rule, owner and review date.

**Acceptance.** Every exclusion in scope has a mechanism, rationale, owner and review date.

**Evidence.** Exclusion register: page type, mechanism, rationale, owner and review.

**When NA is allowed.** No intentional exclusions, with a policy inventory provided.

**Limits.** The business relevance of an exclusion cannot be automated.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/crawling-indexing/block-indexing](https://developers.google.com/search/docs/crawling-indexing/block-indexing)

## TS10 — Each canonical page publishes an absolute, stable and consistent URL.

**Severity**: major. **Unit**: url-set.

**Required inputs**: http, html, sitemap, crawl, intent.

**Applicability.** Families with a declared canonicalization strategy.

**Method.** Compare the final URL, rel=canonical, sitemap and internal links.

**Acceptance.** Rules A01–A04 establish a consistent preference under the declared strategy; exceptions and absences are justified, not inferred from collection gaps.

**Evidence.** Signals converge on the same canonical URL without a chain.

**When NA is allowed.** No relevant document, supported by an inventory and strategy.

**Limits.** rel=canonical is a strong signal, not a guaranteed directive.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls); [https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics); [https://www.sitemaps.org/protocol.html](https://www.sitemaps.org/protocol.html); [https://www.rfc-editor.org/rfc/rfc8288](https://www.rfc-editor.org/rfc/rfc8288)

### TS10-A01 — Canonical declaration

`TSEP@0.1.0-draft.6:TS10-A01`

**Required inputs**: http, html, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Each family member and its declared canonicalization strategy.

**Method.** List members, preferred URL and expected method; compare final URLs, HTTP Link, HTML rel=canonical and required rendered states. Retain multiple declarations, even identical ones.

**Acceptance.** Present signals and those required by strategy identify the same absolute HTTP(S) URL without a fragment. HTML in head or HTTP Link are accepted; no universal HTML tag requirement. A relative canonical is fail for this TSEP rule without claiming Google cannot interpret it. Retain repeated identical declarations, which may agree; an attributable conflict remains fail despite another missing capture.

**Evidence.** Family inventory in intent; headers and source (or html non-applicability record for non-HTML); extraction with location and method, required DOM attached when needed. Bind each capture to the family, context and date. Declare required methods and DOM states before assessment; bind DOMs to the HTTP trace by fingerprint. A rendering exemption needs a source-bound review and supporting records, not a bare “no JS” claim.

**Assumptions.** Strategy distinguishes preferred canonical and duplicates; comparisons do not silently remove parameters or normalize case or slashes.

**Inconclusive.** Incomplete family/intent, ambiguous Link, truncated document or missing required rendered state: inconclusive.

**When NA is allowed.** No atomic exemption when the control applies.

**Limits.** Relative URLs, placement and convergence are TSEP criteria; engine canonical selection is not observed here.

### TS10-A02 — Direct canonical destination

`TSEP@0.1.0-draft.6:TS10-A02`

**Required inputs**: http, html, intent.

**Automation / Automatisation**: `manual`.

**Applicability.** Every preferred destination in declared families.

**Method.** Test the destination, retain GET and content; verify that any canonical there does not point elsewhere. Compare content with the declared family.

**Acceptance.** The expected destination is directly accessible with 200, without canonical chains or cycles, and compatible content. A duplicate may remain 200 and point to the preferred URL; not every duplicate final URL must equal it.

**Evidence.** Destination trace and body tied to the family; declaration graph and reasoned content comparison. The human compatibility review identifies its author, date, each member compared with the preferred representation, reasoned judgment and exact examined captures by fingerprint. A missing/stale reference or unestablished comparison prevents pass.

**Assumptions.** Content similarity is assessed in business context without a universal similarity threshold.

**Inconclusive.** Uncollected destination, timeout or incomparable content: inconclusive. An observed 404/5xx, cycle or hop is a contradiction.

**When NA is allowed.** No atomic exemption when the control applies.

**Limits.** A successful GET does not prove Google will select this URL; no temporal stability is inferred from one instant. A comparator can check the supplied review’s bindings and coverage; it does not turn that judgment into automatic content comparison.

### TS10-A03 — Sitemap agreement

`TSEP@0.1.0-draft.6:TS10-A03`

**Required inputs**: sitemap, intent.

**Automation / Automatisation**: `semiAuto`.

**Atomic exemption inputs**: intent, sitemap.

**Applicability.** Families associated with a sitemap under the declared strategy.

**Method.** Compare entries from all sitemaps/indexes required for the family and preferred URL; retain exclusions justified by strategy. Reconcile captures of each index and all expected children. An observed failure remains fail when another branch is missing; an omission becomes fail only after the declared population has been fully examined.

**Acceptance.** Observed and required entries agree with declared preference; a duplicate published as a competing canonical without justification is fail.

**Evidence.** Raw sitemaps and index coverage, family/entry mapping and justification of omissions.

**Assumptions.** Sitemap scope is declared; absence is not inferred from a 404 at one guessed path.

**Inconclusive.** Incomplete index, unavailable expected sitemap or unknown strategy: inconclusive.

**When NA is allowed.** No sitemap used for this family, established by documented strategy and inventory. Retain a sitemap record explaining absence; no whole-TS10 NA.

**Limits.** Sitemap = published preference, not engine selection or an exhaustive site inventory.

### TS10-A04 — Internal-link agreement

`TSEP@0.1.0-draft.6:TS10-A04`

**Required inputs**: crawl, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Each family and declared source-page population.

**Method.** Extract links from the announced population; compare destinations and documented exceptions with canonical preference.

**Acceptance.** All assessed links follow strategy; no unexplained competing destination. Zero links can satisfy the rule only when the announced population is fully examined. An attributable competing link remains fail even if another source page or required state is missing.

**Evidence.** Crawl export with source URL, href, destination, pages actually visited, failures and exclusions; reconciliation with the declared population. Retain source HTML and DOMs needed for extraction, bound to their traces, contexts and dates; a rendering exemption is reviewed and supported. Exceptions identify source, destination and reason.

**Assumptions.** The crawl checks a declared population; it does not by itself prove that population exhaustive.

**Inconclusive.** Missing source pages, unexamined links or absent crawl: inconclusive, never success from zero results.

**When NA is allowed.** No atomic exemption when the control applies.

**Limits.** No extrapolation to external links, pages outside the population or future dates.

## TS11 — Genuine duplicate variants converge without hiding distinct pages.

**Severity**: major. **Unit**: url-set.

**Required inputs**: content, html, intent.

**Applicability.** Identified duplicate or variant families.

**Method.** Sample parameters, pagination, filters and print versions; compare content and canonicals.

**Acceptance.** Each mapping is justified by content comparison; no tested distinct page is unintentionally consolidated.

**Evidence.** Documented mapping between each duplicate and its relevant canonical.

**When NA is allowed.** No variants or duplication identified after a documented inventory.

**Limits.** Computed similarity does not replace an editorial decision.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)

## TS12 — Google’s selected canonical is compared with the declared canonical.

**Severity**: major. **Unit**: url-set.

**Required inputs**: search-console, html, intent.

**Applicability.** URLs whose Google canonical must be compared with the declared canonical.

**Method.** Inspect priority URLs and record the user-declared and Google-selected canonicals.

**Acceptance.** Both values are timestamped and compared; each discrepancy has an assessment and a decision.

**Evidence.** Agreement or a qualified, addressed divergence.

**When NA is allowed.** Google explicitly out of scope; missing access is NT.

**Limits.** Google’s selected canonical can change after recrawling.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://support.google.com/webmasters/answer/9012289](https://support.google.com/webmasters/answer/9012289)

## TS13 — The sitemap contains only useful absolute canonical URLs.

**Severity**: major. **Unit**: sitemap-set.

**Required inputs**: sitemap, http, html, intent.

**Applicability.** Sitemaps used for the URLs in scope.

**Method.** Parse every sitemap, count URLs and compare status, canonical and indexability.

**Acceptance.** Each scoped entry resolves, is canonical under the strategy and is intended for indexing; exclusions and sample limits are explicit.

**Evidence.** Inventory without redirects, 4xx responses, noindex pages or duplicate canonicals.

**When NA is allowed.** No sitemap used, with inventory and decision provided.

**Limits.** Sitemap inclusion does not guarantee indexing.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)

## TS14 — lastmod reflects a significant change to the page.

**Severity**: minor. **Unit**: sitemap-set.

**Required inputs**: sitemap, change-history.

**Applicability.** Sitemaps containing lastmod.

**Method.** Compare lastmod with editorial history or a significant content deployment.

**Acceptance.** Each tested date maps to a traceable significant change; file generation alone is insufficient.

**Evidence.** ISO 8601 timestamp tied to an actual change, not file generation.

**When NA is allowed.** No lastmod declared; its absence is not itself a defect.

**Limits.** The engine may ignore a lastmod it considers unreliable.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/blog/2023/06/sitemaps-lastmod-ping](https://developers.google.com/search/blog/2023/06/sitemaps-lastmod-ping)

## TS15 — Sitemap size and segmentation limits are respected.

**Severity**: major. **Unit**: sitemap-set.

**Required inputs**: sitemap.

**Applicability.** Declared sitemap files and indexes.

**Method.** Check uncompressed size, URL count, sitemap indexes and encoding.

**Acceptance.** Encoding and syntax are valid; uncompressed size and entry-count limits are met for each file type.

**Evidence.** No more than 50,000 URLs and 50 MB uncompressed per sitemap.

**When NA is allowed.** No sitemap used in scope.

**Limits.** A valid file can still cover the wrong editorial scope.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://www.sitemaps.org/protocol.html](https://www.sitemaps.org/protocol.html)

## TS16 — Every important page receives at least one crawlable internal link.

**Severity**: major. **Unit**: url-set.

**Required inputs**: crawl, inventory, intent.

**Applicability.** Pages identified as important in an inventory.

**Method.** Crawl from public entry points and list pages with no incoming HTML link.

**Acceptance.** Every selected page has at least one resolvable incoming HTML link from an internal page; source and destination are archived.

**Evidence.** Link source, destination, anchor and destination status.

**When NA is allowed.** No relevant important page, with justification and inventory provided.

**Limits.** The presence of a link does not prove its editorial value.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/crawling-indexing/links-crawlable](https://developers.google.com/search/docs/crawling-indexing/links-crawlable)

## TS17 — Essential links use an a element with a resolvable href.

**Severity**: major. **Unit**: page.

**Required inputs**: html, render, intent.

**Applicability.** Navigation destinations declared essential.

**Method.** Compare source and rendered DOM; identify buttons, onclick handlers and anchors without href.

**Acceptance.** Every tested essential destination has an a link with a resolvable href at the observed stage; source and rendered stages are distinguished.

**Evidence.** A crawlable HTML link to every essential destination.

**When NA is allowed.** No relevant navigation, with a justified scope.

**Limits.** Crawlability guarantees neither indexing nor rankings.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/crawling-indexing/links-crawlable](https://developers.google.com/search/docs/crawling-indexing/links-crawlable)

## TS18 — Depth and orphan pages are measured within an explicit scope.

**Severity**: major. **Unit**: url-set.

**Required inputs**: crawl, sitemap, inventory, intent.

**Applicability.** Declared reference inventory with crawl boundaries.

**Method.** Compare crawl, sitemap and CMS export; qualify every difference.

**Acceptance.** Crawl and inventory are reconciled; observed depth and orphan candidates are assessed by family; a crawl alone never establishes completeness.

**Evidence.** Identified and dated reference inventory, crawl boundaries, incoming links, observed depths and assessed differences.

**When NA is allowed.** No relevant navigation graph, with a justification; a missing inventory means NT.

**Limits.** No universal depth guarantees rankings.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/crawling-indexing/links-crawlable](https://developers.google.com/search/docs/crawling-indexing/links-crawlable)

## TS19 — Parameters, filters and calendars do not create an infinite URL space.

**Severity**: major. **Unit**: url-set.

**Required inputs**: crawl, configuration, intent.

**Applicability.** Parameters, filters, calendars and other combinatorial URL spaces.

**Method.** Group URLs by pattern, count combinations and look for crawl traps.

**Acceptance.** Each tested pattern has a navigation/indexing policy; observed limits and traps are explained without inferring actual crawl volume.

**Evidence.** Indexing and navigation rule for each parameter pattern.

**When NA is allowed.** Inventory attesting to the absence of such patterns.

**Limits.** The actual crawled volume requires logs or Search Console.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/crawling-indexing/url-structure](https://developers.google.com/search/docs/crawling-indexing/url-structure)

## TS20 — The URL structure is readable, stable and correctly encoded.

**Severity**: minor. **Unit**: url-set.

**Required inputs**: crawl, configuration, intent.

**Applicability.** Published URL patterns.

**Method.** Identify spaces, fragments, encoded characters, case and volatile identifiers.

**Acceptance.** Encoding, case, stability and variations match declared rules; no observed unintended variant is left without a decision.

**Evidence.** Documented URL patterns and no unintended variants.

**When NA is allowed.** No public URL in scope.

**Limits.** A readable URL is not sufficient evidence of SEO performance.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/crawling-indexing/url-structure](https://developers.google.com/search/docs/crawling-indexing/url-structure)

## TS21 — Discovered but unindexed URLs are investigated by family.

**Severity**: major. **Unit**: url-set.

**Required inputs**: search-console, logs, sitemap, intent.

**Applicability.** Families reported as discovered or crawled but not indexed.

**Method.** Segment the Pages report by template and compare it with sitemaps and logs.

**Acceptance.** Each selected family has a documented diagnosis, a testable hypothesis and a decision; unproven causality is disclosed.

**Evidence.** Hypothesis per family, URL sample and post-fix result.

**When NA is allowed.** A dated report contains no relevant family, or Google is explicitly excluded.

**Limits.** A Search Console label describes a state, not always its cause.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://support.google.com/webmasters/answer/7440203](https://support.google.com/webmasters/answer/7440203)

## TS22 — Each hreflang variant points to an indexable canonical URL.

**Severity**: major. **Unit**: locale-cluster.

**Required inputs**: hreflang, http, html, intent.

**Applicability.** Localized variant clusters using hreflang.

**Method.** Parse HTML, HTTP or sitemap annotations and resolve every URL.

**Acceptance.** Each cluster target is accessible, intended for indexing and consistent with its canonical; language/region codes are checked.

**Evidence.** Valid language/region, 200 response and consistent canonical.

**When NA is allowed.** No hreflang cluster in scope, with an inventory provided.

**Limits.** hreflang helps targeting; it does not replace genuinely localized content.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/specialty/international/localized-versions](https://developers.google.com/search/docs/specialty/international/localized-versions)

## TS23 — hreflang annotations are reciprocal and include the current page.

**Severity**: major. **Unit**: locale-cluster.

**Required inputs**: hreflang, intent.

**Applicability.** Declared hreflang clusters.

**Method.** Build variant clusters and verify return links and self-references.

**Acceptance.** All pairs in the declared cluster are reciprocal and every variant includes itself; cluster boundaries are retained.

**Evidence.** Complete reciprocal cluster with no conflicting URL.

**When NA is allowed.** No hreflang cluster in scope.

**Limits.** A valid cluster does not prove the engine will always serve the expected variant.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/specialty/international/localized-versions](https://developers.google.com/search/docs/specialty/international/localized-versions)

## TS24 — x-default represents a neutral destination or an explicit default variant.

**Severity**: minor. **Unit**: locale-cluster.

**Required inputs**: hreflang, http, intent.

**Applicability.** Clusters where x-default is declared or required by policy.

**Method.** Check its presence and role in every relevant multilingual cluster.

**Acceptance.** The destination is accessible and matches the selection flow or the deliberate default variant.

**Evidence.** Documented, accessible x-default URL consistent with the journey.

**When NA is allowed.** No x-default required or declared; retain the policy justification.

**Limits.** x-default is not mandatory in every case.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/specialty/international/localized-versions](https://developers.google.com/search/docs/specialty/international/localized-versions)

## TS25 — Critical content exists in source HTML or becomes observable after rendering.

**Severity**: blocking. **Unit**: page.

**Required inputs**: html, render, intent.

**Applicability.** Templates whose critical elements are listed.

**Method.** List critical elements, then compare source HTML and rendered DOM under declared conditions. Optional Google inspection is a separate additional observation.

**Acceptance.** Every critical element is observed at the declared source or rendered stage; engine, version and conditions are retained; no equivalence with Google is inferred.

**Evidence.** Title, content, links, canonical and structured data present at the right stage.

**When NA is allowed.** No relevant HTML document in scope.

**Limits.** A local browser does not reproduce Google’s rendering exactly.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)

## TS26 — Resources required for rendering are neither blocked nor failing.

**Severity**: major. **Unit**: page.

**Required inputs**: http, render, robots, intent.

**Applicability.** Resources needed to render the tested templates.

**Method.** Inspect network activity, robots rules, CSP and console errors on priority templates.

**Acceptance.** No tested critical resource is prevented by network error, robots policy or CSP; console and network evidence are retained.

**Evidence.** Critical resources accessible and no error removes essential content.

**When NA is allowed.** No dependent rendering resource, supported by an inventory.

**Limits.** An error-free console does not prove indexing.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)

## TS27 — SPA states and routes produce shareable URLs and consistent server responses.

**Severity**: major. **Unit**: route-set.

**Required inputs**: http, render, intent.

**Applicability.** Application routes or SPA states intended for indexing.

**Method.** Open routes directly and test refresh, history, canonical and HTTP status.

**Acceptance.** Direct opening, refresh and history preserve the expected URL, content, status and signals for each selected route.

**Evidence.** Each indexable view has its own URL, 200 response, content and signals.

**When NA is allowed.** No relevant application or SPA route.

**Limits.** Choosing SSR, CSR or SSG is not in itself an SEO guarantee.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/crawling-indexing/javascript/fix-search-javascript](https://developers.google.com/search/docs/crawling-indexing/javascript/fix-search-javascript)

## TS28 — The document exposes an understandable HTML structure independently of appearance.

**Severity**: major. **Unit**: page.

**Required inputs**: html, render, intent.

**Applicability.** HTML documents in scope.

**Method.** Inspect title, language, main landmark, heading levels, links and labels on a sample.

**Acceptance.** Title, language, structure, navigation and labels match the content and its use; human review is recorded without an accessibility certification.

**Evidence.** Logical structure, one identifiable main subject and accessible components.

**When NA is allowed.** No relevant HTML document.

**Limits.** Syntax validity alone proves neither quality nor relevance.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://html.spec.whatwg.org/](https://html.spec.whatwg.org/)

## TS29 — Essential content remains available when scripts or styles fail.

**Severity**: major. **Unit**: page.

**Required inputs**: html, render, intent.

**Applicability.** Flows whose essential content and navigation are defined.

**Method.** Test source HTML, disabled JavaScript and degraded network conditions.

**Acceptance.** Blocked-script and degraded-style scenarios preserve declared functions or an actually tested fallback.

**Evidence.** Primary information and navigation remain available, or a fallback is documented.

**When NA is allowed.** No relevant web flow, with a justification.

**Limits.** Acceptable degradation depends on the component’s function.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)

## TS30 — Essential metadata is unique, visible and consistent with the page.

**Severity**: major. **Unit**: page.

**Required inputs**: html, content, intent.

**Applicability.** Pages whose editorial metadata is assessed.

**Method.** Compare title, description, H1, Open Graph and main content by template.

**Acceptance.** Present metadata describes content without contradiction; uniqueness and duplication are assessed within the declared corpus, with human review.

**Evidence.** Consistent topic and promise without mechanical duplication.

**When NA is allowed.** No document with relevant editorial metadata.

**Limits.** Google may rewrite the title link or snippet in search results.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/appearance/title-link](https://developers.google.com/search/docs/appearance/title-link)

## TS31 — JSON-LD describes entities that are visible and appropriate to the content.

**Severity**: major. **Unit**: page.

**Required inputs**: structured-data, content, intent.

**Applicability.** Documents publishing structured data.

**Method.** Compare each important property with visible content and type-specific guidance.

**Acceptance.** Examined syntax and properties match visible facts and the selected type; no fabricated data is observed.

**Evidence.** Valid, consistent graph with no invented entity or rating.

**When NA is allowed.** No structured data published in scope.

**Limits.** Valid markup guarantees neither a rich result nor higher rankings.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/appearance/structured-data/sd-policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)

## TS32 — Stable @id values connect the same entities without creating duplicates.

**Severity**: minor. **Unit**: graph.

**Required inputs**: structured-data, intent.

**Applicability.** Graphs using entity identifiers.

**Method.** Build the graph and identify unnamed nodes, variable identifiers and duplicates.

**Acceptance.** The same entities retain identifiers across the corpus; graph references resolve and duplicates are assessed, without requiring all types named in the legacy grid.

**Evidence.** Archived graph, inventory of present entities and identifiers, assessed references and duplicates.

**When NA is allowed.** No relevant graph with identifiers.

**Limits.** Schema.org defines a vocabulary; interpretation depends on the consumer.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://schema.org/docs/datamodel.html](https://schema.org/docs/datamodel.html)

## TS33 — Errors, warnings and unsupported uses are distinguished.

**Severity**: minor. **Unit**: page.

**Required inputs**: structured-data, validator-output, intent.

**Applicability.** Markup whose validity and eligibility are assessed.

**Method.** Test Schema.org syntax and Google eligibility separately; record both results.

**Acceptance.** Syntax, vocabulary, engine eligibility and warnings are separated; each result has a tool, version/date and decision.

**Evidence.** Report with no blocking error and qualified warnings.

**When NA is allowed.** No structured markup in scope.

**Limits.** Rich Results Test does not validate the whole Schema.org vocabulary.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data)

## TS34 — Field Core Web Vitals are documented and classified at the 75th percentile.

**Severity**: major. **Unit**: field-cohort.

**Required inputs**: field-data, intent.

**Applicability.** Cohorts with relevant field data.

**Method.** Use an identified field source: CrUX, Search Console or RUM. Record period, device, granularity and population; do not conflate URL and origin.

**Acceptance.** Source, period, granularity, device and LCP/INP/CLS p75 are recorded and classified against cited thresholds; poor values remain visible and inform a decision.

**Evidence.** LCP ≤ 2.5 s, INP ≤ 200 ms and CLS ≤ 0.1 at the 75th percentile for a Good assessment.

**When NA is allowed.** Flows explicitly outside CWV scope; missing data alone means NT.

**Limits.** Missing CrUX data does not mean the page is fast.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://web.dev/articles/defining-core-web-vitals-thresholds](https://web.dev/articles/defining-core-web-vitals-thresholds)

## TS35 — Laboratory tests support diagnosis rather than simulate field data.

**Severity**: minor. **Unit**: page.

**Required inputs**: lab-data, intent.

**Applicability.** Lab performance diagnostics.

**Method.** Retain URL, device, network profile, tool version and detailed metrics.

**Acceptance.** URL, tool/version, device, network and measurements are retained; conclusions remain limited to the lab and tied to a hypothesis.

**Evidence.** Reproducible Lighthouse/WebPageTest report tied to a remediation hypothesis.

**When NA is allowed.** No lab diagnostic planned in this scope.

**Limits.** A Lighthouse score of 100 guarantees neither field CWV nor rankings.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://web.dev/articles/lab-and-field-data-differences](https://web.dev/articles/lab-and-field-data-differences)

## TS36 — Monitoring connects Search Console, logs and deployments to decision dates.

**Severity**: major. **Unit**: release.

**Required inputs**: logs, search-console, change-history, intent.

**Applicability.** Changes whose crawl/indexing follow-up is assessed.

**Method.** Create a pre-change baseline, then verify at D+1, D+7 and D+30 according to risk.

**Acceptance.** Baseline, deployment and risk-based follow-up observations are dated; anomalies and decisions are linked without automatic causal attribution.

**Evidence.** Deployment log, crawl/indexing anomalies and signed decisions.

**When NA is allowed.** No change subject to follow-up within the declared period.

**Limits.** Temporal correlation is not sufficient to attribute a traffic change.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/crawling/docs/crawl-budget](https://developers.google.com/crawling/docs/crawl-budget)

## TS37 — HTTPS, HSTS and embedded resources create neither certificate errors nor mixed content.

**Severity**: major. **Unit**: host.

**Required inputs**: http, tls, render, configuration, intent.

**Applicability.** Hosts and resources of a public web service.

**Method.** Test certificates on public hosts, follow HTTP/HTTPS variants, record Strict-Transport-Security and find HTTP subresources.

**Acceptance.** Certificates and redirects are valid for tested hosts; mixed content is reviewed; the HSTS decision and scope are documented without requiring preload.

**Evidence.** Archived certificates and HTTP chains, reviewed mixed resources, explicit HSTS decision and documented scope.

**When NA is allowed.** No relevant public HTTP service.

**Limits.** HSTS strengthens transport after the policy is received; it fixes neither an invalid certificate nor a poor URL architecture.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://www.rfc-editor.org/rfc/rfc6797](https://www.rfc-editor.org/rfc/rfc6797)

## TS38 — Host, case and trailing-slash variants converge on one rule.

**Severity**: major. **Unit**: url-set.

**Required inputs**: http, html, sitemap, crawl, intent.

**Applicability.** Host, case and slash variants of resources declared equivalent.

**Method.** Replay www/non-www, HTTP/HTTPS, relevant case and trailing-slash variants on sample routes; compare redirect, canonical, sitemap and links.

**Acceptance.** Every tested variant follows the declared rule; redirects, canonicals, sitemaps and links agree without merging distinct resources.

**Evidence.** One stable final URL per resource, no chain and consistent internal signals.

**When NA is allowed.** No relevant variant after an explicit inventory.

**Limits.** Case can be significant depending on the server and application; the rule must be tested, not assumed.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)

## TS39 — The CDN, Vary and geolocation do not serve contradictory SEO signals.

**Severity**: major. **Unit**: delivery-matrix.

**Required inputs**: http, configuration, intent.

**Applicability.** Delivery varying by region, cache, device or negotiation.

**Method.** Compare status, canonical, robots, language and content across regions or cache keys; inspect Vary, geolocation redirects and edge rules.

**Acceptance.** The condition matrix is declared; observed signals follow policy and variants remain accessible under it; untested cells are visible.

**Evidence.** Identical SEO signals for the same URL, or explicitly documented variants accessible to Googlebot.

**When NA is allowed.** Configuration attests to the absence of variation mechanisms.

**Limits.** Two test locations do not cover every route, POP or cache key.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** RFC 9110 defines Vary and HTTP response semantics. Google separately documents locale-adaptive page behavior.

**References**: [https://www.rfc-editor.org/rfc/rfc9110](https://www.rfc-editor.org/rfc/rfc9110); [https://developers.google.com/search/docs/specialty/international/locale-adaptive-pages](https://developers.google.com/search/docs/specialty/international/locale-adaptive-pages)

## TS40 — The hreflang methods in use are complete and consistent.

**Severity**: major. **Unit**: locale-cluster.

**Required inputs**: hreflang, sitemap, http, html, intent.

**Applicability.** Clusters using at least one hreflang method.

**Method.** Identify all published methods, verify clusters and compare annotations when methods coexist.

**Acceptance.** Each used method covers the cluster; if several are published, their annotations are consistent; no single-method requirement is imposed.

**Evidence.** Equivalent reciprocal clusters; when sitemaps are used, valid xhtml namespace and entries per URL.

**When NA is allowed.** No hreflang annotations in scope.

**Limits.** Combining HTML, headers and sitemaps offers no search benefit and increases divergence risk.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/specialty/international/localized-versions](https://developers.google.com/search/docs/specialty/international/localized-versions)

## TS41 — Critical SEO invariants are replayed automatically before and after deployment.

**Severity**: major. **Unit**: release.

**Required inputs**: configuration, ci-output, change-history, intent.

**Applicability.** Deployments subject to project-defined SEO invariants.

**Method.** Run a representative URL set in CI: final status, redirects, robots/noindex, canonical, hreflang, server content, essential links and JSON-LD.

**Acceptance.** Command and version, URL sets, thresholds, before/after outputs and deployment link are retained; a negative case demonstrates failure behavior.

**Evidence.** Versioned command, timestamped output, explicit failure threshold and link to the relevant deployment.

**When NA is allowed.** No relevant deployment or pipeline within the scope and period.

**Limits.** CI validates known invariants; it replaces neither Search Console, logs nor editorial review.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Edikka governance and non-regression control; no single official document prescribes this complete pipeline.

**References**: TSEP / Edikka method.

## TS42 — Each automated agent is governed according to its documented purpose.

**Severity**: major. **Unit**: policy.

**Required inputs**: configuration, operator-docs, intent.

**Applicability.** Automated agents covered by site policy.

**Method.** Map each relevant token to its documented purpose (search, user action, training, advertising or other), a decision and an owner; retain a dated operator source.

**Acceptance.** Each token is linked to its documented purpose, a decision, a dated operator source and an owner; advertising use is distinguished where relevant.

**Evidence.** Table of user agent, purpose, rule, operator source and review date, without conflating live search with training.

**When NA is allowed.** No agent policy in the declared scope, with a reason provided.

**Limits.** A robots directive is declarative; it proves neither the requester’s identity nor compliance by every operator.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.openai.com/api/docs/bots](https://developers.openai.com/api/docs/bots); [https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)

## TS43 — Access for authorized crawlers is tested with the full user-agent string and reconciled with logs.

**Severity**: major. **Unit**: request-set.

**Required inputs**: http, logs, operator-docs, intent.

**Applicability.** Access-policy tests for declared agents.

**Method.** Send a GET request using the documented full user-agent, record status and redirects, find the request in logs and verify identity when the operator publishes a method.

**Acceptance.** Full user-agent string, response and server trace are reconciled; verified or unverified identity is explicit; imitation is never presented as a real visit.

**Evidence.** Command, full string, final response, timestamp, server trace and verified/unverified identity status.

**When NA is allowed.** No agent to test in the declared policy.

**Limits.** Imitating a user agent does not reproduce crawler infrastructure; the test validates application policy, not a real operator visit.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.openai.com/api/docs/bots](https://developers.openai.com/api/docs/bots)

## TS44 — Critical content and evidence remain accessible without undocumented JavaScript execution.

**Severity**: major. **Unit**: page.

**Required inputs**: html, render, content, intent.

**Applicability.** Content intended for declared automated consumers.

**Method.** Compare raw HTML, rendered content and any public machine-readable resource; verify titles, facts, sources, links and update date.

**Acceptance.** Critical elements and their evidence are available in server HTML or a linked public resource; consistency and assumed capabilities are explicit.

**Evidence.** Essential facts and sources in server HTML or a linked public resource, with a consistent version and stable URL.

**When NA is allowed.** No content intended for these consumers in scope.

**Limits.** An llms.txt or Markdown file may ease access, but neither guarantees citation nor rankings.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Partial scope: Google documents JavaScript rendering for Google Search. This control cautiously extends verification to consumers whose rendering capabilities are not uniformly documented.

**References**: [https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics); [https://developers.openai.com/api/docs/bots](https://developers.openai.com/api/docs/bots); [https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)
