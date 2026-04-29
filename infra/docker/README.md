# Zuno Docker 运行说明

这个目录保存 Zuno 的 Docker Compose 运行栈，用来一次启动 Web 前端、FastAPI 后端和本地基础设施。

## 启动内容

- `frontend`：Vue 生产构建，由 nginx 暴露在 `8090`。
- `backend`：FastAPI 后端，暴露在 `7860`。
- `postgres`：主应用数据库。
- `redis`：缓存。
- `neo4j`：GraphRAG 相关图数据库。
- `minio`：S3 兼容对象存储。

## 要求

- Docker Desktop 或 Docker Engine + Compose v2。
- 至少 6 GB 可用内存。
- 本地配置文件：`infra/docker/docker_config.local.yaml`。

## 快速启动

在仓库根目录执行：

```powershell
copy infra\docker\docker_config.example.yaml infra\docker\docker_config.local.yaml
docker compose -f infra/docker/docker-compose.yml up --build -d
```

macOS/Linux：

```bash
cp infra/docker/docker_config.example.yaml infra/docker/docker_config.local.yaml
docker compose -f infra/docker/docker-compose.yml up --build -d
```

启动后打开：

- Web UI：<http://127.0.0.1:8090>
- 后端健康检查：<http://127.0.0.1:7860/health>
- API 文档：<http://127.0.0.1:7860/docs>
- MinIO Console：<http://127.0.0.1:9001>
- Neo4j Browser：<http://127.0.0.1:7474>

默认基础设施账号：

- PostgreSQL：`postgres` / `postgres`，数据库 `agentchat`
- Neo4j：`neo4j` / `neo4j12345`
- MinIO：`minioadmin` / `minioadmin`

## 配置模型和密钥

`docker_config.local.yaml` 被 git 忽略，用来放真实 API keys 和模型端点。

示例配置能启动服务，但聊天和 Agent 能力需要正确的模型配置。至少检查：

- `multi_models.conversation_model`
- `multi_models.tool_call_model`
- `multi_models.embedding`，如果需要知识库检索
- Tavily、weather、Bocha、delivery 等工具 key，只在需要对应工具时配置

Compose 会把本地配置挂载给后端：

```yaml
AGENTCHAT_CONFIG: /app/agentchat/config.yaml
```

对应挂载：

```yaml
./docker_config.local.yaml:/app/agentchat/config.yaml:ro
```

## 生产镜像模式

默认 Compose 文件不把前后端源码挂进容器，而是从仓库构建镜像：

```powershell
docker compose -f infra/docker/docker-compose.yml build
docker compose -f infra/docker/docker-compose.yml up -d
```

常用检查：

```powershell
docker compose -f infra/docker/docker-compose.yml ps
curl http://127.0.0.1:7860/health
curl http://127.0.0.1:8090
```

## 开发模式

编辑本地源码并希望热更新时，叠加 dev override：

```powershell
docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml up --build -d
```

dev override 会挂载：

- `src/backend` 到 `/app`
- `src/frontend` 到 `/app`
- `tools/cli` 到 `/app/cli_tools`
- `tools/scripts` 到 `/app/scripts`

## 数据持久化

Compose 使用 named volumes 保存运行数据：

- `postgres_data`：PostgreSQL 数据。
- `redis_data`：Redis 数据。
- `neo4j_data`：Neo4j 数据。
- `neo4j_logs`：Neo4j 日志。
- `minio_data`：MinIO 对象存储数据。
- `backend_vector_db`：后端向量库数据。

停止服务但保留数据：

```powershell
docker compose -f infra/docker/docker-compose.yml down
```

删除容器和 named volumes：

```powershell
docker compose -f infra/docker/docker-compose.yml down -v
```

`down -v` 会清空上面的 Docker 数据。旧数据库记录导致启动或运行异常时可以用它重置，例如旧 MCP 记录指向已经不存在的文件。

## 构建镜像源

如果 Docker Hub、npm、Debian 或 PyPI 访问慢，可以传构建镜像源：

```powershell
docker compose -f infra/docker/docker-compose.yml build `
  --build-arg NPM_REGISTRY=https://registry.npmmirror.com `
  --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple `
  --build-arg DEBIAN_MIRROR=mirrors.tuna.tsinghua.edu.cn
```

## 常见问题

### `docker compose config` 失败

确认正在使用 Compose v2：

```powershell
docker compose version
docker compose -f infra/docker/docker-compose.yml config
```

### 前端能打开但登录或聊天失败

先检查后端健康状态和日志：

```powershell
curl http://127.0.0.1:7860/health
docker logs --tail 200 agentchat-backend
```

如果后端正常但 Agent 不回答，检查 `docker_config.local.yaml` 的模型设置。

### 旧 MCP 或工具记录导致异常

优先在 UI 中删除失效记录。确认要重置本地状态时再执行：

```powershell
docker compose -f infra/docker/docker-compose.yml down -v
```

## 相关文档

- [项目 README](../../README.md)
- [Windows Launchers](../../launchers/README.md)
- [Zuno 项目参考](../../docs/reference/zuno.md)
