# Microservices Roadmap

## Purpose

Show future microservice candidates without forcing a split now.

## Current Evidence

The current target docs say monorepo now, service-ready later. Current runtime
truth is `src/backend/zuno`.

## Candidate Services

```text
zuno-api-gateway
zuno-ai-runtime
zuno-knowledge-service
zuno-indexing-worker
zuno-graphrag-service
zuno-tool-service
zuno-business-java-service
zuno-eval-service
zuno-observability
```

## When To Split

Split only when at least one condition is true:

- independent scaling is required
- failure isolation is required
- data ownership is clear
- deployment cadence differs
- team ownership differs
- queue-based job runtime becomes necessary

## Risks

- distributed tracing debt
- cross-service transaction confusion
- duplicated authorization
- slower local development
- premature API freeze
- service ownership without data ownership

## Migration Notes

Keep a modular monolith first. Stabilize interfaces, DTOs, trace fields,
version fields, and job boundaries before extracting services.
