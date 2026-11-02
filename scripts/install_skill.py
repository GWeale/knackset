#!/usr/bin/env python3
"""Copy one complete Knackset package into an existing project's .agents/skills."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

from catalog import load_catalog
from validate import FINGERPRINT_ALGORITHM, NAME, Validator, package_files, package_fingerprint


class InstallError(ValueError):
    pass


def manifest(package: Path) -> dict[str, str]:
    return {file.relative_to(package).as_posix(): hashlib.sha256(file.read_bytes()).hexdigest()
            for file in package_files(package, include_caches=False)}


def project_destination(root: Path, project: Path, name: str) -> Path:
    project = project if project.is_absolute() else Path.cwd() / project
    if any(path.is_symlink() for path in (project, *project.parents)):
        raise InstallError("Use the existing project's canonical path, without symlinks.")
    if not project.is_dir():
        raise InstallError("The target project must already be a directory.")
    project = project.resolve(strict=True)
    if project == root or project.is_relative_to(root) or root.is_relative_to(project):
        raise InstallError("Keep the target project and Knackset source outside each other.")
    destination = project / ".agents" / "skills" / name
    for path in (project / ".agents", destination.parent, destination):
        if path.is_symlink():
            raise InstallError("The installation path must not redirect through symlinks.")
        if path.exists() and not path.is_dir():
            raise InstallError("The installation path must contain only directories.")
    return destination


def copy_skill(root: Path, name: str, project: Path, mode: str) -> dict:
    if not 1 <= len(name) <= 64 or NAME.fullmatch(name) is None:
        raise InstallError("Use a catalog skill name, such as rabbit-hole.")
    entry = next((entry for entry in load_catalog(root) if entry["name"] == name), None)
    if entry is None:
        raise InstallError("Unknown skill name; use scripts/catalog.py list to choose one.")
    source = root / entry["path"]
    validator = Validator(root)
    validator.skill(source, required=True)
    if validator.errors:
        raise InstallError("\n".join(validator.errors))
    expected = manifest(source)
    fingerprint = package_fingerprint(source)
    destination = project_destination(root, project, name)
    if mode == "check":
        if not destination.is_dir():
            raise InstallError("The skill is not installed in this project.")
    elif destination.exists():
        raise InstallError("Destination already exists; use --check or review it before replacing it.")

    if mode == "install":
        # Publish the entrypoint last so unfinished resource copies are not discoverable.
        destination.mkdir(parents=True)
        try:
            for relative in sorted(expected, key=lambda value: (value == "SKILL.md", value)):
                target = destination / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                with (source / relative).open("rb") as original, target.open("xb") as copied:
                    shutil.copyfileobj(original, copied)
                shutil.copymode(source / relative, target)
        except OSError as error:
            raise InstallError(f"Copy is incomplete at {destination}; inspect it before retrying.") from error

    if mode != "preview":
        actual = manifest(destination)
        changed = sorted(name for name in expected.keys() | actual.keys()
                         if expected.get(name) != actual.get(name))
        if changed or package_fingerprint(destination) != fingerprint:
            detail = ", ".join(changed) or "package fingerprint"
            raise InstallError(f"Package contents differ at {destination}: {detail}. Review this copy before use.")
    encoded = json.dumps(expected, sort_keys=True, separators=(",", ":")).encode()
    return {
        "status": {"preview": "planned", "install": "installed", "check": "verified"}[mode],
        "skill": name,
        "source": str(source),
        "destination": str(destination),
        "file_count": len(expected),
        "package_fingerprint_algorithm": FINGERPRINT_ALGORITHM,
        "package_sha256": fingerprint,
        "manifest_sha256": hashlib.sha256(encoded).hexdigest(),
        "files": expected,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill", help="one name from the catalog")
    parser.add_argument("--project", required=True, type=Path, help="existing target project, outside Knackset")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--dry-run", dest="mode", action="store_const", const="preview", help="inspect without writing")
    modes.add_argument("--check", dest="mode", action="store_const", const="check", help="verify an existing copy without writing")
    parser.set_defaults(mode="install")
    parser.add_argument("--json", action="store_true", help="emit the full file-hash receipt")
    args = parser.parse_args(argv)
    try:
        result = copy_skill(Path(__file__).resolve().parents[1], args.skill, args.project, args.mode)
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(f"{result['status']}: {result['skill']} -> {result['destination']} ({result['file_count']} files)")
            print(f"Package SHA-256: {result['package_sha256']}")
    except (OSError, ValueError, RuntimeError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
