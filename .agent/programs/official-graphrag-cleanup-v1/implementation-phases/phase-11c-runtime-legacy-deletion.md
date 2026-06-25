# Phase 11C: Runtime Legacy Deletion

## Goal

Delete or archive legacy runtime surfaces after replacement and cutover evidence
prove no active dependency remains.

## Status

In progress / blocked overall. The current FastAPI router no longer mounts
`/domain-packs`, and active Vue knowledge routes/pages no longer open Domain
Pack entrypoints. `KnowledgeService.get_runtime_settings` now preserves
`domain_pack_id` without auto-loading `DomainPackLoader`, and `GraphRetriever`
no longer loads Domain Pack policy from `domain_pack_id`. Stackless local eval
and the dedicated Contract Review eval can build from GraphRAG Project assets.
Active dependencies still exist in `domain-packs/`, Domain Pack runtime
services/assets, direct `DomainQAGraph` loader fallback paths, Docker surfaces,
remaining direct `DomainQAGraph` source and dependencies, and `tests/compat/`.
The old backend Domain Pack endpoint/API-service wrappers, frontend Domain Pack
API/page files, and direct `MultiAgentSupervisorGraph` source are retired from
current source.

Fresh blocker classification from the 2026-06-25 Phase 01 pass:

- `src/backend/zuno/api/router.py` no longer includes Domain Pack routes.
- `apps/web/src/router/index.ts`,
  `apps/web/src/pages/workspace/components/WorkspaceSettingsShell.vue`, and
  active knowledge pages no longer expose Domain Pack entrypoints.
- `src/backend/zuno/domain_packs/contract_review/` has been removed from the
  current package path as a stale backend package asset copy and archived under
  `docs/architecture/history/domain-packs/backend-package-contract-review/`;
  root `domain-packs/contract_review/` remains Blocked Legacy / Phase 02
  migration evidence.
- `tests/test_phase5_domain_runtime_paths.py` no longer expects
  `GeneralAgent` to expose the old `KnowledgeService` / `AgentRuntime`
  Domain Pack path; it now protects the retired `AgentRuntime` facade boundary
  and the current `GeneralAgent` project-query path.
- `tests/compat/test_general_agent_domain_pack_runtime.py` has been reclassified
  to retired compatibility evidence for the removed `GeneralAgent` Domain Pack
  path.
- `tests/compat/test_domain_qa_graph_offline.py` now matches the current
  `DomainQAGraph` trace shape while remaining Blocked Legacy coverage.
- `src/backend/zuno/api/services/knowledge.py` no longer imports
  `DomainPackLoader` or calls `DomainPackLoader().load` while resolving
  runtime settings from `domain_pack_id`.
- `src/backend/zuno/services/graphrag/retriever.py` no longer imports
  `DomainPackLoader` or calls `DomainPackLoader().load` for retrieval policy
  defaults; Contract Review graph tests pass explicit GraphRAG Project
  `query_policy`.
- `tools/evals/zuno/rag_eval/run_stackless_local_eval.py` can build the
  Contract Review local graph from `GraphRAGProjectLoader` assets and no
  longer loads `DomainPackLoader` for the `contract_review` project path.
- `tools/evals/zuno/contract_review_eval/run_contract_eval.py` loads the
  Contract Review compatibility payload and eval fixture from the GraphRAG
  Project example assets instead of `DomainPackLoader` and no longer executes
  through `DomainQAGraph`.
- `src/backend/zuno/services/workspace/simple_agent.py` no longer imports
  `AgentRuntime`, exposes `domain_qa_runtime`, or calls
  `_run_domain_pack_query`; Workspace knowledge prefetch/tools now use
  `KnowledgeQueryService`.
- `tests/test_phase11c_workspace_project_query_cutover.py`,
  `tests/compat/test_workspace_domain_pack_runtime.py`, and
  `tests/test_phase5_workspace_real_runtime_flow.py` now protect the Workspace
  project-query runtime path.
- `src/backend/zuno/core/runtime/agent_runtime.py` has been removed from
  current backend source; `zuno.core` and `zuno.core.runtime` no longer export
  `AgentRuntime`.
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
- `tests/test_phase11c_agent_runtime_retirement.py`,
  `tests/compat/test_agent_runtime_multi_agent.py`,
  `tests/test_phase1_langgraph_runtime_deepening.py`, and
  `tests/test_phase5_domain_runtime_paths.py` now protect the retired
  `AgentRuntime` facade boundary.
- `src/backend/zuno/api/v1/domain_packs.py` and
  `src/backend/zuno/api/services/domain_pack.py` have been retired from
  current source.
- `src/backend/zuno/services/domain_pack/` still exists.
- `src/backend/zuno/core/graphs/domain_qa_graph.py` still exists.
- `src/backend/zuno/core/graphs/multi_agent_supervisor_graph.py` has been
  retired from current backend source.
- `tests/compat/` still exists with Domain Pack and multi-agent compatibility
  coverage.

## Dependency

Phase 11A and Phase 11B must pass first.

## Scope

- Delete or migrate Domain Pack runtime services.
- Delete or migrate `DomainQAGraph` / `DomainQAState`.
- Remove active `MultiAgentSupervisorGraph` runtime.
- Remove frontend Domain Pack current routes and API clients after replacement.
- Replace or delete compatibility tests that only protect old runtime names.
- Update Docker, launchers, docs, Agent references, and verifiers.

## Stop Conditions

- Any deletion candidate still has an active import, route, launcher, eval, or
  test dependency.
- Replacement tests do not exist.
- Contract Review assets would be lost.
- A database migration is required and not explicitly approved.

## Acceptance Criteria

- Legacy runtime paths are deleted or explicitly blocked with fresh evidence.
- Old terms remain only in history, migration scripts, retired terminology, or
  archived evidence.
- Runtime startup, API contract, frontend contract, and eval replacement tests
  pass.

## Verification Commands

```powershell
pytest -q tests/test_phase11a_knowledge_query_service.py
pytest -q tests/test_phase11b_single_generalagent_cutover.py
pytest -q tests/test_zuno_public_entrypoints.py
pytest -q tests/test_zuno_runtime_chain_guard.py
git grep -n "domain_pack_id"
git grep -n "DomainQAGraph"
git grep -n "MultiAgentSupervisorGraph"
git diff --check
```

## Evidence Package Required

- deletion candidate import proof
- moved/deleted file list
- replacement test list
- final grep classification
- commit hash and push result
