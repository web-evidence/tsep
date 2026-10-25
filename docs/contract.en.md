[Draft.8 — directives, exclusion et preuves / directives, exclusion and evidence](migration-0.3.0-draft.8.md).

Édition draft.7 / Draft.7: [texte HTML principal v3, limites et migration / main-document text v3, limits and migration](migration-0.3.0-draft.7.md).

Préparation / preparation **0.3.0-draft.4** :44 contrôles avec98 règles atomiques bornées /44 controls with98 bounded atomic rules. TS26–30/37 added;85 prior rules preserved. [Contract](render-transport-evidence.md), [migration](migration-0.3.0-draft.4.md). Qualification evidence is separate; no real site audit or publication.

Candidate normative amendment **0.3.0-draft.6**: TS01 structural whitespace and TS02 complete-header trajectories with attributable collector limit stops. [Rules and migration](migration-0.3.0-draft.6.md). No historical dossier migrates implicitly.

Normative **0.3.0-draft.5** amendment: TS30 H1 prerequisites and TS37-A03 resolution/independent observations are clarified in [v2 contract](render-transport-prerequisites-v2.md). See [migration](migration-0.3.0-draft.5.md). Other rules remain identical.

0.3.0-draft.1 adds only TS13-A01/A02 and TS14-A01; 30 rule-bearing controls /70 rules. RC1 rules and their versions are retained. [Bilingual contract](sitemap-quality-evidence.md), [migration from RC1](migration-0.3.0-draft.1.md). Insufficient evidence remains NT; synthetic examples, no real audit. The RC1 scope below is historical.

Draft.44 / reader3: supplied TS25 review fields reviewer, assistance and reason are each limited to8192 raw UTF8 bytes before strip or normalization; each entire review object, including additional fields, to32768 compact UTF8 JSON bytes. Admission checks every supplied review, including unused ones. An overrun is technical refusal before publication, never public C or NT; exact originals are not rewritten. Each native rule diagnostic is bounded to4MiB of sorted compact UTF8 JSON, including A01 and error returns. Overflow produces an explicitly incomplete compact diagnostic retaining an independently established fail, otherwise inconclusive; never pass. Transport refuses that marker and also caps the sum of actual serialized TS25 observation artifacts per target at4MiB (UTF8 JSON indent2, trailing newline), for requested rules. Individual maxima do not guarantee that every combination satisfies aggregate bounds. Other controls and the shared validator are unchanged.
[Migration](migration-draft.44.md).

Draft.43 — TS25 non-object render boundary / frontière render non objet : [presence](critical-presence-evidence.md), [migration](migration-draft.43.md). Independent source failure retained / absence source indépendante conservée.

Draft.42 — TS25-A01/A02 : [présence critique source/rendu / source-render critical presence](critical-presence-evidence.md), [migration](migration-draft.42.md).

Draft.41 — TS24 : contradiction de destination unique même parmi plusieurs cibles / unique-destination contradiction including multiple targets. [Migration](migration-draft.41.md).

Draft.40 — TS24-A01 : [rôle x-default fourni / supplied x-default role](xdefault-role-evidence.md), [migration](migration-draft.40.md).

TS23 draft.39 : frontières typées et refus / typed boundaries and refusal are specified in [the TS23 profile](hreflang-reciprocity-evidence.md#typed-boundaries--frontières-typées), without changing historical controls.

Draft.39 — TS23-A01 : [hreflang fourni / supplied hreflang](hreflang-reciprocity-evidence.md), [migration](migration-draft.39.md).

Draft.38 — TS18-A01/A02/A03 : [graphe fourni / supplied graph](graph-reconciliation-evidence.md), [migration](migration-draft.38.md). Limites bornées, revues fournies / Bounded limits, supplied reviews.

Draft.37 — TS16-A01 : [liens entrants fournis / supplied incoming links](incoming-links-evidence.md), [migration](migration-draft.37.md). Population préalable uniquement / Prior population only.

Draft.36 — TS17-A01/A02 : [liens essentiels fournis / supplied essential links](essential-links-evidence.md), [migration](migration-draft.36.md). Source et états déclarés séparés / Separate source and provider-declared states.
TS17 intake: invalid HTTP types are technically refused; missing evidence or partial objects retain NT with a reason. See the linked contract.

TS15-A03 accepts only pass/inconclusive, declared by the closed `allowed_outcomes` field; fail/NA rejected. See the sitemap-files contract and draft.35 migration.

Draft.35 — TS15-A01/A02/A03 : [fichiers fournis / supplied files](sitemap-files-evidence.md), [migration](migration-draft.35.md). Population déclarée, aucun serveur observé / Declared population, no server observation.

Draft.34 — TS33-A01/A02/A03 : [contrat / contract](structured-validation-evidence.md), [migration](migration-draft.34.md). Captures liées, messages natifs séparés / Bound captures, separate native messages. Erreur bloquante conservée / Blocking errors retained.

Draft.33 adds TS32-A01/A02/A03: prior registry, native IDs/references and bound reviews. [Contract](structured-identity-evidence.md), [migration](migration-draft.33.md). Supplied corpus coherence, no authenticated temporal stability.
Draft.32 adds TS31-A01/A02/A03: prior scope, native JSON-LD reading and entity-bound content reviews. [Bilingual contract](structured-content-evidence.md), [migration](migration-draft.32.md). Supplied evidence, no authenticated visibility/truth or rich-result guarantee.

Draft.31 adds TS36-A01/A02/A03: chronology, stages and supplied decisions. [Bilingual contract](release-monitoring.md), [intake](release-monitoring-intake.md), [migration](migration-draft.31.md). Strict baseline/D+1/D+7/D+30; future stages inconclusive, no causality or authenticated Google visit.

Draft.30 adds TS12-A01/A02/A03: plan, attributed comparisons and supplied review/decision. [Bilingual contract](canonical-comparison.md), [migration](migration-draft.30.md). Planned rendering required; documentary C, not TS10 or indexing.

Draft.29 adds three TS08 rules: scope/objectives, native inspections and bound reviews/decisions. [Bilingual contract](inspection-evidence.md), [migration](migration-draft.29.md). C qualifies selected-set documentation, never guaranteed indexing.

# Report contract — TSEP 0.3.0-draft.1

## RC1 scope / Release-candidate scope

RC1 preserves TS01–TS44 and the existing rule-bearing scope: 28 controls, 67 executable atomic rules. TS03-A01 evaluates only the supplied synthetic .invalid HTTP matrix and literal body markers; it performs no site acquisition and does not classify Google soft 404s. See the [TS03 evidence contract](ts03-response-evidence.md), [migration](migration-0.2.0-rc.1.md), and [44-control status](control-implementation-status.md). No real-site use is verified by this release.

### TS06-A01 — bounded synthetic access matrix

`TS06-A01` is a semi-automated comparison of supplied, prior-plan-bound synthetic HTTP GET traces for declared `.invalid` route/role cells and cold/seed/replay labels. Its result applies only to those authored fixture cases. It never establishes real identity, authentication, server-side protection, shared-cache behavior, or all-site coverage. A supplied leak or unauthorized successful representation is `fail`; missing/partial/ambiguous evidence is `inconclusive`. See [the TS06 evidence profile](ts06-access-evidence.md) and [draft.46 migration](migration-draft.46.md).


### Delivery variants — draft.27

TS39 adds three rules: matrix/configuration, per-cell signals and context/cache attribution. [Contract](delivery-evidence.md), [migration](migration-draft.27.md). Native tests and supplied reviews remain explicit; no actual Googlebot access inferred.


### TS41 clarification — draft.26

Inconclusive recalculation cannot alone accuse an old positive output; unchanged unknown output masked by exit 0 remains a contradiction. [Migration and FR/EN correction](migration-draft.26.md). Reader unchanged.

### Deployment process — draft.25

TS41 adds three rules: plan, execution coverage and failure/unknown response. [Contract](release-invariants.md), [migration](migration-draft.25.md). C qualifies the declared process; a correctly blocked SEO defect stays visible.

### Critical content — draft.24

TS44 adds three rules: prior scope, no-JS delivery, representation coherence and review. [Contract](critical-content-evidence.md), [migration](migration-draft.24.md). No factual truth, actual agent access or citation inferred.

### Agent access and logs — draft.23

TS43 adds three rules for the test client, its traces and attribution. Expected denial can conform; no actual operator access inferred. [Contract](agent-access-evidence.md), [migration](migration-draft.23.md).

### Agent purposes — draft.22

TS42 adds three rules: sources/reviews, owner decisions, and bounded robots comparison. [Contract](agent-usage-policy.md), [migration](migration-draft.22.md). Coupled purposes and explicit tradeoffs; no actual visit inferred.

### Performance — draft.21

TS34 and TS35 have five atomic rules. [Performance contract](performance-evidence.md), [migration](migration-draft.21.md). C describes documentation, not good performance; retain values/classes and missing reviews.

### Preview intent / Intentions de présentation — draft.20

Optional prior google-preview-intent-v1 extends TS07-A01/A03 with text/image/video permission intervals. [Normative bilingual contract](preview-intent.md) and [migration](migration-draft.20.md). Earlier inputs, extraction, reviews and unknowns remain separate. No inferred Google display.

### HTTP canonical context — draft.19

Optional prior `intent.canonical.http_reader: "http-link-context-v1"` extends
TS10-A01/A02 under the [HTTP contract](http-canonical-context.md). Absent selection
keeps the fixed historical reader. First rel, anchor context, literal destination,
evidence and unknowns are retained; no human review or Google selection is inferred.
See [explicit migration](migration-draft.19.md).


## Declared scope

Select a named evidence profile or an explicit custom list of controls before
assessment. Identify the actual target URLs, hosts, inventories, clusters or
release records as stable strings in `scope.targets`; describe selection and
exclusions. The target is the unit being assessed, not necessarily a single URL.
A cluster or inventory target must resolve to an included evidence description
listing its members. Do not label a single URL as an entire site.

Use separate reports when different controls have different target populations.
Never extrapolate sample results to untested templates, regions, bots or times.
Changing scope requires a new report; retain the previous report and rationale.

## Control outcomes

| Code | Meaning | Required basis |
| --- | --- | --- |
| C | Conforming in scope | All expectations, targets and required input kinds covered |
| NC | Nonconforming in scope | At least one evidenced contradiction to an expectation |
| NA | Not applicable | Positive evidence that applicability is absent across the scope |
| NT | Not established | Not started, missing access/evidence, partial or inconclusive assessment |

Every result includes a reason and the procedure actually performed. `NT` records
`not-started` or `inconclusive`; the latter includes attempts and known limitations.
A timeout, unavailable account, unknown directive or incomplete inventory is not
automatically an SEO failure. When there is an observed contradiction, report NC
and explain remaining gaps. NA is never a substitute for missing access.

The schema validates structure. Additional normative rules implemented by the
CLI require unique IDs and targets, exact result/control correspondence, full
named-profile coverage, evidence for C/NC/NA, and complete target coverage for
C/NA. C additionally requires each control's input kinds for every target.
An input file may cover a declared set of targets, but its content must justify
that coverage. The validator checks the declaration, not its truth.

Expectations concern verification practices as well as technical behavior.
For example, TS08 establishes a documented indexing state; it does not promise
indexation. TS34 establishes correctly read field metrics; a C there does not
mean the measured performance is good. Record unfavorable underlying measures
and their operational consequences explicitly.

## Atomic rules of declared controls

Report format is `2`. A **control** retains its TSxx identifier and scoped
C/NC/NA/NT outcome. An **atomic test** addresses an expectation identified by
`TSxx-Ayy` in the canonical JSON. An **observation** is a dated capture or finding
in a given context; its existence alone does not pass a test. Each rule declares `automation`: `automatic`, `semiAuto` or `manual`.

For controls declaring atomic rules in the canonical source, `atomic_results` links each `rule_id`/`target` pair to
an `outcome` (`pass`, `fail`, `not-applicable`, `inconclusive`), a `reason` and
`evidence_ids`. Evidence must also be linked by the control result and cover the
target. A `pass` requires every input kind of the rule. A `fail` contradiction
may be evidenced by a subset of inputs. `not-applicable` is allowed only for rules
with `na_inputs`, with those records and positive justification. A missing file
is not such a justification.

- C requires every rule/target pair, without failure or unknowns, with required
  evidence. One passing test, probe exit 0, an omission or exemptions alone are
  insufficient. The CLI rejects an inconsistent C claim rather than silently
  converting it to NT.
- NC requires at least one evidenced `fail`; retain other unknowns. In this case
  `complete` means the NC conclusion is established, not exhaustive collection.
- NT cannot hide a `fail`; retain attempts and gaps. `not-started` admits no
  observations; `inconclusive` may include passing tests.
- Whole-control NA requires its non-applicability condition, `intent` evidence
  covering every target and no applicable atomic observations. For TS10 that
  evidence includes inventory and strategy. A positive record of no sitemap or
  no HTML surface does not exempt the other rules.

Each target identifies a URL or explicitly inventoried family. Fix crawler,
intent, conditions, link population and required states in evidence before
assessment; split reports for incompatible contexts. For non-HTML, the `html`
record documents its legitimate absence and received type. For a family with no
sitemap, the `sitemap` record justifies that absence. These are not fabricated
HTML/XML captures. TS07 now requires `robots` evidence; required rendering must
be attached as `render`. TS10-A01 also requires DOM evidence when rendering affects
declarations, although the validator cannot determine that need.

The CLI checks declarations, references and coverage, not the correctness of
HTTP/HTML interpretation, intent or exemptions. The historical method fixtures have authored reference verdicts. The separate
[executable conformance suite](conformance.md) interprets raw inputs for ninety-eight rules
within documented bounds; it does not implement all controls. No C extends to unselected
controls, an entire site or actual indexing. See [migration and cases](migration-draft.2.md).

### TS07-A03 rendered captures — draft.4

A pass requires http, html, render and intent inputs for the target so the test
is linked to its source. The plan fixes states, interactions and waiting conditions
before observations. Retain browser/version, JavaScript activation, errors, date
and context per capture. Final URL, context and an HTTP-trace digest bind DOMs to
the assessed source.

A contradiction in a complete, attributable state yields fail even when another
state remains inconclusive. Without a contradiction, a missing, truncated,
erroneous, ambiguous or unattributable required state prevents pass. Removing an
initial source noindex later does not pass A03; the A01 source verdict remains
separate. Prior plan review and capture sufficiency keep this rule semiAuto.

An exemption requires a documented source-bound review with supporting records;
an empty list, absent DOM or unsupported “no JS” assertion is insufficient. The
interpreter compares supplied captures: it neither executes JavaScript nor
simulates the engine. See [format and limits](rendered-states.md) and
[draft.4 migration](migration-draft.4.md). Report validation checks evidence
references/kinds; it does not itself parse DOMs or the plan.

### TS10 canonical families — draft.5

A01 reconciles declarations across every inventoried member: required methods and
states fixed in advance, dated captures bound to context/source. Retain repeated
signals and contradictions despite other gaps. Rendering exemptions need supported
review. A02 requires a directly responding 200 destination and reasoned human
review for each member compared with the preference, fingerprint-bound to examined
records; it remains manual.

A03 reconciles every expected index/child before concluding omission. A04 reconciles
all source pages and required states; zero links cannot pass a partial population.
An attributable failure survives another missing branch/page. Exceptions identify
their precise subject and reason. Positive sitemap absence exempts A03 only.

The [executable format](canonical-families.md) bounds HTTP/HTML, DOM and XML
interpretation. Reports retain evidence, results and unknowns; report validation
neither parses these captures nor guarantees review truth. No automatic TS10 C,
no C from a subset of its rules. See [draft.5 migration](migration-draft.5.md).

## Automation and representation identity

A C with `assessor.mode: "automatic"` is valid only if the control has a nonempty
set of atomic rules, **all** with `automation: "automatic"`, and the report declares
`assessor.tool: {"name": "…", "version": "…"}` with nonblank values. All existing
rule/target/evidence requirements still apply. An exemption does not bypass the
automation requirement. Controls without defined atomic rules cannot yield an
automatic C. `semiAuto` requires human interpretation; `manual` requires human
judgment. These classifications describe the method, not evidence quality.

TS01-A01 and A02 are automatic. A01 requires a final **200**; its inherited title
is broader. A02 compares prior `expected_final_url` and `expected_body_sha256`:

1. A different final URL is fail, even without a reference digest.
2. At the same URL, an identical complete-body digest is pass.
3. Otherwise, prior `representation: "stable"` makes any digest change fail.
4. Otherwise, valid `required_markers` / `forbidden_markers` yield fail if a
   required marker is missing or a forbidden marker appears. Pass requires
   **at least one required marker**, all required markers present and all forbidden
   markers absent. Forbidden-only markers all absent, or no valid criteria:
   inconclusive.

Reference URL/digest must be valid; incomplete/unattributable captures cannot be
passed. Markers are unique, nonblank UTF-8 strings, matched literally and case
sensitively in **extracted source text**, without regex:

- HTML: textual segments with character references decoded; comments, `script`
  and `style` content, tags and attributes excluded. Never concatenate segments
  across a tag or comment to manufacture a marker.
- `text/plain`: the entire decoded body, without interpreting apparent markup.
- Without a distinct profile, no whitespace or case normalization. Unresolved extraction or decoding cannot
  establish a conclusive marker-based verdict.

Extraction does not affect the complete-body SHA-256. It does not measure
visibility: title and CSS-hidden text may count. CSS and JavaScript are not
executed; unsupported reference contexts are documented in
[conformance](conformance.md).
Empty arrays establish nothing. A forbidden marker contained in a required marker
makes the intent contradictory. Invalid markers or an unknown representation
policy cannot resolve a changed digest. The ordered checks above apply: markers
are an alternative for a changed digest; they never bypass a stable-policy failure.
Missing reference digest at the same URL stays inconclusive even with markers.
The owner remains responsible for reference and marker relevance. A timestamp
change alone is not an SEO failure. NT for blocking TS01 still yields NO_GO.
TS07-A01/A02/A03 and TS10-A01/A03/A04 are semiAuto; TS10-A02 is manual.
See [draft.7 migration](migration-draft.7.md) for mandatory reassessment.

Draft.28 adds optional prior `identity_reader: "html-tree-markers-v1"` only to the
HTML marker branch. The [parsed-marker contract](source-markers.md) defines its two
whole-document hypotheses, attributed segments, raw CRLF/CR preprocessing to LF
and unsupported contexts/reported errors. Criteria remain literal; both pass gives
pass, both fail gives fail, otherwise inconclusive. Absent this field preserves the
historical reader. URL/hash/stability precedence remains. New intent followed by new
capture is required, without implicit historical migration; see
[draft.28 migration](migration-draft.28.md).

See [migration from draft.2](migration-draft.3.md) and [CLI workflow](cli.md).
`add-evidence` and `record` validate before replacing the report, refresh its
issuance date, and never infer outcomes. Preserve a copy of earlier assessments.

## Evidence bundle

Keep the report and evidence together. Each artifact declares ID, relative POSIX
path, SHA-256, kind, target IDs, observation time with timezone, and a description.
Declare access as `public`, `restricted` or `synthetic`. TSEP-1 requires public
evidence except declared intent; TSEP-2 additionally accepts restricted evidence from the target engine’s
webmaster tools; Google is the first normative series (TS08/TS12). An assessor still has to document its actual origin. Synthetic
data is explicitly marked in gate output. The `webmaster-tools` kind requires `engine`; only `engine: "google"` satisfies
the existing `search-console` input requirement. The legacy `search-console` kind
means Google and cannot declare another engine. Other engines require their own
future normative series; their evidence does not validate Google controls.
Absolute paths, traversal and symlinks escaping the evidence root are rejected.
All references must resolve locally; no URL is fetched by validation.

Capture the command, tool/version, environment, request conditions, sampling and
relevant raw outputs inside the evidence. Preserve response headers and the stage
observed (source HTML versus rendered DOM). Evidence must precede report issuance.
State redactions and retention/access restrictions. A public version with omitted
evidence cannot claim public reproducibility of the restricted findings.

Hashes prove file integrity only. The person or tool signing an assessment remains
responsible for provenance, accuracy and authorized use. This draft has no trusted
timestamp service, cryptographic signing, or tamper-proof collection pipeline.

## Gate decision

The gate always refers to selected controls and declared targets only. Severity is
read from the pinned protocol, never downgraded inside a report. Apply in order:

1. Blocking NC or blocking NT: `NO_GO`.
2. Any remaining NT, or every result NA: `INCOMPLETE`.
3. Any major NC: `REVIEW`.
4. Otherwise: `GO_WITH_RESERVATIONS`; retain minor/informational NC and limitations.

This is TSEP's proposed delivery policy, not a search-engine rule. A valid report
can be NO_GO. A GO does not prove indexing, ranking, accessibility, security or
the quality of every page. The responsible owner makes the delivery decision.
No configurable severity overrides or silent waivers exist in this draft.

`validate` exits 0 for a structurally/semantically valid report regardless of gate.
`gate` exits 0 for GO_WITH_RESERVATIONS, 1 for NO_GO, 2 for REVIEW/INCOMPLETE,
64 for an invalid report, missing artifact or invalid invocation data.
The argument parser uses the conventional exit code 2 for malformed CLI syntax.

JSON retains `blocking` IDs and adds `blocking_causes`, an array of
`{control_id, status}` with NC or NT for every blocking control. FR/EN readable
summaries show the same cause. Neither the decision nor exit codes change.

## Versions and implementation claims

Pin both version and protocol SHA-256. Cite IDs as
`TSEP@0.1.0-draft.14:TS01`. Never silently replace a released artifact. Changes to
applicability, expectations, required evidence or decisions require a new version
and migration note. TS01–TS44 are permanent identities, not reusable slots.

This candidate has one implementation of report validation. Passing its tests
allows the narrow statement “passes the bundled report-interchange tests for
0.1.0-draft.14.” It does not establish implementation of all 44 assessment methods.
An implementation must publish per-rule mapping and limitations before making a
broader claim. No compatibility with a third-party tool has yet been demonstrated.

## TS02 — draft.8

TS02-A01 requires a prior approved plan and a supplied review bound to plan/context. TS02-A02 compares HTTP trajectories and preserves prefix contradictions despite gaps. Missing review prevents C; missing capture does not establish NA. Server-side HTTP scope, format, bounds and migration are in [redirects](redirects.md) and [draft.8 migration](migration-draft.8.md). TS01/TS07/TS10 rule semantics remain unchanged.


## TS04 and TS07 access — draft.9

TS04-A01 compares a prior origin/crawler resource matrix with its declared robots
profile. TS04-A02 requires planned access/trajectories and supplied resource reviews
bound to the responses. A demonstrated contradiction remains fail despite other
gaps; missing review/capture never becomes pass or NA. A02 exemption requires a
positive inventory review of no required resources before intent. Profiles, format,
bounds, digests and dates are specified in [robots method](robots.md), consistently
with the canonical JSON rules. Choose the profile before measurement, never after
seeing which profile yields a favorable result.

TS07-A02 shares this reader. Inputs without robots_policy keep the fixed historical
legacy-exact-v1 profile; explicit-profile refusal never falls back to it. Attributable
HTTP 401/403 denial remains fail without robots. Rendering/directive/review limits
remain. See [draft.9 migration](migration-draft.9.md). No actual engine visit,
global conformity or indexing is inferred.

## Structured DOM states — draft.10

TS07-A03 and TS10-A01/A02/A04 accept a predeclared structured reader with complete
tree, serialization, bindings and navigation records. Authored trees remain synthetic;
separate acquisitions or known API alteration remain inconclusive. No fallback to
serialization to gain agreement. Reviews, headers and source HTML retain their role;
no engine equivalence. The [detailed contract](structured-rendering.md) and
[migration](migration-draft.10.md) define bounds, decisions and experimental differences.

## Collection agent and semantics — draft.11

Optional prior TS07 directive_crawler=googlebot separates directive semantics
from crawler, the unchanged exact HTTP agent. It assesses only this client's
representation. A02 requires an explicit matching robots product profile; no
Googlebot visit is inferred. Old inputs keep their behavior. The [same-navigation
laboratory](same-navigation-laboratory.md) and [migration](migration-draft.11.md)
describe evidence, refusals and limitations.

## TS04 client scope — draft.12

TS04 now accepts the same prior `directive_crawler=googlebot` field as TS07,
with an explicit `robots_policy` and matching `product_token`. `crawler` remains
the exact HTTP User-Agent, and every trace must still match that agent. Googlebot
group selection concerns the representation received by this client, not a
response received by Googlebot. Results explicitly retain this qualification.

Null, unsupported or inconsistent fields never fall back to the client group.
A resource response contradicting its declared status/destination remains a
failure limited to the observed client, including 401/403/429/5xx when 200 is
expected. It does not prove denial to Googlebot. Missing reviews and population
limits remain; the extension alone cannot establish C. Absent field preserves
legacy behavior. Retain the original package and declare a new plan before new
captures: [draft.12 migration](migration-draft.12.md).

## Known robots fields profile — draft.13

Optional prior `google-robotstxt-fields-v2` records twelve fields classified as
unused in google/robotstxt reporting at commit
`22b355ff855419e6a3ff8ff09c0ad7fdb17116f9`, plus sitemap. These fields change neither
access decisions nor groups. The closed registry, separate documentation/code
sources, retained values and display bounds are in the
[draft.13 migration](migration-draft.13.md). No TS42 verdict follows. Near names
and other fields remain inconclusive; old profiles and required reviews stay
unchanged. Never extend a prior intent retroactively.

## Sitemap page locations — draft.14

TS10-A03 accepts optional prior reader `sitemap-locations-v1`. Direct page loc
remains separate from XHTML/image annotations and ordinary fields retained without
value validation. The legacy profile is unchanged; unknown explicit values never
fall back. Omission still requires complete traversal; an attributable contradiction
is retained. Recognized structures, namespaces, captures, bounds and unknowns are
defined by the [method](sitemap-locations.md) and [migration](migration-draft.14.md).
This atomic success alone establishes neither whole TS10 C, hreflang/image validity
nor Google selection.

## Source directives — draft.15

TS07-A01 and the A03 source prerequisite accept optional prior html-tree-directives-v1. Agreement of two static alternatives stays distinct from rendered states. Refused contexts, encoding, bounds, byte attribution, observations and replay are normative in the [bilingual contract](source-directives.md), included in normative fingerprints. Legacy inputs and review requirements remain unchanged. See [migration](migration-draft.15.md).

### Canonical source — draft.16

The prior optional html-tree-canonical-v1 profile extends TS10-A01/A02 source reading
only. Its [normative bilingual contract](source-canonical.md) defines applicability,
inputs, alternative hypotheses, qualified contradictions, unknown contexts, evidence
and limits. All rendering/content reviews remain required; A04 and DOM readers are
unchanged. New calculations retain observations compared by replay. See the
[migration](migration-draft.16.md); no historical intent is retrofitted.

### Source links — draft.17

TS10-A04 accepts prior html-tree-links-v1 under intent.canonical.links. The [normative bilingual contract](source-link-policy.md) defines population, URLs, base, hypotheses, unknowns and bounds. Convergence scope, including zero observed links, accompanies atomic/control reasons, HTML, EARL and gate scope_notes. Rendering/reviews remain unchanged; [explicit migration](migration-draft.17.md).

### Unparseable bases — draft.18

TS10-A04 also accepts prior html-tree-links-v2. A first base whose href fails WHATWG parsing makes dependent hrefs inconclusive, while independent contradictions survive. Profile v1, A01/A02 and rendering remain unchanged. The [normative bilingual contract](source-link-policy-v2.md) and [migration](migration-draft.18.md) define evidence, hypotheses, observed zero and limits.


### TS05 — policy map only / carte de politique uniquement

Draft.45 adds TS05-A01: a semi-automated comparison of supplied prior intent and configuration. Pass means internal plan consistency only; it does not establish indexing or access control. See [TS05 evidence and limits](ts05-indexing-evidence.md), [dated source capture](source-captures/ts05-google-search-central-2026-10-16.md) and [migration](migration-draft.45.md).

The new `html-tree-markers-v2` intent excludes `noscript` segments from marker matching at reference, assessment and recheck. `html-tree-markers-v1` keeps its marker semantics; old dossiers retain their exact engine. A marker present only in `noscript` cannot satisfy the v2 profile.
