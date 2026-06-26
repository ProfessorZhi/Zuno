# Code Map

## Purpose

Orient Agents to current code owners without copying target architecture design
or authorizing code edits.

## Main Surfaces

- `apps/web/`: Vue web workspace.
- `apps/desktop/`: Electron desktop shell.
- `src/backend/zuno/`: current Python backend runtime truth.
- `src/backend/zuno/api/`: HTTP routes, DTOs, auth, response envelopes, SSE.
- `src/backend/zuno/services/application/`: application use-case boundaries.
- `src/backend/zuno/core/`: single GeneralAgent runtime and orchestration.
- `src/backend/zuno/services/graphrag/`: GraphRAG Project query/index concepts.
- `src/backend/zuno/services/retrieval/`: retrieval planning and retriever adapters.
- `src/backend/zuno/services/memory/`: memory foundation.
- `src/backend/zuno/database/`: persistence models and database wiring.
- `tools/`: scripts, launchers, evals, and maintenance tooling.
- `tests/`: repo-level verification and focused regression tests.
- `docs/`: formal human-facing documentation.
- `.agent/`: Agent workflow library and target-design workspace.

## Current Runtime Path

```text
Completion API
  -> CompletionService
  -> GeneralAgent single loop
  -> prepare_context
  -> ContextOrchestrator.prepare
  -> search_knowledge_base
  -> KnowledgeQueryService
  -> GraphRAGQueryService
  -> RetrievalPlanner / RetrievalOrchestrator
  -> Evidence / Citation / Trace
  -> post_turn_commit
```

## Task Routing

- Backend changes: read `src/backend/zuno/AGENTS.md`.
- Frontend changes: read `apps/web/AGENTS.md`.
- Eval changes: read `tools/evals/zuno/AGENTS.md`.
- Docs or Agent workflow changes: read `AGENTS.md`, `.agent/references/task-routing.md`, and `.agent/references/workflow.md`.

## Boundary

For documentation and workflow normalization tasks, do not modify runtime
surfaces:

- `src/backend/zuno/`
- `apps/web/`
- `apps/desktop/`
- `infra/`
- `tools/evals/zuno/`

If verification would require a forbidden runtime change, stop and return
evidence instead of expanding scope.
