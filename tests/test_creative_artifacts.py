"""Check physical artifact contracts and preserved input bytes through the CLI."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CLI = Path(__file__).resolve().parents[1] / "evals/creative_artifacts.py"


class CreativeArtifactsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(CLI), *map(str, args)],
                              capture_output=True, text=True, timeout=5)

    def test_complete_vector_passes_and_consequential_changes_fail(self):
        svg = self.root / "card.svg"
        copy = self.root / "copy.txt"
        copy.write_text("Look again.\nKeep the edge.\n")
        original = ('<svg xmlns="http://www.w3.org/2000/svg" width="148mm" height="210mm">'
                    '<text x="10" y="20">Look <tspan>again.</tspan></text>'
                    '<text x="10" y="40">Keep the edge.</text></svg>')
        args = ["--svg", svg, "--width-mm", "148", "--height-mm", "210", "--copy-file", copy, "--no-images"]
        svg.write_text(original)
        self.assertEqual(self.run_cli(*args).returncode, 0)
        for content, diagnostic in (
            (original.replace('148mm', '148px'), 'Physical size differs'),
            (original.replace('Keep the edge.', 'Delete the edge.'), 'Required SVG text missing'),
            (original.replace('</svg>', '<image href="photo.jpg"/></svg>'), 'Image nodes are forbidden'),
        ):
            with self.subTest(diagnostic=diagnostic):
                svg.write_text(content)
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 1)
                self.assertIn(diagnostic, result.stdout)
                self.assertEqual(svg.read_text(), content)

    def test_input_changes_missing_and_added_files_are_detected_without_repair(self):
        inputs = self.root / "sources"
        inputs.mkdir()
        source = inputs / "counts.csv"
        source.write_bytes(b"year,visits\n2025,100\n")
        manifest = self.root / "hashes.json"
        manifest.write_text(json.dumps({source.name: hashlib.sha256(source.read_bytes()).hexdigest()}))
        args = ["--input-root", inputs, "--input-manifest", manifest]
        self.assertEqual(self.run_cli(*args).returncode, 0)
        source.write_bytes(b"year,visits\n2025,101\n")
        result = self.run_cli(*args)
        self.assertEqual(result.returncode, 1)
        self.assertIn('counts.csv', result.stdout)
        self.assertEqual(source.read_bytes(), b"year,visits\n2025,101\n")
        source.unlink()
        self.assertEqual(self.run_cli(*args).returncode, 1)
        (inputs / "extra.txt").write_text("extra")
        self.assertIn('extra.txt', self.run_cli(*args).stdout)

    def test_positioned_line_wraps_preserve_copy_and_styled_word_fragments(self):
        svg = self.root / "wrapped.svg"
        approved = self.root / "copy.txt"
        approved.write_text('Follow the edge. Where does your eye pause?\nKeep reading.\n')
        svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="148mm">'
                       '<text x="10" y="20"><tspan x="10" dy="0">Follow the edge.</tspan>'
                       '<tspan x="10" dy="6.2">Where does your eye pause?</tspan></text>'
                       '<text x="10" y="50">Keep rea<tspan>ding.</tspan></text></svg>')
        result = self.run_cli('--svg', svg, '--copy-file', approved)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_bad_inputs_and_symlinked_sources_fail_cleanly(self):
        svg = self.root / "bad.svg"
        svg.write_text('<svg')
        result = self.run_cli('--svg', svg)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn('Traceback', result.stdout + result.stderr)
        result = self.run_cli('--svg', svg, '--width-mm', 'nan', '--height-mm', '210')
        self.assertEqual(result.returncode, 2)
        actual = self.root / "actual"
        actual.mkdir()
        linked = self.root / "linked"
        linked.symlink_to(actual, target_is_directory=True)
        manifest = self.root / "hashes.json"
        manifest.write_text('{}')
        result = self.run_cli('--input-root', linked, '--input-manifest', manifest)
        self.assertEqual(result.returncode, 1)
        self.assertIn('symlink', result.stdout)

    def test_same_baseline_spans_do_not_invent_word_separators(self):
        svg = self.root / "inline.svg"
        approved = self.root / "copy.txt"
        for body, wanted, exit_code in (
            ('<text y="20">Look<tspan y="20">again.</tspan></text>', 'Look again.', 1),
            ('<text y="20">Keep rea<tspan y="20">ding.</tspan></text>', 'Keep reading.', 0),
            ('<text y="20">Look<tspan y="15" dy="5">again.</tspan></text>', 'Look again.', 1),
        ):
            with self.subTest(body=body):
                svg.write_text('<svg xmlns="http://www.w3.org/2000/svg">' + body + '</svg>')
                approved.write_text(wanted + '\n')
                result = self.run_cli('--svg', svg, '--copy-file', approved)
                self.assertEqual(result.returncode, exit_code, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
