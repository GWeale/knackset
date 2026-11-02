# Measured execution records

The 16 older utility workflows have current, scoped offline records. None has
been tested against a live service. The nine field-kit methods remain draft;
their [artifact trials](field-kit-review-20261101.md) are reviewed separately. Keep the individual runs and their limits in view: these are small
trials, not a general success-rate benchmark.

## Creative launch pilot — 2026-11-02 UTC

The [actual-project artifact pilot](../../examples/launch-study/README.md) adds
three matched fresh-context pairs for Rabbit Hole, Reference Remix and Unstick
Project. It has a frozen rubric and independent anonymous artifact review. It
is separate from sandbox execution records and promotion evidence: one pair per
task on one project's launch work cannot establish general gains. Costs and
complete usage/timing telemetry are unknown. The methods remain draft.

## Audit follow-up — 2026-11-01

The [fresh execution record](audit-fixes-2026-11-01.json) contains 14 passing
with-skill trials across eight packages, bound to the current v2 fingerprints.
Each case began in a fresh agent context. Watch setup and its first scheduled
invocation used two phases of one context; the evaluator checked setup before
advancing the fixture clock. Every final reply was reviewed separately from the
state/trace checks. Execution dates are November 2 UTC, November 1 in the audit's
America/Los_Angeles time zone.

The new cases cover chat-only composition, preservation of an existing draft,
UTF-16 ranges, literal spreadsheet input, alert timeout/deduplication, transient
watch setup, and changed travel prices/terms. The six earlier runnable boundaries
were also rerun against the current package contents and corrected graders.
No baseline was run in this wave, so these passes establish scoped behavior,
not improvement over an unassisted agent.

The [description-only routing trial](routing-2026-11-01.json) records 16 selections
before any skill body was supplied. The initial judge accepted 15. Its expectation
for a one-time exact shopping offer was too narrow: `product-shortlist` covers
shopping research, while `web-research` points exact offers elsewhere. The record
retains that initial score and the corrected 16/16 judgment; no agent answer was
changed or rerun. This is not a host-discovery test.

The [clean-PR review](clean-pr-2026-11-01.json) returned no invented findings and
accurately separated supplied checks from tests personally executed. It is a
static decision review, so `github-review` remains `draft`.

The [installation record](host-install-2026-11-01.json) keeps project copy and
host activation evidence separate from these workflow evaluations. The
[20-item resolution](../../docs/audit-resolution.md) maps each audit finding to
its fix and check.

Earlier records below retain their original fingerprints and observed failures.
They are historical; current promotion comes from the v2 follow-up record.

## Calendar and Docs — 2026-11-01

The [boundary record](boundaries-2026-11-01.json) contains five fresh agent runs:
Calendar and Docs with a skill and without one, followed by a Calendar retest.
Every run used its own initialized workspace. The task and tool interface were
provided; raw state, implementation and grading criteria were withheld.

The first Calendar run using the skill saved the right event but skipped reading
the form's date labels before saving. That failed check is retained in the record.
The instruction now says to read the actual field meanings instead of inferring
them from argument names. A fresh run followed that instruction and passed.
The no-skill Calendar run passed on its first attempt. This is a useful correction,
not evidence that the skill outperforms an agent without it.

Both Docs runs prepared the requested local proposal and left the document
unchanged. Their final replies explained that suggestions were unsupported and
did not claim one was saved. The fixture explicitly asks for a local proposal
artifact; repeated identical local proposals are harmless and accepted.

Automated checks cover saved state and action order. The record also includes
the exact final replies and a separate review of their claims. A review of the
grader caught the need for that distinction before these runs began. Package and
fixture hashes identify the instructions and implementation used by each run.

At that revision, Calendar and Docs became `offline-reviewed` for these two cases
only. This historical record did not test scheduling, other Calendar/Docs cases,
or real service behavior.

## First four workflows — 2026-11-01

The [2026-11-01 preview record](preview-2026-11-01.json) contains eight actual
offline fixture executions: four candidate runs and four baselines. Each run used
a fresh evaluator context and its own initialized state. The evaluators received
the task, tool interface and relevant skill where applicable; expected assertions,
grader implementation and raw state were withheld.

Three baselines used the prior skill at revision `57d0e15`; the new reply-draft
case used no skill. Both variants satisfied the checked outcomes in every case.
This small sample does **not** demonstrate an improvement over baseline, a
general success rate, lower cost or compatibility with a real service.

Executed boundaries:

| Case | Actual resulting state checked |
| --- | --- |
| Form autosave | Local draft prepared; persisted profile and notifications unchanged |
| Gmail message scope | Only matching unstarred M1 labeled; starred M2 preserved; nothing sent |
| Sheets append timeout | P-3 saved once with intended values/formula; old rows preserved; target read after write |
| Reply draft timeout | One correct draft saved and read back; no duplicate draft or send |

The source/grader hashes, package fingerprints, actual operation traces, assertion
results and synthetic final states are in the JSON record. A grader review found
that unrelated-record reads initially counted as verification. The corrected
grader checks the target and read ordering after the final write, with CLI
regressions for both failures. Operation semantics did not change; execution and
grading hashes are recorded separately.

At that revision this record supported `offline-reviewed` for its four packages. That status did
not cover all authored cases. None was marked `live-tested`. The remaining
success/routing/domain cases have not been executed by this record.
See the [evaluation procedure](../README.md) for reproducing a scoped run.

## Draft coverage follow-up

The [original eight trials](draft-coverage-20261101.json) retain automated failures
from an overly literal grader. Correct wording, extra useful fields and two
observed bug-reproduction attempts were rejected. The repaired grader checks typed
facts and saved-state order while leaving prose meaning to named semantic review.
Regressions cover decimal money, receipt-policy contradictions, current-case
citations and independent reopening after every reproduction attempt.

[Eight fresh revised runs](draft-coverage-revised-20261101.json) passed both the
automated checks and explicit semantic response review. All 16 packages now have
scoped offline evidence. This does not cover every authored branch or establish
live services, real browser control or a full connected assistant.

The [first matched study](comparison-20261101/REPORT.md) recorded 20 actual runs.
It predates the draft-grader repair and retains its original source fingerprints;
the strict comparison CLI intentionally rejects it against changed source files.
Keep its observations historical rather than rewriting hashes to fit new code.

## Final release-source comparison

The [final matched study](comparison-final-20261101/REPORT.md) contains 20 new
executions and 10 matched pairs accepted against the release's current source
fingerprints. Sheets passed 5/5 for each variant; Gmail passed 3/5 without the
skill and 5/5 with it. The two baseline failures omitted post-write verification
of the starred message; all saved labels were correct. Cost remains unknown.
The report discloses unblinded review and launch-order/setup deviations. These
repeated two-task observations do not establish general or causal superiority.

## Collection expansion and focused refactors

The [expansion review](expansion-review-20261101.md) records three additional
artifact trials and two supplied-record boundaries. The [three bound retests](refactor-retests-20261101.json)
cover the exact revised research, session-capture and bug-reproduction packages;
earlier records remain historical. The [description-only trial](routing-expansion-20261101.json)
accepted all 30 selections across 25 skill descriptions, including positive and
negative requests for each new method and both sides of the research/investigation
boundary. Selection is not execution or host discovery.
