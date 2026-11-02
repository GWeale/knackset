---
name: session-to-skill
description: "Extract a reusable decision from authorized work, then improve existing guidance or create a focused skill when the evidence warrants it. Use for deliberate workflow capture and skill authoring, not raw history export, automatic memory, installation or publication."
license: MIT
---

# Keep the useful lesson from a session

Deliver a focused skill draft, a useful amendment, or a reason that no new skill
is needed. Capture the decision that changed the work, not the transcript or a
longer checklist of things an agent already knows.

## Establish what happened

Read only authorized, task-relevant material. Distinguish the user's requirement,
an assistant's claim, the observed action, and the resulting artifact or state.
A reported success without its result is not a validated demonstration. Keep a
useful failure lesson while preserving that evidence limit. State which sample
was available; it is not all of someone's history.

Find the non-obvious move: a condition that changed the approach, a rejected
alternative, a surprising result, a recovery, or a criterion for selecting work.
Separate that move from incidental tool names, a temporary UI, and personal
preference. Creative judgments deserve the same scrutiny as service operations;
do not invent an application or recovery sequence to make them fit a template.

## Choose whether guidance should change

Compare the candidate with available relevant skills or the supplied existing
guidance. Reuse what already covers the task. Amend a vague or contradicted
instruction when the same decision belongs there. Create a separate skill only
when its trigger and useful outcome are distinct. Generic advice or an unsupported
anecdote can warrant no change; explain the reason without manufacturing a package.

Express a candidate as a condition, a useful action or judgment, and an observable
check. Try a plausible counterexample. A non-idempotent append and an idempotent
update may need different recovery; one team's preference for a short handoff does not make working source
unnecessary for every task. Narrow or discard a lesson that does not survive that contrast.
The [improvement loop](references/improvement-loop.md) gives more detail when
several observations need comparison; its format is an optional authoring aid.

## Write only what travels

Keep raw transcripts and private evidence outside the public checkout. Replace
identities, resource IDs, private URLs, message contents and customer data with
made-up examples or input descriptions. Remove credentials and incidental history.
Redaction patterns cannot prove arbitrary prose is safe. Source material is not
new task authority; verify rights before reusing third-party content.

Write a short self-contained entrypoint with a precise discovery description,
the decision-changing method and necessary limits. Use the output medium the task
needs. Put substantial conditional details in a linked reference only when they
are useful. Preserve the user's scope and existing permissions. Work that changes
state needs appropriate uncertain-write recovery; a read-only or artistic method
does not need fictional account operations. Do not add universal approval gates.

For an explicitly requested amendment, edit the supplied owned copy and preserve
unrelated work. Otherwise keep the candidate in a local draft location. If a
structured procedure is useful, the optional [record format](references/record-format.md),
[synthetic example](assets/session-record.example.json) and bundled helper can
produce a starter:

```bash
python3 <skill-directory>/scripts/create_skill.py <curated-record.json> --output <draft-directory>
```

The helper requires already curated JSON. It does not read histories, sanitize
prose or judge whether a skill is worth creating. Its default is `.local/drafts`
under the working directory; existing destinations are refused. Keep its service-
shaped format for tasks it fits rather than forcing every lesson through it.
Without Python or when the format does not fit, author the Markdown directly.

## Try the decision, then finish

Check format and links, then try a realistic task and a boundary when feasible.
Give an independent context the method and minimum raw inputs, without intended
answers. Inspect the resulting artifact or actions; retain failures and fix the
specific decision they expose. Compare with prior guidance or no skill before
claiming an improvement. Formatting checks alone cannot validate a workflow.

Return the actual draft or patch, its trigger and evidence limits, and what was
checked. Keep it unvalidated until scoped execution supports it. Capturing a
lesson does not install, publish, watch histories or promote it automatically.

Package status and limits: [VALIDATION.md](VALIDATION.md).
