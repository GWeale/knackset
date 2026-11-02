# Skill catalog

Choose a method for the work you have. Read it before installing the whole package.
See [worked examples](../examples/README.md) and the [project copy command](installation.md).

```bash
python3 scripts/catalog.py list --collection field-kit
python3 scripts/catalog.py search "sources" --collection utilities
```

## Field kit

Original methods for investigation, creative work and learning.

| Skill | Category | Status | Tags | Description |
| --- | --- | --- | --- | --- |
| [demo-director](../skills/demo-director/SKILL.md) | creative | draft | demos, storyboards, proof | Turn a real product, working prototype, or creative artifact into an honest demo with a finished script, timed storyboard, and actual media when available tools permit. Use for walkthroughs, launch demos, and explainers that must show proof; not a trim-only video edit or a request to invent product capabilities. |
| [generative-series](../skills/generative-series/SKILL.md) | creative | draft | generative, series, curation | Create and curate a coherent visual series from generative rules, reproducible inputs, and deliberate variation. Use for families of prints, covers, tiles, or algorithmic artworks; not a single reference-led composition or a concept lesson. |
| [reference-remix](../skills/reference-remix/SKILL.md) | creative | draft | references, art-direction, originality | Turn visual references and a brief into distinct original art direction and a usable visual artifact. Use for reference synthesis, moodboards that need a decision, and artwork or design driven by several influences; not a routine edit inside an already settled visual system. |
| [story-mining](../skills/story-mining/SKILL.md) | creative | draft | writing, voice, story | Find an evidence-backed angle in interviews, transcripts, research notes, or rough drafts and turn it into a finished piece that preserves the speaker's voice. Use when the story is buried in source material; not punctuation-only editing or a request to summarize every source evenly. |
| [learn-by-making](../skills/learn-by-making/SKILL.md) | learning | draft | learning, experiments, artifacts | Learn an unfamiliar idea by building a small working artifact, making predictions, and using observed results to repair the mental model. Use for hands-on understanding with a concrete learning goal, not a task the user simply wants completed. |
| [idea-pressure-test](../skills/idea-pressure-test/SKILL.md) | product | draft | ideas, assumptions, experiments | Pressure-test a product or creative project idea with a fair case, contrary evidence, and a cheap test with decision criteria. Use for deciding whether an uncertain idea deserves more work; skip straightforward edits and requests to build an already chosen design. |
| [unstick-project](../skills/unstick-project/SKILL.md) | product | draft | projects, constraints, experiments | Recover progress on a stalled project by separating the intended outcome from the blocked approach and completing a small useful next artifact or experiment. Use when attempts keep circling a dependency or constraint; not a settled edit, a root-cause debugging request, or permission to bypass a real access boundary. |
| [decision-archaeology](../skills/decision-archaeology/SKILL.md) | research | draft | decisions, history, rationale | Reconstruct why a technical, product, or design choice was made from code, history, and notes, and explain what matters before reversing it. Use for inherited behavior, puzzling constraints, and disputed rationale; use ordinary code explanation or defect review when historical intent is not the question. |
| [rabbit-hole](../skills/rabbit-hole/SKILL.md) | research | draft | investigation, sources, explanations | Investigate a puzzling claim, trend, or story by tracing sources, testing rival explanations, and producing a readable account of what changed your understanding. Use for an open question worth digging into, not a quick lookup or a dossier on a private person. |

## Utilities

Supporting workflows for accounts, browsers and operational tasks.

| Skill | Category | Status | Tags | Description |
| --- | --- | --- | --- | --- |
| [web-form-update](../skills/web-form-update/SKILL.md) | browser | offline-reviewed | forms, autosave, profiles | Change specified profile, settings, or form values and verify persistence, including autosave and validation behavior. Use for bounded record edits; purchases, reservations, and outgoing messages need their specific workflow. |
| [web-task-execution](../skills/web-task-execution/SKILL.md) | browser | offline-reviewed | browser, recovery, accounts | Operate a requested website task or recover browser access using the correct account and tab context, then verify the result. Use for general browser handling when a more specific workflow does not fit; public-source research alone is excluded. |
| [browser-bug-reproduction](../skills/browser-bug-reproduction/SKILL.md) | developer | offline-reviewed | browser, bugs, reproduction | Reproduce a reported web UI failure in an authorized test environment and produce a minimal evidence pack with expected and observed behavior. Use for browser reproduction, not code review, implementation, or production incident changes. |
| [github-review](../skills/github-review/SKILL.md) | developer | offline-reviewed | github, pull-request, review | Review a specified GitHub pull request at its current head, inspect the diff and surrounding context, and prepare actionable findings with check status. Use for PR review; reviewing does not authorize comments, approval, pushes, or merging. |
| [session-to-skill](../skills/session-to-skill/SKILL.md) | learning | offline-reviewed | skills, learning, lessons | Extract a reusable decision from authorized work, then improve existing guidance or create a focused skill when the evidence warrants it. Use for deliberate workflow capture and skill authoring, not raw history export, automatic memory, installation or publication. |
| [travel-reservation](../skills/travel-reservation/SKILL.md) | personal | offline-reviewed | travel, reservations, booking | Prepare or complete an explicitly requested travel booking, change, or cancellation while tracking exact travelers, total price, terms, payment, and reservation status. Use for reservation lifecycle work, not a generic shopping shortlist. |
| [calendar-coordination](../skills/calendar-coordination/SKILL.md) | productivity | offline-reviewed | calendar, scheduling, timezones | Find meeting times or create, reschedule, and cancel scoped calendar events while preserving recurrence and invitations. Use for calendar coordination, not a general daily briefing or inbox review. |
| [daily-briefing](../skills/daily-briefing/SKILL.md) | productivity | offline-reviewed | briefing, priorities, digest | Build a source-linked daily brief from specified mail, calendar, task, or project sources, prioritizing deadlines and decisions with explicit coverage. Use for a bounded cross-source briefing, not an account-wide scan, message send, or recurring watch setup. |
| [expense-reconciliation](../skills/expense-reconciliation/SKILL.md) | productivity | offline-reviewed | expenses, receipts, reconciliation | Reconcile a specified expense set with receipts and a supplied policy, preserving currencies, refunds, and unresolved matches. Use for a review ledger or authorized reconciliation updates, not payment, tax advice, or general spreadsheet editing. |
| [gmail-draft-reply](../skills/gmail-draft-reply/SKILL.md) | productivity | offline-reviewed | gmail, email, drafts | Compose, save, revise, or send a scoped Gmail reply as requested, preserving its thread, recipients, sender identity, and attachments. Use for message composition and reply completion, not inbox classification or labeling. |
| [gmail-triage](../skills/gmail-triage/SKILL.md) | productivity | offline-reviewed | gmail, email, labels | Review a bounded Gmail inbox or search result, identify actionable messages, and apply explicitly requested organization. Use for mail triage and labeling; summarizing mail does not authorize sending, deleting, or changing inbox settings. |
| [google-docs-update](../skills/google-docs-update/SKILL.md) | productivity | offline-reviewed | docs, documents, editing | Make a bounded Google Docs content or formatting change in the correct tab and section, preserving unrelated material and verifying the saved revision. Use for document edits, not Sheets cells, document sharing, or exporting files. |
| [google-sheets-update](../skills/google-sheets-update/SKILL.md) | productivity | offline-reviewed | sheets, spreadsheet, rows | Update or append specified Google Sheets cells or rows through available document tools or an authorized browser, preserving formulas and checking saved results. Use for bounded sheet data edits, not workbook redesign or broad data analysis. |
| [product-shortlist](../skills/product-shortlist/SKILL.md) | research | offline-reviewed | shopping, offers, pricing | Compare current product or used-item offers in exact configurations using total cost, condition, and buyer constraints. Use for shopping research and listing comparison; it does not contact sellers, bid, reserve, or purchase. |
| [recurring-monitor](../skills/recurring-monitor/SKILL.md) | research | offline-reviewed | monitoring, changes, alerts | Set up or check a recurring watch with clear alert rules, saved observations, and an available host scheduler. Use for ongoing monitoring, not a one-time lookup. |
| [web-research](../skills/web-research/SKILL.md) | research | offline-reviewed | research, sources, evidence | Answer bounded factual questions, check which sources apply, and compare options using current public evidence or supplied source bundles. Use for facts, status and evidence-based comparisons; an open investigation testing rival explanations belongs to rabbit-hole. |

## Evaluation labels

- `draft`: written, but not yet backed by a qualifying execution record.
- `offline-reviewed`: passed a specific simulated task. The [run records](../evals/results/README.md)
  show which case was tested; the label does not cover every task the skill describes.
- `live-tested`: has a recorded test against a real service for the stated task and tools.

Collections describe the kind of work. Evaluation labels describe testing,
not permission to act or compatibility with your agent.

To update this page, edit [catalog.json](../catalog.json) or the relevant `SKILL.md`,
then run `python3 scripts/catalog.py render`.
