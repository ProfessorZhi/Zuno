# 当前 Program 状态

## Current Truth

当前没有 active program。

`.agent/programs/` 只保留：

- `README.md`
- `current.md`
- `implementation-roadmap.md`
- `closure-checklist.md`

最新完成并归档的 program：

- `docs/history/programs/zuno-repo-layout-cleanup-v1/`

## 最近完成事实

`zuno-repo-layout-cleanup-v1` 已完成：

- root/docs hygiene 和 repo hygiene guardrails。
- `src/backend/` 顶层只保留 `zuno/`。
- `src/backend/fastapi_jwt_auth/` 顶层 shell 已退休。
- prompt、fixture、system skill 资源已进入 `resources/`。
- legacy / vendor 兼容材料已进入 `compatibility/`。
- MCP server implementations 已进入 `capability/mcp/servers/`。
- HTTP middleware implementations 已进入 `platform/middleware/`。
- 仍保留的旧 runtime 顶层目录已有 README 分类和 verifier guard。

## 等待打开

queued draft / not active：

- `.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/`
- `.agent/architecture/future/programs/zuno-architecture-visuals-v1/`

打开下一 program 前必须先更新 `.agent/programs/current.md`、`.agent/programs/implementation-roadmap.md`、`docs/architecture/roadmap.md` 和 verifier/test，并从 `PHASE01` 开始。
