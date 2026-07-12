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
| 06 | Agent Core / Planning & Control | 见下方规范性文档集 | 已建立 Target 主设计、控制协议与一致性协议 |
| 07 | Capability / Skill | [`07-capability-skill.md`](./07-capability-skill.md) | 已建立 Target 规范 |
| 08 | Tool Runtime | `08-tool-runtime.md` | 待细化 |
| 09 | Security | `09-security.md` | 待细化 |
| 10 | Observability & Eval | [`10-observability-eval.md`](./10-observability-eval.md) | 已建立 Target 规范 |
| 11 | Infrastructure | `11-infrastructure.md` | 待细化 |

## Agent Core 规范性文档集

Agent Core Target 由三份正式文档共同构成：

```text
docs/modules/06-agent-core-planning-control.md
    主设计：问题、概念架构、完整运行流程、模块边界、目标代码和持久化规格。

docs/modules/06-agent-core-control-protocols.md
    控制协议：不变量、状态机、DAG、并发、Interrupt、Signal、副作用、Finalization、Failure 与 Budget。

docs/modules/06-agent-core-consistency-lifecycle-protocols.md
    一致性协议：TaskContract、命令仲裁、Domain/Checkpoint、ResultValidity、Event、Artifact、Reconciler 与时间语义。
```

入口：

- [`06-agent-core-planning-control.md`](./06-agent-core-planning-control.md)
- [`06-agent-core-control-protocols.md`](./06-agent-core-control-protocols.md)
- [`06-agent-core-consistency-lifecycle-protocols.md`](./06-agent-core-consistency-lifecycle-protocols.md)

规范优先级：

```text
全局架构原则
→ Agent Core 规范性协议
→ Agent Core 主设计实施规格
→ 后续 Program 与代码
```

三份文件都只描述 Target。Current 与 Gap 不写入这里；升级和迁移步骤放入 `.agent/programs/`。

## Agent 镜像

`docs/modules/` 是正式事实源。Agent Core 保留同名镜像：

```text
docs/modules/06-agent-core-planning-control.md
.agent/modules/06-agent-core-planning-control.md

docs/modules/06-agent-core-control-protocols.md
.agent/modules/06-agent-core-control-protocols.md

docs/modules/06-agent-core-consistency-lifecycle-protocols.md
.agent/modules/06-agent-core-consistency-lifecycle-protocols.md
```

每一对正式文档与镜像必须字节级一致。

规则：

- 不得只修改 `.agent/modules/`；
- 不得在 Target 文档中写 Current Baseline 或具体迁移步骤；
- Current 变化只有在代码、Migration、测试、Trace、Eval 和运行证据完成后，才可写入状态文档；
- 模块设计不得放回 `docs/architecture/`；
- Agent Core 变更必须同步三份文档、三份镜像、入口、验证器和测试。

专用验证：

```text
python tools/scripts/verify_agent_core_target_protocols.py
pytest -q tests/repo/test_agent_core_target_protocols.py -p no:cacheprovider
```

## 与总架构的关系

```text
docs/architecture/architecture.md
    总架构、十一模块关系、全局约束和 Owner 边界。

docs/modules/*.md
    单个逻辑模块的实施级 Target 设计。
```
