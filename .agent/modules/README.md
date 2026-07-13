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
| 08 | Tool Runtime | `08-tool-runtime.md` | 待细化 |
| 09 | Security | [`09-security.md`](./09-security.md) | Target 架构镜像 |
| 10 | Observability & Eval | [`10-observability-eval.md`](./10-observability-eval.md) + [`10-observability-eval-rag-agent-evaluation.md`](./10-observability-eval-rag-agent-evaluation.md) | 实施级 Target 与受控附录镜像 |
| 11 | Infrastructure | `11-infrastructure.md` | 待细化 |

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

专用验证：

```text
python tools/scripts/verify_agent_core_target_protocols.py
python tools/scripts/verify_security_target_protocols.py
python tools/scripts/verify_model_gateway_target_protocols.py
python tools/scripts/verify_model_gateway_contract_freeze.py
python tools/scripts/verify_model_gateway_operations_conformance.py
python tools/scripts/verify_observability_eval_target_protocols.py
```
