# Architecture v1 Target Baseline

status: history-reference
recorded: 2026-08-04
baseline_commit: `c9d099d64a1af28102231751ce55df8217173e89`

## Purpose

本文件为正在执行的既有 Program 与 PHASE01–PHASE22 保留 Architecture v1 参考基线。

Architecture v2 已更新总架构及 Module 03、04、06、10，但不会反向改写既有 Program / Phase 的冻结验收口径。需要查看升级前的完整 Target 文档时，使用以下 Git Commit：

```text
c9d099d64a1af28102231751ce55df8217173e89
```

重点旧文件：

```text
docs/architecture/architecture.md
docs/architecture/architecture-views.md
docs/architecture/architecture.html
docs/modules/03-knowledge-agentic-graphrag.md
docs/modules/04-model-gateway.md
docs/modules/06-agent-core-planning-control.md
docs/modules/10-observability-eval.md
```

## Usage Rule

```text
现有 PHASE01–PHASE22
    继续使用各自已冻结的 Contract、Program 和上述历史基线。

新 Architecture v2
    作为 PHASE22 收口后新 Program 的设计输入。

Current 判断
    始终以当前代码、Migration、测试、Trace、Eval 和状态文档为准。
```

不得因为 Architecture v2 已合并，就把旧 Phase 未实现的 v2 Contract 纳入原验收条件；也不得因为旧 Program 仍在执行，就忽略新的长期 Target。
