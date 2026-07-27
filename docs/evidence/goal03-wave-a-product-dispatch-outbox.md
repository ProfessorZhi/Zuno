# Goal03 Wave A Product Dispatch Outbox Evidence

status: partial_runtime_evidence
phase: PHASE09
commit_scope: Product Surface Backend Runtime repair

本文只证明本次 Wave A 修复切片：Product RuntimeRequest 提交时，同一 PostgreSQL 事务写入 Product-owned `Submission`、`UserMessage`、`ProductCommand`、`CommandReceipt`，并写入 PHASE04 统一 `infra_outbox_events`，用于事务外分发给 Agent Core Owner。

## 已证明

- 新增 Alembic revision `20260725_37`，保持单一 head。
- 新增 `product_messages`，把 UserSubmission 的用户消息作为 Product-owned append-only fact 保存。
- `ProductRepository.submit_command` 在同一事务中写入：
  - `product_submissions`
  - `product_messages`
  - `product_commands`
  - `product_command_receipts`
  - `infra_outbox_events`
- `CommandReceipt` 采用 append-only 版本序列；owner/late terminal receipt 继续追加新版本，不覆盖既有 receipt。
- 同一命令已有 owner receipt 后，后续 owner receipt 会被显式标记为 `LATE_OWNER_RECEIPT`，原始 owner 状态只进入审计 hash payload，不能冒充新的 owner 终态。
- unknown command 的 owner receipt 会 fail closed 为 `owner receipt target unavailable`，不会冒充已存在命令的后续回执。
- `infra_outbox_events.topic = product.runtime_request.dispatch`，payload 明确标记 `consumer_module = Agent Core`。
- 重复相同 client request 只追加 duplicate receipt，不重复创建 command/message/outbox。
- 不同 client request 的 Product journal sequence 在 Repository 内递增，不依赖调用方硬编码。
- `ProductService.consume_runtime_request_dispatch(...)` 可以认领 `product.runtime_request.dispatch` outbox，并把首条未处理消息幂等转换成 Agent Core 的 `GoalVersion`、`TaskContract`、`AgentRun` 和 Product owner receipt，再将 inbox 标记为 processed。
- `ProductService.consume_runtime_request_dispatch(...)` 对 Agent Core Owner unavailable fail closed：Agent Core owner 写入和 inbox receipt 在同一 savepoint 内提交；owner 写入失败时回滚 savepoint，不留下 `AgentRun`、`GoalVersion`、`TaskContract`、owner receipt 或 inbox 半成品，并通过 PHASE04 `record_outbox_publish_failure(...)` 把 dispatch outbox 恢复为 pending retry。
- owner 恢复后，同一 dispatch outbox 可以重新 claim 并成功写入 Agent Core owner fact 和 Product owner receipt，证明 cutover retry 不重复创建 AgentRun。
- `/completion` 只有 `shadow` 模式允许 Product runtime record 失败后继续旧/新 runtime 对比；`new_default` 和 `canary` 不能在 Product command/receipt/outbox 失败时绕过 Product 继续启动 owner runtime。
- `/workspace/task` 默认入口在输入安全 Gate 通过后、Workspace 旧 runtime/Unified runtime/Phase08 cutover 前记录 Product RuntimeRequest；记录失败时 fail closed 为 recoverable failure，不继续生成 artifact 或 completed 事件。
- `/workspace/task` Product RuntimeRequest event 在事件流中位于 `task_started` 之后、`planning`/`retrieval` 之前，用于证明默认 Workspace API 先进入 Product Runtime。
- Completion/Workspace legacy default Product RuntimeRequest 不再使用跨租户固定字符串冒充 AgentVersion；`ProductService.runtime_agent_version_id(...)` 生成 tenant/workspace 隔离的 Product AgentVersion ref，默认 legacy surface 通过 `bootstrap_runtime_agent=True` 在 Product Repository 内确认 PUBLISHED AgentVersion 后再提交 command。

## 验证

```powershell
python -m pytest -q tests/repo/test_goal03_wave_a_migration_contract.py tests/api/test_goal03_product_route.py -p no:cacheprovider
python tools/scripts/verify_product_surface_target_protocols.py
alembic -c infra/db/alembic.ini heads
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py -p no:cacheprovider
```

结果：

```text
5 passed
Product Surface target architecture verification passed.
20260726_40 (head)
13 passed
```

Focused rerun after Agent Core owner unavailable retry guard:

```powershell
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py::test_phase09_product_runtime_dispatch_creates_agent_run_and_owner_receipt tests/integration/test_goal03_wave_a_persistence.py::test_phase09_product_runtime_dispatch_owner_unavailable_retries_without_partial_owner_facts -p no:cacheprovider
python -m compileall -q src/backend/zuno/api/services/product/command_service.py tests/integration/test_goal03_wave_a_persistence.py
```

结果：

```text
2 passed
compileall passed
```

Focused rerun after late owner receipt guard:

```powershell
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py::test_phase09_product_owner_receipts_are_append_only_and_versioned tests/repo/test_goal03_wave_a_migration_contract.py -p no:cacheprovider
python -m pytest -q tests/api/test_completion_unified_runtime.py tests/api/test_goal03_product_route.py tests/repo/test_goal03_wave_a_migration_contract.py -p no:cacheprovider
python -m compileall -q src/backend/zuno/platform/database/product/domain.py tests/integration/test_goal03_wave_a_persistence.py tests/repo/test_goal03_wave_a_migration_contract.py
python .agent/scripts/verify_doc_boundaries.py
alembic -c infra/db/alembic.ini heads
```

结果：

```text
7 passed
24 passed, 1 warning
compileall passed
Doc boundary verification passed.
20260726_40 (head)
```

Focused rerun after Workspace default Product runtime record:

```powershell
python -m pytest -q tests/api/test_workspace_task_runtime.py -p no:cacheprovider
python -m pytest -q tests/api/test_workspace_task_runtime.py::test_workspace_task_runtime_links_task_events_artifact_and_feedback tests/api/test_workspace_task_runtime.py::test_workspace_task_runtime_fails_closed_when_product_runtime_record_fails tests/api/test_workspace_task_runtime.py::test_workspace_task_event_stream_emits_frontend_trace_payloads tests/api/test_workspace_runtime_recovery.py -p no:cacheprovider
python -m compileall -q src/backend/zuno/api/services/workspace_task_runtime.py tests/api/test_workspace_task_runtime.py tests/api/test_workspace_runtime_recovery.py
```

结果：

```text
18 passed, 1 warning
5 passed, 1 warning
compileall passed
```

Focused rerun after legacy default runtime AgentVersion bootstrap:

```powershell
python -m pytest -q tests/api/test_completion_unified_runtime.py -p no:cacheprovider
python -m pytest -q tests/api/test_goal03_product_route.py -p no:cacheprovider
python -m pytest -q tests/api/test_workspace_task_runtime.py -p no:cacheprovider
python -m compileall -q src/backend/zuno/api/services/product/command_service.py src/backend/zuno/api/services/completion.py src/backend/zuno/api/services/workspace_task_runtime.py src/backend/zuno/platform/database/product/domain.py tests/api/test_completion_unified_runtime.py tests/integration/test_goal03_wave_a_persistence.py
python tools/scripts/verify_product_surface_target_protocols.py
```

结果：

```text
12 passed, 1 warning
6 passed, 1 warning
18 passed, 1 warning
compileall passed
Product Surface target architecture verification passed.
```

PostgreSQL integration attempt:

```powershell
python -m pytest -q tests/api/test_completion_unified_runtime.py::test_completion_product_runtime_shadow_records_product_command tests/integration/test_goal03_wave_a_persistence.py::test_phase09_product_service_bootstraps_legacy_runtime_agent_version -p no:cacheprovider
```

结果：

```text
1 passed, 1 warning, 1 error
environment_blocked before ProductService bootstrap assertions:
alembic upgrade head could not connect to PostgreSQL localhost:5432.
Docker daemon check also failed: dockerDesktopLinuxEngine pipe unavailable.
```

2026-07-27 environment recheck:

```powershell
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
Test-NetConnection -ComputerName localhost -Port 5432
Get-Service -Name postgresql* -ErrorAction SilentlyContinue
where.exe postgres
where.exe pg_ctl
where.exe initdb
where.exe psql
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py::test_phase09_product_service_bootstraps_legacy_runtime_agent_version -p no:cacheprovider
```

结果：

```text
docker API unavailable: npipe dockerDesktopLinuxEngine not found.
localhost:5432 TcpTestSucceeded=False.
No local postgresql* Windows service found.
No postgres/pg_ctl/initdb/psql binary found on PATH.
test_phase09_product_service_bootstraps_legacy_runtime_agent_version:
ERROR at migrated_postgres fixture before business assertions.
Failure fingerprint:
alembic upgrade head -> sqlalchemy.exc.OperationalError -> psycopg.errors.ConnectionTimeout at localhost:5432.
```

2026-07-27 environment recovery and PostgreSQL rerun:

```powershell
Start-Service -Name com.docker.service
Start-Process -FilePath 'C:\Program Files\Docker\Docker\Docker Desktop.exe' -WindowStyle Hidden
docker compose -f infra/docker/docker-compose.yml up -d postgres
Test-NetConnection -ComputerName localhost -Port 5432
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py::test_phase09_product_service_bootstraps_legacy_runtime_agent_version -p no:cacheprovider
alembic -c infra/db/alembic.ini heads
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py -p no:cacheprovider
```

结果：

```text
zuno-postgres healthy; localhost:5432 TcpTestSucceeded=True.
1 passed
20260726_40 (head)
14 passed
```

## 未证明

- 浏览器 E2E reconnect/cutover 和更大范围 legacy API cutover fault tests 尚未完成。
- PHASE09 仍是 `in_progress`，不能据此关闭 Goal03 Wave A Gate。
