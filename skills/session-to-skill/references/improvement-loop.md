# Improve a workflow from small, scoped lessons

Use this reference when authorized demonstrations, evaluations, or corrections
reveal a reusable conditional lesson. A complete workflow can stay a single
skill; smaller lessons help decide which instruction to change, not which new
skill folder to create.

Here an atomic lesson means an authored trigger, action, and evidence boundary.
Do not equate this concept with a product named Instinct or claim to reproduce
that product's memory, learning, or integration features. Product behavior needs
its own sources. The [lesson example](../assets/lesson.example.json) is a local
project convention, not a standard skill manifest or executable memory format.

## Extract a candidate

1. Inspect only the supplied or otherwise authorized task evidence. Separate an
   assistant's claim, a user correction, an observed action, and resulting state.
2. State the trigger narrowly enough to distinguish when the lesson helps. Record
   prerequisites, affected operation, and cases it does not cover.
3. Write the action and an observable acceptance check. Preserve existing user
   authorization and host policy; a repeated lesson cannot grant broader access.
4. Record the actual supporting observations and their limits. Use synthetic
   examples in public artifacts. A source summary is not a replay or independent
   resulting-state observation.
5. Seek a plausible counterexample: another account state, an idempotent API,
   autosave, a conflicting record, or a task that shares words but has a different
   finish condition. Narrow or discard the lesson if it overgeneralizes.

The optional `confidence` label is a review heuristic such as `tentative` or
`supported-in-scope`, accompanied by a reason. It is not a calibrated probability,
a security classification, permission, or proof of browser compatibility. Many
similar assertions in one session are not independent demonstrations.

## Evaluate and integrate

Create one positive fixture and one counterexample or boundary case. Test the
changed procedure in a fresh context, compare actual actions/artifacts with the
rubric, and retain failures as well as successes. A decision on supplied state
establishes decision behavior; only executed observations can establish tool or
browser behavior. Compare with the old instruction or no skill before claiming
improvement.

Integrate a supported lesson into the relevant skill or conditional reference.
Prefer replacing a vague or contradicted instruction over appending another
universal rule. Keep the public skill independently usable; private evidence can
remain outside the checkout and its content must not become a required resource.

Keep a candidate unvalidated until the available evidence supports its stated
scope. Do not ingest raw histories autonomously, attach file watchers, retrain a
model, install the lesson, or promote catalog status as a side effect of capture.
Those are separate operations with their own requested scope.

## Retire or supersede

Revisit a lesson when its prerequisite disappears, a real counterexample defeats
its action, the site's supported operation changes, or a narrower replacement
performs better. Mark the lesson retired/superseded with the reason and replacement
when useful; preserve the historical evidence and remove the obsolete instruction
from active guidance. Do not keep stacking exceptions onto a rule that no longer
helps.

Approach informed by [Agent Skills authoring guidance](https://agentskills.io/skill-creation/best-practices)
and [evaluation guidance](https://agentskills.io/skill-creation/evaluating-skills),
checked 2026-11-01. This reference does not implement a learning runtime.
