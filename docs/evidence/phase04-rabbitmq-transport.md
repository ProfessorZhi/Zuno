# PHASE04 RabbitMQ Transport Evidence

phase_id: PHASE04
task_id: P04-T03
date: 2026-07-16
status: partial_implementation_available
publisher_confirm: passed
redelivery: passed
dlq: passed
dlq_replay: passed
backlog_depth: passed
broker_restart: not_yet_proven
network_partition: not_yet_proven
outbox_inbox_atomicity: not_yet_proven

## Boundary

This evidence proves a real RabbitMQ transport subset only. It does not close P04-T03 and does not close PHASE04.

Queue ACK != Domain Success. RabbitMQ delivery, ACK, NACK, reject and DLQ are transport receipts; domain commit remains owned by the PostgreSQL transaction and inbox/outbox boundary.

## Environment

| Item | Value |
| --- | --- |
| Docker service | `zuno-rabbitmq` |
| Image | `rabbitmq:3.13-management-alpine` |
| AMQP endpoint | `amqp://guest:guest@localhost:5672/` |
| Verification command | `python tools/scripts/verify_phase04_rabbitmq_transport.py` |
| Backlog verification | `python tools/scripts/verify_phase04_rabbitmq_backlog.py` |
| Integration test | `pytest -q tests/integration/test_phase04_rabbitmq_transport.py -p no:cacheprovider` |

## Verified Behavior

- Declares durable direct exchange, durable queue, dead-letter exchange and dead-letter queue.
- Publishes persistent JSON message through a channel with publisher confirms enabled.
- Preserves `tenant_id`, `trace_id` and `message_version` headers.
- NACK with `requeue=True` returns the message with RabbitMQ redelivery flag set.
- Reject with `requeue=False` routes the poison message to the DLQ.
- Replays the DLQ message back to the main queue with the same message id and payload plus a replay receipt header.
- Reads passive queue depth to prove backlog growth after publish and drain after ACK.
- Deletes the temporary exchange and queues after the run.

## Commands And Results

```text
python tools/scripts/verify_phase04_rabbitmq_transport.py
PHASE04 RabbitMQ transport verification passed.
```

```text
python tools/scripts/verify_phase04_rabbitmq_backlog.py
PHASE04 RabbitMQ backlog verification passed.
```

```text
pytest -q tests/integration/test_phase04_rabbitmq_transport.py -p no:cacheprovider
1 passed
```

## Remaining Gap

- Transactional outbox publisher claim and RabbitMQ publish are not yet integrated as one recovery flow.
- Consumer inbox dedup and ACK-after-commit are not yet proven against RabbitMQ redelivery.
- Broker restart, connection loss, partition and retry exhaustion are still missing in this evidence file.
- P04-T03 remains `ready`, not completed.
