# Queued Programs

这里保存短期四目标拆出来的后续 program 草案。它们不是当前 active program，不能直接从这里执行。

当前 active program 只在 `.agent/programs/` 根目录中平铺存在。

## 顺序

1. `zuno-workflow-doc-system-v1`：当前 active，文件位于 `.agent/programs/`。
2. [zuno-target-architecture-refresh-v1](zuno-target-architecture-refresh-v1/implementation-roadmap.md)
3. [zuno-repo-layout-cleanup-v1](zuno-repo-layout-cleanup-v1/implementation-roadmap.md)
4. [zuno-runtime-architecture-upgrade-v1](zuno-runtime-architecture-upgrade-v1/implementation-roadmap.md)
5. [zuno-architecture-visuals-v1](zuno-architecture-visuals-v1/implementation-roadmap.md)

## 使用规则

- 每次只打开一个 program。
- 打开时把对应 roadmap 和 phase 文件迁入 `.agent/programs/`，并从 `PHASE01` 开始。
- 被替换的 active program 必须先归档到 `docs/history/programs/`。
