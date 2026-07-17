# PHASE04 PostgreSQL Session Runtime 与 Domain UoW 证据

phase_id: PHASE04
task_id: P04-T01
date: 2026-07-17
status: implementation_available
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
default_runtime_owner: passed
dao_uow_adoption: passed
cross_repository_rollback: passed
uow_owned_commit: passed
async_task_isolation: passed
p04_t01_completion: proven

## 结论与边界

P04-T01 已完成。应用数据库配置只构造一个 `PostgresRuntime`，旧 `engine` 与 `async_engine` 导出指向该 Runtime 的 Engine，不再产生第二套连接池。Runtime 提供 sync/async SQLModel Session Factory、显式事务、tenant context、timeout、isolation、read-only、health/readiness、pool metrics 与 connection rotation。

默认 DAO 入口已迁移到 `domain_uow` / `async_domain_uow`。Repository 不再调用 `commit()` 或 `rollback()`，只执行 `flush()`；提交、回滚和 Session 生命周期由 UoW 唯一拥有。服务可在外层 UoW 中调用多个 Repository，内部 `session_getter` 会复用同一个 Session，因此异常可以原子回滚多个 Repository 写入。

本证据只关闭 P04-T01，不关闭 PHASE04。Alembic 全量领域漂移、RabbitMQ/Outbox 完整采用、MinIO/Checkpointer 和 Backup/Restore/Replay 分别属于 P04-T02、P04-T03、P04-T06、P04-T07。

## 环境

| 项目 | 值 |
| --- | --- |
| PostgreSQL | `zuno-postgres`，`16.14`，镜像 `postgres:16` |
| Image ID | `sha256:eb4759788a2182f08257135e61a34f2cfc3c2914079f3465d64ee62350f4d081` |
| SQLAlchemy / SQLModel | `2.0.48` / `0.0.38` |
| psycopg / asyncpg | `3.2.9` / `0.31.0` |
| 默认配置 SHA-256 | `A2A9A00AAF691E32CD4009F2A2E61F8139910946B7CD7F1F86C074E52ACC36A0` |
| Session Runtime Pool | `pool_size=2`、`max_overflow=1`、`pool_timeout=2s` |
| 默认应用 Pool | `pool_size=10`、`max_overflow=20` |

## 已验证行为

- 错误的 sync/async driver、非法 pool 和非法 timeout 在 Runtime 配置阶段 fail closed。
- sync/async health 读取 PostgreSQL server version 与 recovery state，并返回 pool size、checked-out、overflow。
- sync UoW 在 `SERIALIZABLE` 下提交成功，异常完整回滚；read-only 事务拒绝写入。
- async UoW 应用 `REPEATABLE READ`；statement timeout、Python task cancellation 和 backend termination 后连接池恢复。
- 两个并发 async Session 使用各自 transaction-local tenant；后续无 tenant 事务为空。
- `rotate_connections()` 后 sync/async Engine 都重新 checkout 新连接。
- 默认 `MessageLikeDao` 独立调用由隐式 UoW 提交。
- 一个外层 sync Domain UoW 同时调用 `MessageLikeDao` 和 `MessageDownDao`，模拟失败后两个表都没有残留写入。
- 默认 async `WorkSpaceSessionDao` 独立调用由隐式 UoW 提交，外层 async Domain UoW 异常时写入回滚。
- Repository 在已有 UoW 中复用同一 Session；显式嵌套 UoW、直接 Session commit 和跨 asyncio task 共享 Session 均被拒绝。
- DAO 静态扫描确认不再导入旧 `zuno.database.session`，也没有 Repository-owned commit/rollback。
- deadlock `40P01` 与 serialization `40001` 只在 transaction retry boundary 重试，不与业务 Retry 混用。
- pool exhaustion、lock timeout、statement timeout、connection loss 和 concurrent update 路径使用真实 PostgreSQL。

## 命令与结果

```text
python tools/scripts/verify_phase04_postgres_session_runtime.py
PHASE04 PostgreSQL session runtime verification passed.

python tools/scripts/verify_phase04_domain_uow_adoption.py
PHASE04 Domain UoW adoption verification passed.

pytest -q tests/integration/test_phase04_domain_uow_adoption.py tests/integration/test_phase04_postgres_session_runtime.py -p no:cacheprovider
2 passed

pytest -q tests/agent/test_workspace_session_cleanup.py tests/agent/test_workspace_session_api.py tests/storage/test_pipeline.py tests/repo/test_llm_system_sync.py tests/storage/test_database_schema.py tests/storage/test_memory_runtime_store.py tests/agent/test_memory_durable_runtime.py -p no:cacheprovider
27 passed

pytest -q tests/repo/test_current_program_contract.py tests/repo/test_phase04_complete_infrastructure.py -p no:cacheprovider
10 passed
```

完整 PHASE04 Gate 还会重复运行 deadlock、serialization、pool exhaustion、connection loss 和组合依赖验证；其未满足项必须继续作为 PHASE04 blocker 披露。

## 未通过验证披露

`pytest -q tests --ignore=tests/integration --ignore=tests/e2e -p no:cacheprovider` 实际结果为 `1202 passed, 31 failed`。失败清单主要是仓库当前已知的旧 facade `__all__`、历史 Phase 文档、旧目录结构和过时 frontend/profile 断言；其中一项暴露了本 verifier 重复 `asyncio.run()` 时未 dispose 默认 async pool 的缺陷，该缺陷已修复，并由同一 verifier 连续执行两次及上述两个 Repo Gate 文件 `10 passed` 复验。修复后未重新运行整套 1200+ 测试，因此不把全量非集成测试写成 passed。
