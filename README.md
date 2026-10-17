[TS25 — présence critique fournie / supplied critical presence](docs/critical-presence-evidence.md), [draft.44 migration](docs/migration-draft.44.md).

[TS24 — rôle x-default fourni / supplied x-default role](docs/xdefault-role-evidence.md), [draft.41 migration](docs/migration-draft.41.md).

[TS23 — hreflang fourni / supplied hreflang](docs/hreflang-reciprocity-evidence.md), [draft.39 migration](docs/migration-draft.39.md).

[TS18 — graphe et inventaires fournis / supplied graph and inventories](docs/graph-reconciliation-evidence.md), [draft.38 migration](docs/migration-draft.38.md).

[TS16 — liens entrants fournis / supplied incoming links](docs/incoming-links-evidence.md), [draft.37 migration](docs/migration-draft.37.md).

[TS17 — liens essentiels fournis / supplied essential links](docs/essential-links-evidence.md), [draft.36 migration](docs/migration-draft.36.md).

[TS15 — fichiers sitemap fournis / supplied sitemap files](docs/sitemap-files-evidence.md), [draft.35 migration](docs/migration-draft.35.md).

[TS33 — validation layers / couches de validation](docs/structured-validation-evidence.md), [draft.34 migration](docs/migration-draft.34.md).

TS32: [declared JSON-LD identity corpus](docs/structured-identity-evidence.md), [draft.33 migration](docs/migration-draft.33.md). Supplied corpus coherence and bound reviews; no temporal stability claim.
TS31: [JSON-LD/content evidence](docs/structured-content-evidence.md), [draft.32 migration](docs/migration-draft.32.md). Supplied graph-bound reviews; no authenticated visibility or rich-result guarantee.

TS36: [release follow-up](docs/release-monitoring.md), [intake and closure](docs/release-monitoring-intake.md), [draft.31 migration](docs/migration-draft.31.md). Authored cases only; no real future stage completed.

**RC1: 0.2.0-rc.1** — all TS01–TS44 retained; 28 controls /67 executable atomic rules. TS03 uses synthetic .invalid captures only. [Current 44-control matrix](docs/control-implementation-status.md), [TS03 evidence](docs/ts03-response-evidence.md), [migration](docs/migration-0.2.0-rc.1.md), [application integration dossier](docs/app-integration-roadmap.en.md). No real-site use is verified by this prerelease.

TS08 [native inspections](docs/inspection-evidence.md) and [acquisition](docs/search-console-acquisition.md) remain available.

Optional TS31–33 preparation: [supplied rendered states and source/DOM comparison](docs/jsonld-rendered-observation.md), without browser collection or control outcomes. October12 priority: TS08 then TS12, qualification before the application; TS36 is now available; TS31–33 follow.

Preparing TS31–33: [offline JSON-LD processing](docs/jsonld-processing.md), then [attributed HTML extraction and combined scripts](docs/jsonld-html-observation.md). Frozen contradictory cases and exact replay; effective bases, visible facts and validators remain to qualify. These components add no TS31–33 rules.

The [TS39 laboratory](docs/delivery-laboratory.md) adds eight prefrozen experiments, 38 actual local origin/cache HTTP exchanges, repair with purge and offline replay; pages and reviews remain fictional.

TS39 has [three delivery rules](docs/delivery-evidence.md): prior matrix, per-context signals and cache attribution, with bound reviews and explicit unknowns.
[Current versions and remaining evidence / Versions et preuves manquantes](docs/control-implementation-status.md).

# TSEP — evidence interchange format

**Technical SEO Evidence Protocol · 0.2.0-rc.1 · initiated by Edikka · [Français](README.fr.md)**

Share a technical SEO assessment that its recipient can inspect, replay and
challenge: stable identifiers, explicit scope, evidence linked to findings and
unknowns retained. The report distinguishes established findings from remaining checks.

For TS02, the [prior owner-plan workflow](docs/redirect-plan-workflow.md) prepares
a readable plan and binds a supplied decision to subsequent captures.
The optional [prospective collector](docs/redirect-collection.md) retains bounded
native HTTP hops after supplied approval, then builds the existing replayable report.
The [Search Console preview](docs/search-console-observations.md) compares supplied
API evidence with replayed technical records, without automatic TS08/TS12 verdicts.
The [delivery variants observer](docs/delivery-variants-observation.md) prepares
TS39 with raw HTTP differences and bounded Vary matching, without control outcomes.

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
Sixty-two atomic rules specify twenty-four controls: TS01, TS02, TS04, TS07, TS08, TS10, TS12, TS15, TS16, TS17, TS18, TS23, TS24, TS31, TS32, TS33, TS34, TS35, TS36, TS39, TS41, TS42, TS43 and TS44, with bounded interpreters over supplied evidence. TS10-A02 content comparison
remains a supplied human review bound to the captures.

Performance imports keep field p75/classes (CrUX) separate from laboratory diagnostics
(Lighthouse series). Decisions and hypotheses must be supplied; missing reviews stay
unknown. See the [performance method and limitations](docs/performance-evidence.md).

The [TS44 laboratory](docs/critical-content-laboratory.md) compares four variants over six actual local HTTP exchanges, with explicitly authored DOM and reviews.

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
   The [standalone HTML report](docs/html-report.md) exposes evidence offline and
   compares retained assessments. The [guided TS01 workflow](docs/guided-capture.md)
   captures raw bytes, freezes criteria before measurement and replays offline;
   interpreter 5 provides a [TS01 source-text extractor](docs/source-text-v5.md)
   separate from TS07, with frozen counterexamples and explicit limits.
   Collector 8 preflights reference markers; its [parsed guided profile](docs/guided-parsed-markers.md)
   refuses any complete contradictory hypothesis and requires Node 24 during preparation.
   Adapter 28 retains evidence; HTML 11 displays preflight. A separate [coverage
   diagnostic](docs/reference-diagnostics.md) inventories candidate limitations
   without issuing verdicts. The [paired capture diagnostic](docs/diagnostic-campaign.md)
   compares registered phases and exposes extraction limits on changed bodies.
   Draft.28 adds a distinct optional [parsed HTML marker profile](docs/source-markers.md).
   The earlier lexical [TS01 noscript proposal](docs/proposals/noscript-consensus.md) remains unapplied.
2. **Declare partial coverage**: select a `custom` list, keep unknowns as
   NT/inconclusive and link each artifact to its target. Selecting TS01/TS07 does
   not satisfy a named profile. An isolated test cannot pass its parent control.
3. **Pass the conformance suite**: supply a JSON stdin/stdout adapter, then run
   `python3 conformance/run.py --rules TS01-A01,TS01-A02 --command 'python3 my_adapter.py'`
   for that subset, or omit `--rules` for all sixty-seven rules. State “passes TSEP
   0.2.0-rc.1 conformance for TS01-A01, TS01-A02” with the bounds actually supported.
   [Input format and comparison](docs/conformance.md). Report exact agreements,
   disagreements and reduced coverage separately; accepted inconclusive results
   on marked reference limits are not successful assessments.

Automatic C requires every control rule `automatic`, complete coverage and
`assessor.tool.name/version`. TS01-A01/A02 are automatic: final 200 and resource identity against prior intent (URL, body digest,
declared stability or literal identity markers in extracted source text). Passing
a changed body through markers requires at least one satisfied required marker;
comments and script/style are excluded. TS07-A01/A02/A03 remain semiAuto; TS10-A02 remains manual.
Defining an appropriate content reference remains a human responsibility.

For a first external implementation, use the [TS01 pilot kit](docs/pilot-ts01.en.md):
frozen technical baseline, prior criteria, own captures and human replay.
The kit is available for preparation; recruitment and the pilot have not started.

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

The interpreter covers sixty-seven rules within a documented subset; unsupported inputs
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

Cite `TSEP@0.2.0-rc.1:TS07` with scope, result, evidence and archive hash.
Text/data CC BY 4.0, code Apache-2.0: [licenses](LICENSE.md), [citation](CITATION.cff).
[Development, full verification and independent repository](docs/development.md).

[TS02 HTTP trajectories / Trajectoires HTTP](docs/redirects.md) · [Draft.8 migration](docs/migration-draft.8.md)

[TS04 / shared robots](docs/robots.md) · [Draft.9 migration](docs/migration-draft.9.md)

[Structured rendered states / États rendus structurés](docs/structured-rendering.md) · [Draft.10 migration](docs/migration-draft.10.md)

[Same-navigation laboratory / Laboratoire avec navigation attribuée](docs/same-navigation-laboratory.md) · [Draft.11 migration](docs/migration-draft.11.md)

[Canonical attributes / Attributs de canonical](docs/canonical-attribute-coverage.md) · interpreter 11 / adapter 12

[Draft.12 — TS04 client scope / Portée du client TS04](docs/migration-draft.12.md)

[Draft.13 — Known robots fields / Champs robots connus](docs/migration-draft.13.md)

[Draft.14 — Sitemap page locations / URL de pages](docs/migration-draft.14.md)

[Draft.15 — Source directives / Directives source](docs/migration-draft.15.md)

[TS43 controlled loopback laboratory / Laboratoire contrôlé TS43](docs/agent-access-laboratory.md) : six prefrozen scenarios, eight actual local requests, fictional sources/reviews; no provider visit.

TS05 reference: [method and limits](docs/ts05-indexing-evidence.md), [dated source capture](docs/source-captures/ts05-google-search-central-2026-10-16.md).
