# Phase 00: Current State And Program Gate

## Goal

Prove the current repo state before starting architecture migration work.

## Dependency

None.

## Scope

- Verify Git branch, dirty status, and recent commits.
- Re-run focused Phase 11A and Phase 11B tests.
- Classify Phase 11C active dependencies.
- Confirm Phase 12 is not closed.
- Confirm Context/Memory target is not Current.

## Files To Change

- Program evidence notes only.
- Docs/status files only if current evidence contradicts them.

## Files Not To Change

- Runtime source files.
- Frontend product files.
- Docker, database schema, dependency versions, or eval metrics logic.

## Acceptance Gates

- `KnowledgeQueryService`, `GraphRAGQueryService`,
  `GraphRAGProjectSnapshot`, and `KnowledgeQueryResult` are present.
- `GeneralAgent.search_knowledge_base` calls `KnowledgeQueryService`.
- Domain Pack, `DomainQAGraph`, `MultiAgentSupervisorGraph`, and
  `tests/compat/` are classified as Current / Blocked Legacy.
- Phase 12 remains not closed unless full pytest and eval evidence exist.

## Verification Commands

```powershell
git status --short
git log -5 --oneline
pytest -q tests/test_phase11a_knowledge_query_service.py tests/test_phase11b_single_generalagent_cutover.py
git grep -n "DomainQAGraph"
git grep -n "domain_pack"
git diff --check
```

## Evidence To Return

- command output summary
- dependency classification
- go/no-go for Phase 01
