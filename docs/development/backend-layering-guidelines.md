# Backend Layering Guidelines

This guide turns the target architecture into day-to-day development rules.

## Default Placement

When adding backend code, prefer:

- controller or route code:
  - `src/backend/zuno/api/v1/*`
- business or orchestration code:
  - `src/backend/zuno/api/services/*`
  - `src/backend/zuno/services/*`
  - `src/backend/zuno/core/*`
- persistence code:
  - `src/backend/zuno/database/dao/*`
- infrastructure adapters:
  - `src/backend/zuno/services/redis.py`
  - `src/backend/zuno/services/queue/*`
  - `src/backend/zuno/services/storage/*`
  - `src/backend/zuno/services/rag/vector_db/*`
  - `src/backend/zuno/services/graphrag/*`

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

## Evolution Rule

Whenever possible, write new code so it can later become:

- a standalone internal service
- a queue worker
- or an external language-backed service boundary

That means:

- explicit inputs
- explicit outputs
- minimized hidden state
- minimized cross-layer imports

## Future-Oriented Context

The project is expected to keep growing in three directions:

1. multi-agent product capabilities
2. microservice and cloud-native deployment readiness
3. integration with non-Python business backends such as Java services

Those goals should influence module placement today, even if deployment stays monolithic for now.
