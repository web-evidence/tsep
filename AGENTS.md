# TSEP — contributor instructions

This repository is the independent development source for Technical SEO Evidence
Protocol. Integrations are separate consumers, not runtime dependencies.

## Preparation and scope

- Read `docs/development.md`, the relevant contract and `git status --short`
  before editing. Preserve pre-existing changes.
- Use descriptive branches in the form `<type>/<short-description>`, where type
  is `feat`, `fix`, `docs`, `test` or `chore`. Integrate changes sequentially after
  verification.
- Stay within the requested scope. Changing another repository, publishing,
  buying a domain, registering a DOI or contacting a third party requires
  authorization for that action. Never claim access or approval not obtained.

## Contracts and results

- Preserve TS01–TS44, their versions and provenance. Never present this candidate
  as a certification or a recognized standard.
- A new rule specifies applicability, inputs, expectations, evidence, assumptions,
  inconclusive outcomes and limitations. Distinguish controls, atomic tests and
  observations.
- Missing evidence does not become C or NA. A partial probe cannot establish
  whole-control or global conformity. Do not infer indexing, ranking or adoption.
- Every normative change requires French and English updates, a distinct version,
  explicit migration guidance and contradictory cases. Never replace a published
  artifact or an existing tag.
- Keep synthetic captures and reports labeled as synthetic. Claims about named
  reviewers, contributors, adopters or numerical results require evidence.

## Sources, generated files and delivery

- The bilingual source is `spec/protocol.json`. The report contracts are
  `docs/contract.*.md` and the JSON schema. `docs/controls.*.md` and examples are
  controlled derivatives.
- `maintain.py render` rewrites normative fingerprints and generated pages;
  `examples/replay.py` rewrites examples unless given an explicit `--output-dir`.
  Do not run them to hide a failure without examining the diff.
- Run `python3 scripts/verify.py`. It works in temporary directories and rejects
  source changes. Its HTTP probe cases use a server on 127.0.0.1, without external
  collection.
- Add distributed files explicitly to `release-files.json`. Do not build an
  archive by recursively including the entire repository.
- Check archive reconstruction, Git status and diffs before integration.
  A prepared CI workflow is not evidence of an observed remote run.
- For each new third-party observation, retain its URL, date, scope and a dated
  capture with a fingerprint, or a documented reason why no capture is available.
  Keep delivered tools independent of any contributor's private infrastructure.
- Record observed results and limitations, including failures. Verification
  evidence must not imply a broader assessment than was actually performed.
