# LangGraph Orchestration

## Purpose

Define current and target graph orchestration.

## Current Evidence

- `src/backend/zuno/core/graphs/domain_qa_graph.py` uses `StateGraph` and
  `DomainQAState`.
- Current nodes include load config, resolve domain pack, route intent, rewrite,
  plan retrieval, retrieve evidence, fuse evidence, verify evidence,
  retry/fallback, generate answer, citation check, and finalize.
- `src/backend/zuno/core/graphs/multi_agent_supervisor_graph.py` uses
  `StateGraph`, plans `domain_qa_specialist` and
  `citation_verifier_specialist`, then finalizes.

## Target GraphRAGQAGraph

Target nodes:

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

## Target Responsibilities

LangGraph owns orchestration, state transitions, fallback, specialist handoff,
and trace assembly. It does not own provider clients, SQL, graph-store queries,
or frontend product state.

## Future Multi-Agent Supervisor

```text
Supervisor Agent
  -> Knowledge QA Agent
  -> Contract Review Agent
  -> Tool Execution Agent
  -> Java Business Agent / Business Service Proxy
  -> Report Agent
  -> Critic / Citation Check Agent
```

This is a future extension. Normal knowledge QA should continue to use a single
graph pipeline unless the task complexity justifies multi-agent cost.

## Migration Notes

`DomainQAGraph` is current evidence. `GraphRAGQAGraph` is the target name and
boundary. `agentchat` and legacy compatibility surfaces are not future mainline.
