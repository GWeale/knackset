# Evaluate a workflow skill

Use a realistic task to find out what an agent actually does with a skill. Check
the result, not just its explanation. Start with a simulated task that cannot
affect a real account; use an authorized test account when you need to check a
real integration.

Each `skills/<name>/evals/evals.json` defines made-up tasks and the checks for
judging them: an ordinary success case, a case where something goes wrong or the
agent should stop, and a similar request that belongs to another skill. These
are test inputs. Completed runs are recorded separately in [results/](results/README.md).

## What the checks tell you

1. `python3 scripts/validate.py` checks packages, links, catalog, case coverage and
   whether test records match the current package contents. It does not run a
   workflow or prove a record is truthful. `python3 scripts/catalog.py render --check`
   checks that the catalog page is up to date.
2. `python3 -m unittest discover -s tests -v` executes local helper CLIs against
   temporary synthetic files. It does not test Gmail, Sheets, GitHub, or a browser.
3. `sandbox.py` simulates service behavior in isolated local files. The agent must
   perform actual actions and reads: timed-out writes can persist and retries can
   create duplicates. The simulation covers a few specific behaviors; it does not
   test a service connection or browser.
4. A forward evaluation gives a fresh agent a skill and a task, then checks its
   work against criteria it has not seen. Reading a proposed plan can reveal
   reasoning mistakes, but only an execution can show whether the result was saved.

## Run a forward evaluation

Give a fresh agent the skill instructions, task, permitted tools, and made-up
inputs. Keep the grading criteria, expected answers, and suggested solution out
of its context. In a case from `evals.json`, that means supplying `prompt`,
`context`, and input files without the expected/forbidden fields or assertions.
Keep outputs in a temporary or ignored local workspace; do not supply private
session logs.

To try the Sheets timeout case, initialize a separate workspace:

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

Let the agent choose and run its operations. After it finishes, a separate judge runs:

```bash
python3 evals/sandbox.py grade .local/my-first-run
```

A pass requires one complete requested row, unchanged existing rows, one append
attempt, and a read of the target after the write. An unfinished task fails. The
initializer will not overwrite an existing workspace, so choose a new path for
each run. For a scripted walkthrough that cleans up afterward, run
`python3 scripts/demo.py`; it shows both correct recovery and a retry that creates
a duplicate. It does not run a model.

If you can only ask an agent what it would do with a supplied page or record,
record that as a decision review. Do not describe it as a browser run. For a real
execution, use an explicitly authorized disposable test account or site and
check the saved records, including any duplicates.

## Record the result

Record date, skill revision or content hash, runtime/model and available tools,
prompt/context, actual output/action trace or artifact, checked assertions, result,
and limits. Keep private execution evidence local. Publish only synthetic or
independently sanitized evidence. Compare the same tasks without the skill before
making a claim that the skill improves performance.

Change a catalog status only when the test record supports it. `offline-reviewed`
requires a structured `sandbox` execution record. `live-tested` requires a `live`
record for the exact site, task, and runtime. Both need a matching hash of the
current package and a successful `with-skill` run with every assertion true.
Passing format checks or saying “done” is not enough.

An execution JSON record uses `schema_version: 1`, `date` (`YYYY-MM-DD`), `mode`,
`runtime`, `limitations` and `runs`. Each run names `skill`, a current evaluation
`scenario`, `variant` (`with-skill` or `baseline`), `package_sha256` (null for baseline),
`passed`, an `assertions` object of boolean checks, nonempty operation `trace` and
synthetic `final_state`. Compute package hashes using `package_fingerprint` in
`scripts/validate.py`; all package resources count except bytecode caches.
Changing the package invalidates its evidence. A reviewer still needs to check
that the recorded actions and outcomes happened and that the status does not
claim more than the test covers.

## Earlier records

The first [offline review](offline-review-2026-11-01.md) records seven decision
reviews and one run of a local helper, with content hashes. It does not claim a
live application test. Its original case set is kept in `archive/`; current
coverage checks use the cases inside each skill folder.

Approach informed by [Agent Skills evaluation guidance](https://agentskills.io/skill-creation/evaluating-skills)
and [Anthropic's outcome-based agent evaluation guidance](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).
