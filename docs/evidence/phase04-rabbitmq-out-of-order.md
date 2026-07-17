# PHASE04 RabbitMQ 乱序交付证据

phase_id: PHASE04
task_id: P04-T03
date: 2026-07-17
status: partial_implementation_available
ordering_metadata_headers: passed
out_of_order_buffered: passed
delivery_watermark: passed
restart_reconciliation: passed
contiguous_release: passed
duplicate_sequence_delivery: passed
tenant_ordering_isolation: passed

## 边界

本证据证明 PostgreSQL Transactional Outbox/Inbox 与真实 RabbitMQ 之间的 tenant-scoped ordering 子集。真实领域 handler 采用、broker restart、retry/backoff 和 DLQ 由其他聚合证据证明；本子集不单独关闭 P04-T03，也不关闭 PHASE04。

Queue ACK != Domain Success。ACK 只在乱序消息已经持久写入 Inbox，或顺序消息及被释放消息完成本次模拟 handler 事务后执行；delivery watermark 只表示已连续收到，不表示领域结果成功。

## 环境

| 项目 | 值 |
| --- | --- |
| PostgreSQL | `zuno-postgres`, image `postgres:16` |
| RabbitMQ | `zuno-rabbitmq`, image `rabbitmq:3.13-management-alpine` |
| Database URL | `postgresql+psycopg://postgres:postgres@localhost:5432/zuno` |
| AMQP endpoint | `amqp://guest:guest@localhost:5672/` |
| Alembic head | `20260717_06` |
| 独立验证命令 | `python tools/scripts/verify_phase04_rabbitmq_out_of_order.py` |
| 集成测试命令 | `pytest -q tests/integration/test_phase04_rabbitmq_out_of_order.py tests/integration/test_phase04_outbox_rabbitmq_publisher.py -p no:cacheprovider` |

## 已验证行为

- 同一 tenant 与 ordering key 的三个 Outbox event 在 PostgreSQL 事务内原子分配 sequence `1, 2, 3`。
- 另一个 tenant 使用同一 ordering key 时独立从 sequence `1` 开始，证明顺序 Owner 不跨 tenant 泄漏。
- Publisher 按 `3, 1, 2` 顺序向真实 RabbitMQ 发布 exact event；persistent message header 保留 tenant、trace、ordering key、ordering sequence。
- Consumer 首先收到 sequence 3 时将完整 payload/hash 写入 `infra_inbox_messages`，状态为 `buffered`，watermark 为 contiguous `0`、max seen `3`，随后才 ACK。
- dispose 并重建 PostgreSQL engine 模拟 consumer 进程恢复；sequence 1 将 watermark 推进到 `1/3`。
- sequence 2 到达后在同一事务释放已持久化的 sequence 3，并把 watermark 推进到 `3/3`。
- 恢复路径从 PostgreSQL Inbox 重新加载 sequence 3 payload 并校验 canonical hash，不依赖崩溃前内存状态。
- 三条 Inbox receipt 最终均为 `processed`；再次投递相同 message id/hash/sequence 的 sequence 2 时 `first_seen=false`、`processable=false`，不会重复处理。
- Verifier 删除自己创建的 RabbitMQ topology 与唯一 PostgreSQL 行，不清理其他测试数据。

## 命令与结果

```text
python tools/scripts/verify_phase04_rabbitmq_out_of_order.py
PHASE04 RabbitMQ out-of-order verification passed.
```

```text
pytest -q tests/integration/test_phase04_rabbitmq_out_of_order.py tests/integration/test_phase04_outbox_rabbitmq_publisher.py -p no:cacheprovider
3 passed
```

```text
pytest -q tests/integration/test_phase04_postgres_foundation.py -p no:cacheprovider
10 passed
```

## 剩余缺口

- 真实领域 handler 尚未接入 `released_message_ids` 的 reconciliation 处理入口。
- Outbox owner 路径仍需 broker restart、backoff/retry exhaustion、DLQ/replay 的组合验证。
- P04-T03 已由领域采用与 RabbitMQ 聚合证据关闭；本子集自身不是完成证明。
