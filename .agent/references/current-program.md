# 当前 Program 状态

## Current Truth

state: active
active_program: zuno-target-architecture-runtime-full-implementation-v1
current_phase: PHASE09_agentic-retrieval-evidence-citation-runtime

`.agent/programs/` 当前保存 active runtime implementation program：

- `README.md`
- `current.md`
- `implementation-roadmap.md`
- `closure-checklist.md`
- `PHASE01_program-reopen-and-truth-source-freeze.md`
- `PHASE02_runtime-migration-map-and-repo-ownership-lock.md`
- `PHASE03_task-session-artifact-event-runtime.md`
- `PHASE04_document-ingestion-parse-runtime.md`
- `PHASE05_index-jobs-and-knowledge-space-runtime.md`
- `PHASE06_durable-single-controller-runtime.md`
- `PHASE07_memory-db-and-context-governance.md`
- `PHASE08_tool-control-plane-approval-and-sandbox-runtime.md`
- `PHASE09_agentic-retrieval-evidence-citation-runtime.md`
- `PHASE10_security-observability-and-online-eval.md`
- `PHASE11_web-desktop-surface-and-feedback-loop.md`
- `PHASE12_release-gate-full-e2e-closure.md`

## Program 目标

本 program 不是继续细化架构，也不是再做一轮 contract foundation。它以用户确认的 runtime-first / vertical-slice-first 口径为准，把 Zuno 从“目标架构已定义、contracts 已成型”推进到“目标架构第一版 runtime 闭环真实可跑”。

核心闭环：

```text
上传文档 -> parse -> index -> ask -> Agentic retrieval -> cited answer -> trace/eval -> artifact/feedback
```

本轮验收口径：

- 真实 API / runtime / UI 路径已经接通。
- focused tests 或 e2e 回放证明该路径可运行。
- trace / eval / release gate 能复现该路径的证据。
- verifier 固定防漂移边界。

只写 contract、schema 或 README 不能关闭 runtime phase；只新增 diagram 或 future plan 也不能关闭 runtime phase。

## 当前阶段

- `PHASE01_program-reopen-and-truth-source-freeze.md`：completed，已冻结事实源、验收口径和 verifier/test 期望。
- `PHASE02_runtime-migration-map-and-repo-ownership-lock.md`：completed，已固定旧 runtime 与六层 target owner 的迁移图和兼容策略。
- `PHASE03_task-session-artifact-event-runtime.md`：completed，已打通 workspace / session / file / ingest / task / approval / event / artifact / feedback 后端 API 与 SSE runtime surface。
- `PHASE04_document-ingestion-parse-runtime.md`：completed，已把 `knowledge/ingestion` 推进为 Parse Gateway runtime owner surface。
- `PHASE05_index-jobs-and-knowledge-space-runtime.md`：completed，已将 Document IR 送入本地 BM25 / vector / graph index job runtime。
- `PHASE06_durable-single-controller-runtime.md`：completed，已把 Single Controller harness 推进为 controller-node 级 durable checkpoint / interrupt / resume / cancel runtime surface，并接入 workspace task。
- `PHASE07_memory-db-and-context-governance.md`：completed，已提供 snapshot/local replay、SQLModel-backed DatabaseMemoryStore、GeneralAgent memory 接入、governance ledger、sensitive exclusion、promotion、decay、consolidation 和 Context Pack reasons。
- `PHASE08_tool-control-plane-approval-and-sandbox-runtime.md`：completed，已接通本地 deterministic executor、tool approval API/UI bridge、credential ref broker、sandbox context 和 audit trace。
- `PHASE09_agentic-retrieval-evidence-citation-runtime.md`：active，正在让 Agentic retrieval 消费新 index runtime 并输出稳定 citation。
- `PHASE10_security-observability-and-online-eval.md`：pending。
- `PHASE11_web-desktop-surface-and-feedback-loop.md`：pending。
- `PHASE12_release-gate-full-e2e-closure.md`：pending。

## Current / Target 边界

`zuno-master-architecture-implementation-v1` 已完成目标架构分阶段 contract foundation，但 production-grade parser platform、durable LangGraph-compatible runtime、production Memory DB、真实 Tool approval / sandbox、生产级 GraphRAG extraction / fusion / index job、LangSmith / OTel 产品化 trace/eval、online eval、rootless / gVisor / Firecracker sandbox、credential broker、完整 UI trace panel 仍是 Target。

本 program 的任务是把这些 Target 沿一条真实 vertical slice 推进到 Current；推进条件是代码、测试、trace、eval 或 verifier 证据，不是计划文字。

## 最近完成归档

- `docs/history/programs/zuno-master-architecture-implementation-v1/`：完成 PHASE01-PHASE12 的目标架构分阶段实现、架构刷新和 release closure；它是本轮 runtime implementation program 的直接前置 foundation。
- `docs/history/programs/zuno-architecture-detail-and-execution-plan-v1/`：完成架构文档、架构图、HTML 和后续执行计划细化。
- `docs/history/programs/zuno-eight-deliverables-full-realization-v1/`：完成上一轮八大交付物闭环，范围是 PHASE01-PHASE10。
- `docs/history/programs/zuno-six-layer-internalization-v1/`：完成六层内部第一批 foundation surfaces。
- `docs/history/programs/zuno-repo-layout-cleanup-v1/`：完成顶层六层目录和 final alias surface closure；旧 public import path 由 `src/backend/zuno/platform/compatibility/legacy_aliases.py` 保护。

## Future Reference Drafts

以下旧 draft 仍是未来参考输入，不是 active program：

- `zuno-runtime-architecture-upgrade-v1`
- `zuno-architecture-visuals-v1`
