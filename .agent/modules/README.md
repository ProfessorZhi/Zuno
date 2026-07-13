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
| 10 | Observability & Eval | [`10-observability-eval.md`](../../docs/modules/10-observability-eval.md) | 已建立 Target 规范 |
| 11 | Infrastructure | [`11-infrastructure.md`](./11-infrastructure.md) | Target 主文档镜像 + 数据服务能力附录镜像 |

## Agent Core 唯一 Target 镜像

```text
.agent/modules/06-agent-core-planning-control.md
```

对应正式事实源：

```text
docs/modules/06-agent-core-planning-control.md
```

该文档统一包含主设计、控制协议和一致性生命周期协议。Current 与 Gap 读取 `docs/status/production-readiness.md`；实现与迁移计划读取 `.agent/programs/`。

## Infrastructure Target 镜像边界

```text
.agent/modules/11-infrastructure.md
.agent/modules/11-infrastructure-data-services.md
```

对应正式事实源与受控附录：

```text
docs/modules/11-infrastructure.md
docs/modules/11-infrastructure-data-services.md
```

`11-infrastructure.md` 是第 11 模块唯一模块架构事实源。`11-infrastructure-data-services.md` 是其受控规范性展开，覆盖 PostgreSQL、RabbitMQ、Redis、Milvus、Neo4j/可替换图数据库、BM25/可替换 Search runtime、Object Store、Checkpointer、Trace/Audit persistence 与 Secret/KMS 的运行责任、Ownership、故障、重建、隔离、降级和证据要求。

每对正式文件与镜像必须字节级一致，不得只修改 `.agent/modules/`；附录不得成为第二套独立模块架构。

专用验证：

```text
python tools/scripts/verify_agent_core_target_protocols.py
pytest -q tests/repo/test_agent_core_target_protocols.py -p no:cacheprovider
python tools/scripts/verify_infrastructure_target_protocols.py
pytest -q tests/repo/test_infrastructure_target_protocols.py -p no:cacheprovider
```
