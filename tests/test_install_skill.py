"""Exercise project copies, read-only checks and refusal paths through the CLI."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


class InstallSkillCliTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "library"
        self.project = self.base / "project"
        self.project.mkdir()
        (self.root / "scripts").mkdir(parents=True)
        for name in ("install_skill.py", "catalog.py", "validate.py"):
            shutil.copyfile(SCRIPTS / name, self.root / "scripts" / name)
        self.source = self.root / "skills/sample-flow"
        self.contents = {
            "SKILL.md": ('---\nname: sample-flow\ndescription: Inspect a synthetic example.\nlicense: MIT\n---\n'
                         'Use [the rules](references/rules.md). [Limits](VALIDATION.md).\n').encode(),
            "LICENSE.txt": b"MIT License\n",
            "VALIDATION.md": b"Status: **draft**.\n",
            "references/rules.md": b"# Rules\nKeep the selected material intact.\n",
            "assets/raw.bin": bytes(range(32)),
            "scripts/example.py": b"print('example')\n",
            "evals/evals.json": json.dumps({
                "skill_name": "sample-flow", "evals": [
                    {"id": "sample-" + kind, "kind": kind, "prompt": "Inspect the requested item.",
                     "context": "A fictional input.", "expected_output": "A checked result.",
                     "assertions": ["The result matches the request."], "forbidden": [], "files": []}
                    for kind in ("success", "boundary", "routing")
                ],
            }).encode(),
        }
        for relative, content in self.contents.items():
            target = self.source / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        (self.source / "scripts/example.py").chmod(0o755)
        (self.root / "catalog.json").write_text(json.dumps({
            "schema_version": 1, "skills": [{
                "name": "sample-flow", "path": "skills/sample-flow", "collection": "field-kit",
                "category": "creative", "tags": ["example"], "basis": ["authored"],
                "status": "draft", "evidence": [], "live_validation": False,
                "validation_note": "VALIDATION.md",
            }],
        }))

    def run_cli(self, *arguments, project=None, skill="sample-flow", **options):
        return subprocess.run(
            [sys.executable, str(self.root / "scripts/install_skill.py"), skill,
             "--project", str(project or self.project), *arguments],
            cwd=self.base, capture_output=True, text=True, timeout=10, **options,
        )

    def receipt(self, *arguments, **options):
        result = self.run_cli(*arguments, "--json", **options)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        return json.loads(result.stdout)

    def assert_failure(self, result, diagnostic):
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn(diagnostic, result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    @staticmethod
    def snapshot(folder):
        return {str(p.relative_to(folder)): (p.stat().st_mtime_ns, p.read_bytes())
                for p in folder.rglob("*") if p.is_file()}

    def test_preview_keeps_target_unchanged_then_two_complete_copies_match(self):
        planned = self.receipt("--dry-run")
        self.assertEqual(planned["status"], "planned")
        self.assertFalse((self.project / ".agents").exists())
        self.assertFalse((self.root / ".agents").exists())
        first = self.receipt()
        other = self.base / "other-project"
        other.mkdir()
        second = self.receipt(project=other)
        self.assertEqual(first["status"], "installed")
        self.assertEqual(first["files"], {p: hashlib.sha256(b).hexdigest() for p, b in self.contents.items()})
        self.assertEqual(first["file_count"], len(self.contents))
        self.assertEqual(first["package_fingerprint_algorithm"], "sha256-length-prefixed-v2")
        self.assertEqual(first["package_sha256"], second["package_sha256"])
        self.assertEqual(first["manifest_sha256"], second["manifest_sha256"])
        for project in (self.project, other):
            destination = project / ".agents/skills/sample-flow"
            self.assertEqual({str(p.relative_to(destination)): p.read_bytes()
                              for p in destination.rglob("*") if p.is_file()}, self.contents)
            self.assertTrue((destination / "scripts/example.py").stat().st_mode & stat.S_IXUSR)
        before = self.snapshot(self.project)
        checked = self.receipt("--check")
        self.assertEqual(checked["status"], "verified")
        self.assertEqual(checked["files"], first["files"])
        self.assertEqual(before, self.snapshot(self.project))

    def test_existing_copies_are_never_overwritten_including_empty_directories(self):
        for occupied in (False, True):
            project = self.base / str(occupied)
            destination = project / ".agents/skills/sample-flow"
            destination.mkdir(parents=True)
            if occupied:
                (destination / "keep.txt").write_text("existing work")
            before = self.snapshot(project)
            self.assert_failure(self.run_cli(project=project), "already exists")
            self.assertEqual(before, self.snapshot(project))

    def test_check_identifies_edits_missing_and_extra_files_without_writing(self):
        self.assert_failure(self.run_cli("--check"), "not installed")
        self.assertFalse((self.project / ".agents").exists())
        self.receipt()
        destination = self.project / ".agents/skills/sample-flow"
        changes = [("references/rules.md", b"changed"), ("LICENSE.txt", None), ("extra.txt", b"extra")]
        for relative, content in changes:
            with self.subTest(relative=relative):
                target = destination / relative
                old = target.read_bytes() if target.exists() else None
                if content is None:
                    target.unlink()
                else:
                    target.write_bytes(content)
                before = self.snapshot(self.project)
                self.assert_failure(self.run_cli("--check"), relative)
                self.assertEqual(before, self.snapshot(self.project))
                if old is None:
                    target.unlink()
                else:
                    target.write_bytes(old)

    def test_cache_files_are_excluded_but_links_inside_caches_are_rejected(self):
        cache = self.source / "__pycache__"
        cache.mkdir()
        (cache / "example.pyc").write_bytes(b"cache")
        (self.source / "scratch.pyo").write_bytes(b"cache")
        copied = self.receipt()
        self.assertEqual(set(copied["files"]), set(self.contents))
        destination = self.project / ".agents/skills/sample-flow"
        self.assertFalse((destination / "__pycache__").exists())
        (destination / "__pycache__").mkdir()
        (destination / "__pycache__/generated.pyc").write_bytes(b"runtime cache")
        self.receipt("--check")
        (destination / "__pycache__/linked.pyc").symlink_to(self.source / "SKILL.md")
        self.assert_failure(self.run_cli("--check"), "symlink")

    def test_bad_names_and_overlapping_or_missing_projects_write_nothing(self):
        for name in ("../escape", "unknown", "sample-flow/nested"):
            with self.subTest(name=name):
                self.assert_failure(self.run_cli(skill=name), "skill name")
                self.assertFalse((self.project / ".agents").exists())
        for project in (self.root, self.source, self.base):
            self.assert_failure(self.run_cli(project=project), "outside each other")
            self.assertFalse((project / ".agents").exists())
        self.assert_failure(self.run_cli(project=self.base / "missing"), "already be a directory")

    def test_symlinked_targets_and_sources_are_not_followed(self):
        outside = self.base / "outside"
        outside.mkdir()
        (outside / "keep.txt").write_text("untouched")
        for relative in (".agents", ".agents/skills", ".agents/skills/sample-flow"):
            project = self.base / relative.replace("/", "-")
            project.mkdir()
            link = project / relative
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(outside, target_is_directory=True)
            self.assert_failure(self.run_cli(project=project), "symlinks")
            self.assertEqual(sorted(p.name for p in outside.iterdir()), ["keep.txt"])
        source_file = self.source / "references/rules.md"
        source_file.unlink()
        source_file.symlink_to(outside / "keep.txt")
        self.assert_failure(self.run_cli(), "symlink")
        self.assertFalse((self.project / ".agents").exists())

    def test_parent_components_do_not_hide_links_or_missing_directories(self):
        elsewhere = self.base / "elsewhere"
        (elsewhere / "inner").mkdir(parents=True)
        (self.base / "alias").symlink_to(elsewhere / "inner", target_is_directory=True)
        self.assert_failure(self.run_cli(project=self.base / "alias/../project"), "symlinks")
        self.assertFalse((self.project / ".agents").exists())
        self.assertFalse((elsewhere / "project").exists())
        self.assert_failure(self.run_cli(project=self.base / "missing/../project"), "already be a directory")
        self.assertFalse((self.project / ".agents").exists())
        (self.base / "working").mkdir()
        installed = self.receipt(project=Path("working/../project"))
        self.assertEqual(installed["destination"], str(self.project / ".agents/skills/sample-flow"))

    def test_invalid_package_is_rejected_before_creating_destination(self):
        (self.source / "LICENSE.txt").unlink()
        self.assert_failure(self.run_cli(), "LICENSE.txt")
        self.assertFalse((self.project / ".agents").exists())

    @unittest.skipUnless(sys.platform.startswith("linux"), "file-size failure fixture uses Linux resource limits")
    def test_copy_failure_is_reported_and_incomplete_resources_are_not_activated(self):
        import resource
        import signal

        def limit_output_files():
            resource.setrlimit(resource.RLIMIT_FSIZE, (200, 200))
            signal.signal(signal.SIGXFSZ, signal.SIG_IGN)

        # Limit the package copy, without truncating Python's import caches first.
        result = self.run_cli(preexec_fn=limit_output_files,
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assert_failure(result, "incomplete")
        destination = self.project / ".agents/skills/sample-flow"
        self.assertTrue(destination.is_dir())
        self.assertFalse((destination / "SKILL.md").exists())
        self.assert_failure(self.run_cli(), "already exists")


if __name__ == "__main__":
    unittest.main()
