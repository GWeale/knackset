# Audit fixes — November 1, 2026

The audit examined revision `d54f5a7ddf4a80ea23ba31e1f386af4d887b354c`.
The following changes address its 20 findings. Instruction gaps and missing test
coverage were not treated as observed live-service failures.

| # | Change | Evidence and limit |
| --- | --- | --- |
| 1 | Versioned, length-prefixed package fingerprints | Validator regression distinguishes the formerly ambiguous file layouts; legacy hashes cannot promote |
| 2 | Reject all package symlinks and special resources, including drafts | CLI checks cover file/directory links, caches, package roots, and FIFOs |
| 3 | Require observed Gmail message scope before labeling; forbid thread labeling itself | Sandbox rejects blind targeting and a no-op whole-thread label |
| 4 | Retain historical successes alongside a current retest | Validator accepts mixed history and requires at least one qualifying current result |
| 5 | Verify the appended Sheets formula as well as its value | Missing, literal, and wrong-reference formulas fail the grader |
| 6 | Separate conversation wording, saved Gmail drafts, and sends | Chat-only fixture requires zero mailbox mutations; saved-draft fixtures remain separate |
| 7 | Name the target project, host, and install scope | [Installation guide](installation.md) and disposable project copy check |
| 8 | Supply a complete accepted contribution | [Starter recipe](authoring-example.md) runs through the public validator and catalog CLIs |
| 9 | Exercise installed-host discovery and explicit invocation | [Host record](../evals/results/host-install-2026-11-01.json): fresh Codex project discovery/load and planning passed; no live-service claim |
| 10 | Pin the entire source revision | Two project copies from the same full commit have identical file manifests |
| 11 | Export complete evidence after explicit response review | [Exporter](../scripts/export_eval.py) binds package and grader inputs at initialization; failures are retained |
| 12 | Select from descriptions before loading bodies | [Routing trial](../evals/results/routing-2026-11-01.json), with the original score and a documented judge correction |
| 13 | Exercise actual alert delivery after a timeout | Monitor fixture reconciles the delivered alert, verifies history, and suppresses a duplicate observation |
| 14 | Allow a valid watch to retain a pending baseline after a transient setup failure | Separate setup and scheduled phases; the evaluator advances the clock only after setup passes |
| 15 | Preserve an existing Gmail draft's content and identity | Fixture checks stable draft ID, changed message ID, alias, recipients, attachment, signature, and unrelated draft |
| 16 | Exercise UTF-16 ranges and literal `=` input | Docs checks multiple ranges and neighbors; Sheets rejects formula interpretation even if later repaired |
| 17 | Stop at changed travel prices or cancellation terms | Both quote refreshes require zero book, hold, and payment attempts |
| 18 | Review a correct PR without inventing findings | [Clean-PR decision review](../evals/results/clean-pr-2026-11-01.json); supplied checks are distinguished from personally executed tests |
| 19 | Keep Markdown code spans within blocks and matching delimiters | Broken links survive unmatched ticks across paragraphs, headings, lists, and quotes; genuine multiline code spans remain accepted |
| 20 | Ship validation limits with each package | Every skill links its bundled `VALIDATION.md`; the catalog checks the declared status against that note |

## What was measured

[Fresh sandbox records](../evals/results/audit-fixes-2026-11-01.json) retain the
actual operations, observations, final synthetic state, response checks, and
current package fingerprints. These are bounded offline trials, not browser or
service compatibility tests. The clean-PR exercise is a decision review; the
routing exercise tests metadata selection; host activation checks installation.
Those results are kept separate rather than combined into a single success rate.

The independent code review found three additional edge cases: a formula write
could be hidden by restoring literal text, Markdown links could disappear across
nonblank block boundaries, and a FIFO validation note could block the validator.
All received focused regression checks. A follow-up preserved genuine multiline
code spans inside blockquotes.

No private account, credential, real message, purchase, booking, or document was
used. Earlier evaluation records remain historical. No performance improvement
claim is made without a matched baseline comparison.

Final verification: 96 helper/fixture tests passed, as did package validation and
generated-catalog checks. All 14 fresh workflow trials passed. The named-host
activation probe preserved all five package files and completed explicit discovery,
loading, and synthetic planning. Both disposable fixtures and project registrations
were removed. Independent code review has no remaining material findings.
