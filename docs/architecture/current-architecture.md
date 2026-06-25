# Current Architecture

## Purpose

This file states current repository reality. It does not describe the desired
future state.

## Current

Zuno is a monorepo with these active runtime boundaries:

```text
apps/web
apps/desktop
src/backend/zuno
infra
tools
tests
```

`src/backend/zuno` is the only active Python backend runtime boundary. There is
no active root-level `services/` backend tree and no active `src/frontend`
workspace.

## Current Backend Shape

- FastAPI entrypoint: `src/backend/zuno/main.py`
- API layer: `src/backend/zuno/api/`
- Runtime/core layer: `src/backend/zuno/core/`
- Service layer: `src/backend/zuno/services/`
- Persistence and settings: `src/backend/zuno/database/`,
  `src/backend/zuno/settings.py`
- Eval and maintenance tooling: `tools/evals/zuno/`, `tools/scripts/`

## Current GraphRAG And Agent State

Current code and focused tests prove this mainline:

```text
Completion API
  -> CompletionService
  -> GeneralAgent single loop
  -> search_knowledge_base
  -> KnowledgeQueryService
  -> GraphRAGQueryService
  -> RetrievalPlanner / RetrievalOrchestrator
  -> Evidence / Citation / Trace
  -> GeneralAgent answer
```

Phase 11A is complete. The current code contains `KnowledgeQueryService`,
`GraphRAGQueryService`, `GraphRAGProjectSnapshot`, and `KnowledgeQueryResult`.
This is the current GraphRAG Project Query Runtime boundary.

Phase 11B is complete. `GeneralAgent.astream()` uses the single current session
path, `search_knowledge_base` calls `KnowledgeQueryService`, and
`DomainQAGraph` no longer owns the `GeneralAgent` conversation path.

The old `AgentConfig` public shape still exists, including migration fields
such as `domain_pack_id`; that is current compatibility surface, not target
architecture.

## Blocked Legacy

Phase 11C is blocked because these active dependencies still exist:

- `domain-packs/`
- Domain Pack service/eval/Docker surfaces
- `src/backend/zuno/api/v1/domain_packs.py` as a retained legacy endpoint
  module, not mounted on the current FastAPI router
- `apps/web/src/apis/domain-packs.ts` and Domain Pack Vue components as
  retained legacy assets, not active knowledge routes or settings-shell pages
- `src/backend/zuno/api/services/domain_pack.py`
- `src/backend/zuno/services/domain_pack/`
- `src/backend/zuno/core/runtime/agent_runtime.py`
- remaining `DomainQAGraph` source and dependencies
- remaining `MultiAgentSupervisorGraph` source and compat surfaces
- `tests/compat/`

These surfaces are not the future front-path architecture, but they still have
active imports, evals, assets, runtime paths, Docker references, or tests. They
are retained until 11C active dependency removal is proved.

## Not Current

Context Orchestrator and new Memory layering are Target, not Current.

The near-term Context & Memory design is documented under `.agent/`; it is not
implemented as the current runtime. Do not describe short/medium/long memory,
Context Orchestrator, Dynamic Capability Selector, or the Post-turn Pipeline as
current behavior until code and tests prove them.

Phase 12 is partial / not closed. The repository has focused tests for recent
changes, but final full `pytest` and formal Eval baseline comparison have not
been completed.

## Historical Completion Truth

Phase 0-6 is complete and historical. Do not rewrite those phase files as
incomplete to carry new work.

## Documentation Boundary

`docs/` is formal documentation. `.agent/` is the Agent workflow library.
Historical materials live under `docs/architecture/history/`.
