# TS01 implementation pilot

**Pilot plan 1 · prepared 9 October 2026 · recruitment not started** · [Français](pilot-ts01.fr.md)

Can a developer outside Edikka implement TS01 from the public material and produce
results another person can replay? This small pilot tests that question. It does
not assess adoption, all 44 controls, a whole website or readiness for TSEP 1.0.
Edikka initiated TSEP and benefits commercially from its reputation; see
[governance](../GOVERNANCE.md). AI-assisted reviews are not independent human review.

## Freeze the reference

Use protocol **0.1.0-draft.7**, report format 2, rules **TS01-A01 and TS01-A02**.
The technical baseline is commit
`824c48b19abe15f76f9a9058718cff461a7dbabb`; its development archive SHA-256 is
`8164b70b08aa200ab0c45f905e0079dd2bfd9ba22e6a1f9428e2c1a840f11de0`.
The normative protocol SHA-256 is
`c7666df08e752400a588963e8781b6441e05b634c62289a607c04f807a5604da`.
The pilot kit is a later documentary addition, not a change to these rules or
their corpus. A package including it has a different archive hash: record the
exact package commit, archive hash and version DOI in the activation record.
The [baseline manifest](pilot-ts01-baseline.sha256) pins 72 unchanged files
from that technical baseline, including every tool, contract, schema and corpus.
README, changelog, distribution inventory and citation metadata are documentary
exceptions; they are not used to interpret rules or decide outcomes.
From the extracted package root, without Git:

```sh
shasum -a 256 -c docs/pilot-ts01-baseline.sha256
```

On Linux, `sha256sum -c docs/pilot-ts01-baseline.sha256` is equivalent. Also check
the complete package with `shasum -a 256 -c SHA256SUMS`.
`package_archive_sha256` identifies the ZIP built by `maintain.py` from the package
commit. The planned manual Zenodo deposit uploads that exact ZIP, not an automatic
GitHub source archive. Record its deposited filename and downloaded SHA-256 as
`zenodo_archive_filename` / `zenodo_archive_sha256`; they must identify the same bytes.
For example: `shasum -a 256 /path/to/downloaded-package.zip`. The separate receipt
and logs are not part of that ZIP. A DOI alone does not establish this equality.

Read the [contract](contract.en.md), [conformance format and limits](conformance.md)
and [report workflow](cli.md). TS01-A01 checks a final **200**. TS01-A02 checks
identity against prior intent, in the order specified by the contract. In particular,
prior `representation: "stable"` makes any changed body digest fail, even if only
a timestamp changed. These summaries are informative; the contract and
`spec/protocol.json` take precedence. Disclosure, original implementation, own
captures, public deliverables, human replay and deadlines below are pilot-specific
requirements, not additional protocol requirements.
Keep the normative text, executable baseline and expected corpus frozen throughout
the run. Record ambiguities publicly; a changed normative interpretation requires
a new protocol version and a separately identified pilot, never revised old results.

## Activate before implementation

Copy [the activation template](pilot-ts01-registration.json) to a new versioned
file; never replace the shipped template. The copy moves through
`template-not-activated` → `activated` → `concluded`. Before implementation, fill
all fields under `activation`, agree the dates and commit the accepted plan. Record
its immutable commit URL and public publication/CI event outside that same commit
to avoid a self-reference. Issues may link to it, but an editable issue alone is
not the frozen plan. The unfilled template is **not** an activated or preregistered
study. Keep `conclusion` empty until observed outcomes are published. A local date,
Git author date or checksum alone is not independent timestamp evidence.

The proposed window is 30 calendar days from agreed start, followed by 14 days
to publish the result. The steward (Edikka) and the participant confirm dates before starting;
no start, appointment, remuneration or recruitment is implied by this document.
Declare separately the participant’s and reviewer’s relationships with Edikka
over the preceding 12 months and during the pilot, their funding/compensation,
the reviewer’s relationship with the participant, and AI assistance. Obtain each
person’s consent to publish their name, affiliation and disclosed relationships. A paid external implementation is identified as commissioned,
not spontaneous adoption. Never claim independence solely from a different name.

The participant writes their own interpretation of the two rules; wrapping or
copying `conformance/evaluate.py` or `adapters/captures.py` is not a second
implementation; neither is a line-by-line port into another language. Declare
prior exposure to reference interpretation code and planned consultation: `never`,
`after-first-version` or `throughout`. For consultation after a first version, retain
that version’s commit/hash before reading the reference. Log actual consultation
and repeat this declaration in the final conclusion; reading the reference is a
limitation when interpreting what the pilot proves about the written specification.
Reuse of the report validator, comparison runner and exporter is
allowed and disclosed. Record dependencies, reused code and assistance. Use the
public documentation; log technical help in public issues before relying on it.
Never publish credentials or private data there; sanitize the question and record
any private technical help without exposing its sensitive content.

## Execute and retain

Python 3.9+ runs the reference tools. An external adapter reads one input JSON
object on stdin and writes only its result array on stdout; diagnostics go to stderr.
From the frozen package root, replace the adapter path with the participant's code:

```sh
python3 conformance/run.py --rules TS01-A01,TS01-A02 \
  --command 'python3 /path/to/participant_adapter.py' > conformance-result.json
```

Run every selected case from the unchanged corpus. The runner validates the full
corpus and selects the TS01 pairs; do not edit `expected`, omit targets or suppress
extra results. Publish exit code, exact command, environment, adapter version/hash,
agreements, disagreements and reduced coverage **per rule**. Only explicitly
marked reference-limit pairs may accept inconclusive instead of their conclusive
expectation; such pairs never count as successful assessments. The corpus includes
pass, fail and inconclusive for both rules.

Produce at least one report from the participant's **own captures**, not bundled
examples. Record prior intent, request conditions, every HTTP hop, complete bodies,
tool/version, timestamps and limitations. Use owned or expressly authorized public
test resources; keep the collection small. Do not use production secrets or personal
data. Declare controlled fixtures as such. Preserve raw records and explain any
conversion to the bounded input format. A reference body/markers must precede the
assessment; do not invent intent after seeing the result. Source-text markers do
not establish rendered visibility, indexing or ranking.

The participant's own interpreter supplies the atomic results. Create a `custom`
TS01-only report through [init → add-evidence → record](cli.md), or their own
exporter. Attribute genuinely automatic results using
`init --mode automatic --tool NAME --tool-version VERSION` with the participant’s
interpreter identity and the other required arguments; record its source hash too.
Manual changes remain declared as such, never relabeled automatic. Then run:

```sh
python3 tsep.py validate /path/to/bundle/report.json
python3 tsep.py gate /path/to/bundle/report.json > gate.json
python3 tsep.py gate /path/to/bundle/report.json --summary
python3 tsep.py earl /path/to/bundle/report.json > earl.jsonld
```

Keep every exit code. `validate` 0 means a valid report; `gate` 1 can correctly
mean NO_GO. Gate 0 means GO_WITH_RESERVATIONS **within the declared scope**.
Gate 2 means INCOMPLETE/REVIEW; 64 means invalid data (malformed command syntax
can also exit 2: inspect the message). An NC or NT is not a pilot failure if it
correctly represents the evidence.
Each report retains both rules and all its targets, unknowns and contradictions.
Automatic C additionally needs full evidence and declared tool name/version.

## Decide from evidence

The pilot succeeds only when **all** conditions below are evidenced:

1. **P01 — Plan and attribution.** The activated plan and disclosure requirements were respected; the external
   interpretation is attributable and available for review.
2. **P02 — Conformance.** The full TS01 conformance run has zero disagreements. Accepted reduced coverage
   is reported separately; neither rule is supported only by inconclusive results.
3. **P03 — Own evidence.** At least one own-capture report validates, its rule results are supported by
   the captures and prior intent, and gate/EARL preserve those results and scope.
   The own-capture set establishes at least one conclusive result for each rule.
4. **P04 — Human replay.** A named human outside Edikka, different from the implementer, replays the
   frozen inputs and obtains the same atomic outcomes, control status and gate
   decision. Report dates or JSON formatting need not be byte-identical. The
   reviewer checks evidence relevance, not only successful command exits.
5. **P05 — Public minimum and review access.** Publish the adapter source,
   conformance output, report, gate and EARL. Required captures and prior intent
   are available to the reviewer; any restricted captures have a documented reason.
   A public summary explains the resulting limits on public replay. Do not expose
   sensitive data to meet this criterion; an unmet public minimum prevents success.
6. **P06 — Published conclusion.** Publish the signed human conclusion, elapsed
   effort, ambiguities, interventions, reference-code consultation, limitations and
   negative findings by the agreed deadline. These P01–P06 IDs match the JSON plan.

Use `success`, `failure` or `unfinished` for the **pilot** conclusion, separate
from TSEP outcomes. A persistent mismatch, unsupported success claim, unreproducible
result or undisclosed technical help prevents success. Withdrawal, absent reviewer
or missed deadline is `unfinished`, never success; retain the reason and any
partial technical findings. Separately attribute any technical failure to the
participant, the reference or an undetermined cause, with evidence; a wrong corpus
expectation must not be blamed on the implementer. The frozen run still retains
its disagreement. Publish the result, including negative findings, by
the agreed deadline. Later corrections are dated additions, not replacements.

Use the [implementation report](../.github/ISSUE_TEMPLATE/pilot-implementation.md)
and [ambiguity report](../.github/ISSUE_TEMPLATE/pilot-ambiguity.md) templates.
Human review of the contract can proceed alongside implementation; review of
the final report follows its production. No reviewer is appointed by this kit.

## Twelve-month indicators

Separate proposal for owner decision: count evidenced external implementations,
distinct substantive external contributors, distinct third-party specifications
citing TSEP, and independent published citations. Exclude Edikka's own outputs,
duplicates, stars and downloads as adoption evidence. Record missing evidence as
unknown, not zero. Fix definitions, baseline, start date and twelve-month review
date publicly before measuring; no numerical targets or scheduled monitoring are
adopted here. The unresolved twelve-month targets do not change pilot criteria.
