# Phase 01: Official Cleanup 11C Dependency Removal

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
