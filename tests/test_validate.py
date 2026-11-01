"""Exercise the validator's public CLI against isolated synthetic repositories."""

import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


VALIDATOR = Path(__file__).resolve().parents[1] / "scripts" / "validate.py"


class ValidateCliTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "repo"
        (self.root / "scripts").mkdir(parents=True)
        shutil.copyfile(VALIDATOR, self.root / "scripts" / "validate.py")
        self.skill = self.root / "skills" / "sample-flow"
        self.skill.mkdir(parents=True)
        self.write_skill()
        (self.root / "docs").mkdir()
        (self.root / "docs" / "review.md").write_text("# Review\n", encoding="utf-8")
        (self.root / "README.md").write_text("[Skill](skills/sample-flow/SKILL.md#workflow)\n", encoding="utf-8")
        self.catalog = {
            "schema_version": 1,
            "skills": [{
                "name": "sample-flow", "path": "skills/sample-flow",
                "basis": ["authored"], "status": "draft",
                "evidence": [], "live_validation": False,
            }],
        }
        self.scenarios = {
            "schema_version": 1,
            "scenarios": [self.scenario("ordinary", "success"), self.scenario("uncertain", "boundary")],
        }
        self.write_records()

    @staticmethod
    def scenario(identifier, kind):
        return {
            "id": identifier, "skill": "sample-flow", "kind": kind,
            "prompt": "Update the requested record.", "context": "A synthetic fixture is open.",
            "expected": ["The resulting state is independently checked."],
            "forbidden": ["Repeat an uncertain submission."],
        }

    def write_skill(self, frontmatter=None, body="# Workflow\nInspect the result.\n"):
        frontmatter = frontmatter or "name: sample-flow\ndescription: Complete a sample workflow.\nlicense: MIT\n"
        (self.skill / "SKILL.md").write_text(f"---\n{frontmatter}---\n{body}", encoding="utf-8")

    def write_records(self):
        (self.root / "catalog.json").write_text(json.dumps(self.catalog), encoding="utf-8")
        (self.root / "evals").mkdir(exist_ok=True)
        (self.root / "evals" / "scenarios.json").write_text(json.dumps(self.scenarios), encoding="utf-8")

    def run_cli(self, *arguments):
        return subprocess.run(
            [sys.executable, str(self.root / "scripts" / "validate.py"), *map(str, arguments)],
            cwd=self.root, text=True, capture_output=True, timeout=10,
        )

    def assert_failure(self, result, message):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(message, result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_valid_repository_links_and_promoted_evidence(self):
        references = self.skill / "references"
        references.mkdir()
        (references / "a guide.md").write_text("# Details\n", encoding="utf-8")
        self.write_skill(body=(
            "# Workflow\n[Guide](references/a%20guide.md#details)\n"
            "![Guide](<references/a guide.md>)\n[reference][guide]\n"
            "[guide]: references/a%20guide.md#details\n"
            "[Multiline](\nreferences/a%20guide.md#details\n)\n"
            "[Online](https://example.com/anything) [Here](#workflow)\n"
            "`[example](missing.md)`\n```markdown\n[example](missing.md)\n```\n"
        ))
        self.catalog["skills"][0].update(status="offline-reviewed", evidence=["docs/review.md"])
        self.write_records()
        ignored = self.root / ".local"
        ignored.mkdir()
        (ignored / "private.md").write_text("[Ignored](missing.md)", encoding="utf-8")
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("1 skills, 2 scenarios", result.stdout)
        self.assertIn("Structural checks only", result.stdout)

    def test_standalone_does_not_require_repository_records(self):
        (self.root / "catalog.json").unlink()
        shutil.rmtree(self.root / "evals")
        self.write_skill('name: "sample-flow"\ndescription: "Check: a value, then verify it."\nlicense: "MIT"\n')
        result = self.run_cli("--skill", self.skill)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Validated skill sample-flow", result.stdout)

    def test_bad_names_and_unsupported_frontmatter_are_rejected(self):
        cases = [
            ("name: Sample-flow\ndescription: Work.\nlicense: MIT\n", "lowercase"),
            ("name: sample--flow\ndescription: Work.\nlicense: MIT\n", "single internal hyphens"),
            ("name: different\ndescription: Work.\nlicense: MIT\n", "match folder name"),
            ("name: sample-flow\ndescription: [Work]\nlicense: MIT\n", "unsupported value"),
            ("name: sample-flow\ndescription: Work.\nlicense: MIT\nmetadata:\n  status: draft\n", "unsupported frontmatter"),
            ("name: sample-flow\ndescription: Work.\nlicense: MIT\nlicense: MIT\n", "duplicate frontmatter"),
            ("name: sample-flow\ndescription: Work.\nlicense: Apache-2.0\n", "license must be MIT"),
            ("name: sample-flow\ndescription: false\nlicense: MIT\n", "unsupported value"),
            ('name: sample-flow\ndescription: "   "\nlicense: MIT\n', "1..1024"),
            (f'name: sample-flow\ndescription: "{"x" * 1025}"\nlicense: MIT\n', "1..1024"),
            (f'name: {"a" * 65}\ndescription: Work.\nlicense: MIT\n', "1..64"),
        ]
        for frontmatter, diagnostic in cases:
            with self.subTest(frontmatter=frontmatter):
                self.write_skill(frontmatter)
                self.assert_failure(self.run_cli("--skill", self.skill), diagnostic)

    def test_links_cannot_escape_or_point_to_missing_files(self):
        outside = self.root / "outside.md"
        outside.write_text("Outside the skill package.\n", encoding="utf-8")
        (self.skill / "escaped.md").symlink_to(outside)
        for destination, diagnostic in [
            ("missing.md#heading", "does not exist"),
            ("../../outside.md", "escapes package boundary"),
            ("%2e%2e/%2e%2e/outside.md", "escapes package boundary"),
            ("escaped.md", "escapes package boundary"),
            (str(outside), "absolute"),
        ]:
            with self.subTest(destination=destination):
                # Keep the symlink for the target check, but avoid scanning its contents.
                self.write_skill(body=f"[Target]({destination})\n")
                self.assert_failure(self.run_cli("--skill", self.skill), diagnostic)
        (self.skill / "escaped.md").unlink()
        (self.root / "README.md").write_text("[Missing](docs/missing.md)\n", encoding="utf-8")
        self.write_skill()
        self.assert_failure(self.run_cli(), "README.md:1")

    def test_catalog_requires_exact_membership_evidence_and_live_status(self):
        original = copy.deepcopy(self.catalog)
        changes = [
            (lambda entry: entry.update(status="offline-reviewed"), "requires evidence"),
            (lambda entry: entry.update(live_validation=True), "must match live-tested status"),
            (lambda entry: entry.update(status="live-tested", evidence=["docs/review.md"]), "must match live-tested status"),
            (lambda entry: entry.update(evidence=["README.md"]), "under docs/ or evals/"),
            (lambda entry: entry.update(evidence=["docs/missing.md"]), "does not exist"),
            (lambda entry: entry.update(path="skills/other"), ".path must be"),
        ]
        for change, diagnostic in changes:
            with self.subTest(diagnostic=diagnostic):
                self.catalog = copy.deepcopy(original)
                change(self.catalog["skills"][0])
                self.write_records()
                self.assert_failure(self.run_cli(), diagnostic)
        self.catalog = copy.deepcopy(original)
        self.catalog["skills"].append(copy.deepcopy(self.catalog["skills"][0]))
        self.write_records()
        self.assert_failure(self.run_cli(), "listed more than once")
        self.catalog["skills"] = []
        self.write_records()
        self.assert_failure(self.run_cli(), "missing from catalog")

    def test_scenarios_require_coverage_unique_ids_and_observable_expectations(self):
        original = copy.deepcopy(self.scenarios)
        self.scenarios["scenarios"].pop()
        self.write_records()
        self.assert_failure(self.run_cli(), "requires at least one boundary scenario")
        self.scenarios = copy.deepcopy(original)
        self.scenarios["scenarios"][1]["id"] = "ordinary"
        self.write_records()
        self.assert_failure(self.run_cli(), "duplicate scenario id")
        self.scenarios = copy.deepcopy(original)
        self.scenarios["scenarios"][0]["expected"] = []
        self.write_records()
        self.assert_failure(self.run_cli(), "expected must not be empty")
        self.scenarios = copy.deepcopy(original)
        self.scenarios["scenarios"][0]["skill"] = "unknown"
        self.write_records()
        self.assert_failure(self.run_cli(), "must name an existing skill")


if __name__ == "__main__":
    unittest.main()
