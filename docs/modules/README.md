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
| 04 | Model Gateway | `04-model-gateway.md` | 待细化 |
| 05 | Memory & Context | [`05-memory-context.md`](./05-memory-context.md) | 已建立 Target 规范 |
| 06 | Agent Core / Planning & Control | [`06-agent-core-planning-control.md`](./06-agent-core-planning-control.md) | 已建立单一完整 Target 架构文档 |
| 07 | Capability / Skill | [`07-capability-skill.md`](./07-capability-skill.md) | 已建立 Target 规范 |
| 08 | Tool Runtime | `08-tool-runtime.md` | 待细化 |
| 09 | Security | `09-security.md` | 待细化 |
| 10 | Observability & Eval | [`10-observability-eval.md`](./10-observability-eval.md)；[`RAG Core Five / Agentic GraphRAG / Agent Efficiency 附录`](./10-observability-eval-rag-agent-evaluation.md) | 已建立实施级 Target 规范 |
| 11 | Infrastructure | `11-infrastructure.md` | 待细化 |

## 单一正式 Target 与 Agent 镜像

当前要求字节级同步的模块：

```text
docs/modules/06-agent-core-planning-control.md
.agent/modules/06-agent-core-planning-control.md

docs/modules/10-observability-eval.md
.agent/modules/10-observability-eval.md

docs/modules/10-observability-eval-rag-agent-evaluation.md
.agent/modules/10-observability-eval-rag-agent-evaluation.md
```

Agent Core 文档统一包含概念架构、运行流程、不变量、状态机、DAG 与并发、Interrupt / Signal、副作用、Finalization、一致性、事件、Artifact、恢复、时间、目标代码、数据库和测试规格。

Observability & Eval 主文档统一包含 Trace/Audit/Eval/Evidence 边界、Agent Core 证据映射、事件交付、状态机、存储、恢复、Release Gate 与质量证明标准。受控附录冻结 RAG Core Five、Agentic GraphRAG 全过程 Trace、Graph Failure Bucket、Agent Efficiency、质量约束下的效率比较和对应 Evidence 要求；附录属于模块正式 Target，不是 History 或实现计划。

执行和迁移计划不写入模块 Target 文档：

```text
.agent/programs/    Current → Target 的实现、迁移、切流和收口计划
docs/status/       Current、Gap、Measurement 和完成状态
docs/history/      已完成 Program 与历史证据
```

规则：

- 不得只修改 `.agent/modules/`；
- 不得在 Target 文档中把计划中的表、类或流程写成 Current；
- Current 变化只有在代码、Migration、测试、Trace、Eval 和运行证据完成后，才可写入状态文档；
- 模块设计不得放回 `docs/architecture/`；
- Agent Core 与 Observability & Eval 变更必须同步正式文档、受控附录、镜像、入口、专用验证器和测试。

专用验证：

```text
python tools/scripts/verify_agent_core_target_protocols.py
pytest -q tests/repo/test_agent_core_target_protocols.py -p no:cacheprovider

python tools/scripts/verify_observability_eval_target_protocols.py
pytest -q tests/repo/test_observability_eval_target_protocols.py -p no:cacheprovider
```