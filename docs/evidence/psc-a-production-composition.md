# PSC-A Production Composition Current Evidence

status: `CURRENT / PSC_A_SELECTED_VERIFIED / PRODUCTION_READINESS_NOT_ESTABLISHED`
verified_code_snapshot: `c3938ccb92c8234977ebd5e2956acec697981d24`
workflow: `Current code selected verification`
workflow_run: `35071244101`
event: `push / main`
runner: `ubuntu-24.04`
python: `3.12.14`
postgresql_service: `PostgreSQL 16.15 / healthy`
selected_suite: `210 passed, 18 warnings in 32.79s`
artifact_id: `10436282705`
full_ci: `NOT_RUN / NOT_ESTABLISHED`
production_readiness: `NOT_ESTABLISHED`

PSC-A 解决的是一个很具体的产品装配断点。此前 `WorkspaceRuntimeComposition` 已经定义了 Product Agent Runtime 需要的 durable store、Tool/Security/Infrastructure UoW 和 owner resolver ports，但正式 FastAPI startup 没有建立 production binding；product profile 因而只能在 composition 缺失时 fail closed。

`main@c3938ccb...` 现在在数据库 bootstrap 完成后建立 `WorkspaceRuntimeComposition`，并把它绑定到全局 product composition boundary。Current binding 只注入已有实现：

```text
PostgresAgentRunStore
ToolUnitOfWork factory
SecurityUnitOfWork factory
InfrastructureUnitOfWork factory
```

PSC-A 没有为了让 Product 路径“看起来可运行”伪造还不存在的 owner facts。以下依赖继续显式保持未绑定：

```text
security_approval_sink = None
security_epoch_ref = ""
security_decision_resolver = None
budget_decision_resolver = None
approval_flow = "none"
dynamic_dag_planner = None
```

因此 PSC-A 的绿色证据只证明 production composition root 和 durable AgentRunStore 已经接上；它不证明 PSC-B SecurityDecision、PSC-C Budget Admission、PSC-D approval sink ownership 或 Dynamic DAG product binding 已经完成。

## PostgreSQL store evidence

新增 `PostgresAgentRunStore` 复用仓库已经存在的 `agent_runtime_runs`、`agent_runtime_checkpoints`、`agent_runtime_events` 和 `agent_runtime_interrupts` 表，没有增加第二套 runtime persistence schema。

Selected PostgreSQL probe 在 fresh database 上执行正式 Alembic `upgrade head` 后：

1. 使用第一 个 `PostgresAgentRunStore` 写入 runtime state、checkpoint 和 pending interrupt；
2. 丢弃第一 个 Store instance；
3. 用同一 PostgreSQL engine 创建新的 Store instance；
4. 新 instance 仍能恢复 task、latest checkpoint 和 pending interrupt。

这证明的是当前 `AgentRunStore` Protocol 所需的耐久恢复面，不等于 SQLite Store 的所有额外扩展接口都已迁移。PSC-A 也没有为了接口外观对称而复制未被 Product first-stage path 需要的额外状态机。

## Real startup evidence

同一 selected suite 还直接调用正式 `zuno.main.init_config()`。测试只隔离真实网络/外部启动副作用，数据库使用 fresh PostgreSQL 和正式 migration chain。

probe 验证 startup 后：

```text
get_workspace_product_composition() != None
composition.store is PostgresAgentRunStore
Tool/Security/Infrastructure UoW factories are bound
PSC-B/C/D resolver/approval dependencies remain unbound
```

随后通过 composition 的 Store 写入一个 runtime task，并用新的 `PostgresAgentRunStore` instance 从 PostgreSQL 重新观察到该 task。test reset 再调用 `ProductRuntimeMechanics.reset_runtime_state_for_tests()` 后，全局 composition 会被清空，避免测试 binding 泄漏到下一用例。

这条 startup probe 还暴露并关闭了一个原先没有被真实启动路径覆盖的基础错误：`ProductIngestionService.configure_package_a_production_ingestion()` 的 `runtime` 参数只能以 keyword 方式传入，而旧 `main.py` 使用 positional 调用。第一次 PSC-A PR run 因此在 composition binding 前失败；修复为 `runtime=...` 后，PR 和 main push verification 都转绿。该修复只恢复既有 startup 调用约定，没有改变 ingestion Authority 或业务语义。

## Evidence boundary

Current 可以采用的结论：

- 正式 FastAPI startup 已经建立 production `WorkspaceRuntimeComposition`；
- product runtime 已有 PostgreSQL-backed canonical AgentRunStore；
- runtime state / checkpoint / pending interrupt 能跨 Store instance 恢复；
- Tool / Security / Infrastructure UoW factories 由 server composition 注入；
- composition 缺失和 PSC-B/C/D 未绑定依赖继续 fail closed；
- test reset 能清除 global product composition。

Current 不能扩写成：

- Product tool plan 已经可以通过正式 Security/Budget admission；
- `PostgresSecurityDecisionResolver` 已有可消费的 production owner fact；
- Budget owner fact store 已实现；
- approval flow 已正式接通；
- `PostgresSecurityApprovalFactSink` ownership 已解决；
- 完整 Target composed SecurityEpoch 已实现；
- Full CI、HA、SLA 或 Production Qualification 已完成。

后续 PSC-B/C/D 仍应独立通过各自的 owner-fact、fault 和 product request E2E evidence，不能用 PSC-A 的 startup 绿色替代。