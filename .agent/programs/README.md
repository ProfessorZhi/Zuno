# Agent 执行计划

`.agent/programs/` 当前处于 no-active 等待态。

## 当前状态

- State: no-active
- Active program: none
- Current phase: none
- Latest completed program: `zuno-production-architecture-and-deliverables-completion-v1`
- Latest completed archive: `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`

## 文件

- `current.md`：当前 no-active 状态、最近完成归档和下一轮打开规则。
- `implementation-roadmap.md`：最近完成 program 的归档摘要和下一轮执行规则。
- `closure-checklist.md`：no-active 状态和最近完成 program 的归档检查结果。

PHASE01-PHASE12 文件不留在前台路径；它们已归档到：

- `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`

## 使用规则

- `.agent/programs/` 只保存当前 active program，或像现在一样保存 no-active 等待态入口。
- completed program 必须整体归档到 `docs/history/programs/`。
- 新 program 必须从 PHASE01 开始，并同步 `AGENTS.md`、README、`.agent/references/current-program.md`、verifier 和 repo tests。
- 只写 contract、schema 或 README 不能关闭 runtime phase。
