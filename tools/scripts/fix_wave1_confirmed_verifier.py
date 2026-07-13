from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WAVE_VERIFIER = ROOT / "tools/scripts/verify_wave1_contract_freeze.py"
INFRA_VERIFIER = ROOT / "tools/scripts/verify_infrastructure_target_protocols.py"
INFRA_TESTS = ROOT / "tests/repo/test_infrastructure_target_protocols.py"


def normalize_wave_verifier() -> None:
    text = WAVE_VERIFIER.read_text(encoding="utf-8")
    text = text.replace('"Wave 1 合并前审计清单",', '"Wave 1 合并审计清单",')
    text = text.replace('"design field freeze complete",', '"design available",\n    "本 Registry 已随 Wave 1 合并确认为 `CONFIRMED_TARGET`",')

    anchor = '''    forbidden_unresolved_phrases = [
        "协调状态：`CONFLICT_REQUIRES_DECISION`",
        "本文件当前所有条目最高只能是 `ALIGNED_PENDING_FIELDS`",
        "字段级 Contract 尚未全部确认",
    ]
'''
    replacement = '''    forbidden_unresolved_phrases = [
        "协调状态：`CONFLICT_REQUIRES_DECISION`",
        "本文件当前所有条目最高只能是 `ALIGNED_PENDING_FIELDS`",
        "字段级 Contract 尚未全部确认",
        "Wave 1 合并前审计清单",
        "status = FIELD_FROZEN_PENDING_MERGE",
        "PR #17 合并后，本 Registry 状态应更新为",
    ]
'''
    if replacement not in text:
        if anchor not in text:
            raise RuntimeError("Wave 1 verifier unresolved-phrase block changed unexpectedly")
        text = text.replace(anchor, replacement, 1)

    WAVE_VERIFIER.write_text(text, encoding="utf-8", newline="\n")


def normalize_infrastructure_validation() -> None:
    verifier = INFRA_VERIFIER.read_text(encoding="utf-8")
    verifier = verifier.replace('"Wave 1 合并前审计清单",', '"Wave 1 合并审计清单",')
    if '"本 Registry 已随 Wave 1 合并确认为 `CONFIRMED_TARGET`",' not in verifier:
        anchor = '    "Wave 1 合并审计清单",\n]'
        replacement = (
            '    "Wave 1 合并审计清单",\n'
            '    "本 Registry 已随 Wave 1 合并确认为 `CONFIRMED_TARGET`",\n'
            ']'
        )
        if anchor not in verifier:
            raise RuntimeError("Infrastructure verifier Registry term list changed unexpectedly")
        verifier = verifier.replace(anchor, replacement, 1)
    INFRA_VERIFIER.write_text(verifier, encoding="utf-8", newline="\n")

    tests = INFRA_TESTS.read_text(encoding="utf-8")
    tests = tests.replace('"Wave 1 合并前审计清单",', '"Wave 1 合并审计清单",')
    if '"本 Registry 已随 Wave 1 合并确认为 `CONFIRMED_TARGET`",' not in tests:
        anchor = '        "Wave 1 合并审计清单",\n        "ALIGNED_PENDING_FIELDS",'
        replacement = (
            '        "Wave 1 合并审计清单",\n'
            '        "本 Registry 已随 Wave 1 合并确认为 `CONFIRMED_TARGET`",\n'
            '        "ALIGNED_PENDING_FIELDS",'
        )
        if anchor not in tests:
            raise RuntimeError("Infrastructure focused test term list changed unexpectedly")
        tests = tests.replace(anchor, replacement, 1)
    INFRA_TESTS.write_text(tests, encoding="utf-8", newline="\n")


def main() -> None:
    normalize_wave_verifier()
    normalize_infrastructure_validation()

    for path, required_terms in [
        (
            WAVE_VERIFIER,
            [
                "Wave 1 合并审计清单",
                "design available",
                "本 Registry 已随 Wave 1 合并确认为 `CONFIRMED_TARGET`",
                "status = FIELD_FROZEN_PENDING_MERGE",
            ],
        ),
        (
            INFRA_VERIFIER,
            ["Wave 1 合并审计清单", "本 Registry 已随 Wave 1 合并确认为 `CONFIRMED_TARGET`"],
        ),
        (
            INFRA_TESTS,
            ["Wave 1 合并审计清单", "本 Registry 已随 Wave 1 合并确认为 `CONFIRMED_TARGET`"],
        ),
    ]:
        content = path.read_text(encoding="utf-8")
        for term in required_terms:
            if term not in content:
                raise RuntimeError(f"{path}: missing normalized term {term}")

    print("Wave 1 and Infrastructure validation normalized for final governance state.")


if __name__ == "__main__":
    main()
