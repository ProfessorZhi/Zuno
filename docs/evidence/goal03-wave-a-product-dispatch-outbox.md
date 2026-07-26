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
- `infra_outbox_events.topic = product.runtime_request.dispatch`，payload 明确标记 `consumer_module = Agent Core`。
- 重复相同 client request 只追加 duplicate receipt，不重复创建 command/message/outbox。
- 不同 client request 的 Product journal sequence 在 Repository 内递增，不依赖调用方硬编码。

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
20260725_37 (head)
3 passed
```

## 未证明

- Agent Core consumer 尚未从 `product.runtime_request.dispatch` outbox 默认消费并创建/恢复 AgentRun。
- Projection reducer、SSE cursor/reconnect/expiry、AvailableAction、revocation cleanup 和 legacy API cutover fault tests 尚未完成。
- PHASE09 仍是 `in_progress`，不能据此关闭 Goal03 Wave A Gate。
