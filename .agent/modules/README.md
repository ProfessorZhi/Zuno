# Zuno 逻辑模块设计文档镜像

`.agent/modules/` 保存 Agent System 高频读取的模块镜像；`docs/modules/` 是正式事实源。

## 十一个逻辑模块

| 编号 | 模块 | 正式模块文档 | 状态 |
| --- | --- | --- | --- |
| 01 | Product Surface | `01-product-surface.md` | 待细化 |
| 02 | Input / Document Ingestion | [`02-input-document-ingestion.md`](../../docs/modules/02-input-document-ingestion.md) | 已建立 Target 规范 |
| 03 | Knowledge / Agentic GraphRAG | [`03-knowledge-agentic-graphrag.md`](../../docs/modules/03-knowledge-agentic-graphrag.md) | 已建立 Target 规范 |
| 04 | Model Gateway | [`04-model-gateway.md`](./04-model-gateway.md) + [`04-model-gateway-contract-freeze.md`](./04-model-gateway-contract-freeze.md) + [`04-model-gateway-operations-conformance.md`](./04-model-gateway-operations-conformance.md) | 实施级 Target 镜像 |
| 05 | Memory & Context | [`05-memory-context.md`](../../docs/modules/05-memory-context.md) | 已建立 Target 规范 |
| 06 | Agent Core / Planning & Control | [`06-agent-core-planning-control.md`](./06-agent-core-planning-control.md) | 单一完整 Target 架构镜像 |
| 07 | Capability / Skill | [`07-capability-skill.md`](../../docs/modules/07-capability-skill.md) | 已建立 Target 规范 |
| 08 | Tool Runtime | `08-tool-runtime.md` | 待正式收口 |
| 09 | Security | [`09-security.md`](./09-security.md) | 实施级 Target 镜像 |
| 10 | Observability & Eval | [`10-observability-eval.md`](./10-observability-eval.md) + [`10-observability-eval-rag-agent-evaluation.md`](./10-observability-eval-rag-agent-evaluation.md) | 实施级 Target 与受控附录镜像 |
| 11 | Infrastructure | [`11-infrastructure.md`](./11-infrastructure.md) | 单一完整实施级 Target 架构镜像 |

## Wave 1 共享 Contract

```text
docs/decisions/0003-wave1-cross-module-contract-freeze.md
docs/governance/wave1-cross-module-contract-registry.md
```

ADR 0003 与 Registry 是 Wave 1 跨模块 Owner、Envelope、Receipt、Failure Namespace、Security Epoch 和 Recovery 边界的共享事实源。

当前状态：`CONFIRMED_TARGET`。物理实现归 `src/backend/zuno/platform/**`；Agent Core 只持有 `ActionProposal / ActionExecutionBinding`，可执行副作用事实归 Tool Runtime `PreparedToolAction`。

## Agent Core 唯一 Target 镜像

```text
.agent/modules/06-agent-core-planning-control.md
```

对应正式事实源：

```text
docs/modules/06-agent-core-planning-control.md
```

## Infrastructure 唯一 Target 镜像

```text
.agent/modules/11-infrastructure.md
```

对应唯一正式事实源：

```text
docs/modules/11-infrastructure.md
```

该镜像统一包含 PostgreSQL、RabbitMQ、Object Store / MinIO、LangGraph Checkpointer、Milvus、Neo4j、BM25 / Search、Redis、Trace/Audit、Secret/KMS，以及事务、Queue、索引发布、删除、恢复、审计、升级、安全、SLO、实现规格和验证要求。

Agent 读取规则：

- 不得寻找或重新创建 Infrastructure 数据服务、Consistency 或 Lifecycle 规范性附录；
- Infrastructure Target 的全部设计以唯一主文档为准；
- 正式文档与镜像必须字节级一致；
- 物理实现归 `src/backend/zuno/platform/**`，不得新增顶层 `zuno/infrastructure`；
- Current 与 Gap 读取 `docs/status/production-readiness.md`；
- 实现和迁移计划读取 `.agent/programs/`。

## Model Gateway Target 镜像

```text
.agent/modules/04-model-gateway.md
.agent/modules/04-model-gateway-contract-freeze.md
.agent/modules/04-model-gateway-operations-conformance.md
```

对应正式事实源位于 `docs/modules/`。

## Observability & Eval Target 镜像

```text
.agent/modules/10-observability-eval.md
.agent/modules/10-observability-eval-rag-agent-evaluation.md
```

主文档定义 Trace/Audit/Eval/Evidence 总边界；附录定义 RAG Core Five、Agentic GraphRAG Trace、Failure Bucket 和 Agent Efficiency。

## Security Target 镜像

```text
.agent/modules/09-security.md
```

Security 文档定义服务器端安全控制面、身份、权限、Policy、Gate、脱敏、审批、撤销、Secret 和审计 Contract。

正式文件与镜像必须字节级一致，不得只修改 `.agent/modules/`。

## 专用验证

```text
python tools/scripts/verify_agent_core_target_protocols.py
python tools/scripts/verify_security_target_protocols.py
python tools/scripts/verify_model_gateway_target_protocols.py
python tools/scripts/verify_model_gateway_contract_freeze.py
python tools/scripts/verify_model_gateway_operations_conformance.py
python tools/scripts/verify_infrastructure_target_protocols.py
python tools/scripts/verify_wave1_contract_freeze.py
python tools/scripts/verify_observability_eval_target_protocols.py

pytest -q tests/repo/test_agent_core_target_protocols.py -p no:cacheprovider
pytest -q tests/repo/test_security_target_protocols.py -p no:cacheprovider
pytest -q tests/repo/test_model_gateway_target_protocols.py tests/repo/test_model_gateway_contract_freeze.py tests/repo/test_model_gateway_operations_conformance.py -p no:cacheprovider
pytest -q tests/repo/test_infrastructure_target_protocols.py tests/repo/test_wave1_contract_freeze.py -p no:cacheprovider
pytest -q tests/repo/test_observability_eval_target_protocols.py -p no:cacheprovider
```
