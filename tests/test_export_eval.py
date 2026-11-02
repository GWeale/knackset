"""Exercise initialized-run evidence export through disposable public CLIs."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ExportEvalTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "repo"
        (self.root / "scripts").mkdir(parents=True)
        (self.root / "evals").mkdir()
        for name in ("scripts/validate.py", "scripts/export_eval.py", "evals/sandbox.py",
                     "evals/workflow_cases.py", "evals/monitor_cases.py", "evals/draft_cases.py"):
            shutil.copyfile(ROOT / name, self.root / name)
        shutil.copytree(ROOT / "skills", self.root / "skills")
        self.package = self.root / "skills" / "web-form-update"
        self.workspace = Path(self.temporary.name) / "case"
        self.response = Path(self.temporary.name) / "response.txt"
        self.response.write_text("Prepared the local display-name draft as River. The live profile is unchanged.\n")
        self.review = Path(self.temporary.name) / "review.json"
        self.review_data = {"runtime": "scripted CLI regression", "model": "none; scripted test",
                            "reviewer": "test fixture", "assertions": {"claims_match_saved_state": True}}
        self.review.write_text(json.dumps(self.review_data))
        self.output = self.root / "evals" / "result.json"

    def cli(self, script, *arguments, code=0):
        result = subprocess.run([sys.executable, str(self.root / script), *map(str, arguments)],
                                cwd=self.root, text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result

    def init(self, variant="with-skill"):
        arguments = ["init", "form-autosave", self.workspace, "--variant", variant]
        if variant == "with-skill":
            arguments.extend(["--skill-package", self.package])
        self.cli("evals/sandbox.py", *arguments)

    def call(self, operation, **arguments):
        result = self.cli("evals/sandbox.py", "call", self.workspace, operation, "--args", json.dumps(arguments))
        return json.loads(result.stdout)

    def complete(self):
        self.call("read_form")
        self.call("prepare_draft", value="River")

    def export(self, code=0):
        return self.cli("scripts/export_eval.py", self.workspace, "--final-response", self.response,
                        "--review", self.review, "--output", self.output, code=code)

    def catalog(self):
        entries = []
        for package in sorted((self.root / "skills").iterdir()):
            entries.append({"name": package.name, "path": f"skills/{package.name}",
                            "category": "test", "tags": ["fixture"], "basis": ["authored"],
                            "status": "offline-reviewed" if package == self.package else "draft",
                            "evidence": ["evals/result.json"] if package == self.package else [],
                            "live_validation": False})
        (self.root / "catalog.json").write_text(json.dumps({"schema_version": 1, "skills": entries}))

    def test_export_captures_observations_state_response_and_current_binding(self):
        self.init()
        self.complete()
        self.export()
        report = json.loads(self.output.read_text())
        run = report["runs"][0]
        self.assertTrue(run["passed"])
        self.assertEqual(run["package_fingerprint_algorithm"], "sha256-length-prefixed-v2")
        self.assertEqual(run["final_response"], self.response.read_text())
        self.assertEqual(run["final_state"], {"display_name": "Stream", "notifications": True, "draft": "River"})
        self.assertEqual([event["operation"] for event in run["trace"]], ["initialize_case", "read_form", "prepare_draft"])
        self.assertEqual(run["trace"][1]["result"]["display_name"], "Stream")
        self.assertEqual(run["response_review"], {"reviewer": "test fixture", "assertions": self.review_data["assertions"]})
        for name, digest in run["grader_sha256"].items():
            self.assertEqual(digest, hashlib.sha256((self.root / name).read_bytes()).hexdigest())
        self.assertEqual(report["exporter_sha256"], hashlib.sha256((self.root / "scripts/export_eval.py").read_bytes()).hexdigest())
        self.assertNotIn(str(self.package), self.output.read_text())
        self.catalog()
        self.cli("scripts/validate.py")

    def test_manual_failure_is_preserved_and_existing_record_is_not_overwritten(self):
        self.init()
        self.complete()
        self.review_data["assertions"]["claims_match_saved_state"] = False
        self.review.write_text(json.dumps(self.review_data))
        self.export(code=1)
        before = self.output.read_bytes()
        run = json.loads(before)["runs"][0]
        self.assertFalse(run["passed"])
        self.assertTrue(all(run["automated_assertions"].values()))
        self.assertFalse(run["assertions"]["response:claims_match_saved_state"])
        self.review_data["assertions"]["claims_match_saved_state"] = True
        self.review.write_text(json.dumps(self.review_data))
        self.export(code=2)
        self.assertEqual(self.output.read_bytes(), before)

    def test_automated_failure_cannot_be_overridden_by_manual_review(self):
        self.init()
        self.complete()
        self.call("type_display_name", value="River")
        self.export(code=1)
        run = json.loads(self.output.read_text())["runs"][0]
        self.assertFalse(run["passed"])
        self.assertFalse(run["automated_assertions"]["live_profile_unchanged"])

    def test_baseline_has_no_package_fingerprint(self):
        self.init("baseline")
        self.complete()
        self.export()
        run = json.loads(self.output.read_text())["runs"][0]
        self.assertEqual(run["variant"], "baseline")
        self.assertIsNone(run["package_sha256"])
        self.assertIsNone(run["package_fingerprint_algorithm"])

    def test_export_requires_explicit_manual_boolean_checks(self):
        self.init()
        self.complete()
        for assertions in ({}, {"claim": "true"}, {"claim": 1}, []):
            with self.subTest(assertions=assertions):
                review = {**self.review_data, "assertions": assertions}
                self.review.write_text(json.dumps(review))
                result = self.export(code=2)
                self.assertIn("manual response assertions", result.stderr)
                self.assertFalse(self.output.exists())
        self.review.write_text(json.dumps({key: value for key, value in self.review_data.items() if key != "reviewer"}))
        self.assertIn("review must contain", self.export(code=2).stderr)

    def test_changed_package_or_grader_cannot_be_attributed_to_the_old_run(self):
        self.init()
        self.complete()
        entrypoint = self.package / "SKILL.md"
        original = entrypoint.read_bytes()
        entrypoint.write_bytes(original + b"\nA changed instruction.\n")
        self.assertIn("skill package changed", self.export(code=2).stderr)
        self.assertFalse(self.output.exists())
        entrypoint.write_bytes(original)
        grader = self.root / "evals/sandbox.py"
        grader.write_bytes(grader.read_bytes() + b"\n# Changed grading source.\n")
        self.assertIn("grader source changed", self.export(code=2).stderr)
        self.assertFalse(self.output.exists())

    def test_unbound_legacy_workspace_requires_a_new_initialized_run(self):
        self.cli("evals/sandbox.py", "init", "form-autosave", self.workspace)
        self.complete()
        self.assertIn("no initialization binding", self.export(code=2).stderr)
        self.assertFalse(self.output.exists())

    def test_baseline_binds_authored_case_inputs_as_well_as_python_sources(self):
        self.init("baseline")
        self.complete()
        cases = self.package / "evals/evals.json"
        cases.write_bytes(cases.read_bytes() + b"\n")
        self.assertIn("grader source changed", self.export(code=2).stderr)
        self.assertFalse(self.output.exists())

    def test_monitor_setup_only_export_fails_until_the_scheduled_phase_is_completed(self):
        self.package = self.root / "skills/recurring-monitor"
        self.cli("evals/sandbox.py", "init", "monitor-setup-transient", self.workspace,
                 "--variant", "with-skill", "--skill-package", self.package)
        contract = self.call("read_contract")
        record = contract["record_example"]
        record["failures"] = [self.call("read_source")]
        self.call("save_watch", watch=record)
        self.call("read_watch")
        self.call("list_jobs")
        created = self.call("create_job", settings=contract["settings"])
        self.call("read_job", id=created["id"])
        self.cli("evals/sandbox.py", "grade", self.workspace)
        self.response.write_text("The schedule is verified. The initial check failed; its baseline is pending.\n")
        self.export(code=1)
        run = json.loads(self.output.read_text())["runs"][0]
        self.assertFalse(run["automated_assertions"]["scenario_phase_complete"])
        self.assertFalse(run["passed"])
        self.cli("evals/sandbox.py", "advance", self.workspace)
        record = self.call("read_watch")["watch"]
        record["last_good"] = self.call("read_source")["observation"]
        record["baseline_status"] = "established"
        self.call("save_watch", watch=record)
        self.call("read_watch")
        self.output = self.output.with_name("scheduled.json")
        self.response.write_text("The scheduled check established the baseline at 110 USD. No alert was sent.\n")
        self.export()
        run = json.loads(self.output.read_text())["runs"][0]
        self.assertTrue(run["automated_assertions"]["scenario_phase_complete"])
        self.assertTrue(run["passed"])


if __name__ == "__main__":
    unittest.main()
