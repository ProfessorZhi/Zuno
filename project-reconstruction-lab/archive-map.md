# Formal Round Archive Map

正式 Red / Blue Round 的唯一 Owner 是 [`docs/history/red-blue/`](../docs/history/red-blue/README.md)。
本表只提供导航，不复制 Question、Answer、Score 或 Main Judgment。

## Manual

| Round | Archive | 状态 |
| --- | --- | --- |
| 01 Overall Architecture | [`manual-round-01-overall-architecture.md`](../docs/history/red-blue/manual-round-01-overall-architecture.md) | `ARCHIVED / COMPLETED` |

## Automated

| Round | Archive | 状态 |
| --- | --- | --- |
| 001 Project Architecture V2 | [`automated-round-001-project-architecture-v2.md`](../docs/history/red-blue/automated-round-001-project-architecture-v2.md) | `ARCHIVED / COMPLETED` |
| 002 Architecture V3 | [`automated-round-002-architecture-v3.md`](../docs/history/red-blue/automated-round-002-architecture-v3.md) | `ARCHIVED / COMPLETED` |
| 003 Document Quality V3.1 | [`automated-round-003-document-quality-v31.md`](../docs/history/red-blue/automated-round-003-document-quality-v31.md) | `ARCHIVED / COMPLETED` |
| 004 Human Writing V3.1.2 | [`automated-round-004-human-writing-v312.md`](../docs/history/red-blue/automated-round-004-human-writing-v312.md) | `ARCHIVED / COMPLETED` |
| 005 Failure / Recovery V3.1.3 | [`automated-round-005-failure-recovery-v313.md`](../docs/history/red-blue/automated-round-005-failure-recovery-v313.md) | `ARCHIVED / COMPLETED` |
| 006 Operational Pilot | [`automated-round-006-operational-pilot.md`](../docs/history/red-blue/automated-round-006-operational-pilot.md) | `ABORTED / WORKFLOW_EXECUTION_BLOCKER` |
| Architecture Baseline | [`automated-architecture-baseline-001.md`](../docs/history/red-blue/automated-architecture-baseline-001.md) | `ARCHIVED / COMPLETED` |
| Domain Kernel V3 | [`automated-domain-kernel-v3.md`](../docs/history/red-blue/automated-domain-kernel-v3.md) | `ARCHIVED / COMPLETED` |
| Architecture Reframe V1 | [`automated-architecture-reframe-v1.md`](../docs/history/red-blue/automated-architecture-reframe-v1.md) | `ARCHIVED / COMPLETED` |

## 不是正式 Round

Bootstrap、Reset、Blue Repair、Evidence Closure、P0 Execution、Gate Realignment、Normalization、
Semantic Audit、Workflow Test 和 Session Template 不是新的完整对抗 Round。它们不在当前树保留；
如需考古，使用 Git history 和对应提交。

`archive_commit` 使用 `RECORDED_IN_FINAL_HANDOFF`，避免归档文件在同一个提交中自引用自己的 SHA。
本次清理没有修改 Canonical Architecture，因此 `architecture_revision_commit` 标记为
`NOT_CHANGED_IN_THIS_TASK`。
