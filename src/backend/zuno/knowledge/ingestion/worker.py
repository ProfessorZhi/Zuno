from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from sqlalchemy import Engine

from zuno.knowledge.ingestion.production_runtime import (
    PACKAGE_A_PARSE_REQUESTED_TOPIC,
    PackageAProductionIngestionRuntime,
    PackageARejectDeliveryError,
    PackageAWorkerReceipt,
)
from zuno.platform.queue import (
    OutboxPublishBatch,
    PostgresOutboxRabbitMQPublisher,
    RabbitMQTopology,
    RabbitMQTransport,
)

@dataclass(frozen=True, slots=True)
class PackageAQueuePumpReceipt:
    published_count: int
    failed_publish_count: int
    delivery_received: bool
    worker_receipts: tuple[PackageAWorkerReceipt, ...] = ()
    rejected_delivery_count: int = 0

    @property
    def worker_receipt(self) -> PackageAWorkerReceipt | None:
        return self.worker_receipts[-1] if self.worker_receipts else None


@dataclass(frozen=True, slots=True)
class PackageADeadLetterReplayReceipt:
    replayed: bool
    source_queue: str
    target_queue: str
    message_id: str | None = None
    replay_trace_id: str | None = None


def package_a_rabbitmq_topology(settings: Any) -> RabbitMQTopology:
    rabbitmq = getattr(settings, "rabbitmq", {}) or {}
    exchange = str(rabbitmq.get("ingestion_exchange") or "zuno.ingestion")
    queue = str(rabbitmq.get("ingestion_parse_queue") or "zuno.ingestion.parse")
    routing_key = str(rabbitmq.get("ingestion_parse_routing_key") or "ingestion.parse.requested")
    dead_letter_exchange = str(rabbitmq.get("ingestion_dead_letter_exchange") or f"{exchange}.dlx")
    dead_letter_queue = str(rabbitmq.get("ingestion_dead_letter_queue") or f"{queue}.dlq")
    dead_letter_routing_key = str(
        rabbitmq.get("ingestion_dead_letter_routing_key") or f"{routing_key}.dead"
    )
    return RabbitMQTopology(
        exchange=exchange,
        queue=queue,
        routing_key=routing_key,
        dead_letter_exchange=dead_letter_exchange,
        dead_letter_queue=dead_letter_queue,
        dead_letter_routing_key=dead_letter_routing_key,
    )


class PackageAProductionQueueWorker:
    def __init__(
        self,
        *,
        engine: Engine,
        runtime: PackageAProductionIngestionRuntime,
        transport: RabbitMQTransport,
        topology: RabbitMQTopology,
        tenant_id: str | None = None,
        trace_id: str,
        publisher_worker_id: str = "phase11-package-a-outbox-dispatcher",
    ) -> None:
        self.engine = engine
        self.runtime = runtime
        self.transport = transport
        self.topology = topology
        self.tenant_id = tenant_id
        self.trace_id = trace_id
        self.publisher_worker_id = publisher_worker_id

    async def publish_and_consume_once(
        self,
        *,
        publish_limit: int = 10,
        consume_limit: int | None = None,
        consume_timeout_seconds: float = 5.0,
        publisher_factory: Callable[..., Any] = PostgresOutboxRabbitMQPublisher,
    ) -> PackageAQueuePumpReceipt:
        if publish_limit < 1:
            raise ValueError("publish_limit must be positive")
        resolved_consume_limit = publish_limit if consume_limit is None else consume_limit
        if resolved_consume_limit < 1:
            raise ValueError("consume_limit must be positive")
        await self.transport.declare_topology(self.topology)
        publisher = publisher_factory(
            engine=self.engine,
            transport=self.transport,
            topology=self.topology,
            worker_id=self.publisher_worker_id,
            tenant_id=self.tenant_id,
            trace_id=self.trace_id,
            topics=(PACKAGE_A_PARSE_REQUESTED_TOPIC,),
        )
        batch: OutboxPublishBatch = await publisher.publish_batch(limit=publish_limit)
        if batch.failed:
            return PackageAQueuePumpReceipt(
                published_count=len(batch.published),
                failed_publish_count=len(batch.failed),
                delivery_received=False,
            )
        worker_receipts: list[PackageAWorkerReceipt] = []
        rejected_delivery_count = 0
        for _ in range(resolved_consume_limit):
            delivery = await self.transport.get(self.topology.queue, timeout=consume_timeout_seconds)
            if delivery is None:
                break
            try:
                worker_receipts.append(await self.runtime.process_rabbitmq_delivery(delivery))
            except PackageARejectDeliveryError:
                rejected_delivery_count += 1
                continue
        return PackageAQueuePumpReceipt(
            published_count=len(batch.published),
            failed_publish_count=len(batch.failed),
            delivery_received=bool(worker_receipts) or rejected_delivery_count > 0,
            worker_receipts=tuple(worker_receipts),
            rejected_delivery_count=rejected_delivery_count,
        )

    async def replay_dead_letter_once(
        self,
        *,
        replay_trace_id: str,
        consume_timeout_seconds: float = 5.0,
    ) -> PackageADeadLetterReplayReceipt:
        if not replay_trace_id:
            raise ValueError("replay_trace_id must not be empty")
        await self.transport.declare_topology(self.topology)
        delivery = await self.transport.get(
            self.topology.dead_letter_queue,
            timeout=consume_timeout_seconds,
        )
        if delivery is None:
            return PackageADeadLetterReplayReceipt(
                replayed=False,
                source_queue=self.topology.dead_letter_queue,
                target_queue=self.topology.queue,
            )
        await self.transport.replay_dead_letter(
            self.topology,
            delivery,
            replay_trace_id=replay_trace_id,
        )
        await delivery.ack()
        return PackageADeadLetterReplayReceipt(
            replayed=True,
            source_queue=self.topology.dead_letter_queue,
            target_queue=self.topology.queue,
            message_id=delivery.message_id,
            replay_trace_id=replay_trace_id,
        )


__all__ = [
    "PackageAProductionQueueWorker",
    "PackageADeadLetterReplayReceipt",
    "PackageAQueuePumpReceipt",
    "PACKAGE_A_PARSE_REQUESTED_TOPIC",
    "package_a_rabbitmq_topology",
]
