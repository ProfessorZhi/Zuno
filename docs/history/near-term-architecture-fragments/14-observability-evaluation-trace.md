# Observability Evaluation Trace

## Purpose

Define near-term trace and evaluation expectations.

## Current Evidence

- `TraceIDMiddleware` exists in `src/backend/zuno/middleware/`.
- The retired `DomainQAGraph` source collected trace and cost metadata.
  Historical `MultiAgentSupervisorGraph` work also collected this shape, but
  both direct sources have retired from current backend.
- `RetrievalOrchestrator` emits metadata for retrievers, routing, fallback,
  requery, graph, community, drift-like paths, index version, and index health.
- Evaluation tooling exists under `tools/evals/zuno/`.

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
```

Future fields like service calls and agent steps belong in `../future/` until
they become an explicit near-term implementation target.

## Evaluation Metrics

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

Keep raw internal diagnostics during migration, but public trace should use
query method names: `basic`, `local`, `global`, `drift`, and `auto`.

## Acceptance Direction

Every Enhanced Mode query should explain why it chose or abandoned graph,
community, requery, and rerank paths.
