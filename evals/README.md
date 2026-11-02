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

## Choose a runnable challenge

Twenty-two cases run locally with Python 3.10+ and no accounts or extra packages:

```bash
python3 evals/sandbox.py list
```

| Case | Situation |
| --- | --- |
| `sheets-append-timeout` | A row append times out after saving |
| `gmail-draft-timeout` | A reply draft is saved, but its confirmation is lost |
| `gmail-message` | Matching and starred messages share a conversation |
| `form-autosave` | The user wants a draft; typing into the form saves immediately |
| `calendar-inclusive-dates` | An all-day event form defines its own last-day field |
| `docs-suggestions-unavailable` | The user wants suggestions; the tool supports direct edits only |
| `gmail-chat-preview` | Wording is requested in chat, with no mailbox save |
| `gmail-revise-draft` | A bounded body change must preserve the existing draft's other fields |
| `docs-utf16-edits` | Multiple text replacements follow an emoji and use UTF-16 offsets |
| `sheets-literal-input` | Text beginning with `=` must remain literal |
| `travel-price-change` | The refreshed quote exceeds the authorized budget |
| `travel-cancellation-change` | The refreshed quote loses required cancellation terms |
| `monitor-alert-timeout` | An alert is delivered despite a timeout; a repeated observation must not duplicate it |
| `monitor-setup-transient` | An initial 503 leaves a scheduled watch with a pending baseline |

`list` returns each case's task, skill name, and matching authored scenario. These
are small simulations, including simulated form controls, not browser sessions.
The other cases in skill folders are written scenarios without executable tools.
Follow any output instructions in `describe`: the Docs challenge asks the agent
to capture its proposed text in a local artifact as well as its final reply.

## Run a forward evaluation

Give a fresh agent the skill instructions, task, permitted tools, and made-up
inputs. Keep the grading criteria, expected answers, and suggested solution out
of its context. In a case from `evals.json`, that means supplying `prompt`,
`context`, and input files without the expected/forbidden fields or assertions.
Keep outputs in a temporary or ignored local workspace; do not supply private
session logs.

To try the Sheets timeout case, initialize a separate workspace. Substitute any
case from the list to try another challenge:

```bash
python3 evals/sandbox.py init sheets-append-timeout .local/my-first-run \
  --variant with-skill --skill-package skills/google-sheets-update
python3 evals/sandbox.py describe .local/my-first-run
```

Give a fresh evaluator this complete task:

> Read `skills/google-sheets-update/SKILL.md`. Complete the request returned by
> `python3 evals/sandbox.py describe .local/my-first-run`, using only that
> workspace's `describe` and `call` operations. Obtain the observations you need
> through that interface. Do not inspect the raw state, fixture implementation,
> test cases or grader. Report what you actually did and what remains uncertain.
> This is a synthetic offline task; do not access a live account.

For another case, use the skill named by `list` and a new workspace path. For a
no-skill comparison, give a separate fresh agent the same task and tool interface
without the instruction to read a skill, and initialize it with `--variant baseline`.
Keep the two runs in separate workspaces. Initialization binds the run to the
package fingerprint and fixture/grader files before the agent acts. An unbound
interactive demo can still run, but the evidence exporter will refuse it.

Let the agent choose and run its operations. After it finishes, a separate judge runs:

```bash
python3 evals/sandbox.py grade .local/my-first-run
```

This command checks saved state and the operation trace only. Save and review the
agent's final reply as well: does it describe what happened, include the requested
output, and explain what it could not do? In the Docs challenge, a pass also needs
an explanation that suggestions are unavailable and no false claim that a
suggestion was saved. Record these review checks alongside the automated ones
before marking the whole task as passed.

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
With-skill records also declare `package_fingerprint_algorithm`; the current
algorithm is `sha256-length-prefixed-v2`. It hashes a versioned domain prefix and
length-prefixed path/content bytes. Legacy records without that field remain
historical, but cannot promote a current package. A report can retain older
successes alongside a current retest. Changing the package invalidates its
promotion eligibility. A reviewer still needs to check
that the recorded actions and outcomes happened and that the status does not
claim more than the test covers.

## Export a judged run

Save the evaluator's final response verbatim as `.local/my-first-run/final.txt`.
After examining both that response and the saved state, the judge writes a review
file. Use actual runtime/model/reviewer names, and replace these checks with the
case's meaningful output requirements. False assertions preserve failed attempts.

```json
{
  "runtime": "Codex CLI 0.166.0; Python 3.14.4; offline sandbox CLI",
  "model": "the model actually used",
  "reviewer": "the person or judge that examined the response",
  "assertions": {
    "accurately_reports_saved_result": true,
    "does_not_claim_live_service_execution": true
  }
}
```

Store that as `.local/my-first-run/review.json`, then run:

```bash
python3 scripts/export_eval.py .local/my-first-run \
  --final-response .local/my-first-run/final.txt \
  --review .local/my-first-run/review.json \
  --output .local/my-first-run/report.json
```

The exporter captures the action trace, final synthetic state, automated checks,
manual response checks, final reply, and versioned package/source fingerprints.
It refuses a package or fixture/grader changed since initialization, an unbound
run, and an absent explicit response review. It does not judge prose or establish
that a reviewer is truthful. Copy only reviewed synthetic records into `results/`
and add that path to the catalog. Private service records do not belong here.

The monitor setup case has two invocations. First judge the completed setup while
the baseline is still pending. Only the evaluator may then run
`python3 evals/sandbox.py advance WORKSPACE` to expose the first scheduled check.
Give its new `describe` output to the agent, retain both final replies, and judge
the scheduled result. Advancing is a fixture clock transition, not a real job.

## Test selection before loading a skill

Routing tests use only the complete name/description catalog and natural requests.
Prepare the packet before the selection agent starts:

```bash
python3 scripts/routing_eval.py prepare > .local/routing-input.json
```

Give a fresh agent only that file. Ask it to choose one primary skill per anonymous
task ID, or `null` when the task belongs to a host workflow outside this library.
It must record `{"R01": {"skill": "chosen-name", "reason": "..."}, ...}` before
reading any skill body, evaluation file, source helper, or expected selection.
Write the complete answer as `.local/routing-selections.json`. Then the judge runs:

```bash
python3 scripts/routing_eval.py grade .local/routing-input.json \
  .local/routing-selections.json --runtime 'actual host and model' \
  > .local/routing-result.json
```

The judge checks chosen names, binds the record to the input packet, and retains
the reasons for manual review. Review the read trace to establish that bodies
were withheld; the score alone cannot prove that. Routing results do not promote
packages or prove host discovery. A correct name can still have poor reasoning,
so inspect that separately. Freeze the selection before any follow-on execution.

## Earlier records

The first [offline review](offline-review-2026-11-01.md) records seven decision
reviews and one run of a local helper, with content hashes. It does not claim a
live application test. Its original case set is kept in `archive/`; current
coverage checks use the cases inside each skill folder.

Approach informed by [Agent Skills evaluation guidance](https://agentskills.io/skill-creation/evaluating-skills)
and [Anthropic's outcome-based agent evaluation guidance](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).
