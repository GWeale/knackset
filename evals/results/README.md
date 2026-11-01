# Measured execution records

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

Only the corresponding four packages are marked `offline-reviewed`. Their status
does not cover all authored cases. None is marked `live-tested`. The remaining
canonical success/routing/domain cases have not been executed by this record.
See the [evaluation procedure](../README.md) for reproducing a scoped run.
