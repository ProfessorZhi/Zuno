# Zuno

Zuno 是一个面向复杂任务执行的 Agent 工作台与能力管理系统。

它把对话、工具、MCP、知识库、Skill 和桌面端运行整合到同一套界面与执行链路里，适合用来搭建、测试和迭代可配置的 Agent 应用。

## 主要功能

### 工作台

- 支持聊天模式与 Agent 模式
- 支持会话历史、上下文延续与执行进展展示
- 支持图片、PDF、Word、PPT、TXT、Markdown、Excel 等附件输入
- 支持 Web 与桌面端一致的工作台交互

### MCP

- 支持内置与自定义 MCP 服务管理
- 支持 `STDIO` 与 `流式 HTTP` 两种标准接入方式
- 支持连接测试、工具发现、用户级参数配置与状态校验

### Skill、工具与知识库

- 支持系统工具与自定义工具管理
- 支持 Skill 管理、绑定与工作台快速调用
- 支持知识库上传、解析、索引与检索增强问答

### 桌面端

- 提供 Electron 客户端
- 支持本地启动、停止、重建与桌面化联调
- 支持与本地文件、终端和执行环境联动

## 系统架构

Zuno 当前采用单 Agent 工作台架构。

- 以单一主 Agent 作为统一执行入口
- 基于 ReAct 模式组织推理与工具调用
- 将 MCP、Skill、知识库、工具与终端能力纳入同一条执行链路
- 通过显式命令、能力配置与运行时状态，提升能力可见性与调用稳定性

## 技术栈

### 后端

- Python
- FastAPI
- LangChain
- LangGraph
- SQLModel
- MCP Runtime / Adapters
- RAG Pipeline

### 前端

- Vue 3
- TypeScript
- Vite
- Element Plus

### 桌面端

- Electron
- Node.js

### 基础设施

- MySQL
- Redis
- MinIO
- Docker

## 目录结构

```text
Zuno/
├─ src/
│  ├─ backend/      # 后端服务、Agent runtime、MCP、RAG
│  └─ frontend/     # 前端控制台与工作台界面
├─ desktop/         # Electron 客户端
├─ docker/          # Docker 部署文件
├─ docs/            # 项目文档
├─ scripts/         # 启动、停止、重建脚本
├─ cli_tools/       # 本地 CLI 工具目录
└─ README.md
```

## 快速开始

### 分别启动服务

后端：

```bash
python scripts/start.py
```

前端：

```bash
cd src/frontend
npm install
npm run dev
```

桌面端：

```bash
cd desktop
npm install
npm run dev
```

如果只想单独启动桌面端测试栈，优先使用 `desktop/` 和 `scripts/` 下的现成脚本。

### 使用脚本

`scripts/` 目录下提供了 Windows 启动脚本：

- `zuno-start.bat`
- `zuno-stop.bat`
- `zuno-rebuild-start.bat`
- `zuno-clean-rebuild-start.bat`

### 使用 Docker

```bash
cd docker
docker compose up -d
```

## 文档

- 仓库地址：<https://github.com/ProfessorZhi/Zuno>
- 文档目录：[docs](./docs)

## License

MIT
