# Evaluate a workflow skill

Each `skills/<name>/evals/evals.json` contains canonical synthetic tasks and
acceptance rubrics. These are not recordings or measured results. Each skill
includes success, failure/boundary and neighboring-task routing cases. The
original central set lives under `archive/` as historical evidence, excluded
from current coverage checks.

The first [offline review record](offline-review-2026-11-01.md) contains seven
fixture decision checks and one executed local helper case, with content hashes.
It does not claim all scenarios or any live application workflow were executed.

## Different test seams

1. `python3 scripts/validate.py` checks packages, links, catalog, case coverage and
   promoted evidence fingerprints. It does not execute a workflow or authenticate
   evidence. `python3 scripts/catalog.py render --check` checks discovery docs.
2. `python3 -m unittest discover -s tests -v` executes local helper CLIs against
   temporary synthetic files. It does not test Gmail, Sheets, GitHub, or a browser.
3. `sandbox.py` executes isolated file-backed service fixtures. The agent must
   perform actual actions and reads: timed-out writes can persist and retries can
   create duplicates. These simulate bounded behaviors, not real services or a browser.
4. Forward evaluation asks an independent agent to use a skill on a supplied task,
   then checks actual resulting artifacts/state against a withheld rubric. A plan
   review establishes decision behavior only; a live workflow requires real tool
   execution and observation of the relevant final state.

## Run a forward evaluation

Give a fresh evaluator only the skill folder, scenario prompt/context, permitted
tools, and synthetic inputs. Withhold expected/forbidden arrays until judging the
result. Use a temporary workspace, not the skill library's public tree. Do not give
the evaluator author conclusions, a suggested solution, or private session logs.

For an executable offline case, initialize a separate workspace for every run:

```bash
python3 evals/sandbox.py init sheets-append-timeout .local/my-first-run
python3 evals/sandbox.py describe .local/my-first-run
```

Give a fresh evaluator this complete task:

> Read `skills/google-sheets-update/SKILL.md`. Complete the request returned by
> `python3 evals/sandbox.py describe .local/my-first-run`, using only that
> workspace's `describe` and `call` operations. Obtain the observations you need
> through that interface. Do not inspect the raw state, fixture implementation,
> test cases or grader. Report what you actually did and what remains uncertain.
> This is a synthetic offline task; do not access a live account.

The evaluator chooses and executes its operations. A separate judge then runs:

```bash
python3 evals/sandbox.py grade .local/my-first-run
```

A passing result requires one complete requested row, preserved existing rows,
one append attempt, and a target read after the write. An unfinished workspace
fails; initialization refuses to reset existing state. Use a fresh temporary
workspace for each independent/baseline trial. For a fully scripted walkthrough
with cleanup, run `python3 scripts/demo.py`; it illustrates both correct recovery
and a duplicate-producing retry, without running a model.

If no browser/test account is available or authorized, request a decision trace
against the supplied observed state. Record that limitation; never call it a
browser replay. For a real execution, supply an explicitly authorized disposable
account/site fixture and verify resulting records and duplicate counts.

Record date, skill revision or content hash, runtime/model and available tools,
prompt/context, actual output/action trace or artifact, checked assertions, result,
and limits. Keep private execution evidence local. Publish only synthetic or
independently sanitized evidence. Compare the same tasks without the skill before
making a claim that the skill improves performance.

Promote a catalog entry only when its evidence supports the declared scope:
`offline-reviewed` requires a structured `sandbox` execution record; `live-tested`
requires `live` evidence for the exact site/task/runtime. Both require a current
package fingerprint and matching successful `with-skill` run with all assertions
true. Format checks and an assistant's success claim alone are insufficient.

An execution JSON record uses `schema_version: 1`, `date` (`YYYY-MM-DD`), `mode`,
`runtime`, `limitations` and `runs`. Each run names `skill`, a current evaluation
`scenario`, `variant` (`with-skill` or `baseline`), `package_sha256` (null for baseline),
`passed`, an `assertions` object of boolean checks, nonempty operation `trace` and
synthetic `final_state`. Compute package hashes using `package_fingerprint` in
`scripts/validate.py`; all package resources count except bytecode caches.
Changing the package invalidates its evidence. Human review must still establish
that the trace and outcome are authentic and the promoted scope is appropriate.

No benchmark score or live compatibility claim is implied by the authored suite.

Approach informed by [Agent Skills evaluation guidance](https://agentskills.io/skill-creation/evaluating-skills)
and [Anthropic's outcome-based agent evaluation guidance](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).
