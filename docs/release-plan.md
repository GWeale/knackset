# v0.1 release preparation

Prepared 2026-11-01. George subsequently requested all five remaining milestones,
including launch. That request authorizes the release; this document alone grants
no authority. Publication still requires completed candidate checks.

## Release scope and wording

Proposed title: **Knackset v0.1 — workflows that check what happened**.

Proposed release text:

> Knackset packages portable agent instructions for tasks including Sheets,
> Gmail, forms, calendars and Docs. Workflows emphasize bounded authorization,
> inspecting saved state and recovering from uncertain writes. Start with one
> skill and the local timeout demo. Python helpers use the standard library.
>
> This first preview includes synthetic offline fixtures, explicit execution
> evidence export, routing checks and a paired comparison tool. The scripted
> demo runs no model and accesses no accounts. Evidence is task-, revision- and
> runtime-specific; this preview makes no general performance, cost or live
> integration reliability claim. Host tools and authorization still apply.

See [CHANGELOG](../CHANGELOG.md) for the proposed release contents. Preserve the
existing icon and package licenses.

## Local release gates

1. Freeze a candidate commit and review the diff for private data, provenance,
   package licenses and unchanged unrelated work. Check every catalog validation
   statement against current fingerprints; rerun evidence or return stale entries
   to draft. Do not upgrade validation based on helper tests alone.
2. Run `python3 scripts/validate.py`,
   `python3 scripts/catalog.py render --check`, and
   `python3 -m unittest discover -s tests -v`. Record exact revision, environment,
   commands and outcomes in the release review. Run `python3 scripts/demo.py` and
   inspect its one-row versus duplicate-row outcome.
3. Check the documented project-scoped install in a disposable local project,
   preserving full skill resources and proving the destination. Verify activation
   separately from a file-copy check. Account access is outside this release gate.
4. Review comparison records under [the protocol](comparison-protocol.md) only
   when fresh matched trials actually exist. Otherwise state that comparative
   performance is unmeasured. Do not make fabricated records to fill a release gap.
5. Present the candidate revision, gate results and release text for George's
   publication decision. Tagging, pushing, publishing and contacting testers
   require an explicit instruction; this document is preparation only.

## Demo and feedback packet

A three-minute local demo: show an append timeout, inspect the one persisted row,
then show the scripted blind-retry duplicate. Explain that both are scripted
synthetic paths. Point to a skill's read/action/verify instructions, then show
how an evaluator exports a judged run. Do not present the demo as a benchmark.

Proposed tester request, ready for George to send if desired:

> Try one project-scoped skill on a disposable synthetic task. Tell us your host,
> runtime/model, skill revision, expected result, actual saved result and the
> first confusing instruction. Include sanitized reproduction steps and whether
> activation was observed. Please omit account identifiers, credentials and
> private transcripts. Report uncertain writes and authorization mistakes even
> when the final response sounded successful.

Collect feedback in the existing bug-report form linked from the README; no
messages or issues are sent as part of preparation. Triage first by unintended
write/privacy boundary, then incorrect saved state, activation failure and unclear
instructions. Convert accepted failures into minimal synthetic cases, reproduce
before editing, and rerun relevant checks after a focused repair. Close the loop
with reproducible evidence rather than a broad success claim. A first follow-up
review after five independent reports is a planning target, not evidence already
collected or a deadline promised to testers.

## Integration observations — 2026-11-01

The scripted demo was executed: reconciliation left one requested row and passed;
a blind retry created two requested rows and failed the uniqueness check. This
is a deterministic demonstration, not a model comparison. One fresh with-skill
Sheets pilot passed all four saved-state assertions and an unblinded final-response
review. It made three successful sandbox operations and one rejected CLI syntax
attempt. It is excluded from the planned repeated comparison. No billing meter
was available; cost is unknown. The initial 20-run matched study is complete and retained as historical after
a later grader repair. Eight fresh revised draft trials passed automated and
semantic checks; the final matched study against frozen release sources completed 20 fresh runs
and 10 accepted pairs. With-skill completion was 10/10 versus baseline 8/10;
the two missed checks were verification omissions, with correct saved labels.
Cost is unknown; judging was unblinded. No outside feedback has been collected by this lane.

Live tests remain blocked: no designated disposable account, no discovered
Docs/Sheets/Calendar connectors, and the Gmail profile result did not establish
verified Google authentication. The human-only browser hold remains active.
The runtime is a synthetic local MVP without a real service adapter; this release
does not deliver a full connected assistant.
