# Dated source capture — TS06 HTTP/access semantics

Captured/reviewed: 2026-10-17 (UTC). Scope: selected semantic statements used to bound a synthetic test rule; no site or product was observed. Source documents remain authoritative at the URLs below.

- [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html), §§10.2.2, 15.3.7, 15.4.5, 15.5.2, 15.5.4–15.5.5: Location identifies a redirect target; 206 is partial content; 304 relies on a stored representation; 401 concerns missing valid authentication credentials; 403 denies the request; a server may use 404 to conceal a forbidden resource. These HTTP meanings do not by themselves prove confidentiality or correct application authorization.
- [RFC 9111](https://www.rfc-editor.org/rfc/rfc9111.html), §§3.4–3.5, 4.1, 4.3.4: partial content and authenticated-request storage have specific cache requirements; `Vary` participates in cache matching; 304 validation updates a suitable stored response. A repeated response or a textual `Age`/`X-Cache` field alone does not attribute a cache hit in these fixtures.
- [RFC 6454](https://www.rfc-editor.org/rfc/rfc6454.html), §3.2: an origin is based on scheme, host and port. This supports the same-origin boundary; it does not establish that a redirect is safe.
- [RFC 6761](https://www.rfc-editor.org/rfc/rfc6761.html), §6.4: `.invalid` is a special-use name reserved for invalid names. The implementation treats it only as an authored fixture label and performs no resolution or connection.

The rule’s route matrix, synthetic identity labels, canary matching, outcomes, completeness and limitations are editorial TSEP choices, not requirements asserted by these RFCs. Retrieved text was summarized, not copied.
