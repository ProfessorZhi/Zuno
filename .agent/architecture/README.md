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

`near-term/` is the canonical detailed target architecture. It contains one
HTML visual blueprint and five Markdown documents:

- target runtime architecture
- context and memory architecture
- capability and tool retrieval architecture
- knowledge, GraphRAG, retrieval, and fusion architecture
- repository boundaries and acceptance gates

## future/

`future/` is a slim horizon summary. It protects the near-term architecture
from blocking future options, but it is not the next refactor acceptance target.

## decisions/

`decisions/` records a concise Agent-side decision summary. Formal ADRs remain
under `docs/architecture/decisions/`.

## Related Sources

- `docs/architecture/`: formal human documentation truth.
- `.agent/references/`: slim Agent navigation indexes.
- `AGENTS.md`: repository workflow contract.

When doing code refactor work, read formal docs first, then
`.agent/architecture/near-term/`. Read `future/` only when the task is explicitly
about Java, microservices, event/workers, or multi-agent direction.
