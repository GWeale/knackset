# Review the old methods before adding more

Reviewed 2026-11-01 against `72919f5047ff7cf4b6eaa4417763ca99842b95b6`.
A fresh read-only reviewer inspected all 16 older entrypoints, their canonical
cases, validation notes and relevant resources/tests. These are design gaps,
not measured performance regressions. The review recommended three focused
refactors and preserving the operational knowledge in the other packages.

## Three changes worth making

| Method | Before | Refactor | Actual check |
| --- | --- | --- | --- |
| Session to Skill | A useful curation goal led into a required service-shaped JSON/generator path; updating existing guidance was easy to miss. | Choose reuse, amendment, a distinct new skill or no change first. Write the useful artifact directly. Keep the existing JSON/helper compatible and optional. | Fresh bound candidate-lesson task preserves tentative evidence and its counterexample. A separate creative capture trial actually amends an existing method, preserving editable lettering. |
| Web Research | Its broad synthesis description overlapped Rabbit Hole's investigative explanation. | Keep bounded facts, source applicability and comparisons here; use an investigative method for competing explanations of a puzzling change. | Fresh bound plan/region task still chooses the governing source. Description-only routing selects the intended method on both supplied-source tasks. |
| Browser Bug Reproduction | The output promised minimal steps, but the procedure stopped at repetition. | Remove incidental steps or vary one condition when useful, rerun a reduction, retain reporter conditions and distinguish symptom from cause. | Fresh fixture execution repeats the persistence failure and actually verifies a one-character reduction. A separate record-review task identifies a same-role passing comparison without claiming a new replay. |

The session-record helper, its schema and existing public CLI contracts are
unchanged. No new runtime, memory service, browser framework or dependency was
introduced. The new entrypoint can capture artistic decisions without inventing
an account operation to fit a generator.

Each edited promoted package invalidated its previous fingerprint. The
[three new bound runs](../evals/results/refactor-retests-20261101.json) and separate
final-response reviews cover the current package and named scenario only.
Historical successes and failures remain unchanged. No broad improvement or live
compatibility follows from a scoped retest. The
[expansion review](../evals/results/expansion-review-20261101.md) records the new
artifact and routing checks separately.

## Preserve the rest

| Method | Disposition and reason |
| --- | --- |
| Web Form Update | Keep autosave/draft distinctions and partial-persistence recovery. |
| Web Task Execution | Keep for now. It may later consolidate with a host adapter, but session provenance, identity and resource ownership still matter. Do not make portable methods depend on it. |
| GitHub Review | Keep merge-base comparisons, full-diff coverage, revision-bound findings and the possibility of no finding. |
| Travel Reservation | Keep quote, hold, authorization and per-leg confirmation distinct. |
| Calendar Coordination | Keep recurrence, ambiguous local times, date-only form semantics and invitation effects. Defer Google expansion. |
| Daily Briefing | Keep source coverage, status reconciliation and obligation distinctions. Test stale/inaccessible coverage before adding more instructions. |
| Expense Reconciliation | Keep receipt allocation, signed refunds, currency totals and policy exceptions. |
| Gmail Draft Reply | Keep wording/draft/send states, identity and preservation. Defer Google expansion. |
| Gmail Triage | Keep message/thread scope, frozen target sets and unread effects. Defer Google expansion. |
| Google Docs Update | Keep tab identity, UTF-16 ranges, formatting and revision conflicts. Defer Google expansion. |
| Google Sheets Update | Keep stable keys, literal/formula semantics and non-atomic append recovery. Defer Google expansion. |
| Product Shortlist | Keep exact variants, delivered cost and ranking-reversal conditions. Evaluate missing shipping/no-qualifying cases before expanding it. |
| Recurring Monitor | Keep setup, pending baseline, scheduled check, transient failure and delivery reconciliation distinct. Splitting only for brevity would hide real states. |

Shorter is useful when it removes an unnecessary decision. It is harmful when it
removes a real condition the next agent needs. This pass keeps those distinctions
and improves three methods with concrete acceptance evidence.
