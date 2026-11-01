<img src="assets/icon.svg" width="64" height="64" alt="">

# Muse-Skills

**Personal-agent workflows that verify what they change.** Original, MIT-licensed
skills for browser tasks, mail, calendars, documents, research, and repeatable work.
They run through the tools your agent already has.

[![CI](https://github.com/GWeale/muse-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/GWeale/muse-skills/actions/workflows/ci.yml)

Inspired by publicly documented workflows in Grok Bot, Meta Muse, and Instinct.
This independent project is unaffiliated with those products. It does not contain
their private skills or claim native consumer-app import compatibility. Read the
[product alignment](docs/product-alignment.md) for the evidence and limits.

## Use a skill

Browse the [generated catalog](docs/catalog.md) and choose a task. Each
`skills/<name>/` folder is a self-contained [Agent Skills package](https://agentskills.io/specification)
with instructions, a license, and synthetic evaluation cases. Copy that whole
folder into your host's supported skill directory, or read its `SKILL.md` directly.

For an agent that can read files, a first invocation can be:

> Read skills/web-research/SKILL.md and use it to compare these three public sources.

Optional installation with the third-party [Skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills@1.7.4 add GWeale/muse-skills --list
npx skills@1.7.4 add GWeale/muse-skills --skill web-task-execution
```

That CLI version requires Node.js 22.20+ and defaults to project-scoped
installation. Even `--list` executes the external CLI. The version pins the
installer, not this repository's contents; inspect the package and host behavior
before use. These commands are documented upstream, not an integration test here.

## Find a workflow

- **Browser work:** [operate and recover](skills/web-task-execution/SKILL.md),
  [edit forms](skills/web-form-update/SKILL.md), [reproduce a bug](skills/browser-bug-reproduction/SKILL.md).
- **Personal and office work:** [mail triage](skills/gmail-triage/SKILL.md),
  [draft replies](skills/gmail-draft-reply/SKILL.md), [calendar coordination](skills/calendar-coordination/SKILL.md),
  [Docs edits](skills/google-docs-update/SKILL.md), [Sheets updates](skills/google-sheets-update/SKILL.md),
  [daily briefings](skills/daily-briefing/SKILL.md), [expense reconciliation](skills/expense-reconciliation/SKILL.md).
- **Research and decisions:** [source research](skills/web-research/SKILL.md),
  [exact offers](skills/product-shortlist/SKILL.md), [change monitoring](skills/recurring-monitor/SKILL.md),
  [travel reservations](skills/travel-reservation/SKILL.md), [PR review](skills/github-review/SKILL.md).
- **Learning:** [turn a session into a skill](skills/session-to-skill/SKILL.md),
  including scoped lessons, counterexamples, and replay before promotion.

```bash
python3 scripts/catalog.py list
python3 scripts/catalog.py search gmail
python3 scripts/catalog.py show calendar-coordination --json
```

Descriptions come from each `SKILL.md`; category, tags, provenance, and evidence
come from `catalog.json`. Loading every skill is unnecessary. Skills do not
supply account access, a browser runtime, a scheduler, or permission for new actions.

## What is actually tested?

Every package has authored success, boundary, and neighboring-task routing cases.
Those are test inputs, not claims of successful execution. The
[evaluation guide](evals/README.md) separates structural checks, stateful offline
execution, and live service validation. Catalog statuses require matching evidence
and a package fingerprint before promotion. No live consumer-app compatibility is
claimed. See the [skill analysis](docs/skill-analysis.md) for specific improvements.

The first [stateful execution record](evals/results/README.md) checks autosave
drafts, message-level labels, append recovery, and saved reply drafts. Baselines
also passed; this sample supports scoped behavior, not a general performance claim.

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

An optional [improvement loop](skills/session-to-skill/references/improvement-loop.md)
records one scoped trigger/action lesson, supporting observations, and
counterexamples. A lesson does not silently become a universal instruction or
authorize a background action.

## Develop and verify

Python 3.10+ is sufficient; no third-party packages are required.

```bash
python3 scripts/validate.py
python3 scripts/catalog.py render --check
python3 -m unittest discover -s tests -v
```

CI runs these checks on Python 3.10 and 3.14. No production dependencies, API
keys, or live accounts are required for local verification.

## Help grow the library

Contribute one useful workflow, a failing synthetic case, or an execution record.
[Contribution guidance](CONTRIBUTING.md) and the [growth plan](docs/scaling.md)
describe the intake and evidence gates. Use the GitHub workflow-request or failure
form; keep personal data and raw sessions out of submissions.

The [workflow contract](docs/workflow-contract.md) defines result and retry
conventions. [Research](docs/research.md) links primary sources and reuse limits.
[Provenance](docs/provenance.md) distinguishes observed session lessons from
authored procedures. Original project content is [MIT licensed](LICENSE);
linked third-party material retains its own terms.
