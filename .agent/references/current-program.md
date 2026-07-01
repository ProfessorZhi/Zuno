# 当前 Program 状态

## Current Truth

state: no-active
active_program: none
current_phase: none
latest_completed_program: zuno-production-architecture-and-deliverables-completion-v1

`.agent/programs/` 当前处于明确 no-active 等待态，只保留：

- `README.md`
- `current.md`
- `implementation-roadmap.md`
- `closure-checklist.md`

最新完成并归档的 program：

- `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`

该 program 已完成 PHASE01-PHASE12，是一次性交付型成熟化 program，目标是把 Zuno 从“第一版 runtime-first vertical slice 已完成”推进到“成熟目标架构和四大总交付物完成”。四大总交付物和八类 runtime-first 交付物口径以 `docs/architecture/production-readiness.md` 为准。

本轮继续保留 runtime-first / vertical-slice-first 验收规则：只写 contract、schema 或 README 不能关闭 runtime phase。

最新完成 program 的 Current 事实只能来自代码、测试、trace、eval 或 verifier 证据；未完成的生产级外部平台、真实隔离、凭据、网络、持续评测和 Desktop 发布能力仍以 `docs/architecture/production-readiness.md` 的 Remaining Target 为准。

## 当前执行规则

- 每轮开始必须重新确认当前 worktree、branch、`git status --short --branch`、允许范围和禁止范围。
- 打开新 program 必须从 PHASE01 开始。
- active phase 文件只在有 active program 时平铺在 `.agent/programs/` 根目录。
- completed program 必须归档到 `docs/history/programs/`。
- 本轮没有 active program；如要继续推进生产目标架构，先打开新的 PHASE01 truth source。

## 最近完成归档

- `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`：完成 PHASE01-PHASE12 的生产成熟化 program、四大总交付物、八类 runtime-first deliverables、release closure、full verification 和 no-active closure。
- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`：完成 PHASE01-PHASE12 的 runtime-first 目标架构第一版闭环。
- `docs/history/programs/zuno-master-architecture-implementation-v1/`：完成 PHASE01-PHASE12 的目标架构分阶段实现、架构刷新和 release closure。
- `docs/history/programs/zuno-architecture-detail-and-execution-plan-v1/`：完成架构文档、架构图、HTML 和后续执行计划细化。
- `docs/history/programs/zuno-eight-deliverables-full-realization-v1/`：完成上一轮八大治理交付物闭环，范围是 PHASE01-PHASE10。
- `docs/history/programs/zuno-six-layer-internalization-v1/`：完成六层内部第一批 foundation surfaces。
- `docs/history/programs/zuno-repo-layout-cleanup-v1/`：完成顶层六层目录和 final alias surface closure；旧 public import path 由 `src/backend/zuno/platform/compatibility/legacy_aliases.py` 保护。

## Future Reference Drafts

以下旧 draft 仍是未来参考输入，不是 active program：

- `zuno-runtime-architecture-upgrade-v1`
- `zuno-architecture-visuals-v1`
