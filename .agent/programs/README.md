# Agent 执行计划

`.agent/programs/` 当前处于 no-active 状态。

## 当前状态

- State: no-active
- Active program: none
- Current phase: none
- Latest completed program: `zuno-enterprise-document-ingestion-platform-v2`

最近完成的 Program 1B / V2 已归档到：

- `docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`

## 当前文件

- `current.md`：当前 no-active 状态、最近完成 program 和后续 queued program。
- `implementation-roadmap.md`：Program 1A、Program 1B / V2、Program 3-5 的顺序、依赖和状态。
- `closure-checklist.md`：最近完成 Program 1B / V2 的 closure 结果和下一轮启动检查。
- `queued-programs/`：Program 3-5 的后续计划，不是当前 active phase。

## 已归档 Program 1B / V2

`zuno-enterprise-document-ingestion-platform-v2` 已完成 PHASE01-PHASE08：

- truth source and gap audit
- durable storage contract
- workspace file durable input
- parse / document persistence
- index persistence / rehydrate
- workspace product durable closure
- restart recovery end-to-end
- docs / verifier / archive closure

## 使用规则

- no-active 状态下，`.agent/programs/` 根目录不得保留 `PHASE*.md`。
- queued program 可以放在 `queued-programs/`，但不得写成 active program。
- 新 program 必须从 PHASE01 开始，并同步 `AGENTS.md`、README、`.agent/references/current-program.md`、verifier 和 repo tests。
- 多线程执行必须由当前主线程先确认真实 UI 目标模式和独立 worktree / branch；提示词目标模式不等于 Codex UI 目标模式。
