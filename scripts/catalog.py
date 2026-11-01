#!/usr/bin/env python3
"""Browse the skill catalog or render its Markdown index; standard library only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from validate import NAME, STATUS, Validator


class CatalogError(ValueError):
    pass


def load_catalog(root: Path) -> list[dict]:
    validator = Validator(root)
    skills_root = root / "skills"
    if not skills_root.is_dir():
        raise CatalogError("skills directory does not exist")
    skills = {}
    metadata = {}
    for path in sorted(skills_root.iterdir()):
        if not path.is_dir() or path.name.startswith("."):
            continue
        if not path.resolve().is_relative_to(root.resolve()):
            validator.error(path, "skill folder symlink escapes repository boundary")
            continue
        skills[path.name] = path
        metadata[path.name] = validator.frontmatter(path)
    entries = validator.catalog(skills)
    if validator.errors:
        raise CatalogError("\n".join(validator.errors))
    return sorted(
        ({**entry, "description": metadata[entry["name"]]["description"]} for entry in entries),
        key=lambda entry: entry["name"],
    )


def select(entries: list[dict], args: argparse.Namespace) -> list[dict]:
    words = getattr(args, "query", "").casefold().split()
    return [
        entry for entry in entries
        if (not args.category or entry["category"] == args.category)
        and (not args.tag or args.tag in entry["tags"])
        and (not args.status or entry["status"] == args.status)
        and all(word in " ".join((entry["name"], entry["description"], *entry["tags"])).casefold()
                for word in words)
    ]


def cell(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|")


def render(entries: list[dict]) -> str:
    lines = [
        "# Skill catalog", "",
        "Choose a task below, then read its skill before installing it.", "",
        "- `draft`: written, but not yet backed by a qualifying execution record.",
        "- `offline-reviewed`: passed a specific simulated task. The [run records](../evals/results/README.md)",
        "  show which case was tested; the label does not cover every task the skill describes.",
        "- `live-tested`: has a recorded test against a real service for the stated task and tools.", "",
        "These labels describe testing, not permission to act or compatibility with your agent.", "",
        "| Skill | Category | Status | Tags | Description |",
        "| --- | --- | --- | --- | --- |",
    ]
    for entry in sorted(entries, key=lambda item: (item["category"], item["name"])):
        name = entry["name"]
        lines.append(
            f"| [{name}](../skills/{name}/SKILL.md) | {entry['category']} | {entry['status']} | "
            f"{', '.join(entry['tags'])} | {cell(entry['description'])} |"
        )
    lines.extend([
        "", "To update this page, edit [catalog.json](../catalog.json) or the relevant `SKILL.md`,",
        "then run `python3 scripts/catalog.py render`.",
    ])
    return "\n".join(lines) + "\n"


def print_entries(entries: list[dict], as_json: bool) -> None:
    if as_json:
        print(json.dumps(entries, ensure_ascii=False, indent=2, sort_keys=True))
    elif not entries:
        print("No skills matched.")
    else:
        for entry in entries:
            print(f"{entry['name']} [{entry['category']}; {entry['status']}] {entry['description']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("list", "search"):
        subparser = commands.add_parser(command, help=f"{command} skills by metadata")
        if command == "search":
            subparser.add_argument("query", help="all keywords must occur in name, description, or tags")
        subparser.add_argument("--json", action="store_true", help="emit structured metadata")
        subparser.add_argument("--category", help="filter by exact category slug")
        subparser.add_argument("--tag", help="filter by exact tag slug")
        subparser.add_argument("--status", choices=sorted(STATUS), help="filter by evaluation status")
    show = commands.add_parser("show", help="show one skill's metadata")
    show.add_argument("name")
    show.add_argument("--json", action="store_true", help="emit structured metadata")
    document = commands.add_parser("render", help="generate docs/catalog.md")
    document.add_argument("--check", action="store_true", help="fail if docs/catalog.md is stale")
    args = parser.parse_args(argv)
    if args.command in {"list", "search"}:
        if args.command == "search" and not args.query.strip():
            parser.error("search query must contain a keyword")
        for field in ("category", "tag"):
            value = getattr(args, field)
            if value and NAME.fullmatch(value) is None:
                parser.error(f"--{field} must be a lowercase slug")

    root = Path(__file__).resolve().parent.parent
    try:
        entries = load_catalog(root)
        if args.command in {"list", "search"}:
            print_entries(select(entries, args), args.json)
        elif args.command == "show":
            match = next((entry for entry in entries if entry["name"] == args.name), None)
            if match is None:
                raise CatalogError("unknown skill name")
            if args.json:
                print(json.dumps(match, ensure_ascii=False, indent=2, sort_keys=True))
            else:
                print(f"{match['name']}\n{match['description']}\n")
                for field in ("path", "category", "status", "tags", "basis", "evidence", "live_validation"):
                    value = match[field]
                    if isinstance(value, list):
                        value = ", ".join(value) or "none"
                    print(f"{field}: {value}")
        else:
            destination = root / "docs" / "catalog.md"
            content = render(entries)
            if args.check:
                if not destination.is_file() or destination.read_text(encoding="utf-8") != content:
                    raise CatalogError("docs/catalog.md is stale; run python3 scripts/catalog.py render")
                print("Catalog documentation is current.")
            else:
                if destination.is_symlink() or not destination.parent.resolve().is_relative_to(root):
                    raise CatalogError("catalog documentation path must stay inside the repository")
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(content, encoding="utf-8")
                print("Rendered docs/catalog.md.")
    except CatalogError as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    except (OSError, UnicodeError, ValueError, RuntimeError):
        print("ERROR catalog data or paths could not be read or written", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
