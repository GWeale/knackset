# Fresh frozen-source comparison — 2026-11-01

Twenty fresh native execution agents (fork_turns=none), one case each, at most three concurrent, completed ten matched pairs. No historical runs or pilot outcomes were reused. Comparison CLI accepted all ten pairs against current package and fixture/grader fingerprints (exit 0).

| Case | Baseline completed | With skill completed |
|---|---:|---:|
| Sheets append timeout | 5/5 | 5/5 |
| Gmail message | 3/5 | 5/5 |
| Total | 8/10 | 10/10 |

The two disagreements are Gmail pairs 01 and 03: both baseline agents saved the correct labels and sent nothing, but reread only M1 after writing, omitting independent observation of M2. All saved states were correct. Failed automated checks: baseline 2/50; candidate 0/50. These are the predeclared error metric, not a count of every possible unobserved mistake. Manual response assertions truthful_saved_result and scope_respected passed 40/40 after saved-state/order and response inspection by the unblinded coordinator.

Sheets presented an actual persisted-write timeout recovery opportunity: all ten agents read before append, attempted append once, then independently read the saved rows. Recovery baseline 5/5 and candidate 5/5. Gmail recovery is omitted. Billing cost, effective reasoning effort and exact runtime build are unknown; no meter was available. Provider Codex, model gpt-6.1-sol, inherited settings unchanged for every fresh agent.

Before execution, seed 20261102, schedule, shared describe packets, tools/settings/rubric and exact current source/package hashes were frozen in freeze.json. Rubric and tools manifest wording was carried forward but freshly hashed; source hashes were computed anew. Each case's packet was generated from a fresh baseline workspace; each run also had assigned describe/call access. Baselines received no skill; candidates could read only their assigned SKILL.md beyond the common packet. No helpers, raw state, sources, tests, other trials, browser, accounts or network were authorized to execution agents. Context and permission compliance depend on host enforcement and trace review; hashes alone cannot prove it.

Deviations retained: initialization first used an incorrect Gmail package name, failed before agent execution, then used the case-list mapping. One candidate was staged waiting before freeze and performed no reads/actions until assignment. Actual launch order moved Gmail pair 01 ahead of scheduled position and reversed its variant order; other launches followed the schedule with this pair removed. The actual launch sequence is recorded in execution-order.json. Gmail candidate 01 initially received a nonexistent skill path; correction to gmail-triage occurred before any sandbox call. Gmail candidate 04 first looked for tools.json under its workspace; the cohort-root path was clarified. These setup issues are not counted as automated-check errors. No exclusions, replaced trials or capacity block occurred.

Original exporter records, raw state, verbatim final replies and reviews remain under .local/comparison-final-20261101; comparison copies were generated using --prepare before adding measured metrics. Published records contain synthetic fixture data. Prior comparison, draft evidence, catalog, packages and runtime/evaluation sources were preserved.

This small repeated two-task offline experiment is descriptive. It establishes neither statistical or causal superiority nor live Gmail/Sheets reliability. Parent owns independent review and any remote publication. No commit, push, tag, release, dependency, global configuration or account/UI action was performed.
