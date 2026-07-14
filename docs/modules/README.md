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
| 04 | Model Gateway | [`04-model-gateway.md`](./04-model-gateway.md) | 已建立单一完整 Target 架构文档 |
| 05 | Memory & Context | [`05-memory-context.md`](./05-memory-context.md) | 已建立 Target 规范 |
| 06 | Agent Core / Planning & Control | [`06-agent-core-planning-control.md`](./06-agent-core-planning-control.md) | 已建立单一完整 Target 架构文档 |
| 07 | Capability / Skill | [`07-capability-skill.md`](./07-capability-skill.md) | 已建立 Target 规范 |
| 08 | Tool Runtime | `08-tool-runtime.md` | 待细化 |
| 09 | Security | [`09-security.md`](./09-security.md) | 已建立实施级 Target 规范 |
| 10 | Observability & Eval | [`10-observability-eval.md`](./10-observability-eval.md)；[`RAG Core Five / Agentic GraphRAG / Agent Efficiency 附录`](./10-observability-eval-rag-agent-evaluation.md) | 已建立实施级 Target 规范 |
| 11 | Infrastructure | [`11-infrastructure.md`](./11-infrastructure.md) + [`11-infrastructure-data-services.md`](./11-infrastructure-data-services.md) + [`11-infrastructure-consistency-lifecycle.md`](./11-infrastructure-consistency-lifecycle.md) | 已建立实施级 Target 规范 |

## Wave 1 共享 Contract

```text
docs/decisions/0003-wave1-cross-module-contract-freeze.md
docs/governance/wave1-cross-module-contract-registry.md
```

ADR 0003 与 Registry 统一冻结 Security、Infrastructure、Model Gateway、Observability & Eval 之间的 Owner、Envelope、Receipt、Failure Namespace、Security Epoch 和 Recovery 边界。模块文档中的重复说明不得覆盖共享 Contract。

当前状态：`CONFIRMED_TARGET`。服务端物理实现归 `src/backend/zuno/platform/**`；Agent Core 使用 `ActionProposal / ActionExecutionBinding`，可执行副作用事实归 Tool Runtime `PreparedToolAction`。

## Model Gateway 文档边界

唯一正式 Target 文档及 Agent 镜像：

```text
docs/modules/04-model-gateway.md
.agent/modules/04-model-gateway.md
```

两者必须字节级一致。该文档统一包含：

```text
模块定位、目标与 Ownership
十一个模块的模型使用地图
Role、Operation、Provider、Model、Capability 与 Prompt
完整调用流程、Routing、Admission、Retry、Fallback、Escalation 与 Reconciliation
Generation、Embedding、Rerank、Vision/OCR、Transcription、Classification 与 Judge
Call、Attempt、Stream、Usage、Quota、Health、Circuit、Config 与 Lifecycle 状态机
Adapter Conformance、多租户公平、过载、Cache、运维命令、Retention、Deletion、SLO 与 Readiness
目标代码、数据库、Migration、Requirement、测试与完成证据
```

Current 调用清单、旁路状态和 Production Readiness 必须读取代码、测试、Migration、Trace、Eval 与状态文档，不能从 Target 文档推断。

## Infrastructure 文档边界

```text
docs/modules/11-infrastructure.md
docs/modules/11-infrastructure-data-services.md
docs/modules/11-infrastructure-consistency-lifecycle.md
```

主文档定义关系数据库、对象、Checkpoint、Queue、Lease、Migration、Backup、Restore、Retention、Drain 和部署 primitive；两个附录分别定义 Data Services 和一致性/生命周期协议。Developer/CI Local Adapter 不代表多用户产品部署 Target。

## Observability & Eval 文档边界

```text
docs/modules/10-observability-eval.md
docs/modules/10-observability-eval-rag-agent-evaluation.md
```

主文档定义 Trace、Audit、Metric、Eval、Evidence、Release Gate、事件交付、恢复和质量证明边界；受控附录冻结 RAG Core Five、Agentic GraphRAG 全过程 Trace、Graph Failure Bucket 和 Agent Efficiency。旧 Retrieval、Citation、Safety 与 Runtime 指标保留为诊断层，不得冒充 Core Five。

## Agent Core 文档边界

```text
docs/modules/06-agent-core-planning-control.md
.agent/modules/06-agent-core-planning-control.md
```

它统一包含概念架构、运行流程、不变量、状态机、DAG 与并发、Interrupt / Signal、副作用、Finalization、一致性、事件、Artifact、恢复、时间、目标代码、数据库和测试规格。

## Security 文档边界

```text
docs/modules/09-security.md
.agent/modules/09-security.md
```

它定义服务器端安全控制面、账号与身份、组织树、管理员作用域、资源权限、委派授权、Policy、全链路 Gate、输入输出检测、脱敏、审批、撤销、Secret 和审计 Contract。

执行和迁移计划不写入模块 Target 文档：

```text
.agent/programs/    Current → Target 的实现、迁移、切流和收口计划
docs/status/       Current、Gap、Measurement 和完成状态
docs/history/      已完成 Program 与历史证据
```

存在镜像的正式文件必须字节级一致。模块变更必须同步正式文档、受控附录、镜像、入口、专用验证器和测试。

## 专用验证

```text
python tools/scripts/verify_agent_core_target_protocols.py
pytest -q tests/repo/test_agent_core_target_protocols.py -p no:cacheprovider

python tools/scripts/verify_security_target_protocols.py
pytest -q tests/repo/test_security_target_protocols.py -p no:cacheprovider

python tools/scripts/verify_model_gateway_target_protocols.py
pytest -q tests/repo/test_model_gateway_target_protocols.py -p no:cacheprovider

python tools/scripts/verify_infrastructure_target_protocols.py
python tools/scripts/verify_wave1_contract_freeze.py
pytest -q tests/repo/test_infrastructure_target_protocols.py tests/repo/test_wave1_contract_freeze.py -p no:cacheprovider

python tools/scripts/verify_observability_eval_target_protocols.py
pytest -q tests/repo/test_observability_eval_target_protocols.py -p no:cacheprovider
```
