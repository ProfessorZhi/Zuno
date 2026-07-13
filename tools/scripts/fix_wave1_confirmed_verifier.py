from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WAVE_VERIFIER = ROOT / "tools/scripts/verify_wave1_contract_freeze.py"
INFRA_VERIFIER = ROOT / "tools/scripts/verify_infrastructure_target_protocols.py"
INFRA_TESTS = ROOT / "tests/repo/test_infrastructure_target_protocols.py"


def normalize(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace("Wave 1 合并前审计清单", "Wave 1 合并审计清单")
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    for path in [WAVE_VERIFIER, INFRA_VERIFIER, INFRA_TESTS]:
        normalize(path)
        content = path.read_text(encoding="utf-8")
        if "Wave 1 合并审计清单" not in content:
            raise RuntimeError(f"{path}: missing final Wave 1 audit heading")
        if "Wave 1 合并前审计清单" in content:
            raise RuntimeError(f"{path}: stale pre-merge audit heading remains")

    wave = WAVE_VERIFIER.read_text(encoding="utf-8")
    for term in [
        "design available",
        "本 Registry 已随 Wave 1 合并确认为 `CONFIRMED_TARGET`",
        "status = FIELD_FROZEN_PENDING_MERGE",
    ]:
        if term not in wave:
            raise RuntimeError(f"{WAVE_VERIFIER}: missing final-state assertion {term}")

    print("Wave 1 and Infrastructure validation headings normalized.")


if __name__ == "__main__":
    main()
