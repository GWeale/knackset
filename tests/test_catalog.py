"""Exercise catalog discovery, filtering, and rendering through the public CLI."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


class CatalogCliTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "scripts").mkdir()
        for name in ("catalog.py", "validate.py"):
            shutil.copyfile(SCRIPTS / name, self.root / "scripts" / name)
        self.entries = [
            self.entry("beta-flow", "research", ["sources", "compare"]),
            self.entry("alpha-flow", "web", ["forms", "verify"]),
        ]
        self.write_skill("alpha-flow", "Update a form, then verify its saved state.")
        self.write_skill("beta-flow", "Compare primary sources and report uncertainty.")
        self.write_catalog()

    @staticmethod
    def entry(name, category, tags):
        return {
            "name": name, "path": f"skills/{name}", "category": category, "tags": tags,
            "basis": ["authored"], "status": "draft", "live_validation": False, "evidence": [],
        }

    def write_skill(self, name, description):
        skill = self.root / "skills" / name
        skill.mkdir(parents=True, exist_ok=True)
        (skill / "SKILL.md").write_text(
            f"---\nname: {json.dumps(name)}\ndescription: {json.dumps(description)}\nlicense: MIT\n---\n"
            "Inspect the requested target and resulting state.\n", encoding="utf-8",
        )

    def write_catalog(self):
        (self.root / "catalog.json").write_text(
            json.dumps({"schema_version": 1, "skills": self.entries}), encoding="utf-8",
        )

    def run_cli(self, *arguments):
        return subprocess.run(
            [sys.executable, str(self.root / "scripts/catalog.py"), *arguments],
            cwd=self.root, text=True, capture_output=True, timeout=10,
        )

    def json_result(self, *arguments):
        result = self.run_cli(*arguments, "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        return json.loads(result.stdout)

    def assert_failure(self, result, diagnostic, code=1):
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertIn(diagnostic, result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_list_is_sorted_and_reads_descriptions_from_skills(self):
        entries = self.json_result("list")
        self.assertEqual([entry["name"] for entry in entries], ["alpha-flow", "beta-flow"])
        self.assertEqual(entries[0]["category"], "web")
        self.assertEqual(entries[0]["tags"], ["forms", "verify"])
        self.write_skill("alpha-flow", "A revised source description.")
        self.assertEqual(self.json_result("list")[0]["description"], "A revised source description.")
        self.assertIn("alpha-flow [web; draft]", self.run_cli("list").stdout)

    def test_filters_apply_exact_category_tag_and_status(self):
        self.assertEqual([entry["name"] for entry in self.json_result("list", "--category", "web")], ["alpha-flow"])
        self.assertEqual([entry["name"] for entry in self.json_result("list", "--tag", "sources")], ["beta-flow"])
        self.assertEqual(len(self.json_result("list", "--status", "draft")), 2)
        self.assertEqual(self.json_result("list", "--status", "live-tested"), [])
        self.assertEqual(self.json_result("list", "--category", "web", "--tag", "sources"), [])
        self.assertEqual(self.run_cli("list", "--tag", "unknown").stdout, "No skills matched.\n")

    def test_search_matches_all_keywords_across_name_description_and_tags(self):
        self.assertEqual([entry["name"] for entry in self.json_result("search", "ALPHA verify")], ["alpha-flow"])
        self.assertEqual([entry["name"] for entry in self.json_result("search", "primary compare")], ["beta-flow"])
        self.assertEqual(self.json_result("search", "primary", "--category", "web"), [])
        self.assertEqual(self.json_result("search", "saved", "--tag", "forms", "--status", "draft")[0]["name"], "alpha-flow")

    def test_show_returns_one_record_and_unknown_name_fails_cleanly(self):
        entry = self.json_result("show", "beta-flow")
        self.assertEqual(entry["name"], "beta-flow")
        self.assertEqual(entry["description"], "Compare primary sources and report uncertainty.")
        self.assertIn("path: skills/beta-flow", self.run_cli("show", "beta-flow").stdout)
        self.assert_failure(self.run_cli("show", "missing"), "unknown skill name")

    def test_render_and_check_detect_metadata_drift(self):
        self.assert_failure(self.run_cli("render", "--check"), "is stale")
        self.write_skill("alpha-flow", "Inspect A | B before saving.")
        rendered = self.run_cli("render")
        self.assertEqual(rendered.returncode, 0, rendered.stderr)
        output = self.root / "docs/catalog.md"
        content = output.read_text(encoding="utf-8")
        self.assertIn("[alpha-flow](../skills/alpha-flow/SKILL.md)", content)
        self.assertIn("| web | draft | forms, verify | Inspect A \\| B before saving. |", content)
        self.assertEqual(self.run_cli("render", "--check").returncode, 0)
        self.write_skill("alpha-flow", "Changed source text.")
        self.assert_failure(self.run_cli("render", "--check"), "is stale")
        self.assertEqual(self.run_cli("render").returncode, 0)
        self.assertIn("Changed source text.", output.read_text(encoding="utf-8"))

    def test_bad_arguments_and_bad_data_do_not_traceback(self):
        self.assert_failure(self.run_cli("search", "  "), "must contain a keyword", code=2)
        self.assert_failure(self.run_cli("list", "--category", "Not a slug"), "lowercase slug", code=2)
        self.assert_failure(self.run_cli("list", "--status", "published"), "invalid choice", code=2)
        self.assert_failure(self.run_cli("show"), "required", code=2)
        self.entries[0]["tags"] = ["compare", "compare"]
        self.write_catalog()
        self.assert_failure(self.run_cli("list"), "must not contain duplicates")
        (self.root / "catalog.json").write_text("not JSON", encoding="utf-8")
        self.assert_failure(self.run_cli("list"), "invalid JSON")

    def test_invalid_frontmatter_is_not_silently_rendered(self):
        skill = self.root / "skills/alpha-flow/SKILL.md"
        skill.write_text("---\nname: alpha-flow\ndescription: [not a string]\nlicense: MIT\n---\nAct.\n", encoding="utf-8")
        self.assert_failure(self.run_cli("render"), "unsupported value")
        self.assertFalse((self.root / "docs/catalog.md").exists())


if __name__ == "__main__":
    unittest.main()
