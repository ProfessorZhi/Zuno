# LangGraph Orchestration

## Purpose

Define the near-term target for AI orchestration.

## Current Evidence

- `src/backend/zuno/core/graphs/domain_qa_graph.py` is current implementation
  evidence to migrate from. It uses `StateGraph` and already has nodes for
  config loading, legacy domain pack resolution, query rewrite, retrieval
  planning, evidence retrieval, fusion, verification, retry/fallback, answer
  generation, citation check, and finalize.
- `src/backend/zuno/core/graphs/states.py` defines graph state.
- `MultiAgentSupervisorGraph` exists, but multi-agent defaulting is future
  direction, not near-term mainline.

## Target Design

The near-term graph should be named and explained as `GraphRAGQAGraph`.

Target node order:

```text
load_runtime_context
load_graphrag_project
normalize_query
route_query_method
retrieve_evidence
fuse_and_rerank
verify_evidence
conditional_requery
generate_answer
citation_check
finalize_trace
```

## State Boundaries

Graph state should carry:

- request context
- GraphRAG project context
- normalized query
- requested and resolved query method
- retrieval plan
- evidence context
- citation context
- fallback decision
- trace context
- final answer and report fields

Graph state should not carry:

- provider credentials
- raw database sessions
- frontend component state
- long-lived service clients

## Migration Notes

`DomainQAGraph` is current evidence and can be the migration source. The target
renames the concept away from Domain Pack and toward GraphRAG Project. Do not
delete current graph code until replacement tests prove equivalent behavior.

`agentchat` and legacy graph paths are retired surfaces. They may appear in
history or migration notes, not as near-term front-path architecture.

## Acceptance Direction

Later code work should prove graph node order, fallback behavior, citation
checks, and trace fields with focused tests before changing retrieval behavior.
