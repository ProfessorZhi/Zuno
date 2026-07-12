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
| 06 | Agent Core / Planning & Control | 见下方规范性文档集 | 已建立 Target 主设计、控制协议和一致性协议镜像 |
| 07 | Capability / Skill | [`07-capability-skill.md`](../../docs/modules/07-capability-skill.md) | 已建立 Target 规范 |
| 08 | Tool Runtime | `08-tool-runtime.md` | 待细化 |
| 09 | Security | `09-security.md` | 待细化 |
| 10 | Observability & Eval | [`10-observability-eval.md`](../../docs/modules/10-observability-eval.md) | 已建立 Target 规范 |
| 11 | Infrastructure | `11-infrastructure.md` | 待细化 |

## Agent Core 规范性文档集

```text
.agent/modules/06-agent-core-planning-control.md
    主设计：问题、概念架构、完整运行流程、模块边界、目标代码和持久化规格。

.agent/modules/06-agent-core-control-protocols.md
    控制协议：不变量、状态机、DAG、并发、Interrupt、Signal、副作用、Finalization、Failure 与 Budget。

.agent/modules/06-agent-core-consistency-lifecycle-protocols.md
    一致性协议：TaskContract、命令仲裁、Domain/Checkpoint、ResultValidity、Event、Artifact、Reconciler 与时间语义。
```

对应正式事实源：

```text
docs/modules/06-agent-core-planning-control.md
docs/modules/06-agent-core-control-protocols.md
docs/modules/06-agent-core-consistency-lifecycle-protocols.md
```

入口：

- [`06-agent-core-planning-control.md`](./06-agent-core-planning-control.md)
- [`06-agent-core-control-protocols.md`](./06-agent-core-control-protocols.md)
- [`06-agent-core-consistency-lifecycle-protocols.md`](./06-agent-core-consistency-lifecycle-protocols.md)

这些文件只描述 Target。Current 与 Gap 读取 `docs/status/production-readiness.md`；实现和迁移步骤读取 `.agent/programs/`。

## 镜像规则

正式文件和镜像必须分别保持字节级一致。不得只修改 `.agent/modules/`。

Agent Core 文档不得混入 Current Baseline 或具体实现迁移计划。

专用验证：

```text
python tools/scripts/verify_agent_core_target_protocols.py
pytest -q tests/repo/test_agent_core_target_protocols.py -p no:cacheprovider
```
