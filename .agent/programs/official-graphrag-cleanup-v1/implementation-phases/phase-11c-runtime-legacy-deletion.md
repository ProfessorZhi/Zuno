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
and the dedicated Contract Review eval can build from GraphRAG Project assets
and call graph extractors with `project_payload=project_payload`.
`GraphRetrieverAdapter` maps `scope_policy.graphrag_project_id` to the current
legacy graph storage filter without a database schema, Neo4j property-name,
API, or frontend migration.
Root `domain-packs/` assets are archived under
`docs/architecture/history/domain-packs/root-contract-review/`, and Docker no
longer copies or mounts `/app/domain-packs`. The former `tests/compat/`
holding area is retired. Active dependencies still exist in remaining
migration compatibility surfaces under root `tests/`. The old
backend Domain Pack endpoint/API-service wrappers, frontend Domain Pack
API/page files, direct `DomainQAGraph` source, legacy graph state module,
`src/backend/zuno/services/domain_pack/` runtime service package, and direct
`MultiAgentSupervisorGraph` source are retired from current source.

Fresh blocker classification from the 2026-06-25 Phase 01 pass:

- `src/backend/zuno/api/router.py` no longer includes Domain Pack routes.
- `apps/web/src/router/index.ts`,
  `apps/web/src/pages/workspace/components/WorkspaceSettingsShell.vue`, and
  active knowledge pages no longer expose Domain Pack entrypoints.
- `src/backend/zuno/domain_packs/contract_review/` has been removed from the
  current package path as a stale backend package asset copy and archived under
  `docs/architecture/history/domain-packs/backend-package-contract-review/`;
  root `domain-packs/contract_review/` has also been moved to
  `docs/architecture/history/domain-packs/root-contract-review/` as History.
- `tests/test_phase5_domain_runtime_paths.py` no longer expects
  `GeneralAgent` to expose the old `KnowledgeService` / `AgentRuntime`
  Domain Pack path; it now protects the retired `AgentRuntime` facade boundary
  and the current `GeneralAgent` project-query path.
- `tests/test_general_agent_domain_pack_runtime.py` has been reclassified
  to retired compatibility evidence for the removed `GeneralAgent` Domain Pack
  path.
- Root Phase 11C tests now prove the direct `DomainQAGraph` module and legacy
  graph state module remain retired from current backend source.
- `src/backend/zuno/api/services/knowledge.py` no longer imports
  `DomainPackLoader` or calls `DomainPackLoader().load` while resolving
  runtime settings from `domain_pack_id`.
- `src/backend/zuno/services/graphrag/retriever.py` no longer imports
  `DomainPackLoader` or calls `DomainPackLoader().load` for retrieval policy
  defaults; Contract Review graph tests pass explicit GraphRAG Project
  `query_policy`.
- `src/backend/zuno/services/retrieval/retrievers.py` maps
  `scope_policy.graphrag_project_id` to the current legacy graph storage
  filter field, `domain_pack_id`, so project-scoped graph retrieval works
  without restoring Domain Pack policy loading or changing the storage schema.
- `tools/evals/zuno/rag_eval/run_stackless_local_eval.py` can build the
  Contract Review local graph from `GraphRAGProjectLoader` assets and no
  longer loads `DomainPackLoader` for the `contract_review` project path. It
  calls graph extraction with `project_payload=project_payload` and no longer
  keeps the private `_load_graph_project_domain_payload` alias.
- `tools/evals/zuno/contract_review_eval/run_contract_eval.py` loads the
  Contract Review compatibility payload and eval fixture from the GraphRAG
  Project example assets instead of `DomainPackLoader` and no longer executes
  through `DomainQAGraph`. It calls graph extraction with
  `project_payload=project_payload`.
- `src/backend/zuno/services/workspace/simple_agent.py` no longer imports
  `AgentRuntime`, exposes `domain_qa_runtime`, or calls
  `_run_domain_pack_query`; Workspace knowledge prefetch/tools now use
  `KnowledgeQueryService`.
- `tests/test_phase11c_workspace_project_query_cutover.py`,
  `tests/test_workspace_domain_pack_runtime.py`, and
  `tests/test_phase5_workspace_real_runtime_flow.py` now protect the Workspace
  project-query runtime path.
- `src/backend/zuno/core/runtime/agent_runtime.py` has been removed from
  current backend source; `zuno.core` and `zuno.core.runtime` no longer export
  `AgentRuntime`.
- `DomainQAGraph` and `MultiAgentSupervisorGraph` are no longer exported from
  `zuno.core` or `zuno.core.graphs`; the direct `DomainQAGraph` source has
  been removed from current backend source.
- The direct `src/backend/zuno/core/graphs/multi_agent_supervisor_graph.py`
  source has been removed from current backend source; root Phase 11C tests
  keep retirement evidence that the module stays absent.
- Phase 0 recovery/current-truth tests no longer treat `DomainQAGraph` or
  `DomainPackLoader` as high-value current imports; they use
  `KnowledgeQueryService`, `GraphRAGQueryService`, and
  `GraphRAGProjectSnapshot`.
- Root Phase 5 runtime import tests no longer import Domain Pack loader or the
  legacy graph as current mainline; root Phase 11C tests own retired-import
  coverage.
- Former Phase 5 and Phase 1 `DomainQAGraph` behavior compat tests have been
  removed after the direct graph source retired; root Phase 11C tests now keep
  retirement evidence for the old module instead of behavior coverage. Former
  `MultiAgentSupervisorGraph` compat guard files have also been retired after
  root Phase 11C tests took over the source/import boundary.
- Domain Pack runtime service behavior tests have been replaced by root Phase
  11C retired-import guards for `zuno.services.domain_pack`. Contract Review
  compatibility tests now use GraphRAG Project payloads instead of
  `DomainPackLoader`.
- Root Phase 5 domain runtime path tests no longer assert direct legacy graph
  source availability; root Phase 11C tests own that retired-import coverage.
- `tests/test_phase11c_agent_runtime_retirement.py`,
  `tests/test_phase1_langgraph_runtime_deepening.py`, and
  `tests/test_phase5_domain_runtime_paths.py` now protect the retired
  `AgentRuntime` facade boundary.
- `src/backend/zuno/api/v1/domain_packs.py` and
  `src/backend/zuno/api/services/domain_pack.py` have been retired from
  current source.
- `src/backend/zuno/services/domain_pack/` has been retired from current
  backend source.
- Root `domain-packs/` has been retired from the current root layout and moved
  to `docs/architecture/history/domain-packs/root-contract-review/`.
- Docker no longer copies or mounts `/app/domain-packs`.
- `src/backend/zuno/core/graphs/domain_qa_graph.py` and
  `src/backend/zuno/core/graphs/states.py` have been retired from current
  backend source.
- `src/backend/zuno/core/graphs/multi_agent_supervisor_graph.py` has been
  retired from current backend source.
- Root `tests/` still contains migration/current compatibility coverage that
  must be promoted to target naming or retired before 11C can close.

## Dependency

Phase 11A and Phase 11B must pass first.

## Scope

- Keep Domain Pack runtime services retired from current backend source.
- Keep `DomainQAGraph` / `DomainQAState` retired from current backend source.
- Remove active `MultiAgentSupervisorGraph` runtime.
- Remove frontend Domain Pack current routes and API clients after replacement.
- Replace or delete compatibility tests that only protect old runtime names.
- Keep Docker `/app/domain-packs` copy and mounts retired.
- Update docs, Agent references, and verifiers after each retired surface.

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
