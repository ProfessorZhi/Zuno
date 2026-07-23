from __future__ import annotations

import importlib.util
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORK_PRODUCTS = REPO_ROOT / ".agent" / "programs" / "work-products"
MATRIX = WORK_PRODUCTS / "goal01-closure-matrix.md"
LEDGER = WORK_PRODUCTS / "requirement-ledger.yaml"
SOURCE_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase11-ingestion-source-lineage.md"
RUNTIME_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "input-runtime-batch.md"
P11_T04_T07_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase11-p11-t04-t07-runtime.md"
P11_T08_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase11-p11-t08-delete-recovery-cutover.md"
E2E_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase11-e2e-fault.md"


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


def verify_phase11_pre_closure_gate() -> list[str]:
    errors: list[str] = []
    gaps = _phase_target_not_current_requirements(_read(LEDGER), "PHASE11")
    if gaps:
        errors.append("PHASE11 mandatory target_not_current remains: " + ", ".join(gaps))

    source_evidence = _read(SOURCE_EVIDENCE)
    for phrase in ["status: `implementation_available`", "phase_completion: `approved`", "ARCH-ING-001", "ARCH-ING-080"]:
        if phrase not in source_evidence:
            errors.append(f"phase11 source evidence missing phrase: {phrase}")
    runtime_evidence = _read(RUNTIME_EVIDENCE)
    for phrase in ["status: implementation_available", "ARCH-ING-001", "ARCH-ING-080", "Input runtime batch verification passed"]:
        if phrase not in runtime_evidence:
            errors.append(f"input runtime evidence missing phrase: {phrase}")
    for evidence, label, phrases in [
        (P11_T04_T07_EVIDENCE, "P11-T04-T07 evidence", ["status: completion_candidate", "69 passed", "ReviewTask"]),
        (P11_T08_EVIDENCE, "P11-T08 evidence", ["status: completion_candidate", "Delete / Restore", "Legacy upload/parser cutover verifier"]),
        (E2E_EVIDENCE, "PHASE11 E2E evidence", ["status: passed", "120 passed", "P11-T01～P11-T08"]),
    ]:
        text = _read(evidence)
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{label} missing phrase: {phrase}")

    source_errors = _load_function(
        REPO_ROOT / "tools" / "scripts" / "verify_phase11_ingestion_source_lineage.py",
        "verify_phase11_ingestion_source_lineage",
    )()
    errors.extend(f"phase11 source lineage failed: {error}" for error in source_errors)
    try:
        _load_function(
            REPO_ROOT / "tools" / "scripts" / "verify_input_runtime_batch.py",
            "validate_input_runtime_batch",
        )()
    except Exception as exc:
        errors.append(f"input runtime batch failed: {exc}")
    return errors


def main() -> int:
    errors = verify_phase11_pre_closure_gate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE11 pre-closure gate failed.")
        return 1
    print("PHASE11 pre-closure gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
