from __future__ import annotations

from pathlib import Path


PATH = Path("docs/architecture/README.md")

BLOCK = """**研究只用于校准设计方向。**

外部研究只用于验证设计方向，不证明 Zuno 已经实现或验证了相应能力。与本架构关系最直接的研究主要集中在三类问题：Agentic RAG 的多步规划与动态检索，高风险 AI 的 provenance 与审计，以及 Human-in-the-loop 系统中机器建议和人类权威的边界。

这些工作共同支持一个方向：高风险 AI 需要保留来源、版本、过程、人类决定和可恢复的执行记录，并对复杂 Agent 机制进行真实任务评测。Zuno 的具体 Owner、Receipt 和恢复顺序仍然来自项目自己的法律业务约束；是否值得在真实场景长期保留，则要由后续 Evaluation 和工程 Evidence 回答。

"""


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    count = text.count(BLOCK)
    if count != 1:
        raise SystemExit(f"expected exactly one research coda, got {count}")
    PATH.write_text(text.replace(BLOCK, ""), encoding="utf-8")


if __name__ == "__main__":
    main()
