# PHASE18 Agentic GraphRAG Inner Loop

phase_id: PHASE18
status: planned
depends_on: PHASE12, PHASE17
owner: Module 03 Knowledge / Agentic GraphRAG

## Phase 目标

实现固定 KnowledgeRetrievalGraph 与动态 RetrievalPlan/Round，支持 Standard/Local/Global/DRIFT/Deep/Agentic Profile、BM25/Vector/Entity/Relation/Path/Community Retriever、Fusion/Rerank、EvidenceLedger/Frontier、Quality Verdict、Corrective Retrieval 和 KnowledgeControlProposal。内层纠正不得直接修改 Agent Plan。

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

### P18-T03 Graph Entity/Relation/Path/Community Runtime
- Goal：实现 entity resolution、relation/path traversal、local/global/community summary、source grounding。
- Tests：entity miss、ambiguous entity、path cutoff、community stale、snapshot mismatch、source mapping loss。
- Acceptance：Graph candidate 必须能回到 Document/TextUnit/SourceSpan。

### P18-T04 DRIFT and Multi-retriever Dispatch
- Goal：实现 follow-up branch、parallel retriever batch、budget/branch cap、partial failure。
- Tests：branch explosion、low yield、retriever timeout、duplicate candidate、late result。
- Acceptance：使用 Knowledge 内部 dispatch，不混用 Agent Plan DAG 事实。

### P18-T05 Fusion, Rerank and Rank Lineage
- Goal：记录 raw/fused/reranked rank、score normalization、dropped reason、gold evidence loss。
- Tests：fusion drops gold、reranker demotes gold、score scale mismatch、deterministic tie-break。
- Acceptance：每个 accepted/rejected Evidence 有 lineage。

### P18-T06 EvidenceLedger, Frontier and Quality Verdict
- Goal：累计 coverage、authority、temporal、conflict、citation availability、novel evidence yield 和 stopping criteria。
- Tests：insufficient coverage、conflict unresolved、no new evidence、budget exhausted、strict citation missing。
- Acceptance：Verdict 是 Knowledge 事实，不是 Agent ControlDecision。

### P18-T07 Corrective Retrieval Decision
- Goal：根据 failure bucket 选择 rewrite、parent expansion、alternate retriever、graph expansion、snapshot/index recovery、新 RetrievalRound 或 stop。
- Tests：query rewrite loop cap、index unavailable、repeated no-yield、conflict targeted retrieval、deadline。
- Acceptance：Retry/Corrective Retrieval 不创建 Agent PlanVersion。

### P18-T08 KnowledgeControlProposal and Agent Integration
- Goal：当内层无法解决时输出 ASK_USER/EXTERNAL_SEARCH/REPLAN_REQUIRED/ABSTAIN Proposal，由 Agent Core 验证决策。
- Tests：proposal schema、security refs、Agent accept/reject、Replan Barrier、no direct plan mutation。
- Acceptance：旧 GraphRAG query/orchestrator 切流；无 `legacy_graphrag` 包，临时 adapter PHASE22 删除。

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
