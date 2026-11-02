# Knackset

This repository contains portable Agent Skills and small Python standard-library
helpers. Preserve the existing icon. Install globally or change remote resources
only when the user explicitly requests that action.

## Structure and checks

- `skills/<name>/SKILL.md` is the independently usable entrypoint. Keep its needed
  resources inside that folder. Frontmatter uses this repository's deliberately
  small subset: flat `name`, `description`, and `license` string fields.
- `catalog.json` records provenance and validation status, not runtime permissions.
- `scripts/catalog.py` lists/searches that catalog and renders `docs/catalog.md`.
  `--collection field-kit` and `--collection utilities` filter editorial groups,
  independently of category or evidence status. Older entries default to utilities.
- `scripts/install_skill.py NAME --project PATH` copies a whole package into an
  existing project, with `--dry-run` and read-only `--check` modes. No overwrite,
  global install, network access or host activation is performed. Python caches
  are excluded using the same canonical-file rule as package fingerprints.
- `python3 scripts/demo.py` illustrates uncertain-write recovery with isolated
  synthetic state. It is scripted, not a model evaluation or a live service test.
- `docs/` contains project-wide design, research, and sanitized provenance.
- `skills/<name>/evals/evals.json` is the canonical synthetic case set, with success,
  boundary, and routing cases. `evals/archive/` is historical and excluded from coverage.
- `evals/sandbox.py` executes stateful offline fixtures, not real service/browser calls.
- Bind evaluation runs at init with `--variant with-skill --skill-package PATH`;
  `scripts/export_eval.py` captures evidence after an explicit final-response review.
- `scripts/routing_eval.py prepare` supplies names/descriptions and anonymous tasks;
  keep skill bodies and judge expectations out of the selection agent's context.
- Each package links `VALIDATION.md`; catalog `validation_note` keeps its stated
  status consistent with the catalog. Package notes are part of the fingerprint.
- `python3 evals/sandbox.py list` lists runnable cases with their skill and authored
  scenario IDs. New cases need success and consequential-failure CLI checks;
  grading must inspect actual saved state and the relevant read/write order.
- `evals/results/` records measured runs separately from authored inputs. Promoted
  statuses require structured dated evidence with the current package fingerprint.
- `python3 scripts/validate.py` checks packages, links, catalog, cases and evidence integrity.
- `python3 scripts/catalog.py render --check` checks generated discovery docs.
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
Bundle `LICENSE.txt` in each package. After editing catalog metadata or a skill
description, run `python3 scripts/catalog.py render`. A package edit invalidates
its promoted fingerprint; rerun the relevant evaluation or return its status to draft.
