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

总架构以 `docs/architecture/architecture.md` 为最高层入口；Current、Gap 和 Blocked 状态以 `docs/status/production-readiness.md` 为事实源。

## 十一个逻辑模块

| 编号 | 模块 | 正式模块文档 | 状态 |
| --- | --- | --- | --- |
| 01 | Product Surface | `01-product-surface.md` | 待细化 |
| 02 | Input / Document Ingestion | [`02-input-document-ingestion.md`](../../docs/modules/02-input-document-ingestion.md) | 已建立 Target 规范 |
| 03 | Knowledge / Agentic GraphRAG | [`03-knowledge-agentic-graphrag.md`](../../docs/modules/03-knowledge-agentic-graphrag.md) | 已建立 Target 规范 |
| 04 | Model Gateway | `04-model-gateway.md` | 待细化 |
| 05 | Memory & Context | [`05-memory-context.md`](../../docs/modules/05-memory-context.md) | 已建立 Target 规范 |
| 06 | Agent Core / Planning & Control | [`06-agent-core-planning-control.md`](./06-agent-core-planning-control.md) | 已建立 V2 Target 规范与 Agent 镜像 |
| 07 | Capability / Skill | [`07-capability-skill.md`](../../docs/modules/07-capability-skill.md) | 已建立 Target 规范 |
| 08 | Tool Runtime | `08-tool-runtime.md` | 待细化 |
| 09 | Security | `09-security.md` | 待细化 |
| 10 | Observability & Eval | [`10-observability-eval.md`](../../docs/modules/10-observability-eval.md) | 已建立 Target 规范 |
| 11 | Infrastructure | `11-infrastructure.md` | 待细化 |

## Agent 镜像

`docs/modules/` 是正式事实源。当前 `.agent/modules/` 只保留 Agent 系统需要频繁读取的模块镜像：

```text
.agent/modules/README.md
.agent/modules/06-agent-core-planning-control.md
```

Agent Core 正式文件与镜像必须保持字节级一致：

```text
docs/modules/06-agent-core-planning-control.md
.agent/modules/06-agent-core-planning-control.md
```

其余模块直接读取 `docs/modules/` 正式文件，避免维护不完整或过期副本。

规则：

- 不得只修改 `.agent/modules/`；
- 模块文档描述 Target 时必须明确标记，不得冒充 Current；
- Current 能力只有在代码、迁移、测试、Eval 和运行证据完成后，才能写入 `docs/status/production-readiness.md`；
- 模块设计不得放回 `.agent/architecture/`。

## 与总架构的关系

```text
.agent/architecture/
    总架构四个 canonical 镜像文件

.agent/modules/
    逻辑模块实施级设计镜像
```
