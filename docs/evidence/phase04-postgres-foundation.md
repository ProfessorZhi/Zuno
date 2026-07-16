# PHASE04 PostgreSQL Foundation Partial Evidence

状态：`partial_implementation_available`
phase_completion: `withdrawn`
correction_date: 2026-07-16

## 真实边界

本 Evidence 曾作为 PHASE04 completion candidate。架构审查确认，它只证明 PostgreSQL 16、Alembic、基础 UoW、Outbox/Inbox、IdempotencyClaim、Lease/Fencing、Object Manifest 和 Checkpoint primitive 的最小真实集成，不足以证明完整耐久基础设施 Phase。

它不证明：

- 真实 RabbitMQ publisher confirm、redelivery、DLQ、replay 和 partition recovery；
- 真实 MinIO/S3 Object staging、commit、visibility、authorization、delete、restore 和 legal hold；
- 官方 LangGraph PostgreSQL Checkpointer 的 interrupt/resume、thread isolation、generation reconcile 和 schema upgrade；
- PostgreSQL deadlock/serialization、pool exhaustion、connection loss 和 tenant isolation；
- Backup/Restore、PITR、Projection Replay、Recovery Set 和组合依赖故障；
- 后续领域默认路径已经切换到这些 Primitive。

## 已有环境和部分产物

- PostgreSQL 16 Docker Compose service：`zuno-postgres`
- Database URL：`postgresql+psycopg://postgres:postgres@localhost:5432/zuno`
- Migration head：`20260715_04`
- `src/backend/zuno/platform/database/foundation.py`
- `infra/db/alembic/versions/20260715_04_infrastructure_foundation.py`
- `tests/integration/test_phase04_postgres_foundation.py`

## 当时已运行验证

```text
alembic -c infra/db/alembic.ini upgrade head
Running upgrade 20260417_01 -> 20260715_04, add infrastructure foundation primitives
```

```text
alembic -c infra/db/alembic.ini downgrade 20260417_01
alembic -c infra/db/alembic.ini upgrade head
Running downgrade 20260715_04 -> 20260417_01, add infrastructure foundation primitives
Running upgrade 20260417_01 -> 20260715_04, add infrastructure foundation primitives
```

```text
pytest -q tests/integration/test_phase04_postgres_foundation.py -p no:cacheprovider
5 passed in 4.22s
```

这些结果仅支持 `partial implementation available`。订正后的完整完成要求以 `.agent/programs/PHASE04_postgres-domain-and-transaction-foundation.md` 和 `closure-checklist.md` 为准。
