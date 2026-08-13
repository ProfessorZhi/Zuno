"""Verify the semantic closure of the aborted V4.2 Round-006 pilot.

This is a narrow evidence verifier.  It proves that an interrupted operational
pilot is not reported as an architecture result and that no candidate or merge
was silently created.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
EXPECTED = {
    "round_status": "ABORTED_OPERATIONAL_PILOT",
    "workflow_status": "BLOCKED",
    "stop_reason": "WORKFLOW_EXECUTION_BLOCKER",
    "operational_finding": "WF-API-001",
    "architecture_score": "INVALID",
    "architecture_blocker": "NONE_ESTABLISHED",
    "user_gate": "NOT_TRIGGERED",
    "candidate": "NONE",
    "canonical_sync": "NOT_STARTED",
    "main_merge": "NOT_ATTEMPTED",
}


def _load_v42_verifier():
    path = ROOT / "tools/scripts/verify_red_blue_workflow_v42.py"
    spec = importlib.util.spec_from_file_location("verify_red_blue_workflow_v42", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load V4.2 verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_closure(directory: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = directory / "manifest.yaml"
    if not manifest_path.exists():
        return [f"missing required artifact: {manifest_path}"]
    try:
        manifest: Any = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"manifest.yaml is invalid YAML: {exc}"]
    if not isinstance(manifest, dict):
        return ["manifest.yaml must contain a mapping"]
    if manifest.get("workflow_id") != "ZUNO-RED-BLUE-WORKFLOW-V4.2":
        errors.append("closure must belong to ZUNO-RED-BLUE-WORKFLOW-V4.2")
    if manifest.get("round_id") != "RB-WORKFLOW-V4.2-ROUND-006":
        errors.append("closure must belong to RB-WORKFLOW-V4.2-ROUND-006")
    if manifest.get("execution_profile") != "LIVE_ADAPTIVE":
        errors.append("Round-006 closure execution_profile must be LIVE_ADAPTIVE")
    for key, expected in EXPECTED.items():
        if manifest.get(key) != expected:
            errors.append(f"{key} must be {expected}")
    if manifest.get("question_count", 0) != 3:
        errors.append("closure must preserve the three completed live questions")
    if manifest.get("candidate_branch") not in (None, ""):
        errors.append("closure must not contain a candidate branch")
    if manifest.get("candidate_sha") != "NOT_PROVIDED":
        errors.append("closure must not contain a candidate SHA")
    if manifest.get("external_reviewed_sha") != "NOT_PROVIDED":
        errors.append("Round-006 closure must not claim an external review SHA")

    closure_path = directory / "round-closure.md"
    if not closure_path.exists():
        errors.append("missing round-closure.md")
    else:
        closure = closure_path.read_text(encoding="utf-8")
        for marker in (
            "ABORTED_OPERATIONAL_PILOT",
            "WORKFLOW_EXECUTION_BLOCKER",
            "WF-API-001",
            "PA-GAP-001",
            "READY_FOR_BATCH_ADVERSARIAL_PILOT",
            "next_round_started: false",
        ):
            if marker not in closure:
                errors.append(f"round-closure.md must contain {marker}")

    evidence_path = directory / "operational-evidence.md"
    if not evidence_path.exists():
        errors.append("missing operational-evidence.md")
    else:
        evidence = evidence_path.read_text(encoding="utf-8")
        for marker in (
            "workflow_status: BLOCKED",
            "stop_reason: WORKFLOW_EXECUTION_BLOCKER",
            "operational_finding: WF-API-001",
            "architecture_blocker: NONE_ESTABLISHED",
            "architecture_score_valid: false",
        ):
            if marker not in evidence:
                errors.append(f"operational-evidence.md must contain {marker}")

    try:
        v42 = _load_v42_verifier()
        errors.extend(v42.verify_round(directory))
    except Exception as exc:  # pragma: no cover - reports verifier environment failures
        errors.append(f"V4.2 verifier could not run: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Round-006 V4.2 closure semantics")
    parser.add_argument("--round", type=Path, required=True)
    args = parser.parse_args()
    errors = verify_closure(args.round)
    if errors:
        print("RB_R006_CLOSURE_INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("RB_R006_CLOSURE_VALID")
    print("ARCHITECTURE_SCORE: INVALID_WORKFLOW_BLOCKER")
    return 0


if __name__ == "__main__":
    sys.exit(main())
