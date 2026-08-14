# Zuno 项目事实入口

`docs/facts/` 只回答：**哪些项目事实可以作为今天理解 Zuno 的可靠基线？**

这些文件承载已经恢复、仍与产品边界有关的历史事实；它们不是 Target Architecture，
也不替代 `docs/evidence/` 的当前实现证据。每个不确定结论都必须保留状态标签、来源边界和
`UNKNOWN`，不能用当前代码或目标设计补齐历史空白。

## 阅读顺序

1. [项目背景](project-background.md)
2. [历史需求与业务流程](requirements-and-workflows.md)
3. [开发与演进](development-and-evolution.md)
4. [团队与个人 Ownership](team-and-ownership.md)
5. [交付与客户反馈](delivery-and-feedback.md)
6. [技术现实](technology-reality.md)
7. [待确认 Fact Ledger](confirmation-ledger.md)

## 文件职责

| 文件 | Canonical Question |
| --- | --- |
| `project-background.md` | 项目从哪里来、服务什么方向？ |
| `requirements-and-workflows.md` | 历史业务问题和人工流程恢复到什么程度？ |
| `development-and-evolution.md` | 项目如何从已有产品演进到 Demo、测试和 Pilot？ |
| `team-and-ownership.md` | 团队和用户本人分别确认做了什么？ |
| `delivery-and-feedback.md` | 实际验证、交付阶段和质量反馈是什么？ |
| `technology-reality.md` | 历史技术使用、当前仓库证据和 Target-only 内容如何区分？ |
| `confirmation-ledger.md` | 下一轮用户需要逐项确认哪些历史事实？ |

## 相关入口

- 当前代码、测试、运行与评测证据：[`../evidence/README.md`](../evidence/README.md)
- Target Architecture：[`../architecture/architecture.md`](../architecture/architecture.md)
- ADR：[`../decisions/README.md`](../decisions/README.md)
- 过时材料和 Red/Blue 原始档案：[`../history/README.md`](../history/README.md)

## 状态边界

```text
FACTS        今天理解 Zuno 必须相信什么
EVIDENCE     当前仓库和运行结果实际证明了什么
ARCHITECTURE 当前接受的 Target 设计为什么这样工作
HISTORY      已结束、已替换或只用于考古的材料
```

## Facts 状态词

Facts 统一使用以下状态，状态表示证据来源和可信边界，不表示架构重要性：

| 状态 | 含义 |
| --- | --- |
| `USER_CONFIRMED` | 用户明确确认过的历史事实 |
| `PUBLIC_CORROBORATED` | 官方公开资料直接支持的项目或研究背景 |
| `PUBLIC_RESEARCH_CONTEXT` | 公开论文支持的研究上下文，不能证明已经进入 Zuno 产品 |
| `USER_PARTIAL_RECALL` | 用户明确表示有印象，但细节仍不确定 |
| `RECONSTRUCTED_CANDIDATE` | 基于背景形成的合理重建，尚未由用户确认 |
| `UNKNOWN` | 当前无法可靠恢复 |
| `CURRENT_REPOSITORY_EVIDENCE` | 当前 `main` 能证明，但不能反推历史项目 |
| `TARGET_ONLY` | 当前重新设计的 Target，不能写成历史事实 |

`USER_CONFIRMATION_REQUIRED` 只用于 `confirmation-ledger.md` 的待填写队列，不是已确认事实状态。`USER_PARTIAL_RECALL` 和 `RECONSTRUCTED_CANDIDATE` 不得自动升级为 `USER_CONFIRMED`。技术矩阵中的 `CONFIRMED_USED`、`LEARNED_ONLY` 等词只描述技术细节，必须同时服从上述事实状态边界。

写入 Facts 不会把 `TARGET`、`FUTURE`、`HYPOTHESIS` 或 `UNKNOWN` 升级为 Current。
Production Readiness 仍由证据支持，当前状态为 `NOT_ESTABLISHED`。
