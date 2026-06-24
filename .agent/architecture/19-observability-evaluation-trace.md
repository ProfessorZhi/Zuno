# Observability Evaluation Trace

## Purpose

Define target trace and evaluation fields.

## Current Evidence

- `TraceIDMiddleware` exists in `src/backend/zuno/middleware/`.
- `DomainQAGraph` and `MultiAgentSupervisorGraph` collect trace and cost
  metadata.
- `RetrievalOrchestrator` emits metadata for retrievers, routing, fallback,
  requery, graph, community, drift-like paths, and index health.
- Evaluation tooling exists under `tools/evals/zuno/` and tests cover retrieval,
  multihop, GraphRAG, and docs entrypoints.

## Target Trace Fields

```text
request_id
user_id
knowledge_id
graphrag_project_id
prompt_version
index_version
query_method_requested
query_method_resolved
retrievers_used
retrieval_rounds
requery_count
fallback_reason
chunks_used
graph_paths_used
community_reports_used
citations
citation_coverage
latency
token_cost
model_used
tool_calls
java_service_calls
agent_steps
```

## Evaluation

```text
retrieval hit rate
rerank quality
citation coverage
faithfulness
graph path usefulness
community report usefulness
DRIFT usefulness
cost / latency
method comparison
regression fixtures
```

## Migration Notes

Rename trace fields from old route names to query methods at the public layer,
but keep raw internal diagnostics available during migration.
