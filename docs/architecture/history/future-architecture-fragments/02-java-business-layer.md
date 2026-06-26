# Java Business Layer

## Future Direction

Java may become the business truth layer for enterprise workflows.

## Why It May Matter

Java services can own:

- strict business rules
- transactions
- permissions
- enterprise workflow state
- complex business objects
- audit consistency

Python remains the AI Runtime for LLM, RAG, GraphRAG, tools, and answer
generation.

## Possible Shape

```text
Python AI Runtime
  -> BusinessServiceClient / BusinessToolAdapter
  -> Java Business Capability API
  -> business validation, transaction, audit
  -> Python explanation/report/assistant response
```

## Readiness Conditions

- stable Python service boundary
- clear business capability API
- auth and tenant context propagation
- trace id propagation
- idempotency and timeout policy
- audit ownership defined

## Risks

- AI bypassing business truth
- duplicated permission logic
- inconsistent transaction ownership
- over-designing Java before business workflows exist

## Do Not Do Yet

Do not implement Java services in the near-term architecture program. Near-term
work only preserves adapter and context boundaries.
