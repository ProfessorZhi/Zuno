# Backend Layering Guidelines

This guide turns the current architecture direction into day-to-day backend placement rules.

## Current Placement Default

Treat `src/backend/zuno/` as the stable backend runtime baseline for current architectural decisions.

Prefer:

- controller or route code:
  - `src/backend/zuno/api/*`
- business or orchestration code:
  - `src/backend/zuno/core/*`
  - `src/backend/zuno/services/*`
- persistence code:
  - `src/backend/zuno/database/models/*`
  - `src/backend/zuno/database/dao/*`
- infrastructure adapters:
  - `src/backend/zuno/services/redis.py`
  - `src/backend/zuno/services/queue/*`
  - `src/backend/zuno/services/storage/*`
  - `src/backend/zuno/services/rag/vector_db/*`
  - `src/backend/zuno/services/graphrag/*`

If a capability still exists only under a migration-era path, treat that as transitional debt to be reconciled during recovery, not as the default place to grow new structure.

## Placement Rules

If the code mainly:

- handles HTTP input/output:
  - put it in the control layer
- coordinates business flow:
  - put it in the service layer
- reads or writes database records:
  - put it in the DAO layer
- talks to Redis, queues, storage, vector DBs, or graph stores:
  - put it in the infrastructure layer

## Recovery Rule

Do not deepen the mixed-root situation.

That means:

- do not treat `services/api/src/zuno/*` as the default placement rule unless a later migration phase explicitly reopens that path
- do not let docs, tests, and implementation each point to a different backend root
- do not create new path assumptions without a matching verification step

## Evolution Rule

Write new code so it can later become:

- a clearer internal module boundary
- a queue worker
- or a future service boundary

That means:

- explicit inputs
- explicit outputs
- minimized hidden state
- minimized cross-layer imports

## Future-Oriented Context

The project is expected to keep growing in three directions:

1. multi-agent product capabilities
2. stronger runtime orchestration around LangGraph and GraphRAG
3. possible service extraction or non-Python backend integration later

Those goals should influence module placement today, but they do not justify keeping the current mixed-root state forever.
