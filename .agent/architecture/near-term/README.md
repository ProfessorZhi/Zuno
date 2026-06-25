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

1. [Target / Proposed Visual Blueprint](zuno-ideal-architecture-and-repo-layout.html)
2. [Near-Term Target Overview](01-near-term-target-overview.md)
3. [System Context](02-system-context.md)
4. [Container And Component View](03-container-and-component-view.md)
5. [Layered Architecture](04-layered-architecture.md)
6. [Backend FastAPI Service Layer](05-backend-fastapi-service-layer.md)
7. [LangGraph Orchestration](06-langgraph-orchestration.md)
8. [LangChain LLM Tool Adapters](07-langchain-llm-tool-adapters.md)
9. [Context State Memory](08-context-state-memory.md)
10. [Persistence Database Storage](09-persistence-database-storage.md)
11. [Retrieval RAG Architecture](10-retrieval-rag-architecture.md)
12. [GraphRAG Project Architecture](11-graphrag-project-architecture.md)
13. [Enhanced Mode Pipeline](12-enhanced-mode-pipeline.md)
14. [Frontend API Contract](13-frontend-api-contract.md)
15. [Observability Evaluation Trace](14-observability-evaluation-trace.md)
16. [Near-Term Migration Roadmap](15-near-term-migration-roadmap.md)
17. [Near-Term Acceptance Gates](16-near-term-acceptance-gates.md)
18. [Implementation Phase Map](17-implementation-phase-map.md)
19. [Context Memory Ideal Architecture](18-context-memory-ideal-architecture.md)
20. [Repository Layout And Module Boundaries](19-repository-layout-and-module-boundaries.md)

The HTML blueprint is a Target / Proposed visual reference for maintainers and
Agents. It is not Current Truth and must not be copied into `docs/`.

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
