# Google Search Central source capture — TS03

- URL requested: https://developers.google.com/search/docs/crawling-indexing/http-network-errors
- Redirected URL observed: https://developers.google.com/crawling/docs/troubleshooting/http-status-codes
- Retrieved: 2026-10-17 UTC
- Page states last updated: 2026-02-04 UTC
- Scope: official Google documentation on the effect of HTTP status classes on Google's crawlers; no site-specific data.
- Relevant reading, paraphrased: 2xx responses may be considered for processing; a 2xx page whose supplied content appears erroneous can be reported as a soft 404; 4xx and 5xx responses have distinct processing effects; a 2xx alone does not guarantee indexing.
- TSEP use: supports the limitation that this candidate does not implement Google's soft-404 classification. The synthetic rule compares a supplied route plan, response status and literal body markers only.
- Capture limitation: dated text summary of the official page, not a full-page archival copy. No private or customer data included.
