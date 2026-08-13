# Current Repository Reality

status: current-baseline
canonical_question: 当前 main 的仓库真正有什么代码、配置、Migration、测试和可复现证据？
owner: Status / Evidence Owner
evidence_scope: 当前 Git 树与仓库内可检查的配置表面；不是历史项目档案，也不是生产证明

> 本文只描述当前 `main` 能由仓库文件、测试或可复现检查支持的事实。当前仓库是 `PARTIAL_REPOSITORY_EVIDENCE`，不等于完整历史项目。

## 1. 可以由当前仓库证明的内容

### 应用与语言表面

- 后端代码包含 Python 包和 FastAPI 应用入口；`src/backend/zuno/main.py` 创建 FastAPI 应用并注册 API 路由。
- `pyproject.toml` 声明了 LangGraph、MCP、FastAPI、SQLModel、Alembic、Redis、RabbitMQ 客户端、Milvus、Neo4j、MinIO 等依赖表面。
- 当前仓库包含 Agent、Knowledge、Memory、Capability、MCP / Tool 和 Observability 相关包或 Contract；这些目录存在不等于每条路径都已在真实环境运行。

### 数据、队列和本地运行表面

- `infra/db/alembic/versions/` 包含 PostgreSQL 相关 Migration；这只能证明当前仓库有数据库演进材料，不能推出历史客户环境使用了同一版本。
- `infra/docker/docker-compose.yml` 定义了 `backend`、`worker`、`frontend`、`postgres`、`redis`、`rabbitmq`、`neo4j`、`minio`、`milvus` 和相关依赖；Elasticsearch 通过可选 profile 配置，默认不是启动依赖。
- `infra/docker/README.md` 记录了本地 Compose 的启动说明，以及文档解析、RAG / GraphRAG 索引 Worker 的当前运行表面。
- 仓库有测试、Verifier、Migration 和部分 Evidence 文档；它们的通过范围必须以实际命令输出为准。

### 当前仓库能支持的有限结论

当前 main 可以支持这样的描述：这是一个以 Python / FastAPI 为主要后端表面、包含 Agent / Knowledge / Memory / Tool 相关代码、PostgreSQL Migration 和本地 Compose 运行材料的仓库。当前代码还存在可供 Target Architecture 对齐的 Domain、Runtime、Knowledge、Security、Eval 和 Worker 相关实现表面。

这不是“完整目标已经实现”的结论。具体 Runtime 行为、真实外部 Provider、端到端质量、运行时隔离和部署资格仍由代码级测试或外部证据分别证明。

## 2. 当前仓库不能证明的内容

- 不能由当前代码反推 2026 年历史项目当时使用了 Python、FastAPI、PostgreSQL、RabbitMQ、Milvus、Neo4j、MinIO 或全部这些组件；
- 不能由 Compose、依赖、目录或 Migration 推出这些组件曾在客户环境同时运行；
- 不能由当前代码推出用户本人负责某个完整模块、完整 RAG、完整 Agent Runtime 或完整后端；
- 不能由论文、研究代码或名称相似的 Contract 推出法律算法已经集成到历史产品；
- 不能由当前测试推出法院 QA、真实用户、Pilot 部署、SLA、QPS、质量收益、HA、Sandbox 安全资格或 Production；
- 不能由 Target Architecture 推出当前已经是微服务，或服务数量已经确定；
- 不能把仓库中的 Target 文档、Mock、目录存在或类名当作生产证据。

## 3. Current / History / Target 的分界

```text
Historical Project
    由用户确认、历史 Artifact 和公开背景恢复；入口是 docs/project/history/。

Current Repository
    由当前 main 的代码、Migration、Config、Test、Trace 或可复现命令证明；入口是本文件和 docs/evidence/。

Target Architecture
    由 docs/project/architecture/、ADR 和 Target Status 表达；不代表当前实现或历史实现。

Future
    尚未决定或没有短期证据门的长期能力。
```

## 4. 证据入口

- 当前可复现证据：[`../../evidence/README.md`](../../evidence/README.md)
- 历史项目事实：[`../history/README.md`](../history/README.md)
- Target 状态：[`target-status.md`](target-status.md)
- 生产状态：[`production-readiness.md`](production-readiness.md)
- 当前仓库启动材料：[`../../../infra/docker/README.md`](../../../infra/docker/README.md)

任何更强结论都必须补充代码、测试、Trace、Eval、Artifact 或外部环境证据，并明确它覆盖的是 Current、History 还是 Target。
