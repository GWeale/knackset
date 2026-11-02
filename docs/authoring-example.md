# A complete accepted contribution

The [local-note-update starter](examples/local-note-update/SKILL.md) is an
instruction-only example for one bounded local text edit. It lives under
`docs/examples/`, outside the shipped catalog. Its three scenarios are authored
inputs, not measured runs or executable sandbox cases.

## Accepted files and frontmatter

Copy the whole example folder when starting a contribution:

```text
skills/local-note-update/
  SKILL.md
  LICENSE.txt
  VALIDATION.md
  evals/evals.json
```

The complete [SKILL.md](examples/local-note-update/SKILL.md) starts with exactly
these three flat fields:

```yaml
---
name: local-note-update
description: "Update a specified passage in a local plain-text note and verify the saved result. Use for bounded file edits; route conversation-only wording requests to ordinary drafting."
license: MIT
---
```

This repository deliberately supports a smaller subset than the general
[Agent Skills specification](https://agentskills.io/specification#frontmatter),
checked on 2026-11-01. All three fields are required strings. The name matches
the folder and contains 1–64 lowercase ASCII letters/digits with single internal
hyphens. The description has 1–1024 characters. `license` is exactly `MIT`.
Use a single-line JSON double-quoted value for punctuation or other characters
outside a simple plain string; escape embedded quotes as `\"`. Do not use YAML
block scalars, single quotes, nested metadata, or extra frontmatter fields. Put
environment requirements and workflow instructions in the body.

The starter bundles the unchanged [MIT notice](examples/local-note-update/LICENSE.txt)
and links its [draft validation note](examples/local-note-update/VALIDATION.md)
so those limits remain visible after copying the package alone.

## Catalog entry

Add this object to the existing root `catalog.json` `skills` array. Keep its
`schema_version` at `1`; do not replace the existing entries. A copy is provided
as [local-note-update.catalog.json](examples/local-note-update.catalog.json).

```json
{
  "name": "local-note-update",
  "path": "skills/local-note-update",
  "collection": "utilities",
  "category": "files",
  "tags": ["notes", "verify"],
  "basis": ["authored"],
  "status": "draft",
  "evidence": [],
  "live_validation": false
}
```

`collection` is `field-kit` for the original creative/investigative methods or
`utilities` for supporting operational workflows. Older entries without this
field are treated as utilities. It is separate from category and test status.
Categories and tags are lowercase slugs; tag lists must be nonempty and unique.
`basis` is a nonempty unique list drawn from `authored`, `research-derived`, and
`session-derived`. The description comes from `SKILL.md`, not the catalog. New
skills start as `draft` with no claimed execution evidence.

## Minimum authored cases

The complete [evals/evals.json](examples/local-note-update/evals/evals.json)
contains one `success`, one `boundary`, and one `routing` case. The success case
checks a saved edit and preserved neighboring text. The boundary case makes the
target ambiguous and expects zero writes. The routing prompt naturally asks for
wording in the conversation; it does not disclose an expected skill choice.

Every case supplies `id`, `kind`, `prompt`, `context`, `expected_output`,
`assertions`, `forbidden`, and `files`. IDs must be unique across the library;
prefix them with the skill name. Assertions are nonempty strings in a nonempty
list. `forbidden` and `files` are lists and may be empty. File paths, when used,
are relative to the package root and must name files inside it.

For a routing evaluation, show only the available names/descriptions before the
prompt, record the selection, and only then load the selected body. See the
[evaluation guide](../evals/README.md) for execution and evidence requirements.
Adding JSON cases does not register a runner in `evals/sandbox.py` or justify
promoting the catalog status.

## Copy and check the starter

Run this from the Knackset checkout only when you intend to add this example to
your working tree. It refuses an existing name or folder, copies all package
files, and appends the catalog entry:

```bash
python3 - <<'PY'
import json
from pathlib import Path
import shutil

entry = json.loads(Path("docs/examples/local-note-update.catalog.json").read_text())
catalog_path = Path("catalog.json")
catalog = json.loads(catalog_path.read_text())
destination = Path(entry["path"])
if destination.exists() or destination.is_symlink() or any(
    item["name"] == entry["name"] for item in catalog["skills"]
):
    raise SystemExit("The starter already exists; choose a new skill name before copying.")
shutil.copytree(Path("docs/examples") / entry["name"], destination)
catalog["skills"].append(entry)
catalog_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
PY
python3 scripts/catalog.py render
python3 scripts/validate.py
python3 scripts/catalog.py render --check
```

When adapting it, change the folder, frontmatter name, catalog name/path,
`skill_name`, and case ID prefixes together. Rewrite the description, body,
cases, and validation note for the actual workflow. Then run the checks above
and the repository's relevant tests. The starter's public-CLI check is:

```bash
python3 -m unittest discover -s tests -p test_authoring_example.py -v
```

That check copies this documented starter into a temporary repository and runs
catalog rendering and full structural validation. It does not run a model or
establish behavioral quality. New runnable fixtures additionally need success
and consequential-failure checks described in the [evaluation guide](../evals/README.md).
