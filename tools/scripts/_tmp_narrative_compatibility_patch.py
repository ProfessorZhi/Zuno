from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    readme = ROOT / "docs/architecture/README.md"
    text = readme.read_text(encoding="utf-8")
    old = "需要实施或审查时再进入："
    new = "需要实施或审查时，再结合 [`../decisions/`](../decisions/) 中的 ADR 进入："
    if old not in text:
        raise RuntimeError("architecture README insertion point not found")
    readme.write_text(text.replace(old, new, 1), encoding="utf-8")

    architecture = ROOT / "docs/architecture/architecture.md"
    text = architecture.read_text(encoding="utf-8")
    anchor = "因此 Zuno 的总体设计从一个核心判断出发：**对简单任务保持简单；只有当长期事实、专业责任、失败恢复或现实副作用真正出现时，才引入相应复杂度。** 架构的目标不是让所有请求走最长路径，而是让每类任务只承担它实际需要的责任。"
    insertion = anchor + "\n\n当前总体 Target 已由 Round 02 冻结为 **9 个 Target Logical Modules**。这里的九个模块是逻辑责任与事实 Ownership 边界，不是九个必须独立部署的物理服务。"
    if anchor not in text:
        raise RuntimeError("architecture Round 02 insertion point not found")
    text = text.replace(anchor, insertion, 1)

    old_runtime = "Runtime 需要知道计划执行到哪里、哪些 Step 完成、哪些分支仍在等待；Domain 则需要知道哪些法律事实和工作成果已经正式成立。"
    new_runtime = "Runtime Control State（运行控制状态）需要知道计划执行到哪里、哪些 Step 完成、哪些分支仍在等待；Domain State（领域状态）则需要知道哪些法律事实和工作成果已经正式成立。"
    if old_runtime not in text:
        raise RuntimeError("runtime control terminology insertion point not found")
    text = text.replace(old_runtime, new_runtime, 1)
    architecture.write_text(text, encoding="utf-8")

    Path(__file__).unlink()


if __name__ == "__main__":
    main()
