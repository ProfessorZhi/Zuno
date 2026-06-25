# Zuno Backend Agent Rules

Before changing `src/backend/zuno`, read:

1. `.agent/references/backend-map.md`
2. `.agent/references/runtime-call-chain.md`
3. `.agent/workflows/backend-change.md`

For backend architecture replacement, GraphRAG boundary, Context/Memory, or
package layout work, also read
`.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`.

Rules:

- Routes do not own business logic or retrieval strategy.
- Application services own use cases.
- Core and runtime code must not depend backward on the API layer.
- Public contract changes must sync DTOs, frontend types, and tests.
- Retrieval, Agent, Memory, and GraphRAG changes require the corresponding
  references and architecture notes.
