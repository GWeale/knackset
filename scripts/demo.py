#!/usr/bin/env python3
"""Show timeout recovery with a scripted, isolated offline fixture."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile


SANDBOX = Path(__file__).resolve().parents[1] / "evals" / "sandbox.py"


class DemoError(ValueError):
    pass


def sandbox(*arguments: object, exit_code: int = 0) -> dict:
    result = subprocess.run(
        [sys.executable, str(SANDBOX), *map(str, arguments)],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != exit_code:
        detail = (result.stderr or result.stdout).strip()
        raise DemoError(
            f"sandbox {arguments[0]} returned exit {result.returncode}: {detail}"
        )
    try:
        value = json.loads(result.stdout)
    except ValueError as error:
        raise DemoError(f"sandbox {arguments[0]} returned invalid JSON") from error
    if not isinstance(value, dict):
        raise DemoError(f"sandbox {arguments[0]} did not return an object")
    return value


def call(workspace: Path, operation: str, **arguments: object) -> dict:
    return sandbox("call", workspace, operation, "--args", json.dumps(arguments))


def run_demo() -> str:
    with tempfile.TemporaryDirectory(prefix="knackset-demo-") as temporary:
        reconcile = Path(temporary) / "reconcile"
        retry = Path(temporary) / "blind-retry"
        payload = {"item_id": "P-3", "quantity": 4}

        sandbox("init", "sheets-append-timeout", reconcile)
        task = sandbox("describe", reconcile)["task"]
        call(reconcile, "read_rows")
        saved = call(reconcile, "append", **payload)
        saved_rows = call(reconcile, "read_rows", item_id=payload["item_id"])["rows"]
        safe_grade = sandbox("grade", reconcile)

        sandbox("init", "sheets-append-timeout", retry)
        first_attempt = call(retry, "append", **payload)
        repeated = call(retry, "append", **payload)
        duplicate_rows = call(retry, "read_rows", item_id=payload["item_id"])["rows"]
        retry_grade = sandbox("grade", retry, exit_code=1)

        if (saved["status"] != "timeout" or first_attempt["status"] != "timeout"
                or repeated["status"] != "accepted"):
            raise DemoError("fixture did not produce the expected timeout and retry statuses")
        if (safe_grade["passed"] is not True or len(saved_rows) != 1
                or safe_grade["checks"]["existing_rows_preserved"] is not True):
            raise DemoError("reconciled write did not produce one verified row with existing rows preserved")
        if (retry_grade["passed"] is not False or len(duplicate_rows) != 2
                or retry_grade["checks"]["exactly_one_requested_row"] is not False):
            raise DemoError("blind retry did not fail specifically for duplicate saved rows")

        row = saved_rows[0]
        lines = [
            "Knackset demo: scripted synthetic fixture.",
            f"Task: {task}",
            f"Reconcile first: append returned {saved['status']}.",
            f"Readback: {row['item_id']} quantity={row['quantity']}; saved rows={len(saved_rows)}; "
            f"formula {row['total_formula']}; total={row['total']}.",
            "Verification: PASS; existing rows and formulas preserved.",
            f"Blind retry: append returned {first_attempt['status']}; retry returned {repeated['status']}.",
            f"Readback: saved rows={len(duplicate_rows)}; "
            f"formulas: {', '.join(row['total_formula'] for row in duplicate_rows)}; "
            f"totals={', '.join(str(row['total']) for row in duplicate_rows)}.",
            "Verification: FAIL; exactly_one_requested_row="
            f"{str(retry_grade['checks']['exactly_one_requested_row']).lower()}.",
            "Result: timeout recovery verified; blind retry duplicated the row.",
            "No model or live account used; temporary fixture files removed.",
        ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        print(run_demo())
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, TypeError) as error:
        print(f"ERROR demo could not complete: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
