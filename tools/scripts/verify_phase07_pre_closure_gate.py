from __future__ import annotations

import importlib.util
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORK_PRODUCTS = REPO_ROOT / ".agent" / "programs" / "work-products"
MATRIX = WORK_PRODUCTS / "goal01-closure-matrix.md"
LEDGER = WORK_PRODUCTS / "requirement-ledger.yaml"
EVIDENCE = REPO_ROOT / "docs" / "evidence" / "model-gateway-runtime-batch.md"
PHASE06_CLOSURE = REPO_ROOT / "docs" / "evidence" / "phase06-coordinator-closure.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_function(path: Path, function_name: str):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load verifier: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, function_name)


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


def verify_phase07_pre_closure_gate() -> list[str]:
    errors: list[str] = []
    matrix_section = _phase_section(_read(MATRIX), "PHASE07 Runtime Closure Matrix")
    if not matrix_section:
        errors.append("PHASE07 Runtime Closure Matrix section missing")
    elif "`mandatory_open`" in matrix_section:
        errors.append("PHASE07 Runtime Closure Matrix still contains mandatory_open")
    for phrase in [
        "Provider SDK bypass",
        "Trace / Audit 接入",
        "completion_candidate",
        "PHASE06 Coordinator Closure 已批准",
    ]:
        if phrase not in matrix_section:
            errors.append(f"PHASE07 matrix missing phrase: {phrase}")

    gaps = _phase_target_not_current_requirements(_read(LEDGER), "PHASE07")
    if gaps:
        errors.append("PHASE07 mandatory target_not_current remains: " + ", ".join(gaps))

    evidence = _read(EVIDENCE)
    for phrase in [
        "ARCH-MODEL-001",
        "ARCH-MODEL-088",
        "Provider SDK 只存在",
        "Model Gateway runtime batch verification passed",
    ]:
        if phrase not in evidence:
            errors.append(f"model gateway evidence missing phrase: {phrase}")

    closure = _read(PHASE06_CLOSURE)
    for phrase in ["status: approved", "phase06_state: completed"]:
        if phrase not in closure:
            errors.append(f"PHASE06 closure missing phrase: {phrase}")

    runtime_errors = _load_function(
        REPO_ROOT / "tools" / "scripts" / "verify_model_gateway_runtime_batch.py",
        "verify_model_gateway_runtime_batch",
    )()
    errors.extend(f"model gateway runtime batch failed: {error}" for error in runtime_errors)
    bypass_errors = _load_function(
        REPO_ROOT / "tools" / "scripts" / "verify_model_gateway_bypass.py",
        "verify_model_gateway_bypass",
    )(strict=True)
    errors.extend(f"model gateway strict bypass failed: {error}" for error in bypass_errors)
    observability_errors = _load_function(
        REPO_ROOT / "tools" / "scripts" / "verify_phase06_observability_persistence.py",
        "verify_phase06_observability_persistence",
    )()
    errors.extend(f"phase06 observability persistence failed: {error}" for error in observability_errors)
    return errors


def main() -> int:
    errors = verify_phase07_pre_closure_gate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE07 pre-closure gate failed.")
        return 1
    print("PHASE07 pre-closure gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
