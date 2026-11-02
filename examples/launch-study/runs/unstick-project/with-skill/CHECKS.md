# Checks and remaining gaps

Checked locally on Hatter (`hatter-small`) on 2026-11-01 America/Los_Angeles. This is artifact assembly and inspection, not a new Reference Remix execution or a host-installation test.

## Passed

- Both SVGs match supplied bytes exactly and parse as XML. No script, image, foreignObject, href/src, URL-valued attribute or external entity was found.
- Installed librsvg/Cairo rendered the poster successfully. The PNG decodes at 891 × 1260 pixels.
- Visually inspected that PNG: the complete portrait fits the canvas, the title and all event lines are visible, and the crown, route and lower information band appear without obvious clipping. This was an agent inspection at the saved preview size, not print QA or an audience judgment.
- All Markdown/image links resolve to included files or supplied inputs and are relative; final link check recorded in the execution output.
- Narration contains 161 spoken words: estimated 69 seconds at 140 words/minute, within the requested 60–90 seconds. Cues allow a few pauses.
- Read the source-limit claims against the supplied README, examples README, poster metadata, alpha snapshot and office-workflow comparison report. The packet does not reuse the office scores as creative-method evidence.

A word-count check caught an incorrect timing annotation in the first narration draft; it was corrected. An initial link check caught the README's link to this not-yet-written check record; the record was created before the final link check. These were packet assembly checks, not evidence of a method outcome. No failed render or asset mismatch occurred.

## Preserved asset SHA-256

- `assets/knackset-mark.svg`: `a4af67e7964274e18fdcec6d08dd8aa323ab85dcf20ece14cf1dc7570346c3ae`
- `assets/night-orchard.svg`: `a0411b85965ac254a106e47d63d47fd5606f4a1cca9eaeed7c9161ca0ddeeae8`

## Not performed / still dependent

- No spoken recording, stopwatch timing or outside feedback. A person must read it aloud and judge comprehension and visual appeal.
- No recovery of the original three textual reference studies; they were not supplied. Full source-to-output audit and replay remain unavailable.
- The companion-flyer task is ready to try, not executed or user-tested in this packet. Its prompt is a bounded practice exercise, not the full Reference Remix package. Host discovery/activation and task quality are unverified.
- No print proof, font-portability certification or cross-viewer test. The included PNG is a stable local preview; the SVG uses an installed/local font fallback.
- No repository-wide tests: repository code and packages were not changed. No new dependencies, account connections, network requests, browser/GUI, scheduling, remote writes, commits or publication were used.

The launch choice remains with George. Human review can settle whether this packet communicates the creative promise. Live-account work can later support live-service claims; it is not evidence for this poster or a prerequisite for inspecting this packet.
