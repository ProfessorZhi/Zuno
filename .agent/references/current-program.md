# 当前 Program 状态

## Current Truth

当前 active program：无。

最近完成：`zuno-repo-layout-cleanup-v1` / Directory Surface Alignment V1。

`.agent/programs/` 当前只保留：

- `README.md`
- `current.md`
- `implementation-roadmap.md`
- `closure-checklist.md`

Program 3 PHASE01-06 和早期 PHASE01-09 历史归档：

- `docs/history/programs/zuno-repo-layout-cleanup-v1/`

## 最近完成事实

`src/backend/zuno` 顶层目录已经收敛为：

- `api/`
- `agent/`
- `memory/`
- `capability/`
- `knowledge/`
- `platform/`

旧 `compatibility/`、`resources/`、`config/`、`database/`、`schema/`、`tools/`、`utils/`、`services/`、`core/` 不再作为顶层目录存在；旧 import path 由受控 `.py` alias module 兼容。

## 等待打开

queued draft / not active：

- `.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/`
- `.agent/architecture/future/programs/zuno-architecture-visuals-v1/`
