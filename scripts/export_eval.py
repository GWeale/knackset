#!/usr/bin/env python3
"""Export judge-side offline evidence from an explicitly bound sandbox run.

Initialize with sandbox.py init CASE WORKSPACE --variant with-skill
--skill-package PATH, or --variant baseline. Review JSON must contain runtime,
model, reviewer and a nonempty assertions object whose values are booleans.
The reviewer must supply those response checks; automated grading never invents
them. A failed evaluation is exported with passed=false and exits with status 1.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

from validate import FINGERPRINT_ALGORITHM, package_fingerprint, unique_object, reject_constant

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evals"))
import sandbox


def read_review(path: Path) -> dict:
    review = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object,
                        parse_constant=reject_constant)
    if not isinstance(review, dict) or set(review) != {"runtime", "model", "reviewer", "assertions"}:
        raise ValueError("review must contain runtime, model, reviewer and assertions")
    if any(not isinstance(review[field], str) or not review[field].strip()
           for field in ("runtime", "model", "reviewer")):
        raise ValueError("review runtime, model and reviewer must be nonempty strings")
    assertions = review["assertions"]
    if not isinstance(assertions, dict) or not assertions or any(
        not isinstance(key, str) or not key.strip() or type(value) is not bool
        for key, value in assertions.items()
    ):
        raise ValueError("manual response assertions must be a nonempty object of booleans")
    return review


def build_report(workspace: Path, response_file: Path, review_file: Path) -> dict:
    state = sandbox.load(workspace)
    binding = state.get("evaluation")
    if not isinstance(binding, dict):
        raise ValueError("workspace has no initialization binding; start a fresh run with --variant")
    variant = binding.get("variant")
    if variant not in ("with-skill", "baseline"):
        raise ValueError("invalid initialization variant")
    grader_hashes = sandbox.grader_hashes(state["case"])
    if binding.get("grader_sha256") != grader_hashes:
        raise ValueError("grader source changed since initialization; start a fresh run")
    if variant == "with-skill":
        package = Path(binding["package_path"])
        if (binding.get("package_fingerprint_algorithm") != FINGERPRINT_ALGORITHM
                or package_fingerprint(package) != binding.get("package_sha256")):
            raise ValueError("skill package changed since initialization; start a fresh run")
        if package.name != sandbox.CASES[state["case"]]["skill"]:
            raise ValueError("bound package does not match the case")
    elif any(binding.get(field) is not None for field in
             ("package_path", "package_fingerprint_algorithm", "package_sha256")):
        raise ValueError("baseline initialization must not bind a package")
    response = response_file.read_text(encoding="utf-8")
    if not response.strip():
        raise ValueError("final response must be nonempty")
    review = read_review(review_file)
    result = sandbox.grade(state)
    automated = dict(result["checks"])
    case = sandbox.CASES[state["case"]]
    if "export_requires_phase" in case:
        automated["scenario_phase_complete"] = state["data"].get("phase") == case["export_requires_phase"]
    manual = review["assertions"]
    assertions = {f"automated:{key}": value for key, value in automated.items()}
    assertions.update({f"response:{key}": value for key, value in manual.items()})
    run = {
        "skill": case["skill"], "scenario": case["scenario"], "case": state["case"],
        "variant": variant, "model": review["model"],
        "package_fingerprint_algorithm": binding.get("package_fingerprint_algorithm"),
        "package_sha256": binding.get("package_sha256"),
        "started_at": binding["started_at"], "grader_sha256": grader_hashes,
        "passed": all(assertions.values()), "assertions": assertions,
        "automated_assertions": automated,
        "response_review": {"reviewer": review["reviewer"], "assertions": manual},
        "final_response": response,
        "trace": [{"operation": "initialize_case", "arguments": {"case": state["case"]}}] + state["events"],
        "final_state": state["data"],
        "workspace_sha256": hashlib.sha256(sandbox.state_path(workspace).read_bytes()).hexdigest(),
    }
    return {
        "schema_version": 1, "date": datetime.now(timezone.utc).date().isoformat(), "mode": "sandbox",
        "runtime": review["runtime"],
        "limitations": [
            "Synthetic offline state and operations only; no live service or browser was exercised.",
            "Final-response checks were explicitly supplied by the named reviewer, not inferred by the exporter.",
            "Initialization binds package and grader contents; the mutable local workspace is not a tamper-proof attestation.",
        ],
        "exporter_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "runs": [run],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--final-response", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = build_report(args.workspace, args.final_response, args.review)
        # Never overwrite a prior failure or success record.
        with args.output.open("x", encoding="utf-8") as target:
            json.dump(report, target, indent=2, ensure_ascii=False)
            target.write("\n")
        passed = report["runs"][0]["passed"]
        print(json.dumps({"output": str(args.output), "passed": passed}))
        return 0 if passed else 1
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, RuntimeError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
