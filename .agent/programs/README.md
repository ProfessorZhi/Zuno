# Agent 执行计划

`.agent/programs/` 只保存当前可执行计划或等待态入口。当前没有 active program；已完成的 program 必须整体归档到 `docs/history/programs/`，不要把旧 phase 文件留在前台路径。

## 当前状态

- State: no-active
- 当前入口：[current.md](current.md)
- 下一 program 还没有打开。

## 前台文件

- [current.md](current.md)：说明当前没有 active program，并指向最近完成归档。
- [implementation-roadmap.md](implementation-roadmap.md)：等待态路线骨架；打开新 program 时替换为新 program roadmap。
- [closure-checklist.md](closure-checklist.md)：通用收口闸门；打开新 program 时可复用或替换为新 program checklist。

## 最近归档

- `docs/history/programs/zuno-eight-deliverables-full-realization-v1/`
- `docs/history/programs/zuno-six-layer-internalization-v1/`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/`
- `docs/history/programs/zuno-target-architecture-migration-v1/`
- `docs/history/programs/zuno-architecture-surface-cleanup-v1/`
- `docs/history/programs/zuno-workflow-doc-system-v1/`
- `docs/history/programs/zuno-target-architecture-refresh-v1/`

## 使用规则

- 每次只打开一个 active program。
- 新 program 必须从 `PHASE01` 开始编号。
- active phase 文件必须平铺在 `.agent/programs/` 根目录。
- completed program 必须归档到 `docs/history/programs/`。
- `.agent/architecture/future/programs/` 中的 queued drafts 只能作为参考输入，不能被写成 active。
