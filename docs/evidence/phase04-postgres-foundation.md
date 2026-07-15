# PHASE04 PostgreSQL Domain and Transaction Foundation Evidence

状态：`completion_candidate`

## 真实边界

PHASE04 证明 PostgreSQL 16、Alembic migration、Infrastructure Unit of Work、Outbox/Inbox、IdempotencyClaim、Lease/Fencing、Object Manifest 和 Checkpoint primitive 的最小真实集成闭环。它不证明 RabbitMQ、MinIO/S3、LangGraph 产品运行路径、领域数据切流、Backup/PITR 或 Product Runtime 已完成。

## 环境

- PostgreSQL 16 Docker Compose service：`zuno-postgres`
- Database URL：`postgresql+psycopg://postgres:postgres@localhost:5432/zuno`
- Migration head：`20260715_04`

## 已运行验证

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
