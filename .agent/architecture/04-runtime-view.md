# Runtime View

## Purpose

Describe target runtime flows.

## Current Evidence

- `src/backend/zuno/api/router.py` registers `/api/v1` routes.
- `src/backend/zuno/core/graphs/domain_qa_graph.py` already models load config,
  resolve domain pack, rewrite, plan, retrieve, fuse, verify, retry/fallback,
  generate answer, citation check, and finalize nodes.
- `src/backend/zuno/services/retrieval/orchestrator.py` performs query
  expansion, planning, single pass retrieval, retry, metadata, community/global,
  and drift-like paths.
- `src/backend/zuno/services/rag/handler.py` calls vector/BM25/rerank and then
  the retrieval orchestrator for metadata-rich retrieval.

## Flow 1: Normal Chat / Completion

```text
User -> Frontend -> FastAPI completion/workspace route
  -> Application service
  -> Agent runtime or simple LLM adapter
  -> tools and optional knowledge context
  -> streaming or final response
  -> trace and usage metadata
```

## Flow 2: Knowledge Standard QA

```text
User -> Frontend standard mode
  -> FastAPI knowledge/workspace route
  -> KnowledgeService runtime settings
  -> RetrievalOrchestrator basic/standard route
  -> BM25 + dense vector + fusion + rerank
  -> citations and answer
```

## Flow 3: Enhanced QA

```text
User -> Frontend enhanced mode
  -> FastAPI route
  -> service resolves GraphRAG project/index state
  -> auto query method router
  -> basic/local/global/drift retrieval path
  -> fusion/RRF, rerank, evidence check, conditional requery
  -> citation answer and trace
```

## Flow 4: GraphRAG Indexing

```text
File upload or reindex action
  -> KnowledgeService impact analysis
  -> parse/chunk
  -> vector and BM25 index update
  -> graph extraction
  -> graph store write
  -> community detection/report build when needed
  -> index_version/community_version update
```

## Flow 5: Prompt Tuning + Re-Index

```text
GraphRAG project data sample
  -> prompt tuning service
  -> prompt registry writes prompt_version
  -> settings validator decides re-index need
  -> full re-index for extraction/entity/chunking changes
  -> query prompt updates without graph rebuild when schema unchanged
```

## Flow 6: Multi-Agent Future

```text
Complex task -> Supervisor Agent
  -> plan specialist agents
  -> Knowledge QA Agent / Tool Execution Agent / Report Agent
  -> Critic or Citation Check Agent
  -> final answer with evidence and trace
```

## Flow 7: Java Business Service Integration

```text
User task -> Python service
  -> LangGraph tool node or service adapter
  -> Java business capability API
  -> business validation, permission, transaction, audit
  -> Python answer/explanation/report
```

## Flow 8: Split Microservices

```text
API Gateway -> AI Runtime
  -> Knowledge Service / GraphRAG Service / Tool Service
  -> queue-backed Indexing Worker or Evaluation Worker
  -> shared observability and trace propagation
```
