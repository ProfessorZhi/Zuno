# Near-Term Architecture

## Purpose

This directory is the canonical detailed target architecture for Zuno's next
refactor stages. It is Target / Proposed design, not Current Truth.

The old fragmented 01-19 notes have been archived under
`docs/architecture/history/near-term-architecture-fragments/`.

## Canonical Files

```text
.agent/architecture/near-term/
  README.md
  zuno-ideal-architecture-and-repo-layout.html
  01-target-runtime-architecture.md
  02-context-memory-architecture.md
  03-capability-tool-retrieval-architecture.md
  04-knowledge-graphrag-retrieval-fusion.md
  05-repository-boundaries-and-acceptance-gates.md
```

## Reading Order

1. [Target / Proposed Visual Blueprint](zuno-ideal-architecture-and-repo-layout.html)
2. [Target Runtime Architecture](01-target-runtime-architecture.md)
3. [Context Memory Architecture](02-context-memory-architecture.md)
4. [Capability Tool Retrieval Architecture](03-capability-tool-retrieval-architecture.md)
5. [Knowledge GraphRAG Retrieval Fusion](04-knowledge-graphrag-retrieval-fusion.md)
6. [Repository Boundaries And Acceptance Gates](05-repository-boundaries-and-acceptance-gates.md)

## Boundary

Near-term means the next plausible architecture inside the current
Python/FastAPI and LangGraph monorepo. It does not mean Java implementation,
microservice extraction, event bus rollout, or default multi-agent behavior.

The HTML blueprint is the only canonical Target / Proposed visual blueprint.
It must not be copied into `docs/` and must not be used as Current evidence.
