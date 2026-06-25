# Near-Term Architecture

## Purpose

This directory describes Zuno's near-term ideal architecture: detailed enough to
drive the next refactor stage, but still honest that it is target design rather
than current implementation truth.

## Scope

Near-term means the next plausible refactor inside the current Python/FastAPI
and LangGraph monorepo. It does not mean Java implementation, service
extraction, event bus rollout, or default multi-agent behavior.

## Reading Order

1. [Near-Term Target Overview](01-near-term-target-overview.md)
2. [System Context](02-system-context.md)
3. [Container And Component View](03-container-and-component-view.md)
4. [Layered Architecture](04-layered-architecture.md)
5. [Backend FastAPI Service Layer](05-backend-fastapi-service-layer.md)
6. [LangGraph Orchestration](06-langgraph-orchestration.md)
7. [LangChain LLM Tool Adapters](07-langchain-llm-tool-adapters.md)
8. [Context State Memory](08-context-state-memory.md)
9. [Persistence Database Storage](09-persistence-database-storage.md)
10. [Retrieval RAG Architecture](10-retrieval-rag-architecture.md)
11. [GraphRAG Project Architecture](11-graphrag-project-architecture.md)
12. [Enhanced Mode Pipeline](12-enhanced-mode-pipeline.md)
13. [Frontend API Contract](13-frontend-api-contract.md)
14. [Observability Evaluation Trace](14-observability-evaluation-trace.md)
15. [Near-Term Migration Roadmap](15-near-term-migration-roadmap.md)
16. [Near-Term Acceptance Gates](16-near-term-acceptance-gates.md)
17. [Implementation Phase Map](17-implementation-phase-map.md)
18. [Context Memory Ideal Architecture](18-context-memory-ideal-architecture.md)

## Standard Sections

Near-term documents should use these sections where they help:

```text
Purpose
Current Evidence
Target Design
Responsibilities
Non-Responsibilities
Migration Notes
Acceptance Direction
```
