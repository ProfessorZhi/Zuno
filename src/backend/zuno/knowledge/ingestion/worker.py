from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from sqlalchemy import Engine

from zuno.knowledge.ingestion.production_runtime import (
    PackageAProductionIngestionRuntime,
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
    worker_receipt: PackageAWorkerReceipt | None = None


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
        tenant_id: str,
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
        consume_timeout_seconds: float = 5.0,
        publisher_factory: Callable[..., Any] = PostgresOutboxRabbitMQPublisher,
    ) -> PackageAQueuePumpReceipt:
        await self.transport.declare_topology(self.topology)
        publisher = publisher_factory(
            engine=self.engine,
            transport=self.transport,
            topology=self.topology,
            worker_id=self.publisher_worker_id,
            tenant_id=self.tenant_id,
            trace_id=self.trace_id,
        )
        batch: OutboxPublishBatch = await publisher.publish_batch(limit=publish_limit)
        delivery = await self.transport.get(self.topology.queue, timeout=consume_timeout_seconds)
        if delivery is None:
            return PackageAQueuePumpReceipt(
                published_count=len(batch.published),
                failed_publish_count=len(batch.failed),
                delivery_received=False,
            )
        worker_receipt = await self.runtime.process_rabbitmq_delivery(delivery)
        return PackageAQueuePumpReceipt(
            published_count=len(batch.published),
            failed_publish_count=len(batch.failed),
            delivery_received=True,
            worker_receipt=worker_receipt,
        )


__all__ = [
    "PackageAProductionQueueWorker",
    "PackageAQueuePumpReceipt",
    "package_a_rabbitmq_topology",
]
