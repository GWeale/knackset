# Validation and provenance

Status: **offline-reviewed**. Scope: alert delivery reconciliation and a transient failure during watch setup.
The [dated execution record](https://github.com/GWeale/knackset/blob/main/evals/results/audit-fixes-2026-11-01.json)
identifies each tested package by its versioned content fingerprint and preserves
failed attempts as well as passes. Match that fingerprint before applying the
status to a modified copy. This note contains no self-referential package hash.

Only the named synthetic conditions were exercised. Other branches in the
[authored cases](evals/evals.json) are not implied to pass. No live service or
browser workflow, account integration, implicit host routing, or performance
improvement is established by this status.

Independently written by Knackset contributors; basis: `research-derived`, `authored`. No proprietary
product prompts or upstream skill files were copied. The [MIT license](LICENSE.txt)
covers this package; linked external sources retain their own terms.
[Provenance at the audit baseline](https://github.com/GWeale/knackset/blob/d54f5a7ddf4a80ea23ba31e1f386af4d887b354c/docs/provenance.md)
describes the bounded, sanitized session lessons and public research.

Validation notes are part of the package. Update this note and rerun the relevant
evaluation when changing the workflow; an old successful run does not validate
new package contents.
