"""Exercise the validator's public CLI against isolated synthetic repositories."""

import copy
import hashlib
import json
import os
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
        (self.skill / "LICENSE.txt").write_text("MIT License\nSynthetic copyright notice.\n", encoding="utf-8")
        (self.root / "docs").mkdir()
        (self.root / "docs" / "review.md").write_text("# Review\n", encoding="utf-8")
        (self.root / "README.md").write_text("[Skill](skills/sample-flow/SKILL.md#workflow)\n", encoding="utf-8")
        self.catalog = {
            "schema_version": 1,
            "skills": [{
                "name": "sample-flow", "path": "skills/sample-flow",
                "basis": ["authored"], "status": "draft",
                "evidence": [], "live_validation": False,
                "category": "web", "tags": ["forms", "verification"],
            }],
        }
        self.scenarios = {
            "skill_name": "sample-flow",
            "evals": [self.scenario("ordinary", "success"), self.scenario("uncertain", "boundary"),
                      self.scenario("near-miss", "routing")],
        }
        self.write_records()

    @staticmethod
    def scenario(identifier, kind):
        return {
            "id": identifier, "kind": kind,
            "prompt": "Update the requested record.", "context": "A synthetic fixture is open.",
            "expected_output": "The resulting state is independently checked.",
            "assertions": ["The saved result is observed."],
            "forbidden": ["Repeat an uncertain submission."],
            "files": [],
        }

    def write_skill(self, frontmatter=None, body="# Workflow\nInspect the result.\n"):
        frontmatter = frontmatter or "name: sample-flow\ndescription: Complete a sample workflow.\nlicense: MIT\n"
        (self.skill / "SKILL.md").write_text(f"---\n{frontmatter}---\n{body}", encoding="utf-8")

    def write_records(self):
        (self.root / "catalog.json").write_text(json.dumps(self.catalog), encoding="utf-8")
        (self.skill / "evals").mkdir(exist_ok=True)
        (self.skill / "evals" / "evals.json").write_text(json.dumps(self.scenarios), encoding="utf-8")

    def test_portable_validation_note_must_match_catalog_status(self):
        self.catalog["skills"][0]["validation_note"] = "VALIDATION.md"
        self.write_records()
        note = self.skill / "VALIDATION.md"
        note.write_text("Status: **offline-reviewed**.\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(self.root / "scripts/validate.py")],
                                text=True, capture_output=True, cwd=self.root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("portable validation status must match", result.stdout + result.stderr)
        note.write_text("Status: **draft**.\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(self.root / "scripts/validate.py")],
                                text=True, capture_output=True, cwd=self.root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_declared_portable_note_cannot_be_missing(self):
        self.catalog["skills"][0]["validation_note"] = "VALIDATION.md"
        self.write_records()
        result = subprocess.run([sys.executable, str(self.root / "scripts/validate.py")],
                                text=True, capture_output=True, cwd=self.root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("VALIDATION.md", result.stdout + result.stderr)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO resource requires POSIX")
    def test_declared_portable_note_rejects_fifo_without_reading(self):
        self.catalog["skills"][0]["validation_note"] = "VALIDATION.md"
        self.write_records()
        os.mkfifo(self.skill / "VALIDATION.md")
        result = self.run_cli()
        self.assert_failure(result, "portable validation note must be a regular package file")

    def fingerprint(self):
        # Independent fixture calculation; production code is exercised via CLI.
        digest = hashlib.sha256(b"knackset-package\0sha256-length-prefixed-v2\0")
        files = sorted(file for file in self.skill.rglob("*") if file.is_file())
        for file in files:
            if "__pycache__" in file.parts or file.suffix in {".pyc", ".pyo"}:
                continue
            for value in (file.relative_to(self.skill).as_posix().encode("utf-8"), file.read_bytes()):
                digest.update(len(value).to_bytes(8, "big"))
                digest.update(value)
        return digest.hexdigest()

    def execution_report(self):
        return {
            "schema_version": 1, "date": "2026-11-01", "mode": "sandbox",
            "runtime": "synthetic fixture runner", "limitations": ["No live account was exercised."],
            "runs": [{
                "skill": "sample-flow", "scenario": "ordinary", "variant": "with-skill",
                "package_fingerprint_algorithm": "sha256-length-prefixed-v2",
                "package_sha256": self.fingerprint(), "passed": True,
                "assertions": {"saved_result_observed": True},
                "trace": [{"operation": "read", "arguments": {"target": "synthetic"}}],
                "final_state": {"saved": True},
            }],
        }

    def write_report(self, report):
        destination = self.root / "evals" / "results.json"
        destination.parent.mkdir(exist_ok=True)
        destination.write_text(json.dumps(report), encoding="utf-8")

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
        self.catalog["skills"][0].update(status="offline-reviewed", evidence=["evals/results.json"])
        self.write_records()
        self.write_report(self.execution_report())
        ignored = self.root / ".local"
        ignored.mkdir()
        (ignored / "private.md").write_text("[Ignored](missing.md)", encoding="utf-8")
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("1 skills, 3 evaluations", result.stdout)
        self.assertIn("Structural checks only", result.stdout)

    def test_standalone_does_not_require_repository_records(self):
        self.write_skill('name: "sample-flow"\ndescription: "Check: a value, then verify it."\nlicense: "MIT"\n')
        standalone = self.root / "drafts" / "sample-flow"
        standalone.parent.mkdir()
        shutil.copytree(self.skill, standalone)
        shutil.rmtree(standalone / "evals")
        (standalone / "LICENSE.txt").unlink()
        result = self.run_cli("--skill", standalone)
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
            ('name: sample-flow\ndescription: "bad\\u007fvalue"\nlicense: MIT\n', "unsupported value"),
        ]
        for frontmatter, diagnostic in cases:
            with self.subTest(frontmatter=frontmatter):
                self.write_skill(frontmatter)
                self.assert_failure(self.run_cli("--skill", self.skill), diagnostic)

    def test_links_cannot_escape_or_point_to_missing_files(self):
        outside = self.root / "outside.md"
        outside.write_text("Outside the skill package.\n", encoding="utf-8")
        for destination, diagnostic in [
            ("missing.md#heading", "does not exist"),
            ("../../outside.md", "escapes package boundary"),
            ("%2e%2e/%2e%2e/outside.md", "escapes package boundary"),
            (str(outside), "absolute"),
        ]:
            with self.subTest(destination=destination):
                self.write_skill(body=f"[Target]({destination})\n")
                self.assert_failure(self.run_cli("--skill", self.skill), diagnostic)
        (self.skill / "escaped.md").symlink_to(outside)
        self.assert_failure(self.run_cli("--skill", self.skill), "symlink")
        (self.skill / "escaped.md").unlink()
        (self.root / "README.md").write_text("[Missing](docs/missing.md)\n", encoding="utf-8")
        self.write_skill()
        self.assert_failure(self.run_cli(), "README.md:1")
        (self.root / "README.md").write_text("[Nul](docs/%00.md)\n", encoding="utf-8")
        self.assert_failure(self.run_cli(), "control character")

    def test_catalog_requires_exact_membership_evidence_and_live_status(self):
        original = copy.deepcopy(self.catalog)
        changes = [
            (lambda entry: entry.update(status="offline-reviewed"), "requires evidence"),
            (lambda entry: entry.update(live_validation=True), "must match live-tested status"),
            (lambda entry: entry.update(status="live-tested", evidence=["docs/review.md"]), "must match live-tested status"),
            (lambda entry: entry.update(evidence=["README.md"]), "under docs/ or evals/"),
            (lambda entry: entry.update(evidence=["docs/missing.md"]), "does not exist"),
            (lambda entry: entry.update(path="skills/other"), ".path must be"),
            (lambda entry: entry.update(category="Not a slug"), ".category must be"),
            (lambda entry: entry.update(collection="unknown"), ".collection must be"),
            (lambda entry: entry.update(collection=[]), ".collection must be"),
            (lambda entry: entry.update(tags=[]), ".tags must be"),
            (lambda entry: entry.update(tags=["forms", "forms"]), ".tags must not contain duplicates"),
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

    def test_evaluations_require_coverage_unique_ids_and_observable_expectations(self):
        original = copy.deepcopy(self.scenarios)
        self.scenarios["evals"].pop()
        self.write_records()
        self.assert_failure(self.run_cli(), "requires at least one routing evaluation")
        self.scenarios = copy.deepcopy(original)
        self.scenarios["evals"][1]["id"] = "ordinary"
        self.write_records()
        self.assert_failure(self.run_cli(), "duplicate evaluation id")
        self.scenarios = copy.deepcopy(original)
        self.scenarios["evals"][0]["assertions"] = []
        self.write_records()
        self.assert_failure(self.run_cli(), "assertions must not be empty")
        self.scenarios = copy.deepcopy(original)
        self.scenarios["skill_name"] = "unknown"
        self.write_records()
        self.assert_failure(self.run_cli(), "skill_name must match")

    def test_repository_packages_require_own_evaluations_and_license(self):
        (self.skill / "LICENSE.txt").unlink()
        self.assert_failure(self.run_cli("--skill", self.skill), "LICENSE.txt")
        (self.skill / "LICENSE.txt").write_text("MIT License\n", encoding="utf-8")
        (self.skill / "evals" / "evals.json").unlink()
        archive = self.root / "evals" / "archive"
        archive.mkdir(parents=True)
        (archive / "scenarios-v0.json").write_text(json.dumps(self.scenarios), encoding="utf-8")
        self.assert_failure(self.run_cli(), "evals/evals.json")

    def test_evaluation_fields_and_fixture_boundaries(self):
        original = copy.deepcopy(self.scenarios)
        fixture = self.skill / "evals" / "sample.json"
        fixture.write_text('{}', encoding="utf-8")
        self.scenarios["evals"][0]["files"] = ["evals/sample.json"]
        self.write_records()
        self.assertEqual(self.run_cli().returncode, 0)
        patches = [
            ({"prompt": " "}, ".prompt must be"),
            ({"context": None}, ".context must be"),
            ({"expected_output": []}, ".expected_output must be"),
            ({"kind": []}, ".kind must be"),
            ({"forbidden": "no"}, ".forbidden must be"),
            ({"files": [12]}, ".files must be"),
            ({"files": ["evals/missing.json"]}, "existing file"),
            ({"files": ["../../docs/review.md"]}, "escapes package boundary"),
            ({"files": [str(self.root / "docs/review.md")]}, "relative package paths"),
        ]
        for patch, diagnostic in patches:
            with self.subTest(patch=patch):
                self.scenarios = copy.deepcopy(original)
                self.scenarios["evals"][0].update(patch)
                self.write_records()
                self.assert_failure(self.run_cli(), diagnostic)
        fixture.unlink()
        fixture.symlink_to(self.root / "docs" / "review.md")
        self.scenarios = copy.deepcopy(original)
        self.scenarios["evals"][0]["files"] = ["evals/sample.json"]
        self.write_records()
        self.assert_failure(self.run_cli(), "symlink")

    def test_evaluation_identifiers_are_unique_across_packages(self):
        second = self.root / "skills" / "another-flow"
        shutil.copytree(self.skill, second)
        (second / "SKILL.md").write_text(
            "---\nname: another-flow\ndescription: Another workflow.\nlicense: MIT\n---\nObserve results.\n",
            encoding="utf-8",
        )
        record = copy.deepcopy(self.scenarios)
        record["skill_name"] = "another-flow"
        (second / "evals/evals.json").write_text(json.dumps(record), encoding="utf-8")
        entry = dict(self.catalog["skills"][0], name="another-flow", path="skills/another-flow")
        self.catalog["skills"].append(entry)
        self.write_records()
        self.assert_failure(self.run_cli(), "duplicate evaluation id")

    def test_status_promotion_requires_current_successful_execution_evidence(self):
        self.catalog["skills"][0].update(status="offline-reviewed", evidence=["evals/results.json"])
        self.write_records()
        original = self.execution_report()
        self.write_report(original)
        self.assertEqual(self.run_cli().returncode, 0)
        patches = [
            (lambda report: report.update(mode="unknown"), "execution mode must be"),
            (lambda report: report.update(mode="live"), "matching structured execution evidence"),
            (lambda report: report.update(date="2026-02-30"), "valid YYYY-MM-DD"),
            (lambda report: report["runs"][0].update(package_sha256="0" * 64), "matching structured execution evidence"),
            (lambda report: report["runs"][0].update(package_fingerprint_algorithm="unknown"), "supported fingerprint algorithm"),
            (lambda report: report["runs"][0].update(package_fingerprint_algorithm=[]), "supported fingerprint algorithm"),
            (lambda report: report["runs"][0].update(passed=False), "matching structured execution evidence"),
            (lambda report: report["runs"][0].update(skill="another-flow"), "matching structured execution evidence"),
            (lambda report: report["runs"][0].update(scenario="unknown-case"), "matching structured execution evidence"),
            (lambda report: report["runs"][0].update(assertions={}), "nonempty object of boolean checks"),
            (lambda report: report["runs"][0].update(assertions={"check": "true"}), "boolean checks"),
            (lambda report: report["runs"][0].update(assertions={"check": False}), "matching structured execution evidence"),
        ]
        for patch, diagnostic in patches:
            with self.subTest(diagnostic=diagnostic):
                report = copy.deepcopy(original)
                patch(report)
                self.write_report(report)
                self.assert_failure(self.run_cli(), diagnostic)
        self.catalog["skills"][0].update(evidence=["docs/review.md"])
        self.write_records()
        self.assert_failure(self.run_cli(), "matching structured execution evidence")

    def test_live_status_requires_live_report_and_cache_files_do_not_change_fingerprint(self):
        self.catalog["skills"][0].update(status="live-tested", live_validation=True, evidence=["evals/results.json"])
        self.write_records()
        report = self.execution_report()
        report["mode"] = "live"
        self.write_report(report)
        cache = self.skill / "__pycache__"
        cache.mkdir()
        (cache / "scratch.pyc").write_bytes(b"cache")
        (self.skill / "scratch.pyo").write_bytes(b"cache")
        self.assertEqual(self.run_cli().returncode, 0)
        (self.skill / "added.txt").write_text("Material package change.\n", encoding="utf-8")
        self.assert_failure(self.run_cli(), "matching structured execution evidence")

    def test_changed_file_layout_cannot_reuse_execution_evidence(self):
        self.catalog["skills"][0].update(status="offline-reviewed", evidence=["evals/results.json"])
        self.write_records()
        (self.skill / "a").write_bytes(b"x\0b\0y")
        self.write_report(self.execution_report())
        self.assertEqual(self.run_cli().returncode, 0)
        (self.skill / "a").write_bytes(b"x")
        (self.skill / "b").write_bytes(b"y")
        self.assert_failure(self.run_cli(), "matching structured execution evidence")

    def test_historical_successes_can_coexist_with_a_current_retest(self):
        self.catalog["skills"][0].update(status="offline-reviewed", evidence=["evals/results.json"])
        self.write_records()
        report = self.execution_report()
        historical = copy.deepcopy(report["runs"][0])
        historical.update(package_sha256="0" * 64, scenario="retired-scenario")
        report["runs"].insert(0, historical)
        self.write_report(report)
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report["runs"].pop()
        self.write_report(report)
        self.assert_failure(self.run_cli(), "matching structured execution evidence")

    def test_legacy_fingerprint_records_are_preserved_but_cannot_promote(self):
        self.catalog["skills"][0].update(status="offline-reviewed", evidence=["evals/results.json"])
        self.write_records()
        current = self.execution_report()
        for algorithm in (None, "sha256-nul-delimited-v1"):
            with self.subTest(algorithm=algorithm):
                report = copy.deepcopy(current)
                if algorithm is None:
                    del report["runs"][0]["package_fingerprint_algorithm"]
                else:
                    report["runs"][0]["package_fingerprint_algorithm"] = algorithm
                # Even a copied current digest cannot promote without v2's label.
                self.write_report(report)
                self.assert_failure(self.run_cli(), "matching structured execution evidence")
                report["runs"].append(current["runs"][0])
                self.write_report(report)
                result = self.run_cli()
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                # Historical records still have to contain structurally valid proof.
                report["runs"][0]["trace"] = []
                self.write_report(report)
                self.assert_failure(self.run_cli(), "trace must contain operations")

    def test_historical_report_can_remain_beside_a_qualifying_report(self):
        self.catalog["skills"][0].update(
            status="offline-reviewed", evidence=["evals/results.json", "evals/historical.json"],
        )
        self.write_records()
        self.write_report(self.execution_report())
        historical = self.execution_report()
        historical["runs"][0].update(package_sha256="0" * 64, scenario="retired")
        del historical["runs"][0]["package_fingerprint_algorithm"]
        (self.root / "evals" / "historical.json").write_text(json.dumps(historical), encoding="utf-8")
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_all_package_statuses_reject_unreferenced_resource_symlinks(self):
        external = self.root / "external"
        external.mkdir()
        (external / "helper.py").write_text("pass\n", encoding="utf-8")
        for status in ("draft", "offline-reviewed"):
            self.catalog["skills"][0].update(status=status, evidence=["evals/results.json"])
            self.write_records()
            self.write_report(self.execution_report())
            for target in (external / "helper.py", external, self.skill / "LICENSE.txt", external / "missing"):
                with self.subTest(status=status, target=target):
                    resource = self.skill / "unreferenced"
                    resource.symlink_to(target)
                    try:
                        self.assert_failure(self.run_cli(), "symlink")
                    finally:
                        resource.unlink()

    def test_package_entrypoint_and_ignored_caches_reject_symlinks(self):
        external = self.root / "external.md"
        external.write_text("---\nname: sample-flow\ndescription: Example.\nlicense: MIT\n---\nValid body.\n")
        for name in ("SKILL.md", "scratch.pyc", "__pycache__", ".local"):
            with self.subTest(name=name):
                resource = self.skill / name
                previous = resource.read_bytes() if resource.exists() else None
                if previous is not None:
                    resource.unlink()
                resource.symlink_to(external)
                try:
                    self.assert_failure(self.run_cli("--skill", self.skill), "symlink")
                finally:
                    resource.unlink()
                    if previous is not None:
                        resource.write_bytes(previous)

    def test_package_special_files_are_rejected_without_reading_them(self):
        for name in ("helper.pipe", "SKILL.md", "evals/evals.json"):
            with self.subTest(name=name):
                resource = self.skill / name
                previous = resource.read_bytes() if resource.exists() else None
                if previous is not None:
                    resource.unlink()
                os.mkfifo(resource)
                try:
                    self.assert_failure(self.run_cli(), "regular files and directories")
                finally:
                    resource.unlink()
                    if previous is not None:
                        resource.write_bytes(previous)

    def test_direct_entrypoint_rejects_symlinked_package_root(self):
        alias = self.root / "drafts" / "sample-flow"
        alias.parent.mkdir()
        alias.symlink_to(self.skill, target_is_directory=True)
        self.assert_failure(self.run_cli("--skill", alias), "symlink")
        alias.unlink()
        alias.parent.rmdir()
        alias.parent.symlink_to(self.skill.parent, target_is_directory=True)
        self.assert_failure(self.run_cli("--skill", alias), "symlink")

    def test_inline_code_cannot_hide_links_across_paragraphs_or_mismatched_runs(self):
        for body in (
            "An unmatched ` opener.\n\n[Broken](missing.md)\n\nAnother ` opener.\n",
            "An unmatched ` opener.\n \t\n[Broken](missing.md)\n\nAnother ` opener.\n",
            "An unmatched `` opener [Broken](missing.md) closes with `.\n",
            "An unmatched ` opener [Broken](missing.md) closes with ``.\n",
            "An unmatched ` opener\n# Heading [Broken](missing.md)\nclosing `\n",
            "An unmatched ` opener\n- [Broken](missing.md)\nclosing `\n",
            "An unmatched ` opener\n1. [Broken](missing.md)\nclosing `\n",
            "An unmatched ` opener\n> [Broken](missing.md)\nclosing `\n",
        ):
            with self.subTest(body=body):
                self.write_skill(body=body)
                self.assert_failure(self.run_cli(), "does not exist")

    def test_genuine_inline_code_spans_hide_example_links(self):
        self.write_skill(body=(
            "A `[Example](missing.md)` inline example.\n\n"
            "A ``[Example](missing.md) with a ` literal`` example.\n\n"
            "A ``[Example](missing.md) with ``` literals`` example.\n\n"
            "A `multiline\n[Example](missing.md)` example.\n"
            "\n> A `multiline\n> [Example](missing.md)` quoted example.\n"
            "\n> A `multiline\n[Example](missing.md)` lazy quoted example.\n"
        ))
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_duplicate_json_and_empty_body_fail_cleanly(self):
        record = self.skill / "evals" / "evals.json"
        text = record.read_text(encoding="utf-8")
        record.write_text(text[:-1] + ', "skill_name": "sample-flow"}', encoding="utf-8")
        self.assert_failure(self.run_cli(), "duplicate JSON object field")
        self.write_records()
        self.write_skill(body="\n")
        self.assert_failure(self.run_cli(), "body must contain instructions")


if __name__ == "__main__":
    unittest.main()
