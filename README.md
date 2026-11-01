![Knackset — Agent skills with follow-through.](assets/knackset-social.jpg)

# Knackset

**Agent workflows that check what actually happened.**

Practical, open-source skills for agents connected to your browser, mail,
calendar, and documents. They describe the task, the tricky decisions, and the
saved result to check before calling it done.

[![CI](https://github.com/GWeale/knackset/actions/workflows/ci.yml/badge.svg)](https://github.com/GWeale/knackset/actions/workflows/ci.yml)
[MIT](LICENSE) · [Browse the skills](docs/catalog.md) · [Contribute a failure case](https://github.com/GWeale/knackset/issues/new?template=bug-report.yml)

## The row was saved. The response timed out.

Retrying the append would create a duplicate. The useful next step is to inspect
the saved row. Knackset captures that kind of follow-through in reusable workflows.

See the distinction in a scripted, synthetic demo. Python 3.10+, no packages or
accounts required:

```bash
git clone https://github.com/GWeale/knackset.git
cd knackset
python3 scripts/demo.py
```

The demo performs both paths against isolated state: reconciling leaves one row;
blindly retrying creates two. It cleans up afterward. This illustrates the
workflow; it is not an agent benchmark. [Let your agent try the fixture](evals/README.md#run-a-forward-evaluation).

## Start with a workflow

| Task | The detail the skill handles |
| --- | --- |
| [Update Google Sheets](skills/google-sheets-update/SKILL.md) | Recheck row identity; reconcile an uncertain append before retrying |
| [Triage Gmail](skills/gmail-triage/SKILL.md) | Label matching messages without changing their starred thread neighbors |
| [Prepare or update a form](skills/web-form-update/SKILL.md) | Discover autosave before typing into a draft-only request |
| [Compose a Gmail reply](skills/gmail-draft-reply/SKILL.md) | Preserve recipients and thread; verify a saved draft after a timeout |

The [full catalog](docs/catalog.md) also covers calendars, Docs, research,
monitoring, reservations, briefings, PR review, and capturing a session as a skill.

## Install one skill

Your host agent needs file-based skill support and the relevant browser or
service tools. Each folder is a self-contained [Agent Skills package](https://agentskills.io/specification).

With the optional third-party [Skills CLI](https://github.com/vercel-labs/skills)
(Node.js 22.20+):

```bash
npx skills@1.7.4 add GWeale/knackset --skill google-sheets-update
```

Or copy the entire `skills/google-sheets-update/` folder into your host's supported
skills directory. The CLI command pins the installer, not repository contents;
host discovery and live integrations have not been tested here.

## Evidence

Four workflows have [stateful offline execution records](evals/results/README.md).
The baselines also passed: the current sample does not establish performance
gains or live service compatibility. Every package includes authored success,
boundary, and routing cases. Those inputs are separate from completed executions.

## Bring one failure your agent should recover from

A duplicate row, an autosaved draft, a wrong recipient: a concrete example is a
useful contribution. [Report a failure](https://github.com/GWeale/knackset/issues/new?template=bug-report.yml)
or [request a workflow](https://github.com/GWeale/knackset/issues/new?template=workflow-request.yml).
Use synthetic details; keep private histories and credentials out of submissions.
Maintainers apply the [contribution and evidence checks](CONTRIBUTING.md).

## Develop

Python 3.10+, standard library only. CI checks Python 3.10 and 3.14.

```bash
python3 scripts/validate.py
python3 scripts/catalog.py render --check
python3 -m unittest discover -s tests -v
```

Original, independent project. [Research and product comparisons](docs/product-alignment.md),
[provenance](docs/provenance.md), and [growth decisions](docs/scaling.md) document
the sources and limits. Original copyright notices are retained under the [MIT license](LICENSE).
