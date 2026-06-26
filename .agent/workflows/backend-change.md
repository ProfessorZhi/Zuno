# Backend Change Workflow

## Trigger

Use for changes under `src/backend/zuno`.

## Required Reading

- `.agent/references/code-map.md`
- `.agent/references/runtime-call-chain.md`
- relevant architecture files under `.agent/architecture/near-term/`

## Rules

- Routes do not carry business or retrieval strategy.
- Application services own use cases.
- Core/runtime does not depend backward on the API layer.
- Public contract changes must sync DTOs, frontend types, and tests.
- Retrieval, Agent, Memory, and GraphRAG changes require `code-map.md`,
  `runtime-call-chain.md`, and the matching canonical architecture notes.

## Verification

Run targeted tests first, then broader tests as risk requires.
