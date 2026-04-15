# Zuno

Zuno 是一个面向复杂任务执行的个人 Agent 平台项目。

它的目标不是“做一个聊天网页”，而是把 **智能体、MCP、Skill、知识库、工具、模型与桌面执行环境** 放进同一个工作台里，让一个主 Agent 能稳定完成真实任务。

## 项目定位

当前 Zuno 的核心方向是：

- 先把 **单 Agent 架构** 做稳
- 把 MCP、Skill、知识库、工具、终端能力统一治理
- 支持 Web 与 Electron 双端运行
- 让用户可以在统一界面中完成配置、测试与执行

换句话说，Zuno 更接近一个 **Agent 工作台 / Agent 应用构建平台**，而不是单纯的对话应用。

## 核心能力

### 1. 工作台执行
- 聊天模式
- Agent 模式
- 终端 / 本地执行模式
- 会话历史与上下文保留

### 2. MCP 管理
- 统一管理平台内 MCP 服务
- 支持用户级配置与测试
- 支持 `STDIO` 与 `流式 HTTP` 两类标准接入
- 支持官方预置 MCP 与自定义 MCP

### 3. Skill / 工具 / 知识库
- Skill 管理与绑定
- 系统工具与自定义工具管理
- 知识库上传、解析、向量检索与问答增强

### 4. 桌面端
- Electron 客户端封装
- 本地工作台运行
- 与本地环境、文件和终端能力联动

## 技术栈

### 后端
- Python
- FastAPI
- LangChain / LangGraph
- SQLModel
- MCP
- RAG

### 前端
- Vue 3
- TypeScript
- Element Plus

### 基础设施
- MySQL
- Redis
- MinIO
- Docker
- Electron

## 项目结构

```text
Zuno/
├─ src/
│  ├─ backend/                 # FastAPI + Agent runtime
│  └─ frontend/                # Vue3 管理后台与工作台
├─ desktop/                    # Electron 客户端
├─ docker/                     # 容器化部署配置
├─ docs/                       # 项目文档
├─ scripts/                    # 启停 / rebuild / 辅助脚本
├─ cli_tools/                  # 本地 CLI 工具目录
└─ README.md
```

## 快速开始

### 方式一：本地开发

#### 1. 启动后端

```bash
cd src/backend
python -m agentchat.main
```

#### 2. 启动前端

```bash
cd src/frontend
npm install
npm run dev
```

#### 3. 启动桌面端

```bash
cd desktop
npm install
npm run dev
```

### 方式二：Docker

```bash
cd docker
docker compose up -d
```

## 开发重点

这个项目当前最重要的设计目标不是“上很多 agent”，而是把 **单 Agent 的能力治理** 做清楚：

- 让 Agent 清楚自己当前有哪些能力
- 让显式命令稳定命中 MCP / Skill / 知识库 / 终端
- 让用户能在界面里看见、配置、测试这些能力
- 让 Web 与桌面端体验尽量一致

## 仓库说明

- GitHub: <https://github.com/ProfessorZhi/Zuno>
- 项目文档目录: [docs](./docs)

## 安全说明

- 仓库中不应提交真实生产密钥、令牌或私有凭证
- 所有真实配置应保留在本地私有环境中
- 当前已移除公开提交中的飞书示例密钥代码

## License

MIT
