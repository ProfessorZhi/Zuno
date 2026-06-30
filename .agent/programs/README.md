# Agent 执行计划

`.agent/programs/` 当前处于 no-active 等待态。

## 当前状态

- State: no-active
- Active program: none
- 最近完成 program: `zuno-master-architecture-implementation-v1`
- 归档位置: `docs/history/programs/zuno-master-architecture-implementation-v1/`

## 使用规则

- 打开下一轮 program 前，必须重新确认 worktree、branch、`git status --short --branch`、允许范围和禁止范围。
- 每个新 program 必须从 `PHASE01` 开始。
- active phase 文件只在有 active program 时平铺在 `.agent/programs/` 根目录。
- completed program 必须归档到 `docs/history/programs/`。
- 本等待态不授权 runtime、docs 或 workflow 修改；新任务必须由用户给出明确目标或打开新的 program。
