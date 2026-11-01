# Measured execution records

Six workflows have scoped offline records. None has been tested against a live
service. Keep the individual runs and their limits in view: these are small
trials, not a general success-rate benchmark.

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

Calendar and Docs are now `offline-reviewed` for these two cases only. Scheduling,
the other Calendar/Docs cases, and real service behavior remain untested here.

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

This record supports `offline-reviewed` for its four packages. Their status does
not cover all authored cases. None is marked `live-tested`. The remaining
success/routing/domain cases have not been executed by this record.
See the [evaluation procedure](../README.md) for reproducing a scoped run.
