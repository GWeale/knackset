![Knackset](assets/knackset-mark.svg)

# Knackset

**A working collection for curious people who make things.**

Investigate a strange story. Find the angle in a pile of notes. Turn a few
references into an original direction. Find out whether an idea deserves a month
of your life before you give it one.

Knackset studies good public skills and makes original methods from the parts
worth keeping. The point of view is in the choices: which evidence matters,
which reference earns its place, what to leave alone, and when to make something.

[Start with a skill](#start-with-what-you-have) · [See worked examples](examples/README.md) · [Explore the source shelf](docs/source-shelf.md) · [See the whole catalog](docs/catalog.md)

[![CI](https://github.com/GWeale/knackset/actions/workflows/ci.yml/badge.svg)](https://github.com/GWeale/knackset/actions/workflows/ci.yml) · [MIT](LICENSE)

## Start with what you have

| You have… | Use | Walk away with… |
| --- | --- | --- |
| A question you keep coming back to | [Rabbit Hole](skills/rabbit-hole/SKILL.md) | An investigation with a revealing turn, a source trail, and an answer that survives scrutiny |
| A folder of things you love | [Reference Remix](skills/reference-remix/SKILL.md) | An original creative direction and a usable artifact, with reasons behind the choices |
| An idea you might spend months on | [Idea Pressure Test](skills/idea-pressure-test/SKILL.md) | The assumption that matters, the strongest alternative, and a cheap way to learn what to do next |
| Notes, interviews, or a rambling draft | [Story Mining](skills/story-mining/SKILL.md) | A defensible angle and a finished piece that still sounds like its author |
| Something working that is hard to explain | [Demo Director](skills/demo-director/SKILL.md) | A demo built around what works: what changes, what to show, what to say, and where to cut |
| Something you want to understand | [Learn by Making](skills/learn-by-making/SKILL.md) | A small working experiment, an explanation tied to its behavior, and a next thing to try |
| An inherited choice nobody can explain | [Decision Archaeology](skills/decision-archaeology/SKILL.md) | The recorded reason, later explanations, and what matters before reversing it |
| A visual idea that needs a family | [Generative Series](skills/generative-series/SKILL.md) | A selected edition, editable generator, and enough inputs to reproduce it |
| A project going in circles | [Unstick Project](skills/unstick-project/SKILL.md) | One useful proof or experiment, with the next decision made clearer |

A few ways in:

> Use rabbit-hole. People keep saying this little cinema saved the neighborhood.
> Follow the story back to its sources and tell me what actually changed.

> Use reference-remix. I like field guides, old transit maps, and low-budget space
> films. Help me turn those references into a direction for my project.

> Use idea-pressure-test. I want to build this. Find the part I might be wrong
> about and a way to test it before I disappear into the build.

> Use story-mining. There is something good in these notes. Find the angle,
> preserve the odd bits that make them mine, and finish a piece worth reading.

The nine methods are original drafts, with raw example inputs and authored cases.
The [worked examples](examples/README.md) show what came out; package
notes and review records keep the limits visible. Earlier office and browser
workflows remain on the [utility shelf in the full catalog](docs/catalog.md).

## See what came out

[![Night Orchard: a poster made by Reference Remix](examples/field-kit/reference-remix/night-orchard-small.png)](examples/field-kit/reference-remix/night-orchard.png)

Reference Remix made this poster from three fictional reference descriptions.
Rabbit Hole found a changed denominator inside a tempting cinema success story.
Learn by Making produced a runnable curve experiment.
[Inspect all six outputs, their inputs, and what was checked](examples/README.md).

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

No account connection is needed for this example. For installation, copy the
**whole skill folder** into the directory your host supports. See the
[project-scoped copy recipe](docs/installation.md).

For Codex with the optional [Skills CLI](https://github.com/vercel-labs/skills):

```bash
cd /absolute/path/to/your-project
npx skills@1.7.4 add GWeale/knackset --skill rabbit-hole --agent codex --copy
```

The command selects the host and project, but follows repository contents. Use
the [full-commit recipe](docs/installation.md) when you need reproducible contents.
Installation supplies a method; your host supplies tools and permissions.

## Improve what is already here

Session capture now chooses whether to amend an existing method, write a distinct
skill, or keep no new instruction. Web Research handles bounded facts and
comparisons; Rabbit Hole investigates competing explanations. Bug reproduction
now tests reductions instead of calling an untried shorter list a minimal repro.
[Read the older-skill review and its checks](docs/refactor-review-20261101.md).

## Bring an interesting job

A good contribution starts with a task you would actually want help with, a
non-obvious decision, and a result someone can inspect. Show us the messy input
and what a useful finish looks like. A longer prompt or another connector is not
by itself a new capability.

[Propose a skill](https://github.com/GWeale/knackset/issues/new?template=workflow-request.yml) · [Report a failure](https://github.com/GWeale/knackset/issues/new?template=bug-report.yml) · [Contribution guide](CONTRIBUTING.md)

## Evidence and development

The first six methods have [supplied-input artifact trials](evals/results/field-kit-review-20261101.md).
The [expansion review](evals/results/expansion-review-20261101.md) records three
more worked examples, focused refactors and fresh routing. Neither wave has a
comparison baseline. The older utility
packages retain their [dated offline records](evals/results/README.md); those
records do not validate the new methods. Authored examples, inspected sources,
scripted fixtures and actual agent executions are labeled separately.

Python helpers use the standard library. The [experimental local runner](docs/runtime.md)
and [historical comparisons](evals/results/README.md) are available for people
working on execution and recovery; they are supporting tools for this collection.

```bash
python3 scripts/validate.py
python3 scripts/catalog.py render --check
python3 -m unittest discover -s tests -v
```

[Provenance](docs/provenance.md) · [Full catalog](docs/catalog.md) · [MIT license](LICENSE)
