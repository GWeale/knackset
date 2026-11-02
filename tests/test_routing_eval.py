"""Exercise discovery-only packets and score boundaries through the public CLI."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'scripts/routing_eval.py'


class RoutingTests(unittest.TestCase):
    def test_packet_withholds_judge_fields_and_grading_rejects_wrong_selection(self):
        result = subprocess.run([sys.executable, str(CLI), 'prepare'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        packet = json.loads(result.stdout)
        self.assertEqual(len(packet['catalog']), 16)
        self.assertEqual(len(packet['tasks']), 16)
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
