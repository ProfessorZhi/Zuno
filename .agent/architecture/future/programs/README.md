# Queued Programs

这里保存短期四目标拆出来的后续 program 草案。它们不是当前 active program，不能直接从这里执行。

当前没有 active program；下一次打开 program 时，active phase 文件只允许平铺在 `.agent/programs/` 根目录。

## 当前状态

- `zuno-workflow-doc-system-v1` 已完成，归档在 `docs/history/programs/zuno-workflow-doc-system-v1/`。
- `zuno-target-architecture-refresh-v1` 已完成，归档在 `docs/history/programs/zuno-target-architecture-refresh-v1/`。
- `zuno-repo-layout-cleanup-v1` 已完成，归档在 `docs/history/programs/zuno-repo-layout-cleanup-v1/`。

## Queued 顺序

1. [zuno-runtime-architecture-upgrade-v1](zuno-runtime-architecture-upgrade-v1/implementation-roadmap.md)
2. [zuno-architecture-visuals-v1](zuno-architecture-visuals-v1/implementation-roadmap.md)

## 使用规则

- 每次只打开一个 program。
- 打开时把对应 roadmap 和 phase 文件迁入 `.agent/programs/`，并从 `PHASE01` 开始。
- 被替换的 active program 必须先归档到 `docs/history/programs/`。
- 单个 queued roadmap 或 phase 文件必须写明 `queued draft / not active`，避免被误当成当前执行计划。
