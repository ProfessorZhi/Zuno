# Agent 执行计划

`.agent/programs/` 只保存当前可执行计划或等待态入口。已完成的 program 必须整体归档到 `docs/history/programs/`，不要把旧 phase 文件留在前台路径。

## 当前状态

- State: active
- Active program: `zuno-architecture-detail-and-execution-plan-v1`
- 当前阶段：[PHASE04_execution-roadmap-from-architecture.md](PHASE04_execution-roadmap-from-architecture.md)
- 当前入口：[current.md](current.md)

## Program 目标

本 program 只做架构文档、总架构文档、架构图 HTML、图清单、program 状态和后续执行计划的细化，重点覆盖 Agent Core、Memory Layer、Tool Control Plane、Document Ingestion、安全、Trace / Eval 和企业知识库场景。它不实施 runtime feature，不新增 API / DB / frontend 行为。

总架构文档 pair 是：

- `docs/architecture/overall-architecture.md`
- `.agent/architecture/overall-architecture.md`

当前 PHASE04 的重点是把架构评估转成后续 runtime implementation programs：Document Ingestion、Runtime + Memory + Tool Plane、Eval / Observability、安全与企业场景。

## 前台文件

- [current.md](current.md)：当前 active program 和边界。
- [implementation-roadmap.md](implementation-roadmap.md)：本 program 的阶段路线和验收。
- [closure-checklist.md](closure-checklist.md)：本 program 的收口闸门。
- [PHASE01_architecture-state-and-program-boot.md](PHASE01_architecture-state-and-program-boot.md)：架构状态与 program 启动。
- [PHASE02_target-architecture-detailing.md](PHASE02_target-architecture-detailing.md)：目标架构细化。
- [PHASE03_mermaid-html-detail-refresh.md](PHASE03_mermaid-html-detail-refresh.md)：Mermaid 与 HTML 展示升级。
- [PHASE04_execution-roadmap-from-architecture.md](PHASE04_execution-roadmap-from-architecture.md)：从架构图反推执行计划。
- [PHASE05_validation-and-closure.md](PHASE05_validation-and-closure.md)：验证、同步和归档准备。

## 最近归档

- `docs/history/programs/zuno-eight-deliverables-full-realization-v1/`
- `docs/history/programs/zuno-six-layer-internalization-v1/`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/`
- `docs/history/programs/zuno-target-architecture-migration-v1/`
- `docs/history/programs/zuno-architecture-surface-cleanup-v1/`
- `docs/history/programs/zuno-workflow-doc-system-v1/`
- `docs/history/programs/zuno-target-architecture-refresh-v1/`

## 使用规则

- 每次只打开一个 active program。
- 每次新 program 都从 `PHASE01` 开始编号。
- active phase 文件必须平铺在 `.agent/programs/` 根目录。
- completed program 必须归档到 `docs/history/programs/`。
- `.agent/architecture/future/programs/` 中的 queued drafts 只能作为参考输入，不能被写成 active。
