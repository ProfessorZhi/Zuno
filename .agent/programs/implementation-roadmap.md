# Agent Program 路线图

> 状态：Program 3 continuation active。每次新 program 都从 `PHASE01` 开始编号；Program 3 continuation 使用延续 phase 编号。

## 当前 Active

`zuno-repo-layout-cleanup-v1` 当前重新打开为 Directory Surface Alignment V1：

- active phase：`.agent/programs/PHASE10_directory-surface-map-and-guardrails.md`
- 历史归档：`docs/history/programs/zuno-repo-layout-cleanup-v1/`

Program 3 不能再写成“文件夹整理完成”。当前完成事实是：

- `src/backend/` 顶层只保留 `zuno/`。
- `src/backend/fastapi_jwt_auth/` 顶层 compatibility shell 已退休。
- `prompts/`、`fixtures/`、`system_skills/` 已迁入 `resources/`。
- `legacy/`、`vendor/` 已迁入 `compatibility/`。
- MCP server implementations 已迁入 `capability/mcp/servers/`，旧 `mcp_servers/` 顶层目录已退休为 `mcp_servers.py` alias module。
- HTTP middleware implementations 已迁入 `platform/middleware/`，旧 `middleware/` 顶层目录已退休为 `middleware.py` alias module。
- Eval tooling 仍在 `tools/evals/zuno/`，旧 `evals/` 顶层目录已退休为 `evals.py` alias module。
- `core/`、`services/`、`schema/`、`tools/`、`utils/`、`database/`、`config/` 等仍保留目录还不是目标完成态，当前 PHASE10 负责目录地图和 guardrails。

## Program 3 当前退出标准

Program 3 closure 不能只看六层目录是否出现。后续完成前至少要满足：

1. `src/backend/zuno/DIRECTORY_MAP.md` 固定每个一等目录的 `keep / migrate / facade / retire` 策略。
2. `api / agent / memory / capability / knowledge / platform` 成为新代码正式入口。
3. 新增 runtime 一等目录必须被 verifier 拦截，除非同步登记。
4. 旧路径如果必须保留，只能作为 compatibility facade 或 alias module。
5. docs / AGENTS / `.agent/references` 按六层指路，不把 Program 4 runtime upgrade 混进 Program 3。

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
