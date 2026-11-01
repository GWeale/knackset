# Contributing a workflow

Start with one real task and a finish condition another agent can observe. Read
the [contract](docs/workflow-contract.md), then add a folder under `skills/` using
the Agent Skills format. Keep the skill independently usable and link only the
references that its workflow needs.

Describe intended outcomes and application semantics. Discover current controls
from the live page; do not record a click sequence, session element ID, or cookie.
Honor tool policies in the host environment. A portable skill must not invent
tools, bypass access controls, or grant itself permission for an external action.

Private histories are input to a local analysis, never a contribution artifact.
Replace identities and task data with synthetic examples; remove identifiers,
private links, transcripts, screenshots, and credentials. Generalize the failure
and recovery lesson. A pattern scan cannot establish that text is safe to publish.

Add a `catalog.json` entry with category, focused tags, evidence basis and honest
validation state. Keep the description canonical in `SKILL.md`; do not duplicate
it in catalog metadata. Bundle the root MIT notice as `LICENSE.txt` in the package.

Add `evals/evals.json` inside the skill with `skill_name` and an `evals` list. Each
case has a globally unique `id`, `kind` (`success`, `boundary`, or `routing`),
`prompt`, synthetic starting `context`, `expected_output`, nonempty `assertions`,
`forbidden` action list and `files` list. Include all three kinds; fixture paths
are relative to the skill folder and must stay inside it. Do not pre-supply the
desired readback when the agent should choose and execute the observation.

Run `python3 scripts/catalog.py render` after metadata/description changes, then
all three checks from the README. [Evaluation guidance](evals/README.md) explains
how to record actual outputs and compare a candidate with a baseline. A newly
authored case is not execution evidence.

Use `draft` until the scope of evidence supports promotion. For `offline-reviewed`,
attach a structured `sandbox` execution record with a successful `with-skill` run,
nonempty boolean assertions and the current package fingerprint. For `live-tested`,
the record must use `live` mode and a specifically authorized live test. Include
date, runtime, task scope and limitations. The validator checks consistency and
fingerprints, not the truth of a contributor's claim. When changing a promoted
package, rerun the relevant evaluation or return it to draft.

Original contributions use the repository's MIT license. Link to source material
and verify the license of any reused file separately; an accessible repository,
an aggregation page, or a paper does not itself grant redistribution rights.

Use the GitHub workflow-request or failure form to suggest coverage or share a
minimal synthetic reproduction. See the [growth plan](docs/scaling.md) for intake
priorities and the [security note](SECURITY.md) for sensitive reports.
