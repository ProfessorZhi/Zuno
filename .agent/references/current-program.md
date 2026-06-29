# 当前 Program 状态

## Current Truth

当前 active program：`zuno-repo-layout-cleanup-v1` continuation / Directory Surface Alignment V1。

`.agent/programs/` 当前保留：

- `README.md`
- `current.md`
- `implementation-roadmap.md`
- `closure-checklist.md`
- `PHASE01_directory-closure-master-plan.md`
- `PHASE02_platform-foundation-directory-migration.md`
- `PHASE03_schema-tools-resources-directory-migration.md`
- `PHASE04_services-thinning-directory-migration.md`
- `PHASE05_core-agent-runtime-directory-migration.md`
- `PHASE06_final-six-layer-guard-and-closure.md`

Program 3 PHASE01-09 历史归档：

- `docs/history/programs/zuno-repo-layout-cleanup-v1/`

## 最近完成事实

`zuno-repo-layout-cleanup-v1` 已完成的切片：

- root/docs hygiene 和 repo hygiene guardrails。
- `src/backend/` 顶层只保留 `zuno/`。
- `src/backend/fastapi_jwt_auth/` 顶层 shell 已退休。
- prompt、fixture、system skill 资源已进入 `resources/`。
- legacy / vendor 兼容材料已进入 `compatibility/`。
- MCP server implementations 已进入 `capability/mcp/servers/`。
- HTTP middleware implementations 已进入 `platform/middleware/`。
- 旧 `mcp_servers/`、`middleware/`、`evals/` 顶层兼容壳已退休为 `.py` alias module。
- 当前仍保留的 `compatibility/`、`resources/`、`core/`、`services/`、`database/`、`schema/`、`tools/`、`utils/`、`config/` 说明 Program 3 尚未 closure。PHASE01-06 将分 PR 下沉、迁出、变薄和 final guard。

## Program 3 完成标准

Program 3 结束时，`src/backend/zuno` 顶层目录只允许：

- `api/`
- `agent/`
- `memory/`
- `capability/`
- `knowledge/`
- `platform/`

顶层文件只允许 `__init__.py`、`main.py` 和受控 alias module。

## 等待打开

queued draft / not active：

- `.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/`
- `.agent/architecture/future/programs/zuno-architecture-visuals-v1/`

打开下一 program 前必须先更新 `.agent/programs/current.md`、`.agent/programs/implementation-roadmap.md`、`docs/architecture/roadmap.md` 和 verifier/test，并从 `PHASE01` 开始。
