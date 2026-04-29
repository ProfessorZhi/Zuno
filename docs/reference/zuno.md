# Zuno 项目参考

Zuno 是一个本地优先的个人 Agent 工作台，用 Web、桌面端和 Docker 运行栈统一承载聊天、Agent 执行、MCP、Skills、知识库、工具和模型配置。

## 核心入口

- `src/backend/`：FastAPI 后端、Agent runtime、RAG、MCP 和工具执行。
- `src/frontend/`：Vue 3 + Vite Web 工作台。
- `apps/desktop/`：Electron 桌面端壳层。
- `infra/docker/`：Dockerfile、Compose、nginx 和容器运行配置模板。
- `launchers/`：Windows Web/Desktop 稳定启动入口。
- `tools/cli/`：可被 Agent 调用的本地 CLI 工具。
- `tools/scripts/`：本地维护脚本。
- `tools/migrations/`：一次性迁移脚本。

## 运行入口

- Web UI：`http://127.0.0.1:8090`
- 后端健康检查：`http://127.0.0.1:7860/health`
- API 文档：`http://127.0.0.1:7860/docs`
- 桌面本地前端：`http://127.0.0.1:8091`

## 本地资料与配置

- `.local/` 放个人资料、学习材料和历史运行数据，不提交。
- `infra/docker/docker_config.local.yaml` 放 Docker 本地模型配置和密钥，不提交。
- `src/backend/agentchat/config.local.yaml` 放本地后端覆盖配置，不提交。
- Docker named volumes 保存 PostgreSQL、Redis、Neo4j、MinIO 和后端向量库数据。

## 相关文档

- [README](../../README.md)
- [核心架构](./core.md)
- [数据库结构](./database.md)
- [API 参考](./api.md)
- [Docker 运行](../../infra/docker/README.md)
