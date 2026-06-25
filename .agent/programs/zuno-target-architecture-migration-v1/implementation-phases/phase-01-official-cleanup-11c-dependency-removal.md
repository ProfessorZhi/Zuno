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
- The standalone `src/backend/zuno/core/runtime/agent_runtime.py` facade has
  been removed from current backend source; `zuno.core` and
  `zuno.core.runtime` no longer export `AgentRuntime`.
- `DomainQAGraph` and `MultiAgentSupervisorGraph` are no longer exported from
  `zuno.core` or `zuno.core.graphs`; the direct `DomainQAGraph` source remains
  for Blocked Legacy coverage.
- The direct `src/backend/zuno/core/graphs/multi_agent_supervisor_graph.py`
  source has been removed from current backend source; `tests/compat/` now
  keeps retirement evidence that the module stays absent.
- Phase 0 recovery/current-truth tests no longer treat `DomainQAGraph` or
  `DomainPackLoader` as high-value current imports; they use
  `KnowledgeQueryService`, `GraphRAGQueryService`, and
  `GraphRAGProjectSnapshot`.
- Root Phase 5 runtime import tests no longer import Domain Pack loader or the
  legacy graph as current mainline; direct legacy import coverage remains under
  `tests/compat/`.
- Phase 5 `DomainQAGraph` runtime tests have moved from root `tests/` into
  `tests/compat/` as Blocked Legacy coverage. Former
  `MultiAgentSupervisorGraph` compat tests now prove the supervisor source and
  module remain retired.
- Phase 1 `DomainQAGraph` LangGraph runtime-deepening tests have moved from
  root `tests/` into `tests/compat/` as Blocked Legacy coverage.
- Domain Pack formalization and Contract Review asset-runtime tests have moved
  from root `tests/` into `tests/compat/` until Phase 02 migrates the assets.
- Root Phase 5 domain runtime path tests no longer assert direct legacy graph
  source availability; that coverage is isolated to 11C/compat tests.
- The stale tracked backend package asset copy
  `src/backend/zuno/domain_packs/contract_review/` has been removed from the
  current package path and archived under
  `docs/architecture/history/domain-packs/backend-package-contract-review/`
  after grep showed the current loader defaults to root `domain-packs/`.
- `tests/test_phase5_domain_runtime_paths.py` no longer expects
  `GeneralAgent` to expose `KnowledgeService` or `AgentRuntime`; it now records
  the current 11B fact that `GeneralAgent` uses `KnowledgeQueryService` and a
  single react loop while protecting the retired `AgentRuntime` facade boundary.
- `tests/compat/test_general_agent_domain_pack_runtime.py` has been reclassified
  from legacy Domain Pack runtime coverage to retired compatibility evidence:
  it now proves `GeneralAgent` no longer exposes the old
  `KnowledgeService` / `AgentRuntime` / `RagHandler` path.
- `tests/compat/test_domain_qa_graph_offline.py` has been synchronized with the
  current `DomainQAGraph` trace shape; it remains Blocked Legacy coverage, not
  a target runtime endorsement.
- `KnowledgeService.get_runtime_settings` no longer auto-loads
  `DomainPackLoader` from `domain_pack_id`. It preserves the migration field
  and explicit `domain_pack` compatibility payloads while keeping
  `graphrag_project_id` as the GraphRAG Project configuration field.
- `GraphRetriever` no longer loads Domain Pack retrieval policy from a bare
  `domain_pack_id`; graph policy must be provided as explicit `query_policy`.
  Contract Review compatibility graph tests now load that policy from the
  GraphRAG Project example assets.
- Stackless local eval can build its Contract Review local graph from
  GraphRAG Project schema, prompt, retrieval policy, and eval assets without
  loading `DomainPackLoader` for `contract_review`.
- The dedicated Contract Review eval now loads the same GraphRAG Project
  compatibility payload and eval fixture without loading `DomainPackLoader`,
  while still executing through `DomainQAGraph` as Blocked Legacy.

Retained as Blocked Legacy / Phase 02 migration assets:

- `domain-packs/contract_review/`
- `src/backend/zuno/services/domain_pack/`
- direct `DomainQAGraph` loader fallback paths and Domain Pack Docker mounts

Retired from current source:

- `src/backend/zuno/api/v1/domain_packs.py`
- `src/backend/zuno/api/services/domain_pack.py`
- `apps/web/src/apis/domain-packs.ts`
- `apps/web/src/pages/knowledge/domain-pack-list.vue`
- `apps/web/src/pages/knowledge/domain-pack-create.vue`
- `apps/web/src/pages/knowledge/domain-pack-detail.vue`

Still blocked:

- `tools/evals/zuno/contract_review_eval/` still depends on `DomainQAGraph`,
  but no longer loads `DomainPackLoader`.
- direct `DomainQAGraph` id-only fallback paths still depend on
  `DomainPackLoader`.
- Stackless local eval still keeps a legacy Domain Pack fallback for
  unmigrated packs.
- `tests/compat/` still contains active compatibility coverage for Workspace,
  direct `DomainQAGraph`, Domain Pack loader/eval, and graph/runtime surfaces,
  plus replacement evidence for retired runtime names, including
  `MultiAgentSupervisorGraph`.
