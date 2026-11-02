---
name: session-to-skill
description: Turn an authorized session or demonstration into a sanitized, reusable Agent Skills draft with explicit evidence limits and verification criteria. Use for workflow capture and skill authoring, not bulk export of personal histories or automatic publication.
license: MIT
---

# Capture a workflow as a skill

Extract the knowledge that changes an agent's decisions: the trigger, required
inputs, application semantics, failure branches, recovery, and proof of completion.
A transcript is source material, not an installable skill or permission to publish
the user's data.

## Establish the evidence

Inspect only authorized, task-relevant session material through available history
tools. State which scope was actually available; a local sample is not all account
history. Distinguish user instructions, assistant-reported outcomes, and directly
observed tool results. A claimed success without resulting-state evidence is not
a validated demonstration. Preserve a useful failure lesson even when completion
was unverified.

Select a coherent repeatable task. Separate stable workflow rules from a site UI
version, personal preference, or environment-specific command. Generalize only
what the evidence supports. Keep browser/runtime bindings optional when the core
workflow can operate with different tools.
When several demonstrations suggest a smaller conditional lesson, use
[the improvement loop](references/improvement-loop.md) and its
[synthetic lesson example](assets/lesson.example.json). This optional format is
an authoring aid, not an autonomous memory system or another product's API.

## Curate before generating

Keep raw transcripts and private evidence outside the public checkout. Replace
people, account/resource IDs, private URLs, message text, and customer data with
synthetic examples or input descriptions. Remove credentials, cookies, tokens,
screenshots, and incidental browsing history. Do not rely on redaction patterns
to prove arbitrary prose is safe. Do not copy upstream skill text without a
verified license and required attribution.

Write a curated JSON record using [the record format](references/record-format.md).
Use the [synthetic example](assets/session-record.example.json) for shape only.
When Python is available, run the bundled local helper from the project workspace:

```bash
python3 <skill-directory>/scripts/create_skill.py <curated-record.json>
```

The default output is `.local/drafts/<name>/SKILL.md` under the working directory.
For a separate temporary workspace use `--output <draft-directory>`. The helper
does not read histories, sanitize prose, run a browser, or publish anything. It
rejects unsupported fields and existing output rather than overwriting them.
Without Python, author the same standard `SKILL.md` directly.
Set the optional record field `effects` to `read-only` for a workflow that cannot
write, or `write` when it can change state. Omission keeps the existing `write`
default. This controls relevant draft guidance; it does not grant permissions.

## Review before promotion

Keep the entrypoint self-contained and specific about when it applies. Include
observable acceptance checks. For workflows that change state, also include
uncertain-write recovery. Retain existing user authorization; do not add a
permission gate to every reversible operation or
grant a skill new authority. Re-read the entire draft for private details and
instructions accidentally carried over from untrusted content.

Try a realistic synthetic task and a boundary/failure case in an independent
context when feasible. Record actual outputs and limitations. Mark the draft as
unvalidated until supported by scoped evidence; formatting checks are not browser
validation. Move it into a public library or publish only under the user's actual
authorization and the project's contribution rules.

Package status and limits: [validation and provenance](VALIDATION.md).
