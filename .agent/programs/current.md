# 当前程序

state: active
active_program: zuno-target-architecture-runtime-full-implementation-v1
current_phase: PHASE04_document-ingestion-parse-runtime

## 目标

本 program 将 Zuno 从“目标架构已定义、contracts 已成型”推进到“目标架构第一版 runtime 闭环真实可跑”。它以用户确认的 runtime-first / vertical-slice-first 口径为准，不再允许用 contract foundation 代替 runtime 验收。

## 核心闭环

```text
upload document
  -> parse
  -> index
  -> ask
  -> Agentic retrieval
  -> cited answer
  -> trace/eval
  -> artifact/feedback
```

## 当前阶段

- `PHASE01_program-reopen-and-truth-source-freeze.md`：completed。
- `PHASE02_runtime-migration-map-and-repo-ownership-lock.md`：completed。
- `PHASE03_task-session-artifact-event-runtime.md`：completed。
- `PHASE04_document-ingestion-parse-runtime.md`：active。
- `PHASE05_index-jobs-and-knowledge-space-runtime.md`：pending。
- `PHASE06_durable-single-controller-runtime.md`：pending。
- `PHASE07_memory-db-and-context-governance.md`：pending。
- `PHASE08_tool-control-plane-approval-and-sandbox-runtime.md`：pending。
- `PHASE09_agentic-retrieval-evidence-citation-runtime.md`：pending。
- `PHASE10_security-observability-and-online-eval.md`：pending。
- `PHASE11_web-desktop-surface-and-feedback-loop.md`：pending。
- `PHASE12_release-gate-full-e2e-closure.md`：pending。

## 最近完成归档

最近完成的 foundation program 是 `zuno-master-architecture-implementation-v1`：

- `docs/history/programs/zuno-master-architecture-implementation-v1/`

## 本轮硬边界

- 目标架构不推倒重来；正式事实源仍是 `docs/architecture/architecture.md`。
- README 只保留摘要和入口；active program 事实源是 `.agent/programs/current.md` 与 `.agent/references/current-program.md`。
- 本轮验收从“contract 可关闭”改为“真实 vertical slice 可跑、可追踪、可评测才关闭”。
- 生产级能力不能因计划存在而写成 Current；Current 必须来自代码、测试、trace、eval 或 verifier。
- 兼容路径不为了视觉清爽删除；runtime owner 迁移必须由 import matrix、focused tests 和 verifier 保护。
