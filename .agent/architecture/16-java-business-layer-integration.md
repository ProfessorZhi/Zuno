# Java Business Layer Integration

## Purpose

Define future Java business service integration.

## Current Evidence

There is no Java backend service in this repo today. The current backend truth
is `src/backend/zuno`.

## Target Positioning

```text
Python FastAPI / LangGraph Runtime
  responsible for AI, RAG, GraphRAG, LLM, Agent orchestration.

Java Business Services
  responsible for strict business rules, transactions, permissions,
  enterprise workflows, complex business objects, and audit consistency.
```

## Target Interfaces

```text
BusinessServiceClient
BusinessToolAdapter
BusinessContext
BusinessCommand
BusinessEvent
```

## Integration Rules

- Java services are not a replacement for the Python AI runtime.
- Python calls Java through HTTP, gRPC, or a message bus.
- Java exposes business capability APIs.
- LangGraph uses a Tool or Service Adapter to call Java.
- Java is the business truth for consistency and audit.
- AI can suggest, explain, report, and assist automation, but it must not bypass
  Java-owned business rules.

## Required Cross-Cutting Fields

```text
auth propagation
tenant / user context
trace id propagation
idempotency key
audit log
timeout / retry / circuit breaker
```
