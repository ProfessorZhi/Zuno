# Multi-Agent Architecture

## Future Direction

Multi-agent mode may be useful for complex tasks, but it is not the default
near-term QA path.

## Current Evidence

`MultiAgentSupervisorGraph` exists today and plans a domain QA specialist plus
citation verifier. That is current evidence of possibility, not proof that
ordinary QA should default to multi-agent.

## Possible Shape

```text
Supervisor Agent
  -> Query Understanding Agent
  -> Knowledge Retrieval Agent
  -> GraphRAG Reasoning Agent
  -> Contract Review Agent
  -> Tool Execution Agent
  -> Business Proxy Agent
  -> Report Writer Agent
  -> Critic / Citation Check Agent
```

## Readiness Conditions

- single-pipeline QA is stable
- evidence context is first-class
- trace context survives specialist handoff
- max step/tool/budget limits exist
- specialist input/output contracts exist
- citation checks cannot be skipped

## Risks

- higher latency and cost
- loop risk
- tool overuse
- citation loss
- harder debugging

## Do Not Do Yet

Do not make multi-agent the default for ordinary knowledge QA in the near-term
architecture. Keep it for future complex task programs.
