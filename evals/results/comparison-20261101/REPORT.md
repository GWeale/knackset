# Matched synthetic study — 2026-11-01

Completed all 20 fresh-context runs, 10 matched pairs (five per case), in the predeclared seed-20261101 launch order. The excluded integration-trial-01 pilot contributes no observations. No cohort run was excluded or retried. `comparison.json` was accepted by the comparison CLI (exit 0, ten pairs).

| Case | Baseline passing | With-skill passing | Failed automated checks baseline / skill |
| --- | --- | --- | --- |
| Sheets append timeout | 5/5 | 5/5 | 0/20 / 0/20 |
| Gmail message labels | 3/5 | 5/5 | 2/30 / 0/30 |
| Total | 8/10 | 10/10 | 2/50 / 0/50 |

The two discordant pairs are Gmail repeats 03 and 05. Both baselines saved the correct labels and sent nothing, but read only M1 after the write. The frozen `message_labels_independently_read` check requires post-write observation of both M1 and M2. Thus these are verification-boundary failures, not incorrect final labels. Each contributes one error under the predeclared error definition: number of failed automated assertions. This does not measure CLI errors or all agent mistakes. All 40 manual response assertions passed: each response matched saved state and claimed no unauthorized action.

Sheets supplied an actual uncertain-write opportunity in all ten runs. Both variants recovered in 5/5 opportunities: read, one append returning timeout, then read confirming exactly one P-3 row and preserved existing formulas. Gmail had no recovery opportunity and its recovery metric is omitted. Complete billing cost is unknown for all 20 runs; no meter was available and no cost estimate was substituted.

Before execution, task packets and the tools/settings/rubric manifest were frozen with hashes in `freeze.json`. Candidates read the designated SKILL.md; baselines received no skill. All contexts were native `fork_turns=none`, inherited Codex/gpt-6.1-sol and unchanged settings. The harness does not expose an exact reasoning-effort value or runtime build; these remain unknown rather than inferred. Each run used an independently init-bound workspace. Agents were restricted to their frozen packet, treatment skill if applicable, and public sandbox describe/call operations. No live accounts, browser, network, source inspection or helper use was authorized. No package or harness changes occurred.

Setup deviations: run 02 initially received an incorrect skill filename, reported it missing without searching or executing, then received the correct treatment path before execution. Agents were generally staged with a READY turn before their single run; none executed a second run. One native launch and two coordinator shell calls returned `aborted before dispatch`; retries succeeded. No thread-limit error occurred. Runs overlapped in execution while retaining scheduled launch order, with at most three active execution agents. The full shared tools manifest includes judge measurement definitions, so execution agents were not blinded to those definitions; skill bodies and fixture/grader internals were withheld from baselines. The coordinator judged actual saved states and verbatim responses unblinded, having assigned treatments; no independent blinded-judge claim is made.

Raw init-bound workspaces, exact response files, explicit reviews and immutable exporter originals remain under `.local/comparison-20261101/`. The twenty named JSON files here are comparison copies created with `--prepare`, bound to the same per-case packet and common tool manifest; measured metrics were subsequently added without modifying exporter originals. They retain actual synthetic traces, state, failures, exact responses and source-report hashes. `schedule.json`, packets, tools manifest and freeze hashes accompany them. Synthetic `.invalid` addresses and fixture identifiers are intentional; no real account data is included.

These are small repeated observations on two fixed offline tasks, not independent task sampling, a significance test, a causal improvement estimate or evidence of live Gmail/Sheets reliability. No catalog promotion follows. Parent review and publication remain separate.
