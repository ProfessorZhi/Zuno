# 当前程序

state: no-active
active_program: none
current_phase: none
latest_completed_program: zuno-production-architecture-and-deliverables-completion-v1

## 当前状态

`.agent/programs/` 当前是明确 no-active 等待态。最近完成的 active program 已整体归档：

- `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`

该 program 是一次性交付型成熟化 program，已完成 PHASE01-PHASE12，把 Zuno 从“第一版 runtime-first vertical slice 已完成”推进到“成熟目标架构和四大总交付物完成”的本地可验证 baseline。

## 最近完成归档

- `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`：完成 PHASE01-PHASE12 的生产成熟化收口，包含四大总交付物、八类 runtime-first 交付物、release evidence、full verification 和 no-active closure。
- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`：完成 PHASE01-PHASE12 的 runtime-first 目标架构第一版闭环。
- `docs/history/programs/zuno-master-architecture-implementation-v1/`：完成 PHASE01-PHASE12 的目标架构分阶段实现、架构刷新和 release closure。

## 继续打开 program 的规则

- 新 program 必须从 PHASE01 开始。
- 打开前必须重新确认当前 worktree、branch、`git status --short --branch`、允许范围和禁止范围。
- 生产成熟度和 runtime-first 交付物口径以 `docs/architecture/production-readiness.md` 为准。
- 只写 contract、schema 或 README 不能关闭 runtime phase；Current 必须来自代码、测试、trace、eval 或 verifier 证据。
- 不把 Codex 多 agent 执行方式写成 Zuno 产品 runtime 多 Agent 架构。
