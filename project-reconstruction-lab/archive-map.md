# Formal Round Archive Map

正式 Red / Blue Round 的唯一 Owner 是 [`docs/history/red-blue/`](../docs/history/red-blue/README.md)。
本表只提供当前树中的导航，不复制 Question、Answer、Score 或 Main Judgment。

## Manual archive

| Round | Archive | 状态 |
| --- | --- | --- |
| 01 Overall Architecture | [`manual-round-01-overall-architecture.md`](../docs/history/red-blue/manual-round-01-overall-architecture.md) | `ARCHIVED / COMPLETED` |

未来手工轮次使用 `manual-round-NN-<theme>.md`，不预先创建空文件。

## Legacy automated archive

| Scope | Archive | 状态 |
| --- | --- | --- |
| Previous automated Red/Blue program | [`legacy-automated-rounds.md`](../docs/history/red-blue/legacy-automated-rounds.md) | `FROZEN SUMMARY` |

摘要保留旧程序的来源、原始状态、基线和处置；旧完整包由 Git history 追溯。Round-006 在摘要中
保持 `ABORTED_OPERATIONAL_PILOT` / `WORKFLOW_EXECUTION_BLOCKER`，其 `architecture_score: INVALID`。

## Boundary

历史归档不拥有当前事实、Target Architecture 或 ADR。新的架构审查必须由用户明确启动，并先读取
[`project-reconstruction-lab/WORKFLOW.md`](WORKFLOW.md) 与当前 Canonical 文档。
