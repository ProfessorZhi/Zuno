# Architecture Index

## Default Reading Order

1. [README](README.md)
2. [Near-Term README](near-term/README.md)
3. [Near-Term Target Overview](near-term/01-near-term-target-overview.md)
4. [Layered Architecture](near-term/04-layered-architecture.md)
5. [GraphRAG Project Architecture](near-term/11-graphrag-project-architecture.md)
6. [Enhanced Mode Pipeline](near-term/12-enhanced-mode-pipeline.md)
7. [Near-Term Migration Roadmap](near-term/15-near-term-migration-roadmap.md)
8. [Locked Near-Term Decisions](decisions/01-locked-near-term-decisions.md)
9. [Open Architecture Questions](decisions/02-open-architecture-questions.md)
10. [Future README](future/README.md)

## Rule For Refactor Work

For near-term code refactor work, read `near-term/` first after the formal docs.
The current mainline is Python FastAPI + Service Layer + LangGraph + LLM/Tool
Adapters + RAG/GraphRAG + Persistence + Frontend API Contract.

Read `future/` only when discussing Java business services, microservices,
event-driven workers, independent GraphRAG/evaluation services, or multi-agent
direction. Those topics must not become near-term acceptance gates unless the
user explicitly opens a new future-direction implementation program.

`docs/architecture/` remains the formal documentation truth. `.agent/architecture/`
is the detailed Agent-side design library.
