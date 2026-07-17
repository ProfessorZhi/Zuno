from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Engine

from zuno.platform.database.foundation import InfrastructureUnitOfWork, OutboxEventRecord
from zuno.platform.queue.rabbitmq import RabbitMQTopology, RabbitMQTransport


@dataclass(frozen=True, slots=True)
class PublishedOutboxEvent:
    event_id: str
    topic: str
    payload_hash: str
    idempotency_key: str


class PostgresOutboxRabbitMQPublisher:
    def __init__(
        self,
        *,
        engine: Engine,
        transport: RabbitMQTransport,
        topology: RabbitMQTopology,
        worker_id: str,
        tenant_id: str,
        trace_id: str,
    ) -> None:
        self.engine = engine
        self.transport = transport
        self.topology = topology
        self.worker_id = worker_id
        self.tenant_id = tenant_id
        self.trace_id = trace_id

    async def publish_pending(self, *, limit: int = 10) -> list[PublishedOutboxEvent]:
        published: list[PublishedOutboxEvent] = []
        with InfrastructureUnitOfWork(self.engine) as repo:
            event_ids = repo.claim_outbox(worker_id=self.worker_id, limit=limit)
            records = [
                repo.load_claimed_outbox_event(event_id=event_id, worker_id=self.worker_id)
                for event_id in event_ids
            ]

        for record in records:
            await self._publish_record(record)
            with InfrastructureUnitOfWork(self.engine) as repo:
                repo.complete_outbox(event_id=record.event_id, worker_id=self.worker_id)
            published.append(
                PublishedOutboxEvent(
                    event_id=record.event_id,
                    topic=record.topic,
                    payload_hash=record.payload_hash,
                    idempotency_key=record.idempotency_key,
                )
            )
        return published

    async def publish_event(self, *, event_id: str) -> PublishedOutboxEvent:
        with InfrastructureUnitOfWork(self.engine) as repo:
            if not repo.claim_outbox_event(event_id=event_id, worker_id=self.worker_id):
                raise RuntimeError("outbox event is not pending")
            record = repo.load_claimed_outbox_event(event_id=event_id, worker_id=self.worker_id)
        await self._publish_record(record)
        with InfrastructureUnitOfWork(self.engine) as repo:
            repo.complete_outbox(event_id=record.event_id, worker_id=self.worker_id)
        return PublishedOutboxEvent(
            event_id=record.event_id,
            topic=record.topic,
            payload_hash=record.payload_hash,
            idempotency_key=record.idempotency_key,
        )

    async def _publish_record(self, record: OutboxEventRecord) -> None:
        if record.tenant_id and record.tenant_id != self.tenant_id:
            raise RuntimeError("outbox publisher tenant does not match the claimed event tenant")
        await self.transport.publish(
            self.topology,
            message_id=record.event_id,
            payload={
                "aggregate_id": record.aggregate_id,
                "event_id": record.event_id,
                "idempotency_key": record.idempotency_key,
                "payload": record.payload,
                "payload_hash": record.payload_hash,
                "topic": record.topic,
            },
            tenant_id=record.tenant_id or self.tenant_id,
            trace_id=self.trace_id,
            ordering_key=record.ordering_key,
            ordering_sequence=record.ordering_sequence,
        )


__all__ = [
    "PostgresOutboxRabbitMQPublisher",
    "PublishedOutboxEvent",
]
