# Paired comparison protocol

Authored 2026-11-01. This is a proposed experiment protocol, not a completed
comparison or a claim of improved performance. Existing historical records are
not sufficient for this protocol. Do not backfill missing observations from guesses.

## Freeze before running

Choose runnable cases with ordinary success and consequential failure boundaries.
Freeze the package, task text/context/inputs, fixture/grader sources, tools and
permissions, runtime/model/version/settings, rubric, trial count, budget and stop
rules. Hash the exact task packet and tool/settings manifest with SHA-256. Include
model settings in the tool/settings manifest even if the model name is unchanged.
Assign a cohort name and unique trial ID to each matched pair. Predeclare at least
five repeated pairs per case as a practical starting point, not a power guarantee;
report the sample size and uncertainty rather than assuming five is sufficient.

Randomize variant execution order within each pair and case order across trials;
save the seed, schedule and deviations before inspecting outcomes. Use fresh
agent contexts and isolated, identically initialized workspaces for both variants.
The baseline must receive no skill body or prior solution. Both receive the same
task, available operations, limits and context. Keep judges' criteria, fixture
internals and prior runs out of execution-agent context. Do not reuse a context
between variants or let one agent read the other's trace. Follow the host's
actual agent-delegation authorization policy; this document does not authorize
starting agents, installing tools or using accounts.

## Preserve and judge the work

Use the binding and exporter procedure in [the evaluation guide](../evals/README.md).
Keep failures, timeouts, exhausted budgets and incomplete runs. Judge saved state,
action order and the final response, not persuasive explanations alone. A separate
judge should receive anonymous outputs with variant labels and skill references
redacted, a fixed rubric and saved-state evidence. Freeze judgments before revealing
variants; record unavoidable clues and any unblinding. Automated graders cannot
establish context isolation or judge blinding.

Keep exported originals immutable. Use `--prepare` to create comparison copies
without manually calculating hashes. Before either agent starts, save the exact
shared task text/context/inputs to `.local/task-packet.txt`; capture `describe`
output using `python3 evals/sandbox.py describe WORKSPACE > .local/task-packet.txt`
when that is the complete shared task. Add any shared evaluator instructions and
input contents before freezing it. Save the actual tool permissions, command
interface/version, runtime/model settings and budgets to `.local/tools.txt`.
Both variants must use these same frozen files; skill-loading instructions are
the treatment and are kept separately. After normal init/execution/export:

```bash
python3 scripts/compare_evals.py .local/baseline/report.json --prepare \
  --task-packet .local/task-packet.txt --tool-manifest .local/tools.txt \
  --cohort timeout-study --trial sheets-01 --baseline-no-skill \
  --output .local/baseline-comparison.json
python3 scripts/compare_evals.py .local/candidate/report.json --prepare \
  --task-packet .local/task-packet.txt --tool-manifest .local/tools.txt \
  --cohort timeout-study --trial sheets-01 \
  --output .local/with-skill-comparison.json
```

Preparation refuses overwrites, retains the original exported evidence, and
records its hash. `--baseline-no-skill` is the experimenter's explicit attestation,
not an automatic finding about the agent's context. Preparation adds metadata;
the subsequent pair comparison performs current-source and comparability checks.
The manifests must describe the run as executed, not a reconstructed ideal setup.
Do not hash a convenient unrelated file and call it the task packet. Retain the source path/hash in your experiment log.
Required fields are `cohort`, `trial`, `task_sha256`, and `tools_sha256`. Baseline
runs must additionally declare `baseline_kind: "no-skill"` inside `comparison`.
The cohort/trial pair identifies one baseline and one with-skill run; use unique
trial IDs across cases within a cohort. Runtime, model, case, scenario, task/tool
hashes and assertion names must agree within a pair. A changed rubric needs a
new cohort. Exported `workspace_sha256` values must be present and unique.

Optional `comparison.metrics` may contain `errors` (nonnegative integer),
`recovered` (boolean), and `cost_usd` (finite nonnegative number). Supply a nonempty
`comparison.measurement_source` whenever metrics are present. Predeclare error
categories and recovery criteria, retain judge evidence, and count errors using
that rubric. Recovery means a judged recovery opportunity and successful handling;
omit it when no opportunity was presented, rather than recording a false failure.
Cost requires an actual meter or billing observation for the complete run under
the same accounting scope, including skill loading and retries. Do not infer it
from trace length or treat a missing value as zero. Partial cost is not total cost.

For example, metadata on a genuinely measured no-skill run would have this shape
(the placeholders below must be replaced; they are not an execution record):

```json
{
  "cohort": "frozen-experiment-name",
  "trial": "case-name-repeat-01",
  "task_sha256": "REPLACE_WITH_EXACT_TASK_PACKET_SHA256",
  "tools_sha256": "REPLACE_WITH_TOOLS_AND_SETTINGS_MANIFEST_SHA256",
  "baseline_kind": "no-skill"
}
```

## Compare and report

```bash
python3 scripts/compare_evals.py .local/baseline-comparison.json \
  .local/with-skill-comparison.json > .local/comparison.json
```

The standard-library CLI accepts schema-1 sandbox execution records, checks
current package and fixture/grader fingerprints and refuses stale, unmatched,
duplicate or incomparable inputs. It preserves failed completions. It reports
paired completion and measured errors/recovery/cost; incomplete metric pairs are
explicitly unmeasured. Exit 0 means the comparison is structurally valid, even if
tasks failed; exit 2 means invalid input. Current-source checking deliberately
prevents presenting an old run as evidence for a modified package.

Report per-case results, all exclusions/deviations, denominators for each metric,
paired disagreements, measured costs and limits. The output is descriptive; it
provides no significance test or causal superiority verdict. More repetitions,
independent tasks and a justified analysis are needed for broader claims. A
manifest/hash is a binding claim, not proof that agents obeyed the protocol.
Historical previous-skill baselines cannot be relabeled as no-skill controls.
No live service or browser reliability follows from offline fixture success.
