# Disposable service pilot

Use an explicitly designated test account and test resources. A connected personal
account is not evidence that it is disposable. Do not scan unrelated mail or files.
Browser operations remain deferred while the existing human-only security hold is active.

| Service | Bounded task | Verification | Cleanup |
| --- | --- | --- | --- |
| Gmail | Create and revise an unsent synthetic draft | Read back target draft, recipients, body and stable identity | Delete only that test draft through an available supported operation |
| Sheets | Append one uniquely keyed synthetic row; reconcile an intentionally lost acknowledgement | Read key, values and formulas; require one row | Remove only the identified test row or disposable sheet |
| Docs | Replace two synthetic paragraphs following an emoji | Read current revision, text and neighboring formatting | Delete disposable document |
| Calendar | Create one all-day test event without guests | Read saved dates, calendar and guest list | Delete the exact test event |

Before execution, record tool capabilities and confirm that required read, write,
and cleanup operations are actually available. Missing cleanup is a blocker to
creating persistent test data unless the user explicitly chooses to retain it.
Keep resource identifiers and raw responses in ignored local storage; publish only
sanitized evidence tied to package revision and task variant. Capture uncertain
writes as uncertain, and reconcile before retrying.

A comparison uses separate equivalent resources and fresh contexts for with-skill
and no-skill runs. Randomize order, retain failures, and distinguish measured model
usage from unavailable billing data. Never mark a skill live-tested from a planning
answer or a synthetic fixture.

Current discovery found a Gmail connector. No disposable account has yet been
designated, and no Sheets, Docs or Calendar service connector was found in the
current tool inventory. No live service writes have been performed for this pilot.
