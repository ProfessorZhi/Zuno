# 当前执行计划占位

> 状态：当前没有 active program。每次新 program 都从 `PHASE01` 开始编号。

`.agent/programs/` 目前只保留入口和收口规则，不保存已完成 program 的 phase 文件。

## 等待打开的 Program

- `zuno-runtime-architecture-upgrade-v1`：queued / not active，位于 `.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/`。
- `zuno-architecture-visuals-v1`：queued / not active，位于 `.agent/architecture/future/programs/zuno-architecture-visuals-v1/`。

## 打开规则

1. 确认当前 `.agent/programs/` 没有 `PHASE*.md` 或旧 `thread-prompts/`。
2. 从 `.agent/architecture/future/programs/` 迁入一个 queued program。
3. 迁入后的 active program 必须从 `PHASE01` 开始，phase 文件平铺在 `.agent/programs/` 根目录。
4. 多线程模式下，主线程先划分粗粒度任务，再把本轮线程提示词放到 `.agent/programs/thread-prompts/`。
5. 完成后按 `closure-checklist.md` 自维护审查并归档到 `docs/history/programs/`。

## 已完成归档

- `docs/history/programs/zuno-workflow-doc-system-v1/`
- `docs/history/programs/zuno-target-architecture-refresh-v1/`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/`
