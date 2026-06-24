# Phase 08: Query Method Router

## Goal

Replace public old retrieval modes with official-style query methods:
`auto/basic/local/global/drift`.

## Why This Phase Exists

Current code still routes through `rag_graph_deep`, `local_graphrag`,
`community_global`, and `drift_like`. These are internal or migration names,
not final public methods.

## Required Reading

- Phase 07 evidence package
- `.agent/architecture/near-term/10-retrieval-rag-architecture.md`
- `.agent/architecture/near-term/12-enhanced-mode-pipeline.md`

## Scope

Router inputs and outputs, public method names, fallback trace, old-name
compatibility reads, and tests.

## Non-goals

- frontend UI migration before backend contract is stable
- deleting old runtime names in the same phase
- changing Basic baseline quality without tests

## Candidate Files

- `src/backend/zuno/services/retrieval/planner.py`
- `src/backend/zuno/services/retrieval/models.py`
- `src/backend/zuno/services/retrieval/orchestrator.py`
- `src/backend/zuno/services/graphrag/models.py`
- `src/backend/zuno/schema/knowledge.py`
- `tests/compat/test_retrieval_planner.py`
- `tests/test_phase2_retrieval_strategy_program.py`
- `tests/test_retrieval_mode_semantics.py`

## Execution Order

1. Add tests for public `auto/basic/local/global/drift`.
2. Map old names only through compatibility reads.
3. Make trace show requested method, resolved method, fallback reason, and
   retrievers used.
4. Preserve Basic baseline behavior.
5. Update docs and grep classification.

## Acceptance Criteria

- Public query methods are `auto/basic/local/global/drift`.
- `rag_graph_deep` maps to Enhanced Mode plus `query_method=auto`.
- `local_graphrag`, `community_global`, and `drift_like` do not leak as public
  names.
- Fallback from unavailable graph/community assets is traceable.

## Verification Commands

```powershell
pytest -q tests/compat/test_retrieval_planner.py
pytest -q tests/test_phase2_retrieval_strategy_program.py
pytest -q tests/test_retrieval_mode_semantics.py
git grep -n "rag_graph_deep"
git grep -n "local_graphrag"
git grep -n "community_global"
git grep -n "drift_like"
git diff --check
```

## GitHub Sync Requirements

Before editing:

```powershell
git branch --show-current
git status --short
git log -1 --oneline
```

Before commit:

```powershell
git status --short
git diff --stat
git diff --check
```

After validation passes:

```powershell
git add src/backend/zuno tests docs .agent
git commit -m "refactor: introduce public graphrag query methods"
git push
```

Forbidden: force push, force-with-lease, amend, unrelated files, or success
claims after failed validation.

## Stop Conditions

- Basic quality drops.
- Old names must remain in frontend public labels to pass tests.
- Router cannot express fallback reason.

## Evidence Package Required

- old-to-new mapping table
- trace field examples
- grep classification
- test outputs
- commit hash and push result

## Risks

- Renaming modes without preserving semantics.
- Letting `auto` hide untested routing choices.

## Follow-up Phase

Phase 09: Enhanced Mode Pipeline.
