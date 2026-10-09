# Report contract — TSEP 0.1.0-draft.2

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

## Atomic rules for TS01, TS07 and TS10

Report format is `2`. A **control** retains its TSxx identifier and scoped
C/NC/NA/NT outcome. An **atomic test** addresses an expectation identified by
`TSxx-Ayy` in the canonical JSON. An **observation** is a dated capture or finding
in a given context; its existence alone does not pass a test. Atomic methods
remain manual or assisted.

For these three controls, `atomic_results` links each `rule_id`/`target` pair to
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
HTTP/HTML interpretation, intent or exemptions. Bundled method cases have authored
reference verdicts, not an automatic SEO engine. No C extends to unselected
controls, an entire site or actual indexing. See [migration and cases](migration-draft.2.md).

## Evidence bundle

Keep the report and evidence together. Each artifact declares ID, relative POSIX
path, SHA-256, kind, target IDs, observation time with timezone, and a description.
Declare access as `public`, `restricted` or `synthetic`. TSEP-1 requires public
evidence except declared intent; TSEP-2 additionally accepts restricted Search
Console evidence. An assessor still has to document its actual origin. Synthetic
data is explicitly marked in gate output. This draft refuses a fully automatic C
because none of its complete control methods has an automated implementation.
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

## Versions and implementation claims

Pin both version and protocol SHA-256. Cite IDs as
`TSEP@0.1.0-draft.2:TS01`. Never silently replace a released artifact. Changes to
applicability, expectations, required evidence or decisions require a new version
and migration note. TS01–TS44 are permanent identities, not reusable slots.

This candidate has one implementation of report validation. Passing its tests
allows the narrow statement “passes the bundled report-interchange tests for
0.1.0-draft.2.” It does not establish implementation of all 44 assessment methods.
An implementation must publish per-rule mapping and limitations before making a
broader claim. No compatibility with a third-party tool has yet been demonstrated.
