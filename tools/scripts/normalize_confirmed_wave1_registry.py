from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs/governance/wave1-cross-module-contract-registry.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 0:
        print(f"SKIP {label}: already normalized")
        return text
    if count != 1:
        raise RuntimeError(f"{label}: expected one occurrence, got {count}")
    return text.replace(old, new, 1)


def main() -> None:
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
    text = text.replace("reviewed_parallel_prs:\n  - `#18 Model Gateway @ 3bd9b3e4437314c376a5b1b767ef052e3c74db53`\n  - `#19 Security @ f9fd19c16721cb9cec97c25d82b86274660622e6`\n  - `#20 Observability & Eval @ 4a91953799cd0bae7f3ca441cccabffbce1271f9`",
        "reviewed_wave1_proposals:\n  - `#18 Model Gateway @ 3bd9b3e4437314c376a5b1b767ef052e3c74db53`\n  - `#19 Security @ f9fd19c16721cb9cec97c25d82b86274660622e6`\n  - `#17 Infrastructure @ e9ff166f0621fb3986be2086eff6036ac5de4707`\n  - `#21 Observability & Eval integration @ a2252e64a99feda2aae36affe507d8984985e2c6`")
    REGISTRY.write_text(text, encoding="utf-8", newline="\n")
    print("confirmed Wave 1 registry normalized")


if __name__ == "__main__":
    main()
