# PHASE04 Outbox RabbitMQ Publisher Evidence

phase_id: PHASE04
task_id: P04-T03
date: 2026-07-16
status: partial_implementation_available
outbox_claim: passed
rabbitmq_publish_confirm: passed
outbox_published_receipt: passed
inbox_dedup_receipt: passed
commit_after_publish_before_complete_crash: passed
broker_restart: not_yet_proven
partition_recovery: not_yet_proven

## Boundary

This evidence proves a real PostgreSQL outbox to RabbitMQ publisher subset. It does not close P04-T03 and does not close PHASE04.

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
- Deletes temporary RabbitMQ topology after verification.

## Commands And Results

```text
python tools/scripts/verify_phase04_outbox_rabbitmq_publisher.py
PHASE04 outbox RabbitMQ publisher verification passed.
```

```text
pytest -q tests/integration/test_phase04_outbox_rabbitmq_publisher.py -p no:cacheprovider
1 passed
```

## Remaining Gap

- Broker restart, network partition, backlog, retry exhaustion and DLQ replay are not yet proven for the outbox publisher.
- Consumer domain transaction plus inbox `COMMITTED` state is not yet proven.
- P04-T03 remains `ready`, not completed.
