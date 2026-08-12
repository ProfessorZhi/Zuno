# Architecture-to-Code Workflow

## 入口条件

只有设计状态为 `ACCEPTED_TARGET`，且对应 ADR/Canonical Doc 已通过用户架构 Gate，才允许
激活 implementation Program 和执行实现任务。User Gate 前可以生成有边界的
`Codex Implementation Task Candidate`，用于说明 I-P0 如何解锁，但不能修改 Product Runtime、
创建 active implementation Program，或把 Candidate 写成 `IMPLEMENTED`。

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

`I-P0` 不能作为“先有实现才能通过 User Gate”的循环前置条件；它们应在 Gate Package 中
记录 Contract、Scope、Evidence 和 Rollback，再在 User Gate 通过后激活。`E-P0` 和 `X-P0`
分别继续走 Benchmark 与 External Qualification Track。

## 每个 Gap 的审查项

- Current 代码、Migration、进程和测试是什么；
- Target 的 Canonical Owner 和 Contract 是什么；
- 状态迁移、错误、Retry、Recovery 和 Idempotency 如何定义；
- Security、Observability、数据兼容和回滚如何处理；
- 需要哪些 Unit、Integration、Fault、E2E、Trace 或 Eval；
- 如果 Spike/Benchmark 失败，如何删除或降级该设计。

## Codex 交付边界

Codex task 必须声明 Goal、Allowed Scope、Forbidden Scope、References、Acceptance Criteria 和 Commands。数据库 schema、公开 API、依赖、安全边界和生产路径变化属于 Stop Condition，需要额外确认。
