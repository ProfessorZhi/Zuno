# Phase 5: Tests And Minimal Eval

## Goal

Prove that the new product surface and Deep GraphRAG V1 runtime are both real.

## Minimum Proof Areas

### Frontend

1. standard vs enhanced creation flow
2. Domain Pack binding flow
3. Domain Pack create-return flow
4. maintenance impact messaging
5. settings-shell layout integrity

### Backend

1. config impact classification
2. default planner strategy
3. fallback and downgrade metadata
4. community detection
5. global search smoke path
6. drift-like smoke path

### Minimal Eval

Compare at least:

1. `baseline_rag`
2. `local_graphrag`
3. `deep_graphrag`

## Closure Gate

Phase 5 is complete only when:

1. product flow tests pass
2. runtime route tests pass
3. Deep GraphRAG V1 can prove fallback-aware behavior
4. community-not-ready degradation is visible in trace
