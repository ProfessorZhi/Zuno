# PHASE04 RabbitMQ Broker Restart Evidence

phase_id: PHASE04
task_id: P04-T03
date: 2026-07-16
status: partial_implementation_available
broker_restart: passed
durable_topology: passed
persistent_message_survived_restart: passed
tenant_trace_headers_survived_restart: passed
network_partition: not_yet_proven
retry_exhaustion: not_yet_proven

## Boundary

This evidence proves a real RabbitMQ broker restart subset. It does not close P04-T03 and does not close PHASE04.

Queue ACK != Domain Success. A persistent RabbitMQ message surviving restart proves transport durability for this subset; it does not prove consuming domain success or full outbox/inbox recovery.

## Environment

| Item | Value |
| --- | --- |
| RabbitMQ service | `zuno-rabbitmq` |
| Image | `rabbitmq:3.13-management-alpine` |
| AMQP endpoint | `amqp://guest:guest@localhost:5672/` |
| Fault command | `docker restart zuno-rabbitmq` |
| Verification command | `python tools/scripts/verify_phase04_rabbitmq_broker_restart.py` |
| Integration test | `pytest -q tests/integration/test_phase04_rabbitmq_broker_restart.py -p no:cacheprovider` |

## Verified Behavior

- Declares durable exchange, queue, DLX and DLQ on real RabbitMQ.
- Publishes a persistent JSON message with `tenant_id`, `trace_id` and `message_version` headers.
- Closes the publisher connection before restart.
- Restarts the real RabbitMQ Docker container.
- Waits for AMQP port recovery.
- Reconnects with a fresh transport after restart.
- Consumes the same message id and payload after broker restart.
- Verifies tenant header survives the restart.
- ACKs the message and deletes the temporary topology.

## Commands And Results

```text
python tools/scripts/verify_phase04_rabbitmq_broker_restart.py
PHASE04 RabbitMQ broker restart verification passed.
```

```text
pytest -q tests/integration/test_phase04_rabbitmq_broker_restart.py -p no:cacheprovider
1 passed
```

## Remaining Gap

- Network partition is not yet proven.
- Retry exhaustion and DLQ replay are not yet proven.
- Consumer crash during domain transaction is not yet proven.
- P04-T03 remains `ready`, not completed.
