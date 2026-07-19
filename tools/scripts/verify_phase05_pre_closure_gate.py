from __future__ import annotations

import importlib.util
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORK_PRODUCTS = REPO_ROOT / ".agent" / "programs" / "work-products"
MATRIX = WORK_PRODUCTS / "goal01-closure-matrix.md"
LEDGER = WORK_PRODUCTS / "requirement-ledger.yaml"
EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase05-security-control-plane.md"


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


def verify_phase05_pre_closure_gate() -> list[str]:
    errors: list[str] = []
    matrix = _read(MATRIX)
    section = _phase_section(matrix, "PHASE05 PEP/PDP Cutover Matrix")
    if not section:
        errors.append("PHASE05 closure matrix section missing")
    for row in [
        "Execute / Side Effect",
        "Approval / Resume",
        "Artifact Read / Download",
        "Citation / Source Access",
        "Admin 管理面：MCP HTTP/SSE + stdio",
        "Admin 管理面：Agent / Tool / Dialog / MCP Agent / LLM / Knowledge / Knowledge File",
        "Secret Lease",
        "Legacy Approval Boolean 到 Decision/Ref",
    ]:
        if row not in section or f"| {row} |" not in section:
            errors.append(f"PHASE05 matrix row missing: {row}")
    if "`mandatory_open`" in section:
        errors.append("PHASE05 matrix still contains mandatory_open")
    if "future_runtime_not_current" not in section or "External Export" not in section:
        errors.append("PHASE05 external export future boundary missing")

    ledger_gaps = _phase_target_not_current_requirements(_read(LEDGER), "PHASE05")
    if ledger_gaps:
        errors.append("PHASE05 mandatory target_not_current remains: " + ", ".join(ledger_gaps))

    evidence = _read(EVIDENCE)
    for phrase in [
        "phase_completion: `not_approved`",
        "canonical_security_guard",
        "temporary.adapter.tool_runtime.approved_bool",
        "删除 Phase 绑定为 `PHASE16`",
        "python tools/scripts/verify_phase05_security_persistence.py",
        "python tools/scripts/verify_phase05_security_eval.py",
    ]:
        if phrase not in evidence:
            errors.append(f"PHASE05 evidence missing phrase: {phrase}")
    for blocker in [
        "尚未覆盖完整 PEP/PDP cutover",
        "Legacy Approval Boolean 到 Decision/Ref 仍是",
    ]:
        if blocker in evidence:
            errors.append(f"PHASE05 evidence still contains pre-closure blocker: {blocker}")

    errors.extend(
        f"PHASE05 security persistence verifier failed: {error}"
        for error in _load_errors(
            "verify_phase05_security_persistence.py",
            "verify_phase05_security_persistence",
        )
    )
    errors.extend(
        f"PHASE05 security eval verifier failed: {error}"
        for error in _load_errors("verify_phase05_security_eval.py", "verify_phase05_security_eval")
    )
    return errors


def main() -> int:
    errors = verify_phase05_pre_closure_gate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE05 pre-closure gate failed.")
        return 1
    print("PHASE05 pre-closure gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
