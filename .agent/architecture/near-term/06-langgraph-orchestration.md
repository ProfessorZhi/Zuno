# LangGraph Orchestration

## Purpose

Define the near-term target for AI orchestration.

## Current Evidence

- The current conversation mainline is the single `GeneralAgent` loop calling
  `KnowledgeQueryService` and `GraphRAGQueryService`.
- `src/backend/zuno/core/graphs/domain_qa_graph.py` and its legacy
  `states.py` module are retired from current backend source.
- Historical `DomainQAGraph` and `MultiAgentSupervisorGraph` work can inform
  migration notes, but they are not current implementation surfaces.
- Multi-agent defaulting is future direction, not near-term mainline.

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

Historical `DomainQAGraph` evidence has been replaced on the current mainline
by `KnowledgeQueryService`, `GraphRAGQueryService`, and focused retirement
tests. Any future graph extraction should be implemented around GraphRAG
Project contracts, not by restoring the old Domain Pack graph.

`agentchat` and legacy graph paths are retired surfaces. They may appear in
history or migration notes, not as near-term front-path architecture.

## Acceptance Direction

Later code work should prove graph node order, fallback behavior, citation
checks, and trace fields with focused tests before changing retrieval behavior.
