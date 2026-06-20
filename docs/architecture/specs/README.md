# Architecture Specs

This directory keeps the stable architecture definitions that should outlive any one execution phase.

## Read These First

1. [Architecture Upgrade Design](architecture-upgrade-2026-06.md)
2. [Layered Backend And Service Evolution](layered-backend-and-service-evolution.md)
3. [Domain Pack + LangGraph + GraphRAG Architecture](domain-pack-langgraph-graphrag-architecture.md)
4. [LangGraph Runtime](langgraph-runtime.md)
5. [Retrieval Orchestrator](retrieval-orchestrator.md)
6. [Enterprise Retrieval Governance](enterprise-retrieval-governance.md)
7. [RAG Evaluation And Observability](rag-evaluation-and-observability.md)
8. [Platform Evolution And Future Direction](platform-evolution-and-future-direction.md)
9. [Knowledge Product Boundary](knowledge-product-boundary.md)
10. [Deep GraphRAG V1 Runtime](deep-graphrag-v1-runtime.md)
11. [Enhanced Retrieval Orchestrator Contract](enhanced-retrieval-orchestrator-contract.md)
12. [Domain Pack Builder](domain-pack-builder.md)
13. [Knowledge Config Impact And Reindex](knowledge-config-impact-and-reindex.md)

## What Belongs Here

A spec belongs here only if it defines one of these:

- repo or service boundaries
- runtime workflow contracts
- Domain Pack / GraphRAG architecture
- retrieval governance
- evaluation and proof surfaces
- long-lived evolution constraints

## What Does Not Belong Here

- one-off checklists
- readiness notes
- phase-temperature status notes
- historical completion narratives

Those belong in either:

- `../phases/`
- `../history/`
- `../../development/`
