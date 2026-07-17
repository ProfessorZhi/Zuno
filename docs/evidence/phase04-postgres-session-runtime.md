# PHASE04 PostgreSQL Session Runtime 证据

phase_id: PHASE04
task_id: P04-T01
date: 2026-07-17
status: partial_implementation_available
sync_session_factory: passed
async_session_factory: passed
explicit_transaction_scope: passed
commit_rollback: passed
nested_misuse_reject: passed
failed_entry_connection_cleanup: passed
tenant_concurrency_isolation: passed
tenant_context_no_leak: passed
read_only_transaction: passed
transaction_isolation: passed
async_statement_timeout: passed
async_cancellation_recovery: passed
async_connection_loss_recovery: passed
connection_rotation: passed
pool_health_metrics: passed

## 边界

本证据证明独立 `PostgresRuntime` 可以从显式配置创建 sync/async Engine 与 Session Factory，并为两种 Session 提供一致的 UoW、transaction-local tenant、timeout、isolation、read-only、health/readiness、pool metrics 与 connection rotation 语义。

本证据不关闭 P04-T01，也不关闭 PHASE04。现有领域服务尚未全部从导入时全局 engine/session 切换到该 Runtime Factory，不能把基础设施 Port 可用解释为 production default path 已迁移。

## 环境

| 项目 | 值 |
| --- | --- |
| PostgreSQL | `zuno-postgres`，镜像 `postgres:16` |
| Sync driver | `postgresql+psycopg` |
| Async driver | `postgresql+asyncpg` |
| Pool | `pool_size=2`、`max_overflow=1`、`pool_timeout=2s` |
| 验证命令 | `python tools/scripts/verify_phase04_postgres_session_runtime.py` |
| 集成测试 | `pytest -q tests/integration/test_phase04_postgres_session_runtime.py -p no:cacheprovider` |

## 已验证行为

- Runtime 配置拒绝错误的 sync/async driver、非法 pool 与非法 timeout。
- sync 与 async health 分别读取 PostgreSQL server version 和 recovery state，并输出 pool size、checked-out 与 overflow。
- sync Session UoW 在 `SERIALIZABLE` 事务中设置 tenant context，提交后持久写入，异常时完整回滚。
- sync read-only transaction 对写入 fail closed。
- foundation UoW、sync Session UoW 与 async Session UoW 都拒绝同一对象 nested/concurrent entry。
- foundation UoW 在事务级配置失败后回滚并归还已取得的连接，连接池 checked-out 数恢复为零。
- 两个真实 async Session 并发使用不同 tenant，彼此读取到各自 transaction-local context；后续无 tenant 事务读取为空。
- async Session UoW 正确应用 `REPEATABLE READ`，read-only transaction 拒绝写入。
- async `statement_timeout=100ms` 取消 `pg_sleep(1)` 后，连接池可重新 health/readiness。
- Python task cancellation 中止 `pg_sleep(30)`，UoW 回滚并关闭 Session，后续 async health 通过。
- `pg_terminate_backend` 终止 async backend 后，旧事务 fail closed，新 checkout 恢复。
- `rotate_connections()` dispose sync/async pool；下一次 async checkout 使用不同 backend pid，随后两类 health 均通过。
- Runtime 不保存数据库异常文本，只在 health receipt 暴露异常类型代码。

## 命令与结果

```text
python tools/scripts/verify_phase04_postgres_session_runtime.py
PHASE04 PostgreSQL session runtime verification passed.
```

## 剩余缺口

- 领域 Service/Repository 默认路径尚未全面接入 `PostgresRuntime` 与显式 UoW。
- 旧 `zuno.database` 导入时全局 engine/session 仍是 compatibility surface，需要 Expand/Migrate/Verify/Contract cutover 后才能收缩。
- P04-T01 保持 `ready`，不是 completed。
