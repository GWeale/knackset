# Install and verify one skill

Use an existing target project outside the Knackset checkout. The local Python
command copies a complete package, including its license, resources, authored
cases and validation note. It needs Python 3.10+ and the standard library.
It does not download dependencies or connect an account.

## Choose and inspect

If you do not have a checkout, clone the repository outside your target project:

```bash
git clone https://github.com/GWeale/knackset.git
cd knackset
```

The default branch follows current repository contents. From the checkout:

```bash
python3 scripts/catalog.py list --collection field-kit
python3 scripts/catalog.py show rabbit-hole
```

Read `skills/rabbit-hole/SKILL.md` and its needed resources. Use another catalog
name to select a different package. `field-kit` and `utilities` describe the work;
`draft`, `offline-reviewed` and `live-tested` describe evidence. Installing a draft
does not make it tested.

## Preview, copy, check

Replace the project path. You can stay in the Knackset checkout; `--project`
chooses the destination explicitly.

```bash
python3 scripts/install_skill.py rabbit-hole --project /absolute/path/to/your-project --dry-run
python3 scripts/install_skill.py rabbit-hole --project /absolute/path/to/your-project
python3 scripts/install_skill.py rabbit-hole --project /absolute/path/to/your-project --check
```

The destination is `YOUR_PROJECT/.agents/skills/rabbit-hole/`. This is the
[Codex project location](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills),
checked 2026-11-01. Other hosts may use another location; follow their documented
installation method rather than assuming this directory is universal.

The command:

- Validates the catalog and selected package before copying.
- Refuses an existing destination, source/target overlap, redirected paths and
  symlink or special-file resources.
- Copies all canonical regular files, preserving script modes. Python bytecode
  caches are excluded, as they are from the package fingerprint.
- Reads the copied contents back and compares every file path and hash before
  reporting `installed`. `--check` does this without modifying the target.

`--dry-run` does not create or change target project files. Add `--json` to any
mode for file hashes, manifest SHA-256 and the versioned package fingerprint.
Keep that receipt with the project notes when repeatability matters.

A check compares against **this checkout's bytes**. A newer source revision may
legitimately differ from an older installed copy. The command does not update,
replace, delete or repair that copy. Review the differences first. On an I/O
failure, an incomplete directory is left for inspection and the command exits
unsuccessfully; do not treat it as an installed skill or blindly retry over it.

## Pin the source when repeatability matters

Use a full reviewed 40-character commit that contains both the command and the
chosen package. In your source checkout:

```bash
git checkout --detach YOUR_REVIEWED_40_CHARACTER_COMMIT
python3 scripts/install_skill.py rabbit-hole --project /absolute/path/to/your-project --json
```

The command copies local files; it does not fetch or change revisions for you.
The receipt identifies their actual contents, not a claim that an uncommitted
working tree is a particular Git revision. Two copies from the same unchanged
package produce the same manifest and package hashes.

## Confirm the host loads it

Run Codex in the target project. Use `/skills` to find the installed skill and
`$rabbit-hole` to select it. If it does not appear, restart Codex. These are the
official [discovery and invocation mechanisms](https://learn.chatgpt.com/docs/build-skills).

For a bounded first check:

> Use $rabbit-hole. This is a synthetic planning exercise. Two news articles
> repeat one owner newsletter. What would you check before treating them as
> independent confirmation? Explain the next step; do not browse or call a service.

Confirm that the host loaded the installed `SKILL.md` from the target project.
Keep its discovery/path evidence and read trace, not only a plausible answer.
A verified file copy does not establish host loading, implicit selection or task
quality. Historical [copy and host records](../evals/results/README.md) retain
their original package/revision limits; they do not prove this command's host use.

## Optional Skills CLI

For hosts supported by the third-party [Skills CLI](https://github.com/vercel-labs/skills),
its pinned [1.7.4 add reference](https://github.com/vercel-labs/skills/blob/v1.7.4/docs/commands.md#skills-add)
is an alternative. From the target project, using your reviewed source checkout:

```bash
npx skills@1.7.4 add /absolute/path/to/knackset --skill rabbit-hole --agent codex --copy
```

That route can download the CLI and use npm's cache. It requires
[Node.js 22.20+](https://github.com/vercel-labs/skills/blob/v1.7.4/package.json).
Choose one route per destination and review its displayed path before confirming.
The local Python command has no installer or Node dependency. No optional-CLI
execution or cross-host compatibility is claimed by the local-copy tests.
