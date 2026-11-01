# Adapt to the available browser

Map capabilities from the host's documented tools. These are requirements to
discover, not callable function names or a new protocol.

| Need | Evidence/capability to find | If missing |
| --- | --- | --- |
| Select authorized context | Browser/tab inventory and relevant account state | Identify the required authorized session; do not transfer profiles |
| Observe | Accessibility/DOM snapshot or screenshot | Report that the next target cannot be reliably identified |
| Act | Supported click/type/select/navigation operation | Use another host-permitted route or report the missing capability |
| Wait | Bounded observable condition or fresh observation | Reinspect; do not equate elapsed time with completion |
| Verify | Fresh page/record read of the requested result | Report the result as unverified or uncertain |

Some tools expose semantic locators; others expose references from the latest
snapshot. Refresh those references after a structural change. For repeated labels,
scope to the intended form, row, or record before acting. Coordinates require a
current visual identification and host support. Avoid requiring injected page
JavaScript, DevTools, or shell access; these are absent in some browser agents.

For a permitted fallback, first explain the observed capability failure and
preserve the user's browser/account choice. Do not install a different runtime,
change security settings, or extract cookies to recover a routine task. A bounded
handoff needs the exact target, authorized operation, task inputs, and saved-state
acceptance check, without credentials or unrelated browsing history.

These principles are informed by [Playwright's user-visible locator guidance](https://playwright.dev/docs/best-practices)
and [actionability checks](https://playwright.dev/docs/actionability). They do not
require Playwright. [Meta's Muse browser architecture](https://research.meta.ai/blog/security-and-safety-for-ai-agents-our-approach-with-muse)
illustrates why browser JavaScript access cannot be assumed across runtimes.
