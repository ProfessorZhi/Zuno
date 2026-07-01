# PHASE02 Storage Interface 与 PostgreSQL Boundary

status: pending
program: zuno-enterprise-ingestion-async-infrastructure-v1
phase: PHASE02_storage-interface-and-postgres-boundary
mode: tdd-implementation

## 目标

把 Program 2 的 `SQLiteDurableIngestionStore` 背后能力抽成 `DurableIngestionStore` interface / protocol，保留 SQLite 默认实现，同时新增 PostgreSQL-compatible boundary、dependency probe 和 target-blocked evidence。目标不是强制测试环境启动 Postgres，而是让业务事实源契约不再写死 SQLite。

## 范围

- 新增 `DurableIngestionStore` protocol，覆盖 source object、workspace file、parse job / snapshot、document version / block、index manifest / chunk、task、event、artifact、feedback。
- 将 `WorkspaceTaskRuntimeService.configure_durable_ingestion()` 类型从具体 SQLite store 放宽到 protocol。
- 保留 `SQLiteDurableIngestionStore` 作为默认 local / test implementation。
- 新增 `PostgresDurableIngestionStore` boundary 或 factory probe：无 DSN 时返回 dependency probe / target-blocked evidence，不影响 tests。
- 审查 JSON 字段、idempotency key、status、attempt_count、document_version_id、index_job_id 是否 Postgres-compatible。

## 禁止范围

- 不要求真实 PostgreSQL 服务。
- 不引入必须安装系统服务才能通过的测试。
- 不迁移现有 SQLite 测试数据。
- 不改 `/workspace/file`、`/workspace/ingest` public response shape。
- 不把 Postgres production deployment 写成 Current。

## 验收闸门

- storage contract tests 先失败后通过。
- 现有 `tests/api/test_workspace_durable_ingest_runtime.py` 仍通过。
- `PostgresDurableIngestionStore` 无 DSN 时有稳定 dependency probe / target-blocked evidence。
- Store protocol 覆盖 Program 2 已有所有 durable operations。
- schema review 记录哪些字段未来需要真实 migration 管理。

## 验证命令

```powershell
pytest -q tests/knowledge/test_enterprise_ingestion_storage_contract.py -p no:cacheprovider
pytest -q tests/api/test_workspace_durable_ingest_runtime.py -p no:cacheprovider
git diff --check
```

## 需要先读取

- `src/backend/zuno/knowledge/storage/contracts.py`
- `src/backend/zuno/knowledge/storage/durable_ingestion_store.py`
- `src/backend/zuno/knowledge/storage/sqlmodel_models.py`
- `src/backend/zuno/knowledge/storage/__init__.py`
- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `tests/knowledge/test_enterprise_ingestion_storage_contract.py`
- `tests/api/test_workspace_durable_ingest_runtime.py`

## 需要修改的文件

- `src/backend/zuno/knowledge/storage/contracts.py`
- `src/backend/zuno/knowledge/storage/durable_ingestion_store.py`
- `src/backend/zuno/knowledge/storage/__init__.py`
- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `tests/knowledge/test_enterprise_ingestion_storage_contract.py`
- 可新增 `src/backend/zuno/knowledge/storage/postgres_ingestion_store.py`

## 执行拆解

1. 写 failing test：Workspace runtime 可接受 protocol typed store，而不依赖 SQLite concrete class。
2. 写 failing test：Postgres store probe 在缺少 DSN 时返回 target-blocked evidence。
3. 实现 protocol 和类型放宽。
4. 实现 Postgres boundary / dependency probe。
5. 跑 focused tests。
6. 更新 PHASE02 evidence。

## 多 agent 分工

- Storage Agent：审 store protocol completeness。
- API Compatibility Agent：审 response shape 是否 additive。
- Verification Agent：跑 storage / durable ingest focused tests。

## 需要返回的证据

- failing test 输出。
- green test 输出。
- Store protocol 方法清单。
- Postgres target-blocked evidence 示例。
- 当前仍未接真实 Postgres 的 Target 边界。

## 停止条件

- 需要真实 Postgres 才能让基础 tests 通过。
- Store protocol 会破坏现有 durable ingest response。
- SQLModel 表改动需要 migration 方案但没有明确边界。
