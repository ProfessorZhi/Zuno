# Zuno 逻辑模块设计文档镜像

`.agent/modules/` 保存 Agent System 高频读取的模块镜像；`docs/modules/` 是正式事实源。

## 十一个逻辑模块

| 编号 | 模块 | 正式模块文档 | 状态 |
| --- | --- | --- | --- |
| 01 | Product Surface | `01-product-surface.md` | 待细化 |
| 02 | Input / Document Ingestion | [`02-input-document-ingestion.md`](../../docs/modules/02-input-document-ingestion.md) | 已建立 Target 规范 |
| 03 | Knowledge / Agentic GraphRAG | [`03-knowledge-agentic-graphrag.md`](../../docs/modules/03-knowledge-agentic-graphrag.md) | 已建立 Target 规范 |
| 04 | Model Gateway | [`04-model-gateway.md`](./04-model-gateway.md) + [`04-model-gateway-contract-freeze.md`](./04-model-gateway-contract-freeze.md) + [`04-model-gateway-operations-conformance.md`](./04-model-gateway-operations-conformance.md) | 主 Target、Contract Freeze 与 Operations/Conformance 镜像 |
| 05 | Memory & Context | [`05-memory-context.md`](../../docs/modules/05-memory-context.md) | 已建立 Target 规范 |
| 06 | Agent Core / Planning & Control | [`06-agent-core-planning-control.md`](./06-agent-core-planning-control.md) | 单一完整 Target 架构镜像 |
| 07 | Capability / Skill | [`07-capability-skill.md`](../../docs/modules/07-capability-skill.md) | 已建立 Target 规范 |
| 08 | Tool Runtime | `08-tool-runtime.md` | 待细化；必须采用 PreparedToolAction 决议 |
| 09 | Security | [`09-security.md`](./09-security.md) | 已建立 Target 规范 |
| 10 | Observability & Eval | [`10-observability-eval.md`](../../docs/modules/10-observability-eval.md) | 并行 Draft Target，待对齐已合并共享 Contract |
| 11 | Infrastructure | [`11-infrastructure.md`](./11-infrastructure.md) | Target 主文档镜像 + 数据服务与一致性生命周期附录镜像 |

## Model Gateway Target 镜像

```text
.agent/modules/04-model-gateway.md
.agent/modules/04-model-gateway-contract-freeze.md
.agent/modules/04-model-gateway-operations-conformance.md
```

对应正式事实源：

```text
docs/modules/04-model-gateway.md
docs/modules/04-model-gateway-contract-freeze.md
docs/modules/04-model-gateway-operations-conformance.md
```

每一对正式文件与镜像都必须字节级一致。

- 主文档定义 Model Gateway 完整调用协议与领域边界；
- Contract Freeze 附录补充跨模块 Ownership、ModelOperationKind、ModelCall、Budget / Usage / Quota、Event、Streaming、Routing Replay、Capability 和 ResultValidity；
- Operations / Conformance 附录补充 Adapter 一致性、Config / Model 生命周期、租户公平、过载背压、缓存、运维、Retention / Deletion、SLO / Readiness、兼容升级和 Eval / Judge 治理。

Model Gateway Current 与旁路调用不能从 Target 文档推断，必须读取状态文件、代码调用链和 boundary verifier。

专用验证：

```text
python tools/scripts/verify_model_gateway_target_protocols.py
python tools/scripts/verify_model_gateway_contract_freeze.py
python tools/scripts/verify_model_gateway_operations_conformance.py
pytest -q tests/repo/test_model_gateway_target_protocols.py tests/repo/test_model_gateway_contract_freeze.py tests/repo/test_model_gateway_operations_conformance.py -p no:cacheprovider
```

## Agent Core 唯一 Target 镜像

```text
.agent/modules/06-agent-core-planning-control.md
```

对应正式事实源：

```text
docs/modules/06-agent-core-planning-control.md
```

该文档统一包含主设计、控制协议和一致性生命周期协议。Current 与 Gap 读取 `docs/status/production-readiness.md`；实现与迁移计划读取 `.agent/programs/`。

## Security Target 镜像

```text
.agent/modules/09-security.md
```

对应正式事实源：

```text
docs/modules/09-security.md
```

Security 文档定义服务端权威的身份与组织树、管理员作用域、知识库和 Tool 三档权限、委派授权、Policy、全链路 Gate、输入输出检测、脱敏、审批、撤销、Secret 和审计 Contract。前端只通过 Product API 使用后端安全事实。

## Infrastructure Target 镜像边界

```text
.agent/modules/11-infrastructure.md
.agent/modules/11-infrastructure-data-services.md
.agent/modules/11-infrastructure-consistency-lifecycle.md
```

对应正式事实源与受控附录：

```text
docs/modules/11-infrastructure.md
docs/modules/11-infrastructure-data-services.md
docs/modules/11-infrastructure-consistency-lifecycle.md
```

`11-infrastructure.md` 是第 11 模块唯一模块架构事实源，并把服务端后端固定为产品 Target；本地 Adapter 仅用于开发、测试和 CI。

`11-infrastructure-data-services.md` 覆盖 PostgreSQL、RabbitMQ、Redis、Milvus、Neo4j、BM25/Search、Object Store、Checkpointer、Trace/Audit persistence 与 Secret/KMS 的运行责任、Ownership、故障、重建、隔离、降级和证据要求。

`11-infrastructure-consistency-lifecycle.md` 覆盖 Index Lifecycle、ServingWatermark、跨存储删除、RecoverySet、Mandatory Audit、PreparedToolAction 边界、租户隔离、Upgrade Compatibility、Conformance、SLO、Network、Release 和 Attribution。

字段级共享 Contract 与物理目录最终决议：

```text
docs/decisions/0003-wave1-cross-module-contract-freeze.md
docs/governance/wave1-cross-module-contract-registry.md
```

Agent 读取规则：

- ADR 0003 冻结服务端产品边界与 Infrastructure 物理实现到 `src/backend/zuno/platform/**`；
- Agent Core 使用 `ActionProposal + ActionExecutionBinding`，可执行事实归 Tool Runtime `PreparedToolAction`；
- Registry 当前为 `FIELD_FROZEN_PENDING_MERGE`，合并到 `main` 后才成为 `CONFIRMED_TARGET`；
- 未合并 Draft 或 Target 不能写成 Current；
- PR #20 必须在合并前对齐 ADR 0003。

每对正式文件与镜像必须字节级一致，不得只修改 `.agent/modules/`；两个 Infrastructure 附录不得形成第二套独立模块架构，必须服从主文档和已合并 ADR。

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
