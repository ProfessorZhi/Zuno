# Zuno

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.121-009688?logo=fastapi&logoColor=white)
![Vue](https://img.shields.io/badge/Vue-3-42B883?logo=vuedotjs&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-5-646CFF?logo=vite&logoColor=white)
![Electron](https://img.shields.io/badge/Electron-32-47848F?logo=electron&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

Zuno 是一个个人 Agent 工作台，把聊天、Agent 执行、MCP 服务、Skills、知识库检索、本地工具和桌面自动化放进同一个可运行环境里。

它的目标不是做一个只有聊天框的前端，而是提供一套本地优先的 Agent 操作台：Web 可访问、桌面可启动、Docker 可一键跑全套依赖，配置和数据能在本机稳定保留。

## 功能

- 多模型 Agent 对话与工具调用。
- MCP 服务、Skills 和本地 CLI 工具接入。
- 知识库检索、向量库和 GraphRAG 相关能力。
- Web 工作台，基于 Vue 3 + Vite。
- Electron 桌面壳，复用后端和本地桌面前端。
- Docker Compose 一键启动 PostgreSQL、Redis、Neo4j、MinIO、后端和前端。
- Windows 启动器固定入口，方便做桌面快捷方式。

## 技术栈

| 层 | 技术 |
| --- | --- |
| 后端 | Python 3.12, FastAPI, LangChain, LangGraph, SQLModel |
| 前端 | Vue 3, Vite, TypeScript, Pinia, Element Plus |
| 桌面端 | Electron |
| 数据与缓存 | PostgreSQL, Redis, Neo4j, MinIO, Chroma/vector DB |
| 运行与部署 | Docker Compose, nginx, Windows CMD/PowerShell launchers |
| Agent 扩展 | MCP, Skills, local CLI tools |

## 目录结构

```text
Zuno/
├─ src/
│  ├─ backend/          # FastAPI 后端、Agent runtime、RAG、MCP、工具执行
│  └─ frontend/         # Vue 3 Web 工作台
├─ apps/
│  └─ desktop/          # Electron 桌面端
├─ infra/
│  └─ docker/           # Dockerfile、Compose、nginx、运行配置模板
├─ launchers/           # Windows Web/Desktop 稳定启动入口
├─ tools/
│  ├─ cli/              # 可被 Agent 调用的本地 CLI 工具
│  ├─ scripts/          # 本地维护脚本
│  └─ migrations/       # 一次性迁移脚本
├─ docs/                # 架构、API、数据库和运行参考
├─ tests/               # 仓库级测试
└─ .local/              # 本地资料和历史运行数据，不提交
```

## 端口

| 服务 | 地址 |
| --- | --- |
| Web UI | <http://127.0.0.1:8090> |
| Backend API | <http://127.0.0.1:7860> |
| Backend health | <http://127.0.0.1:7860/health> |
| API docs | <http://127.0.0.1:7860/docs> |
| Desktop local frontend | <http://127.0.0.1:8091> |
| Redis | `127.0.0.1:6379` |
| Neo4j Browser | <http://127.0.0.1:7474> |
| Neo4j Bolt | `127.0.0.1:7687` |
| MinIO API | <http://127.0.0.1:9000> |
| MinIO Console | <http://127.0.0.1:9001> |

## Docker 一键运行

要求：

- Docker Desktop 或 Docker Engine + Compose v2。
- 至少 6 GB 可用内存。
- 第一次运行前复制本地配置文件。

在仓库根目录执行：

```powershell
copy infra\docker\docker_config.example.yaml infra\docker\docker_config.local.yaml
docker compose -f infra/docker/docker-compose.yml up --build -d
```

启动后打开：

- Web UI：<http://127.0.0.1:8090>
- 健康检查：<http://127.0.0.1:7860/health>
- API 文档：<http://127.0.0.1:7860/docs>

停止但保留数据：

```powershell
docker compose -f infra/docker/docker-compose.yml down
```

删除容器和 Docker volumes：

```powershell
docker compose -f infra/docker/docker-compose.yml down -v
```

`down -v` 会清掉 PostgreSQL、Redis、Neo4j、MinIO 和后端向量库数据。只有在需要重置本地运行状态时再用。

更多 Docker 细节见 [infra/docker/README.md](./infra/docker/README.md)。

## Windows Launchers

Windows 稳定入口在 `launchers/`，适合绑定桌面快捷方式：

```powershell
.\launchers\Zuno-Web-Start.cmd
.\launchers\Zuno-Web-Stop.cmd
.\launchers\Zuno-Web-Rebuild.cmd
.\launchers\Zuno-Web-Full-Rebuild.cmd
```

```powershell
.\launchers\Zuno-Desktop-Start.cmd
.\launchers\Zuno-Desktop-Stop.cmd
.\launchers\Zuno-Desktop-Rebuild.cmd
.\launchers\Zuno-Desktop-Full-Rebuild.cmd
```

Web 启动器负责 Docker Web 栈，等待 `7860` 和 `8090` 可用。Desktop 启动器会启动后端容器、本地桌面前端和 Electron，等待 `7860` 和 `8091` 可用。

桌面运行日志在 `%TEMP%\zuno-desktop-runtime`，优先看 `desktop.err.log`、`frontend.err.log`。更多说明见 [launchers/README.md](./launchers/README.md)。

## 开发运行

后端：

```powershell
pip install -r requirements.txt
cd src\backend
uvicorn agentchat.main:app --host 0.0.0.0 --port 7860
```

前端：

```powershell
cd src\frontend
npm install
npm run dev -- --host 127.0.0.1 --port 8090
```

桌面端：

```powershell
cd apps\desktop
npm install
npm start
```

Docker 热更新开发模式：

```powershell
docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml up --build -d
```

## 数据与配置持久化

- `infra/docker/docker_config.local.yaml`：本机 Docker 运行配置，放真实模型配置和 API keys，不提交。
- `src/backend/agentchat/config.yaml`：本地后端配置文件，按需要维护，不建议提交真实密钥。
- `src/backend/agentchat/config.local.yaml`：本地覆盖配置，不提交。
- `.local/`：个人资料、学习材料、历史运行数据，不提交。
- Docker volumes：`postgres_data`、`redis_data`、`neo4j_data`、`neo4j_logs`、`minio_data`、`backend_vector_db`。
- Docker 后端会把 `infra/docker/docker_config.local.yaml` 挂载到容器内 `/app/agentchat/config.yaml`。

## 常见问题

### Web 能打开但聊天失败

先看后端健康检查：

```powershell
curl http://127.0.0.1:7860/health
docker logs --tail 200 agentchat-backend
```

如果后端正常但 Agent 不回答，检查 `infra/docker/docker_config.local.yaml` 里的模型和 key。

### Docker Compose 配置报错

确认正在使用 Compose v2：

```powershell
docker compose version
docker compose -f infra/docker/docker-compose.yml config
```

### 旧 MCP 或工具记录导致启动异常

优先在 UI 里清理失效记录。确认要重置本地数据时再执行：

```powershell
docker compose -f infra/docker/docker-compose.yml down -v
```

### Docker 拉取或构建很慢

可以给 npm、PyPI、Debian 传镜像源：

```powershell
docker compose -f infra/docker/docker-compose.yml build `
  --build-arg NPM_REGISTRY=https://registry.npmmirror.com `
  --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple `
  --build-arg DEBIAN_MIRROR=mirrors.tuna.tsinghua.edu.cn
```

### Electron 没出现但服务可用

检查：

```powershell
curl http://127.0.0.1:8091
notepad $env:TEMP\zuno-desktop-runtime\desktop.err.log
```

## 验证

```powershell
cd src\frontend
npm run lint
npm run build
```

```powershell
pytest tests/test_launcher_scripts.py
```

```powershell
docker compose -f infra/docker/docker-compose.yml config
docker compose -f infra/docker/docker-compose.yml build frontend backend
```

## 参考文档

- [Zuno 项目参考](./docs/reference/zuno.md)
- [核心架构](./docs/reference/core.md)
- [数据库结构](./docs/reference/database.md)
- [API 参考](./docs/reference/api.md)
- [Docker 运行](./infra/docker/README.md)
- [Windows Launchers](./launchers/README.md)
