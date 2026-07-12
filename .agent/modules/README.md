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
如何证明 Target 已经实现
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
| 06 | Agent Core / Planning & Control | [`06-agent-core-planning-control.md`](./06-agent-core-planning-control.md)；[`06-agent-core-control-protocols.md`](./06-agent-core-control-protocols.md) | 已建立 Target 主设计、控制协议与 Agent 镜像 |
| 07 | Capability / Skill | [`07-capability-skill.md`](../../docs/modules/07-capability-skill.md) | 已建立 Target 规范 |
| 08 | Tool Runtime | `08-tool-runtime.md` | 待细化 |
| 09 | Security | `09-security.md` | 待细化 |
| 10 | Observability & Eval | [`10-observability-eval.md`](../../docs/modules/10-observability-eval.md) | 已建立 Target 规范 |
| 11 | Infrastructure | `11-infrastructure.md` | 待细化 |

## Agent Core 规范性文档集

```text
.agent/modules/06-agent-core-planning-control.md
    问题、概念架构、完整运行流程、模块边界和实施规格

.agent/modules/06-agent-core-control-protocols.md
    架构不变量、三套状态机、DAG 与并发协议、Signal、副作用、
    Finalization、失败预算、Ownership 和 Contract Versioning
```

对应正式事实源：

```text
docs/modules/06-agent-core-planning-control.md
docs/modules/06-agent-core-control-protocols.md
```

这些文件只描述 Target。Current 与 Gap 读取 `docs/status/production-readiness.md`，后续升级 Program 以正式 Target 为目标约束。

## Agent 镜像

`docs/modules/` 是正式事实源。当前 `.agent/modules/` 保留 Agent 系统需要频繁读取的入口与 Agent Core 镜像：

```text
.agent/modules/README.md
.agent/modules/06-agent-core-planning-control.md
.agent/modules/06-agent-core-control-protocols.md
```

正式文件与镜像必须分别保持字节级一致：

```text
docs/modules/06-agent-core-planning-control.md
.agent/modules/06-agent-core-planning-control.md

docs/modules/06-agent-core-control-protocols.md
.agent/modules/06-agent-core-control-protocols.md
```

其余模块直接读取 `docs/modules/` 正式文件，避免维护不完整或过期副本。

规则：

- 不得只修改 `.agent/modules/`；
- 模块文档描述 Target 时必须明确标记，不得冒充 Current；
- Current 能力只有在代码、Migration、测试、Eval 和运行证据完成后，才能写入 `docs/status/production-readiness.md`；
- 模块设计不得放回 `.agent/architecture/`；
- Agent Core 控制协议变更必须同步正式文档、镜像、验证器和测试。

专用验证：

```text
python tools/scripts/verify_agent_core_target_protocols.py
pytest -q tests/repo/test_agent_core_target_protocols.py -p no:cacheprovider
```

## 与总架构的关系

```text
.agent/architecture/
    总架构四个 canonical 镜像文件

.agent/modules/
    逻辑模块实施级 Target 设计镜像
```
