# Zuno Web

`apps/web/` 是 Zuno 的 Vue 3 + Vite Web 工作台。

它负责：

- 用户登录、会话、知识库、模型、工具、MCP、Skill 等管理界面
- workspace 聊天与 Agent 交互体验
- 和 `src/backend/zuno` 暴露的 HTTP / SSE 接口对接

它不负责：

- 后端业务逻辑
- 数据库迁移
- Docker 基础设施
- Electron 桌面宿主逻辑

## Development

在仓库根目录执行：

```bash
npm run frontend:dev
```

或在当前目录执行：

```bash
npm install
npm run dev
```

默认本地后端地址是 `http://127.0.0.1:7860`。

## Build

```bash
npm run build
```

## Related Paths

- `apps/desktop/`：桌面壳，消费这个 web workspace
- `src/backend/`：后端运行时
- `tools/launchers/windows/`：Windows 稳定启动脚本
