# PHASE04 RabbitMQ Network Partition Evidence

phase_id: PHASE04
task_id: P04-T03
date: 2026-07-17
status: partial_implementation_available
network_partition: passed
partition_publish_fail_closed: passed
partition_unknown_reconciled: passed
transport_reconnect: passed
pre_partition_persistent_delivery: passed
post_recovery_confirmed_delivery: passed
tenant_trace_context_after_recovery: passed

## 边界

本证据证明真实 RabbitMQ 的 client/broker network partition 与恢复子集，不关闭 P04-T03，也不关闭 PHASE04。

Queue ACK != Domain Success。Partition 期间未取得 publisher confirm 的操作不得解释为领域成功；恢复后消息被消费和 ACK，也只证明 transport delivery。

## 环境

| 项目 | 值 |
| --- | --- |
| RabbitMQ 服务 | `zuno-rabbitmq` |
| Image | `rabbitmq:3.13-management-alpine` |
| Broker endpoint | `localhost:5672` |
| Fault mechanism | 本地 ephemeral TCP proxy 暂停双向转发，形成无断链、无响应的 network blackhole；broker 进程保持 healthy |
| Verification | `python tools/scripts/verify_phase04_rabbitmq_network_partition.py` |
| Integration test | `pytest -q tests/integration/test_phase04_rabbitmq_network_partition.py -p no:cacheprovider` |

## 已验证行为

- 通过 fault proxy 连接真实 RabbitMQ，声明 durable exchange、queue、DLX 和 DLQ。
- Partition 前发布 persistent message 并取得 publisher confirm，但暂不消费。
- Partition 时保持 TCP socket，但暂停 client/broker 双向数据转发，publisher 无法取得 broker confirm。
- Partition 期间 publish 无法取得 confirm，调用超时或连接失败，不返回成功。
- 超时不取消底层 receipt future；恢复后等待 publisher confirm，并按 message id 对账该次 UNKNOWN delivery。
- 恢复 proxy 后关闭旧 transport，新的 `aio_pika.connect_robust` transport 成功重连并发布新消息。
- 恢复后消费 partition 前持久消息和恢复后 confirmed 消息，并校验 message id、tenant 与 trace header。
- 清理临时 topology；RabbitMQ 容器在整个 fault 中保持运行。

## 命令与结果

```text
python tools/scripts/verify_phase04_rabbitmq_network_partition.py
PHASE04 RabbitMQ network partition verification passed.
```

```text
pytest -q tests/integration/test_phase04_rabbitmq_network_partition.py -p no:cacheprovider
1 passed
```

## 剩余缺口

- Outbox publisher 自身的 partition/reconnect、confirm-UNKNOWN reconciliation 与 consumer crash transaction 仍需独立证明。
- Out-of-order delivery/consumer ownership 的完整运行时处理仍未收口。
- P04-T03 保持 `ready`，不是 completed。
