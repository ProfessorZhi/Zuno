# Microservices Roadmap

## Future Direction

Zuno may later split into services, but the current path remains modular
monolith first.

## Candidate Services

```text
zuno-api-gateway
zuno-ai-runtime
zuno-knowledge-service
zuno-graphrag-service
zuno-indexing-worker
zuno-tool-service
zuno-eval-service
zuno-observability
zuno-business-java-service
```

## Readiness Conditions

Split only when one or more are true:

- independent scaling is necessary
- failure isolation is necessary
- data ownership is stable
- deployment cadence differs
- team ownership differs
- async job volume requires a worker boundary

## Risks

- distributed tracing debt
- unclear data ownership
- duplicated auth
- slower local development
- premature API freeze
- service split without operational benefit

## Do Not Do Yet

Do not split services as part of the near-term GraphRAG cleanup/refactor. First
stabilize module contracts, DTOs, trace, versions, and tests.
