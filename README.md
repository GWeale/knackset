<h1><img src="assets/knackset-mark.svg" alt="" width="32" height="32"> Knackset</h1>

**Follow a question. Make something worth keeping.**

Portable agent skills for investigation, creative direction, writing and learning.
Bring a question, a folder of references or a project that has stalled.

[Start with a skill](#start-with-what-you-have) · [See worked examples](examples/README.md) · [Browse the catalog](docs/catalog.md)

## Start with what you have

- **[Rabbit Hole](skills/rabbit-hole/SKILL.md)** · Follow a puzzling claim, test
  competing explanations and write an account with a source trail.
- **[Reference Remix](skills/reference-remix/SKILL.md)** · Turn a folder of
  references into an original direction and a finished artifact.
- **[Unstick Project](skills/unstick-project/SKILL.md)** · Find a useful way
  forward on stalled work and make the first proof.

<details>
<summary>Six more ways in</summary>

- **[Idea Pressure Test](skills/idea-pressure-test/SKILL.md):** Test the assumption
  that could change whether an idea is worth pursuing.
- **[Story Mining](skills/story-mining/SKILL.md):** Find an angle in notes or
  interviews and finish a piece that sounds like its author.
- **[Demo Director](skills/demo-director/SKILL.md):** Decide what to show, what
  to say and where to cut.
- **[Learn by Making](skills/learn-by-making/SKILL.md):** Build a small experiment
  to understand how something works.
- **[Decision Archaeology](skills/decision-archaeology/SKILL.md):** Recover the
  reasoning behind an inherited choice before reversing it.
- **[Generative Series](skills/generative-series/SKILL.md):** Make a visual family
  with an editable generator and reproducible inputs.

</details>

These are original draft methods. [Worked examples](examples/README.md) show the
outputs; package notes explain what has been checked. Office and browser workflows
are on the [utility shelf](docs/catalog.md).

## See what came out

<a href="examples/field-kit/reference-remix/night-orchard.png"><img src="examples/field-kit/reference-remix/night-orchard-small.png" alt="Night Orchard: a poster made by Reference Remix" width="240"></a>

Reference Remix made this poster from three fictional reference descriptions.
The [worked examples](examples/README.md) include an investigation with a source trail
and a runnable curve experiment, with their inputs and checks.

[Watch the 80-second preview](examples/creative-preview/README.md) · [Read the Field Notes case study](examples/field-notes/CASE-STUDY.md)

## A source shelf with a point of view

The [source shelf](docs/source-shelf.md) examines individual skills from
Impeccable, gstack, Pawel Huryn, Corey Haines, Anthropic, Baoyu, K-Dense, Cursor's
pstack, Humanizer, and Superpowers. Each pick links to the file we read at a
specific revision, its license, the useful mechanism, and the baggage we would
leave behind.

This is a collection to explore and adapt. We do not bundle upstream skills or
silently relabel their work as ours. Knackset's original procedures have their
own scope and judgments. [How we curate](docs/workflow-contract.md).

## Try one

Read the chosen `SKILL.md`, then give it to an agent with the material it needs.
You can try Rabbit Hole immediately with the bundled fictional cinema sources:

> Read `skills/rabbit-hole/SKILL.md`. Use only the supplied
> `skills/rabbit-hole/evals/files/cinema-sources.md` to investigate the cinema story.
> Write an explanation for a curious local reader and show the evidence that matters.

No account connection is needed for this example. From a Knackset checkout,
copy one complete package into an existing project with Python 3.10+:

```bash
python3 scripts/install_skill.py rabbit-hole --project /absolute/path/to/your-project --dry-run
python3 scripts/install_skill.py rabbit-hole --project /absolute/path/to/your-project
```

The command checks the source, preserves the license and resources, refuses an
existing destination, and verifies the copied files. Use `--check` to compare an
installed copy with this checkout. [Install and verify a skill](docs/installation.md).

To browse the two collections:

```bash
python3 scripts/catalog.py list --collection field-kit
python3 scripts/catalog.py search "sources" --collection utilities
```

Installation supplies a method; your host supplies tools and permissions.
Use the [field-test guide](docs/try-the-field-kit.md) to try one on your own work
and report what you kept, changed or discarded.

## Bring an interesting job

A good contribution starts with a task you would actually want help with, a
non-obvious decision, and a result someone can inspect. Show us the messy input
and what a useful finish looks like. A longer prompt or another connector is not
by itself a new capability.

[Propose a skill](https://github.com/GWeale/knackset/issues/new?template=workflow-request.yml) · [Report a failure](https://github.com/GWeale/knackset/issues/new?template=bug-report.yml) · [Contribution guide](CONTRIBUTING.md)

## Evidence and development

[![CI](https://github.com/GWeale/knackset/actions/workflows/ci.yml/badge.svg)](https://github.com/GWeale/knackset/actions/workflows/ci.yml)

The field kit has [worked examples and scoped reviews](examples/README.md),
alongside a [small paired pilot on actual launch work](examples/launch-study/README.md).
Those observations are task-specific: one slight preference each way and one tie.
The [later repeated comparisons](evals/results/field-round-20261102/RESULTS.md) use
real NPS figures and USGS references and retain the limits of a single reviewer.
Neither round establishes general improvement. The older utilities retain their
[dated offline records](evals/results/README.md). Those records do not validate
the creative methods. [Provenance](docs/provenance.md) explains the distinction
between authored cases, source research and actual executions.

Python helpers use the standard library. The [experimental local runner](docs/runtime.md)
and [historical comparisons](evals/results/README.md) are available for people
working on execution and recovery; they are supporting tools for this collection.

```bash
python3 scripts/validate.py
python3 scripts/catalog.py render --check
python3 -m unittest discover -s tests -v
```

[Provenance](docs/provenance.md) · [Full catalog](docs/catalog.md) · [MIT license](LICENSE)
