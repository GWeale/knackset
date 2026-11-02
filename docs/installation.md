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
target project. This example pins the published revision
`d54f5a7ddf4a80ea23ba31e1f386af4d887b354c`; it is a reproducible historical
example, not a promise that it contains later fixes. Choose a reviewed full
40-character commit ID to use another revision.

```bash
export KNACKSET_SOURCE=/absolute/path/to/knackset-pinned
export KNACKSET_TARGET=/absolute/path/to/your-target-project
export KNACKSET_REVISION=d54f5a7ddf4a80ea23ba31e1f386af4d887b354c
git clone --no-checkout https://github.com/GWeale/knackset.git "$KNACKSET_SOURCE"
git -C "$KNACKSET_SOURCE" checkout --detach "$KNACKSET_REVISION"
cd "$KNACKSET_TARGET"
```

Read `skills/google-sheets-update/SKILL.md` and its resources in that source
checkout. Then copy and verify it:

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
package = source / "skills/google-sheets-update"
destination = target / ".agents/skills/google-sheets-update"
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

## Optional Skills CLI

The third-party [Skills CLI 1.7.4 installation reference](https://github.com/vercel-labs/skills/blob/v1.7.4/docs/commands.md#skills-add)
supports local paths, explicit agent selection, and copies. It requires
[Node.js 22.20+](https://github.com/vercel-labs/skills/blob/v1.7.4/package.json).
After the pinned checkout above, this is an alternative to the Python copy:

```bash
cd "$KNACKSET_TARGET"
npx skills@1.7.4 add "$KNACKSET_SOURCE" --skill google-sheets-update --agent codex --copy
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
`google-sheets-update` appears and select it with `$google-sheets-update`.
These are the official [explicit invocation mechanisms](https://learn.chatgpt.com/docs/build-skills).
For a first check, use a synthetic request:

> Use $google-sheets-update. This is a synthetic planning exercise with no
> connected account. An append for item P-3 timed out, and no saved-state read
> has happened yet. Explain your next step; do not call a browser or service.

Confirm that the session loaded the installed `SKILL.md` from the target project
and calls for a saved-state check before any retry. A plausible answer alone
does not prove activation: retain the discovery/path evidence and skill-read
trace. Record the host version, date, package revision and file manifest, prompt,
response, and limits. Keep this host check separate from the [offline task records](../evals/results/README.md).

This procedure describes the check to perform. A successful discovery/activation
check establishes that one host loaded one installed package. It does not prove
live Sheets compatibility, implicit selection accuracy, or a performance gain.
