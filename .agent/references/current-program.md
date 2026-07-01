# 当前 Program 状态

## Current Truth

state: no-active
active_program: none
current_phase: none

`.agent/programs/` 当前处于 no-active 等待态，只保留：

- `README.md`
- `current.md`

最近完成并归档的 program：

- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`

该 program 已完成 PHASE01-PHASE12，把 Zuno 从“目标架构已定义、contracts 已成型”推进到“目标架构第一版 runtime 闭环真实可跑”。核心闭环：

```text
上传文档 -> parse -> index -> ask -> Agentic retrieval -> cited answer -> trace/eval -> artifact/feedback
```

本轮关闭后的长期验收规则仍是 runtime-first / vertical-slice-first：只写 contract、schema 或 README 不能关闭 runtime phase。

它仍然遵守 Current / Target / Future / History 边界：未由代码、测试、trace、eval 或 verifier 证明的能力不能写成 Current。成熟度和 runtime-first 交付物口径以 `docs/architecture/production-readiness.md` 为准；本文件只记录 program 状态、归档位置和下一轮打开规则。

## 下一轮打开规则

- 打开下一轮 program 前，必须重新确认当前 worktree、branch、`git status --short --branch`、允许范围和禁止范围。
- 每个新 program 必须从 `PHASE01` 开始。
- active phase 文件只在有 active program 时平铺在 `.agent/programs/` 根目录。
- 已完成 program 必须归档到 `docs/history/programs/`。
- 当前 no-active 状态不授权 runtime、docs 或 workflow 修改；新任务必须由用户给出明确目标或打开新的 program。

## 最近完成归档

- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`：完成 PHASE01-PHASE12 的 runtime-first 目标架构第一版闭环。
- `docs/history/programs/zuno-master-architecture-implementation-v1/`：完成 PHASE01-PHASE12 的目标架构分阶段实现、架构刷新和 release closure。
- `docs/history/programs/zuno-architecture-detail-and-execution-plan-v1/`：完成架构文档、架构图、HTML 和后续执行计划细化。
- `docs/history/programs/zuno-eight-deliverables-full-realization-v1/`：完成上一轮八大交付物闭环，范围是 PHASE01-PHASE10。
- `docs/history/programs/zuno-six-layer-internalization-v1/`：完成六层内部第一批 foundation surfaces。
- `docs/history/programs/zuno-repo-layout-cleanup-v1/`：完成顶层六层目录和 final alias surface closure；旧 public import path 由 `src/backend/zuno/platform/compatibility/legacy_aliases.py` 保护。

## Future Reference Drafts

以下旧 draft 仍是未来参考输入，不是 active program：

- `zuno-runtime-architecture-upgrade-v1`
- `zuno-architecture-visuals-v1`
