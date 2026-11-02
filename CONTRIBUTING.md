# Contributing to Knackset

Start with one task and a way to tell whether it finished. You can
[report a failure](https://github.com/GWeale/knackset/issues/new?template=bug-report.yml),
[request a workflow](https://github.com/GWeale/knackset/issues/new?template=workflow-request.yml),
or contribute a skill. A small example with made-up data is enough to start a
discussion.

## Write one focused skill

Read the [workflow contract](docs/workflow-contract.md) and
[provenance notes](docs/provenance.md). Start with the [complete accepted example](docs/authoring-example.md):
it includes a skill, license, catalog entry, and three authored cases, with exact
copy and check commands. Keep everything the skill needs inside its folder.

Knackset accepts a smaller frontmatter subset than the general
[Agent Skills format](https://agentskills.io/specification): exactly the flat
string fields `name`, `description`, and `license`, with `license: MIT`. Use
single-line JSON double-quoted strings when values contain punctuation such as
a colon. Nested metadata, block scalars, extra fields, and single-quoted YAML
strings are not accepted here. The name must match its folder and use 1–64
lowercase ASCII letters/digits with single internal hyphens; the description
must contain 1–1024 characters. Put tool requirements in the skill body.

Explain the intended outcome, the application's relevant behavior, and the
decisions the agent must make. The agent should discover current page controls
as it works; saved click sequences and session element IDs will go stale. Use
only tools and permissions available in the host environment. A skill cannot
invent a tool or authorize an external action on the user's behalf.

Add a `catalog.json` entry with a category, focused tags, evidence basis,
validation status, `live_validation`, and `evidence`. Keep the description in
`SKILL.md`; the catalog reads it from there. Copy the root MIT notice into the
package as `LICENSE.txt`, and link `VALIDATION.md` from the skill so an installed
copy retains its limits. Set catalog `validation_note` to `VALIDATION.md` and keep
its `Status: **draft**.` line aligned with the catalog until evidence qualifies.

## Add cases the skill should handle

Create `evals/evals.json` inside the skill with `skill_name` and an `evals` list.
Include at least one case of each kind: `success`, `boundary`, and `routing`.
Routing cases check whether the agent recognizes a task that needs a different
workflow.

Each case needs:

- A globally unique `id` and a `kind`.
- A `prompt` and synthetic starting `context`.
- An `expected_output` and nonempty `assertions`.
- A `forbidden` action list and a `files` list.

Fixture paths are relative to the skill folder and must stay inside it. When the
agent needs to read the saved result, let it perform that read; do not supply the
answer in the starting context.

## Match the status to the evidence

New skills start as `draft`. To use `offline-reviewed`, attach a structured
`sandbox` execution record with a successful `with-skill` run, nonempty boolean
assertions, and the current package fingerprint. `live-tested` requires a `live`
record from a specifically authorized live test. Include the date, runtime, task
scope, and limitations.

The [evaluation guide](evals/README.md) explains how to record outputs and compare
a candidate with a baseline. Authored cases alone are not execution evidence.
The validator checks record consistency and fingerprints; it cannot establish
that a contributor's reported execution happened. If you change a promoted
package, rerun the relevant evaluation or return its status to `draft`.

## Check the change

After changing catalog metadata or a skill description, regenerate the catalog
and run the repository checks:

```bash
python3 scripts/catalog.py render
python3 scripts/validate.py
python3 scripts/catalog.py render --check
python3 -m unittest discover -s tests -v
```

In the pull request, say what changed, which checks ran, and what remains untested.
See the [growth plan](docs/scaling.md) for coverage priorities.

## Keep sources clear and private data out

Original contributions use the repository's MIT license. Link to your sources
and check the license of each reused file. A public repository, aggregation page,
or paper does not by itself grant permission to redistribute its contents.

If a private session revealed a useful failure, contribute the lesson with
made-up identities and task data. Do not include histories, identifiers, private
links, transcripts, screenshots, or credentials. Automated scans cannot replace
reviewing the material yourself. Use the [security reporting guidance](SECURITY.md)
for sensitive concerns.
