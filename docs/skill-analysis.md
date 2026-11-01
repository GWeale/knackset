# Skill analysis and improvement decisions

Reviewed 2026-11-01 against [current authoring guidance](https://agentskills.io/skill-creation/best-practices)
and [evaluation guidance](https://agentskills.io/skill-creation/evaluating-skills).
The review prioritized non-obvious task semantics over longer general advice.
These are concrete changes, not universal scores or a claim to implement every
practice in every host.

## Existing workflows

| Skill | Identified gap | Resulting improvement |
| --- | --- | --- |
| `web-form-update` | A draft can persist while typing on an autosave form | Discover commit semantics before typing; prepare locally when live controls autosave |
| `google-sheets-update` | Row identity can change between lookup and write | Recheck key/prior values; preserve formulas; disclose non-atomic append deduplication |
| `gmail-triage` | Mutating a paginated result can skip messages | Collect bounded matching IDs before changing query membership; preserve message/thread scope |
| `github-review` | A first diff page can look complete | Check pagination, truncation and unavailable patches; tie findings/checks to the reviewed head |
| `web-task-execution` | General routing can swallow application workflows | Use as browser fallback; reobserve identity after redirects/authentication/human handoff |
| `product-shortlist` | Headline price can belong to a different variant | Resolve chosen configuration and material unknown costs; use conditional rankings when needed |
| `web-research` | Supplied evidence can be mistaken for live retrieval | Label source bundles, compare scope/effective dates, distinguish unavailable evidence |
| `session-to-skill` | Every generated draft assumed writes | Add explicit read-only/write scope; conditional recovery; optional scoped lessons and counterexamples |

## Added task families

| Skill | Domain knowledge that justifies a distinct package |
| --- | --- |
| `calendar-coordination` | Time zones, availability, recurrence occurrences, invitation effects |
| `recurring-monitor` | Last good state, meaningful deltas, missing sources, scheduler handoff |
| `expense-reconciliation` | Transaction identity, currencies, duplicate/partial matching, unresolved ledger |
| `browser-bug-reproduction` | Safe test environment, expected/actual behavior, minimal repeatable steps |
| `travel-reservation` | Search/quote/hold/commit/confirm/change/cancel lifecycle, total costs and uncertain writes |
| `gmail-draft-reply` | Local composition versus saved draft, recipient/thread identity, no send under draft scope |
| `google-docs-update` | Document/tab targeting, revision conflicts, bounded formatting-preserving edits |
| `daily-briefing` | Cross-source deduplication, explicit time window, actionable priorities, coverage gaps |

Current official application semantics are linked inside the relevant package.
No upstream instruction files were imported. [Product alignment](product-alignment.md)
records which public product examples informed the expansion.

## Quality gates that scale

- Description is the routing source of truth. Catalog tags improve deterministic
  discovery without loading every skill's instructions.
- Each package carries its own license and canonical `evals/evals.json`: an
  ordinary task, a failure/boundary, and an adjacent task that should route elsewhere.
- Test inputs and measured execution are separate. State-changing fixtures must
  require an actual observation after the action rather than pre-supplying success.
- Promotion requires a structured dated execution record, a matching package
  fingerprint, successful assertions and the right offline/live evidence mode.
  These checks establish integrity, not authenticity of an author's claim.
- A scoped learned lesson needs a trigger, conditions, proposed action, evidence,
  limits and counterexamples. Repetition or heuristic confidence alone does not
  authorize actions or establish a broadly correct rule.

The [evaluation guide](../evals/README.md) explains the test seams and limits.
Live account behavior and consumer-product integration remain separate work.
The [stateful preview results](../evals/results/README.md) record actual actions
for four risk-bearing boundaries and their baselines, including a corrected
grader failure. Equal observed outcomes do not establish performance improvement.

## Follow-up review — 2026-11-01

A review of the wording found four instructions worth correcting:

| Skill | Correction |
| --- | --- |
| `calendar-coordination` | Scope the exclusive all-day end date to the Google API; follow the actual field's meaning in other tools |
| `google-docs-update` | Prepare proposed text when suggestions are unsupported; do not silently apply direct edits |
| `recurring-monitor` | Treat an ongoing-watch request as authorization to schedule it, while respecting a request to defer the first check |
| `session-to-skill` | Require write-recovery guidance only for workflows that can change state |

These came from reading the instructions, not observing new live failures. Three
new boundary cases cover the calendar, Docs, and scheduling decisions. They are
authored inputs, not completed agent runs. All four changed packages remain
`draft`; the four packages with existing execution records are unchanged.
