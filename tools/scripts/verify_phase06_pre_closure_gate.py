from __future__ import annotations

import importlib.util
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORK_PRODUCTS = REPO_ROOT / ".agent" / "programs" / "work-products"
MATRIX = WORK_PRODUCTS / "goal01-closure-matrix.md"
LEDGER = WORK_PRODUCTS / "requirement-ledger.yaml"
EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase06-observability-persistence.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_errors(script_name: str, function_name: str) -> list[str]:
    path = REPO_ROOT / "tools" / "scripts" / script_name
    spec = importlib.util.spec_from_file_location(script_name[:-3], path)
    if spec is None or spec.loader is None:
        return [f"cannot load {script_name}"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return list(getattr(module, function_name)())


def _phase_section(text: str, heading: str) -> str:
    match = re.search(rf"(?ms)^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)", text)
    return match.group("body") if match else ""


def _phase_target_not_current_requirements(ledger: str, phase_id: str) -> list[str]:
    gaps: list[str] = []
    for block in re.split(r"\n(?=  - requirement_id: )", ledger):
        if f'target_phase: "{phase_id}"' not in block:
            continue
        if "mandatory: true" not in block:
            continue
        if "current_status: target_not_current" in block:
            match = re.search(r"requirement_id:\s+([A-Z0-9-]+)", block)
            gaps.append(match.group(1) if match else f"unknown {phase_id} requirement")
    return gaps


def verify_phase06_pre_closure_gate() -> list[str]:
    errors: list[str] = []
    matrix = _read(MATRIX)
    section = _phase_section(matrix, "PHASE06 Adapter Cutover Matrix")
    if not section:
        errors.append("PHASE06 closure matrix section missing")
    for row in [
        "Agent",
        "Model",
        "Knowledge",
        "Capability",
        "Tool",
        "Security",
        "Infrastructure",
        "Product Query",
    ]:
        if f"| {row} |" not in section:
            errors.append(f"PHASE06 matrix row missing: {row}")
    if "`mandatory_open`" in section:
        errors.append("PHASE06 matrix still contains mandatory_open")
    for phrase in [
        "record_model_gateway_trace_event",
        "/api/v1/observability/traces/{trace_id}",
        "external sink failure does not roll back local facts",
    ]:
        if phrase not in section:
            errors.append(f"PHASE06 matrix missing phrase: {phrase}")

    ledger_gaps = _phase_target_not_current_requirements(_read(LEDGER), "PHASE06")
    if ledger_gaps:
        errors.append("PHASE06 mandatory target_not_current remains: " + ", ".join(ledger_gaps))

    evidence = _read(EVIDENCE)
    for phrase in [
        "PostgresObservabilityRuntimeAdapter.record_model_gateway_trace_event",
        "/api/v1/observability/traces/{trace_id}",
        "python tools/scripts/verify_phase06_observability_persistence.py",
        "tests/api/test_phase06_observability_query_route.py",
    ]:
        if phrase not in evidence:
            errors.append(f"PHASE06 evidence missing phrase: {phrase}")
    if "phase_completion: `not_approved`" not in evidence and "phase_completion: `approved`" not in evidence:
        errors.append("PHASE06 evidence missing phase completion phrase")
    for blocker in [
        "FastAPI route 尚未接入",
        "完整 Agent、Knowledge、Memory、Capability、Tool、Security、Infrastructure adapter cutover 尚未全部证明",
    ]:
        if blocker in evidence:
            errors.append(f"PHASE06 evidence still contains pre-closure blocker: {blocker}")

    errors.extend(
        f"PHASE06 observability persistence verifier failed: {error}"
        for error in _load_errors(
            "verify_phase06_observability_persistence.py",
            "verify_phase06_observability_persistence",
        )
    )
    return errors


def main() -> int:
    errors = verify_phase06_pre_closure_gate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE06 pre-closure gate failed.")
        return 1
    print("PHASE06 pre-closure gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
