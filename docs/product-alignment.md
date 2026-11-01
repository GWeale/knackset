# Product alignment, without claiming private implementation parity

Sources checked 2026-11-01. The goal is an open library that can complete the same
**kinds of tasks** documented by personal-agent products. That does not establish
identical internal instructions, runtime behavior, native import, or approval by a
vendor. No private product prompt or skill has been extracted or copied.

## Public evidence and implementation boundary

| Product | Public evidence | What this library can claim |
| --- | --- | --- |
| Grok Bot | Saved procedures, demonstration-generated drafts, skills shared across Bots, scheduled/event routines. [Official guide](https://docs.x.ai/grok-bot/skills-routines-and-automations) | Comparable task procedures and a capture/review loop; consumer import and runtime integration untested |
| Meta Muse | Connector-specific skills, a browser, persistent environment, and external action controls. [Architecture](https://research.meta.ai/blog/security-and-safety-for-ai-agents-our-approach-with-muse) | Workflow design informed by public requirements; consumer `SKILL.md` import not established by reviewed sources |
| Instinct | Text/call assistant that uses phone/computer tools for errands. [Official site](https://instinct.com/) | Outcome inspiration; no skill import, calling, or tool-binding compatibility demonstrated |

The similar names Grok Build and Muse Code refer to separate coding products;
their skill support does not prove consumer-agent support. Standard Agent Skills
packaging likewise does not make browser tools interchangeable.
[Agent Skills format](https://agentskills.io/specification)

## Concrete workflow coverage

These are mappings from public examples to independently authored packages,
not assertions that the packages passed the vendors' tests.

| Documented job | Relevant packages | Distinctive behavior |
| --- | --- | --- |
| Priorities and family coordination | `daily-briefing`, `calendar-coordination` | Bounded source coverage, time zones, occurrence identity, separate event invitations from suggestions |
| Ongoing goal/source tracking | `recurring-monitor` | Baseline, state delta, duplicate suppression, missing-source handling, explicit scheduler capability |
| Expense administration | `expense-reconciliation` | Receipt matching, exact money/currency handling, unmatched items, no implied reimbursement approval |
| Browser work and staging bugs | `web-task-execution`, `web-form-update`, `browser-bug-reproduction` | Current observation, account/target identity, autosave semantics, reproducible evidence |
| Mail and office tasks | `gmail-triage`, `gmail-draft-reply`, `google-docs-update`, `google-sheets-update` | Message scope, draft identity, document revisions, current row keys and saved-result checks |
| Research and booking | `web-research`, `product-shortlist`, `travel-reservation` | Exact offer, full known price/terms, quoted/pending/confirmed distinctions and recovery |
| Reusable methods | `session-to-skill` | Curated demonstrations, scoped lessons, counterexamples and evidence before promotion |

Examples come from [Grok Bot roles](https://docs.x.ai/grok-bot/use-cases),
[Meta's design account](https://introducing.muse.ai/), and [Instinct](https://instinct.com/).

## Match observable requirements

Muse's connector guidelines emphasize complete supported task lifecycles,
accurate total prices and terms, clear read/write effects, authorization, confirmed
outcomes, and status reconciliation before retrying. Our travel, form, mail, and
document procedures use those design principles. Applying them is not connector
approval or permission to execute an action. The host still enforces its own
controls. [Muse connector requirements](https://platform.muse.ai/docs)

Grok Bot's guide recommends making a one-time method reliable before saving and
automating it. The teaching result remains a draft; branches and failures still
need authoring. Our capture and monitoring workflows use that progression, with
no bundled background observer or scheduler. [Skills and routines](https://docs.x.ai/grok-bot/skills-routines-and-automations)

Native integration claims require a named product/version, supported import/tool
path, scoped execution, independent outcome evidence, and documented limits.
Until then, compatibility is limited to the package format and observed test seam.
