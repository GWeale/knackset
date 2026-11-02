#!/usr/bin/env python3
"""Prepare description-only routing inputs and score a saved selection, offline."""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import sys

from validate import Validator

ROOT = Path(__file__).resolve().parents[1]


def packet() -> tuple[dict, dict]:
    validator = Validator(ROOT)
    catalog = []
    tasks = []
    expected = json.loads((ROOT / 'evals/routing_expected.json').read_text())
    for folder in sorted((ROOT / 'skills').iterdir()):
        if not folder.is_dir() or folder.name.startswith('.'):
            continue
        metadata = validator.frontmatter(folder)
        catalog.append({key: metadata[key] for key in ('name', 'description')})
        cases = json.loads((folder / 'evals/evals.json').read_text())['evals']
        for case in cases:
            if case['kind'] == 'routing':
                tasks.append({'id': f'R{len(tasks) + 1:02d}', 'prompt': case['prompt'],
                              'context': case['context']})
                if case['id'] not in expected:
                    raise ValueError('routing case has no judge expectations')
                expected[tasks[-1]['id']] = {'scenario': case['id'], **expected.pop(case['id'])}
    if validator.errors:
        raise ValueError('\n'.join(validator.errors))
    if set(expected) != {task['id'] for task in tasks}:
        raise ValueError('routing expectations do not match current cases')
    return {'schema_version': 1, 'catalog': catalog, 'tasks': tasks}, expected


def sha256(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('prepare', help='print the input packet; contains no skill bodies or judge fields')
    score = commands.add_parser('grade', help='judge a saved description-only selection')
    score.add_argument('packet', type=Path)
    score.add_argument('responses', type=Path)
    score.add_argument('--runtime', required=True)
    args = parser.parse_args()
    try:
        current, expected = packet()
        if args.command == 'prepare':
            print(json.dumps(current, indent=2, ensure_ascii=False))
            return 0
        supplied = json.loads(args.packet.read_text())
        if supplied != current:
            raise ValueError('packet differs from the current descriptions or prompts; retain old results and prepare a new run')
        responses = json.loads(args.responses.read_text())
        if not isinstance(responses, dict) or set(responses) != set(expected):
            raise ValueError('responses must contain exactly one entry per task ID')
        names = {item['name'] for item in current['catalog']}
        results = []
        for task in current['tasks']:
            response = responses[task['id']]
            if not isinstance(response, dict) or set(response) != {'skill', 'reason'}:
                raise ValueError('each response needs skill (name or null) and reason')
            selection = response['skill']
            if selection is not None and (not isinstance(selection, str) or selection not in names):
                raise ValueError('skill must be a listed name or null for an external workflow')
            if not isinstance(response['reason'], str) or not response['reason'].strip():
                raise ValueError('each response needs a nonempty reason')
            judge = expected[task['id']]
            results.append({**task, 'scenario': judge['scenario'], 'selection': response,
                            'accepted': judge['accepted'], 'passed': selection in judge['accepted']})
        if not args.runtime.strip():
            raise ValueError('runtime must identify the actual selection agent')
        report = {'schema_version': 1, 'date': date.today().isoformat(), 'mode': 'routing',
                  'runtime': args.runtime, 'packet_sha256': sha256(current), 'input': current,
                  'passed': all(item['passed'] for item in results), 'results': results,
                  'limitations': ['Description-only selection; no skill body, service, or host activation is tested.',
                                  'The judge checks chosen names. Review the reasons and the agent read trace separately.',
                                  'This record does not qualify a package for execution promotion.']}
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if report['passed'] else 1
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'ERROR {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
