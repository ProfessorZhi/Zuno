# Agent 执行计划

`.agent/programs/` 当前处于 no-active 等待态。

## 当前状态

- State: no-active
- Active program: none
- Current phase: none
- Latest completed program: `zuno-production-document-ingestion-and-thread-foundation-v1`

最近完成的 Program 1 已归档到：

- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`

## 当前文件

- `current.md`：当前 no-active 状态、最近完成 program 和下一轮候选。
- `implementation-roadmap.md`：Program 1-5 总路线、当前完成状态、queued program 顺序和下一轮启动门槛。
- `closure-checklist.md`：Program 1 closure 结果、no-active 自维护检查和下一轮启动前检查。
- `queued-programs/`：Program 2-5 的后续计划，不是当前 active phase。

## 已归档 Program 1

`zuno-production-document-ingestion-and-thread-foundation-v1` 已完成 PHASE01-PHASE08：

- parser current audit
- Document IR / parser adapter contract freeze
- parser worker runtime and job lifecycle
- native text and structured file parsers
- PDF / Office / OCR / VLM adapter boundaries
- index handoff provenance and fixtures
- 后续 Runtime Subsystems thread prompts and branch plan
- verification, docs sync and no-active closure

Runtime Subsystems thread prompts 保存在归档目录的 `thread-prompts/` 下。它们是后续 Program 3 可复用输入，不代表 Program 3 已启动。

## 使用规则

- `.agent/programs/` 根目录只保存当前状态文件；completed phase 文件必须移入 `docs/history/programs/<program-id>/`。
- 后续 queued program 可以放在 `queued-programs/`，但不得写成 active program。
- 新 program 必须从 PHASE01 开始，并同步 `AGENTS.md`、README、`.agent/references/current-program.md`、verifier 和 repo tests。
- 只写 contract、schema 或 README 不能关闭 runtime phase。
- 多线程执行必须由当前主线程先确认真实 UI 目标模式和独立 worktree / branch；提示词目标模式不等于 Codex UI 目标模式。
