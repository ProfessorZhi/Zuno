# Agent Program 路线图

> 状态：当前没有 active program。每次新 program 都从 `PHASE01` 开始编号。

## 最新完成

`zuno-repo-layout-cleanup-v1` 已完成并归档：

- `docs/history/programs/zuno-repo-layout-cleanup-v1/`

Program 3 的最终完成事实：

- `src/backend/` 顶层只保留 `zuno/`。
- `src/backend/fastapi_jwt_auth/` 顶层 compatibility shell 已退休。
- `prompts/`、`fixtures/`、`system_skills/` 已迁入 `resources/`。
- `legacy/`、`vendor/` 已迁入 `compatibility/`。
- MCP server implementations 已迁入 `capability/mcp/servers/`，旧 `mcp_servers/` 只保留 compatibility shell。
- HTTP middleware implementations 已迁入 `platform/middleware/`，旧 `middleware/` 只保留 compatibility shell。
- `core/`、`services/`、`schema/`、`tools/`、`utils/`、`database/`、`config/`、`evals/` 等仍保留的目录都有 README 分类、目标归属、禁止事项和 focused tests。
- `tools/scripts/verify_repo_structure.py` 和 repo tests 固定目录分类、retired paths、root local artifacts 和 first-class responsibility directories。

## 等待打开的 Program

后续 program 仍是 queued draft / not active：

1. `zuno-runtime-architecture-upgrade-v1`
   - 位置：`.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/`
   - 目的：在 Program 3 已完成的目录边界上推进 runtime architecture slices。
   - 边界：不能把 Java、微服务、事件驱动 worker 或产品级多 Agent 模式写成近期实现。

2. `zuno-architecture-visuals-v1`
   - 位置：`.agent/architecture/future/programs/zuno-architecture-visuals-v1/`
   - 目的：优化架构 HTML / Mermaid 展示面。
   - 边界：HTML 不能成为第二套架构真相。

## 打开下一 Program 的步骤

1. 确认用户目标和范围。
2. 更新 `.agent/programs/current.md` 和本文件为新的 active program。
3. 在 `.agent/programs/` 新建 `PHASE01_<name>.md`。
4. 同步 `AGENTS.md`、`.agent/references/current-program.md`、`docs/architecture/roadmap.md`、verifier 和 repo tests。
5. 按新 program 的实际修改范围运行最小有效验证。

## 禁止

- 禁止把 queued draft 当作 active program。
- 禁止在没有 `PHASE01` 的情况下开始新 program。
- 禁止把 Program 3 已完成事实改写成未完成。
- 禁止把 runtime architecture upgrade 或 architecture visuals 混回 Program 3。
