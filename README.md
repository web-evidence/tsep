# TSEP — evidence interchange format

**Technical SEO Evidence Protocol · 0.1.0-draft.7 · initiated by Edikka · [Français](README.fr.md)**

Share a technical SEO assessment that its recipient can inspect, replay and
challenge: stable identifiers, explicit scope, evidence linked to findings and
unknowns retained. The report distinguishes established findings from remaining checks.

## Who it is for

SEO and development teams preparing acceptance checks, clients reviewing audit
evidence, and tool authors exporting observations in a common format without
turning partial coverage into global conformity.

## Actual output

A `report.json`, evidence files with SHA-256, a decision restricted to declared
controls/targets and an EARL JSON-LD companion. Controls use C, NC, NA or NT;
atomic rules use pass, fail, not-applicable or inconclusive.

**TS01–TS44 are the permanent identifiers inherited from grid 1.1.** TSEP has a
separate version sequence; the original FR/EN sources and provenance remain intact.
Nine rules specify TS01, TS07 and TS10, with a bounded interpreter over raw inputs:
TS01-A01/A02, TS07-A01/A02/A03 and TS10-A01 through A04. TS10-A02 content comparison
remains a supplied human review bound to the captures.

## Try it in two minutes

Python 3.9+, standard library only; synthetic examples, no account or network
collection. From the repository root:

```sh
python3 tsep.py validate examples/pass/report.json
python3 tsep.py gate examples/pass/report.json --summary
python3 tsep.py gate examples/fail/report.json --summary
python3 conformance/run.py
python3 tsep.py earl examples/partial/report.json
```

The passing case displays `GO_WITH_RESERVATIONS`, `C=1` and **1 control out of 44,
one target, synthetic evidence**. The failing case deliberately exits 1. Report
validation establishes consistency and file integrity.

## Implement TSEP

1. **Emit a report**: pin protocol version and hash, declare targets, selection and
   tool. `init` starts at NT; `add-evidence` computes SHA-256 and records kind,
   targets and date; `record` adds the reasoned control result and atomic observations.
   See the [complete CLI workflow](docs/cli.md). Supplied structured captures can
   also produce a [report, evidence and EARL bundle](docs/capture-adapter.md)
   directly, with computed results and explicit coverage.
2. **Declare partial coverage**: select a `custom` list, keep unknowns as
   NT/inconclusive and link each artifact to its target. Selecting TS01/TS07 does
   not satisfy a named profile. An isolated test cannot pass its parent control.
3. **Pass the conformance suite**: supply a JSON stdin/stdout adapter, then run
   `python3 conformance/run.py --rules TS01-A01,TS01-A02 --command 'python3 my_adapter.py'`
   for that subset, or omit `--rules` for all nine rules. State “passes TSEP
   0.1.0-draft.7 conformance for TS01-A01, TS01-A02” with the bounds actually supported.
   [Input format and comparison](docs/conformance.md). Report exact agreements,
   disagreements and reduced coverage separately; accepted inconclusive results
   on marked reference limits are not successful assessments.

Automatic C requires every control rule `automatic`, complete coverage and
`assessor.tool.name/version`. TS01-A01/A02 are automatic: final 200 and resource identity against prior intent (URL, body digest,
declared stability or literal identity markers in extracted source text). Passing
a changed body through markers requires at least one satisfied required marker;
comments and script/style are excluded. TS07-A01/A02/A03 remain semiAuto; TS10-A02 remains manual.
Defining an appropriate content reference remains a human responsibility.

## Evidence profiles

| Profile | Controls | Evidence type |
| --- | ---: | --- |
| TSEP-1 | 27 | Public observations and declared context |
| TSEP-2 | 29 | TSEP-1 and the target engine’s webmaster tools; Google is the first normative series |
| TSEP-3 | 44 | TSEP-2, logs, configuration, inventories, history and CI |

Profiles describe required evidence, not a quality level. `webmaster-tools`
evidence declares its `engine`; another engine's evidence does not validate the
Google series. Exact control lists are versioned in the JSON.

## Status and path to 1.0

**Status on 9 October 2026: development candidate in a public repository;
local verification and remote CI observed, no established independent practitioner review.**

TSEP is hosted in [web-evidence/tsep](https://github.com/web-evidence/tsep), under
[Web Evidence](https://github.com/web-evidence). It was initiated by Edikka, which
remains its steward. The [first CI run](https://github.com/web-evidence/tsep/actions/runs/37962185984)
passed all seven jobs on commit `253b0a1`: Linux/Python 3.9–3.14 and macOS/Python 3.14.
The repository, issues, pull requests and CI are publicly readable. See the
[dated results and scope](docs/development.md#first-observed-ci-run) before applying
this result to another revision.
For a later revision, inspect its commit and result in the
[verification workflow](https://github.com/web-evidence/tsep/actions/workflows/verify.yml).

| Stage | Success criterion before 1.0 |
| --- | --- |
| Stabilize methods | Applicability, evidence, limits and contradictory cases for every rule; verified FR/EN parity |
| Establish interoperability | At least one external implementation passes a declared suite coverage; differences documented |
| Organize review | Documented independent review and two identified independent co-maintainers under the governance rules |
| Freeze a version | Normative disagreements resolved or explicitly excluded, migration documented, reproducible archives and observed CI on the announced matrix |

These are cumulative requirements for 1.0, not a publication schedule. The observed
CI run addresses part of the last criterion. All other criteria remain open,
including external implementation and independent review.

## Limits

TSEP is a proposed format, not a certification or recognized standard. The validator
checks declarations and hashes, not authenticity, appropriate intent or every
assessment judgment. A hash does not establish authorship or actual collection
time. Bundled cases are synthetic.

The interpreter covers nine rules within a documented subset; unsupported inputs
remain inconclusive. TS07-A03 compares supplied source/DOM captures without executing JavaScript;
the plan and exemptions require review. TS10 compares declared family signals and checks the binding of the supplied
human content review, without guaranteeing its correctness.
A partial check never produces global conformity. No result guarantees indexing,
ranking or future engine behavior.

[EN contract](docs/contract.en.md) · [44 controls](docs/controls.en.md) ·
[Bilingual source](spec/protocol.json) · [Schema](schemas/report.schema.json) ·
[Draft.7 migration](docs/migration-draft.7.md) · [EARL](docs/interoperability.md) ·
[Governance](GOVERNANCE.md) · [Contribute](CONTRIBUTING.md) · [History](CHANGELOG.md) ·
[Acceptance clause](docs/acceptance-clause.md) · [HTTP probe](probes/README.md).

Cite `TSEP@0.1.0-draft.7:TS07` with scope, result, evidence and archive hash.
Text/data CC BY 4.0, code Apache-2.0: [licenses](LICENSE.md), [citation](CITATION.cff).
[Development, full verification and independent repository](docs/development.md).
