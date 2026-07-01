# 当前 Program 状态

## Current Truth

state: active
active_program: zuno-production-architecture-and-deliverables-completion-v1
current_phase: PHASE08_durable-agent-runtime-persistence

`.agent/programs/` 当前保存 active program 的平铺执行计划：

- `README.md`
- `current.md`
- `implementation-roadmap.md`
- `closure-checklist.md`
- `PHASE01_production-maturity-gap-audit.md`
- `PHASE02_program-truth-source-and-execution-system.md`
- `PHASE03_workflow-self-maintenance-automation.md`
- `PHASE04_documentation-dedup-architecture-clarity.md`
- `PHASE05_repo-ownership-and-compatibility-retirement.md`
- `PHASE06_product-surface-desktop-recovery-loop.md`
- `PHASE07_production-parse-and-index-platform.md`
- `PHASE08_durable-agent-runtime-persistence.md`
- `PHASE09_memory-context-production-governance.md`
- `PHASE10_tool-sandbox-vault-network-runtime.md`
- `PHASE11_production-graphrag-evidence-citation.md`
- `PHASE12_security-trace-eval-release-closure.md`

本轮是一次性交付型成熟化 program，目标是把 Zuno 从“第一版 runtime-first vertical slice 已完成”推进到“成熟目标架构和四大总交付物完成”。四大总交付物和八类 runtime-first 交付物口径以 `docs/architecture/production-readiness.md` 为准。

最近完成并归档的 program：

- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`

该 program 的 runtime-first closure evidence 保留在归档目录；本状态索引不重复闭环链路细节。

本轮继续保留 runtime-first / vertical-slice-first 验收规则：只写 contract、schema 或 README 不能关闭 runtime phase。

它仍然遵守 Current / Target / Future / History 边界：未由代码、测试、trace、eval 或 verifier 证明的能力不能写成 Current。成熟度和 runtime-first 交付物口径以 `docs/architecture/production-readiness.md` 为准；本文件只记录 program 状态、归档位置和下一轮打开规则。

## 当前执行规则

- 每轮开始必须重新确认当前 worktree、branch、`git status --short --branch`、允许范围和禁止范围。
- 必须按 PHASE01 -> PHASE12 顺序推进。
- active phase 文件平铺在 `.agent/programs/` 根目录。
- 已完成 program 必须归档到 `docs/history/programs/`。
- 当前 active program 授权围绕成熟目标架构和四大总交付物推进；每个 phase 的具体写入范围仍以 phase 文件和用户指令为准。

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
