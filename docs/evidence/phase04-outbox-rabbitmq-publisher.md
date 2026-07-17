# PHASE04 Outbox RabbitMQ Publisher Evidence

phase_id: PHASE04
task_id: P04-T03
date: 2026-07-17
status: implementation_available
outbox_claim: passed
rabbitmq_publish_confirm: passed
outbox_published_receipt: passed
inbox_dedup_receipt: passed
commit_after_publish_before_complete_crash: passed
broker_restart: passed_in_phase04-rabbitmq-broker-restart.md
partition_recovery: passed_in_phase04-rabbitmq-network-partition.md
confirm_unknown_reclaim_republish: passed
consumer_crash_redelivery: passed
inbox_first_seen_dedup: passed
out_of_order_delivery: passed_in_phase04-rabbitmq-out-of-order.md
durable_retry_backoff: passed_in_phase04-outbox-delivery-policy.md
outbox_dead_letter_replay: passed_in_phase04-outbox-delivery-policy.md
outbox_backlog_visibility: passed_in_phase04-outbox-delivery-policy.md
domain_handler_adoption: passed_in_phase04-domain-event-adoption.md
p04_t03_completion: proven

## Boundary

本证据与 `phase04-domain-event-adoption.md` 及 RabbitMQ fault evidence 共同关闭 P04-T03，但不关闭 PHASE04。

Queue ACK != Domain Success. The outbox row and inbox row are infrastructure receipts around transport; domain success remains owned by the producing and consuming domain transactions.

## Environment

| Item | Value |
| --- | --- |
| PostgreSQL service | `zuno-postgres`, image `postgres:16` |
| RabbitMQ service | `zuno-rabbitmq`, image `rabbitmq:3.13-management-alpine` |
| Database URL | `postgresql+psycopg://postgres:postgres@localhost:5432/zuno` |
| AMQP endpoint | `amqp://guest:guest@localhost:5672/` |
| Verification command | `python tools/scripts/verify_phase04_outbox_rabbitmq_publisher.py` |
| Integration test | `pytest -q tests/integration/test_phase04_outbox_rabbitmq_publisher.py -p no:cacheprovider` |

## Verified Behavior

- Inserts a pending event into real `infra_outbox_events` inside a PostgreSQL UoW.
- Claims the pending outbox row with `FOR UPDATE SKIP LOCKED`.
- Loads the claimed row and verifies canonical payload hash before publishing.
- Publishes the row to real RabbitMQ with persistent message, tenant header and trace header.
- Uses the outbox `event_id` as RabbitMQ `message_id`.
- Marks the outbox row `published` only after RabbitMQ publish returns.
- Consumes the RabbitMQ message and records a real `infra_inbox_messages` receipt.
- ACKs RabbitMQ after the inbox receipt is written.
- Simulates crash after RabbitMQ publish but before `complete_outbox`.
- Reclaims the stale claimed outbox row using `claimed_at` timeout.
- Republishes the same event id through RabbitMQ.
- Records the duplicate delivery into the same inbox row with the same payload hash.
- Leaves exactly one inbox receipt row and final outbox status `published`.
- Network blackhole 中 publisher confirm 超过 deadline 时 Outbox 保持 `claimed`；恢复后对账 confirm，stale owner reclaim 并按同 event id republish。
- Consumer 在 Inbox + follow-up Outbox 事务提交前崩溃时两者都 rollback；未 ACK delivery 在新连接中 redeliver。
- `InboxReceipt.first_seen` 区分首次处理与同 hash duplicate，duplicate 只 ACK，不重复 follow-up 写入。
- Tenant-scoped ordering metadata、乱序持久缓冲、delivery watermark、restart reconciliation、连续释放和 sequence duplicate 收敛由 `phase04-rabbitmq-out-of-order.md` 证明。
- Outbox 发布 Owner 的持久 retry/backoff、重试耗尽 dead-letter、人工 replay 审计、delivery attempt header 和 backlog visibility 由 `phase04-outbox-delivery-policy.md` 证明。
- Deletes temporary RabbitMQ topology after verification.

## Commands And Results

```text
python tools/scripts/verify_phase04_outbox_rabbitmq_publisher.py
PHASE04 outbox RabbitMQ publisher verification passed.
```

```text
pytest -q tests/integration/test_phase04_outbox_rabbitmq_publisher.py -p no:cacheprovider
2 passed
```

```text
python tools/scripts/verify_phase04_rabbitmq_network_partition.py
PHASE04 RabbitMQ network partition verification passed.
```

```text
python tools/scripts/verify_phase04_rabbitmq_out_of_order.py
PHASE04 RabbitMQ out-of-order verification passed.
```

```text
python tools/scripts/verify_phase04_outbox_delivery_policy.py
PHASE04 outbox delivery policy verification passed.
```

## Remaining Boundary

- Product 领域事实 + Outbox 与 Inbox + Memory 领域事实的同事务采用由 `phase04-domain-event-adoption.md` 证明。
- PHASE04 仍受 P04-T06、P04-T07、官方 Checkpointer、完整恢复集与最终审批阻止，不能从 P04-T03 完成状态推导整个 Phase 完成。
