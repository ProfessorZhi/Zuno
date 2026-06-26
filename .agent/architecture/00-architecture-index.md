# Architecture Index

## Default Reading Order

1. [README](README.md)
2. [Near-Term README](near-term/README.md)
3. [Target Runtime Architecture](near-term/01-target-runtime-architecture.md)
4. [Context Memory Architecture](near-term/02-context-memory-architecture.md)
5. [Capability Tool Retrieval Architecture](near-term/03-capability-tool-retrieval-architecture.md)
6. [Knowledge GraphRAG Retrieval Fusion](near-term/04-knowledge-graphrag-retrieval-fusion.md)
7. [Repository Boundaries And Acceptance Gates](near-term/05-repository-boundaries-and-acceptance-gates.md)
8. [Architecture Decisions](decisions/architecture-decisions.md)
9. [Future Horizon](future/future-horizon.md)

## Rule For Refactor Work

For near-term code refactor work, read `near-term/` first after the formal docs.
The target mainline is Single GeneralAgent + Context/Memory + Capability/Tool
Retrieval + Knowledge/GraphRAG + Retrieval/Fusion/Evidence + Trace/Eval.

Read `future/` only when discussing Java business services, microservices,
event-driven workers, independent GraphRAG/evaluation services, or multi-agent
direction. Those topics must not become near-term acceptance gates unless the
user explicitly opens a new future-direction implementation program.

`docs/architecture/` remains the formal documentation truth. `.agent/architecture/`
is the detailed Agent-side target design library.
