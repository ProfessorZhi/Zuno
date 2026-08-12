# Technology Reality

本文件回答：历史项目实际使用了什么？必须把用户个人参与、团队使用、框架提供、当前仓库表面和新 Target 分开。

## Historical Technology Reality Matrix

| Technology / Capability | Historical status | Evidence | User involvement | Confidence | Notes |
|---|---|---|---|---|---|
| Python | `UNKNOWN` | 当前仓库是 Python 后端 | 未确认本人负责全程 Python 后端 | Low | 当前 Python 不能反推历史全程 Python |
| FastAPI | `UNKNOWN` | 当前仓库有 FastAPI 入口 | 未确认本人负责全部 API | Low | 不写成个人主责 |
| LangGraph | `LEARNED_ONLY` | 用户确认加入后学习 LangGraph；当前仓库也有相关表面 | 参与 Agent 开发，但具体 LangGraph 代码贡献 UNKNOWN | Medium | 不等于完整 Runtime 或生产主链路 |
| OpenViking | `CONFIRMED_USED` | 用户明确确认参与 Memory / Context 区域接入 | 有本人参与 | High | 不等于系统所有 Memory、法律事实存储或生产关键路径 |
| Agent development | `CONFIRMED_USED` | 用户明确确认参与 Agent 部分开发 | 有本人参与 | High | 不等于整个 Agent Runtime Owner |
| Tool Calling Strategy | `CONFIRMED_USED` | 用户明确确认参与工具调用策略开发 | 有本人参与 | High | 具体选择、参数、失败和权限语义仍 UNKNOWN |
| GraphRAG | `LEARNED_ONLY` | 用户确认在开发过程中学习，学长要求学习 | 学习参与，产品实现范围 UNKNOWN | Medium | 必须区分 Experiment / Demo / Main Path |
| Database access | `CONFIRMED_USED` | 用户明确确认亲自进入数据库查看/调试数据 | 有本人参与 | High | 具体产品、表、SQL、客户端和历史版本 UNKNOWN |
| PostgreSQL | `UNKNOWN` | 当前 Migration/Compose/代码有部分表面 | 用户是否操作过 PostgreSQL UNKNOWN | Low | 数据库操作事实不等于 PostgreSQL 产品已确认 |
| RabbitMQ | `UNKNOWN` | 当前 Compose/代码有 RabbitMQ 表面 | 用户参与 UNKNOWN | Low | 不能反推历史使用 |
| MinIO | `UNKNOWN` | 当前 Compose/代码有对象存储表面 | 用户参与 UNKNOWN | Low | 不能反推历史使用 |
| Milvus | `UNKNOWN` | 当前依赖/Compose/配置有向量存储表面 | 用户参与 UNKNOWN | Low | 不能反推历史使用 |
| Neo4j | `UNKNOWN` | 当前 Compose/依赖有图存储表面 | 用户参与 UNKNOWN | Low | 不能反推历史 GraphRAG 产品主链路 |
| Elasticsearch | `UNKNOWN` | 当前依赖/配置有检索表面 | 用户参与 UNKNOWN | Low | 不能反推历史使用 |
| Redis | `UNKNOWN` | 当前 Compose/代码有缓存/基础设施表面 | 用户参与 UNKNOWN | Low | 不能反推历史使用 |
| Hybrid Retrieval / BM25 / Vector / Reranker | `UNKNOWN` | 简历候选和当前代码表面不足以确认历史产品链路 | 用户参与 UNKNOWN | Low | 需要实验、旧 Demo 或代码证据 |
| MCP | `UNKNOWN` | 当前仓库有 MCP API/服务表面 | 用户参与 UNKNOWN | Low | 不能反推历史项目使用或用户负责 |
| Pytest | `UNKNOWN` | 当前仓库有测试 | 历史测试参与 UNKNOWN | Low | 不能反推历史测试流程 |
| Docker / Docker Compose | `UNKNOWN` | 用户部分回忆本地大概率使用；当前仓库也有 Compose | 用户可能参与本地启动，具体服务 UNKNOWN | Medium | 历史服务清单和启动方式仍 UNKNOWN |

允许的技术状态只有：`CONFIRMED_USED`、`TEAM_USED_USER_INVOLVEMENT_UNKNOWN`、`EXPERIMENTED`、`LEARNED_ONLY`、`PARTIAL_REPOSITORY_EVIDENCE`、`TARGET_ONLY`、`UNKNOWN`。本表中的历史状态如果没有直接历史证据，保留为 `UNKNOWN`，括号中的当前仓库观察不改变它。

## Current Repository Partial Evidence

当前 `main` 可以复核到的表面包括：

- Python 3.12、FastAPI 入口、Agent/Memory/Knowledge/Tool 代码和测试；
- PostgreSQL Migration 与运行配置；
- Compose 中的 PostgreSQL、Redis、RabbitMQ、Neo4j、MinIO、Milvus 等服务表面；
- 依赖和配置中的 Elasticsearch、MCP、GraphRAG、LangGraph Checkpointer 等表面。

这些都统一标为 `PARTIAL_REPOSITORY_EVIDENCE`。当前仓库未发现 OpenViking 的实现或依赖；这不否定用户记忆中的历史接入，反而说明历史项目与当前仓库不能简单等同。当前仓库也没有证明上述所有组件曾在同一历史版本、同一环境或生产路径中运行。

## 用户个人与团队边界

```text
个人确认：Agent 参与、Memory 任务、OpenViking Memory/Context 接入、Tool Calling Strategy、LangGraph/GraphRAG 学习、数据库查看/调试。

团队或他人工作：全部 RAG、全部 GraphRAG、全部 FastAPI、全部数据库、法律算法、整体架构、生产部署和客户项目管理，当前不能归属于用户。

框架提供：LangGraph/OpenViking 等库的通用能力；参与接入不等于实现框架本身。
```

## Target Only

以下属于新架构目标，不能写入历史 Current：

```text
Python-only backend
Microservice Architecture
Legal Domain Kernel
Domain-aware Runtime
新的 Multi-Agent 服务模型
新的 Legal Intelligence Engine
新的 Service Boundary
```

## 事实 Owner

本文件负责历史技术矩阵和证据边界；具体实现证据进入 [`../../evidence/`](../../evidence/README.md)，候选解释和下一轮问题进入 [`../../../project-red-blue/01-project-facts.md`](../../../project-red-blue/01-project-facts.md)。
