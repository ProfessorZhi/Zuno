# Phase 00: Current State And Program Gate

## Status

Complete for the 2026-06-25 execution pass.

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
- Domain Pack-era migration compatibility tests are classified as Current /
  Blocked Legacy; the former `tests/compat/` holding area is retired.
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

## 2026-06-25 Evidence

- `git status --short`: clean before Phase 00 edits.
- `git log -5 --oneline`: `53ab9e4`, `60b6b62`, `b160c4b`,
  `24abdd9`, `c4c52d9`.
- `pytest -q tests/test_phase11a_knowledge_query_service.py tests/test_phase11b_single_generalagent_cutover.py`:
  `4 passed`.
- Phase 11A is proved from `KnowledgeQueryService`,
  `GraphRAGQueryService`, `GraphRAGProjectSnapshot`, and
  `KnowledgeQueryResult`.
- Phase 11B is proved for the Completion API / `GeneralAgent` path through
  `search_knowledge_base` and `KnowledgeQueryService`.
- Phase 11C remains blocked by remaining compatibility surfaces in
  root `tests/`. The standalone `AgentRuntime` facade, direct
  `DomainQAGraph` source, direct `MultiAgentSupervisorGraph` source,
  `src/backend/zuno/services/domain_pack/` runtime service package, root
  Domain Pack assets, and Docker `/app/domain-packs` references have been
  removed or archived after this gate was first established.
- Phase 12 remains partial / not closed; full `pytest` and formal Eval
  baseline comparison were not completed in this pass.
- Go for bounded Phase 01 work: yes, but only for surfaces whose references
  are proved safe before removal.
