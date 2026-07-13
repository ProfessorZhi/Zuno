# Zuno 逻辑模块设计文档

`docs/modules/` 是 Zuno 十一个逻辑模块的正式 Target 设计目录。

这里回答：

```text
模块解决什么问题
负责与不负责什么
完整运行流程
状态、失败、恢复、幂等和安全
跨模块 Contract 与 Ownership
目标代码、数据库和测试规格
什么证据才能把 Target 变为 Current
```

总架构以 `docs/architecture/architecture.md` 为最高层入口；Current、Gap 和 Blocked 以 `docs/status/production-readiness.md` 为事实源。

## 十一个逻辑模块

| 编号 | 模块 | 正式模块文档 | 状态 |
| --- | --- | --- | --- |
| 01 | Product Surface | `01-product-surface.md` | 待细化 |
| 02 | Input / Document Ingestion | [`02-input-document-ingestion.md`](./02-input-document-ingestion.md) | 已建立 Target 规范 |
| 03 | Knowledge / Agentic GraphRAG | [`03-knowledge-agentic-graphrag.md`](./03-knowledge-agentic-graphrag.md) | 已建立 Target 规范 |
| 04 | Model Gateway | `04-model-gateway.md` | 并行 Draft Target，待对齐已合并共享 Contract |
| 05 | Memory & Context | [`05-memory-context.md`](./05-memory-context.md) | 已建立 Target 规范 |
| 06 | Agent Core / Planning & Control | [`06-agent-core-planning-control.md`](./06-agent-core-planning-control.md) | 已建立单一完整 Target 架构文档 |
| 07 | Capability / Skill | [`07-capability-skill.md`](./07-capability-skill.md) | 已建立 Target 规范 |
| 08 | Tool Runtime | `08-tool-runtime.md` | 待细化；必须采用 PreparedToolAction 决议 |
| 09 | Security | [`09-security.md`](./09-security.md) | 已建立 Target 规范 |
| 10 | Observability & Eval | [`10-observability-eval.md`](./10-observability-eval.md) | 并行 Draft Target，待对齐已合并共享 Contract |
| 11 | Infrastructure | [`11-infrastructure.md`](./11-infrastructure.md) | Target 主文档 + 数据服务与一致性生命周期附录 |

## Agent Core 文档边界

唯一正式 Target 文档：

```text
docs/modules/06-agent-core-planning-control.md
```

它统一包含概念架构、运行流程、不变量、状态机、DAG 与并发、Interrupt / Signal、副作用、Finalization、一致性、事件、Artifact、恢复、时间、目标代码、数据库和测试规格。

执行和迁移计划不写入模块 Target 文档：

```text
.agent/programs/    Current → Target 的实现、迁移、切流和收口计划
docs/status/       Current、Gap、Measurement 和完成状态
docs/history/      已完成 Program 与历史证据
```

## Security 文档边界

正式 Target 文档：

```text
docs/modules/09-security.md
```

它定义服务端权威的身份与组织树、管理员作用域、知识库和 Tool 三档权限、委派授权、Policy、全链路 Gate、输入输出检测、脱敏、审批、撤销、Secret 和审计 Contract。前端只通过 Product API 使用后端事实；Current 实现状态仍以 `docs/status/production-readiness.md` 为准。

## Infrastructure 文档边界

Infrastructure 的主文档、受控规范性附录与字节级镜像：

```text
docs/modules/11-infrastructure.md
.agent/modules/11-infrastructure.md

docs/modules/11-infrastructure-data-services.md
.agent/modules/11-infrastructure-data-services.md

docs/modules/11-infrastructure-consistency-lifecycle.md
.agent/modules/11-infrastructure-consistency-lifecycle.md
```

`11-infrastructure.md` 仍是第 11 模块唯一模块架构事实源，冻结服务端产品部署、Database、Transaction、Object Store、Checkpoint、Queue/Worker、Inbox/Outbox、Lease/Fencing、Clock、Migration、Backup/Restore、Retention/Legal Hold、Drain、Capacity、DR 与跨模块 capability contract。

`11-infrastructure-data-services.md` 是主文档的受控展开，冻结 PostgreSQL、RabbitMQ、Redis、Milvus、Neo4j/可替换图数据库、BM25/可替换 Search runtime、Object Store、Checkpointer、Trace/Audit persistence 与 Secret/KMS 的运行责任、Ownership、故障、重建、隔离、降级和证据要求。

`11-infrastructure-consistency-lifecycle.md` 是第二个受控展开，冻结派生索引发布、ServingWatermark、跨存储删除、一致恢复集、Mandatory Audit 背压、PreparedToolAction 边界、租户隔离、Upgrade Compatibility、Adapter Conformance、SLO、Network、Release Provenance 与 Resource Attribution。

跨模块字段级 Contract 与物理目录最终决议：

```text
docs/decisions/0003-wave1-cross-module-contract-freeze.md
docs/governance/wave1-cross-module-contract-registry.md
```

ADR 0003 冻结：

- 服务端后端是产品权威运行边界，本地 Adapter 只用于开发、测试和 CI；
- Infrastructure 是逻辑模块，物理代码归 `src/backend/zuno/platform/**`；不新增 `src/backend/zuno/infrastructure/` 顶层目录；
- `CrossModuleEnvelopeV1`、Effective Security Epoch、Secret/Credential、Audit、Model、Index 和 Tool Effect 字段；
- `PreparedAction` 最终拆分为 Agent Core `ActionProposal/ActionExecutionBinding` 与 Tool Runtime `PreparedToolAction/ToolAttempt/EffectReceipt`；
- Failure Prefix、Retry/Recovery/Reconcile Owner 和 Receipt 边界。

当前 ADR 与 Registry 状态是 `FIELD_FROZEN_PENDING_MERGE`。它们只有合并到 `main` 后才成为 `CONFIRMED_TARGET`，仍不能冒充 Current。

这些文档记录 Current Inventory 只是为了防止 Target 冒充 Current；实现与迁移仍进入 `.agent/programs/`，完成状态仍进入 `docs/status/`。

## Agent 镜像

```text
docs/modules/06-agent-core-planning-control.md
.agent/modules/06-agent-core-planning-control.md

docs/modules/09-security.md
.agent/modules/09-security.md

docs/modules/11-infrastructure.md
.agent/modules/11-infrastructure.md

docs/modules/11-infrastructure-data-services.md
.agent/modules/11-infrastructure-data-services.md

docs/modules/11-infrastructure-consistency-lifecycle.md
.agent/modules/11-infrastructure-consistency-lifecycle.md
```

每对正式文件与镜像必须字节级一致。

规则：

- 不得只修改 `.agent/modules/`；
- 不得在 Target 文档中把未实现能力写成 Current；
- Current 变化只有在代码、Migration、测试、Trace、Eval 和运行证据完成后，才可写入状态文档；
- 模块设计不得放回 `docs/architecture/`；
- Agent Core、Security 或 Infrastructure 变更必须同步正式文档、镜像、入口、验证器和测试；
- Infrastructure 两个附录必须服从主文档和已合并 ADR，不得形成竞争架构；
- 未合并 ADR/Registry 只能标记 `FIELD_FROZEN_PENDING_MERGE`，不能标记 Current；
- PR #18、#20 合并前必须对齐已合并的 ADR 0003 并处理兼容 Alias。

专用验证：

```text
python tools/scripts/verify_agent_core_target_protocols.py
pytest -q tests/repo/test_agent_core_target_protocols.py -p no:cacheprovider
python tools/scripts/verify_security_target_protocols.py
pytest -q tests/repo/test_security_target_protocols.py -p no:cacheprovider
python tools/scripts/verify_infrastructure_target_protocols.py
pytest -q tests/repo/test_infrastructure_target_protocols.py -p no:cacheprovider
python tools/scripts/verify_wave1_contract_freeze.py
pytest -q tests/repo/test_wave1_contract_freeze.py -p no:cacheprovider
```
