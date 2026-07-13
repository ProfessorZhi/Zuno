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
| 04 | Model Gateway | [`04-model-gateway.md`](./04-model-gateway.md) + [`04-model-gateway-contract-freeze.md`](./04-model-gateway-contract-freeze.md) | 已建立 Target 规范与 Wave 1 Contract Freeze 附录 |
| 05 | Memory & Context | [`05-memory-context.md`](./05-memory-context.md) | 已建立 Target 规范 |
| 06 | Agent Core / Planning & Control | [`06-agent-core-planning-control.md`](./06-agent-core-planning-control.md) | 已建立单一完整 Target 架构文档 |
| 07 | Capability / Skill | [`07-capability-skill.md`](./07-capability-skill.md) | 已建立 Target 规范 |
| 08 | Tool Runtime | `08-tool-runtime.md` | 待细化 |
| 09 | Security | `09-security.md` | 待细化 |
| 10 | Observability & Eval | [`10-observability-eval.md`](./10-observability-eval.md) | 已建立 Target 规范 |
| 11 | Infrastructure | `11-infrastructure.md` | 待细化 |

## Model Gateway 文档边界

正式 Target 文档、Contract Freeze 附录与 Agent 镜像：

```text
docs/modules/04-model-gateway.md
.agent/modules/04-model-gateway.md

docs/modules/04-model-gateway-contract-freeze.md
.agent/modules/04-model-gateway-contract-freeze.md
```

每一对正式文件与 Agent 镜像都必须字节级一致。主文档定义完整 Model Gateway Target；Contract Freeze 附录进一步冻结 Security / Infrastructure / Observability Ownership、ModelOperationKind、ModelCall 聚合、Budget / Usage / Quota 崩溃语义、事件目录、三层 Streaming、Routing Replay、Capability 生命周期和 ResultValidity 传播。

Current 调用清单及旁路状态仍由代码、测试和 `docs/status/production-readiness.md` 证明。并行 PR 中出现的名称仍是 `Parallel Proposal`，不能因附录引用而提升为 Current 或 Confirmed Target。

专用验证：

```text
python tools/scripts/verify_model_gateway_target_protocols.py
python tools/scripts/verify_model_gateway_contract_freeze.py
pytest -q tests/repo/test_model_gateway_target_protocols.py tests/repo/test_model_gateway_contract_freeze.py -p no:cacheprovider
```

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

## Agent 镜像

```text
docs/modules/06-agent-core-planning-control.md
.agent/modules/06-agent-core-planning-control.md
```

正式文件与镜像必须字节级一致。

规则：

- 不得只修改 `.agent/modules/`；
- 不得在 Target 文档中写 Current Baseline 或具体迁移步骤；
- Current 变化只有在代码、Migration、测试、Trace、Eval 和运行证据完成后，才可写入状态文档；
- 模块设计不得放回 `docs/architecture/`；
- Agent Core 变更必须同步单一正式文档、镜像、入口、验证器和测试。

专用验证：

```text
python tools/scripts/verify_agent_core_target_protocols.py
pytest -q tests/repo/test_agent_core_target_protocols.py -p no:cacheprovider
```
