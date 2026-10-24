# Migration — TSEP 0.1.0-draft.45

## Change

Draft.45 adds one versioned atomic rule, TS05-A01, for a supplied policy map
that separates crawling, indexing and access protection. It updates the protocol
version and the version field for all current atomic rules while retaining their
identifiers and decision semantics. TS01–TS44 remain present.

The native offline interpreter advances from 43 to 44 and adds one rule:
26 controls / 65 executable rules. Four authored synthetic TS05 cases add four
rule-target pairs to the existing corpus (1498 cases / 3123 pairs). The method
fixture corpus adds four cases. The report JSON schema pins draft.45. No historical
report, tag, demonstration copy or prior archive is replaced.

## Reader and conservative outcomes

conformance/ts05_indexing.py compares supplied configuration and prior
intent.ts05_policy records only. It never fetches a live site or observes Search
results. A Disallow-only deindexing guarantee and robots-only confidentiality
claim fail; hidden noindex and unknown methods remain inconclusive. A noindex
directive or removal request does not prove actual index change. Positive NA
requires a dated, complete inventory review. A pass establishes only consistency
of the supplied policy map, not deployment, crawler access, indexing or privacy.

## Migration guidance

Existing reports remain valid for their recorded protocol version and hash.
New TS05 assessments must use TSEP@0.1.0-draft.45:TS05-A01, attach both
configuration and intent evidence to each target, and record the dated policy
map, separate mechanisms, visibility assumption and claim bases. Reviewers must
retain unsupported, missing, future-dated and inaccessible-directive states as
inconclusive. Do not convert missing input to NA or reuse a TS05 result as proof of
whole-site compliance.

## Verification status and limits

Targeted native tests and full candidate qualification are reported separately.
Application import/reception, downloaded export, archive reconstruction and replay
outside the application remain separate required checks. The synthetic cases do
not assess a real site, current index state, identity, crawl, ranking, adoption or
certification.
