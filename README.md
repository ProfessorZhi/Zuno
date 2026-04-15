# Zuno

Zuno 是一个面向复杂任务执行场景的 Agent 工作台与能力管理系统。  
它把对话、工具、MCP、知识库、Skill 和桌面端执行整合到同一套界面与运行链路中，适合用来搭建和测试可配置的 Agent 应用。

## 功能特性

### 工作台

- 支持聊天模式、Agent 模式与终端模式
- 支持图片、PDF、Word、PPT、TXT、Markdown、Excel 等附件输入
- 支持会话历史、上下文延续和执行进展展示

### MCP

- 支持内置与自定义 MCP 服务管理
- 支持 `STDIO` 与 `流式 HTTP` 两种标准接入方式
- 支持连接测试、工具发现、用户级参数配置和状态校验

### 工具、Skill 与知识库

- 支持系统工具与自定义工具管理
- 支持 Skill 绑定与调用
- 支持知识库上传、解析、索引与检索增强回答

### 桌面端

- 提供 Electron 客户端
- 支持本地启动、停止、重建与桌面化调试
- 支持与本地文件、终端和执行环境联动

## 系统架构

Zuno 当前采用单 Agent 工作台架构。

- 以单主 Agent 作为统一执行入口
- 通过 ReAct 模式组织推理与工具调用
- 将 MCP、Skill、知识库、工具与终端能力接入同一运行链路
- 通过显式命令与能力配置，提升不同能力的可见性、可控性与命中率

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
|-- src/
|   |-- backend/      # 后端服务、Agent runtime、MCP、RAG
|   `-- frontend/     # 前端控制台与工作台界面
|-- desktop/          # Electron 客户端
|-- docker/           # Docker 部署文件
|-- docs/             # 项目文档
|-- scripts/          # 启动、停止、重建脚本
|-- cli_tools/        # 本地 CLI 工具目录
`-- README.md
```

## 快速开始

### 分别启动服务

后端：

```bash
cd src/backend
python -m agentchat.main
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

- 项目仓库：<https://github.com/ProfessorZhi/Zuno>
- 文档目录：[docs](./docs)

## License

MIT
