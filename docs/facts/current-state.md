# Zuno 当前状态

status: `current-baseline`
canonical_question: 当前仓库和交付状态实际上被什么证明？
owner: Facts / Evidence Owner
evidence_scope: 当前 main、仓库配置、测试和可复现证据；不是历史项目完整档案，也不是 Target 设计

> 本文只描述当前可以由代码、Migration、Test、Trace、Eval 或真实运行证据支持的内容。没有证据的结论保留为 `UNKNOWN`、`NOT_MEASURED` 或 `NOT_ESTABLISHED`。

## 当前仓库已证明的表面

- 后端包含 Python 包和 FastAPI 应用入口；`src/backend/zuno/main.py` 创建应用并注册 API 路由。
- `pyproject.toml` 声明了 LangGraph、MCP、FastAPI、SQLModel、Alembic、Redis、RabbitMQ 客户端、Milvus、Neo4j、MinIO 等依赖表面。
- 当前仓库包含 Agent、Knowledge、Memory、Capability、MCP / Tool 和 Observability 相关代码或 Contract；目录存在不等于每条路径都已在真实环境运行。
- `infra/db/alembic/versions/` 包含 PostgreSQL Migration；`infra/docker/docker-compose.yml` 包含 backend、worker、frontend、postgres、redis、rabbitmq、neo4j、minio、milvus 等本地运行表面。
- 仓库包含测试、Verifier、Migration 和当前 Evidence 文档；通过范围以实际命令输出和对应 Evidence 为准。

当前 main 可以支持这样的保守描述：这是一个以 Python / FastAPI 为主要后端表面，包含 Agent / Knowledge / Memory / Tool 相关代码、数据库演进材料和本地 Compose 运行材料的仓库。

## 当前没有被证明的内容

- 当前代码不能反推历史客户环境同时使用过全部声明的技术组件；
- 目录、依赖、Compose、类名、Mock 或 Target 文档不能证明生产部署；
- 当前代码不能推出用户本人负责完整模块、完整 RAG、完整 Agent Runtime 或完整后端；
- 当前测试不能推出法院 QA、真实用户规模、Pilot 部署、SLA、QPS、质量收益、HA、Sandbox 资格或生产资格；
- 当前 Target Architecture 不能推出服务数量已经确定，`FINAL_MODULE_COUNT` 仍未冻结。

## Production Readiness

当前生产状态：`NOT_ESTABLISHED`。

已知的当前状态包括：

- Repository Closure：`CLOSED`；
- Local Workspace Closure：已完成历史现场收口；
- 正式 Benchmark 执行路径可用，但外部数据与运行资格不足，Measurement 为 `blocked_external` / `blocked_not_measured`；
- Architecture Gate 和 Target 设计基线已接受，但不代表实现、测量、安全资格或生产部署；
- Quality：`not_yet_proven`。

尚未建立的生产证据包括真实运行规模、法院 QA、端到端质量、HA、故障恢复、安全资格、No-egress、Sandbox、备份恢复和正式外部验收。

历史 Pilot 不等于 Production；当前代码、Compose、Migration、Target 文档或测试通过也不会自动建立生产证明。

## 证据入口

- 当前可复现证据：[`../evidence/`](../evidence/README.md)
- 当前运行基线：[`../evidence/current-runtime-baseline.md`](../evidence/current-runtime-baseline.md)
- 当前测试基线：[`../evidence/current-test-baseline.md`](../evidence/current-test-baseline.md)
- 当前 Eval 基线：[`../evidence/current-eval-baseline.md`](../evidence/current-eval-baseline.md)
- 当前仓库启动材料：[`../../infra/docker/README.md`](../../infra/docker/README.md)
- Target 设计：[`../architecture/architecture.md`](../architecture/architecture.md)

任何更强结论都必须补充代码、测试、Trace、Eval、Artifact 或外部环境证据，并明确它覆盖的是 Current、Target 还是 History。
