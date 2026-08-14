---
name: architecture-red-blue-loop
description: Run an evidence-driven Red/Blue architecture review for an existing project, including attack, defense, counter-review, Main judgment, archive-first recording, optional canonical revision, and focused validation. Use when architecture must become simpler, replaceable, recoverable, and interviewable without inventing complexity.
---

# Architecture Red Blue Loop

## Purpose

把一次架构攻击收口为可审计的历史记录和明确决策；先删除、简化、复用或测量，再考虑新增设计。

## Inputs

- 最新 `main` 和可证明的 BASE SHA；
- `docs/facts/`、`docs/architecture/`、ADR、治理和 Evidence；
- 允许读取的代码、测试和外部资料；
- Round Theme、最大轮数、Main 模式：`MANUAL_MAIN` 或 `AUTOMATED_MAIN`。

## Workflow

1. Bootstrap：确认分支、工作树、Owner、阅读范围和禁止范围；
2. Main Brief：定义一个最强 Root Claim，不预设固定模块数量或题量；
3. Red Attack：追问必要性、替代、状态、失败、恢复、安全、成本和反转条件；
4. Blue Defense：用普通语言回答，再补 Contract；明确未知和证据不足；
5. Red Review：区分事实缺口、架构缺口、测量缺口和实现缺口；
6. Main Judgment：选择 `ACCEPT / REJECT / DEFER / MEASUREMENT / FACT_GAP / NO_CHANGE`；
7. Archive First：先保存 Question、Answer、Review、Decision、BASE SHA 和状态；
8. Architecture Revision：只有 Main 授权时，在 Candidate/独立 Revision Commit 修改正式 Owner；
9. Validation：运行受影响的文档、链接、边界和专项测试；需要实现证据时另开 Implementation Track。

## Outputs

- 一个正式 Round Archive；
- Red Findings、Blue Decisions、Main Judgment；
- `KEEP / SIMPLIFY / REUSE / EXTERNALIZE / MEASURE / BUILD / DELETE / DEFER` 处置；
- 可追溯的 Canonical Delta、验证结果、Open Gaps 和下一步建议。

## Boundaries

- Red 只攻击，不替 Blue 修复；Blue 不自动写回 Canonical；
- Archive Commit 与 Architecture Revision Commit 分离；
- 不把 Red Finding 自动升级为 ADR 或 Architecture Gap；
- 不把代码存在、Mock、Target 文档或 Round 分数当作生产证明；
- 多 Agent、GraphRAG、Memory、Microservice、LangGraph、Kafka、Kubernetes 等均需问题和证据，
  不是默认答案。

## Failure / Stop Conditions

- BASE SHA、Context 或权限边界无法证明时停止；
- Blue 需要业务代码或前一轮答案才能回答冷启动问题时记录 `CONTEXT_GAP`；
- 复杂度收益只能靠口号表达时选择 `MEASUREMENT` 或 `SIMPLIFY`；
- 需要改 API、Schema、Dependency、安全边界或生产环境时停止并请求单独授权；
- Round 中止时保留 `ABORTED`，不得补写不存在的 Answer、Score 或 Candidate。

## Evidence Rules

每个决策至少绑定：Problem、Alternative、Owner、State、Failure/Recovery、Test、Cost 和
Reversal Condition。Current、Target、Hypothesis、History 分开；历史归档进入
`docs/history/red-blue/`，正式架构才回到 `docs/architecture/` 或 ADR。

## Example Invocation

```text
请使用 architecture-red-blue-loop，在最新 main 上只审查“Domain State 是否必须独立于 Runtime
Checkpoint”。先做 Red/Blue/Review 和 Archive；没有 Main 明确授权，不修改 docs/architecture。
```
