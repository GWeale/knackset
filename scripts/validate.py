#!/usr/bin/env python3
"""Check Knackset structure using Python 3.10+ and the standard library.

This is not a general YAML/Markdown parser, a behavioral evaluation, or a privacy
audit. Frontmatter deliberately supports only the project's three flat string
fields. Use JSON double-quoted strings for values outside the safe plain subset.
"""

from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import unicodedata
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
COLLECTIONS = {"field-kit", "utilities"}
EVAL_KINDS = {"success", "boundary", "routing"}
FINGERPRINT_ALGORITHM = "sha256-length-prefixed-v2"
LEGACY_FINGERPRINT_ALGORITHM = "sha256-nul-delimited-v1"


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object field")
        result[key] = value
    return result


def reject_constant(_value: str) -> None:
    raise ValueError("nonstandard JSON constant")


def package_files(path: Path, *, include_caches: bool = True) -> list[Path]:
    """List regular files only after rejecting every symlink and special resource."""
    absolute = Path(os.path.abspath(path))
    if any(item.is_symlink() for item in (absolute, *absolute.parents)):
        raise ValueError("package path must not contain symlinks")
    if not stat.S_ISDIR(path.lstat().st_mode):
        raise ValueError("skill folder must be a regular directory")
    directories = [path]
    files = []
    while directories:
        for resource in directories.pop().iterdir():
            mode = resource.lstat().st_mode
            relative = resource.relative_to(path).as_posix()
            if stat.S_ISLNK(mode):
                raise ValueError(f"package resource must not be a symlink: {relative!r}")
            if stat.S_ISDIR(mode):
                directories.append(resource)
            elif stat.S_ISREG(mode):
                files.append(resource)
            else:
                raise ValueError(f"package resources must be regular files and directories: {relative!r}")
    if not include_caches:
        files = [file for file in files
                 if "__pycache__" not in file.relative_to(path).parts
                 and file.suffix not in {".pyc", ".pyo"}]
    return sorted(files, key=lambda item: item.relative_to(path).as_posix())


def package_fingerprint(path: Path) -> str:
    """Hash length-prefixed path/content pairs with a versioned domain prefix.

    All resources are checked before reading; regular Python bytecode caches are
    then excluded. Lengths are unsigned 64-bit big-endian byte counts.
    """
    digest = hashlib.sha256(b"knackset-package\0" + FINGERPRINT_ALGORITHM.encode("ascii") + b"\0")
    for file in package_files(path, include_caches=False):
        relative = file.relative_to(path)
        for value in (relative.as_posix().encode("utf-8"), file.read_bytes()):
            digest.update(len(value).to_bytes(8, "big"))
            digest.update(value)
    return digest.hexdigest()


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

    def read_json(self, path: Path, *, schema_version: bool = True) -> dict | None:
        content = self.read_text(path)
        if content is None:
            return None
        try:
            value = json.loads(content, object_pairs_hook=unique_object, parse_constant=reject_constant)
        except ValueError as exc:
            message = exc.msg if isinstance(exc, json.JSONDecodeError) else str(exc)
            self.error(path, f"invalid JSON: {message}", getattr(exc, "lineno", None))
            return None
        if not isinstance(value, dict):
            self.error(path, "expected a JSON object")
            return None
        if schema_version and (type(value.get("schema_version")) is not int or value["schema_version"] != 1):
            self.error(path, "schema_version must be the integer 1")
        return value

    def frontmatter(self, skill: Path) -> dict[str, str]:
        path = skill / "SKILL.md"
        content = self.read_text(path)
        if content is None:
            return {}
        lines = content.splitlines()
        if not lines or lines[0] != "---":
            self.error(path, "frontmatter must start with --- on the first line")
            return {}
        try:
            end = lines.index("---", 1)
        except ValueError:
            self.error(path, "frontmatter is missing its closing ---")
            return {}
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
        if not "\n".join(lines[end + 1:]).strip():
            self.error(path, "skill body must contain instructions")
        return fields

    @staticmethod
    def scalar(raw: str) -> str | None:
        if raw.startswith('"'):
            try:
                value = json.loads(raw)
            except json.JSONDecodeError:
                return None
            return value if isinstance(value, str) and not any(
                unicodedata.category(char) in {"Cc", "Cf", "Cs", "Zl", "Zp"} for char in value
            ) else None
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
        if any(ord(char) < 32 or ord(char) == 127 for char in path_text):
            self.error(source, "local link destination contains a control character", line)
            return None
        if Path(path_text).is_absolute() or "\\" in path_text:
            self.error(source, f"absolute or unsupported local link: {target!r}", line)
            return None
        try:
            resolved = (source.parent / path_text).resolve()
        except (OSError, ValueError, RuntimeError):
            self.error(source, "local link target cannot be resolved", line)
            return None
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

    def skill(self, path: Path, *, required: bool = False, seen_ids: set[str] | None = None) -> int:
        try:
            package_files(path)
        except (OSError, ValueError) as exc:
            self.error(path, f"cannot validate package resources: {exc}")
            return 0
        self.frontmatter(path)
        for markdown in markdown_files(path):
            self.markdown(markdown, path)
        license_path = path / "LICENSE.txt"
        if required or license_path.exists() or license_path.is_symlink():
            if not license_path.resolve().is_relative_to(path.resolve()):
                self.error(license_path, "license file escapes package boundary")
            else:
                content = self.read_text(license_path)
                if content is not None and not content.strip():
                    self.error(license_path, "license file must not be empty")
        return self.evaluations(path, required=required, seen_ids=seen_ids)

    def catalog(self, skills: dict[str, Path]) -> list[dict]:
        path = self.root / "catalog.json"
        data = self.read_json(path)
        if data is None:
            return []
        entries = data.get("skills")
        if not isinstance(entries, list):
            self.error(path, "skills must be a list")
            return []
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
            collection = entry.get("collection", "utilities")
            if not isinstance(collection, str) or collection not in COLLECTIONS:
                self.error(path, f"{label}.collection must be one of {sorted(COLLECTIONS)}")
            category = entry.get("category")
            if not isinstance(category, str) or NAME.fullmatch(category) is None:
                self.error(path, f"{label}.category must be a lowercase slug")
            tags = entry.get("tags")
            if not isinstance(tags, list) or not tags or any(
                not isinstance(tag, str) or NAME.fullmatch(tag) is None for tag in tags
            ):
                self.error(path, f"{label}.tags must be a nonempty list of lowercase slugs")
            elif len(set(tags)) != len(tags):
                self.error(path, f"{label}.tags must not contain duplicates")
            basis = entry.get("basis")
            if not isinstance(basis, list) or not basis or any(not isinstance(item, str) or item not in BASIS for item in basis):
                self.error(path, f"{label}.basis must be a nonempty list drawn from {sorted(BASIS)}")
            elif len(set(basis)) != len(basis):
                self.error(path, f"{label}.basis must not contain duplicates")
            status = entry.get("status")
            if not isinstance(status, str) or status not in STATUS:
                self.error(path, f"{label}.status must be one of {sorted(STATUS)}")
            note = entry.get("validation_note")
            if note is not None and name in skills:
                if note != "VALIDATION.md":
                    self.error(path, f"{label}.validation_note must name VALIDATION.md inside its package")
                else:
                    note_path = skills[name] / note
                    if note_path.is_symlink() or not note_path.is_file() or not note_path.resolve().is_relative_to(skills[name].resolve()):
                        self.error(note_path, "portable validation note must be a regular package file")
                        content = None
                    else:
                        content = self.read_text(note_path)
                    if content is not None and re.findall(r"^Status: \*\*([^*]+)\*\*", content, re.MULTILINE) != [status]:
                        self.error(note_path, "portable validation status must match the catalog")
            live = entry.get("live_validation")
            if not isinstance(live, bool):
                self.error(path, f"{label}.live_validation must be a boolean")
            elif live != (status == "live-tested"):
                self.error(path, f"{label}.live_validation must match live-tested status")
            evidence = entry.get("evidence")
            if not isinstance(evidence, list) or any(not isinstance(item, str) or not item.strip() for item in evidence):
                self.error(path, f"{label}.evidence must be a list of nonempty relative paths")
                continue
            promoted = isinstance(status, str) and status in {"offline-reviewed", "live-tested"}
            if promoted and not evidence:
                self.error(path, f"{label} requires evidence for promoted status {status!r}")
            verified_report = False
            for item in evidence:
                parts = Path(item).parts
                if not parts or parts[0] not in {"docs", "evals"} or ".." in parts:
                    self.error(path, f"{label} evidence must name a relative file under docs/ or evals/: {item!r}")
                    continue
                previous_errors = len(self.errors)
                resolved = self.local_target(path, item, self.root)
                if resolved is not None and not resolved.is_file():
                    self.error(path, f"{label} evidence must name a file: {item!r}")
                elif promoted and resolved is not None and resolved.suffix == ".json" and name in skills:
                    verified_report |= self.execution_report(resolved, name, skills[name], status)
                if resolved is None and len(self.errors) == previous_errors:
                    # External/fragment destinations are not evidence files.
                    self.error(path, f"{label} evidence must name an existing local file: {item!r}")
            if promoted and not verified_report:
                self.error(path, f"{label} requires matching structured execution evidence for promoted status")
        for missing in sorted(set(skills) - seen):
            self.error(path, f"skill {missing!r} is missing from catalog")
        return entries

    def execution_report(self, path: Path, name: str, skill: Path, status: str) -> bool:
        previous_errors = len(self.errors)
        data = self.read_json(path)
        if data is None:
            return False
        try:
            if not isinstance(data.get("date"), str):
                raise ValueError
            date.fromisoformat(data["date"])
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", data["date"]) is None:
                raise ValueError
        except ValueError:
            self.error(path, "execution date must be a valid YYYY-MM-DD date")
        expected_mode = "live" if status == "live-tested" else "sandbox"
        if data.get("mode") not in ("live", "sandbox"):
            self.error(path, "execution mode must be 'live' or 'sandbox'")
        if not isinstance(data.get("runtime"), str) or not data["runtime"].strip():
            self.error(path, "execution runtime must be a nonempty string")
        limitations = data.get("limitations")
        if not isinstance(limitations, list) or any(not isinstance(item, str) or not item.strip() for item in limitations):
            self.error(path, "execution limitations must be a list of nonempty strings")
        runs = data.get("runs")
        if not isinstance(runs, list) or not runs:
            self.error(path, "execution runs must be a nonempty list")
            return False
        try:
            fingerprint = package_fingerprint(skill)
        except (OSError, UnicodeError, ValueError, RuntimeError):
            self.error(skill, "cannot fingerprint regular package files")
            return False
        evaluation_data = self.read_json(skill / "evals" / "evals.json", schema_version=False)
        cases = evaluation_data.get("evals", []) if evaluation_data is not None else []
        scenario_ids = {
            case["id"] for case in cases
            if isinstance(case, dict) and isinstance(case.get("id"), str)
        } if isinstance(cases, list) else set()
        matching = False
        for index, run in enumerate(runs):
            label = f"runs[{index}]"
            if not isinstance(run, dict):
                self.error(path, f"{label} must be an object")
                continue
            for field in ("skill", "scenario"):
                if not isinstance(run.get(field), str) or not run[field].strip():
                    self.error(path, f"{label}.{field} must be a nonempty string")
            variant = run.get("variant")
            if variant not in ("with-skill", "baseline"):
                self.error(path, f"{label}.variant must be with-skill or baseline")
            sha = run.get("package_sha256")
            if variant == "with-skill" and (not isinstance(sha, str) or re.fullmatch(r"[0-9a-f]{64}", sha) is None):
                self.error(path, f"{label}.package_sha256 must be a lowercase SHA-256 digest")
            elif variant == "baseline" and sha is not None:
                self.error(path, f"{label}.package_sha256 must be null for a baseline")
            algorithm = run.get("package_fingerprint_algorithm", LEGACY_FINGERPRINT_ALGORITHM)
            if variant == "with-skill" and algorithm not in (FINGERPRINT_ALGORITHM, LEGACY_FINGERPRINT_ALGORITHM):
                self.error(path, f"{label}.package_fingerprint_algorithm must name a supported fingerprint algorithm")
            elif variant == "baseline" and run.get("package_fingerprint_algorithm") is not None:
                self.error(path, f"{label}.package_fingerprint_algorithm must be null for a baseline")
            if not isinstance(run.get("passed"), bool):
                self.error(path, f"{label}.passed must be a boolean")
            assertions = run.get("assertions")
            valid_assertions = isinstance(assertions, dict) and bool(assertions) and all(
                isinstance(key, str) and key.strip() and isinstance(value, bool)
                for key, value in assertions.items()
            )
            if not valid_assertions:
                self.error(path, f"{label}.assertions must be a nonempty object of boolean checks")
            trace = run.get("trace")
            if not isinstance(trace, list) or not trace or any(
                not isinstance(action, dict) or not isinstance(action.get("operation"), str)
                or not action["operation"].strip() or not isinstance(action.get("arguments"), dict)
                for action in trace
            ):
                self.error(path, f"{label}.trace must contain operations and argument objects")
            if not isinstance(run.get("final_state"), dict):
                self.error(path, f"{label}.final_state must be an object")
            # Historical successes remain valid records. Only an explicit current
            # algorithm, package and scenario can establish promotion eligibility.
            if (run.get("skill") == name and variant == "with-skill" and run.get("passed") is True
                    and data.get("mode") == expected_mode and algorithm == FINGERPRINT_ALGORITHM
                    and sha == fingerprint and isinstance(run.get("scenario"), str)
                    and run["scenario"] in scenario_ids and valid_assertions and all(assertions.values())):
                matching = True
        return matching and len(self.errors) == previous_errors

    def evaluations(self, skill: Path, *, required: bool, seen_ids: set[str] | None = None) -> int:
        path = skill / "evals" / "evals.json"
        if not required and not path.exists() and not path.is_symlink():
            return 0
        if not path.resolve().is_relative_to(skill.resolve()):
            self.error(path, "evaluation file escapes package boundary")
            return 0
        data = self.read_json(path, schema_version=False)
        if data is None:
            return 0
        if data.get("skill_name") != skill.name:
            self.error(path, "skill_name must match the skill folder name")
        scenarios = data.get("evals")
        if not isinstance(scenarios, list):
            self.error(path, "evals must be a list")
            return 0
        seen = seen_ids if seen_ids is not None else set()
        coverage: set[str] = set()
        for index, scenario in enumerate(scenarios):
            label = f"evals[{index}]"
            if not isinstance(scenario, dict):
                self.error(path, f"{label} must be an object")
                continue
            identifier = scenario.get("id")
            if not isinstance(identifier, str) or not identifier.strip():
                self.error(path, f"{label}.id must be a nonempty string")
            elif identifier in seen:
                self.error(path, f"duplicate evaluation id {identifier!r}")
            else:
                seen.add(identifier)
            kind = scenario.get("kind")
            if kind not in ("success", "boundary", "routing"):
                self.error(path, f"{label}.kind must be success, boundary, or routing")
            else:
                coverage.add(kind)
            for field in ("prompt", "context", "expected_output"):
                value = scenario.get(field)
                if not isinstance(value, str) or not value.strip():
                    self.error(path, f"{label}.{field} must be a nonempty string")
            for field in ("assertions", "forbidden", "files"):
                value = scenario.get(field)
                if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
                    self.error(path, f"{label}.{field} must be a list of nonempty strings")
                elif field == "assertions" and not value:
                    self.error(path, f"{label}.assertions must not be empty")
                elif field == "files":
                    for item in value:
                        self.fixture(path, skill, item, label)
        for kind in sorted(EVAL_KINDS - coverage):
            self.error(path, f"skill {skill.name!r} requires at least one {kind} evaluation")
        return len(scenarios)

    def fixture(self, source: Path, skill: Path, item: str, label: str) -> None:
        try:
            if Path(item).is_absolute() or "\\" in item or urlsplit(item).scheme or item.startswith("//"):
                self.error(source, f"{label}.files must use relative package paths")
                return
            resolved = (skill / item).resolve()
            if not resolved.is_relative_to(skill.resolve()):
                self.error(source, f"{label} fixture escapes package boundary: {item!r}")
            elif not resolved.is_file():
                self.error(source, f"{label} fixture must name an existing file: {item!r}")
        except (OSError, ValueError, RuntimeError):
            self.error(source, f"{label} fixture path cannot be resolved")

    def repository(self) -> tuple[int, int]:
        skills_root = self.root / "skills"
        skills: dict[str, Path] = {}
        seen_ids: set[str] = set()
        evaluations = 0
        if not skills_root.is_dir():
            self.error(skills_root, "skills directory does not exist")
        else:
            for path in sorted(skills_root.iterdir()):
                if path.name in IGNORED:
                    continue
                if path.is_symlink():
                    self.error(path, "skill folder must not be a symlink")
                    continue
                if not path.is_dir():
                    continue
                skills[path.name] = path
                evaluations += self.skill(path, required=True, seen_ids=seen_ids)
            if not skills:
                self.error(skills_root, "no skill folders found")
        for path in markdown_files(self.root):
            if path.relative_to(self.root).parts[0] != "skills":
                self.markdown(path, self.root)
        self.catalog(skills)
        return len(skills), evaluations


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
    # Code spans can wrap within a paragraph, but cannot span blank block
    # boundaries. Delimiters must be entire backtick runs of equal length.
    # Headings, lists and block quotes can interrupt a paragraph without a
    # blank line. Do not let a delimiter in the preceding block consume them.
    blocks, paragraph = [], []
    def flush() -> None:
        if paragraph:
            blocks.append(strip_inline_code("".join(paragraph)))
            paragraph.clear()
    quote_depth = 0
    for line in text.splitlines(keepends=True):
        quote = re.match(r"^(?: {0,3}>[ \t]?)+", line)
        depth = quote.group().count(">") if quote else 0
        content = line[quote.end():] if quote else line
        interrupt = re.match(r"^ {0,3}(?:#{1,6}(?:[ \t]|$)|(?:[-+*]|[0-9]{1,9}[.)])[ \t])", content)
        standalone = re.match(r"^ {0,3}(?:#{1,6}(?:[ \t]|$)|(?:=+|-+)[ \t]*$|(?:\*[ \t]*){3,}$|(?:_[ \t]*){3,}$)", content)
        # A plain line can lazily continue an open blockquote paragraph.
        if not depth and quote_depth and paragraph and content.strip() and not (interrupt or standalone):
            depth = quote_depth
        if depth != quote_depth or not content.strip() or interrupt or standalone:
            flush()
        paragraph.append(line)
        if not content.strip() or standalone:
            flush()
        quote_depth = depth
    flush()
    text = "".join(blocks)
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


def strip_inline_code(text: str) -> str:
    delimiters = list(re.finditer(r"`+", text))
    next_run: dict[int, int] = {}
    closing: dict[int, int] = {}
    for index in range(len(delimiters) - 1, -1, -1):
        length = len(delimiters[index].group())
        if length in next_run:
            closing[index] = next_run[length]
        next_run[length] = index
    pieces = []
    position = index = 0
    while index < len(delimiters):
        opener = delimiters[index]
        # A backslash escape prevents an opener, but backslashes inside code do
        # not prevent its closing delimiter.
        before = text[:opener.start()]
        escaped = (len(before) - len(before.rstrip("\\"))) % 2
        if escaped or index not in closing:
            index += 1
            continue
        end = delimiters[closing[index]].end()
        pieces.append(text[position:opener.start()])
        pieces.append(re.sub(r"[^\n]", " ", text[opener.start():end]))
        position = end
        index = closing[index] + 1
    pieces.append(text[position:])
    return "".join(pieces)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", type=Path, help="validate one skill without the repository catalog")
    args = parser.parse_args(argv)
    try:
        root = Path(os.path.abspath(args.skill)) if args.skill else Path(__file__).resolve().parent.parent
        validator = Validator(root)
        if args.skill:
            repository_root = Path(__file__).resolve().parent.parent
            required = root.parent.resolve() == (repository_root / "skills").resolve()
            validator.skill(root, required=required)
            summary = f"skill {root.name}"
        else:
            skills, evaluations = validator.repository()
            summary = f"repository ({skills} skills, {evaluations} evaluations)"
    except (OSError, UnicodeError, ValueError, RuntimeError):
        print("ERROR validation data or paths could not be read", file=sys.stderr)
        return 1
    if validator.errors:
        for error in validator.errors:
            print(f"ERROR {error}", file=sys.stderr)
        print(f"Validation failed: {len(validator.errors)} error(s).", file=sys.stderr)
        return 1
    print(f"Validated {summary}. Structural checks only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
