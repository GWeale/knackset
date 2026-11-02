# Install into the project that will use the skill

These instructions target **Codex CLI, project scope**. Start with an existing
target project, separate from this library checkout. Copy the whole skill folder,
including its license, references, fixtures, and validation note when present.
Installing a skill supplies instructions; the host must supply the tools and
authorized access needed for the task.

The official [Codex skill documentation](https://learn.chatgpt.com/docs/build-skills)
describes these scopes, checked on 2026-11-01:

| Scope | Directory | Effect |
| --- | --- | --- |
| Project | `YOUR_PROJECT/.agents/skills/` | Available when Codex runs in that project; repository parents are also searched up to its root |
| User | `~/.agents/skills/` | Available across that user's projects |
| Admin | `/etc/codex/skills/` | Shared machine configuration |

The recipe below writes only the selected project scope. Other hosts may use
different directories. Follow the chosen host's documentation before copying.

## Copy a pinned revision into a Codex project

Requires Git and Python 3.10+, with no Node.js or installer dependency. Replace
the two absolute paths. The source path must be a new directory outside your
target project. This example pins the reviewed revision
`cebb70e2deeaebb4e76137d6f9ae097a61074cd5`, which contains all nine field-kit draft methods.
The example selects `rabbit-hole`; set `KNACKSET_SKILL` to another folder name to
choose a different package. A pinned copy makes contents reproducible; it does
not imply that the selected draft has passed an evaluation suite. Use a full
40-character commit ID containing the package you want.

```bash
export KNACKSET_SOURCE=/absolute/path/to/knackset-pinned
export KNACKSET_TARGET=/absolute/path/to/your-target-project
export KNACKSET_REVISION=cebb70e2deeaebb4e76137d6f9ae097a61074cd5
export KNACKSET_SKILL=rabbit-hole
git clone --no-checkout https://github.com/GWeale/knackset.git "$KNACKSET_SOURCE"
git -C "$KNACKSET_SOURCE" checkout --detach "$KNACKSET_REVISION"
cd "$KNACKSET_TARGET"
```

Read the selected `skills/<name>/SKILL.md` and its resources in the source
checkout. Then copy and verify the whole package:

```bash
python3 - <<'PY'
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

source = Path(os.environ["KNACKSET_SOURCE"]).resolve()
target = Path(os.environ["KNACKSET_TARGET"]).resolve()
revision = os.environ["KNACKSET_REVISION"]
selected = os.environ["KNACKSET_SKILL"]
if len(selected) > 64 or re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", selected) is None:
    raise SystemExit("Use a catalog skill folder name, such as rabbit-hole.")
if re.fullmatch(r"[0-9a-f]{40}", revision) is None:
    raise SystemExit("Use a full lowercase 40-character commit ID.")
head = subprocess.check_output(
    ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
).strip()
dirty = subprocess.check_output(
    ["git", "-C", str(source), "status", "--porcelain", "--untracked-files=all", "--ignored"],
    text=True,
)
if head != revision or dirty:
    raise SystemExit("The source must be an unchanged checkout of the pinned revision.")
if not target.is_dir() or Path.cwd().resolve() != target:
    raise SystemExit("Change directory to the existing target project first.")
if target == source or target.is_relative_to(source) or source.is_relative_to(target):
    raise SystemExit("Keep the target project and Knackset source outside each other.")
package = source / "skills" / selected
if not package.is_dir() or package.is_symlink() or (source / "skills").is_symlink():
    raise SystemExit("The selected package must be a regular skill directory in this revision.")
destination = target / ".agents" / "skills" / selected
if any(path.is_symlink() for path in (target / ".agents", destination.parent, destination)):
    raise SystemExit("The installation path must not redirect through symlinks.")
if destination.exists():
    raise SystemExit("Destination already exists; review it before replacing a skill.")

def manifest(folder):
    result = {}
    for path in sorted(folder.rglob("*")):
        if path.is_symlink():
            raise SystemExit("This copy recipe requires a package without symlinks.")
        if path.is_file():
            result[path.relative_to(folder).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result

expected = manifest(package)
if "SKILL.md" not in expected or "LICENSE.txt" not in expected:
    raise SystemExit("The source is missing its skill or license.")
shutil.copytree(package, destination)
if manifest(destination) != expected:
    raise SystemExit("Copied resources differ from the source; do not activate this copy.")
encoded = json.dumps(expected, sort_keys=True, separators=(",", ":")).encode()
print(f"Installed {len(expected)} files at {destination}")
print(f"Source revision: {revision}")
print(f"Installation manifest SHA-256: {hashlib.sha256(encoded).hexdigest()}")
PY
```

The command refuses an existing destination. It compares every relative file
path and its bytes after the copy. Keep the printed source revision and manifest
hash with your project notes. Repeating the copy into another empty project from
the same unchanged revision produces the same manifest hash even after `main`
changes. This installation manifest is separate from the package fingerprint
used by Knackset's evaluation records.

## Observed package-copy checks, November 1, 2026

The [current copy record](../evals/results/expansion-install-20261101.json) executes
the Python block above for the default Rabbit Hole and all three expansion
packages. Two isolated copies of each package matched every file path and hash.
Existing destinations and an invalid folder name were refused. All temporary
source and target files were removed. The [earlier six-package check](../evals/results/field-kit-install-20261101.json)
remains historical at its recorded revision.

The source was materialized from the pinned Git archive. This tested the copy
block, not the network clone command, optional CLI, or agent host activation.

## Optional Skills CLI

The third-party [Skills CLI 1.7.4 installation reference](https://github.com/vercel-labs/skills/blob/v1.7.4/docs/commands.md#skills-add)
supports local paths, explicit agent selection, and copies. It requires
[Node.js 22.20+](https://github.com/vercel-labs/skills/blob/v1.7.4/package.json).
After the pinned checkout above, this is an alternative to the Python copy:

```bash
cd "$KNACKSET_TARGET"
npx skills@1.7.4 add "$KNACKSET_SOURCE" --skill "$KNACKSET_SKILL" --agent codex --copy
```

Choose this or the copy recipe, not both for the same destination. Check the
displayed project destination before confirming. In version 1.7.4, omitting
`--global` means the current project; `--agent codex` selects Codex and `--copy`
requests a copy rather than a symlink. Its [Codex path mapping](https://github.com/vercel-labs/skills/blob/v1.7.4/docs/agents.md)
is `.agents/skills/`. The `npx` route can download the CLI and use npm's cache
outside your project. The direct Python copy avoids that dependency. These CLI
facts were verified from the pinned upstream documentation on 2026-11-01; this
repository does not claim an executed installer test.

## Check discovery and activation

Start a fresh Codex CLI session in the target project. Use `/skills` to confirm
`rabbit-hole` appears and select it with `$rabbit-hole` when using the default
package above. Substitute your selected name for another package.
These are the official [explicit invocation mechanisms](https://learn.chatgpt.com/docs/build-skills).
For a first check, use a synthetic request:

> Use $rabbit-hole. This is a synthetic planning exercise. Two news articles
> repeat one owner newsletter. What would you check before treating them as
> independent confirmation? Explain the next step; do not browse or call a service.

Confirm that the session loaded the installed `SKILL.md` from the target project
and distinguishes repeated claims from independent evidence. A plausible answer alone
does not prove activation: retain the discovery/path evidence and skill-read
trace. Record the host version, date, package revision and file manifest, prompt,
response, and limits. Keep this host check separate from the [offline task records](../evals/results/README.md).

## Historical host check, November 1, 2026

The [host record](../evals/results/host-install-2026-11-01.json) verifies
`google-sheets-update` from revision
`b56d6a705370779dfa2aa33f5cad95eb877a87d8`, in a fresh T3 Code session using
**Codex CLI 0.166.0-alpha.5.1 on Ubuntu**
and `gpt-6-astra`. The session reported the project skill in its initial catalog,
then read that installed `SKILL.md` before answering the synthetic timeout prompt.
It called for reconciling saved state before any retry; no browser or service was
called. The parent inspected the recorded command sequence and output.

All five package files matched the pinned source. Two earlier project copies had
identical manifests. The probe materialized selected files from the commit rather
than executing the optional Skills CLI or Git clone command above. Temporary
copies and their project registrations were removed; no global skill was installed.
Private absolute paths are normalized to project-relative paths in the public record.

This establishes explicit discovery, loading, and planning in that host/version.
It does not establish implicit selection accuracy, live Sheets compatibility,
exactly-once insertion, or a performance gain.

This older host check does not establish discovery or activation of the field-kit
methods. Their worked examples loaded the source skill explicitly. The current
selected-package copy check is a file-integrity check, separate from host use.
