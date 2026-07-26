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
python -m pytest -q tests/api/test_goal03_product_route.py tests/repo/test_goal03_wave_a_migration_contract.py -p no:cacheprovider
python -m compileall -q src/backend/zuno/platform/database/product/domain.py tests/integration/test_goal03_wave_a_persistence.py tests/repo/test_goal03_wave_a_migration_contract.py
python .agent/scripts/verify_doc_boundaries.py
alembic -c infra/db/alembic.ini heads
```

结果：

```text
7 passed
12 passed, 1 warning
compileall passed
Doc boundary verification passed.
20260726_40 (head)
```

## 未证明

- 浏览器 E2E reconnect/cutover 和更大范围 legacy API cutover fault tests 尚未完成。
- PHASE09 仍是 `in_progress`，不能据此关闭 Goal03 Wave A Gate。
