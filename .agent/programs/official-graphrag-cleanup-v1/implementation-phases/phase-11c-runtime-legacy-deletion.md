# Phase 11C: Runtime Legacy Deletion

## Goal

Delete or archive legacy runtime surfaces after replacement and cutover evidence
prove no active dependency remains.

## Status

In progress / blocked overall. The current FastAPI router no longer mounts
`/domain-packs`, and active Vue knowledge routes/pages no longer open Domain
Pack entrypoints. Active dependencies still exist in `domain-packs/`, Domain
Pack services/assets, retained legacy endpoint/frontend files, eval/Docker
surfaces, `AgentRuntime`, remaining `DomainQAGraph` source and dependencies,
remaining `MultiAgentSupervisorGraph` source/compat surfaces, and
`tests/compat/`.

Fresh blocker classification from the 2026-06-25 Phase 01 pass:

- `src/backend/zuno/api/router.py` no longer includes Domain Pack routes.
- `apps/web/src/router/index.ts`,
  `apps/web/src/pages/workspace/components/WorkspaceSettingsShell.vue`, and
  active knowledge pages no longer expose Domain Pack entrypoints.
- `src/backend/zuno/api/v1/domain_packs.py` still retains legacy endpoint
  functions for asset migration and compatibility evidence.
- `src/backend/zuno/api/services/domain_pack.py` still exists.
- `src/backend/zuno/services/domain_pack/` still exists.
- `src/backend/zuno/core/runtime/agent_runtime.py` still dispatches legacy graph
  runtime.
- `src/backend/zuno/core/graphs/domain_qa_graph.py` still exists.
- `src/backend/zuno/core/graphs/multi_agent_supervisor_graph.py` still exists.
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
