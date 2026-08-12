# Architecture-to-Code Workflow

## 入口条件

只有设计状态为 `ACCEPTED_TARGET`，且对应 ADR/Canonical Doc 已通过用户架构 Gate，才允许生成实现任务。`PROPOSED` 或 `UNDER_ATTACK` 设计只能生成 Spike/Benchmark 任务，不能直接改生产 Runtime。

## 流程

```text
Current Repository Inventory
  → Target Contract
  → Gap Record
  → Dependency / State / Failure Review
  → Expand
  → Migrate
  → Verify
  → Contract
  → Evidence Update
```

## 每个 Gap 的审查项

- Current 代码、Migration、进程和测试是什么；
- Target 的 Canonical Owner 和 Contract 是什么；
- 状态迁移、错误、Retry、Recovery 和 Idempotency 如何定义；
- Security、Observability、数据兼容和回滚如何处理；
- 需要哪些 Unit、Integration、Fault、E2E、Trace 或 Eval；
- 如果 Spike/Benchmark 失败，如何删除或降级该设计。

## Codex 交付边界

Codex task 必须声明 Goal、Allowed Scope、Forbidden Scope、References、Acceptance Criteria 和 Commands。数据库 schema、公开 API、依赖、安全边界和生产路径变化属于 Stop Condition，需要额外确认。
