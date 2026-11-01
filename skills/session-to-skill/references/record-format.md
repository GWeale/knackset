# Curated session record

This is a project-specific JSON input to `scripts/create_skill.py`, not a raw
session export format. An authorized author must sanitize and review the content
before invoking the generator. The helper validates shape, not confidentiality,
truth, prompt-injection resistance, or workflow quality.

The object must contain these required keys and may also contain `effects`:

| Key | Value |
| --- | --- |
| `name` | Lowercase letters/digits and single hyphens, 1–64 characters; no edge hyphens |
| `description` | One-line nonempty routing description, at most 1024 characters |
| `site` | One-line nonempty service/domain description; no private account URLs |
| `preconditions` | Nonempty list of one-line, nonempty strings describing task inputs and access |
| `steps` | Nonempty list of one-line, nonempty reusable task instructions |
| `verification` | Nonempty list of one-line, nonempty observable resulting-state checks |
| `recovery` | Nonempty list of one-line, nonempty failure/recovery instructions |
| `evidence` | `synthetic` or `session-summary`; neither means browser-validated |
| `effects` (optional) | `read-only` or `write`; defaults to `write` for existing records. Affects relevant draft guidance, not execution permissions |

Strings must not contain line breaks/control characters or a standalone Markdown
frontmatter delimiter. The name determines a folder under the chosen output
directory; paths in the name are rejected. Existing output is preserved.

Use public or synthetic service names, task inputs instead of literal account
values, and general rules instead of timestamps/element IDs from a run. A field
named `raw_transcript`, even with sanitized contents, is intentionally rejected.
Review rights to any third-party material separately before redistribution.
