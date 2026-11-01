# Provenance and limits

Authored 2026-11-01. The library contains independently written procedures, not
extracted proprietary Muse or Grok Bot prompts. Public sources are linked in
[research](research.md) and the application skills.

## Private session evidence

A bounded read-only review inspected six prior threads available on the current
worker: two user setup/workflow threads and four delegated browser verification
threads. One verification thread was also checked at tool-activity level. That
activity established opening an agent-owned tab, observing a loaded page through
a snapshot, and closing it. It did not establish a completed authenticated form,
mail, spreadsheet, shopping, or code-review workflow.

Reusable lessons were generalized: discover actual tool availability; distinguish
worker and personal sessions; use current page observations; clean up owned tabs;
separate connection success from task completion. The browser skill incorporates
these lessons alongside research. The application skills are authored proposals
informed by public documentation, not claimed successful history replays.

The available history is a sample, not an account-wide audit. Private thread
identifiers, links, transcripts, account data, and screenshots are intentionally
absent from this repository. The bundled session record is entirely synthetic.

## Public material and licensing

Each catalog entry records `session-derived`, `research-derived`, and/or `authored`
basis. Those labels are not third-party endorsements or rights grants. Links are
research references; no upstream skills or implementation files were vendored.
The MIT license covers original project content. External documentation, models,
repositories, and linked resources retain their own licenses and terms.

## Validation

The initial revision `57d0e15` recorded eight skills as `draft`, with no live
validation. The first [offline decision review](../evals/offline-review-2026-11-01.md)
belongs to that revision. Its original central scenario set is preserved in the
historical archive; current cases live inside each package.

Structural checks and Python CLI tests do not promote skills automatically.
Measured execution is recorded separately in `evals/results/`; promotion requires
matching structured evidence, its limitations and the current package fingerprint.
Stateful sandbox results establish synthetic execution only. A live test must use
an authorized account and verify the actual saved outcome. No live account message,
purchase, booking, or document edit was performed while authoring this release.
The user subsequently authorized publication of this repository on GitHub.
