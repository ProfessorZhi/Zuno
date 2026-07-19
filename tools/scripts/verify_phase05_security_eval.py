from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase05-security-control-plane.md"
EVAL_TEST = REPO_ROOT / "tests" / "security" / "test_phase05_security_eval_gate.py"
FAULT_TEST = REPO_ROOT / "tests" / "fault" / "security" / "test_phase05_security_sink_fail_closed.py"


def verify_phase05_security_eval() -> list[str]:
    errors: list[str] = []
    if not EVIDENCE.exists():
        return ["missing PHASE05 security evidence document"]
    if not EVAL_TEST.exists():
        errors.append("missing PHASE05 security eval test")
    if not FAULT_TEST.exists():
        errors.append("missing PHASE05 security sink fault test")

    evidence = EVIDENCE.read_text(encoding="utf-8")
    for phrase in [
        "status: partial_implementation_available",
        "phase_completion: `not_approved`",
        "adaptive attack side-effect request must require approval or deny",
        "benign read-only request must preserve utility",
        "security sink outage must fail closed before effect",
        "尚未形成 PHASE05 closure decision",
    ]:
        if phrase not in evidence:
            errors.append(f"PHASE05 security evidence missing phrase: {phrase}")

    if EVAL_TEST.exists():
        eval_test = EVAL_TEST.read_text(encoding="utf-8")
        for phrase in [
            "adaptive_attack",
            "benign_utility",
            "sink_outage_fail_closed",
            "attack_success_rate == 0.0",
            "utility_preserved is True",
        ]:
            if phrase not in eval_test:
                errors.append(f"PHASE05 security eval test missing phrase: {phrase}")
    return errors


def main() -> int:
    errors = verify_phase05_security_eval()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE05 security eval verification failed.")
        return 1
    print("PHASE05 security eval verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
