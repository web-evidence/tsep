# Technical SEO Evidence Protocol — TSEP

**0.1.0-draft.2 · working draft · initiated by Edikka · [Français](README.fr.md)**

Make a technical SEO assessment inspectable: named controls, a declared scope,
traceable evidence, explicit unknowns, and a result another practitioner can challenge.
This package is usable independently of Edikka. It is not a certification, an
established standard, a ranking score, or a guarantee of indexation.

## Independent repository

This is the autonomous development repository. See [development and integration boundaries](docs/development.md). Run the complete local verification with `python3 scripts/verify.py`. The import tag preserves the original candidate; later infrastructure work is a development snapshot until separately released.

## Try it in two minutes

Python 3.9+; standard library only. No account, API key, installation or network
collection is needed for the demonstration. From this directory:

```sh
python3 examples/replay.py
python3 tsep.py validate examples/pass/report.json
python3 tsep.py gate examples/fail/report.json
python3 tsep.py earl examples/partial/report.json
python3 -m unittest discover -s tests -v
```

The second command validates the report format and local evidence hashes. It does
not independently validate the auditor's judgment. The failing gate returns exit
code 1 on purpose. Examples are synthetic; they are not observations of Edikka or
any other live site. The successful example covers **TS01 only on one URL**.

Create a report without silently marking anything as passed:

```sh
python3 tsep.py init --profile TSEP-1 \
  --target https://example.com/ \
  --assessor 'Your team' --label 'Homepage sample' \
  --selection-method 'One deliberately selected URL; no site-wide inference' > report.json
```

Every selected control starts as `NT`. Add evidence files and record the assessment
before validation. `--controls TS01,TS07` creates an explicitly custom selection;
it cannot be combined with a named profile. The CLI does not fetch the target.

## Read or implement the contract

- [Report contract and decision rules](docs/contract.en.md)
- [44 controls, generated from the bilingual source](docs/controls.en.md)
- [Canonical source](spec/protocol.json) and [JSON Schema](schemas/report.schema.json)
- [EARL mapping and ACT relationship](docs/interoperability.md)
- [Governance, conflicts and contributions](GOVERNANCE.md)
- [Contribution requirements](CONTRIBUTING.md), [change history](CHANGELOG.md)
- [Acceptance-clause template, EN/FR](docs/acceptance-clause.md)
- [Licensing and attribution](LICENSE.md)
- [Bounded HTTP probe and its 48 historical regression cases](probes/README.md)

TS01, TS07 and TS10 now have nine atomic rules with evidence requirements and
synthetic FR/EN cases. Report format 2 requires coverage per target before C on
these controls. See [migration from draft.1](docs/migration-draft.2.md) and
[method cases](tests/fixtures/control-cases.json). Case verdicts are authored;
tests verify aggregation, not an automatic SEO engine.

The normative package is the versioned JSON, report contract and schema together.
An inconsistency is a defect to report, not permission to select the easiest rule.
The original Edikka grid 1.1 is preserved byte-for-byte in `upstream/` for provenance.
It remains a separate historical publication. TSEP has its own version sequence.

## Evidence profiles

| Draft profile | Controls | Evidence access |
| --- | ---: | --- |
| TSEP-1 | 27 | Public observations plus a declared audit context |
| TSEP-2 | 29 | TSEP-1 plus Google Search Console |
| TSEP-3 | 44 | TSEP-2 plus logs, configuration, inventories and change/CI records |

These profiles describe access, not increasing quality or confidence. Public data
does not imply complete automation. Declared context supplies expected behavior;
it does not prove that behavior. The exact versioned ID lists are in `protocol.json`.
Google-specific controls are not satisfied by a Bing report. Bing can supply
additional evidence; this draft has no separate normative Bing control set.

## What the implementation proves

The CLI checks report shape, scope consistency, evidence references, required input
coverage, local SHA-256 hashes, and conservative gate decisions. The test suite
checks this **report interchange implementation**, not 44 SEO test algorithms.
It rejects unsupported claims and exposes unselected controls. It cannot prove
that a screenshot is truthful or that a human judgment is sound. SHA-256 provides
integrity, not identity, trusted time or authenticity.

The human-assisted assessment methods are not yet backed by an independently
reviewed per-control fixture suite. No external adopter, reviewer, maintainer,
public repository or DOI is claimed. The working name has not undergone legal
clearance. No metrics about llms.txt adoption underpin this design.

## Reuse and cite

Use the identifiers in tools and procurement: `TSEP@0.1.0-draft.2:TS07`. Preserve
the version, actual evaluated scope, result and evidence reference. A crawler
alert can map to part of a control without claiming the entire control passed.

Suggested citation: *Edikka. Technical SEO Evidence Protocol (TSEP),
0.1.0-draft.2, 2026-10-09. Working draft.* Include the release archive hash when
sharing this unpublished candidate. No DOI should be invented.

Text/data are CC BY 4.0; original software is Apache-2.0. Attribution belongs in
documentation or citation metadata; TSEP adds no promotional backlink condition.

To build a deterministic standalone archive outside this directory:

```sh
python3 maintain.py check
python3 maintain.py build --output /tmp/tsep-0.1.0-draft.2.zip
```
