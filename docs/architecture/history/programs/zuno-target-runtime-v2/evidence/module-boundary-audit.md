# Module Boundary Audit

## Status

Phase 02 audit for `zuno-target-runtime-v2`.

## Current Backend Directory Overview

Current runtime boundary remains `src/backend/zuno/`.

Important current packages:

- `api/`: FastAPI router, `api/v1` route modules, and legacy API-facing service
  adapters.
- `core/`: Agent runtime, callbacks, model manager, and graph/runtime surfaces.
- `services/application/`: current application foundation contracts and thin
  compatibility facades.
- `services/application/context/`: current typed context contracts.
- `services/application/capabilities/`: current capability metadata and minimal
  selector contracts.
- `services/graphrag/`: GraphRAG Project query, project loading, prompt,
  versioning, graph, community, and retriever components.
- `services/retrieval/`: retrieval planner, fusion, orchestrator, and retriever
  abstractions.
- `services/rag/`: parser, vector store, embedding, rerank, and legacy RAG
  handler surfaces.
- `database/` and `schema/`: persistence models/DAO and public DTOs.

## Target Directory Overview

The near-term target remains a Python modular monolith:

```text
api -> application services -> agent/runtime -> capability / knowledge / retrieval / persistence
```

The target does not require an immediate full package split. The first
migration slice should move one proven use-case owner at a time.

## First Low-Risk Candidate

### Move KnowledgeQueryService

```text
src/backend/zuno/api/services/knowledge_query.py
-> src/backend/zuno/services/application/knowledge/query_service.py
```

Reason:

- `KnowledgeQueryService` is a use-case/application boundary, not an HTTP
  route concern.
- `GeneralAgent`, workspace runtime, `/knowledge/search`, and focused tests
  already treat it as the mainline knowledge query service.
- The move can be validated with Phase 11A/11B and runtime-chain tests without
  changing retrieval behavior.

Deletion condition for `zuno.api.services.knowledge_query`:

- Phase 03 should update all current imports and tests to
  `zuno.services.application.knowledge.query_service`.
- Prefer deleting the old module entirely.
- If a temporary re-export is required, it must state its deletion phase and be
  guarded by `verify_module_boundaries.py`.

Phase 03 migration result:

- `KnowledgeQueryService` moved to
  `src/backend/zuno/services/application/knowledge/query_service.py`.
- The old `src/backend/zuno/api/services/knowledge_query.py` module is deleted.
- Current imports and tests use `zuno.services.application.knowledge`.

## Other Candidate Areas

### Context Contracts

Current path:

```text
src/backend/zuno/services/application/context/
```

Assessment: already an acceptable application boundary for the first slice.
Phase 04 should extend this package with `ContextOrchestrator` instead of
moving it.

### Capability Contracts

Current path:

```text
src/backend/zuno/services/application/capabilities/
```

Assessment: already an acceptable foundation boundary. Mature product-level
selection is later work, not Phase 02/03.

### GraphRAG Query Service

Current path:

```text
src/backend/zuno/services/graphrag/query_service.py
```

Possible future target:

```text
src/backend/zuno/services/graphrag/query/service.py
```

Assessment: higher risk than `KnowledgeQueryService` because many GraphRAG and
retrieval tests import the current module. Defer until after the application
knowledge boundary move is proven.

## High-Risk Files Not To Move In This Slice

- `src/backend/zuno/core/agents/general_agent.py`: may receive small import or
  Context Orchestrator call changes only.
- `src/backend/zuno/api/services/knowledge.py`: large API-facing service with
  config, persistence, and project compatibility behavior.
- `src/backend/zuno/services/rag/handler.py`: still used by legacy RAG flows.
- `src/backend/zuno/database/` and `src/backend/zuno/schema/`: no schema or DTO
  package moves in this round.
- `src/backend/zuno/services/graphrag/query_service.py`: defer structural split.

## Import Impact Summary

Former import consumers for `zuno.api.services.knowledge_query` included:

- `src/backend/zuno/core/agents/general_agent.py`
- `src/backend/zuno/api/services/knowledge.py`
- `src/backend/zuno/services/workspace/simple_agent.py`
- focused tests for Phase 11A/11B, runtime chain guards, and knowledge API
  contracts
- `tools/scripts/verify_phase0_runtime_recovery.py`

Current `api/v1` route modules do not directly import concrete retrieval,
GraphRAG, or RAG implementation modules.

Known broader debt, not Phase 03 scope:

- several non-route services still import `zuno.api.services.*` as application
  facades.
- `core/agents/general_agent.py` imports multiple API service facades. Phase 03
  should only address `KnowledgeQueryService`.

## Test Commands Per Candidate

For `KnowledgeQueryService` move:

```powershell
pytest -q tests/test_phase11a_knowledge_query_service.py tests/test_phase11b_single_generalagent_cutover.py -p no:cacheprovider
pytest -q tests/test_zuno_public_entrypoints.py tests/test_zuno_runtime_chain_guard.py -p no:cacheprovider
python .agent/scripts/verify_module_boundaries.py
python .agent/scripts/verify_agent_system.py
python tools/scripts/verify_repo_structure.py
git diff --check
```

For Context Orchestrator Phase 04:

```powershell
pytest -q tests/test_context_orchestrator.py -p no:cacheprovider
pytest -q tests/test_phase11b_single_generalagent_cutover.py -p no:cacheprovider
python .agent/scripts/verify_module_boundaries.py
python .agent/scripts/verify_agent_system.py
git diff --check
```

## Stop Conditions

- A file move requires DB schema changes.
- A file move requires dependency upgrades.
- A file move requires broad frontend changes.
- A file move rewrites `GeneralAgent.astream()` streaming.
- A file move restores `DomainQAGraph`, `MultiAgentSupervisorGraph`, or
  `AgentRuntime`.
- Tests can pass only by deleting or weakening assertions.
- A verifier would force Target behavior into Current documentation.
