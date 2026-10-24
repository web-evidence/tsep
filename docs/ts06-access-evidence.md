# TS06-A01 — Synthetic sensitive-route access matrix / Matrice synthétique d’accès aux routes sensibles

Status: candidate draft 0.1.0-draft.46. This is a mechanism qualification over authored `.invalid` fixtures, not a site assessment or certification. Claude’s review supplied method suggestions only; Claude did not run or verify these tests.

## Scope and inputs

The atomic rule accepts only a prior `intent.ts06_access` plan, a matching `configuration.ts06_access.plan_sha256`, and a supplied HTTP matrix. The plan declares a bounded set of synthetic `.invalid` route labels, canaries, fictional roles, every route/role test, allowed same-origin login paths, and one cold/authorized-seed/anonymous-replay triplet per route. The native reader accepts HTTP GET traces only, with exactly `Host`, a fixed fixture user-agent, and `X-TSEP-Synthetic-Role`. It never resolves the host or opens a socket.

## Procedure and outcomes

1. Bind the prior intent plan to configuration by its compact sorted-JSON SHA-256 and require its timestamp to precede the observations.
2. Require complete coverage of every declared route by every synthetic unauthorized role, and exactly one ordered cold anonymous → authorized synthetic seed → anonymous replay sequence per route. A cache identifier is a label only.
3. Inspect supplied raw responses for declared canaries in response headers and body, including the implemented literal, HTML/percent/JSON/hex, and bounded Base64/URL-safe Base64 forms. Preserve an attributable leak as `fail` before reporting duplicate or missing matrix cells.
4. Treat 401/403 as denial; a login redirect is accepted only through the route’s declared path allowlist and same origin. A 404 is accepted only when explicitly declared in the plan. A successful 2xx to an unauthorized role or any attributable canary leak is `fail`.
5. Return `pass` only for the complete supplied synthetic matrix and ordered triplets without an unauthorized canary. Partial 206, 304 without a full retained representation, unsupported content coding, missing/ambiguous cells, incomplete attribution, and cross-origin redirects are `inconclusive`. Whole-control `NA` requires a complete, dated, positive synthetic inventory with no sensitive routes and no tests/triplets.

## Contradictory cases

The frozen extension `tests/fixtures/ts06-access-cases.json` contains 23 authored cases: safe complete matrix, canary in an error body or response header, successful public representation, cache-replay leak, preserved leak despite a duplicate trace, explicit versus undeclared 404, base64url offset, forbidden API-key request header, cross-origin login, unsupported Brotli coding, reordered cache triplet, observation outside the plan window, query-bearing credential URL, live-host label, missing role/matrix evidence, partial 206, conditional 304, future plan, positive synthetic NA, and same-origin declared login redirect. Exact expected outcomes are checked against the native reader and in-process evaluation; no fixture is a remote observation.

## Limits and migration

This mechanism does not establish actual identity, authentication, authorization, shared-cache behavior, route coverage, confidentiality, TLS behavior, JavaScript behavior, crawler access, index state, or whole-site protection. Synthetic role headers and cache labels are not credentials or server attestations. `Age`/`X-Cache` alone are not evidence of a replay relationship. URL aliases, query strings, HEAD, live domains, and unsupported encodings remain outside this reader. A native capture adapter for a real authorized environment would require a separate reviewed design, strict scope controls and a future migration; this draft does not authorize a live crawl. See [migration draft.46](migration-draft.46.md) and [dated RFC source capture](source-captures/rfc-ts06-access-2026-10-17.md).
