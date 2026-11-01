#!/usr/bin/env python3
"""Check Muse-Skills structure using Python 3.10+ and the standard library.

This is not a general YAML/Markdown parser, a behavioral evaluation, or a privacy
audit. Frontmatter deliberately supports only the project's three flat string
fields. Use JSON double-quoted strings for values outside the safe plain subset.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
PLAIN = re.compile(r"[A-Za-z0-9][A-Za-z0-9 .,_/()'!?;+-]*\Z")
IMPLICIT_NUMBER = re.compile(
    r"[+-]?(?:[0-9_]+(?:\.[0-9_]*)?(?:[eE][+-]?[0-9]+)?"
    r"|0[xX][0-9a-fA-F_]+|0[oO][0-7_]+|0[bB][01_]+)\Z"
)
IGNORED = {".git", ".local"}
BASIS = {"authored", "research-derived", "session-derived"}
STATUS = {"draft", "offline-reviewed", "live-tested"}


class Validator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.errors: list[str] = []

    def error(self, path: Path, message: str, line: int | None = None) -> None:
        try:
            label = str(path.relative_to(self.root))
        except ValueError:
            label = str(path)
        if line is not None:
            label += f":{line}"
        self.errors.append(f"{label}: {message}")

    def read_text(self, path: Path) -> str | None:
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            self.error(path, f"cannot read UTF-8 file: {exc}")
            return None

    def read_json(self, path: Path) -> dict | None:
        content = self.read_text(path)
        if content is None:
            return None
        try:
            value = json.loads(content)
        except json.JSONDecodeError as exc:
            self.error(path, f"invalid JSON: {exc.msg}", exc.lineno)
            return None
        if not isinstance(value, dict):
            self.error(path, "expected a JSON object")
            return None
        if type(value.get("schema_version")) is not int or value["schema_version"] != 1:
            self.error(path, "schema_version must be the integer 1")
        return value

    def frontmatter(self, skill: Path) -> None:
        path = skill / "SKILL.md"
        content = self.read_text(path)
        if content is None:
            return
        lines = content.splitlines()
        if not lines or lines[0] != "---":
            self.error(path, "frontmatter must start with --- on the first line")
            return
        try:
            end = lines.index("---", 1)
        except ValueError:
            self.error(path, "frontmatter is missing its closing ---")
            return
        fields: dict[str, str] = {}
        seen: set[str] = set()
        for number, line in enumerate(lines[1:end], 2):
            if not line.strip() or line.startswith("#"):
                continue
            match = re.fullmatch(r"([a-z][a-z-]*):[ ]*(.*)", line)
            if match is None:
                self.error(path, "unsupported frontmatter syntax; use flat string fields", number)
                continue
            key, raw = match.groups()
            raw = raw.strip()
            if key not in {"name", "description", "license"}:
                self.error(path, f"unsupported frontmatter field {key!r}", number)
                continue
            if key in seen:
                self.error(path, f"duplicate frontmatter field {key!r}", number)
                continue
            seen.add(key)
            value = self.scalar(raw)
            if value is None:
                self.error(
                    path,
                    f"unsupported value for {key!r}; use a safe plain string or a JSON double-quoted string",
                    number,
                )
                continue
            fields[key] = value
        for key in ("name", "description", "license"):
            if key not in fields:
                self.error(path, f"missing valid {key!r} string field")
        name = fields.get("name")
        if name is not None:
            if not 1 <= len(name) <= 64 or NAME.fullmatch(name) is None:
                self.error(path, "name must be 1..64 lowercase letters/digits with single internal hyphens")
            if name != skill.name:
                self.error(path, f"name {name!r} must match folder name {skill.name!r}")
        description = fields.get("description")
        if description is not None and (not description.strip() or not 1 <= len(description) <= 1024):
            self.error(path, "description must contain 1..1024 characters")
        if "license" in fields and fields["license"] != "MIT":
            self.error(path, "license must be MIT")

    @staticmethod
    def scalar(raw: str) -> str | None:
        if raw.startswith('"'):
            try:
                value = json.loads(raw)
            except json.JSONDecodeError:
                return None
            return value if isinstance(value, str) and not any(ord(char) < 32 for char in value) else None
        if PLAIN.fullmatch(raw) is None:
            return None
        if raw.lower() in {"true", "false", "yes", "no", "on", "off", "null"}:
            return None
        if IMPLICIT_NUMBER.fullmatch(raw) or re.fullmatch(r"\d{4}-\d\d-\d\d", raw):
            return None
        return raw

    def local_target(self, source: Path, target: str, boundary: Path, line: int | None = None) -> Path | None:
        # Markdown backslash escapes are punctuation escapes, not path separators.
        target = re.sub(r"\\([!\"#$%&'()*+,\-./:;<=>?@\[\]^_`{|}~])", r"\1", target)
        if re.match(r"^[A-Za-z]:[\\/]", target):
            self.error(source, f"absolute local link is not portable: {target!r}", line)
            return None
        try:
            parsed = urlsplit(target)
        except ValueError:
            self.error(source, f"invalid link destination {target!r}", line)
            return None
        if parsed.scheme and parsed.scheme.lower() != "file":
            return None
        if parsed.netloc and not parsed.scheme:
            return None
        if parsed.scheme.lower() == "file":
            self.error(source, f"absolute local link is not portable: {target!r}", line)
            return None
        path_text = unquote(parsed.path)
        if not path_text:
            return None  # A same-document fragment or query has no separate file.
        if Path(path_text).is_absolute() or "\\" in path_text:
            self.error(source, f"absolute or unsupported local link: {target!r}", line)
            return None
        resolved = (source.parent / path_text).resolve()
        if not resolved.is_relative_to(boundary.resolve()):
            self.error(source, f"local link escapes package boundary: {target!r}", line)
            return None
        if not resolved.exists():
            self.error(source, f"local link target does not exist: {target!r}", line)
            return None
        return resolved

    def markdown(self, source: Path, boundary: Path) -> None:
        if not source.resolve().is_relative_to(boundary.resolve()):
            self.error(source, "Markdown file symlink escapes package boundary")
            return
        content = self.read_text(source)
        if content is not None:
            for line, target in markdown_links(content):
                self.local_target(source, target, boundary, line)

    def skill(self, path: Path) -> None:
        if not path.is_dir():
            self.error(path, "skill folder does not exist")
            return
        self.frontmatter(path)
        for markdown in markdown_files(path):
            self.markdown(markdown, path)

    def catalog(self, skills: dict[str, Path]) -> None:
        path = self.root / "catalog.json"
        data = self.read_json(path)
        if data is None:
            return
        entries = data.get("skills")
        if not isinstance(entries, list):
            self.error(path, "skills must be a list")
            return
        seen: set[str] = set()
        for index, entry in enumerate(entries):
            label = f"skills[{index}]"
            if not isinstance(entry, dict):
                self.error(path, f"{label} must be an object")
                continue
            name = entry.get("name")
            if not isinstance(name, str):
                self.error(path, f"{label}.name must be a string")
                continue
            if name in seen:
                self.error(path, f"skill {name!r} is listed more than once")
            seen.add(name)
            if name not in skills:
                self.error(path, f"catalog skill {name!r} has no matching skill folder")
            if entry.get("path") != f"skills/{name}":
                self.error(path, f"{label}.path must be 'skills/{name}'")
            basis = entry.get("basis")
            if not isinstance(basis, list) or not basis or any(not isinstance(item, str) or item not in BASIS for item in basis):
                self.error(path, f"{label}.basis must be a nonempty list drawn from {sorted(BASIS)}")
            elif len(set(basis)) != len(basis):
                self.error(path, f"{label}.basis must not contain duplicates")
            status = entry.get("status")
            if not isinstance(status, str) or status not in STATUS:
                self.error(path, f"{label}.status must be one of {sorted(STATUS)}")
            live = entry.get("live_validation")
            if not isinstance(live, bool):
                self.error(path, f"{label}.live_validation must be a boolean")
            elif live != (status == "live-tested"):
                self.error(path, f"{label}.live_validation must match live-tested status")
            evidence = entry.get("evidence")
            if not isinstance(evidence, list) or any(not isinstance(item, str) or not item.strip() for item in evidence):
                self.error(path, f"{label}.evidence must be a list of nonempty relative paths")
                continue
            if status in {"offline-reviewed", "live-tested"} and not evidence:
                self.error(path, f"{label} requires evidence for promoted status {status!r}")
            for item in evidence:
                parts = Path(item).parts
                if not parts or parts[0] not in {"docs", "evals"} or ".." in parts:
                    self.error(path, f"{label} evidence must name a relative file under docs/ or evals/: {item!r}")
                    continue
                previous_errors = len(self.errors)
                resolved = self.local_target(path, item, self.root)
                if resolved is not None and not resolved.is_file():
                    self.error(path, f"{label} evidence must name a file: {item!r}")
                if resolved is None and len(self.errors) == previous_errors:
                    # External/fragment destinations are not evidence files.
                    self.error(path, f"{label} evidence must name an existing local file: {item!r}")
        for missing in sorted(set(skills) - seen):
            self.error(path, f"skill {missing!r} is missing from catalog")

    def scenarios(self, skills: dict[str, Path]) -> int:
        path = self.root / "evals" / "scenarios.json"
        data = self.read_json(path)
        if data is None:
            return 0
        scenarios = data.get("scenarios")
        if not isinstance(scenarios, list):
            self.error(path, "scenarios must be a list")
            return 0
        seen: set[str] = set()
        coverage = {name: set() for name in skills}
        for index, scenario in enumerate(scenarios):
            label = f"scenarios[{index}]"
            if not isinstance(scenario, dict):
                self.error(path, f"{label} must be an object")
                continue
            identifier = scenario.get("id")
            if not isinstance(identifier, str) or not identifier.strip():
                self.error(path, f"{label}.id must be a nonempty string")
            elif identifier in seen:
                self.error(path, f"duplicate scenario id {identifier!r}")
            else:
                seen.add(identifier)
            skill = scenario.get("skill")
            if not isinstance(skill, str) or skill not in skills:
                self.error(path, f"{label}.skill must name an existing skill")
            kind = scenario.get("kind")
            if kind not in ("success", "boundary"):
                self.error(path, f"{label}.kind must be success or boundary")
            elif isinstance(skill, str) and skill in coverage:
                coverage[skill].add(kind)
            for field in ("prompt", "context"):
                value = scenario.get(field)
                if not isinstance(value, str) or not value.strip():
                    self.error(path, f"{label}.{field} must be a nonempty string")
            for field in ("expected", "forbidden"):
                value = scenario.get(field)
                if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
                    self.error(path, f"{label}.{field} must be a list of nonempty strings")
                elif field == "expected" and not value:
                    self.error(path, f"{label}.expected must not be empty")
        for name, kinds in coverage.items():
            for kind in sorted({"success", "boundary"} - kinds):
                self.error(path, f"skill {name!r} requires at least one {kind} scenario")
        return len(scenarios)

    def repository(self) -> tuple[int, int]:
        skills_root = self.root / "skills"
        skills: dict[str, Path] = {}
        if not skills_root.is_dir():
            self.error(skills_root, "skills directory does not exist")
        else:
            for path in sorted(skills_root.iterdir()):
                if not path.is_dir() or path.name in IGNORED:
                    continue
                if not path.resolve().is_relative_to(self.root):
                    self.error(path, "skill folder symlink escapes repository boundary")
                    continue
                skills[path.name] = path
                self.skill(path)
            if not skills:
                self.error(skills_root, "no skill folders found")
        for path in markdown_files(self.root):
            if path.relative_to(self.root).parts[0] != "skills":
                self.markdown(path, self.root)
        self.catalog(skills)
        return len(skills), self.scenarios(skills)


def markdown_files(root: Path):
    for directory, subdirs, filenames in os.walk(root, followlinks=False):
        subdirs[:] = sorted(name for name in subdirs if name not in IGNORED)
        for name in sorted(filenames):
            if Path(name).suffix.lower() == ".md":
                yield Path(directory) / name


def markdown_links(content: str):
    """Yield destinations from inline/image links and reference definitions.

    Fenced and inline code are ignored. Destination fragments are handled later;
    this checks file resolution, not the existence of generated heading anchors.
    """
    fence: tuple[str, int] | None = None
    lines = []
    for original in content.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", original)
        if fence:
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= fence[1]:
                fence = None
            lines.append("")
            continue
        if marker:
            fence = (marker.group(1)[0], len(marker.group(1)))
            lines.append("")
            continue
        lines.append(original)
    text = "\n".join(lines)
    text = re.sub(r"(`+).*?\1", lambda match: "\n" * match.group().count("\n"), text, flags=re.DOTALL)
    starts = [match.end() for match in re.finditer(r"^ {0,3}\[[^\]\n]+\]:\s*", text, re.MULTILINE)]
    starts.extend(match.end() for match in re.finditer(r"\]\(\s*", text))
    for start in sorted(starts):
        number = text.count("\n", 0, start) + 1
        remaining = text[start:]
        if remaining.startswith("<"):
            end = remaining.find(">", 1)
            if end != -1:
                yield number, remaining[1:end]
            continue
        destination = []
        depth = 0
        escaped = False
        for char in remaining:
            if escaped:
                destination.extend(("\\", char))
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == "(":
                depth += 1
                destination.append(char)
            elif char == ")":
                if depth == 0:
                    break
                depth -= 1
                destination.append(char)
            elif char.isspace() and depth == 0:
                break
            else:
                destination.append(char)
        if destination:
            yield number, "".join(destination)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", type=Path, help="validate one standalone skill folder without catalog or scenarios")
    args = parser.parse_args(argv)
    root = args.skill.resolve() if args.skill else Path(__file__).resolve().parent.parent
    validator = Validator(root)
    if args.skill:
        validator.skill(root)
        summary = f"skill {root.name}"
    else:
        skills, scenarios = validator.repository()
        summary = f"repository ({skills} skills, {scenarios} scenarios)"
    if validator.errors:
        for error in validator.errors:
            print(f"ERROR {error}", file=sys.stderr)
        print(f"Validation failed: {len(validator.errors)} error(s).", file=sys.stderr)
        return 1
    print(f"Validated {summary}. Structural checks only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
