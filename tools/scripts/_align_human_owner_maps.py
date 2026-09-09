from __future__ import annotations

from pathlib import Path


FILES = {
    Path("docs/architecture/README.md"): {
        "| 材料与知识事实 | `DocumentVersion`、`KnowledgeGeneration`、`ReadinessDecision`、检索 lineage | Knowledge & Evidence | 稳定材料版本、generation 状态和面向当前任务的就绪判断 |":
            "| 材料与知识事实 | `DocumentVersion`、`KnowledgeGeneration`、`ReadinessDecision`、检索 lineage | `DocumentVersion` canonical identity 归 Legal Domain & Work Product；`KnowledgeGeneration`、`ReadinessDecision` 与检索 lineage 归 Knowledge & Evidence | 正式材料版本读取 02 的领域事实；知识派生与任务就绪读取 03 的耐久事实 |",
        "| **02 Legal Domain & Work Product** | 让正式法律结果拥有长期版本、接纳和失效语义 | Evidence、Finding、HumanDecision、WorkProduct、DomainVersion、Admission causation | 不把机器候选或 Runtime completed 当正式事实 |":
            "| **02 Legal Domain & Work Product** | 让 Matter、DocumentVersion 与正式法律结果拥有长期身份、版本、接纳和失效语义 | Matter、DocumentVersion、Evidence、Finding、HumanDecision、WorkProduct、DomainVersion、Admission causation | 不把机器候选或 Runtime completed 当正式事实 |",
        "| **03 Knowledge & Evidence** | 让材料身份、可重建知识和任务就绪彼此独立 | DocumentVersion ref 上的 KnowledgeGeneration、ReadinessDecision、检索 lineage | 不拥有正式 Evidence / WorkProduct 的业务接纳；DocumentVersion canonical identity 归 02 |":
            "| **03 Knowledge & Evidence** | 围绕正式 DocumentVersion 构建可重建知识、任务就绪和检索候选 | KnowledgeGeneration、ReadinessDecision、检索 lineage 及相关派生状态 | 不拥有 Matter / DocumentVersion canonical identity，也不拥有正式 Evidence / WorkProduct 的业务接纳 |",
        "---\n\n工程 / Agent 精确参考见 [`reference.md`](reference.md)。":
            "---\n\n单个责任域的 Human Narrative 继续进入 [`docs/modules/`](../modules/README.md)；总体 Architecture 的工程 / Agent 精确参考见 [`reference.md`](reference.md)。",
    },
    Path("docs/modules/README.md"): {
        "| 02 | Legal Domain & Work Product | 决定什么最终成为正式、长期、可审计的法律业务事实 | [domain](domain/README.md) |":
            "| 02 | Legal Domain & Work Product | 拥有 Matter / DocumentVersion canonical identity，并决定什么最终成为正式、长期、可审计的法律业务事实 | [domain](domain/README.md) |",
        "| 03 | Knowledge & Evidence | 区分正式材料、可重建知识派生、任务就绪和检索候选 | [knowledge](knowledge/README.md) |":
            "| 03 | Knowledge & Evidence | 围绕 02 的正式材料版本管理可重建知识派生、任务就绪和检索候选 | [knowledge](knowledge/README.md) |",
    },
}


def main() -> None:
    for path, replacements in FILES.items():
        text = path.read_text(encoding="utf-8")
        for old, new in replacements.items():
            count = text.count(old)
            if count != 1:
                raise SystemExit(f"{path}: expected exactly one match, got {count}: {old[:100]}")
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
