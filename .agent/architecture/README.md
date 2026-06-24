# Zuno Architecture Design Library

This directory is the Agent-side architecture design library for Zuno. It is not
the formal documentation truth; formal conclusions still live in
`docs/architecture/`.

## Structure

```text
.agent/architecture/
  README.md
  00-architecture-index.md
  near-term/
  future/
  decisions/
  glossary.md
```

## near-term/

`near-term/` is the detailed near-term ideal architecture. It is the main design
reference for the next real refactor stage.

Near-term can describe target behavior that is not implemented yet, but it must
stay clear that:

- target is not current
- Current Evidence is code/docs evidence that exists now
- Target Design is the next-stage Python AI Runtime architecture
- Migration Notes describe how to get there
- Acceptance Direction describes what would prove the stage later

Near-term focuses on:

- FastAPI API Layer
- Application Service Layer
- LangGraph Orchestration
- LangChain / LLM / Tool Adapter boundary
- Context / State / Memory
- Persistence / Database / Storage
- Retrieval / RAG
- GraphRAG Project
- Enhanced Mode Pipeline
- Frontend API Contract
- Observability / Evaluation / Trace
- Near-term migration and acceptance gates

## future/

`future/` is horizon planning. It protects the near-term architecture from
blocking future options, but it is not the next refactor acceptance target.

Future includes Java business services, microservices, event-driven workflows,
independent workers, and multi-agent mode. These are direction-setting notes,
not current implementation requirements.

## decisions/

`decisions/` records locked near-term choices, split open questions, and retired
surfaces. It is the first place to check when a future idea threatens to pull the
near-term mainline off course.

## Related Sources

- `docs/architecture/`: formal human documentation truth.
- `.agent/references/current_architecture/`: current reality quick snapshot.
- `AGENTS.md`: repository workflow contract.

When doing code refactor work, read formal docs first, then
`.agent/architecture/near-term/`. Read `future/` only when the task is explicitly
about Java, microservices, event/workers, or multi-agent direction.
