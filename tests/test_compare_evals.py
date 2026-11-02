"""Public CLI checks using clearly synthetic execution records."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import compare_evals


class ComparisonCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        case = 'sheets-append-timeout'
        definition = compare_evals.sandbox.CASES[case]
        self.report = {'schema_version': 1, 'date': '2026-11-01', 'mode': 'sandbox',
                       'runtime': 'synthetic test runtime', 'runs': []}
        for variant in ('baseline', 'with-skill'):
            self.report['runs'].append({
                'case': case, 'skill': definition['skill'], 'scenario': definition['scenario'],
                'variant': variant, 'model': 'synthetic model',
                'package_sha256': (compare_evals.package_fingerprint(ROOT / 'skills' / definition['skill'])
                                   if variant == 'with-skill' else None),
                'package_fingerprint_algorithm': compare_evals.FINGERPRINT_ALGORITHM,
                'grader_sha256': compare_evals.sandbox.grader_hashes(case),
                'workspace_sha256': hashlib.sha256(variant.encode()).hexdigest(),
                'passed': True, 'assertions': {'synthetic_check': True},
                'trace': [{'operation': 'synthetic_test_only'}], 'final_state': {},
                'comparison': {'cohort': 'synthetic', 'trial': '1', 'task_sha256': 'a'*64,
                               'tools_sha256': 'b'*64, 'baseline_kind': 'no-skill'}})

    def invoke(self):
        path = Path(self.tmp.name) / 'records.json'
        path.write_text(json.dumps(self.report))
        return subprocess.run([sys.executable, str(ROOT / 'scripts/compare_evals.py'), str(path)],
                              capture_output=True, text=True)

    def test_pairs_without_inventing_cost(self):
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['completion_counts'], {'baseline': 1, 'with-skill': 1})
        self.assertEqual(report['pairs'][0]['metrics']['cost_usd'],
                         {'status': 'unmeasured or incomplete'})

    def test_measured_metrics_and_failure_retained(self):
        for run in self.report['runs']:
            run['comparison'].update(measurement_source='synthetic test meter',
                                     metrics={'errors': 1, 'recovered': False, 'cost_usd': 0.25})
        self.report['runs'][0]['passed'] = False
        self.report['runs'][0]['assertions']['synthetic_check'] = False
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['completion_counts']['baseline'], 0)
        self.assertEqual(output['pairs'][0]['metrics']['cost_usd']['baseline'], .25)

    def test_prepare_hashes_public_packets_and_preserves_original(self):
        record = copy.deepcopy(self.report)
        record['runs'] = [record['runs'][0]]
        del record['runs'][0]['comparison']
        source = Path(self.tmp.name) / 'export.json'
        task = Path(self.tmp.name) / 'task.txt'
        tools = Path(self.tmp.name) / 'tools.txt'
        output = Path(self.tmp.name) / 'prepared.json'
        source.write_text(json.dumps(record))
        original = source.read_bytes()
        task.write_text('synthetic task')
        tools.write_text('synthetic tools and fixed model settings')
        command = [sys.executable, str(ROOT / 'scripts/compare_evals.py'), str(source),
                   '--prepare', '--task-packet', str(task), '--tool-manifest', str(tools),
                   '--cohort', 'test', '--trial', '1', '--baseline-no-skill', '--output', str(output)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        meta = json.loads(output.read_text())['runs'][0]['comparison']
        self.assertEqual(meta['task_sha256'], hashlib.sha256(task.read_bytes()).hexdigest())
        self.assertEqual(source.read_bytes(), original)
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)

    def test_rejects_unmatched_stale_incomparable_and_invalid(self):
        original = copy.deepcopy(self.report)
        mutations = [
            lambda r: r['runs'].pop(),
            lambda r: r['runs'][1].update(package_sha256='0'*64),
            lambda r: r['runs'][0].update(grader_sha256={}),
            lambda r: r['runs'][1].update(model='different'),
            lambda r: r['runs'][1]['comparison'].update(task_sha256='c'*64),
            lambda r: r['runs'][0]['comparison'].update(baseline_kind='previous-skill'),
            lambda r: r['runs'][0]['comparison'].update(metrics={'cost_usd': -1}),
            lambda r: r['runs'][0].update(passed=False),
            lambda r: r['runs'].append(copy.deepcopy(r['runs'][0])),
        ]
        for mutate in mutations:
            self.report = copy.deepcopy(original)
            mutate(self.report)
            with self.subTest(mutation=mutate):
                result = self.invoke()
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertIn('error', json.loads(result.stderr))


if __name__ == '__main__':
    unittest.main()
