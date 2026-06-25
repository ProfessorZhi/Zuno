# Phase 01: Official Cleanup 11C Dependency Removal

## Status

In progress / blocked overall.

## Goal

Remove active dependencies that keep Domain Pack, `DomainQAGraph`,
`MultiAgentSupervisorGraph`, and `tests/compat/` on the current path.

## Dependency

Phase 00 complete.

## Scope

- Continue `official-graphrag-cleanup-v1` Phase 11C.
- Replace active Domain Pack routes, services, frontend API clients, eval
  references, Docker references, and compatibility tests with GraphRAG Project
  equivalents or archived history.
- Keep migration-only compatibility only where a test proves it is still
  required.

## Files To Change

- `src/backend/zuno/api/`
- `src/backend/zuno/api/services/`
- `src/backend/zuno/core/`
- `src/backend/zuno/services/domain_pack/`
- `apps/web/src/apis/`
- `tools/evals/zuno/`
- `tests/`
- `.agent/programs/official-graphrag-cleanup-v1/`

## Files Not To Change

- Database migrations unless explicitly approved.
- Dependency versions.
- Java, microservice, event worker, or product-level multi-agent code.

## Acceptance Gates

- No active current route depends on `/domain-packs`.
- No current `GeneralAgent` path imports `DomainQAGraph`.
- `MultiAgentSupervisorGraph` is removed from current runtime or explicitly
  moved to history/compat with proof.
- `tests/compat/` is reduced, replaced, or reclassified with exact evidence.

## Verification Commands

```powershell
pytest -q tests/test_phase11a_knowledge_query_service.py tests/test_phase11b_single_generalagent_cutover.py
pytest -q tests/test_zuno_public_entrypoints.py tests/test_zuno_runtime_chain_guard.py
git grep -n "domain_pack_id"
git grep -n "DomainQAGraph"
git grep -n "MultiAgentSupervisorGraph"
git diff --check
```

## Evidence To Return

- moved/deleted file list
- replacement tests
- grep classification
- commit hash and push result

## 2026-06-25 Progress

Removed from the active current path:

- Current FastAPI router no longer imports or includes
  `zuno.api.v1.domain_packs.router`; `/api/v1/domain-packs` is no longer a
  mounted current route.
- Active Vue knowledge routes and settings-shell mappings no longer expose
  Domain Pack list/create/detail pages.
- Knowledge create/settings pages no longer call `getDomainPacksAPI`; they use
  `graphrag_project_id` as the GraphRAG Project field.
- Workspace knowledge prefetch and Workspace `search_knowledge_base` no longer
  import `AgentRuntime`, expose `domain_qa_runtime`, or call
  `_run_domain_pack_query`; they use `KnowledgeQueryService` and
  `KnowledgeQueryResult` payload mapping.
- The stale tracked backend package asset copy
  `src/backend/zuno/domain_packs/contract_review/` has been removed from the
  current package path and archived under
  `docs/architecture/history/domain-packs/backend-package-contract-review/`
  after grep showed the current loader defaults to root `domain-packs/`.
- `tests/test_phase5_domain_runtime_paths.py` no longer expects
  `GeneralAgent` to expose `KnowledgeService` or `AgentRuntime`; it now records
  the current 11B fact that `GeneralAgent` uses `KnowledgeQueryService` and a
  single react loop while still retaining `AgentRuntime` tests as Blocked
  Legacy evidence.
- `tests/compat/test_general_agent_domain_pack_runtime.py` has been reclassified
  from legacy Domain Pack runtime coverage to retired compatibility evidence:
  it now proves `GeneralAgent` no longer exposes the old
  `KnowledgeService` / `AgentRuntime` / `RagHandler` path.
- `tests/compat/test_domain_qa_graph_offline.py` has been synchronized with the
  current `DomainQAGraph` trace shape; it remains Blocked Legacy coverage, not
  a target runtime endorsement.

Retained as Blocked Legacy / Phase 02 migration assets:

- `domain-packs/contract_review/`
- `src/backend/zuno/api/v1/domain_packs.py`
- `src/backend/zuno/api/services/domain_pack.py`
- `src/backend/zuno/services/domain_pack/`
- `apps/web/src/apis/domain-packs.ts`
- `apps/web/src/pages/knowledge/domain-pack-*.vue`
- Contract Review eval assets and Domain Pack Docker mounts

Still blocked:

- `src/backend/zuno/core/runtime/agent_runtime.py` still imports and dispatches
  `DomainQAGraph` and `MultiAgentSupervisorGraph`; it remains a standalone
  Blocked Legacy source/compat surface.
- `tools/evals/zuno/contract_review_eval/` and stackless eval paths still
  depend on `DomainPackLoader` / `DomainQAGraph`.
- `tests/compat/` still contains active compatibility coverage for Workspace,
  `AgentRuntime`, `DomainQAGraph`, `MultiAgentSupervisorGraph`, Domain Pack
  loader/eval, and graph/runtime surfaces.
