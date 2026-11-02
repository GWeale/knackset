#!/usr/bin/env python3
"""Compare explicitly paired, current offline execution records (JSON to stdout)."""
from __future__ import annotations

import argparse
import hashlib
from datetime import date
import json
import math
from pathlib import Path
import sys

from validate import FINGERPRINT_ALGORITHM, package_fingerprint, unique_object, reject_constant

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'evals'))
import sandbox


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def compare(paths, root=ROOT):
    pairs = {}
    identities = set()
    for path in paths:
        report = json.loads(Path(path).read_text(), object_pairs_hook=unique_object,
                            parse_constant=reject_constant)
        if not isinstance(report, dict) or report.get('schema_version') != 1 or report.get('mode') != 'sandbox':
            raise ValueError('only schema 1 sandbox execution records are comparable')
        date.fromisoformat(report['date'])
        if not nonempty(report.get('runtime')) or not report.get('runs'):
            raise ValueError('runtime and runs are required')
        if not isinstance(report['runs'], list):
            raise ValueError('runs must be an array')
        for run in report['runs']:
            if not isinstance(run, dict):
                raise ValueError('run must be an object')
            meta = run.get('comparison', {})
            if not isinstance(meta, dict):
                raise ValueError('comparison must be an object')
            if not all(nonempty(meta.get(k)) for k in ('cohort', 'trial', 'task_sha256', 'tools_sha256')):
                raise ValueError('comparison requires cohort, trial, task_sha256 and tools_sha256')
            for field in ('task_sha256', 'tools_sha256'):
                if len(meta[field]) != 64 or any(c not in '0123456789abcdef' for c in meta[field]):
                    raise ValueError(field + ' must be a SHA-256 digest')
            case = run.get('case')
            if case not in sandbox.CASES:
                raise ValueError('unknown runnable case')
            expected = sandbox.CASES[case]
            if run.get('skill') != expected['skill'] or run.get('scenario') != expected['scenario']:
                raise ValueError('case, skill and scenario disagree')
            if run.get('grader_sha256') != sandbox.grader_hashes(case):
                raise ValueError('stale or missing fixture/grader binding')
            variant = run.get('variant')
            if variant == 'with-skill':
                if (run.get('package_fingerprint_algorithm') != FINGERPRINT_ALGORITHM or
                        run.get('package_sha256') != package_fingerprint(root / 'skills' / run['skill'])):
                    raise ValueError('stale or missing package fingerprint')
            elif variant == 'baseline':
                if meta.get('baseline_kind') != 'no-skill' or run.get('package_sha256') is not None:
                    raise ValueError('baseline must explicitly be no-skill')
                if run.get('baseline_kind', 'no-skill') != 'no-skill':
                    raise ValueError('previous-skill baselines cannot be compared as no-skill')
            else:
                raise ValueError('unknown variant')
            assertions = run.get('assertions')
            if (not isinstance(assertions, dict) or not assertions or
                    any(type(v) is not bool for v in assertions.values()) or
                    type(run.get('passed')) is not bool or run['passed'] != all(assertions.values())):
                raise ValueError('passed must agree with nonempty boolean assertions')
            if (not isinstance(run.get('trace'), list) or not run['trace'] or
                    not isinstance(run.get('final_state'), dict) or not nonempty(run.get('model'))):
                raise ValueError('execution trace, saved state and model are required')
            identity = run.get('workspace_sha256')
            if (not nonempty(identity) or len(identity) != 64 or
                    any(c not in '0123456789abcdef' for c in identity) or identity in identities):
                raise ValueError('missing or duplicate workspace identity')
            identities.add(identity)
            metrics = meta.get('metrics', {})
            if not isinstance(metrics, dict) or set(metrics) - {'errors', 'recovered', 'cost_usd'}:
                raise ValueError('unknown comparison metrics')
            if 'errors' in metrics and (type(metrics['errors']) is not int or metrics['errors'] < 0):
                raise ValueError('errors must be a measured nonnegative integer')
            if 'recovered' in metrics and type(metrics['recovered']) is not bool:
                raise ValueError('recovered must be a judged boolean')
            if 'cost_usd' in metrics and (type(metrics['cost_usd']) not in (int, float) or
                    not math.isfinite(metrics['cost_usd']) or metrics['cost_usd'] < 0):
                raise ValueError('cost_usd must be a measured finite nonnegative number')
            if metrics and not nonempty(meta.get('measurement_source')):
                raise ValueError('metrics require a measurement_source')
            key = (meta['cohort'], meta['trial'])
            group = pairs.setdefault(key, {})
            if variant in group:
                raise ValueError('duplicate cohort/trial variant')
            signature = (case, run['skill'], run['scenario'], report['runtime'], run['model'],
                         meta['task_sha256'], meta['tools_sha256'], tuple(sorted(assertions)))
            group[variant] = (signature, run['passed'], metrics)
    if not pairs:
        raise ValueError('no pairs')
    output = []
    for key, group in sorted(pairs.items()):
        if set(group) != {'baseline', 'with-skill'}:
            raise ValueError('unmatched cohort/trial: ' + str(key))
        baseline, candidate = group['baseline'], group['with-skill']
        if baseline[0] != candidate[0]:
            raise ValueError('incomparable task/runtime/model/tools/assertion cohort')
        item = {'cohort': key[0], 'trial': key[1], 'case': baseline[0][0],
                'completion': {'baseline': baseline[1], 'with-skill': candidate[1]}, 'metrics': {}}
        for metric in ('errors', 'recovered', 'cost_usd'):
            a, b = baseline[2].get(metric), candidate[2].get(metric)
            item['metrics'][metric] = ({'baseline': a, 'with-skill': b} if a is not None and b is not None
                                       else {'status': 'unmeasured or incomplete'})
        output.append(item)
    return {'schema_version': 1, 'pairs': output, 'pair_count': len(output),
            'completion_counts': {v: sum(p['completion'][v] for p in output)
                                  for v in ('baseline', 'with-skill')},
            'limitations': ['Descriptive paired observations only; no statistical or causal superiority claim.',
                            'Fresh contexts, randomization, measurement provenance and judge blinding require independent review.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('records', type=Path, nargs='+')
    parser.add_argument('--prepare', action='store_true', help='add pairing metadata to one exported report')
    parser.add_argument('--task-packet', type=Path)
    parser.add_argument('--tool-manifest', type=Path)
    parser.add_argument('--cohort')
    parser.add_argument('--trial')
    parser.add_argument('--baseline-no-skill', action='store_true', help='attest baseline had no skill instructions')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        if args.prepare:
            if (len(args.records) != 1 or not args.task_packet or not args.tool_manifest or
                    not nonempty(args.cohort) or not nonempty(args.trial) or not args.output):
                raise ValueError('prepare requires one record, task-packet, tool-manifest, cohort, trial and output')
            report = json.loads(args.records[0].read_text(), object_pairs_hook=unique_object,
                                parse_constant=reject_constant)
            if report.get('schema_version') != 1 or report.get('mode') != 'sandbox' or len(report.get('runs', [])) != 1:
                raise ValueError('prepare requires a single exported sandbox run')
            run = report['runs'][0]
            if 'comparison' in run:
                raise ValueError('refusing to replace existing comparison metadata')
            if run.get('variant') == 'baseline':
                if not args.baseline_no_skill or run.get('baseline_kind', 'no-skill') != 'no-skill':
                    raise ValueError('baseline requires explicit no-skill attestation; previous-skill is ineligible')
            run['comparison'] = {
                'cohort': args.cohort, 'trial': args.trial,
                'task_sha256': hashlib.sha256(args.task_packet.read_bytes()).hexdigest(),
                'tools_sha256': hashlib.sha256(args.tool_manifest.read_bytes()).hexdigest(),
                'source_report_sha256': hashlib.sha256(args.records[0].read_bytes()).hexdigest(),
            }
            if run.get('variant') == 'baseline':
                run['comparison']['baseline_kind'] = 'no-skill'
            with args.output.open('x', encoding='utf-8') as target:
                json.dump(report, target, indent=2)
                target.write('\n')
            print(json.dumps({'output': str(args.output), 'status': 'prepared; pair validation still required'}))
            return 0
        if any((args.task_packet, args.tool_manifest, args.cohort, args.trial, args.output, args.baseline_no_skill)):
            raise ValueError('preparation options require --prepare')
        print(json.dumps(compare(args.records), indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
