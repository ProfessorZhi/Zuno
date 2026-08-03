# Architecture v1 Target Baseline

status: history-reference
recorded: 2026-08-04
baseline_commit: `c9d099d64a1af28102231751ce55df8217173e89`
v2_decision: `docs/decisions/0006-evidence-driven-agentic-graphrag.md`

## Purpose

本文件为正在执行的既有 Program 与 PHASE01–PHASE22 固定 Architecture v1 参考基线。

本轮没有用精简版文本覆盖十一模块的既有完整规范，也没有修改 Program / Phase。Architecture v2 先作为独立的 `accepted-target` ADR 建立，避免正在执行的 Program 在收口前失去原 Target 参考。

需要读取现有 Program 冻结时的完整 Target 文档，使用：

```text
c9d099d64a1af28102231751ce55df8217173e89
```

重点文件：

```text
docs/architecture/architecture.md
docs/architecture/architecture-views.md
docs/architecture/architecture.html
docs/modules/03-knowledge-agentic-graphrag.md
docs/modules/04-model-gateway.md
docs/modules/06-agent-core-planning-control.md
docs/modules/10-observability-eval.md
```

## Architecture v2 Routing

新的 Evidence-Driven Agentic GraphRAG 目标由以下 ADR 定义：

```text
docs/decisions/0006-evidence-driven-agentic-graphrag.md
```

该 ADR 的规范优先级高于旧模块描述，但在 PHASE22 收口前不反向改变旧 Program 的任务、Contract 和验收条件。PHASE22 完成后，应以最新 Current 为起点，把 ADR 0006 与相关模块文档重新协调，再形成独立 Program。

## Usage Rule

```text
现有 PHASE01–PHASE22
    继续使用各自冻结的 Contract、Program 和 v1 baseline。

ADR 0006 / Architecture v2
    记录新的长期 Target，不授权立即实现。

PHASE22 之后
    读取最新 Current，协调 Module 03 / 04 / 06 / 10 与总架构，创建新 Program。

Current 判断
    始终以代码、Migration、测试、Trace、Eval 和状态文档为准。
```

不得因为 ADR 0006 已接受，就把 v2 Contract 纳入旧 Phase 验收；也不得因为旧 Program 仍在执行，就把 v2 设计误写为未决讨论或已实现事实。
