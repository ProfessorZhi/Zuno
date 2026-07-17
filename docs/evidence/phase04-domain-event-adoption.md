# PHASE04 领域 Outbox/Inbox 采用证据

phase_id: PHASE04
task_id: P04-T03
date: 2026-07-17
status: implementation_available
verification_baseline_commit: 2363ca30938ca0f70bfa84c576ea09d767e46f49
domain_write_outbox_atomic: passed
producer_precommit_crash_rollback: passed
rabbitmq_publish_confirm: passed
rabbitmq_consumer_redelivery: passed
inbox_domain_write_atomic: passed
consumer_precommit_crash_rollback: passed
same_hash_duplicate_no_domain_reexecution: passed
different_hash_quarantine: passed
queue_ack_after_domain_commit: passed
unknown_message_version_fail_closed: passed
p04_t03_completion: proven

## 结论与边界

P04-T03 已达到 `implementation available`。真实 Product `MessageLikeDao` 通过当前 PostgreSQL Domain UoW 在同一事务写入领域事实与 canonical Outbox；真实 Memory consumer 在同一事务写入 Inbox receipt 与 `MemoryRawEventTable`，并且只在事务提交成功后 ACK RabbitMQ。Queue ACK、Outbox published 和 Inbox receipt 均不解释为领域成功。

本证据与 RabbitMQ transport、delivery policy、broker restart、network partition、out-of-order 和 backlog/retry evidence 共同关闭 P04-T03，但不关闭 PHASE04。

## 环境与可复现输入

| 项目 | 值 |
| --- | --- |
| PostgreSQL | `zuno-postgres`，`PostgreSQL 16.14` |
| RabbitMQ | `zuno-rabbitmq`，`RabbitMQ 3.13.7` |
| 数据库 | `postgresql+psycopg://postgres:postgres@localhost:5432/zuno` |
| AMQP | `amqp://guest:guest@localhost:5672/` |
| Compose SHA-256 | `fb53082b499ec5363591562d8a67d663c4430e13bd26903a136f4677df9e1d23` |
| Session adapter SHA-256 | `6be3ad0ee1f4e855872be2a937f7c7639e3b31c362bd6135c4c4bc8e545864bc` |
| Product producer SHA-256 | `c8da8eca5641678812d90d7471ac23558bee6a6f7869a8105e0acd95d4cdc833` |
| Memory consumer SHA-256 | `08e9918d26ca797e5ccba39f7e72fef876b02a6e595f8d9c68e3e9300ef7de24` |
| Verifier SHA-256 | `1a1c8e52ac31c7b98cf817e7805aaed450d1104d16baff2437f9672a4839f686` |

## 已验证调用链

```text
ProductFeedbackOutboxService
→ domain_uow
→ MessageLikeDao + SessionOutbox
→ infra_outbox_events
→ PostgresOutboxRabbitMQPublisher
→ RabbitMQ publisher confirm
→ ProductFeedbackMemoryConsumer
→ SessionInbox + MemoryRawEventTable
→ PostgreSQL commit
→ RabbitMQ ACK
```

- Producer 使用 PHASE03 Registry 中唯一 `ProductCommandV1`，包在 `CrossModuleEnvelopeV1` 中，显式携带 tenant、workspace、principal context、trace、canonical payload hash 和 idempotency key。
- Verifier 在 Product 领域写与 Outbox 写完成后、事务提交前注入进程崩溃；两类行均为零，证明没有半提交。
- Outbox claim、persistent publish 和 publisher confirm 成功后才把记录改为 published；已有 confirm-UNKNOWN/reclaim/republish 证据继续适用。
- Consumer 首次写入 Inbox 和 Memory 领域事件后、事务提交前崩溃，RabbitMQ NACK/requeue；数据库两类行均回滚。
- 新 consumer 收到 `redelivered=true` 的同一消息后原子提交 Inbox 与 Memory 事实，再 ACK。
- 同 message ID、同 canonical hash 的 duplicate 只 ACK，不重复写 Memory 事实。
- 同 message ID、不同但结构有效的 canonical payload 被持久标记 `quarantined`，不改变 Memory 事实，并由 RabbitMQ reject 路由到 DLQ。
- Consumer 对 message/event/aggregate/idempotency、tenant/workspace、trace、producer/consumer owner、topic 与 Registry schema hash 全部 fail closed 校验。
- 未知 RabbitMQ `message_version` 被 consumer fail closed reject，并进入 DLQ，不写 Inbox 或领域事实。

## 命令与结果

```text
python tools/scripts/verify_phase04_domain_event_adoption.py
PHASE04 domain event adoption verification passed.
```

```text
pytest -q tests/integration/test_phase04_domain_event_adoption.py -p no:cacheprovider
1 passed
```

```text
pytest -q tests/integration/test_phase04_rabbitmq_transport.py tests/integration/test_phase04_rabbitmq_backlog.py tests/integration/test_phase04_rabbitmq_retry_exhaustion.py tests/integration/test_phase04_outbox_rabbitmq_publisher.py tests/integration/test_phase04_outbox_delivery_policy.py tests/integration/test_phase04_rabbitmq_out_of_order.py tests/integration/test_phase04_rabbitmq_broker_restart.py tests/integration/test_phase04_rabbitmq_network_partition.py tests/integration/test_phase04_domain_event_adoption.py -p no:cacheprovider
10 passed in 93.43s
```

## 剩余目标

- P04-T06 的官方 LangGraph PostgreSQL Checkpointer 仍处于依赖 Stop Condition。
- P04-T07 仍需完整 Checkpointer restore、Projection Replay、恢复水位与运维闭环。
- PHASE04 coordinator approval 与 PHASE05 gate 保持关闭。
