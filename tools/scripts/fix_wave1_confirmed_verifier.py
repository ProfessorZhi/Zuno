from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WAVE_VERIFIER = ROOT / "tools/scripts/verify_wave1_contract_freeze.py"


def main() -> None:
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

    for required in [
        '"Wave 1 合并审计清单",',
        '"design available",',
        '"本 Registry 已随 Wave 1 合并确认为 `CONFIRMED_TARGET`",',
        '"status = FIELD_FROZEN_PENDING_MERGE",',
    ]:
        if required not in text:
            raise RuntimeError(f"missing normalized verifier term: {required}")

    WAVE_VERIFIER.write_text(text, encoding="utf-8", newline="\n")
    print("Confirmed Wave 1 verifier normalized for final governance state.")


if __name__ == "__main__":
    main()
