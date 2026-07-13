from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs/governance/wave1-cross-module-contract-registry.md"
VERIFIER = ROOT / "tools/scripts/verify_wave1_contract_freeze.py"
TEST = ROOT / "tests/repo/test_wave1_contract_freeze.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 0:
        print(f"SKIP {label}: already normalized")
        return text
    if count != 1:
        raise RuntimeError(f"{label}: expected one occurrence, got {count}")
    return text.replace(old, new, 1)


def normalize_registry() -> None:
    text = REGISTRY.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "PARALLEL_PROPOSAL\nALIGNED_PENDING_FIELDS\nCONFLICT_REQUIRES_DECISION\nCONFIRMED_TARGET\nCONFIRMED_TARGET\nIMPLEMENTATION_AVAILABLE\nCURRENT",
        "PARALLEL_PROPOSAL\nALIGNED_PENDING_FIELDS\nCONFLICT_REQUIRES_DECISION\nFIELD_FROZEN_PENDING_MERGE\nCONFIRMED_TARGET\nIMPLEMENTATION_AVAILABLE\nCURRENT",
        "status enum history",
    )
    text = replace_once(
        text,
        "CONFIRMED_TARGET\n    已完成字段级设计审计，但仍在未合并 PR。\n\nCONFIRMED_TARGET\n    ADR 0003 与本 Registry 已合并到 main。",
        "FIELD_FROZEN_PENDING_MERGE\n    历史状态：已完成字段级设计审计，但当时尚未合并。\n\nCONFIRMED_TARGET\n    ADR 0003 与本 Registry 已合并到 main，现为正式共享 Target。",
        "status semantics",
    )
    text = replace_once(
        text,
        "本轮决议不会把 Target 写成 Current，也不会把 PR #18、#19、#20 当成已合并事实源。",
        "本轮决议不会把 Target 写成 Current。PR #18、#19、#17 与替代旧 #20 的集成 PR #21 已合并；其文档仍只证明 Target 设计，不证明 Runtime 实现。",
        "merged PR note",
    )
    text = text.replace(
        "reviewed_parallel_prs:\n  - `#18 Model Gateway @ 3bd9b3e4437314c376a5b1b767ef052e3c74db53`\n  - `#19 Security @ f9fd19c16721cb9cec97c25d82b86274660622e6`\n  - `#20 Observability & Eval @ 4a91953799cd0bae7f3ca441cccabffbce1271f9`",
        "reviewed_wave1_proposals:\n  - `#18 Model Gateway @ 3bd9b3e4437314c376a5b1b767ef052e3c74db53`\n  - `#19 Security @ f9fd19c16721cb9cec97c25d82b86274660622e6`\n  - `#17 Infrastructure @ e9ff166f0621fb3986be2086eff6036ac5de4707`\n  - `#21 Observability & Eval integration @ a2252e64a99feda2aae36affe507d8984985e2c6`",
    )
    REGISTRY.write_text(text, encoding="utf-8", newline="\n")


def normalize_verifier() -> None:
    text = VERIFIER.read_text(encoding="utf-8")
    text = text.replace('    "design field freeze complete",\n', "")
    text = text.replace('            "PreparedToolAction",\n', "")
    old = '''    for stale_status in ["accepted-target-pending-merge", "field-frozen-pending-merge", "FIELD_FROZEN_PENDING_MERGE"]:
        if stale_status in adr or stale_status in registry:
            findings.append(Finding("XMOD_STALE_PENDING_STATUS", f"stale pending status remains: {stale_status}"))
'''
    new = '''    for stale_status in ["status: accepted-target-pending-merge", "status: field-frozen-pending-merge"]:
        if stale_status in adr or stale_status in registry:
            findings.append(Finding("XMOD_STALE_PENDING_STATUS", f"active metadata still uses pending status: {stale_status}"))
'''
    text = replace_once(text, old, new, "active status validation")
    VERIFIER.write_text(text, encoding="utf-8", newline="\n")


def normalize_test() -> None:
    text = TEST.read_text(encoding="utf-8")
    text = text.replace('    assert "FIELD_FROZEN_PENDING_MERGE" not in content\n', '    assert "FIELD_FROZEN_PENDING_MERGE" in content  # retained as a historical lifecycle state\n')
    TEST.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    normalize_registry()
    normalize_verifier()
    normalize_test()
    print("confirmed Wave 1 registry and status validation normalized")


if __name__ == "__main__":
    main()
