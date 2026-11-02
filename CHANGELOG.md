# Changelog

## v0.1.0-alpha.1 — 2026-11-02 (UTC)

Initial preview of Knackset's portable workflow skills and offline evaluation
helpers and a local runtime preview.

- Workflow packages cover bounded changes, independent saved-state checks and
  recovery after uncertain writes, with package-local licenses and validation notes.
- A synthetic local runtime MVP persists intent and reconciliation state in SQLite,
  with bounded ticks and durable attempt ordering to prevent starvation. It has
  no real service adapter.
- Eight additional draft fixtures bring executable offline coverage to 22 cases;
  all 16 packages now carry scoped judged offline evidence.
- A searchable catalog and installation guidance help users choose and copy one
  complete skill into a project.
- The scripted timeout demo illustrates safe reconciliation and duplicate creation
  using isolated synthetic state, without a model or connected account.
- Offline fixtures, routing checks and judged evidence export distinguish authored
  scenarios from executed observations and bind results to package/source contents.
- A paired comparison CLI rejects stale, unmatched and incomparable records,
  preserves failures and reports cost only when measured for both variants.
- A final 20-run matched study passed current-hash checks: with-skill 10/10,
  baseline 8/10. Both baseline failures omitted Gmail verification reads while
  preserving correct labels. Sheets passed 5/5 per variant; billing cost is unknown.
  This small, unblinded, two-task study supports no general superiority claim.
- The comparison protocol specifies fresh contexts, randomized repeated trials,
  fixed rubrics and explicit judging limits. Release guidance includes a local
  demo and a sanitized feedback packet.

Limits: helper checks and synthetic observations do not establish live service
reliability, cross-host compatibility, general improvement over no-skill baselines or cost
savings. See [comparison protocol](docs/comparison-protocol.md) and
[release plan](docs/release-plan.md).
