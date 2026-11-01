"""Exercise the demonstration through its public CLI in an unrelated directory."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "demo.py"


class DemoCliTests(unittest.TestCase):
    def test_demo_observes_timeout_recovery_and_duplicates_without_leaving_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            result = subprocess.run(
                [sys.executable, str(SCRIPT)], cwd=workspace,
                env={**os.environ, "TMPDIR": temporary},
                capture_output=True, text=True, timeout=20,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertIn("scripted synthetic fixture", result.stdout)
            self.assertIn("Reconcile first: append returned timeout.", result.stdout)
            self.assertIn("P-3 quantity=4; saved rows=1; formula =B4*10; total=40.", result.stdout)
            self.assertIn("Verification: PASS; existing rows and formulas preserved.", result.stdout)
            self.assertIn("Blind retry: append returned timeout; retry returned accepted.", result.stdout)
            self.assertIn("saved rows=2; formulas: =B4*10, =B5*10; totals=40, 40.", result.stdout)
            self.assertIn("Verification: FAIL; exactly_one_requested_row=false.", result.stdout)
            self.assertIn("temporary fixture files removed", result.stdout)
            self.assertLessEqual(len(result.stdout.splitlines()), 10)
            self.assertEqual(list(workspace.iterdir()), [])

    def test_missing_sandbox_reports_failure_without_a_traceback(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            scripts = workspace / "scripts"
            scripts.mkdir()
            isolated_script = scripts / "demo.py"
            isolated_script.write_bytes(SCRIPT.read_bytes())
            result = subprocess.run(
                [sys.executable, str(isolated_script)], cwd=workspace,
                env={**os.environ, "TMPDIR": temporary},
                capture_output=True, text=True, timeout=20,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "")
            self.assertIn("ERROR demo could not complete: sandbox init returned exit", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(list(workspace.iterdir()), [scripts])


if __name__ == "__main__":
    unittest.main()
