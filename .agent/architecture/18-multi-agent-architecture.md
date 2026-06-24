# Multi-Agent Architecture

## Purpose

Define when and how future multi-agent mode should be used.

## Current Evidence

- `MultiAgentSupervisorGraph` currently exists and runs two specialists:
  `domain_qa_specialist` and `citation_verifier_specialist`.
- Tests reference multi-agent supervisor runtime paths.

## Target Agents

```text
Supervisor Agent
  -> Query Understanding Agent
  -> Knowledge Retrieval Agent
  -> GraphRAG Reasoning Agent
  -> Contract Review Agent
  -> Tool Execution Agent
  -> Java Business Proxy Agent
  -> Report Writer Agent
  -> Critic / Citation Check Agent
```

## Target Rules

- Multi-agent is not the default for ordinary QA.
- Use multi-agent only when the task needs decomposition, tools, business
  service calls, reports, or critique.
- Supervisor owns plan, route, budget, stop condition, and trace assembly.
- Each agent must have input and output contracts.
- Agents share Evidence Context and Trace Context.
- Prevent infinite loops with max steps, max tool calls, and budget limits.
- Prevent citation loss by making evidence bundles first-class.

## Future Extension

The Java Business Proxy Agent should call Java business capability APIs through
the same business service adapter used by non-agent flows.
