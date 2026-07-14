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
| 07 | Capability / Skill | [`07-capability-skill.md`](./07-capability-skill.md) | 单一完整 Target 架构镜像 |
| 08 | Tool Runtime | `08-tool-runtime.md` | 待细化 |
| 09 | Security | [`09-security.md`](./09-security.md) | 实施级 Target 镜像 |
| 10 | Observability & Eval | [`10-observability-eval.md`](./10-observability-eval.md) + [`10-observability-eval-rag-agent-evaluation.md`](./10-observability-eval-rag-agent-evaluation.md) | 实施级 Target 与受控附录镜像 |
| 11 | Infrastructure | [`11-infrastructure.md`](./11-infrastructure.md) + [`11-infrastructure-data-services.md`](./11-infrastructure-data-services.md) + [`11-infrastructure-consistency-lifecycle.md`](./11-infrastructure-consistency-lifecycle.md) | 实施级 Target 镜像 |

## Wave 1 共享 Contract

```text
docs/decisions/0003-wave1-cross-module-contract-freeze.md
docs/governance/wave1-cross-module-contract-registry.md
```

ADR 0003 与 Registry 是 Wave 1 跨模块 Owner、Envelope、Receipt、Failure Namespace、Security Epoch 和 Recovery 边界的共享事实源。

当前状态：`CONFIRMED_TARGET`。物理实现归 `src/backend/zuno/platform/**`；Agent Core 只持有 `ActionProposal / ActionExecutionBinding`，可执行副作用事实归 Tool Runtime `PreparedToolAction`。

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

## Infrastructure Target 镜像

```text
.agent/modules/11-infrastructure.md
.agent/modules/11-infrastructure-data-services.md
.agent/modules/11-infrastructure-consistency-lifecycle.md
```

对应正式事实源：

```text
docs/modules/11-infrastructure.md
docs/modules/11-infrastructure-data-services.md
docs/modules/11-infrastructure-consistency-lifecycle.md
```

## Observability & Eval Target 镜像

```text
.agent/modules/10-observability-eval.md
.agent/modules/10-observability-eval-rag-agent-evaluation.md
```

对应正式事实源：

```text
docs/modules/10-observability-eval.md
docs/modules/10-observability-eval-rag-agent-evaluation.md
```

主文档定义 Trace/Audit/Eval/Evidence 总边界；附录定义 RAG Core Five、Agentic GraphRAG Trace、Failure Bucket 和 Agent Efficiency。

## Agent Core 唯一 Target 镜像

```text
.agent/modules/06-agent-core-planning-control.md
```

对应正式事实源：

```text
docs/modules/06-agent-core-planning-control.md
```

## Capability / Skill 唯一 Target 镜像

```text
.agent/modules/07-capability-skill.md
```

对应正式事实源：

```text
docs/modules/07-capability-skill.md
```

它统一定义 Capability、Skill、Provider Binding、Conformance、Availability、Selection、渐进加载、Connector Pack、版本、状态机、失败恢复、目标代码、数据库和验证规格。真实 ToolDefinition、ProviderInstance、Prepare、Execute、Receipt 和 Reconcile 仍归 Tool Runtime。

## Security Target 镜像

```text
.agent/modules/09-security.md
```

对应正式事实源：

```text
docs/modules/09-security.md
```

Security 文档定义服务器端安全控制面、账号与身份、组织树、管理员作用域、资源权限、委派授权、Policy、全链路 Gate、输入输出检测、脱敏、审批、撤销、Secret 和审计 Contract。

正式文件与镜像必须字节级一致，不得只修改 `.agent/modules/`。Current 与 Gap 读取 `docs/status/production-readiness.md`；实现与迁移计划读取 `.agent/programs/`。

## 专用验证

```text
python tools/scripts/verify_agent_core_target_protocols.py
python tools/scripts/verify_capability_skill_target_protocols.py
python tools/scripts/verify_security_target_protocols.py
python tools/scripts/verify_model_gateway_target_protocols.py
python tools/scripts/verify_model_gateway_contract_freeze.py
python tools/scripts/verify_model_gateway_operations_conformance.py
python tools/scripts/verify_infrastructure_target_protocols.py
python tools/scripts/verify_wave1_contract_freeze.py
python tools/scripts/verify_observability_eval_target_protocols.py

pytest -q tests/repo/test_agent_core_target_protocols.py -p no:cacheprovider
pytest -q tests/repo/test_capability_skill_target_protocols.py -p no:cacheprovider
pytest -q tests/repo/test_security_target_protocols.py -p no:cacheprovider
pytest -q tests/repo/test_model_gateway_target_protocols.py tests/repo/test_model_gateway_contract_freeze.py tests/repo/test_model_gateway_operations_conformance.py -p no:cacheprovider
pytest -q tests/repo/test_infrastructure_target_protocols.py tests/repo/test_wave1_contract_freeze.py -p no:cacheprovider
pytest -q tests/repo/test_observability_eval_target_protocols.py -p no:cacheprovider
```
