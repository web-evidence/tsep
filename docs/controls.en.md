# TSEP 0.1.0-draft.41 — Controls

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

`TSEP@0.1.0-draft.41:TS01-A01`

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

`TSEP@0.1.0-draft.41:TS01-A02`

**Required inputs**: http, intent.

**Automation / Automatisation**: `automatic`.

**Applicability.** Each final response whose content can be compared to intent.

**Method.** First compare final URL with expected_final_url, then complete-body SHA-256 with expected_body_sha256. Fix references, any stable policy and markers before measurement. The changed non-stable body branch uses the historical reader unless prior identity_reader: html-tree-markers-v1 selects two whole-document static hypotheses, byte-attributed parsed segments and literal criteria. Hashing still covers the unchanged complete body.

**Acceptance.** Different final URL: fail. At the same URL, identical digest: pass. Otherwise, representation: stable requires fail. Otherwise, under the historical reader, valid markers yield fail if any required marker is missing or any forbidden marker is present. Pass requires at least one required marker, all required markers present and all forbidden markers absent. Forbidden-only markers all absent: inconclusive. Without markers or declared stability: inconclusive. HTTP status does not replace this comparison. Under html-tree-markers-v1, each complete reading compares all markers; both pass gives pass, both fail gives fail, every other pair is inconclusive. URL, hash and stability precedence remains unchanged.

**Evidence.** HTTP trace, complete body and dated prior intent with URL, reference digest and any markers/stability policy; extraction, computed values and tool/version. Hash after transfer and content decoding, before any transformation. Literal case-sensitive markers within each decoded HTML source-text segment: character references resolved; comments, script/style, tags and attributes excluded; segments never concatenated across markup. For text/plain, the entire decoded body. No whitespace normalization or regular expressions. The distinct parsed profile normalizes source CRLF/CR to LF before reference expansion without changing criteria; retain both projections, contexts, positions, reported errors, results and tools. Identical contexts are referenced without removing segments; trees can be reconstructed from the body and exact tools.

**Assumptions.** The owner fixes a reference representation before collection; its business relevance remains their responsibility. Comparison is automatic; defining intent is not. Any selected profile and its criteria are declared in new intent before capture; no silent selection or conversion of historical intents.

**Inconclusive.** Missing/truncated capture, unknown decoding, missing/invalid reference URL or subsequent intent: inconclusive. At an identical URL, missing/invalid reference digest: inconclusive. When digests differ without stability, absent, empty, malformed or contradictory markers, unresolved extraction, or forbidden-only markers all absent: inconclusive. A different URL remains fail even without a reference digest. For the parsed profile: divergent hypotheses, reported parse5 errors, nonblank foreign text outside exclusions, unsupported frames/contexts, unattributable spans, unavailable runtime or exceeded bound remain inconclusive without fallback.

**When NA is allowed.** No atomic exemption when the control applies.

**Limits.** A changed digest alone does not prove wrong content. Source-text extraction measures neither CSS/DOM visibility nor semantic similarity; title and CSS-hidden text may count. Appropriate markers and a correct reference remain the owner’s responsibility. Wrong intent can validate wrong content. No engine soft-404 classification, indexing or undeclared routes. The new profile retains title/textarea/options/hidden text, excludes HTML/SVG scripts/styles and inactive templates; its contract specifies refusals. No browser behavior, complete HTML validity or new Edikka assessment follows.

## TS02 — Redirects are intentional, direct and loop-free.

**Severity**: major. **Unit**: url-set.

**Required inputs**: http, intent.

**Applicability.** Variants and legacy URLs with a declared expected behavior.

**Method.** Test HTTP/HTTPS, host, trailing-slash and legacy URL variants, including the redirect count.

**Acceptance.** Each tested variant follows the approved destination and hop count without a loop; the owner confirms intent.

**Evidence.** One final destination, documented chain and no loop.

**When NA is allowed.** No redirects or expected variants, supported by an inventory.

**Limits.** A valid redirect does not prove the semantic relevance of its destination. The executable reference covers bounded server-side HTTP trajectories; other mechanisms remain unestablished, without exempting the control.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/crawling-indexing/301-redirects](https://developers.google.com/search/docs/crawling-indexing/301-redirects)

### TS02-A01 — Previously approved redirect plan

`TSEP@0.1.0-draft.41:TS02-A01`

**Required inputs**: intent.

**Automation / Automatisation**: `manual`.

**Applicability.** Variants and legacy URLs with a declared expected behavior.

**Method.** Declare source, final destination, allowed redirect and terminal statuses, minimum/maximum redirect count and context. Check the supplied owner review, reasoned, dated between declaration and capture and digest-bound to plan/context.

**Acceptance.** The owner explicitly approves the applicable plan before capture. Explicit rejection bound to the same plan is fail; missing or unattributable review remains inconclusive.

**Evidence.** Plan, context, declared owner identity and role, date, decision, reason, assistance and review provenance; exact digest of examined criteria.

**Assumptions.** The owner supplies criteria before capture; a laboratory author may supply an explicitly synthetic review. A digest binds records without authenticating a person.

**Inconclusive.** Missing, invalid or late plan; absent, unbound or mistimed review; unsupported mechanism. The tool supplies no human approval.

**When NA is allowed.** No atomic exemption. Whole-control non-applicability needs a separate positive inventory; a missing capture does not establish it.

**Limits.** A valid redirect does not prove the semantic relevance of its destination. The executable reference covers bounded server-side HTTP trajectories; other mechanisms remain unestablished, without exempting the control.

### TS02-A02 — HTTP trajectory matches the plan

`TSEP@0.1.0-draft.41:TS02-A02`

**Required inputs**: http, intent.

**Automation / Automatisation**: `automatic`.

**Applicability.** Variants and legacy URLs with a declared expected behavior.

**Method.** Read each attributable GET exchange in order, resolve Location, retain codes and URLs, count redirects and check terminal destination/status. Compare with the pre-capture plan without reconstructing missing responses.

**Acceptance.** The complete chain matches declared destination, statuses and bounds, without a loop. A forbidden type, exceeded maximum, redirect without Location or return to a visited URL is fail as soon as a complete prefix establishes it. Wrong terminal destination/status or insufficient count is fail after an attributable terminal response.

**Evidence.** Original HTTP requests/responses per hop, URL, completeness, client and context; prior plan. Proven contradictions survive later gaps and absent A01 approval.

**Assumptions.** The owner supplies criteria before capture; a laboratory author may supply an explicitly synthetic review. A digest binds records without authenticating a person.

**Inconclusive.** Unfinished chain without contradiction, collection limit, ambiguous Location, unsupported fragment/syntax, conditional/authenticated request, incomplete or unattributable capture. A collection limit does not prove a loop; exceeding an intended maximum is distinct.

**When NA is allowed.** No atomic exemption. Whole-control non-applicability needs a separate positive inventory; a missing capture does not establish it.

**Limits.** A valid redirect does not prove the semantic relevance of its destination. The executable reference covers bounded server-side HTTP trajectories; other mechanisms remain unestablished, without exempting the control.

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

**Method.** Declare origin, crawler, interpretation profile and resource/expected-policy matrix before collection; compare policy and access under A01–A02.

**Acceptance.** Effective rules and resource access match the declared policy; documented intentional absence may be compatible, without universally requiring 200.

**Evidence.** Prior plan, origin, product token and User-Agent, profile, dated raw robots, selected lines, required-resource responses and supplied reviews.

**When NA is allowed.** No crawlable host in scope.

**Limits.** robots.txt is a crawling protocol, not an access-control mechanism.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical references observed October 10, 2026; captures/fingerprints in docs/source-observations.md. Acceptance remains a TSEP proposal.

**References**: [https://www.rfc-editor.org/rfc/rfc9309.html](https://www.rfc-editor.org/rfc/rfc9309.html); [https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec](https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec)

### TS04-A01 — Policy per origin, crawler and resource

`TSEP@0.1.0-draft.41:TS04-A01`

**Required inputs**: http, robots, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Each origin and path matrix whose crawl policy is assessed.

**Method.** Freeze the profile and expected allowances/disallows before observation. Interpret robots status, groups, rules and redirects in the initial origin context; retain the lines determining each outcome.

**Acceptance.** Every observed policy matches declared intent. Unexpected permission and unexpected disallow are contradictions. Intentional absence can be compatible under the profile; no universal 200 requirement.

**Evidence.** Complete matrix, prior intent, context, full robots request/response, profile and reasoned per-resource result.

**Assumptions.** Choose the profile before measurement and keep it fixed for a campaign context; never select the favorable profile after observation. Distinguish RFC model, documented Google policy and unobserved actual cache. Optional directive_crawler=googlebot, frozen before capture, selects the Googlebot policy only on the representation received by crawler, the exact HTTP User-Agent. An explicit robots_policy with case-insensitive googlebot product_token is required, as for TS07. Without the field, historical behavior is preserved. Optional prior google-robotstxt-fields-v2 extends the closed registry of fields outside access scope using pinned google/robotstxt sources; old profiles remain unchanged with no automatic selection.

**Inconclusive.** Absent profile/capture/timing, unsupported syntax or unresolved error/cache: inconclusive. An attributable contradiction on another resource remains fail. Null, unsupported or inconsistent directive_crawler makes policy interpretation inconclusive without falling back to the client group. An independent HTTP contradiction remains limited to the observed client.

**When NA is allowed.** No atomic exemption when the control applies.

**Limits.** semiAuto: matrix and profile suitability remain declared. The reference is bounded to one origin, documented profiles and supplied captures; no engine visit, ingestion or indexing is established. In explicit mode, every robots conclusion concerns the declared product on bytes received by the client, without proving the representation received by Googlebot. An HTTP status contrary to the plan (including 401/403/429/5xx when 200 is expected) remains fail for that client, never evidence of denial to Googlebot. Registry fields and sitemap are recorded without assessing usage preferences, TS42 or indexing and never delimit groups. Other fields and tolerances remain unsupported. Full line numbers and values are retained; reason previews disclose truncation.

### TS04-A02 — Access to required resources

`TSEP@0.1.0-draft.41:TS04-A02`

**Required inputs**: http, robots, intent.

**Automation / Automatisation**: `semiAuto`.

**Atomic exemption inputs**: intent.

**Applicability.** Resources explicitly required in the declared scope, including selected rendering resources.

**Method.** Compare robots policy and HTTP trajectories with planned destinations/statuses, then review responses for obstacles. Bind each supplied review to bytes, dates, intent and context. Retain gaps separately.

**Acceptance.** Every required resource and observed hop is allowed under the profile, reaches its planned response and has no obstacle according to supplied review. Robots blocking, a contradictory response or an evidenced obstacle gives fail even when other evidence is missing.

**Evidence.** Resource plan, robots, complete HTTP traces, reasoned per-resource review with declared identity, date, provenance, assistance and binding digest.

**Assumptions.** A test client does not authenticate as Googlebot; 200 alone cannot establish absence of a challenge. Software does not produce the review or authenticate reviewer identity. Optional directive_crawler=googlebot, frozen before capture, selects the Googlebot policy only on the representation received by crawler, the exact HTTP User-Agent. An explicit robots_policy with case-insensitive googlebot product_token is required, as for TS07. Without the field, historical behavior is preserved. Optional prior google-robotstxt-fields-v2 extends the closed registry of fields outside access scope using pinned google/robotstxt sources; old profiles remain unchanged with no automatic selection.

**Inconclusive.** Missing resource/review, unbound review, incomplete response, uncertainty or unsupported scope: inconclusive without erasing an established contradiction. Null, unsupported or inconsistent directive_crawler makes policy interpretation inconclusive without falling back to the client group. An independent HTTP contradiction remains limited to the observed client.

**When NA is allowed.** No required resource in this scope, established by reasoned inventory review dated before the plan; an unjustified empty list is insufficient.

**Limits.** Inventory sufficiency and human judgment are not fully automated. The reference covers one origin and attributable trajectories; it does not execute rendering or establish actual engine access. In explicit mode, every robots conclusion concerns the declared product on bytes received by the client, without proving the representation received by Googlebot. An HTTP status contrary to the plan (including 401/403/429/5xx when 200 is expected) remains fail for that client, never evidence of denial to Googlebot. Registry fields and sitemap are recorded without assessing usage preferences, TS42 or indexing and never delimit groups. Other fields and tolerances remain unsupported. Full line numbers and values are retained; reason previews disclose truncation.

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

`TSEP@0.1.0-draft.41:TS07-A01`

**Required inputs**: http, html, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Each document with a declared indexing objective, for an explicitly named crawler and context.

**Method.** Inventory all final X-Robots-Tag headers and robots/target-crawler meta tags in source HTML, separate from redirect hops. Apply documented crawler semantics, including duplicates, scope, case, parameters and ignored rules. Optional source_reader=html-tree-directives-v1, declared before capture, constructs two complete static hypotheses without executing scripts; HTML robots/googlebot meta in head/body without foreign ancestors are combined separately with final headers. Ordinary template contents are retained but excluded from active directives. Optional prior presentation_reader=google-preview-intent-v1 compares minimum/maximum permission intervals for text, images and video under the preview-intent contract; extraction and states remain separate.

**Acceptance.** Combined effects match the declared indexing objective and declared presentation/link restrictions. For Google: an applicable restriction prevails over permission, none includes noindex/nofollow; nofollow or a preview limit alone does not mean noindex. Missing directives are not failure when intent permits indexing. For this profile, two pass yield pass, two fail yield fail, every other pair stays inconclusive; never merge directives across alternative hypotheses or confuse them with observed rendered states. For this new profile, all possible values within the intended interval yield pass; all outside on one side yield fail; otherwise inconclusive. Independent contradiction prevails within a reading; existing source consensus and rendered priority remain.

**Evidence.** Raw repeated headers, source HTML, token/crawler/effect table and dated technical reference. For non-HTML, the html-kind record documents why this surface does not apply, with Content-Type, without inventing HTML. This profile also retains both full meta inventories, contexts/namespaces, original tags/body-byte spans, templates, decoding, reported errors, versions and fingerprints in calculated observations linked to the report and compared during replay. The new profile additionally retains ordered HTTP/meta values, scopes, unknowns, dimension decisions and intervals in bound replayed observations.

**Assumptions.** Intent and crawler fixed before review; do not extrapolate Google rules to another engine. For indexifembedded or unavailable_after, include the required embedding context and date. Intent retains crawler as the exact HTTP User-Agent. Optional directive_crawler, frozen before collection and limited here to googlebot, selects directive semantics only for this client representation; it does not describe a response received by Googlebot. Without this field, historical behavior requires crawler=googlebot. Absent source_reader preserves the legacy reader; null/unknown or missing Node 24 never falls back. This profile requires explicit HTTP UTF-8 HTML, consumes one initial BOM and retains unreported repairs by the pinned parser. The bilingual source-directives contract specifies assumptions/bounds without asserting HTML validity. Bounds concern a permission cap, not actual display. Selection and bounds are prior; absent reader preserves historical behavior and no scalar is automatically migrated.

**Inconclusive.** Missing objective, unknown syntax/scope, partial capture or missing context: inconclusive. A documented ignored directive is recorded, not automatically treated as an error. Present but unsupported, null or inconsistent directive_crawler: inconclusive; no favorable fallback. For this profile: incomplete reading, reported error, unsupported encoding, declared open/closed shadow, template for, foreign-context robots metadata, missing content/mixed roles or near form defined by the contract, unknown directive and exceeded bound remain inconclusive. Unreadable HTML never becomes header-only agreement. The preview profile retains unqualified image defaults, max-snippet:0 video interaction, unsupported syntax and exceeded bounds as unknown under the contract’s conservative intervals. Noindex does not give a presentation pass.

**When NA is allowed.** No atomic exemption when the control applies.

**Limits.** Assesses observed declarations, not ingestion or actual indexing. A01 alone does not cover access or rendering. Automation is semiAuto: the bounded interpreter does not cover every syntax, crawler or context; unsupported inputs remain inconclusive and require review. This methodological choice does not simulate Google. No rendering, access, review or TS10 outcome is inferred. The preview profile assesses neither Google display, image availability, data-nosnippet nor licensed, structured-data or AI usage; it produces no review.

### TS07-A02 — Access to the directive

`TSEP@0.1.0-draft.41:TS07-A02`

**Required inputs**: http, robots, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Every resource for which directive effects are assessed.

**Method.** Compare effective robots policy and access conditions for the target crawler; distinguish the test client response, explicit blocking and unobserved crawler access. With explicit directive_crawler, require an explicit robots_policy whose product_token matches googlebot case-insensitively; select that group and never fall back to the browser agent group.

**Acceptance.** No observed obstacle prevents reading the directive in the declared context. Robots disallow contradicts a strategy relying on reading noindex. An attributable HTTP 401/403 remains fail even if robots evidence is missing.

**Evidence.** Robots capture and interpretation for URL/crawler, HTTP trace and access assumptions documented in intent.

**Assumptions.** Policy is interpreted by the shared TS04 reader. A new profile is declared in intent before capture. Without robots_policy, legacy inputs retain the fixed legacy-exact-v1 profile without implicit coverage extension. The client does not authenticate as Googlebot. Intent retains crawler as the exact HTTP User-Agent. Optional directive_crawler, frozen before collection and limited here to googlebot, selects directive semantics only for this client representation; it does not describe a response received by Googlebot. Without this field, historical robots profiles retain their behavior. Optional prior google-robotstxt-fields-v2 extends the closed registry of fields outside access scope using pinned google/robotstxt sources; old profiles remain unchanged with no automatic selection.

**Inconclusive.** Unavailable or ambiguous policy, unresolved challenge, missing capture: inconclusive, never NA for missing access. The new path without a matching profile remains inconclusive. Attributable HTTP 401/403 denial retains precedence.

**When NA is allowed.** No atomic exemption when the control applies.

**Limits.** No evidence of an actual engine visit; TS04 and other access controls are not globally validated. Automation is semiAuto: the bounded interpreter does not cover every syntax, crawler or context; unsupported inputs remain inconclusive and require review. Registry fields and sitemap are recorded without assessing usage preferences, TS42 or indexing and never delimit groups. Other fields and tolerances remain unsupported. Full line numbers and values are retained; reason previews disclose truncation.

### TS07-A03 — Required rendered states

`TSEP@0.1.0-draft.41:TS07-A03`

**Required inputs**: http, html, render, intent.

**Automation / Automatisation**: `semiAuto`.

**Atomic exemption inputs**: intent, http, html.

**Applicability.** Pages whose scripts or states can affect directives, or whose stability is not established.

**Method.** Fix required states, interactions and waiting conditions before capture. Compare final headers and source HTML with each DOM, declaring browser/version, enabled scripts, time, errors and context. Bind each capture to the source response and target. Do not assume the engine renders initially noindex HTML. The DOM reader is chosen before capture: structured-inventory-v2, or the fixed legacy serialization reader when the field is absent. No fallback after refusal. The complete structured inventory retains namespaces, positions, duplicates, serialization and navigation attribution records; no node is removed based on its presumed origin. The optional new source_reader affects only the A01 source prerequisite, never each DOM reader; priority for an attributable rendered contradiction remains unchanged. Optional prior presentation_reader=google-preview-intent-v1 compares minimum/maximum permission intervals for text, images and video under the preview-intent contract; extraction and states remain separate.

**Acceptance.** All required states are documented and compatible with intent in the declared context. A contradiction in a complete, attributable state is fail even if other states are missing. Removing initial noindex with JavaScript does not yield pass: A03 remains inconclusive unless a required state supplies another contradiction; A01 retains its own source verdict. For this new profile, all possible values within the intended interval yield pass; all outside on one side yield fail; otherwise inconclusive. Independent contradiction prevails within a reading; existing source consensus and rendered priority remain.

**Evidence.** Retained headers/source HTML, prior plan, dated raw DOMs with binding digest of the HTTP trace, final URL, context, browser/version, script state, interactions, waiting conditions and errors. Reasoned comparison and limitations; no simulated engine capture. The new profile additionally retains ordered HTTP/meta values, scopes, unknowns, dimension decisions and intervals in bound replayed observations.

**Assumptions.** Required states are listed before the test; local and engine rendering remain distinct. The structured reader interprets HTML meta children directly in the real document head; ambiguous placement or shadow remains inconclusive. It retains combination with the declared navigation headers. Intent retains crawler as the exact HTTP User-Agent. Optional directive_crawler, frozen before collection and limited here to googlebot, selects directive semantics only for this client representation; it does not describe a response received by Googlebot. Without this field, historical behavior requires crawler=googlebot. Bounds concern a permission cap, not actual display. Selection and bounds are prior; absent reader preserves historical behavior and no scalar is automatically migrated.

**Inconclusive.** Missing required plan/capture, truncated state, script error, inconsistent source/target/context binding, invalid chronology, uninterpretable directive or late removal of initial noindex: inconclusive without an inferred pass. An established contradiction in another attributable state remains fail. For the structured reader: incomplete tree/transport, loading document, known API alteration, missing integrity history, separate source/DOM acquisition without same-navigation attribution or a different agent: inconclusive. A digest alone does not prove navigation. Present but unsupported, null or inconsistent directive_crawler: inconclusive; no favorable fallback. The preview profile retains unqualified image defaults, max-snippet:0 video interaction, unsupported syntax and exceeded bounds as unknown under the contract’s conservative intervals. Noindex does not give a presentation pass.

**When NA is allowed.** Non-HTML or directive stability demonstrated by documented review; intent evidence references this justification and supporting records. No unsupported “no JS” assertion.

**Limits.** semiAuto: the plan and sufficiency of observations require review. The interpreter compares supplied captures; it does not execute JavaScript or establish exhaustive states, TS25, engine rendering or indexing. Supplied attribution and APIs are not authenticated; authored synthetic records are explicitly labeled, never actual visits. Frames, template fragments and closed shadow roots are outside scope. Bounds and migration are documented in docs/structured-rendering.md. The preview profile assesses neither Google display, image availability, data-nosnippet nor licensed, structured-data or AI usage; it produces no review.

## TS08 — The actual indexing status is checked in Search Console.

**Severity**: major. **Unit**: url-set.

**Required inputs**: search-console, intent.

**Applicability.** URLs whose Google indexing state must be established.

**Method.** Declare selection, objectives, sources and prior knowledge before acquisition; retain native API JSON, limitations and supplied reviews under google-inspection-evidence-v1.

**Acceptance.** All three rules pass for the entire selected set. C qualifies documentation of Google-reported status, never an indexing promise or current site state.

**Evidence.** Known URL, crawling permission, indexing state and Google-selected canonical documented.

**When NA is allowed.** Google is explicitly out of scope; lack of access alone is insufficient.

**Limits.** Non-live API, supplied unauthenticated attribution/dates; missing/reserved fields, insufficient freshness and absent reviews remain inconclusive under the bounded profile. No site extrapolation.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://support.google.com/webmasters/answer/9012289](https://support.google.com/webmasters/answer/9012289); [https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect](https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect); [https://developers.google.com/webmaster-tools/v1/urlInspection.index/UrlInspectionResult](https://developers.google.com/webmaster-tools/v1/urlInspection.index/UrlInspectionResult)

### TS08-A01 — Qualified prior scope and objectives.

`TSEP@0.1.0-draft.41:TS08-A01`

**Required inputs**: intent, search-console.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Explicit selected URL set whose Google-reported state must be documented.

**Method.** Declare members, objectives/sources, selection reasons, prior knowledge and freshness policy; retain the bound prior plan review.

**Acceptance.** Supported selection/objective review, plan and review before acquisition, no omitted member. Supplied contradiction or acquisition preceding the plan fails; absence alone is inconclusive.

**Evidence.** Dated sourced plan, native request/response JSON and hashes, actual metadata, supplied evidence-bound reviews; inspection-evidence-v1 contract.

**Assumptions.** Dates, authorship, provenance, access and attribution are supplied, never authenticated by hashes alone.

**Inconclusive.** Missing, invalid or ambiguous evidence, review or binding; retain limitations, unknowns and API errors.

**When NA is allowed.** No atomic exemption; lack of access is not NA.

**Limits.** Selected-set documentation only; non-live API and crawl time distinct from field timestamps. No current state, causality, TS12 or SEO outcome inferred.

### TS08-A02 — Attributed and readable native inspections.

`TSEP@0.1.0-draft.41:TS08-A02`

**Required inputs**: search-console, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Explicit selected URL set whose Google-reported state must be documented.

**Method.** Read native bytes using diagnostic1, compare URL/property attribution, retain fields and check dates against prior policy.

**Acceptance.** Every member has a usable response with known required fields and dates within policy. Explicitly allowed absent API fields stay visible; API errors and unknown values never become C.

**Evidence.** Dated sourced plan, native request/response JSON and hashes, actual metadata, supplied evidence-bound reviews; inspection-evidence-v1 contract.

**Assumptions.** Dates, authorship, provenance, access and attribution are supplied, never authenticated by hashes alone.

**Inconclusive.** Missing, invalid or ambiguous evidence, review or binding; retain limitations, unknowns and API errors.

**When NA is allowed.** No atomic exemption; lack of access is not NA.

**Limits.** Selected-set documentation only; non-live API and crawl time distinct from field timestamps. No current state, causality, TS12 or SEO outcome inferred.

### TS08-A03 — Evidence-bound interpretation and decision.

`TSEP@0.1.0-draft.41:TS08-A03`

**Required inputs**: search-console, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Explicit selected URL set whose Google-reported state must be documented.

**Method.** Read supplied review: exact API verdict claim, interpretation, relation to prior objective, temporal scope, typed explanation and operational decision.

**Acceptance.** All facets are qualified; a documented discrepancy may pass. Explicit verdict/scope contradiction or contradiction judgment fails and survives independent unknowns. Missing review or unsupported cause remains inconclusive.

**Evidence.** Dated sourced plan, native request/response JSON and hashes, actual metadata, supplied evidence-bound reviews; inspection-evidence-v1 contract.

**Assumptions.** Dates, authorship, provenance, access and attribution are supplied, never authenticated by hashes alone.

**Inconclusive.** Missing, invalid or ambiguous evidence, review or binding; retain limitations, unknowns and API errors.

**When NA is allowed.** No atomic exemption; lack of access is not NA.

**Limits.** Selected-set documentation only; non-live API and crawl time distinct from field timestamps. No current state, causality, TS12 or SEO outcome inferred.

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

`TSEP@0.1.0-draft.41:TS10-A01`

**Required inputs**: http, html, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Each family member and its declared canonicalization strategy.

**Method.** List members, preferred URL and expected method; compare final URLs, HTTP Link, HTML rel=canonical and required rendered states. Retain multiple declarations, even identical ones. The DOM reader is chosen before capture: structured-inventory-v2, or the fixed legacy serialization reader when the field is absent. No fallback after refusal. The complete structured inventory retains namespaces, positions, duplicates, serialization and navigation attribution records; no node is removed based on its presumed origin. Optional prior intent.canonical.source_reader=html-tree-canonical-v1 compares two complete static source hypotheses with byte-attributed source/tree positions. The source-canonical.md contract defines its boundaries. Optional prior intent.canonical.http_reader=http-link-context-v1 applies docs/http-canonical-context.md to final GET 200 Link fields; absent selection retains the historical reader.

**Acceptance.** Present signals and those required by strategy identify the same absolute HTTP(S) URL without a fragment. HTML in head or HTTP Link are accepted; no universal HTML tag requirement. A relative canonical is fail for this TSEP rule without claiming Google cannot interpret it. Retain repeated identical declarations, which may agree; an attributable conflict remains fail despite another missing capture. Two source pass yield pass, two fail yield fail, otherwise inconclusive. Ordinary body canonical remains a contradiction even for the preferred URL; relative values are never resolved through base. Attributable HTTP Link, redirect and DOM contradictions remain independent of source unknowns. The new reader separates context from literal destination, retaining first rel and repeated declarations; unknowns prevent pass and independent attributable HTTP conflicts remain fail.

**Evidence.** Family inventory in intent; headers and source (or html non-applicability record for non-HTML); extraction with location and method, required DOM attached when needed. Bind each capture to the family, context and date. Declare required methods and DOM states before assessment; bind DOMs to the HTTP trace by fingerprint. A rendering exemption needs a source-bound review and supporting records, not a bare “no JS” claim. Also retain profile observations: document, body, canonical/base, templates, prefix tokens, context, errors, decoding, sources/runtime and separate decisions; replay compares these records. Retain ordered HTTP diagnostics, raw fields/parameters, excluded/unknown contexts, requested/final URLs, timestamp and source-trace fingerprint.

**Assumptions.** Strategy distinguishes preferred canonical and duplicates; comparisons do not silently remove parameters or normalize case or slashes. In structured DOM, a difference between absolute raw href and the resolved property prevents a conclusion on that surface, without substituting either value or asserting an SEO defect. A relative or out-of-head canonical in ordinary DOM remains a TSEP contradiction; open shadow remains inconclusive. Absent field preserves legacy reading. Null/unknown or absent Node 24 never falls back. This profile neither validates HTML nor replaces rendering or supplied human judgment.

**Inconclusive.** Incomplete family/intent, ambiguous Link, truncated document or missing required rendered state: inconclusive. For the structured reader: incomplete tree/transport, loading document, known API alteration, missing integrity history, separate source/DOM acquisition without same-navigation attribution or a different agent: inconclusive. A digest alone does not prove navigation. After-head reinsertion, indirect head descendant, foreign context, unknown/modifying attributes, declared shadow, incomplete bounded reading/diagnostics prevent success as defined by the contract; retain any separately qualified contradiction. Unknown HTTP selection, unqualified context/uncertain equivalence, extensions or unsupported syntax are inconclusive without favorable fallback; the HTTP contract fixes bounds and their scope.

**When NA is allowed.** No atomic exemption when the control applies.

**Limits.** Relative URLs, placement and convergence are TSEP criteria; engine canonical selection is not observed here. Supplied attribution and APIs are not authenticated; authored synthetic records are explicitly labeled, never actual visits. Frames, template fragments and closed shadow roots are outside scope. Bounds and migration are documented in docs/structured-rendering.md. Source scope only; A04 and DOM readers are not extended. The hypotheses are not coexisting observed rendered states. No Google canonical choice is inferred. No engine execution or destination normalization; an RFC-valid relative can fail TSEP’s absolute criterion. See draft.19 migration; historical reader preserved.

### TS10-A02 — Direct canonical destination

`TSEP@0.1.0-draft.41:TS10-A02`

**Required inputs**: http, html, intent.

**Automation / Automatisation**: `manual`.

**Applicability.** Every preferred destination in declared families.

**Method.** Test the destination, retain GET and content; verify that any canonical there does not point elsewhere. Compare content with the declared family. The DOM reader is chosen before capture: structured-inventory-v2, or the fixed legacy serialization reader when the field is absent. No fallback after refusal. The complete structured inventory retains namespaces, positions, duplicates, serialization and navigation attribution records; no node is removed based on its presumed origin. Optional prior intent.canonical.source_reader=html-tree-canonical-v1 compares two complete static source hypotheses with byte-attributed source/tree positions. The source-canonical.md contract defines its boundaries. Optional prior intent.canonical.http_reader=http-link-context-v1 applies docs/http-canonical-context.md to final GET 200 Link fields; absent selection retains the historical reader.

**Acceptance.** The expected destination is directly accessible with 200, without canonical chains or cycles, and compatible content. A duplicate may remain 200 and point to the preferred URL; not every duplicate final URL must equal it. Two source pass yield pass, two fail yield fail, otherwise inconclusive. Ordinary body canonical remains a contradiction even for the preferred URL; relative values are never resolved through base. Attributable HTTP Link, redirect and DOM contradictions remain independent of source unknowns. The new reader separates context from literal destination, retaining first rel and repeated declarations; unknowns prevent pass and independent attributable HTTP conflicts remain fail.

**Evidence.** Destination trace and body tied to the family; declaration graph and reasoned content comparison. The human compatibility review identifies its author, date, each member compared with the preferred representation, reasoned judgment and exact examined captures by fingerprint. A missing/stale reference or unestablished comparison prevents pass. Also retain profile observations: document, body, canonical/base, templates, prefix tokens, context, errors, decoding, sources/runtime and separate decisions; replay compares these records. Retain ordered HTTP diagnostics, raw fields/parameters, excluded/unknown contexts, requested/final URLs, timestamp and source-trace fingerprint.

**Assumptions.** Content similarity is assessed in business context without a universal similarity threshold. In structured DOM, a difference between absolute raw href and the resolved property prevents a conclusion on that surface, without substituting either value or asserting an SEO defect. A relative or out-of-head canonical in ordinary DOM remains a TSEP contradiction; open shadow remains inconclusive. Absent field preserves legacy reading. Null/unknown or absent Node 24 never falls back. This profile neither validates HTML nor replaces rendering or supplied human judgment.

**Inconclusive.** Uncollected destination, timeout or incomparable content: inconclusive. An observed 404/5xx, cycle or hop is a contradiction. For the structured reader: incomplete tree/transport, loading document, known API alteration, missing integrity history, separate source/DOM acquisition without same-navigation attribution or a different agent: inconclusive. A digest alone does not prove navigation. After-head reinsertion, indirect head descendant, foreign context, unknown/modifying attributes, declared shadow, incomplete bounded reading/diagnostics prevent success as defined by the contract; retain any separately qualified contradiction. Unknown HTTP selection, unqualified context/uncertain equivalence, extensions or unsupported syntax are inconclusive without favorable fallback; the HTTP contract fixes bounds and their scope.

**When NA is allowed.** No atomic exemption when the control applies.

**Limits.** A successful GET does not prove Google will select this URL; no temporal stability is inferred from one instant. A comparator can check the supplied review’s bindings and coverage; it does not turn that judgment into automatic content comparison. Supplied attribution and APIs are not authenticated; authored synthetic records are explicitly labeled, never actual visits. Frames, template fragments and closed shadow roots are outside scope. Bounds and migration are documented in docs/structured-rendering.md. Source scope only; A04 and DOM readers are not extended. The hypotheses are not coexisting observed rendered states. No Google canonical choice is inferred. No engine execution or destination normalization; an RFC-valid relative can fail TSEP’s absolute criterion. See draft.19 migration; historical reader preserved.

### TS10-A03 — Sitemap agreement

`TSEP@0.1.0-draft.41:TS10-A03`

**Required inputs**: sitemap, intent.

**Automation / Automatisation**: `semiAuto`.

**Atomic exemption inputs**: intent, sitemap.

**Applicability.** Families associated with a sitemap under the declared strategy.

**Method.** Compare entries from all sitemaps/indexes required for the family and preferred URL; retain exclusions justified by strategy. Reconcile captures of each index and all expected children. An observed failure remains fail when another branch is missing; an omission becomes fail only after the declared population has been fully examined. Optional sitemap-locations-v1 must be declared before capture; absence uses the fixed legacy reader, unknown values never fall back. Only direct Sitemaps 0.9 loc under url counts as a page URL; under sitemap it identifies children. Decode XML and trim surrounding XML whitespace only, then compare literally without URL normalization. Record recognized XHTML alternate, image and ordinary fields separately, without comparing them as page URLs.

**Acceptance.** Observed and required entries agree with declared preference; a duplicate published as a competing canonical without justification is fail.

**Evidence.** Raw sitemaps and index coverage, family/entry mapping and justification of omissions. Retain XML bytes and complete annotation values; bounded reason preview with explicit truncation.

**Assumptions.** Sitemap scope is declared; absence is not inferred from a 404 at one guessed path. The new reader requires explicitly covered namespaces and structures; prefixes are arbitrary and annotation values are not validated. Preference remains supplied intent, not observed engine choice.

**Inconclusive.** Incomplete index, unavailable expected sitemap or unknown strategy: inconclusive. Unknown reader, missing/wrong namespace, unsupported extension/attribute, duplicate leaf, ambiguous structure, mixed text, DTD/entities, malformed XML or exceeded bound: entire document inconclusive.

**When NA is allowed.** No sitemap used for this family, established by documented strategy and inventory. Retain a sitemap record explaining absence; no whole-TS10 NA.

**Limits.** Sitemap = published preference, not engine selection or an exhaustive site inventory. No hreflang, image or value-validity verdict. The bounded reader is not a full XML Schema validator. Profile, structural registry, limits and migration: docs/sitemap-locations.md and docs/migration-draft.14.md.

### TS10-A04 — Internal-link agreement

`TSEP@0.1.0-draft.41:TS10-A04`

**Required inputs**: crawl, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Each family and declared source-page population.

**Method.** Extract links from the announced population; compare destinations and documented exceptions with canonical preference. The DOM reader is chosen before capture: structured-inventory-v2, or the fixed legacy serialization reader when the field is absent. No fallback after refusal. The complete structured inventory retains namespaces, positions, duplicates, serialization and navigation attribution records; no node is removed based on its presumed origin. Optional prior intent.canonical.links.source_reader=html-tree-links-v1 qualifies attributed HTML a/area hrefs, base and WHATWG resolution under two static hypotheses. source-link-policy.md defines this method; earlier rendered readers remain unchanged. Draft.18 adds html-tree-links-v2: a first base whose href fails WHATWG parsing adds base uncertainty; v1 remains unchanged. Computation against the final URL is then conditional, without inferring a destination for dependent hrefs. source-link-policy-v2.md defines this delta.

**Acceptance.** All assessed links follow strategy; no unexplained competing destination. Zero links can satisfy the rule only when the announced population is fully examined. An attributable competing link remains fail even if another source page or required state is missing. Two source passes yield pass, two failures yield fail, otherwise inconclusive. An uncertain base cannot establish failure for dependent hrefs; an independent qualified absolute conflict remains usable. Zero counts and limited convergence scope remain visible through control and gate without adding a link-presence requirement.

**Evidence.** Crawl export with source URL, href, destination, pages actually visited, failures and exclusions; reconciliation with the declared population. Retain source HTML and DOMs needed for extraction, bound to their traces, contexts and dates; a rendering exemption is reviewed and supported. Exceptions identify source, destination and reason. The new profile retains inventory, namespaces, templates, tags/bytes, calculated URLs, bases/limits, versions, per-hypothesis decisions/counts in replayable observations.

**Assumptions.** The crawl checks a declared population; it does not by itself prove that population exhaustive. Structured reader v2 retains raw hrefs; bounded resolution only without a base declaration and with baseURI equal to the final URL. Shadow links or unsupported syntax remain inconclusive. Family URLs must already equal their WHATWG serialization or source is inconclusive, without silent normalization. Outside-family URLs are retained, never guessed duplicates. No-namespace href with no nofollow/download filtering; static destination only. Empty/whitespace base href, data/javascript schemes and CSP remain distinct from that parse failure; never select a second base instead.

**Inconclusive.** Missing source pages, unexamined links or absent crawl: inconclusive, never success from zero results. For the structured reader: incomplete tree/transport, loading document, known API alteration, missing integrity history, separate source/DOM acquisition without same-navigation attribution or a different agent: inconclusive. A digest alone does not prove navigation. Null/unknown source selection, missing Node24, incomplete traversal/diagnostic: inconclusive without fallback. SVG/foreign ancestors, declared shadow and duplicate link attributes remain unknown; unmodeled CSP/base prevents conclusive dependent-href resolution.

**When NA is allowed.** No atomic exemption when the control applies.

**Limits.** No extrapolation to external links, pages outside the population or future dates. Supplied attribution and APIs are not authenticated; authored synthetic records are explicitly labeled, never actual visits. Frames, template fragments and closed shadow roots are outside scope. Bounds and migration are documented in docs/structured-rendering.md. Source profile measures neither activation, link presence/sufficiency, forms/events nor Google behavior. Bounds, retained out-of-scope elements and migration: source-link-policy.md and migration-draft.17.md. Version2 correction and preserved historical results: migration-draft.18.md. The diagnostic establishes neither a general browser bug nor a Google state.

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

**Required inputs**: search-console, http, html, render, intent.

**Applicability.** URLs whose Google canonical must be compared with the declared canonical.

**Method.** Declare sourced preference, readers and rendered states; attribute API JSON and captures, compare literal strings and retain supplied reviews/decisions under google-canonical-comparison-v1.

**Acceptance.** Qualified prior plan and all planned surfaces; retained values, separate dates and bound decisions. Documentary C, never canonical equality; documented differences allowed.

**Evidence.** Agreement or a qualified, addressed divergence.

**When NA is allowed.** Google explicitly out of scope; missing access is NT.

**Limits.** Missing required rendering or absent Google canonical: inconclusive. Literal comparison without inferred URL equivalence, live state, causality, TS10 or indexing.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://support.google.com/webmasters/answer/9012289](https://support.google.com/webmasters/answer/9012289)

### TS12-A01 — Qualified prior comparison plan.

`TSEP@0.1.0-draft.41:TS12-A01`

**Required inputs**: intent, search-console, http.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Selected set whose reported and captured canonicals must be compared.

**Method.** Declare selection/objectives, prior knowledge, sourced preference, readers and rendered states; qualify the bound plan before every acquisition.

**Acceptance.** Supported selection/objectives/preferences/surfaces/temporal_policy judgments, prior chronology and complete set. Supplied contradiction or acquisition before plan fails; gaps are inconclusive.

**Evidence.** Prior plan/review, native API JSON, HTTP traces, supplied structured DOM states and reviews bound to exact evidence; canonical-comparison-v1 contract.

**Assumptions.** Supplied data, dates, provenance and judgments; hashes do not authenticate people, navigation or history.

**Inconclusive.** Missing/unknown/invalid evidence, required state, value, policy, review or binding; retain limits and errors.

**When NA is allowed.** No atomic exemption; lack of access or rendering is not NA.

**Limits.** Missing required rendering or absent Google canonical: inconclusive. Literal comparison without inferred URL equivalence, live state, causality, TS10 or indexing.

### TS12-A02 — Complete attributed readings and comparisons.

`TSEP@0.1.0-draft.41:TS12-A02`

**Required inputs**: search-console, http, html, render, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Selected set whose reported and captured canonicals must be compared.

**Method.** Read native evidence and both static HTML hypotheses; retain separate HTTP/HTML/DOM candidates, dates and literal comparisons.

**Acceptance.** Qualified API, present Google canonical, readable HTTP/HTML and every planned DOM state; prior thresholds satisfied, duplicates retained. Different values allowed; source-only/absent Google remains inconclusive.

**Evidence.** Prior plan/review, native API JSON, HTTP traces, supplied structured DOM states and reviews bound to exact evidence; canonical-comparison-v1 contract.

**Assumptions.** Supplied data, dates, provenance and judgments; hashes do not authenticate people, navigation or history.

**Inconclusive.** Missing/unknown/invalid evidence, required state, value, policy, review or binding; retain limits and errors.

**When NA is allowed.** No atomic exemption; lack of access or rendering is not NA.

**Limits.** Missing required rendering or absent Google canonical: inconclusive. Literal comparison without inferred URL equivalence, live state, causality, TS10 or indexing.

### TS12-A03 — Qualification and decision bound to comparisons.

`TSEP@0.1.0-draft.41:TS12-A03`

**Required inputs**: search-console, http, html, render, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Selected set whose reported and captured canonicals must be compared.

**Method.** Examine every surface value claim in a supplied evidence-bound review with interpretation, chronology, changes, objective, explanation and decision.

**Acceptance.** Claims match known lists, supported qualification, reasoned relation and decision. A contradicted claim retains fail despite another unknown; missing review or unsupported established-cause assertion is inconclusive.

**Evidence.** Prior plan/review, native API JSON, HTTP traces, supplied structured DOM states and reviews bound to exact evidence; canonical-comparison-v1 contract.

**Assumptions.** Supplied data, dates, provenance and judgments; hashes do not authenticate people, navigation or history.

**Inconclusive.** Missing/unknown/invalid evidence, required state, value, policy, review or binding; retain limits and errors.

**When NA is allowed.** No atomic exemption; lack of access or rendering is not NA.

**Limits.** Missing required rendering or absent Google canonical: inconclusive. Literal comparison without inferred URL equivalence, live state, causality, TS10 or indexing.

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

**Required inputs**: sitemap, intent.

**Applicability.** Declared population of supplied native sitemap files; roots are not automatically discovered.

**Method.** Read original bytes, base XML structure, decompressed size, direct entries and index children in the declared set.

**Acceptance.** Within the bounded profile: qualified UTF-8 and minimal structure, at most52,428,800 bytes and50,000 direct entries per file, coverage of the declared set.

**Evidence.** Base64/SHA-256 originals, declared URLs/dates and set plan; native-sitemap-files-v1 bounds.

**When NA is allowed.** No sitemap used in scope.

**Limits.** Supplied files only, no observed server or site completeness. No full XSD, lastmod/changefreq/priority values, URL host/path/length, canonical or indexing validation.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://www.sitemaps.org/protocol.html](https://www.sitemaps.org/protocol.html)

### TS15-A01 — Encoding and minimal structure of supplied files.

`TSEP@0.1.0-draft.41:TS15-A01`

**Required inputs**: sitemap, intent.

**Automation / Automatisation**: `automatic`.

**Applicability.** Declared population of supplied native sitemap files; roots are not automatically discovered.

**Method.** Check strict UTF-8,0.9 root, unique nonempty loc and unique ordered leaves; DTD/unqualified extensions stay unknown.

**Acceptance.** Every complete file passes the bounded structure; established structural contradiction fails.

**Evidence.** Base64/SHA-256 originals, declared URLs/dates and set plan; native-sitemap-files-v1 bounds.

**Assumptions.** Supplied URL, date, origin and completeness, unauthenticated. No server observation.

**Inconclusive.** Missing/ambiguous file, incomplete stream, unknown profile, reader bound, nested index or unqualified extension; independent violation retained.

**When NA is allowed.** No NA in this profile.

**Limits.** Supplied files only, no observed server or site completeness. No full XSD, lastmod/changefreq/priority values, URL host/path/length, canonical or indexing validation.

### TS15-A02 — Actual size and population limits.

`TSEP@0.1.0-draft.41:TS15-A02`

**Required inputs**: sitemap, intent.

**Automation / Automatisation**: `automatic`.

**Applicability.** Declared population of supplied native sitemap files; roots are not automatically discovered.

**Method.** Count actually decompressed bytes and direct url/sitemap elements, including duplicates and entries without loc.

**Acceptance.** Each file is at most52,428,800 bytes and50,000 entries; observed excess fails, partial reading without excess is inconclusive.

**Evidence.** Base64/SHA-256 originals, declared URLs/dates and set plan; native-sitemap-files-v1 bounds.

**Assumptions.** Supplied URL, date, origin and completeness, unauthenticated. No server observation.

**Inconclusive.** Missing/ambiguous file, incomplete stream, unknown profile, reader bound, nested index or unqualified extension; independent violation retained.

**When NA is allowed.** No NA in this profile.

**Limits.** Supplied files only, no observed server or site completeness. No full XSD, lastmod/changefreq/priority values, URL host/path/length, canonical or indexing validation.

### TS15-A03 — Coverage of declared population and bound children.

`TSEP@0.1.0-draft.41:TS15-A03`

**Required inputs**: sitemap, intent.

**Automation / Automatisation**: `automatic`.

**Allowed outcomes**: pass, inconclusive.

**Applicability.** Declared population of supplied native sitemap files; roots are not automatically discovered.

**Method.** Bind each document to an exact declared URL and each index child to a complete leaf; roots and scope remain declared.

**Acceptance.** All declared documents and branches are qualified; absence/ambiguity/outside-profile is inconclusive, never negative evidence about site sitemap use.

**Evidence.** Base64/SHA-256 originals, declared URLs/dates and set plan; native-sitemap-files-v1 bounds.

**Assumptions.** Supplied URL, date, origin and completeness, unauthenticated. No server observation.

**Inconclusive.** Missing/ambiguous file, incomplete stream, unknown profile, reader bound, nested index or unqualified extension; independent violation retained.

**When NA is allowed.** No NA in this profile.

**Limits.** Supplied files only, no observed server or site completeness. No full XSD, lastmod/changefreq/priority values, URL host/path/length, canonical or indexing validation.

## TS16 — Every important page receives at least one crawlable internal link.

**Severity**: major. **Unit**: url-set.

**Required inputs**: http, html, inventory, intent.

**Applicability.** Important destinations and internal sources selected before captures, with dated original inventory and bound prior plan; incoming-document-links-v1.

**Method.** For each destination, seek an a/href witness from a distinct qualified internal document: source HTML under two static hypotheses or provider-declared no-interaction DOM. Qualify each source, destination and surface separately.

**Acceptance.** Each declared destination has a qualified incoming witness and its original HTTP evidence. Absence is established only across every qualified eligible surface of the prior inventory and remains bounded to that population.

**Evidence.** Original inventory, prior plan, HTTP/DOM originals, requested/final URLs, dates, destination status, raw href, anchor reference and per-destination diagnostics. DOM is required for surfaces that depend on it; an independent source witness suffices without DOM, without inventing one.

**When NA is allowed.** No relevant important page only with justification and inventory; no automatic NA in the bounded reader.

**Limits.** Population and importance are supplied, not authenticated. No site completeness, observed acquisition or interaction, editorial value, Google visit, indexing or ranking. Bounded absence does not establish a site-wide orphan. Expected source content and soft404s are not assessed.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/crawling-indexing/links-crawlable](https://developers.google.com/search/docs/crawling-indexing/links-crawlable)

### TS16-A01 — Incoming witness in the prior internal population.

`TSEP@0.1.0-draft.41:TS16-A01`

**Required inputs**: http, html, inventory, intent.

**Automation / Automatisation**: `automatic`.

**Applicability.** Important destinations and internal sources selected before captures, with dated original inventory and bound prior plan; incoming-document-links-v1.

**Method.** For each destination, seek an a/href witness from a distinct qualified internal document: source HTML under two static hypotheses or provider-declared no-interaction DOM. Qualify each source, destination and surface separately.

**Acceptance.** Pass when every destination has an independently qualified witness and a destination original. Fail when a destination has no witness across the complete qualified eligible population. Otherwise inconclusive; an independent fail survives other unknowns.

**Evidence.** Original inventory, prior plan, HTTP/DOM originals, requested/final URLs, dates, destination status, raw href, anchor reference and per-destination diagnostics. DOM is required for surfaces that depend on it; an independent source witness suffices without DOM, without inventing one.

**Assumptions.** Inventory observed before the plan binding its digest, captures within the prior window; exact origins and no-interaction states supplied. Integrity does not authenticate evidence or simultaneity.

**Inconclusive.** Insufficient plan/inventory/original, ambiguous population, unqualified surface, incoherent dates or absent runtime. A pair whose destination redirects back to its source remains inconclusive; another witness may suffice.

**When NA is allowed.** No automatic NA in this profile.

**Limits.** Population and importance are supplied, not authenticated. No site completeness, observed acquisition or interaction, editorial value, Google visit, indexing or ranking. Bounded absence does not establish a site-wide orphan. Expected source content and soft404s are not assessed.

## TS17 — Essential links use an a element with a resolvable href.

**Severity**: major. **Unit**: page.

**Required inputs**: http, html, render, intent.

**Applicability.** Declared essential destinations under the prior source-and-rendered strategy, on supplied captures.

**Method.** Compare HTML a/href links in source and every declared DOM state; separate stages and exact document URLs.

**Acceptance.** Each declared destination has a resolvable a/href in both required stages within essential-document-links-v1.

**Evidence.** Original HTTP bytes, bound DOM v2 tree, prior plan and separate source/render diagnostics; provider-declared states.

**When NA is allowed.** No relevant navigation, with a justified scope.

**Limits.** C only within the declared strategy. No established visibility, interaction, editorial importance, authenticity, Google visit, indexing or ranking. Source presence is not a universal Google requirement.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/crawling-indexing/links-crawlable](https://developers.google.com/search/docs/crawling-indexing/links-crawlable)

### TS17-A01 — Essential links present in supplied source.

`TSEP@0.1.0-draft.41:TS17-A01`

**Required inputs**: http, html, intent.

**Automation / Automatisation**: `automatic`.

**Applicability.** Declared essential destinations under the prior source-and-rendered strategy, on supplied captures.

**Method.** Read native source under both static scripting hypotheses; require their agreement.

**Acceptance.** Every destination in the qualified stage: pass; established absence in complete inventory: fail; otherwise inconclusive.

**Evidence.** Original HTTP bytes, bound DOM v2 tree, prior plan and separate source/render diagnostics; provider-declared states.

**Assumptions.** Prior plan, population, scenarios and completeness supplied; checked HTTP/DOM association but unauthenticated acquisition.

**Inconclusive.** Missing/incomplete/out-of-profile plan or stage, active base, ambiguous reading or missing runtime. Independent contradictions remain.

**When NA is allowed.** No automatic NA in this profile.

**Limits.** C only within the declared strategy. No established visibility, interaction, editorial importance, authenticity, Google visit, indexing or ranking. Source presence is not a universal Google requirement.

### TS17-A02 — Essential links present in declared rendered states.

`TSEP@0.1.0-draft.41:TS17-A02`

**Required inputs**: http, render, intent.

**Automation / Automatisation**: `automatic`.

**Applicability.** Declared essential destinations under the prior source-and-rendered strategy, on supplied captures.

**Method.** Check each complete HTTP-bound tree and disclose repeated snapshots; scenarios are unauthenticated.

**Acceptance.** Every destination in the qualified stage: pass; established absence in complete inventory: fail; otherwise inconclusive.

**Evidence.** Original HTTP bytes, bound DOM v2 tree, prior plan and separate source/render diagnostics; provider-declared states.

**Assumptions.** Prior plan, population, scenarios and completeness supplied; checked HTTP/DOM association but unauthenticated acquisition.

**Inconclusive.** Missing/incomplete/out-of-profile plan or stage, active base, ambiguous reading or missing runtime. Independent contradictions remain.

**When NA is allowed.** No automatic NA in this profile.

**Limits.** C only within the declared strategy. No established visibility, interaction, editorial importance, authenticity, Google visit, indexing or ranking. Source presence is not a universal Google requirement.

## TS18 — Depth and orphan pages are measured within an explicit scope.

**Severity**: major. **Unit**: url-set.

**Required inputs**: crawl, sitemap, inventory, intent, http, html.

**Applicability.** Population, roots, families and boundaries declared before captures; bounded supplied-graph-reconciliation-v1 profile.

**Method.** Reconcile original reference, crawl, CMS and sitemap inventories; compute native bounded graph links/distances; verify supplied reviews bound to family and difference measurements.

**Acceptance.** Three complete layers within supplied scope: qualified reconciliation, qualified native measurements and bound documentary reviews. An evidenced reviewed defect remains NC despite another unknown.

**Evidence.** Dated fingerprinted original inventories, declared production/dependencies, prior plan, original HTTP/source/DOM, pairs and bounds, per-inventory dates and supplied reviews bound to exact dossiers.

**When NA is allowed.** No relevant navigation graph, with a justification; a missing inventory means NT.

**Limits.** Declared graph only: no completeness, site-wide orphan, universal SEO depth, authenticated acquisition/reviews, observed interaction, indexing or ranking. HTTP200 does not verify expected content or soft404s. The reader does not adjudicate supplied rationale.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/crawling-indexing/links-crawlable](https://developers.google.com/search/docs/crawling-indexing/links-crawlable)

### TS18-A01 — Prior scope and reconciled original inventories.

`TSEP@0.1.0-draft.41:TS18-A01`

**Required inputs**: crawl, sitemap, inventory, intent.

**Automation / Automatisation**: `automatic`.

**Allowed outcomes**: pass, inconclusive.

**Applicability.** Population, roots, families and boundaries declared before captures; bounded supplied-graph-reconciliation-v1 profile.

**Method.** Read explicitly declared formats and lineage; ordered reference bound to plan, crawl following links from roots only, native CMS and sitemap with explicit optional dependency.

**Acceptance.** Pass if all originals, dates, families and declarations are qualified; otherwise inconclusive. Matching lists do not establish completeness. Mixed or list seeding is inconclusive in this profile.

**Evidence.** Dated fingerprinted original inventories, declared production/dependencies, prior plan, original HTTP/source/DOM, pairs and bounds, per-inventory dates and supplied reviews bound to exact dossiers.

**Assumptions.** Exact origins/documents, prior plan, captures within at most24hours; unauthenticated production and no-interaction declarations.

**Inconclusive.** Missing, ambiguous, out-of-profile, misbound or out-of-window plan/original/surface/review; required runtime absent. Unknowns remain explicit and independent defects survive.

**When NA is allowed.** No automatic NA; missing proof is inconclusive.

**Limits.** Declared graph only: no completeness, site-wide orphan, universal SEO depth, authenticated acquisition/reviews, observed interaction, indexing or ranking. HTTP200 does not verify expected content or soft404s. The reader does not adjudicate supplied rationale.

### TS18-A02 — Depths and incoming degrees within the bounded graph.

`TSEP@0.1.0-draft.41:TS18-A02`

**Required inputs**: http, html, intent.

**Automation / Automatisation**: `automatic`.

**Allowed outcomes**: pass, inconclusive.

**Applicability.** Population, roots, families and boundaries declared before captures; bounded supplied-graph-reconciliation-v1 profile.

**Method.** Read each pair from source under two hypotheses or qualified no-interaction DOM; compute lower/upper distances and counts of distinct incoming sources, excluding self-links.

**Acceptance.** Pass if roots and every pair are qualified; otherwise inconclusive even if one depth is exact. A no-incoming candidate requires an upper degree of0. No universal depth threshold.

**Evidence.** Dated fingerprinted original inventories, declared production/dependencies, prior plan, original HTTP/source/DOM, pairs and bounds, per-inventory dates and supplied reviews bound to exact dossiers.

**Assumptions.** Exact origins/documents, prior plan, captures within at most24hours; unauthenticated production and no-interaction declarations.

**Inconclusive.** Missing, ambiguous, out-of-profile, misbound or out-of-window plan/original/surface/review; required runtime absent. Unknowns remain explicit and independent defects survive.

**When NA is allowed.** No automatic NA; missing proof is inconclusive.

**Limits.** Declared graph only: no completeness, site-wide orphan, universal SEO depth, authenticated acquisition/reviews, observed interaction, indexing or ranking. HTTP200 does not verify expected content or soft404s. The reader does not adjudicate supplied rationale.

### TS18-A03 — Supplied documentary qualification of families and differences.

`TSEP@0.1.0-draft.41:TS18-A03`

**Required inputs**: intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Population, roots, families and boundaries declared before captures; bounded supplied-graph-reconciliation-v1 profile.

**Method.** Derive subjects only from native measurements; check one review for each family, known difference, no-incoming candidate and unreachable document, bound to plan, originals, dates and measurements.

**Acceptance.** Pass if every qualified subject has a correctly bound supplied explanation; fail if a supplied defect binds an evidenced subject; otherwise inconclusive. Reviews cannot cure unknown measurements and are never software-created human approval.

**Evidence.** Dated fingerprinted original inventories, declared production/dependencies, prior plan, original HTTP/source/DOM, pairs and bounds, per-inventory dates and supplied reviews bound to exact dossiers.

**Assumptions.** Exact origins/documents, prior plan, captures within at most24hours; unauthenticated production and no-interaction declarations.

**Inconclusive.** Missing, ambiguous, out-of-profile, misbound or out-of-window plan/original/surface/review; required runtime absent. Unknowns remain explicit and independent defects survive.

**When NA is allowed.** No automatic NA; missing proof is inconclusive.

**Limits.** Declared graph only: no completeness, site-wide orphan, universal SEO depth, authenticated acquisition/reviews, observed interaction, indexing or ranking. HTTP200 does not verify expected content or soft404s. The reader does not adjudicate supplied rationale.

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

**Required inputs**: http, hreflang, intent.

**Applicability.** Cluster and primary channels declared before capture; bounded hreflang-reciprocity-v1 profile.

**Method.** Read native HTML or HTTP Link annotations from originals, preserve two HTML hypotheses and secondary channels, compare every code–URL pair to the prior cluster without unioning channels.

**Acceptance.** Each cluster page includes the entire expected set in its primary channel, including self-reference; no qualified target contradiction. Several codes may share a URL and cross-domain clusters are allowed.

**Evidence.** Prior plan/expected mappings, selected channels, original HTTP requests/responses and hashes, dates, element/head-closure positions, static hypotheses, primary/secondary sets, exclusions and unknowns.

**When NA is allowed.** No hreflang cluster in scope.

**Limits.** Supplied cluster and primary mode declarations: no capture authenticity, site completeness, TS22 language validity, indexability/canonical, TS24 x-default suitability, translation, executed JavaScript or Google processing. Relevant supplied sitemap/DOM channels remain outside this profile.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/specialty/international/localized-versions](https://developers.google.com/search/docs/specialty/international/localized-versions)

### TS23-A01 — Native reciprocal and self references within the prior cluster.

`TSEP@0.1.0-draft.41:TS23-A01`

**Required inputs**: http, hreflang, intent.

**Automation / Automatisation**: `automatic`.

**Applicability.** Cluster and primary channels declared before capture; bounded hreflang-reciprocity-v1 profile.

**Method.** Read native HTML or HTTP Link annotations from originals, preserve two HTML hypotheses and secondary channels, compare every code–URL pair to the prior cluster without unioning channels.

**Acceptance.** Pass if all pages are qualified and include the expected set in their primary channel. Fail for established qualified absence, invalid primary-HTML placement or target conflict. Otherwise inconclusive; independent contradictions survive unknowns.

**Evidence.** Prior plan/expected mappings, selected channels, original HTTP requests/responses and hashes, dates, element/head-closure positions, static hypotheses, primary/secondary sets, exclusions and unknowns.

**Assumptions.** Prior plan, at most24-hour window, HTTP200 requested=final without redirects, exact absolute HTTP(S) URLs. Two static HTML hypotheses, no script execution.

**Inconclusive.** Missing/ambiguous plan or original, unqualified chronology/channel, source recovery outside admitted boundary, language/URL outside closed admission, unplanned outside annotation or missing required runtime.

**When NA is allowed.** No automatic NA; an empty plan does not establish non-applicability.

**Limits.** Supplied cluster and primary mode declarations: no capture authenticity, site completeness, TS22 language validity, indexability/canonical, TS24 x-default suitability, translation, executed JavaScript or Google processing. Relevant supplied sitemap/DOM channels remain outside this profile.

## TS24 — x-default represents a neutral destination or an explicit default variant.

**Severity**: minor. **Unit**: locale-cluster.

**Required inputs**: http, hreflang, intent.

**Applicability.** Group and x-default policy supplied before capture; bounded xdefault-role-v1 profile.

**Method.** Read native HTML/HTTP Link observations; check destination, motivated context, captured availability and bound supplied role review; retain unknowns and contested reviews.

**Acceptance.** Qualified presence/context, policy-consistent target, original200 and consistent supplied review. Independently evidenced failure is NC; no inferred approval or semantic validity.

**Evidence.** Prior policy/context, original HTTP and hashes, primary/secondary observations, original bound reviews, dates and unknowns.

**When NA is allowed.** No native NA or manual override; historical manual dossiers stay separate, optional absence is inconclusive.

**Limits.** Supplied scope, no representative audience or authenticated semantic role; HTTP200 does not detect error templates/soft404s. No translation, Google visit, indexing, completeness or global conformity.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/specialty/international/localized-versions](https://developers.google.com/search/docs/specialty/international/localized-versions)

### TS24-A01 — Documented x-default role in the prior context.

`TSEP@0.1.0-draft.41:TS24-A01`

**Required inputs**: http, hreflang, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Group and x-default policy supplied before capture; bounded xdefault-role-v1 profile.

**Method.** Read native HTML/HTTP Link observations; check destination, motivated context, captured availability and bound supplied role review; retain unknowns and contested reviews.

**Acceptance.** Pass requires every surface qualified, an unambiguous expected target, its original200 and bound consistent review. Fail for qualified required-primary absence, any qualified target conflicting with the unique policy destination, including among multiple declarations, attributable404/410, contradicted URL distinctness or one bound defect review. Otherwise inconclusive.

**Evidence.** Prior policy/context, original HTTP and hashes, primary/secondary observations, original bound reviews, dates and unknowns.

**Assumptions.** Prior plan and one motivated context; one non-redirect GET per original, window<=24h, two static HTML hypotheses. Supplied review, unauthenticated author.

**Inconclusive.** Missing/unqualified plan, context, original or review; unqualified declarations or divergent hypotheses without an independent contradiction, contested reviews, status outside200/404/410, relevant unexamined channel or missing required runtime.

**When NA is allowed.** No native NA or manual override; historical manual dossiers stay separate, optional absence is inconclusive.

**Limits.** Supplied scope, no representative audience or authenticated semantic role; HTTP200 does not detect error templates/soft404s. No translation, Google visit, indexing, completeness or global conformity.

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

### TS31-A01 — Reviewed prior scope and hypotheses.

`TSEP@0.1.0-draft.41:TS31-A01`

**Required inputs**: structured-data, content, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Selected page with JSON-LD; planned source and DOM profile.

**Method.** Qualify the plan, dated guidance and bound prior scope/source-base/guidance review.

**Acceptance.** Three supported judgments; bound contradiction fails, missing or unknown review is inconclusive.

**Evidence.** Native HTTP, attributed trees, supplied contexts/guidance, recomputed graphs and bound reviews; jsonld-visible-content-v1 contract.

**Assumptions.** Supplied scope, bases, dates, visible content and judgments; hashes do not authenticate.

**Inconclusive.** Gaps, bounds, missing context/runtime, ambiguous reading, empty graph, notice or unknown review; independent contradictions preserved.

**When NA is allowed.** No atomic exemption; absence in a bounded profile does not establish NA.

**Limits.** JSON-LD and documentary review of the selected page; no Schema.org vocabulary validation, authenticated truth/visibility, rich result, indexing or ranking.

### TS31-A02 — Attributed source and rendered JSON-LD reading.

`TSEP@0.1.0-draft.41:TS31-A02`

**Required inputs**: structured-data, content, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Selected page with JSON-LD; planned source and DOM profile.

**Method.** Recompute exact scripts under both source hypotheses and all planned DOM states using supplied contexts.

**Acceptance.** Complete readings and at least one nonempty graph without notices; attributed invalid JSON fails, other limits are inconclusive.

**Evidence.** Native HTTP, attributed trees, supplied contexts/guidance, recomputed graphs and bound reviews; jsonld-visible-content-v1 contract.

**Assumptions.** Supplied scope, bases, dates, visible content and judgments; hashes do not authenticate.

**Inconclusive.** Gaps, bounds, missing context/runtime, ambiguous reading, empty graph, notice or unknown review; independent contradictions preserved.

**When NA is allowed.** No atomic exemption; absence in a bounded profile does not establish NA.

**Limits.** JSON-LD and documentary review of the selected page; no Schema.org vocabulary validation, authenticated truth/visibility, rich result, indexing or ranking.

### TS31-A03 — Content and type consistency reviewed per entity.

`TSEP@0.1.0-draft.41:TS31-A03`

**Required inputs**: structured-data, content, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Selected page with JSON-LD; planned source and DOM profile.

**Method.** Bind supplied content and every flattened node to complete reviews covering visibility, type, all properties and absence of fabrication.

**Acceptance.** Exact population and supported qualifications; bound supplied contradiction fails, gaps or unknowns are inconclusive.

**Evidence.** Native HTTP, attributed trees, supplied contexts/guidance, recomputed graphs and bound reviews; jsonld-visible-content-v1 contract.

**Assumptions.** Supplied scope, bases, dates, visible content and judgments; hashes do not authenticate.

**Inconclusive.** Gaps, bounds, missing context/runtime, ambiguous reading, empty graph, notice or unknown review; independent contradictions preserved.

**When NA is allowed.** No atomic exemption; absence in a bounded profile does not establish NA.

**Limits.** JSON-LD and documentary review of the selected page; no Schema.org vocabulary validation, authenticated truth/visibility, rich result, indexing or ranking.

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

### TS32-A01 — Qualified prior registry and corpus.

`TSEP@0.1.0-draft.41:TS32-A01`

**Required inputs**: structured-data, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Declared corpus of 2–16 JSON-LD exports using identifiers.

**Method.** Check distinct entities, plan and bound prior population/mapping/reference review.

**Acceptance.** Collision-free registry and three supported judgments; distinct-entity collision fails even with absent review.

**Evidence.** Prior registry, native exports, local contexts, recomputed graphs and bound reviews; jsonld-identity-corpus-v1 contract.

**Assumptions.** Declared/reviewed origin, completeness, bases, dates and mappings; not authenticated.

**Inconclusive.** Missing evidence, review, runtime or context; empty/named graph, notice or unqualified reference/ID. Independent contradictions preserved.

**When NA is allowed.** No NA in this bounded profile.

**Limits.** Supplied corpus coherence, no temporal stability, real identity, page collection, cross-document merging or Google guarantee.

### TS32-A02 — Required identifiers and corpus references.

`TSEP@0.1.0-draft.41:TS32-A02`

**Required inputs**: structured-data, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Declared corpus of 2–16 JSON-LD exports using identifiers.

**Method.** Recompute native exports independently and compare defined IRIs with the registry; inventory references and scope.

**Acceptance.** Required IRIs defined and scope/references qualified; required absence from a complete nonempty graph fails, gaps or ambiguity are inconclusive.

**Evidence.** Prior registry, native exports, local contexts, recomputed graphs and bound reviews; jsonld-identity-corpus-v1 contract.

**Assumptions.** Declared/reviewed origin, completeness, bases, dates and mappings; not authenticated.

**Inconclusive.** Missing evidence, review, runtime or context; empty/named graph, notice or unqualified reference/ID. Independent contradictions preserved.

**When NA is allowed.** No NA in this bounded profile.

**Limits.** Supplied corpus coherence, no temporal stability, real identity, page collection, cross-document merging or Google guarantee.

### TS32-A03 — Evidence-bound mapping and duplicate review.

`TSEP@0.1.0-draft.41:TS32-A03`

**Required inputs**: structured-data, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Declared corpus of 2–16 JSON-LD exports using identifiers.

**Method.** Bind each export and recomputed node to mapping, repetition/duplicate and reference-meaning reviews.

**Acceptance.** Exact coverage and supported judgments; bound contradiction fails, incomplete/unknown review is inconclusive.

**Evidence.** Prior registry, native exports, local contexts, recomputed graphs and bound reviews; jsonld-identity-corpus-v1 contract.

**Assumptions.** Declared/reviewed origin, completeness, bases, dates and mappings; not authenticated.

**Inconclusive.** Missing evidence, review, runtime or context; empty/named graph, notice or unqualified reference/ID. Independent contradictions preserved.

**When NA is allowed.** No NA in this bounded profile.

**Limits.** Supplied corpus coherence, no temporal stability, real identity, page collection, cross-document merging or Google guarantee.

## TS33 — Errors, warnings and unsupported uses are distinguished.

**Severity**: minor. **Unit**: page.

**Required inputs**: structured-data, validator-output, intent.

**Applicability.** Selected page with bound HTTP/DOM JSON-LD captures and a separate native Google indexed result.

**Method.** Qualify the plan; recompute capture syntax and Schema.org names; separately classify native indexed-version messages and their decisions.

**Acceptance.** All three rules pass within the declared scope: qualified plan, attributed syntax and names, indexed messages without blocking errors and with an exact review. Correspondence between snapshots remains unestablished.

**Evidence.** Report with no blocking error and qualified warnings.

**When NA is allowed.** No NA in this profile; missing markup or evidence remains NT.

**Limits.** Vocabulary names and roles only; no inferred complete semantic validity, cross-snapshot correspondence, current eligibility or display. Supplied origins and dates are not authenticated.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data)

### TS33-A01 — Qualified prior scope, features and layers.

`TSEP@0.1.0-draft.41:TS33-A01`

**Required inputs**: structured-data, validator-output, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Selected page, bound HTTP/DOM JSON-LD captures and separate indexed APIv1 snapshot.

**Method.** Check prior plan, dated feature guidance and bound scope/support/separation review.

**Acceptance.** Three supported qualifications; reasoned contradiction fails, absence/unknown is inconclusive.

**Evidence.** Plan, native captures, pinned vocabulary30.1, original API outputs and bound reviews; jsonld-validation-layers-v1 contract.

**Assumptions.** Supplied/reviewed origin, dates and completeness, not authenticated; Google backend version unexposed.

**Inconclusive.** Missing evidence/review/runtime, unattributed layer, unknown format/severity or undetected feature; independent errors retained.

**When NA is allowed.** No NA in this profile.

**Limits.** Schema.org names only; separate snapshots, no inferred live test, current eligibility, display or indexing.

### TS33-A02 — Syntax and vocabulary names on bound captures.

`TSEP@0.1.0-draft.41:TS33-A02`

**Required inputs**: structured-data, validator-output, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Selected page, bound HTTP/DOM JSON-LD captures and separate indexed APIv1 snapshot.

**Method.** Reprocess source/DOM with TS31 readers; compare classes/properties with complete Schema.org30.1, equivalent HTTP/HTTPS namespaces.

**Acceptance.** Attributed typed graphs without syntax error, missing term or contradictory role; unknowns remain distinct.

**Evidence.** Plan, native captures, pinned vocabulary30.1, original API outputs and bound reviews; jsonld-validation-layers-v1 contract.

**Assumptions.** Supplied/reviewed origin, dates and completeness, not authenticated; Google backend version unexposed.

**Inconclusive.** Missing evidence/review/runtime, unattributed layer, unknown format/severity or undetected feature; independent errors retained.

**When NA is allowed.** No NA in this profile.

**Limits.** Schema.org names only; separate snapshots, no inferred live test, current eligibility, display or indexing.

### TS33-A03 — Native Google messages and decisions retained without downgrade.

`TSEP@0.1.0-draft.41:TS33-A03`

**Required inputs**: structured-data, validator-output, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Selected page, bound HTTP/DOM JSON-LD captures and separate indexed APIv1 snapshot.

**Method.** Read all APIv1 messages, severities and features; bind an exact review to the indexed response, separate from current captures.

**Acceptance.** No ERROR/FAIL; exact coverage and qualifications. Error, omission or downgrade fails even when documented; technical failure is inconclusive.

**Evidence.** Plan, native captures, pinned vocabulary30.1, original API outputs and bound reviews; jsonld-validation-layers-v1 contract.

**Assumptions.** Supplied/reviewed origin, dates and completeness, not authenticated; Google backend version unexposed.

**Inconclusive.** Missing evidence/review/runtime, unattributed layer, unknown format/severity or undetected feature; independent errors retained.

**When NA is allowed.** No NA in this profile.

**Limits.** Schema.org names only; separate snapshots, no inferred live test, current eligibility, display or indexing.

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

### TS34-A01 — Attributable field cohort

`TSEP@0.1.0-draft.41:TS34-A01`

**Required inputs**: field-data, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Declared performance scope for this control and qualified reading profile.

**Method.** Identify source, request/returned key, URL/origin, device, period and population under performance-evidence-v1. No implicit scope fallback.

**Acceptance.** Cohort matches the plan with retained dates/provenance. Explicit lab-for-field substitution fails; a different or old cohort remains inconclusive.

**Evidence.** Original JSON with source/date/hash; plan and supplied review when required, diagnostics and limits under docs/performance-evidence.md.

**Assumptions.** Supplied data/reviews are not authenticated. Plan precedes assessment and lab runs; a historical cohort is not preregistration.

**Inconclusive.** Insufficient source/plan/dates/measures; unsupported format/profile, scope mismatch, exceeded bounds or missing review under the contract. Absence never becomes C or NA.

**When NA is allowed.** No automatic atomic exemption; whole-control non-applicability requires its own evidence.

**Limits.** C describes documentation, not good performance. No display/ranking, demonstrated cause, automatic human review or global conformity. Replay performs no new measurement.

### TS34-A02 — Retained p75 measurements and classes

`TSEP@0.1.0-draft.41:TS34-A02`

**Required inputs**: field-data, intent.

**Automation / Automatisation**: `automatic`.

**Applicability.** Declared performance scope for this control and qualified reading profile.

**Method.** Read LCP/INP/CLS p75 in native units and compare exactly with cited thresholds, without relabeling FID/TBT. Retain poor values and unknowns.

**Acceptance.** All three measures are classified correctly. A bound classification contradicting p75 fails; correctly documented poor performance passes.

**Evidence.** Original JSON with source/date/hash; plan and supplied review when required, diagnostics and limits under docs/performance-evidence.md.

**Assumptions.** Supplied data/reviews are not authenticated. Plan precedes assessment and lab runs; a historical cohort is not preregistration.

**Inconclusive.** Insufficient source/plan/dates/measures; unsupported format/profile, scope mismatch, exceeded bounds or missing review under the contract. Absence never becomes C or NA.

**When NA is allowed.** No automatic atomic exemption; whole-control non-applicability requires its own evidence.

**Limits.** C describes documentation, not good performance. No display/ranking, demonstrated cause, automatic human review or global conformity. Replay performs no new measurement.

### TS34-A03 — Reasoned decision bound to measurements

`TSEP@0.1.0-draft.41:TS34-A03`

**Required inputs**: field-data, intent.

**Automation / Automatisation**: `manual`.

**Applicability.** Declared performance scope for this control and qualified reading profile.

**Method.** Retain supplied review, author, provenance, date, source hash and decision for each metric; verify binding without fabricating judgment.

**Acceptance.** Each metric retains its class, reason and action. A contradictory class fails. Missing/incomplete/unbound review is inconclusive.

**Evidence.** Original JSON with source/date/hash; plan and supplied review when required, diagnostics and limits under docs/performance-evidence.md.

**Assumptions.** Supplied data/reviews are not authenticated. Plan precedes assessment and lab runs; a historical cohort is not preregistration.

**Inconclusive.** Insufficient source/plan/dates/measures; unsupported format/profile, scope mismatch, exceeded bounds or missing review under the contract. Absence never becomes C or NA.

**When NA is allowed.** No automatic atomic exemption; whole-control non-applicability requires its own evidence.

**Limits.** C describes documentation, not good performance. No display/ranking, demonstrated cause, automatic human review or global conformity. Replay performs no new measurement.

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

### TS35-A01 — Repeatable laboratory context and measurements

`TSEP@0.1.0-draft.41:TS35-A01`

**Required inputs**: lab-data, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Declared performance scope for this control and qualified reading profile.

**Method.** Retain a planned series of 2–10 distinct Lighthouse reports, dates, URLs, tool/version, client, device, throttling, native measures and spread.

**Acceptance.** Series matches planned context/count. URL contrary to plan fails; different context, missing measure or runtime error remains inconclusive.

**Evidence.** Original JSON with source/date/hash; plan and supplied review when required, diagnostics and limits under docs/performance-evidence.md.

**Assumptions.** Supplied data/reviews are not authenticated. Plan precedes assessment and lab runs; a historical cohort is not preregistration.

**Inconclusive.** Insufficient source/plan/dates/measures; unsupported format/profile, scope mismatch, exceeded bounds or missing review under the contract. Absence never becomes C or NA.

**When NA is allowed.** No automatic atomic exemption; whole-control non-applicability requires its own evidence.

**Limits.** C describes documentation, not good performance. No display/ranking, demonstrated cause, automatic human review or global conformity. Replay performs no new measurement.

### TS35-A02 — Diagnostic hypothesis and next verification

`TSEP@0.1.0-draft.41:TS35-A02`

**Required inputs**: lab-data, intent.

**Automation / Automatisation**: `manual`.

**Applicability.** Declared performance scope for this control and qualified reading profile.

**Method.** Bind a supplied review to ordered reports, measured metrics, a hypothesis and next measurement. Separate laboratory, INP and field results.

**Acceptance.** Bound review names hypothesis, metrics and action without field substitution. Explicit lab/CWV or TBT/INP substitution fails; absent review is inconclusive.

**Evidence.** Original JSON with source/date/hash; plan and supplied review when required, diagnostics and limits under docs/performance-evidence.md.

**Assumptions.** Supplied data/reviews are not authenticated. Plan precedes assessment and lab runs; a historical cohort is not preregistration.

**Inconclusive.** Insufficient source/plan/dates/measures; unsupported format/profile, scope mismatch, exceeded bounds or missing review under the contract. Absence never becomes C or NA.

**When NA is allowed.** No automatic atomic exemption; whole-control non-applicability requires its own evidence.

**Limits.** C describes documentation, not good performance. No display/ranking, demonstrated cause, automatic human review or global conformity. Replay performs no new measurement.

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

### TS36-A01 — Prior plan and release chronology.

`TSEP@0.1.0-draft.41:TS36-A01`

**Required inputs**: intent, change-history.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Selected release whose dated follow-up is assessed.

**Method.** Qualify the bound plan before baseline, receipt identities and baseline/deployment order.

**Acceptance.** Supported plan, matching identity and baseline recorded before deployment; explicit contradiction fails, gaps remain inconclusive.

**Evidence.** Bound plan/reviews, deployment receipt, native API and supplied normalized logs; release-monitoring-v1 contract.

**Assumptions.** Supplied scope, dates, layer and judgments; hashes alone authenticate nothing.

**Inconclusive.** Future stage, missing evidence, errors, unknown values, incomplete logs or invalid bindings; preserve independent contradictions.

**When NA is allowed.** No atomic exemption; absence or delay never establishes NA.

**Limits.** Documentary C for selected baseline/D+1/D+7/D+30; no causality, authenticated Google visit, indexing or global coverage.

### TS36-A02 — Observations attributed to follow-up stages.

`TSEP@0.1.0-draft.41:TS36-A02`

**Required inputs**: intent, search-console, logs, change-history.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Selected release whose dated follow-up is assessed.

**Method.** Read baseline/d1/d7/d30, qualify TS08-A02 API and exact-window log inventories.

**Acceptance.** All four stages reached, complete attributed evidence within bounds; future/absence/error remains inconclusive.

**Evidence.** Bound plan/reviews, deployment receipt, native API and supplied normalized logs; release-monitoring-v1 contract.

**Assumptions.** Supplied scope, dates, layer and judgments; hashes alone authenticate nothing.

**Inconclusive.** Future stage, missing evidence, errors, unknown values, incomplete logs or invalid bindings; preserve independent contradictions.

**When NA is allowed.** No atomic exemption; absence or delay never establishes NA.

**Limits.** Documentary C for selected baseline/D+1/D+7/D+30; no causality, authenticated Google visit, indexing or global coverage.

### TS36-A03 — Interpretation, decisions and closure bound to evidence.

`TSEP@0.1.0-draft.41:TS36-A03`

**Required inputs**: intent, search-console, logs, change-history.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Selected release whose dated follow-up is assessed.

**Method.** Compare claims to known values, retain changes without causality and qualify supplied reviews/decisions.

**Acceptance.** Faithful claims, supported reviews and complete cycle; false known claim or closure before a future stage fails; other gaps inconclusive.

**Evidence.** Bound plan/reviews, deployment receipt, native API and supplied normalized logs; release-monitoring-v1 contract.

**Assumptions.** Supplied scope, dates, layer and judgments; hashes alone authenticate nothing.

**Inconclusive.** Future stage, missing evidence, errors, unknown values, incomplete logs or invalid bindings; preserve independent contradictions.

**When NA is allowed.** No atomic exemption; absence or delay never establishes NA.

**Limits.** Documentary C for selected baseline/D+1/D+7/D+30; no causality, authenticated Google visit, indexing or global coverage.

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

**Method.** Declare and review matrix, configuration and policy before collection; compare native signals, content and access per cell; qualify contexts and cache reuse through bound evidence under delivery-evidence-v1.

**Acceptance.** All three rules pass over declared cells: reviewed policy, consistent signals and attributed mechanisms; legitimate variations, independent defects and unqualified cells remain distinct.

**Evidence.** Configuration, prior matrix, native HTTP, rendered states or positive exemptions, bound reviews and cache journals where tested. Googlebot access policy is qualified separately from test-client requests; no actual visit inferred.

**When NA is allowed.** Configuration attests to the absence of variation mechanisms.

**Limits.** First bounded profile with one canonical member per cell and reuse without transformation. Supplied reviews, sources, regions, clocks and logs are not authenticated; no general cache simulation. Two points do not cover all POPs/routes, and C does not establish actual Googlebot access.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** RFC 9110 defines Vary and HTTP response semantics. Google separately documents locale-adaptive page behavior.

**References**: [https://www.rfc-editor.org/rfc/rfc9110](https://www.rfc-editor.org/rfc/rfc9110); [https://developers.google.com/search/docs/specialty/international/locale-adaptive-pages](https://developers.google.com/search/docs/specialty/international/locale-adaptive-pages)

### TS39-A01 — Reviewed prior matrix and configuration

`TSEP@0.1.0-draft.41:TS39-A01`

**Required inputs**: configuration, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Delivery varying by region, cache, device or negotiation.

**Method.** Check window, cells, mechanisms, retained configuration and bound prior review, including representativeness and Googlebot access policy.

**Acceptance.** Configuration and matrix qualified by supported review; documented rejection = fail.

**Evidence.** Configuration, prior matrix, native HTTP, rendered states or positive exemptions, bound reviews and cache journals where tested. Googlebot access policy is qualified separately from test-client requests; no actual visit inferred.

**Assumptions.** Supplied intent, context and source/review qualifications; their truth remains to verify.

**Inconclusive.** Missing, late or unbound configuration/review; unqualified matrix minimum or mechanism.

**When NA is allowed.** No automatic atomic exemption.

**Limits.** First bounded profile with one canonical member per cell and reuse without transformation. Supplied reviews, sources, regions, clocks and logs are not authenticated; no general cache simulation. Two points do not cover all POPs/routes, and C does not establish actual Googlebot access.

### TS39-A02 — Signal consistency in each context

`TSEP@0.1.0-draft.41:TS39-A02`

**Required inputs**: http, content, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Delivery varying by region, cache, device or negotiation.

**Method.** Compare status/final URL, recalculate TS07-A01/A02/A03 and TS10-A01, then compare language/content/accessibility through bound reviews; retain each unknown.

**Acceptance.** All cells follow policy; positive rendering exemption retained. Any attributable contradiction fails despite other unknowns.

**Evidence.** Configuration, prior matrix, native HTTP, rendered states or positive exemptions, bound reviews and cache journals where tested. Googlebot access policy is qualified separately from test-client requests; no actual visit inferred.

**Assumptions.** Supplied intent, context and source/review qualifications; their truth remains to verify.

**Inconclusive.** Missing cell, source, rendering, review or profile; incomplete body, unbound context or unknown semantics.

**When NA is allowed.** No automatic atomic exemption.

**Limits.** First bounded profile with one canonical member per cell and reuse without transformation. Supplied reviews, sources, regions, clocks and logs are not authenticated; no general cache simulation. Two points do not cover all POPs/routes, and C does not establish actual Googlebot access.

### TS39-A03 — Context and cache attribution

`TSEP@0.1.0-draft.41:TS39-A03`

**Required inputs**: configuration, http, logs, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Delivery varying by region, cache, device or negotiation.

**Method.** Qualify contexts/mechanisms through bound sources; for cache, link stored entry, served request, layer, clock, Vary and freshness review.

**Acceptance.** Consistent attribution and policy over all cells/checks; attributed reuse incompatible with Vary or policy fails. A test is not an operator visit.

**Evidence.** Configuration, prior matrix, native HTTP, rendered states or positive exemptions, bound reviews and cache journals where tested. Googlebot access policy is qualified separately from test-client requests; no actual visit inferred.

**Assumptions.** Supplied intent, context and source/review qualifications; their truth remains to verify.

**Inconclusive.** Unqualified region, source, journal, linkage or freshness; Age/HIT, User-Agent, sequence or ETag alone are insufficient.

**When NA is allowed.** No automatic atomic exemption.

**Limits.** First bounded profile with one canonical member per cell and reuse without transformation. Supplied reviews, sources, regions, clocks and logs are not authenticated; no general cache simulation. Two points do not cover all POPs/routes, and C does not establish actual Googlebot access.

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

**Method.** Fix the population, matrix and policy before attempts; replay native inputs/outputs, bound events and negative rehearsal under release-invariants-v1.

**Acceptance.** Reviewed representative plan, covered executions and correct failure/unknown handling; all three rules pass. A correctly blocked SEO defect stays visible without failing the process.

**Evidence.** Bound plan/reviews, identified command/environment, native input/output receipts, process exit codes, JSONL journal and artifacts around application.

**When NA is allowed.** No relevant deployment or pipeline within the scope and period.

**Limits.** First strict native TSEP profile without overrides; supplied commands are never executed. Reviews, completeness, clocks and runner are supplied, not authenticated. C qualifies the declared process, not global SEO health, causality or remote CI.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Edikka governance and non-regression control; no single official document prescribes this complete pipeline.

**References**: TSEP / Edikka method.

### TS41-A01 — Prior plan and representativeness

`TSEP@0.1.0-draft.41:TS41-A01`

**Required inputs**: configuration, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Deployments subject to project-defined SEO invariants.

**Method.** Check the window, attempts, matrix, strict policy and bound representativeness review before the window.

**Acceptance.** Complete plan and supported review; explicit bound rejection = fail.

**Evidence.** Bound plan/reviews, identified command/environment, native input/output receipts, process exit codes, JSONL journal and artifacts around application.

**Assumptions.** Supplied population, comparable context, artifact identities and reviews; their truth remains to qualify.

**Inconclusive.** Missing, unbound, late or incomplete plan/review; unsupported profile, threshold or scope.

**When NA is allowed.** No automatic atomic exemption.

**Limits.** First strict native TSEP profile without overrides; supplied commands are never executed. Reviews, completeness, clocks and runner are supplied, not authenticated. C qualifies the declared process, not global SEO health, causality or remote CI.

### TS41-A02 — Execution coverage and output fidelity

`TSEP@0.1.0-draft.41:TS41-A02`

**Required inputs**: configuration, ci-output, change-history, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Deployments subject to project-defined SEO invariants.

**Method.** Recalculate retained inputs; check matrix, artifacts, command, triggers and chronology without executing argv.

**Acceptance.** Exact population and faithful outputs including retained unknowns; conclusive binding or output contradiction = fail.

**Evidence.** Bound plan/reviews, identified command/environment, native input/output receipts, process exit codes, JSONL journal and artifacts around application.

**Assumptions.** Supplied population, comparable context, artifact identities and reviews; their truth remains to qualify.

**Inconclusive.** Missing receipt, cell, review, event or runtime; ambiguous journal, extra execution or differing inconclusive recalculation.

**When NA is allowed.** No automatic atomic exemption.

**Limits.** First strict native TSEP profile without overrides; supplied commands are never executed. Reviews, completeness, clocks and runner are supplied, not authenticated. C qualifies the declared process, not global SEO health, causality or remote CI.

### TS41-A03 — Negative rehearsal and process response

`TSEP@0.1.0-draft.41:TS41-A03`

**Required inputs**: configuration, ci-output, change-history, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Deployments subject to project-defined SEO invariants.

**Method.** Check prior negative failure, distinct pass/fail/inconclusive exit codes and explicit block/apply or accept/hold event.

**Acceptance.** Effective negative rehearsal and phase-correct responses; masked failure/unknown, wrong action or observed override = fail.

**Evidence.** Bound plan/reviews, identified command/environment, native input/output receipts, process exit codes, JSONL journal and artifacts around application.

**Assumptions.** Supplied population, comparable context, artifact identities and reviews; their truth remains to qualify.

**Inconclusive.** Missing/unqualified rehearsal, process exit, binding or action; journal absence cannot establish a block.

**When NA is allowed.** No automatic atomic exemption.

**Limits.** First strict native TSEP profile without overrides; supplied commands are never executed. Reviews, completeness, clocks and runner are supplied, not authenticated. C qualifies the declared process, not global SEO health, causality or remote CI.

## TS42 — Each automated agent is governed according to its documented purpose.

**Severity**: major. **Unit**: policy.

**Required inputs**: configuration, operator-docs, intent.

**Applicability.** Automated agents covered by site policy.

**Method.** Document mappings and their review, retain the owner decision, then compare its implementation under agent-governance-v1; retain coupled purposes and unknowns.

**Acceptance.** All three rules pass for each declared target and mechanism; qualified policy matches the accepted choice, with supplied review and responsibility.

**Evidence.** Mechanism/purpose inventory, dated operator sources bound to reviews, owner decision and tradeoffs, captured robots policy.

**When NA is allowed.** No agent policy in the declared scope, with a reason provided.

**Limits.** Supplied scope and bounded robots profile; no automatic registry. Sources, reviews and decisions are unauthenticated; no inferred visit, real identity, operator compliance, indexing or citation.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.openai.com/api/docs/bots](https://developers.openai.com/api/docs/bots); [https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)

### TS42-A01 — Documented purposes and mechanisms

`TSEP@0.1.0-draft.41:TS42-A01`

**Required inputs**: operator-docs, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Each target URL and mechanism of the previously declared policy.

**Method.** Bind operator, actor, token, mechanism and purposes to dated UTF-8 sources; check hashes and supplied bound review.

**Acceptance.** Every mapping has a complete, dated, bound supported review with explicit robots applicability. A bound contradiction fails.

**Evidence.** Inputs, dates, hashes and detailed findings under docs/agent-usage-policy.md.

**Assumptions.** Supplied inventory; declared source interpretation and personal authority, without automatic authentication.

**Inconclusive.** Missing, stale or ambiguous source; missing hash, binding, completeness or review.

**When NA is allowed.** No automatic atomic exemption.

**Limits.** Supplied scope and bounded robots profile; no automatic registry. Sources, reviews and decisions are unauthenticated; no inferred visit, real identity, operator compliance, indexing or citation.

### TS42-A02 — Owner decisions and tradeoffs

`TSEP@0.1.0-draft.41:TS42-A02`

**Required inputs**: intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Each target URL and mechanism of the previously declared policy.

**Method.** Check every reasoned choice, the separate declared owner/delegate decision and its plan binding; retain any arbitration of coupled purposes.

**Acceptance.** Each mechanism/purpose pair has a choice and reason; the owner accepts the plan and its exact tradeoffs. A bound rejection fails.

**Evidence.** Inputs, dates, hashes and detailed findings under docs/agent-usage-policy.md.

**Assumptions.** Supplied inventory; declared source interpretation and personal authority, without automatic authentication.

**Inconclusive.** Missing/undeclared author, unbound decision, inconsistent dates, incomplete choice or arbitration.

**When NA is allowed.** No automatic atomic exemption.

**Limits.** Supplied scope and bounded robots profile; no automatic registry. Sources, reviews and decisions are unauthenticated; no inferred visit, real identity, operator compliance, indexing or citation.

### TS42-A03 — Captured policy and effective choice

`TSEP@0.1.0-draft.41:TS42-A03`

**Required inputs**: configuration, operator-docs, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Each target URL and mechanism of the previously declared policy.

**Method.** Group tokens case-insensitively, qualify mappings and compare Allow/Disallow with the effective choice; retain reading, tradeoffs, contradictions and unknowns.

**Acceptance.** For each qualified group, the attributable client robots 200 policy matches the accepted choice. Any independent contradiction fails.

**Evidence.** Inputs, dates, hashes and detailed findings under docs/agent-usage-policy.md.

**Assumptions.** Supplied inventory; declared source interpretation and personal authority, without automatic authentication.

**Inconclusive.** Opposing purposes without arbitration, unsupported mechanism, ignored field or missing HTTP/source/decision evidence; other robots profiles unqualified.

**When NA is allowed.** No automatic atomic exemption.

**Limits.** Supplied scope and bounded robots profile; no automatic registry. Sources, reviews and decisions are unauthenticated; no inferred visit, real identity, operator compliance, indexing or citation.

## TS43 — Access for authorized crawlers is tested with the full user-agent string and reconciled with logs.

**Severity**: major. **Unit**: request-set.

**Required inputs**: http, logs, operator-docs, intent.

**Applicability.** Access-policy tests for declared agents.

**Method.** Declare operator access separately from test-client treatment; compare its full chain, reconcile logs and qualify its origin honestly under agent-access-v1.

**Acceptance.** All three rules pass for the declared test scope, with planned response, qualified correlation and explicitly unverified operator identity; an intended denial can conform.

**Evidence.** Prior plan, reviewed full User-Agent, raw HTTP, native JSONL logs, bound supplied reviews, command/receipt and identity qualification.

**When NA is allowed.** No agent to test in the declared policy.

**Limits.** First profile: assessor-initiated test client; no actual visit, identity, security or operator access inferred. Sources, logs, reviews and receipt are unauthenticated.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Technical reference; the TSEP acceptance rule remains an editorial proposal.

**References**: [https://developers.openai.com/api/docs/bots](https://developers.openai.com/api/docs/bots)

### TS43-A01 — Full client and expected treatment

`TSEP@0.1.0-draft.41:TS43-A01`

**Required inputs**: http, operator-docs, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Each URL and HTTP client within the previously declared test scope.

**Method.** Read sources and bound review; check the dated HTTP chain then planned test-client response/body.

**Acceptance.** Reviewed documentation and response agree with the test plan; retain independent contradictions despite other missing evidence.

**Evidence.** Evidence, dates, bindings and observations under docs/agent-access-evidence.md.

**Assumptions.** Supplied sources, context, log quality and reviews; test scope limited to its client.

**Inconclusive.** Missing client/source/review, incomplete chain, absent test expectation or required body reference.

**When NA is allowed.** No automatic atomic exemption.

**Limits.** First profile: assessor-initiated test client; no actual visit, identity, security or operator access inferred. Sources, logs, reviews and receipt are unauthenticated.

### TS43-A02 — Chain reconciled with logs

`TSEP@0.1.0-draft.41:TS43-A02`

**Required inputs**: http, logs, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Each URL and HTTP client within the previously declared test scope.

**Method.** Check export and layer/ID/cache/clock review, then identify each unique in-window line before literal comparison.

**Acceptance.** Every hop has an attributed record with matching method, URL, client and status; any qualified difference fails despite another missing hop.

**Evidence.** Evidence, dates, bindings and observations under docs/agent-access-evidence.md.

**Assumptions.** Supplied sources, context, log quality and reviews; test scope limited to its client.

**Inconclusive.** Missing logs, client-supplied/reused ID, duplicate, other layer, unknown format or insufficient window/review.

**When NA is allowed.** No automatic atomic exemption.

**Limits.** First profile: assessor-initiated test client; no actual visit, identity, security or operator access inferred. Sources, logs, reviews and receipt are unauthenticated.

### TS43-A03 — Test origin without invented identity

`TSEP@0.1.0-draft.41:TS43-A03`

**Required inputs**: http, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Each URL and HTTP client within the previously declared test scope.

**Method.** Check bound execution receipt and supplied attribution; distinguish assessor test from an operator visit.

**Acceptance.** Assessor-test origin, not-verified operator identity and no real-visit claim; any bound contrary claim fails.

**Evidence.** Evidence, dates, bindings and observations under docs/agent-access-evidence.md.

**Assumptions.** Supplied sources, context, log quality and reviews; test scope limited to its client.

**Inconclusive.** Missing receipt/command/attribution, inconsistent dates, absent binding or ambiguous identity status.

**When NA is allowed.** No automatic atomic exemption.

**Limits.** First profile: assessor-initiated test client; no actual visit, identity, security or operator access inferred. Sources, logs, reviews and receipt are unauthenticated.

## TS44 — Critical content and evidence remain accessible without undocumented JavaScript execution.

**Severity**: major. **Unit**: page.

**Required inputs**: http, html, render, content, intent.

**Applicability.** Content intended for declared automated consumers.

**Method.** Declare critical facts and paths before collection; verify no-JS access, values and exact representation reviews under critical-content-nojs-v1.

**Acceptance.** All three rules pass for the no-JavaScript reference client, with qualified delivery, coherent values and bound reviews; no actual consumption inferred.

**Evidence.** Prior plan/review, complete HTTP chains, raw HTML/JSON, attributed rendered tree and bound context reviews.

**When NA is allowed.** No content intended for these consumers in scope.

**Limits.** First bounded HTML/JSON profile, optional Node and supplied rendered evidence; no authenticated CSS visibility, truth, reviewer identity, ingestion or citation. Authored DOM explicitly synthetic.

C requires all expectations across the declared scope. NC requires evidenced contradiction; otherwise NT. NA requires evidence of non-applicability.

**Source scope.** Partial scope: Google documents JavaScript rendering for Google Search. This control cautiously extends verification to consumers whose rendering capabilities are not uniformly documented.

**References**: [https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics); [https://developers.openai.com/api/docs/bots](https://developers.openai.com/api/docs/bots); [https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)

### TS44-A01 — Prior critical scope

`TSEP@0.1.0-draft.41:TS44-A01`

**Required inputs**: content, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Content intended for declared automated consumers.

**Method.** Check inventory, no-JS client, planned states/resources and bound review predating captures.

**Acceptance.** Complete scope supported by review; bound rejection = fail.

**Evidence.** Prior plan/review, complete HTTP chains, raw HTML/JSON, attributed rendered tree and bound context reviews.

**Assumptions.** Supplied inventory, expected references, context and reviews; scope fixed before capture, unauthenticated evidence.

**Inconclusive.** Missing, late, unbound or incomplete plan/review, or different reference capability.

**When NA is allowed.** No automatic atomic exemption.

**Limits.** First bounded HTML/JSON profile, optional Node and supplied rendered evidence; no authenticated CSS visibility, truth, reviewer identity, ingestion or citation. Authored DOM explicitly synthetic.

### TS44-A02 — Delivery path without JavaScript

`TSEP@0.1.0-draft.41:TS44-A02`

**Required inputs**: http, html, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Content intended for declared automated consumers.

**Method.** Check the prior path, explicit resource link if needed, anonymous HTTP and all critical elements.

**Acceptance.** Expected destination/response and present elements; any qualified denial, wrong path or absence fails.

**Evidence.** Prior plan/review, complete HTTP chains, raw HTML/JSON, attributed rendered tree and bound context reviews.

**Assumptions.** Supplied inventory, expected references, context and reviews; scope fixed before capture, unauthenticated evidence.

**Inconclusive.** Missing capture, unsupported format/runtime/link/context or incomplete unqualified reading.

**When NA is allowed.** No automatic atomic exemption.

**Limits.** First bounded HTML/JSON profile, optional Node and supplied rendered evidence; no authenticated CSS visibility, truth, reviewer identity, ingestion or citation. Authored DOM explicitly synthetic.

### TS44-A03 — Value and context coherence

`TSEP@0.1.0-draft.41:TS44-A03`

**Required inputs**: http, html, render, content, intent.

**Automation / Automatisation**: `semiAuto`.

**Applicability.** Content intended for declared automated consumers.

**Method.** Compare qualified values from each representation/rendered state to the plan; review whole critical context with representation-specific bindings.

**Acceptance.** Coherent values and reviews; qualified contradiction retained despite other missing evidence.

**Evidence.** Prior plan/review, complete HTTP chains, raw HTML/JSON, attributed rendered tree and bound context reviews.

**Assumptions.** Supplied inventory, expected references, context and reviews; scope fixed before capture, unauthenticated evidence.

**Inconclusive.** Missing/unknown review, rendering, value or attribution; unplanned supplied state or unsupported context.

**When NA is allowed.** No automatic atomic exemption.

**Limits.** First bounded HTML/JSON profile, optional Node and supplied rendered evidence; no authenticated CSS visibility, truth, reviewer identity, ingestion or citation. Authored DOM explicitly synthetic.
