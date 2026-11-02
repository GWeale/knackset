"""Check the copyable contribution recipe through the public helper CLIs."""

import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class AuthoringExampleTests(unittest.TestCase):
    def test_documented_starter_passes_full_repository_checks(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(ROOT / "scripts", root / "scripts")
            shutil.copytree(ROOT / "docs/examples", root / "docs/examples")
            (root / "evals/results").mkdir(parents=True)
            # The generated catalog links to the run index; the fixture has no runs.
            (root / "evals/results/README.md").write_text("# No execution records\n", encoding="utf-8")
            (root / "catalog.json").write_text(
                json.dumps({"schema_version": 1, "skills": []}) + "\n", encoding="utf-8"
            )
            guide = (ROOT / "docs/authoring-example.md").read_text(encoding="utf-8")
            recipe = re.search(r"```bash\n(python3 - <<'PY'\n.*?)\n```", guide, re.DOTALL)
            self.assertIsNotNone(recipe, "The copyable starter recipe is missing")
            copied = subprocess.run(
                ["bash", "-e", "-c", recipe.group(1)], cwd=root,
                text=True, capture_output=True, timeout=15,
            )
            self.assertEqual(copied.returncode, 0, copied.stdout + copied.stderr)
            self.assertIn("Validated repository (1 skills, 3 evaluations)", copied.stdout)
            self.assertIn("Catalog documentation is current", copied.stdout)
            shown = subprocess.run(
                [sys.executable, "scripts/catalog.py", "show", "local-note-update", "--json"],
                cwd=root, text=True, capture_output=True, timeout=10,
            )
            self.assertEqual(shown.returncode, 0, shown.stdout + shown.stderr)
            entry = json.loads(shown.stdout)
            self.assertEqual(entry["status"], "draft")
            self.assertEqual(entry["evidence"], [])
            self.assertFalse(entry["live_validation"])
            self.assertEqual(
                (root / "skills/local-note-update/LICENSE.txt").read_bytes(),
                (ROOT / "LICENSE").read_bytes(),
            )


if __name__ == "__main__":
    unittest.main()
