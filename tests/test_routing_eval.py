"""Exercise discovery-only packets and score boundaries through the public CLI."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'scripts/routing_eval.py'


class RoutingTests(unittest.TestCase):
    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'FIFO resources require POSIX')
    def test_packet_rejects_special_resources_before_metadata_or_case_reads(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'scripts').mkdir()
            for name in ('routing_eval.py', 'catalog.py', 'validate.py'):
                shutil.copyfile(ROOT / 'scripts' / name, root / 'scripts' / name)
            skill = root / 'skills/sample-flow'
            (skill / 'evals').mkdir(parents=True)
            (skill / 'SKILL.md').write_text('---\nname: sample-flow\ndescription: Inspect a sample.\nlicense: MIT\n---\nInspect the result.\n')
            (skill / 'LICENSE.txt').write_text('MIT License\n')
            (skill / 'evals/evals.json').write_text(json.dumps({'skill_name': 'sample-flow', 'evals': [
                {'id': 'sample-' + kind, 'kind': kind, 'prompt': 'Inspect the item.',
                 'context': 'Fictional supplied input.', 'expected_output': 'A result.',
                 'assertions': ['The result is inspected.'], 'forbidden': [], 'files': []}
                for kind in ('success', 'boundary', 'routing')
            ]}))
            (root / 'catalog.json').write_text(json.dumps({'schema_version': 1, 'skills': [{
                'name': 'sample-flow', 'path': 'skills/sample-flow', 'category': 'research',
                'tags': ['sources'], 'basis': ['authored'], 'status': 'draft',
                'live_validation': False, 'evidence': [],
            }]}))
            (root / 'evals').mkdir()
            (root / 'evals/routing_expected.json').write_text(json.dumps({'sample-routing': {'accepted': [None]}}))
            command = [sys.executable, str(root / 'scripts/routing_eval.py'), 'prepare']
            self.assertEqual(subprocess.run(command, capture_output=True, timeout=2).returncode, 0)
            for relative in ('SKILL.md', 'evals/evals.json'):
                with self.subTest(resource=relative):
                    path = skill / relative
                    content = path.read_bytes()
                    path.unlink()
                    os.mkfifo(path)
                    result = subprocess.run(command, capture_output=True, text=True, timeout=2)
                    self.assertEqual(result.returncode, 2)
                    self.assertIn('regular files', result.stderr)
                    self.assertNotIn('Traceback', result.stderr)
                    path.unlink()
                    path.write_bytes(content)

    def test_packet_withholds_judge_fields_and_grading_rejects_wrong_selection(self):
        result = subprocess.run([sys.executable, str(CLI), 'prepare'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        packet = json.loads(result.stdout)
        declared = json.loads((ROOT / 'catalog.json').read_text())['skills']
        self.assertEqual({item['name'] for item in packet['catalog']},
                         {item['name'] for item in declared})
        expected_routes = json.loads((ROOT / 'evals/routing_expected.json').read_text())
        self.assertEqual(len(packet['tasks']), len(expected_routes))
        self.assertEqual(len({task['id'] for task in packet['tasks']}), len(packet['tasks']))
        for metadata in packet['catalog']:
            self.assertEqual(set(metadata), {'name', 'description'})
        for task in packet['tasks']:
            self.assertEqual(set(task), {'id', 'prompt', 'context'})
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            (path / 'packet.json').write_text(result.stdout)
            responses = {task['id']: {'skill': None, 'reason': 'No matching package.'}
                         for task in packet['tasks']}
            (path / 'responses.json').write_text(json.dumps(responses))
            command = [sys.executable, str(CLI), 'grade', str(path / 'packet.json'),
                       str(path / 'responses.json'), '--runtime', 'synthetic CLI test, no model']
            judged = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(judged.returncode, 1, judged.stderr)
            report = json.loads(judged.stdout)
            self.assertFalse(report['passed'])
            self.assertEqual(report['mode'], 'routing')
            responses.pop(next(iter(responses)))
            (path / 'responses.json').write_text(json.dumps(responses))
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
            packet['catalog'][0]['description'] += ' changed'
            (path / 'packet.json').write_text(json.dumps(packet))
            stale = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(stale.returncode, 2)
            self.assertIn('packet differs', stale.stderr)


if __name__ == '__main__':
    unittest.main()
