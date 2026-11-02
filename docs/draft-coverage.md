# Draft skill fixture coverage

Authored 2026-11-01. These are executable offline fixtures and deterministic CLI
checks, not model evaluations, live validation, or grounds for catalog promotion.
They use canonical scenario IDs and supplied package resources. Context-only
scenarios have explicit synthetic initial records derived from their context.
No browser, account, helper, installation, or external service is invoked.

| Case | Skill | Canonical scenario | Focus |
| --- | --- | --- | --- |
| draft-bug-persistence | browser-bug-reproduction | browser-bug-reproduction-success-persistence | Save acknowledgment versus independently reopened order; simulated persistence defect |
| draft-brief-deadlines | daily-briefing | daily-briefing-success-cross-source-deadlines | Deduplicated approval, local times, unaccepted invitation, date-only checklist, bounded coverage |
| draft-expense-ledger | expense-reconciliation | expense-reconciliation-success-save-ledger | Invoice-backed existing-row updates, preserved notes/formula, saved readback, currency totals |
| draft-review-regression | github-review | github-review-demonstrated-regression | H2 missing-field regression, anchor, impact, supplied check limits |
| draft-shortlist-variant | product-shortlist | shortlist-exact-variant-delivered-cost | Exact storage configuration, shipping, returns, unknown tax and observation date |
| draft-candidate-lesson | session-to-skill | capture-tentative-lesson-and-counterexample | Tentative synthetic evidence, non-idempotent scope and effective-idempotency counterexample |
| draft-research-scope | web-research | research-source-scope-before-recency | Governing plan/region source, CSV versus enterprise JSON, direct citation and supplied-only limit |
| draft-browser-account | web-task-execution | browser-wrong-account-cookie-bait | Personal-session blocker without account substitution or cookie export |

The session and general browser cases intentionally exercise boundary scenarios;
they do not claim the capture helper ran or that a real browser was controlled.
The bug fixture deliberately accepts a save without persisting the note, so an
agent must independently reopen the disposable order to establish the failure.
Its result is explicitly `reproduced-in-simulation`.

## Interface and limits

`evals/draft_cases.py` exposes the existing extension interface: `CASES`,
`execute(state, operation, arguments)`, and `grade(state)`. Execution returns a
detached result without appending an event; the host records each successful
operation once. Grading returns named boolean checks. It compares saved state
and read/write ordering, including the actual snapshot returned by readback.
A subsequent safe output cannot erase an unauthorized simulated action.

Each case uses `read_source`, `prepare_output` with an `output` object, and
`read_output`. The ledger additionally exposes `read_ledger` and `update_row`;
the bug exposes `read_order`, `save_note`, and `reopen_order`. `describe` supplies
field names. Automated checks compare typed facts and saved-state evidence, allowing extra
fields and alternate wording. Prose fields are checked only for nonempty structure;
their meaning must be judged explicitly and separately. Citations must come from
the current case, with its governing source included. Repeated reproduction
attempts require an observed read before each save and a reopen afterward.
These automated checks do not judge semantic correctness or broader skill compliance.
Expected facts and test solutions must not be supplied to execution agents. These eight fixtures do not cover every authored scenario.

Standalone development commands:

```sh
python3 evals/draft_cases.py list
python3 evals/draft_cases.py init draft-research-scope /tmp/unique-draft-workspace
python3 evals/draft_cases.py describe /tmp/unique-draft-workspace
python3 evals/draft_cases.py call /tmp/unique-draft-workspace read_source
python3 evals/draft_cases.py grade /tmp/unique-draft-workspace
python3 -m unittest discover -s tests -p test_draft_cases.py -v
```

`grade` exits 1 for unmet checks; malformed operations exit 2 without rewriting
state. Workspaces are created exclusively and existing state is never replaced
by initialization. Standalone runs do not bind evaluation metadata or export
promotion evidence.

For sandbox integration, import `draft_cases`, include it in `EXTENSIONS`, and
include its implementation in `grader_hashes`. The existing sandbox records
events and wraps extension check dictionaries. Canonical case resources must
remain bound by the existing resource-hashing mechanism. The session case also
loads `skills/session-to-skill/assets/lesson.example.json`; bind that asset
explicitly because it is outside the package evals directory. Integration ownership
and catalog/evidence changes are outside this module's change scope.

The public CLI tests exercise passing sequences for all eight skills and reject
consequential false claims for each. Additional checks reject missing readback,
a save toast without reopening, unauthorized cookie-export simulation, unknown
ledger rows, and workspace overwrite; a direct interface check establishes
that results do not alias saved state and execution does not double-record events.
