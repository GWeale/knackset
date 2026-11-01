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

Add a `catalog.json` entry with its evidence basis and honest validation state.
Add a synthetic scenario to `evals/scenarios.json` covering both a useful outcome
and a plausible boundary or failure. Run both repository checks from the README.
For browser validation, use an explicitly authorized test account and record the
dated result, skill revision, capabilities, observations, and unresolved limits.

Original contributions use the repository's MIT license. Link to source material
and verify the license of any reused file separately; an accessible repository,
an aggregation page, or a paper does not itself grant redistribution rights.
