# Zuno 逻辑模块设计文档

`docs/modules/` 是 Zuno 十一个逻辑模块的正式设计文档目录。

这里回答的是：

```text
每个模块负责什么
不负责什么
代码应放在哪里
对外提供什么 Contract / Port
内部如何分层
如何持久化
如何测试和验收
如何从 Current 迁移到 Target
```

总架构仍以 `docs/architecture/architecture.md` 为最高层设计入口；Current、Gap 和 Blocked 状态仍以 `docs/architecture/production-readiness.md` 为事实源。

## 十一个逻辑模块

| 编号 | 模块 | 正式模块文档 | 状态 |
| --- | --- | --- | --- |
| 01 | Product Surface | `01-product-surface.md` | 待细化 |
| 02 | Input / Document Ingestion | `02-input-document-ingestion.md` | 待细化 |
| 03 | Knowledge / Agentic GraphRAG | `03-knowledge-agentic-graphrag.md` | 待细化 |
| 04 | Model Gateway | `04-model-gateway.md` | 待细化 |
| 05 | Memory & Context | `05-memory-context.md` | 待细化 |
| 06 | Agent Core / Planning & Control | [`06-agent-core-planning-control.md`](./06-agent-core-planning-control.md) | 已建立 V2 Target 规范 |
| 07 | Capability / Skill | `07-capability-skill.md` | 待细化 |
| 08 | Tool Runtime | `08-tool-runtime.md` | 待细化 |
| 09 | Security | `09-security.md` | 待细化 |
| 10 | Observability & Eval | `10-observability-eval.md` | 待细化 |
| 11 | Infrastructure | `11-infrastructure.md` | 待细化 |

## Agent 镜像

每份正式模块文档在 `.agent/modules/` 下保留同名镜像：

```text
docs/modules/<module>.md
.agent/modules/<module>.md
```

规则：

- `docs/modules/` 是正式事实源；
- `.agent/modules/` 只是 Agent 工作镜像；
- 两份同名文档必须保持字节级一致；
- 不得只修改 `.agent/modules/`；
- 模块文档描述 Target 时，必须明确标记，不得冒充 Current；
- Current 能力只有在代码、迁移、测试、Eval 和运行证据完成后才能写入 `production-readiness.md`。

## 与 architecture 专题文档的关系

```text
docs/architecture/architecture.md
    总架构、十一模块关系、运行域和全局约束

docs/modules/*.md
    单个逻辑模块的实施级设计

docs/architecture/*-runtime.md 等专题
    跨模块专题、历史兼容入口或专项附录
```

Agent Core 当前的精确 PostgreSQL DDL 与 Alembic 规格同时保留在：

```text
docs/modules/06-agent-core-planning-control.md
docs/architecture/agent-core-runtime.md
```

后续清理时应以 `docs/modules/06-agent-core-planning-control.md` 作为模块入口，避免新增第三套互相竞争的规范。