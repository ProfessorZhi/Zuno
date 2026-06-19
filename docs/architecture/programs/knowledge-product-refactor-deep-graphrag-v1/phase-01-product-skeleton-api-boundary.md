# Phase 1: Product Skeleton And API Boundary

## Goal

Land the product surface and API boundary for:

1. Domain Pack page
2. knowledge creation wizard
3. knowledge maintenance page

without yet requiring the full Deep GraphRAG runtime chain.

## Required Outcome

### Frontend

1. a Domain Pack page under the knowledge module
2. a multi-step knowledge creation wizard
3. a maintenance page that replaces the giant technical form surface
4. product labels that expose only:
   - `标准检索`
   - `增强检索`

### Backend

1. Domain Pack API skeleton
2. knowledge create-with-config path
3. knowledge config get/update path
4. config impact analysis path
5. reindex action path
6. eval profile listing path
7. index status fields

## Files Expected To Change

Typical targets for this phase include:

- `apps/web/src/router/`
- `apps/web/src/pages/knowledge/`
- `apps/web/src/apis/knowledge.ts`
- `apps/web/src/apis/`
- `src/backend/zuno/api/v1/knowledge.py`
- `src/backend/zuno/api/v1/`
- `src/backend/zuno/api/services/knowledge.py`
- `src/backend/zuno/schema/`
- `src/backend/zuno/database/models/`

## Files Not To Change Yet

1. Community GraphRAG runtime modules
2. DRIFT-like runtime chain
3. retrieval router internals beyond the minimum config and status contract

## Closure Gate

This phase is complete only when:

1. the three frontend surfaces exist
2. Domain Pack is treated as an independent resource
3. config impact and reindex actions are explicit API concepts
4. maintenance UI shows status and action separation
5. the product layer never exposes internal runtime mode names to normal users
