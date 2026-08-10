# Current Runtime Baseline

状态：`CURRENT / QUALITY_NOT_ESTABLISHED`

## Owner 边界

当前 Product API 不再依赖一个全能 Runtime Facade：

| Product surface | Application Owner | 下层事实源 |
|---|---|---|
| `POST /product/runtime-requests`、action consume、Agent 管理 | `ProductService` | command、outbox、projection |
| `POST /product/files`、`POST /product/ingestions` | `ProductIngestionService` | durable ingestion store、object store、parse/index handoff |
| Agent Run submit / query / resume / cancel | `AgentRunApplicationService` | `AgentRuntimeService` + 显式 `AgentRunStore` |
| Artifact read / download / feedback | `ProductArtifactService` | artifact / task-event durable records |
| Retrieval observability | `ProductObservabilityService` / projection query service | observability projection |

`ProductRuntimeMechanics` 仅是当前测试和内部组合仍使用的 mechanics/state component，
不是 HTTP owner，也不允许重新成为 Product God Service。新的生产执行路径只有：

```text
Product command / Agent Run application
    → AgentRuntimeService
    → AgentRunStore / checkpoint
    → Agent Core graph
```

旧 workspace task owner、旧 `/workspace/task*` 入口、direct tool execution、
shadow/canary/rollback runtime switch 均已移除。

## 保留的故障语义

删除的是新旧系统切换机制，不是可靠性语义：

- persistence failure：未能持久化的 Run 不进入执行；
- approval：中断保存在 Agent Run Store，恢复校验当前 interrupt；
- duplicate command / tool claim：由 command idempotency 和 Agent Run Store claim
  返回既有结果；
- cancel：canonical checkpointer 写入 terminal cancellation；
- restart：新 service instance 从 SQLite/PostgreSQL adapter 的 checkpoint 恢复；
- unknown external effect：Tool Gateway 进入 `RECONCILE`，禁止盲目 retry；
- security failure：Security / Budget owner reference 无效时 fail closed。

以上是架构和当前代码路径的 baseline，不等同于 production readiness 已证明。
