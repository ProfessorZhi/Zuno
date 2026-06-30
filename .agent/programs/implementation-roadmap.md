# zuno-target-architecture-runtime-full-implementation-v1 实施路线

## Program Definition

本 program 是完整目标架构 runtime 实现 program，不是架构细化 program，也不是 contract foundation program。它把上一轮 `zuno-master-architecture-implementation-v1` 留在 Target 的能力，沿一条真实用户闭环推进到可运行、可观测、可评测和可交付。

## Runtime-first 验收口径

一个 phase 只有满足以下条件之一，才能把能力写成 Current：

1. 真实 API / runtime / UI 路径已经接通。
2. focused tests 或 e2e 回放证明该路径可运行。
3. trace / eval / release gate 能复现该路径的证据。
4. verifier 固定了防漂移边界。

只新增 type、contract、README、diagram 或 future plan，不能关闭 runtime phase。

## Phase Map

| Phase | 名称 | 状态 | 目标 |
| --- | --- | --- | --- |
| PHASE01 | program-reopen-and-truth-source-freeze | completed | 打开新 active program，冻结 runtime-first 验收口径和事实源。 |
| PHASE02 | runtime-migration-map-and-repo-ownership-lock | completed | 固定旧 runtime 与六层 target owner 的迁移图和兼容策略。 |
| PHASE03 | task-session-artifact-event-runtime | completed | 已打通 workspace / session / file / ingest / task / approval / event / artifact / feedback 后端 API 与 SSE runtime surface。 |
| PHASE04 | document-ingestion-parse-runtime | completed | 已让 `knowledge/ingestion` 拥有 Parse Gateway runtime owner surface、adapter registry、fixture replay、job status 和 legacy chunk normalizer。 |
| PHASE05 | index-jobs-and-knowledge-space-runtime | completed | 已将 Document IR 送入本地 BM25 / vector / graph index job runtime，并提供 manifest、失败重试、回放和 retrieval payload。 |
| PHASE06 | durable-single-controller-runtime | completed | 已在 Single Controller harness 之上提供 durable checkpoint / interrupt / resume / cancel / failure runtime surface，并接入 workspace task snapshot / approval / cancel API。 |
| PHASE07 | memory-db-and-context-governance | active | 将 MemoryEngine 升级为可持久化、可审查、可治理的 memory runtime。 |
| PHASE08 | tool-control-plane-approval-and-sandbox-runtime | pending | 接通真实 executor、approval API/UI、credential broker 和 sandbox profile。 |
| PHASE09 | agentic-retrieval-evidence-citation-runtime | pending | 让 Agentic retrieval 消费新 index runtime 并输出稳定 citation。 |
| PHASE10 | security-observability-and-online-eval | pending | 将 security gates、ZunoSpan、eval baseline 接入真实运行时。 |
| PHASE11 | web-desktop-surface-and-feedback-loop | pending | 完成用户可感知的上传、事件流、审批、artifact、citation、trace 和 feedback UI。 |
| PHASE12 | release-gate-full-e2e-closure | pending | 以完整 vertical slice 做 release closure、归档、验证、commit、merge 和 push。 |

## 黄金脊柱

最短路径优先打通：

```text
PHASE03 task/session/event/artifact
  -> PHASE04 parse runtime
  -> PHASE05 index jobs
  -> PHASE06 runtime state
  -> PHASE09 retrieval/evidence/citation
  -> PHASE10 trace/eval
  -> PHASE11 UI/feedback
  -> PHASE12 e2e closure
```

PHASE07 与 PHASE08 可以在黄金脊柱稳定后并行加深，但不能改变 Single Controller Agent 近期主线。

## 八类 runtime 交付物

1. 产品闭环交付物：workspace、session、task、event、artifact、feedback、SSE 和 Web/Desktop 基本界面。
2. 文档解析与索引交付物：Parse Gateway runtime、Document IR、parser adapters、chunk/provenance/ACL、BM25/vector/graph index job。
3. Agent Runtime 交付物：durable state graph、checkpoint/resume、interrupt/approval wait、plan/replan、post-turn commit。
4. Memory 与 Context 交付物：raw event log、recent window、task summary、durable memory store、promotion/decay/consolidation、context pack。
5. Tool Control Plane 与 Sandbox 交付物：ToolCard registry、executor adapters、approval gate、credential broker、sandbox profile、network policy、audit trail。
6. Knowledge / GraphRAG / Evidence / Citation 交付物：basic/local/global/drift runtime、fusion/rerank、EvidenceBundle、CitationBuilder、unsupported claim guard、graph extraction/index job。
7. Security / Trace / Eval / Release 交付物：四道安全闸、redaction、sandbox audit、ZunoSpan、dataset、offline/online eval、CI release gate。
8. 仓库治理与一致性交付物：README、architecture、`.agent/programs/current.md`、HTML、verifier、legacy guards 和历史归档一致。

## Program-level 验证

每个 phase 至少运行：

```powershell
git diff --check
python .agent/scripts/verify_agent_system.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py -p no:cacheprovider
```

涉及 runtime 的 phase 必须追加对应 focused tests；PHASE12 必须追加完整 e2e 回放、parser golden、retrieval/eval/security baseline 和 full repo verification。
