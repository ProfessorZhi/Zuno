# PHASE04 PostgreSQL Runtime Evidence

phase_id: PHASE04
task_id: P04-T01
date: 2026-07-16
status: partial_implementation_available
readiness: passed
tenant_context: passed
tenant_context_no_leak: passed
statement_timeout: passed
lock_timeout: passed
connection_loss_recovery: passed
deadlock_retry_boundary: passed
serialization_retry_boundary: passed
pool_exhaustion: passed
sync_session_factory: passed_in_phase04-postgres-session-runtime.md
async_session_factory: passed_in_phase04-postgres-session-runtime.md
read_only_transaction: passed_in_phase04-postgres-session-runtime.md
async_cancellation_recovery: passed_in_phase04-postgres-session-runtime.md
connection_rotation: passed_in_phase04-postgres-session-runtime.md

## 边界

本证据证明真实 PostgreSQL 上的 runtime transaction 子集：UoW 可以设置事务级 tenant context、statement timeout 和 lock timeout；tenant context 不泄漏到后续事务；慢查询会被 statement timeout 取消；等待已被其他事务持有的 row lock 会被 lock timeout 拒绝；受限连接池耗尽会 fail closed 并在释放连接后恢复；被终止 backend connection 会 fail closed，engine 可重新 checkout 恢复。

本文件单独不关闭 P04-T01，也不关闭 PHASE04。P04-T01 的 sync/async Session Factory、默认 Domain UoW 接入、read-only、cancellation 和 connection rotation 已由 `phase04-postgres-session-runtime.md` 与对应真实 verifier 补齐，聚合状态现为 completed。

## 环境

| 项目 | 值 |
| --- | --- |
| PostgreSQL service | `zuno-postgres`, image `postgres:16` |
| Database URL | `postgresql+psycopg://postgres:postgres@localhost:5432/zuno` |
| Verification command | `python tools/scripts/verify_phase04_postgres_runtime.py` |
| Deadlock retry verification | `python tools/scripts/verify_phase04_postgres_deadlock_retry.py` |
| Serialization retry verification | `python tools/scripts/verify_phase04_postgres_serialization_retry.py` |
| Pool exhaustion verification | `python tools/scripts/verify_phase04_postgres_pool_exhaustion.py` |
| Connection loss verification | `python tools/scripts/verify_phase04_postgres_connection_loss.py` |
| Session runtime verification | `python tools/scripts/verify_phase04_postgres_session_runtime.py` |
| Integration test | `pytest -q tests/integration/test_phase04_postgres_runtime.py -p no:cacheprovider` |

## 已验证行为

- `InfrastructureUnitOfWork(..., tenant_id=...)` 使用 PostgreSQL `set_config(..., is_local=true)` 设置事务级 `app.tenant_id`。
- `current_tenant_id()` 在当前 UoW 内返回 tenant id。
- 新 UoW 中 tenant context 为空，证明事务级配置没有泄漏。
- `check_readiness()` 在真实 PostgreSQL 上执行 `SELECT 1`。
- `statement_timeout_ms` 会取消 `pg_sleep(1)` 这类慢查询。
- `lock_timeout_ms` 会拒绝等待另一个事务持有的 `FOR UPDATE` row lock。
- `run_transaction_with_retry()` 只对 PostgreSQL transient SQLSTATE 执行事务级重试；真实双事务 deadlock 触发 `40P01` 后，其中一个事务被重试并最终提交。
- `run_transaction_with_retry(..., isolation_level="SERIALIZABLE")` 在真实写偏斜冲突触发 `40001` 后重跑完整事务，两个 worker 最终都提交。
- `create_foundation_engine(..., pool_size=1, max_overflow=0, pool_timeout=1)` 在唯一连接被占用时会对第二个 checkout 抛出 SQLAlchemy `TimeoutError`，释放连接后同一 pool 可恢复执行 `SELECT 1`。
- `pg_terminate_backend()` 终止 engine 持有的 backend 后，旧 connection fail closed；关闭旧 connection 后，同一 engine 可重新 checkout 并执行 `SELECT 1`。
- `PostgresRuntime` 通过显式配置创建 sync/async Engine 与 Session Factory；commit/rollback、nested misuse、并发 tenant isolation、read-only、async timeout/cancel、backend terminate recovery 和 connection rotation 已通过。

## 命令与结果

```text
python tools/scripts/verify_phase04_postgres_runtime.py
PHASE04 PostgreSQL runtime verification passed.
```

```text
python tools/scripts/verify_phase04_postgres_deadlock_retry.py
PHASE04 PostgreSQL deadlock retry verification passed.
```

```text
python tools/scripts/verify_phase04_postgres_serialization_retry.py
PHASE04 PostgreSQL serialization retry verification passed.
```

```text
python tools/scripts/verify_phase04_postgres_pool_exhaustion.py
PHASE04 PostgreSQL pool exhaustion verification passed.
```

```text
python tools/scripts/verify_phase04_postgres_connection_loss.py
PHASE04 PostgreSQL connection loss verification passed.
```

```text
pytest -q tests/integration/test_phase04_postgres_runtime.py -p no:cacheprovider
1 passed
```

```text
pytest -q tests/integration/test_phase04_postgres_deadlock_retry.py -p no:cacheprovider
1 passed
```

```text
pytest -q tests/integration/test_phase04_postgres_serialization_retry.py -p no:cacheprovider
1 passed
```

```text
pytest -q tests/integration/test_phase04_postgres_pool_exhaustion.py -p no:cacheprovider
1 passed
```

```text
pytest -q tests/integration/test_phase04_postgres_connection_loss.py -p no:cacheprovider
1 passed
```

```text
python tools/scripts/verify_phase04_postgres_session_runtime.py
PHASE04 PostgreSQL session runtime verification passed.
```

## 剩余缺口

- P04-T01 范围内没有剩余缺口；PHASE04 的其他 Work Package 仍按各自 Gate 管理。
