# Recorded browser failure evidence pack

Review date: 2026-11-01. All observations and identifiers are fictional.
Result: a failure is supported by supplied records; this reviewer did not run a
browser, replay steps, inspect code, or collect fresh execution evidence.

## Sources and scope

- Procedure: `skills/browser-bug-reproduction/SKILL.md`, read for its instructions
  to separate observations from hypotheses, verify saved state by reopening,
  reduce only with observed evidence, and retain a nearby passing comparison.
- Observation source: `skills/browser-bug-reproduction/evals/files/recorded-attempts.md`.
  All execution claims below are attributed to that tester-supplied record.
- No other source files were consulted. No network, browser, GUI, account,
  replay, helper, installation, package edit, shared-file edit, commit, or
  publication was used.

## Target and preconditions

- Target: staging build R8, as recorded by the tester.
- Each attempt began with a reset owned test order and an empty delivery note.
- Failing role: reviewer. The administrator role is a separate comparison.
- Browser/version, viewport, locale, time zone, feature flags, exact order
  identifier, and source revision were not supplied.
- Expected behavior, inferred from the save-and-reopen task: after saving a
  delivery note, reopening that same order should show the entered note.

## Smallest already-observed failing sequence

Attempt 2 is the shortest failing sequence actually present in the records:

1. As reviewer, open the reset test order with an empty delivery note.
2. Enter `Gate A` as the delivery note.
3. Save.
4. Reopen the same order.

Recorded result: the toast said saved; the reopened delivery note was empty.
Expected: the reopened note would be `Gate A`.

Attempt 1 also failed with reviewer and `Gate A`, but added opening Help,
changing table sort, and visiting Dashboard before opening the order. Attempt 2
shows that those extra actions were unnecessary for this recorded failure.
There is no observed failing sequence shorter than attempt 2 in the supplied
record. This does not establish that every remaining action or character is
necessary.

## Passing comparisons and observations

| Evidence | Role | Sequence difference from attempt 2 | Entered note | Toast | Note after reopening |
| --- | --- | --- | --- | --- | --- |
| Attempt 1 | reviewer | Help, sort change, Dashboard before opening order | `Gate A` | saved | empty |
| Attempt 2 | reviewer | baseline | `Gate A` | saved | empty |
| Attempt 3 | reviewer | input changed only | `Gate B` | saved | `Gate B` |
| Attempt 4 | administrator | role changed only | `Gate A` | saved | `Gate A` |

Attempt 3 is the closest same-role passing comparison: it keeps the shorter
path, reviewer role, and recorded reset state, while changing `Gate A` to
`Gate B`. The reopened note was `Gate B`. Attempt 4 is a complementary,
single-condition comparison: with `Gate A` and the shorter path, administrator
passed. These comparisons narrow the observed boundary; neither establishes a
code-level cause or proves that the failure is specific to the reviewer/input
combination.

## Frequency and evidence limits

- The exact shorter reviewer / `Gate A` sequence was recorded once and failed
  once (attempt 2). No exact-sequence repeat is supplied.
- Both supplied reviewer / `Gate A` attempts failed (2 of 2), with different
  preceding navigation. This is not a measured failure rate or proof of
  determinism.
- The reviewer / `Gate B` and administrator / `Gate A` sequences each passed
  once. They do not establish that either condition always passes.
- Reopening supplies a recorded UI observation of the note. No direct service,
  storage, or network evidence establishes whether the value was rejected,
  lost, delayed, or displayed incorrectly. The success toast alone is not
  evidence of persistence.

## What remains untested

- Exact repeats of the shorter failing sequence and both passing comparisons.
- Any further step reduction or a shorter input that still fails; the necessity
  of remaining steps and individual characters has not been tested.
- Other note values, roles, builds, flag settings, browser conditions, and
  starting data states. Even administrator / `Gate B` is not recorded.
- Source code, service/storage state, and network traces. Root cause is unknown.
- Any proposed repair or workaround beyond the individual recorded passing
  attempts.

The next useful execution, if a runner is later authorized and available, is to
repeat attempt 2 from its recorded reset state, then repeat attempt 3 with only
the input changed. No such execution was performed for this review.

## Artifacts and actual checks

- `evidence-pack.md`: this source-attributed review of the four supplied attempts.
- `final.txt`: complete handoff answering the requested failing sequence,
  closest passing comparison, and untested conditions.
- Actual review checks: read the two allowed source files; compared each
  sequence and reopened-note result; distinguished the one exact shorter-path
  failure from the broader two-attempt combination; checked both output files
  exist, are nonempty, and contain the stated observations and limitations.
- No browser execution, automated reproduction test, or live validation was run.
