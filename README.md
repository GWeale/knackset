<img src="assets/icon.svg" width="64" height="64" alt="">

# Muse-Skills

Portable, open-source skills for agents that work across websites. Each skill
captures a task, the evidence needed to finish it, and how to recover when the
website behaves differently. The agent supplies the browser or service tools.

This is an independent project, unaffiliated with Meta Muse or Grok Bot. It is a
workflow library, not a replacement for their runtime, models, memory, scheduling,
account isolation, or authentication.

## Use a skill

Read the relevant `skills/<name>/SKILL.md`, or copy that entire folder into your
agent's supported skills directory. Keep any bundled references and scripts with
it. These files use the [Agent Skills format](https://agentskills.io/specification);
installation and automatic discovery depend on the host agent. No specific host
or consumer app integration has been tested yet.

For an agent that can read files, a first invocation can be:

> Read skills/web-research/SKILL.md and use it to compare these three public sources.

The application skills work independently; loading every skill is unnecessary.
Use [web-task-execution](skills/web-task-execution/SKILL.md) for general browser
handling and tool adaptation.

| Skill | Work it handles | Basis |
| --- | --- | --- |
| [web-task-execution](skills/web-task-execution/SKILL.md) | Choose an authorized browser/session, act, and verify results | Sanitized session lessons + research |
| [web-form-update](skills/web-form-update/SKILL.md) | Edit a specific form or settings record without duplicate submissions | Authored workflow + research |
| [web-research](skills/web-research/SKILL.md) | Gather current primary evidence and resolve conflicting claims | Authored workflow |
| [product-shortlist](skills/product-shortlist/SKILL.md) | Compare exact offers, total cost, condition, and uncertainty | Authored workflow |
| [gmail-triage](skills/gmail-triage/SKILL.md) | Review scoped mail and perform requested organization | Authored workflow + official Gmail docs |
| [google-sheets-update](skills/google-sheets-update/SKILL.md) | Update or append bounded rows, preserve formulas, verify saved cells | Authored workflow + official Sheets docs |
| [github-review](skills/github-review/SKILL.md) | Review a specific PR revision and prepare evidence-based findings | Authored workflow + official GitHub docs |
| [session-to-skill](skills/session-to-skill/SKILL.md) | Distill a private session into a reusable, sanitized draft | Authored authoring workflow |

All eight skills are **drafts without live application validation**. Passing the
repository checks proves structural integrity and local helper behavior, not that
a model can complete every website task. See [provenance](docs/provenance.md) and
the [evaluation procedure](evals/README.md). A first independent
[offline evaluation](evals/offline-review-2026-11-01.md) records decision checks
and a local draft-generation run, with their limits.

## Turn a session into a draft

Keep raw histories outside the checkout. Review and generalize a task into the
[curated record format](skills/session-to-skill/references/record-format.md), then run:

```bash
python3 skills/session-to-skill/scripts/create_skill.py \
  skills/session-to-skill/assets/session-record.example.json
python3 scripts/validate.py --skill .local/drafts/example-profile-update
```

The example is synthetic. The generator writes to ignored `.local/drafts/`,
refuses overwrites, and does not read agent databases or publish anything. It does
**not** detect every secret or redact private prose. Review a draft before moving
it into `skills/` and adding it to the catalog.

## Develop and verify

Python 3.10+ is sufficient; no third-party packages are required.

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

The [workflow contract](docs/workflow-contract.md) defines evidence, authorization,
and recovery conventions. [Research](docs/research.md) records primary sources and
reuse limitations, checked on 2026-11-01. [Contributing](CONTRIBUTING.md) explains
how to add one grounded workflow. Original project content is MIT licensed;
linked third-party content retains its own terms.
