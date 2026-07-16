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
connection_loss_recovery: not_yet_proven
deadlock_retry_boundary: not_yet_proven
pool_exhaustion: not_yet_proven

## 边界

本证据证明真实 PostgreSQL 上的 runtime transaction 子集：UoW 可以设置事务级 tenant context、statement timeout 和 lock timeout；tenant context 不泄漏到后续事务；慢查询会被 statement timeout 取消；等待已被其他事务持有的 row lock 会被 lock timeout 拒绝。

这不关闭 P04-T01，也不关闭 PHASE04。当前尚未证明 async engine、完整 session factory、connection loss recovery、deadlock/serialization retry boundary、pool exhaustion 和 production domain service cutover。

## 环境

| 项目 | 值 |
| --- | --- |
| PostgreSQL service | `zuno-postgres`, image `postgres:16` |
| Database URL | `postgresql+psycopg://postgres:postgres@localhost:5432/zuno` |
| Verification command | `python tools/scripts/verify_phase04_postgres_runtime.py` |
| Integration test | `pytest -q tests/integration/test_phase04_postgres_runtime.py -p no:cacheprovider` |

## 已验证行为

- `InfrastructureUnitOfWork(..., tenant_id=...)` 使用 PostgreSQL `set_config(..., is_local=true)` 设置事务级 `app.tenant_id`。
- `current_tenant_id()` 在当前 UoW 内返回 tenant id。
- 新 UoW 中 tenant context 为空，证明事务级配置没有泄漏。
- `check_readiness()` 在真实 PostgreSQL 上执行 `SELECT 1`。
- `statement_timeout_ms` 会取消 `pg_sleep(1)` 这类慢查询。
- `lock_timeout_ms` 会拒绝等待另一个事务持有的 `FOR UPDATE` row lock。

## 命令与结果

```text
python tools/scripts/verify_phase04_postgres_runtime.py
PHASE04 PostgreSQL runtime verification passed.
```

```text
pytest -q tests/integration/test_phase04_postgres_runtime.py -p no:cacheprovider
1 passed
```

## 剩余缺口

- Async engine、session factory、pool health/readiness 和 connection rotation 尚未证明。
- Connection loss recovery、deadlock retry boundary、serialization conflict 和 pool exhaustion 尚未证明。
- Tenant context 尚未接入所有 domain service 默认路径。
- P04-T01 仍是 `ready`，不是 completed。
