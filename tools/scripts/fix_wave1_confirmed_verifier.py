from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WAVE_VERIFIER = ROOT / "tools/scripts/verify_wave1_contract_freeze.py"
INFRA_VERIFIER = ROOT / "tools/scripts/verify_infrastructure_target_protocols.py"
INFRA_TESTS = ROOT / "tests/repo/test_infrastructure_target_protocols.py"


def normalize_infrastructure_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace("Wave 1 合并前审计清单", "Wave 1 合并审计清单")
    path.write_text(text, encoding="utf-8", newline="\n")


def normalize_wave_verifier() -> None:
    text = WAVE_VERIFIER.read_text(encoding="utf-8")

    # REGISTRY_TERMS must require the active final heading.
    text = text.replace(
        '    "Failure Ownership Matrix",\n    "Wave 1 合并前审计清单",\n]',
        '    "Failure Ownership Matrix",\n    "Wave 1 合并审计清单",\n]',
        1,
    )

    # The unresolved/stale list must continue to reject the historical active heading.
    bad_forbidden = (
        '        "字段级 Contract 尚未全部确认",\n'
        '        "Wave 1 合并审计清单",\n'
        '        "status = FIELD_FROZEN_PENDING_MERGE",'
    )
    good_forbidden = (
        '        "字段级 Contract 尚未全部确认",\n'
        '        "Wave 1 合并前审计清单",\n'
        '        "status = FIELD_FROZEN_PENDING_MERGE",'
    )
    text = text.replace(bad_forbidden, good_forbidden, 1)
    WAVE_VERIFIER.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    normalize_wave_verifier()
    for path in [INFRA_VERIFIER, INFRA_TESTS]:
        normalize_infrastructure_file(path)

    wave = WAVE_VERIFIER.read_text(encoding="utf-8")
    for term in [
        '    "Wave 1 合并审计清单",',
        '        "Wave 1 合并前审计清单",',
        "design available",
        "本 Registry 已随 Wave 1 合并确认为 `CONFIRMED_TARGET`",
        "status = FIELD_FROZEN_PENDING_MERGE",
    ]:
        if term not in wave:
            raise RuntimeError(f"{WAVE_VERIFIER}: missing final-state assertion {term}")

    for path in [INFRA_VERIFIER, INFRA_TESTS]:
        content = path.read_text(encoding="utf-8")
        if "Wave 1 合并审计清单" not in content:
            raise RuntimeError(f"{path}: missing final Wave 1 audit heading")
        if "Wave 1 合并前审计清单" in content:
            raise RuntimeError(f"{path}: stale pre-merge audit heading remains")

    print("Wave 1 final heading and stale-state guards normalized.")


if __name__ == "__main__":
    main()
