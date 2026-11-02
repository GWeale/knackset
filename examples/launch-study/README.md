# Three real launch tasks, with and without the skill

Executed 2026-11-02 UTC. Six completed fresh-context runs form three matched
artifact pairs on Knackset's own launch work. These are actual project inputs,
not invented customers or fictional session records. The visual references
include earlier fictional artworks, explicitly identified as such.

This is an exploratory pilot: one pair per task, one project, one model, no
measured billing cost or complete token/timing telemetry. It does not satisfy
the five-repeat [sandbox study protocol](../../docs/comparison-protocol.md),
establish general improvement or promote a package.

## Inspect the work

| Task | Without the Knackset skill | With the skill |
| --- | --- | --- |
| Investigate whether existing evidence supports creative-quality claims | [Account](runs/rabbit-hole/baseline/account.md) and [source trail](runs/rabbit-hole/baseline/source-trail.md) | [Account](runs/rabbit-hole/with-skill/account.md) and [source trail](runs/rabbit-hole/with-skill/source-trail.md) |
| Make a real launch card from the icon and existing visual references | [Card](runs/reference-remix/baseline/card.png), [editable SVG](runs/reference-remix/baseline/card.svg), [decisions](runs/reference-remix/baseline/decisions-and-checks.md) | [Card](runs/reference-remix/with-skill/card.png), [editable SVG](runs/reference-remix/with-skill/card.svg), [decisions](runs/reference-remix/with-skill/notes.md) |
| Finish a local creative demo despite account/tester dependencies | [Self-contained HTML](runs/unstick-project/baseline/demo.html), [packet](runs/unstick-project/baseline/README.md) | [Packet and artwork](runs/unstick-project/with-skill/README.md), [first task](runs/unstick-project/with-skill/FIRST-TASK.md) |

The [captioned preview](../creative-preview/README.md) presents these saved
outputs. It is assembled afterward and is not a recording of their execution.

## Read the result

[Results and decision](RESULTS.md) · [Anonymous review](review.md) ·
[Variant key and original judgment hashes](unblinding.json). One slight preference
favored the skill, one favored the baseline, and one pair tied. All six were
usable; this pilot did not establish a consistent advantage.

## What was frozen

The [manifest](freeze.json) records source revision, current full-package
fingerprints, input hashes, task hashes, runtime/settings, seed and within-pair
order. Each agent read the same supplied input snapshot and task; the skill
body was the treatment. Baselines were instructed not to read a Knackset skill
body. Output directories and contexts were separate. This is instructed isolation
on a shared filesystem, not a hard sandbox or proof of universal tool equivalence.

- [Investigation prompt](rabbit-hole-task.txt)
- [Launch-card prompt](reference-remix-task.txt)
- [Stalled-launch prompt](unstick-project-task.txt)
- [Frozen rubric and decision rule](rubric.json)
- [Execution deviations](execution-deviations.md), including one initial capacity
  failure retried with unchanged settings.

All final outputs are retained, including the version not selected for any later
use. [Publication hashes](publication.json) distinguish original outputs from
link-normalized presentation copies. Raw Markdown inputs have a `.md.txt` suffix
to preserve historical text without treating its old links as current project
documentation. Their bytes and hashes are unchanged.

## Input shelf

- [Repository README](inputs/README.md.txt) and [examples index](inputs/examples/README.md.txt)
- [Execution index](inputs/evals/results/README.md.txt) and [historical utility comparison](inputs/evals/results/comparison-final-20261101/REPORT.md.txt)
- [Published alpha snapshot](inputs/published-alpha.md.txt)
- [Installation guide snapshot](inputs/docs/installation.md.txt)
- [Original icon](inputs/assets/knackset-mark.svg), [Night Orchard](inputs/examples/field-kit/reference-remix/night-orchard.svg), and [Held Between](inputs/examples/expansion/generative-series/overview.svg)

The snapshot is intentionally narrower than the repository. Missing original
reference studies or underlying historical traces remain missing for the trial
agents even though a coordinator may find them elsewhere later.

## Review limits

A fresh independent judge received anonymous pairs, the original prompts, inputs
and frozen rubric. Variant labels, package bodies, mapping, previous discussion
and parent conclusions were withheld. Path-only substitutions supported anonymous
review. The judge's frozen judgment is recorded before the variant key is revealed.
Stylistic clues and one model judging its own provider's outputs can still bias
this process. Agent judgment is separate from actual human taste or usefulness.

All three packages remain draft. Outside-user feedback and host loading remain
separate checks. [Try a method on your own work](../../docs/try-the-field-kit.md).
