from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "docs/modules/README.md"
REFERENCE = ROOT / "docs/modules/reference.md"
MARKER = "## 九模块最重要的事实所有权"

STALE_SINGLE_FILE = "当前每个语义目录只有一份 `README.md`，里面仍保留完整 Part A / Part B / Part C。这是迁移期的单一事实源。只有在下一轮能够机械验证拆分前后 Owner、Authority、Contract、Recovery 和 Current/Target 完全一致时，才把 Part B/C 物理拆成 `reference.md`；在那之前不复制第二份正文。"
CURRENT_SPLIT = "当前每个语义目录已经物理分成 `README.md` 与 `reference.md`：README 只保留 Human Narrative；reference 保存 Part B、B14 Detail Candidate 与 Part C。拆分只改变信息密度，不改变 Owner、Authority、Contract、Recovery 或 Current/Target。"

STALE_ROOT_REFERENCE = "## 为什么下面还保留大量 Reference\n\n从下一节开始，本 README 转入跨模块 Reference：事实 Ownership、Completion Proof、Cancellation、Late Result、Idempotency、Recovery 和横向系统设计。它们用于整体一致性审查，不要求第一次阅读全部记住。\n\n"
CURRENT_ROOT_REFERENCE = "## 工程 Reference\n\n跨模块的事实 Ownership、Completion Proof、Cancellation、Late Result、Idempotency、Recovery、横向系统设计、Detail Candidate 与 Freeze Review 进入 [`reference.md`](reference.md)。README 到这里结束，第一次阅读不需要继续下钻。\n\n"


def main() -> None:
    text = README.read_text(encoding="utf-8")
    if text.count(MARKER) != 1:
        raise RuntimeError("expected one cross-module reference split marker")
    if STALE_SINGLE_FILE not in text:
        raise RuntimeError("expected pre-split module README statement")
    if STALE_ROOT_REFERENCE not in text:
        raise RuntimeError("expected root reference transition")

    text = text.replace(STALE_SINGLE_FILE, CURRENT_SPLIT)
    text = text.replace(STALE_ROOT_REFERENCE, CURRENT_ROOT_REFERENCE)
    human, engineering = text.split(MARKER, 1)
    README.write_text(human.rstrip() + "\n", encoding="utf-8")

    reference = REFERENCE.read_text(encoding="utf-8").rstrip()
    reference += "\n\n---\n\n## Cross-module Engineering Reference\n\n" + MARKER + engineering
    REFERENCE.write_text(reference.rstrip() + "\n", encoding="utf-8")

    human_after = README.read_text(encoding="utf-8")
    reference_after = REFERENCE.read_text(encoding="utf-8")
    if MARKER in human_after or MARKER not in reference_after:
        raise RuntimeError("modules root split invariant failed")
    for required in (
        "module_design_baseline: AVAILABLE_V1",
        "module_detail_freeze: NOT_YET",
        "implementation_authorization: NO",
        "reference.md",
    ):
        if required not in human_after:
            raise RuntimeError(f"human module map lost required marker: {required}")
    for required in (
        "Cancellation（取消）是停止未来工作，不是全局回滚",
        "Idempotency（幂等）不是一个全局 key",
        "恢复时先找 Owner Fact，再修复 Projection",
        "Module Detail Freeze Review",
    ):
        if required not in reference_after:
            raise RuntimeError(f"module reference lost required marker: {required}")


if __name__ == "__main__":
    main()
