import asyncio
from types import SimpleNamespace

from zuno.knowledge.ingestion.production_runtime import PackageAWorkerReceipt
from zuno.knowledge.ingestion.worker import (
    PACKAGE_A_PARSE_REQUESTED_TOPIC,
    PackageAProductionQueueWorker,
    package_a_rabbitmq_topology,
)
from zuno.platform.database.foundation import OutboxEventRecord
from zuno.platform.queue import PostgresOutboxRabbitMQPublisher


def test_package_a_rabbitmq_topology_uses_canonical_defaults() -> None:
    settings = SimpleNamespace(rabbitmq={})

    topology = package_a_rabbitmq_topology(settings)

    assert topology.exchange == "zuno.ingestion"
    assert topology.queue == "zuno.ingestion.parse"
    assert topology.routing_key == "ingestion.parse.requested"
    assert topology.dead_letter_exchange == "zuno.ingestion.dlx"
    assert topology.dead_letter_queue == "zuno.ingestion.parse.dlq"
    assert topology.dead_letter_routing_key == "ingestion.parse.requested.dead"


def test_package_a_queue_worker_publishes_then_consumes_delivery() -> None:
    asyncio.run(_assert_package_a_queue_worker_publishes_then_consumes_delivery())


def test_package_a_queue_worker_consumes_bounded_delivery_batch() -> None:
    asyncio.run(_assert_package_a_queue_worker_consumes_bounded_delivery_batch())


def test_outbox_publisher_claims_only_configured_topics(monkeypatch) -> None:
    import zuno.platform.queue.outbox as outbox

    calls: list[dict] = []

    class FakeRepo:
        def claim_outbox(self, **kwargs):
            calls.append(kwargs)
            return []

    class FakeUnitOfWork:
        def __init__(self, engine):
            self.repo = FakeRepo()

        def __enter__(self):
            return self.repo

        def __exit__(self, exc_type, exc, tb):
            return None

    monkeypatch.setattr(outbox, "InfrastructureUnitOfWork", FakeUnitOfWork)
    publisher = PostgresOutboxRabbitMQPublisher(
        engine=object(),
        transport=object(),
        topology=package_a_rabbitmq_topology(SimpleNamespace(rabbitmq={})),
        worker_id="phase11-package-a-outbox-dispatcher",
        tenant_id=None,
        trace_id="trace-topic-claim",
        topics=(PACKAGE_A_PARSE_REQUESTED_TOPIC,),
    )

    asyncio.run(publisher.publish_batch(limit=7))

    assert calls == [
        {
            "worker_id": "phase11-package-a-outbox-dispatcher",
            "limit": 7,
            "topics": (PACKAGE_A_PARSE_REQUESTED_TOPIC,),
        }
    ]


def test_outbox_publisher_cross_tenant_mode_uses_record_tenant() -> None:
    asyncio.run(_assert_outbox_publisher_cross_tenant_mode_uses_record_tenant())


def test_outbox_publisher_fixed_tenant_rejects_mismatch() -> None:
    asyncio.run(_assert_outbox_publisher_fixed_tenant_rejects_mismatch())


def test_queue_runner_defaults_to_package_a_ingestion_worker(monkeypatch) -> None:
    from zuno.platform.services.queue import runner

    events: list[str] = []

    async def fake_initialize_worker_runtime():
        events.append("init")

    async def fake_package_a_worker_forever():
        events.append("package-a")

    monkeypatch.setattr(runner, "app_settings", SimpleNamespace(rabbitmq={"enabled": True}))
    monkeypatch.setattr(runner, "initialize_worker_runtime", fake_initialize_worker_runtime)
    monkeypatch.setattr(runner, "run_package_a_ingestion_worker_forever", fake_package_a_worker_forever)

    asyncio.run(runner.main())

    assert events == ["init", "package-a"]


async def _assert_package_a_queue_worker_publishes_then_consumes_delivery() -> None:
    events: list[tuple[str, object]] = []
    delivery = SimpleNamespace(message_id="event-1")
    worker_receipt = PackageAWorkerReceipt(
        parse_job_id="job-1",
        parse_attempt_id="attempt-1",
        status="succeeded",
        acked_after_domain_commit=True,
        indexable_snapshot_id="indexable-1",
        outbox_event_id="snapshot-outbox-1",
    )

    class FakeTransport:
        def __init__(self) -> None:
            self.delivered = False

        async def declare_topology(self, topology):
            events.append(("declare", topology.queue))

        async def get(self, queue_name, *, timeout):
            events.append(("get", (queue_name, timeout)))
            if self.delivered:
                return None
            self.delivered = True
            return delivery

    class FakeRuntime:
        async def process_rabbitmq_delivery(self, received_delivery):
            events.append(("process", received_delivery.message_id))
            return worker_receipt

    class FakePublisher:
        def __init__(self, **kwargs):
            events.append(("publisher", kwargs["worker_id"]))
            events.append(("tenant", kwargs["tenant_id"]))
            events.append(("topics", kwargs["topics"]))

        async def publish_batch(self, *, limit):
            events.append(("publish_batch", limit))
            return SimpleNamespace(published=(object(),), failed=())

    topology = package_a_rabbitmq_topology(SimpleNamespace(rabbitmq={}))
    worker = PackageAProductionQueueWorker(
        engine=object(),
        runtime=FakeRuntime(),
        transport=FakeTransport(),
        topology=topology,
        trace_id="trace-1",
    )

    receipt = await worker.publish_and_consume_once(
        publish_limit=3,
        consume_timeout_seconds=0.25,
        publisher_factory=FakePublisher,
    )

    assert receipt.published_count == 1
    assert receipt.failed_publish_count == 0
    assert receipt.delivery_received is True
    assert receipt.worker_receipt == worker_receipt
    assert events == [
        ("declare", "zuno.ingestion.parse"),
        ("publisher", "phase11-package-a-outbox-dispatcher"),
        ("tenant", None),
        ("topics", (PACKAGE_A_PARSE_REQUESTED_TOPIC,)),
        ("publish_batch", 3),
        ("get", ("zuno.ingestion.parse", 0.25)),
        ("process", "event-1"),
        ("get", ("zuno.ingestion.parse", 0.25)),
    ]


async def _assert_package_a_queue_worker_consumes_bounded_delivery_batch() -> None:
    processed: list[str] = []
    deliveries = [
        SimpleNamespace(message_id="event-1"),
        SimpleNamespace(message_id="event-2"),
        SimpleNamespace(message_id="event-3"),
    ]

    class FakeTransport:
        async def declare_topology(self, topology):
            return None

        async def get(self, queue_name, *, timeout):
            return deliveries.pop(0) if deliveries else None

    class FakeRuntime:
        async def process_rabbitmq_delivery(self, delivery):
            processed.append(delivery.message_id)
            return PackageAWorkerReceipt(
                parse_job_id=f"job-{delivery.message_id}",
                parse_attempt_id=f"attempt-{delivery.message_id}",
                status="succeeded",
                acked_after_domain_commit=True,
            )

    class FakePublisher:
        def __init__(self, **kwargs):
            return None

        async def publish_batch(self, *, limit):
            return SimpleNamespace(published=(object(), object(), object()), failed=())

    worker = PackageAProductionQueueWorker(
        engine=object(),
        runtime=FakeRuntime(),
        transport=FakeTransport(),
        topology=package_a_rabbitmq_topology(SimpleNamespace(rabbitmq={})),
        trace_id="trace-batch",
    )

    receipt = await worker.publish_and_consume_once(
        publish_limit=3,
        consume_limit=2,
        publisher_factory=FakePublisher,
    )

    assert processed == ["event-1", "event-2"]
    assert receipt.published_count == 3
    assert receipt.delivery_received is True
    assert len(receipt.worker_receipts) == 2
    assert receipt.worker_receipt.parse_job_id == "job-event-2"


async def _assert_outbox_publisher_cross_tenant_mode_uses_record_tenant() -> None:
    published: list[dict] = []

    class FakeTransport:
        async def publish(self, topology, **kwargs):
            published.append(kwargs)

    publisher = PostgresOutboxRabbitMQPublisher(
        engine=object(),
        transport=FakeTransport(),
        topology=package_a_rabbitmq_topology(SimpleNamespace(rabbitmq={})),
        worker_id="phase11-package-a-outbox-dispatcher",
        tenant_id=None,
        trace_id="trace-tenant-dispatch",
    )
    await publisher._publish_record(
        OutboxEventRecord(
            event_id="event-tenant-a",
            aggregate_id="job-tenant-a",
            topic="ingestion.parse.requested",
            payload={"parse_job_id": "job-tenant-a"},
            payload_hash="hash",
            idempotency_key="tenant-a:parse:job-tenant-a",
            claim_owner="phase11-package-a-outbox-dispatcher",
            tenant_id="tenant-a",
            ordering_key="job-tenant-a",
            ordering_sequence=1,
            publish_attempts=0,
            retry_count=0,
            replay_count=0,
        )
    )

    assert published[0]["tenant_id"] == "tenant-a"


async def _assert_outbox_publisher_fixed_tenant_rejects_mismatch() -> None:
    class FakeTransport:
        async def publish(self, topology, **kwargs):
            raise AssertionError("mismatched tenant records must be rejected before publish")

    publisher = PostgresOutboxRabbitMQPublisher(
        engine=object(),
        transport=FakeTransport(),
        topology=package_a_rabbitmq_topology(SimpleNamespace(rabbitmq={})),
        worker_id="phase11-package-a-outbox-dispatcher",
        tenant_id="tenant-a",
        trace_id="trace-tenant-dispatch",
    )
    try:
        await publisher._publish_record(
            OutboxEventRecord(
                event_id="event-tenant-b",
                aggregate_id="job-tenant-b",
                topic="ingestion.parse.requested",
                payload={"parse_job_id": "job-tenant-b"},
                payload_hash="hash",
                idempotency_key="tenant-b:parse:job-tenant-b",
                claim_owner="phase11-package-a-outbox-dispatcher",
                tenant_id="tenant-b",
                ordering_key="job-tenant-b",
                ordering_sequence=1,
                publish_attempts=0,
                retry_count=0,
                replay_count=0,
            )
        )
    except RuntimeError as exc:
        assert "tenant does not match" in str(exc)
    else:
        raise AssertionError("mismatched tenant outbox record was not rejected")
