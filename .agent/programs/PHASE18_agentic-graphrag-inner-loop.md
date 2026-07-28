# PHASE18 Agentic GraphRAG Inner Loop

phase_id: PHASE18
status: in_progress
depends_on: PHASE12, PHASE17
owner: Module 03 Knowledge / Agentic GraphRAG

## Phase 目标

实现固定 KnowledgeRetrievalGraph 与动态 RetrievalPlan/Round，支持 Standard/Local/Global/DRIFT/Deep/Agentic Profile、BM25/Vector/Entity/Relation/Path/Community Retriever、Fusion/Rerank、EvidenceLedger/Frontier、Quality Verdict、Corrective Retrieval 和 KnowledgeControlProposal。内层纠正不得直接修改 Agent Plan。

## Goal04 PR D Startup

status: in_progress
branch: codex/goal04-phase18-agentic-graphrag
base_main_sha: 4d14ae9e8cd953359c82e51d55279cc123ab47ae
startup_evidence: docs/evidence/goal04-phase18-startup-audit.md
alembic_head_at_start: 20260728_49

2026-07-28 PHASE17 PR C 已合并到 main，PHASE18 依赖满足并启动一次性 startup audit。Frozen Gap List 已冻结 P18-T01 至 P18-T08；当前仅表示 PHASE18 in_progress，不表示 completed、quality proven 或 production ready。

## Minimal Read Set

- `docs/modules/03-knowledge-agentic-graphrag.md`
- PHASE12 Knowledge Version/Standard RAG
- PHASE17 Agent Core Control/Replan
- PHASE06 Trace
- PHASE07 Model Gateway roles
- 当前 GraphRAG extractor/router/planner/orchestrator

## Current Anchors

```text
src/backend/zuno/knowledge/**
GraphRAGExtractorConfig
AgenticRetrievalRouter
RetrievalPlanner / RetrievalOrchestrator
EvidenceBundle / CitationBuilder
Graph indexes/entity/relation/community code
```

## Allowed Paths

```text
src/backend/zuno/knowledge/retrieval/**
src/backend/zuno/knowledge/graph/**
src/backend/zuno/knowledge/evidence/**
src/backend/zuno/knowledge/application/**
src/backend/zuno/platform/database/knowledge/**
alembic/**
tests/knowledge/agentic/**
tests/integration/knowledge/agentic/**
tests/fault/knowledge/agentic/**
docs/evidence/**
```

## Forbidden Paths

- Knowledge 直接激活 PlanVersion、Ask User、External Tool、Final Answer。
- Corrective Retrieval 经过 Agent Replan Barrier。
- 每次请求无条件跑所有 Retriever/Profile。
- Graph path 无 SourceSpan grounding 进入 strict evidence。

## Work Packages

### P18-T01 EvidenceRequirement and Profile Selection
- Goal：将 Agent Core EvidenceRequirement、scope、budget、risk、profile ceiling 解析为 KnowledgeQueryRequest。
- Tests：simple/no-retrieval、multi-hop、global、conflict、restricted scope、budget ceiling。
- Acceptance：Profile 自适应，不默认 Agentic。

### P18-T02 Fixed KnowledgeRetrievalGraph and Round Domain
- Goal：实现 validate→pin snapshot→scope→interpret→select profile→plan round→admit→dispatch→normalize→fuse→ledger→evaluate→decide。
- Tests：state schema、round immutability、restart、deadline、cancel、invalid snapshot。
- Acceptance：RetrievalRound 不修改 Agent PlanVersion。
- 2026-07-28 progress：固定 `KnowledgeRetrievalGraph` trace、内部 profile、`KnowledgeControlProposal` 和 `KnowledgeStepExecutor` observation metadata 已实现第一版；验证见 `docs/evidence/goal04-phase18-knowledge-retrieval-graph-contract.md`。PHASE18 仍为 in_progress。
- 2026-07-28 progress：`RetrievalPlan` / `RetrieverDispatchPlan` 已接入 `plan_round/admit/dispatch` trace，预算耗尽时阻断 dispatch 并输出 proposal；验证见同一 evidence 文件。

### P18-T03 Graph Entity/Relation/Path/Community Runtime
- Goal：实现 entity resolution、relation/path traversal、local/global/community summary、source grounding。
- Tests：entity miss、ambiguous entity、path cutoff、community stale、snapshot mismatch、source mapping loss。
- Acceptance：Graph candidate 必须能回到 Document/TextUnit/SourceSpan。

### P18-T04 DRIFT and Multi-retriever Dispatch
- Goal：实现 follow-up branch、parallel retriever batch、budget/branch cap、partial failure。
- Tests：branch explosion、low yield、retriever timeout、duplicate candidate、late result。
- Acceptance：使用 Knowledge 内部 dispatch，不混用 Agent Plan DAG 事实。
- 2026-07-28 progress：Deep profile 已产生 BM25/Vector/Entity/Relation/Path/Community retriever dispatch plan，并记录 budget、timeout 和 parallel group；实际 retriever partial failure / late result 仍待实现。
- 2026-07-28 progress：`RetrieverAttemptResult` 已记录 required retriever timeout / index unavailable、budget exhausted 和 optional graph late-result fencing；BM25/Vector 失败阻断 normalize，optional graph late result 不进入 EvidenceLedger。branch explosion、duplicate candidate 和真实 partial failure adapter 仍待实现。

### P18-T05 Fusion, Rerank and Rank Lineage
- Goal：记录 raw/fused/reranked rank、score normalization、dropped reason、gold evidence loss。
- Tests：fusion drops gold、reranker demotes gold、score scale mismatch、deterministic tie-break。
- Acceptance：每个 accepted/rejected Evidence 有 lineage。

### P18-T06 EvidenceLedger, Frontier and Quality Verdict
- Goal：累计 coverage、authority、temporal、conflict、citation availability、novel evidence yield 和 stopping criteria。
- Tests：insufficient coverage、conflict unresolved、no new evidence、budget exhausted、strict citation missing。
- Acceptance：Verdict 是 Knowledge 事实，不是 Agent ControlDecision。
- 2026-07-28 progress：Durable port 已使用稳定 QueryRun/Round id 与 `strict_evidence_ids` 进行 idempotent replay，重复请求不会重复写 strict evidence，并在 trace 中输出 `idempotent_replay`；Frontier/coverage/conflict 聚合仍待补齐。
- 2026-07-28 progress：`EvidenceFrontier` / `EvidenceCoverageSummary` 已计算 claim coverage、strict citation coverage、authority、temporal versions、conflict groups、missing strict citation 和 stop reasons，并进入 `evidence_ledger`、`evaluate` 与 proposal trace。

### P18-T07 Corrective Retrieval Decision
- Goal：根据 failure bucket 选择 rewrite、parent expansion、alternate retriever、graph expansion、snapshot/index recovery、新 RetrievalRound 或 stop。
- Tests：query rewrite loop cap、index unavailable、repeated no-yield、conflict targeted retrieval、deadline。
- Acceptance：Retry/Corrective Retrieval 不创建 Agent PlanVersion。

### P18-T08 KnowledgeControlProposal and Agent Integration
- Goal：当内层无法解决时输出 ASK_USER/EXTERNAL_SEARCH/REPLAN_REQUIRED/ABSTAIN Proposal，由 Agent Core 验证决策。
- Tests：proposal schema、security refs、Agent accept/reject、Replan Barrier、no direct plan mutation。
- Acceptance：旧 GraphRAG query/orchestrator 切流；无 `legacy_graphrag` 包，临时 adapter PHASE22 删除。
- 2026-07-28 progress：`KnowledgeStepExecutor` 已增加 deterministic proposal gate，接受 `accept_evidence`，拒绝 `abstain` 等未解决 proposal 并转为 blocked observation；验证见 `docs/evidence/goal04-phase18-knowledge-retrieval-graph-contract.md`。旧 GraphRAG 默认路径切流尚未完成。

## Phase 完成定义

- KnowledgeRetrievalGraph/Round/Profile/Graph/Fusion/Ledger/Corrective Retrieval 可运行。
- Agent Core 与 Knowledge 两层控制清晰。
- Multi-hop/global/conflict/no-answer/blocked Fault/Integration Test 通过。
- 尚未声明相对 Baseline 质量提升，等待 PHASE20/22。

## Validation

```bash
git diff --check
pytest -q tests/knowledge/agentic tests/integration/knowledge/agentic tests/fault/knowledge/agentic -p no:cacheprovider
python tools/scripts/verify_architecture_semantic_alignment.py
```
