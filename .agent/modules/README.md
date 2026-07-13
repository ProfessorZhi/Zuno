# Zuno 逻辑模块设计文档镜像

`.agent/modules/` 保存 Agent System 高频读取的模块镜像；`docs/modules/` 是正式事实源。

## 十一个逻辑模块

| 编号 | 模块 | 正式模块文档 | 状态 |
| --- | --- | --- | --- |
| 01 | Product Surface | `01-product-surface.md` | 待细化 |
| 02 | Input / Document Ingestion | [`02-input-document-ingestion.md`](../../docs/modules/02-input-document-ingestion.md) | 已建立 Target 规范 |
| 03 | Knowledge / Agentic GraphRAG | [`03-knowledge-agentic-graphrag.md`](../../docs/modules/03-knowledge-agentic-graphrag.md) | 已建立 Target 规范 |
| 04 | Model Gateway | `04-model-gateway.md` | 待细化 |
| 05 | Memory & Context | [`05-memory-context.md`](../../docs/modules/05-memory-context.md) | 已建立 Target 规范 |
| 06 | Agent Core / Planning & Control | [`06-agent-core-planning-control.md`](./06-agent-core-planning-control.md) | 单一完整 Target 架构镜像 |
| 07 | Capability / Skill | [`07-capability-skill.md`](../../docs/modules/07-capability-skill.md) | 已建立 Target 规范 |
| 08 | Tool Runtime | `08-tool-runtime.md` | 待细化 |
| 09 | Security | `09-security.md` | 待细化 |
| 10 | Observability & Eval | [`10-observability-eval.md`](./10-observability-eval.md)；[`RAG Core Five / Agentic GraphRAG / Agent Efficiency 附录`](./10-observability-eval-rag-agent-evaluation.md) | 实施级 Target 架构镜像 |
| 11 | Infrastructure | `11-infrastructure.md` | 待细化 |

## 字节级一致的 Target 镜像

```text
.agent/modules/06-agent-core-planning-control.md
.agent/modules/10-observability-eval.md
.agent/modules/10-observability-eval-rag-agent-evaluation.md
```

对应正式事实源：

```text
docs/modules/06-agent-core-planning-control.md
docs/modules/10-observability-eval.md
docs/modules/10-observability-eval-rag-agent-evaluation.md
```

Agent Core 定义控制运行时、状态与一致性生命周期。Observability & Eval 主文档定义 Trace/Audit/Eval/Evidence、Agent Core 证据映射、交付与恢复、Release Gate 和质量证明标准；受控附录定义 RAG Core Five、Agentic GraphRAG 全过程 Trace、Graph Failure Bucket、Agent Efficiency 与质量约束下的效率 Gate。

Current 与 Gap 读取 `docs/status/production-readiness.md`；实现与迁移计划读取 `.agent/programs/`。正式文件、受控附录与对应镜像必须字节级一致，不得只修改 `.agent/modules/`。

专用验证：

```text
python tools/scripts/verify_agent_core_target_protocols.py
pytest -q tests/repo/test_agent_core_target_protocols.py -p no:cacheprovider

python tools/scripts/verify_observability_eval_target_protocols.py
pytest -q tests/repo/test_observability_eval_target_protocols.py -p no:cacheprovider
```