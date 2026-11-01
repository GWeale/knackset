"""Exercise the curated-record helper through its command-line interface."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "skills/session-to-skill/scripts/create_skill.py"


class CreateSkillTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.record_path = self.root / "curated.json"
        self.output = self.root / "drafts"
        self.record = {
            "name": "example-profile-update",
            "description": 'Update a public display name on an example site; use "profile" settings.',
            "site": "example.invalid",
            "preconditions": ["The user requested an update to the public display name."],
            "steps": ["Observe the intended public profile.", "Set the requested display name and save once."],
            "verification": ["Read the saved public profile independently."],
            "recovery": ["If save times out, read the current name before retrying."],
            "evidence": "synthetic",
        }

    def run_cli(self, record: object = None, *, use_default: bool = False) -> subprocess.CompletedProcess[str]:
        self.record_path.write_text(
            json.dumps(self.record if record is None else record), encoding="utf-8",
        )
        command = [sys.executable, str(SCRIPT), str(self.record_path)]
        if not use_default:
            command += ["--output", str(self.output)]
        return subprocess.run(command, cwd=self.root, capture_output=True, text=True, check=False)

    def test_success_creates_reviewable_draft_with_quoted_metadata(self) -> None:
        result = self.run_cli()
        destination = self.output / self.record["name"] / "SKILL.md"
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, f"created: {destination}\n")
        self.assertEqual(result.stderr, "")
        content = destination.read_text(encoding="utf-8")
        metadata = {
            key: json.loads(value.strip())
            for key, value in (line.split(":", 1) for line in content.split("---", 2)[1].strip().splitlines())
        }
        self.assertEqual(metadata, {
            "name": self.record["name"], "description": self.record["description"], "license": "MIT",
        })
        for field in ("preconditions", "steps", "verification", "recovery"):
            for value in self.record[field]:
                self.assertIn(value, content)
        self.assertIn("Status: draft. Live validation: not performed.", content)
        self.assertIn("Source type: synthetic.", content)
        self.assertEqual(list(self.output.iterdir()), [destination.parent])

    def test_default_stays_in_local_drafts(self) -> None:
        result = self.run_cli(use_default=True)
        destination = self.root / ".local/drafts" / self.record["name"] / "SKILL.md"
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(destination.is_file())

    def test_repeat_refuses_to_overwrite_existing_skill(self) -> None:
        self.assertEqual(self.run_cli().returncode, 0)
        destination = self.output / self.record["name"] / "SKILL.md"
        prior_bytes = destination.read_bytes()
        self.record["description"] = "A changed description that must not replace prior work."
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(destination.read_bytes(), prior_bytes)
        self.assertEqual(list(self.output.iterdir()), [destination.parent])

    def test_existing_symlink_is_not_followed_or_replaced(self) -> None:
        self.output.mkdir()
        outside = self.root / "outside"
        skill_path = self.output / self.record["name"]
        skill_path.symlink_to(outside, target_is_directory=True)
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(skill_path.is_symlink())
        self.assertFalse(outside.exists())

    def test_invalid_names_cannot_escape_the_output(self) -> None:
        for name in ("../escape", "/absolute", "upper-Case", "-leading", "trailing-", "two--hyphens", "a" * 65):
            with self.subTest(name=name):
                record = dict(self.record, name=name)
                result = self.run_cli(record)
                self.assertEqual(result.returncode, 2)
                self.assertFalse(self.output.exists())
                self.assertFalse((self.root / "escape").exists())

    def test_unknown_history_field_is_rejected_without_echoing_input(self) -> None:
        sentinel = "PRIVATE-INPUT-MUST-NOT-APPEAR"
        result = self.run_cli(dict(self.record, raw_history=sentinel))
        self.assertEqual(result.returncode, 2)
        self.assertNotIn(sentinel, result.stdout + result.stderr)
        self.assertFalse(self.output.exists())

    def test_invalid_types_lines_and_evidence_are_rejected_before_writing(self) -> None:
        invalid = (
            {"description": 12}, {"description": "x" * 1025},
            {"site": " "}, {"preconditions": "one step"},
            {"steps": []}, {"steps": [12]}, {"steps": [" "]},
            {"steps": ["first\nsecond"]}, {"recovery": ["first\rsecond"]},
            {"verification": ["tab\tcharacter"]}, {"site": "line\u2028separator"},
            {"description": "a --- delimiter"}, {"site": "..."},
            {"evidence": "live-tested"}, {"evidence": ["synthetic"]},
        )
        for patch in invalid:
            with self.subTest(patch=patch):
                result = self.run_cli(dict(self.record, **patch))
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertFalse(self.output.exists())

    def test_duplicate_json_fields_are_rejected(self) -> None:
        text = json.dumps(self.record)
        self.record_path.write_text(text[:-1] + ', "name": "different-name"}', encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(self.record_path), "--output", str(self.output)],
            cwd=self.root, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
