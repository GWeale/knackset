# Muse-Skills

This repository contains portable Agent Skills and small Python standard-library
helpers. Preserve the existing icon. Do not install this library globally or
change remote resources as part of authoring it.

## Structure and checks

- `skills/<name>/SKILL.md` is the independently usable entrypoint. Keep its needed
  resources inside that folder. Frontmatter uses this repository's deliberately
  small subset: flat `name`, `description`, and `license` string fields.
- `catalog.json` records provenance and validation status, not runtime permissions.
- `docs/` contains project-wide design, research, and sanitized provenance.
- `evals/` contains synthetic scenarios, not completed browser tests.
- `python3 scripts/validate.py` checks frontmatter, catalog, links, and scenario coverage.
- `python3 -m unittest discover -s tests -v` checks the public helper CLIs in temporary directories.

## Authoring

Read `docs/workflow-contract.md` and `docs/provenance.md` before expanding the
library. Prefer a focused skill over a new runtime or dependency. Host tool and
authorization policies override example bindings. Do not embed private history,
account IDs, profile paths, credentials, machine IDs, or brittle element IDs.

Research current facts from primary sources and date the findings. Do not copy
upstream skills without checking file-level licensing. Label authored procedures,
observed session lessons, offline evaluation, and live validation separately.
Never mark a skill live-tested without dated execution evidence at a named revision.
