import asyncio
from types import SimpleNamespace

from zuno.knowledge.ingestion.production_runtime import PackageARejectDeliveryError, PackageAWorkerReceipt
from zuno.knowledge.ingestion.worker import (
    PACKAGE_A_PARSE_REQUESTED_TOPIC,
    PackageAProductionQueueWorker,
    package_a_rabbitmq_topology,
)
from zuno.platform.database.foundation import OutboxEventRecord
from zuno.platform.queue import PostgresOutboxRabbitMQPublisher, RabbitMQTransport


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


def test_package_a_queue_worker_continues_after_rejected_delivery() -> None:
    asyncio.run(_assert_package_a_queue_worker_continues_after_rejected_delivery())


def test_package_a_queue_worker_does_not_consume_after_publish_failure() -> None:
    asyncio.run(_assert_package_a_queue_worker_does_not_consume_after_publish_failure())


def test_package_a_queue_worker_replays_one_dead_letter_delivery() -> None:
    asyncio.run(_assert_package_a_queue_worker_replays_one_dead_letter_delivery())


def test_package_a_rabbitmq_replay_increments_outbox_replay_count() -> None:
    asyncio.run(_assert_package_a_rabbitmq_replay_increments_outbox_replay_count())


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


def test_outbox_publisher_maps_envelope_security_epoch_to_rabbitmq_header() -> None:
    asyncio.run(_assert_outbox_publisher_maps_envelope_security_epoch_to_rabbitmq_header())


def test_outbox_publisher_maps_envelope_workspace_to_rabbitmq_header() -> None:
    asyncio.run(_assert_outbox_publisher_maps_envelope_workspace_to_rabbitmq_header())


def test_outbox_publisher_maps_envelope_trace_to_rabbitmq_header() -> None:
    asyncio.run(_assert_outbox_publisher_maps_envelope_trace_to_rabbitmq_header())


def test_outbox_publisher_maps_envelope_data_classification_to_rabbitmq_header() -> None:
    asyncio.run(_assert_outbox_publisher_maps_envelope_data_classification_to_rabbitmq_header())


def test_outbox_publisher_maps_envelope_contract_version_to_rabbitmq_header() -> None:
    asyncio.run(_assert_outbox_publisher_maps_envelope_contract_version_to_rabbitmq_header())


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


async def _assert_package_a_queue_worker_continues_after_rejected_delivery() -> None:
    processed: list[str] = []
    deliveries = [
        SimpleNamespace(message_id="poison-event"),
        SimpleNamespace(message_id="valid-event"),
    ]

    class FakeTransport:
        async def declare_topology(self, topology):
            return None

        async def get(self, queue_name, *, timeout):
            return deliveries.pop(0) if deliveries else None

    class FakeRuntime:
        async def process_rabbitmq_delivery(self, delivery):
            processed.append(delivery.message_id)
            if delivery.message_id == "poison-event":
                raise PackageARejectDeliveryError("delivery is not a Package A parse request")
            return PackageAWorkerReceipt(
                parse_job_id="parse-job-valid",
                parse_attempt_id="parse-job-valid:attempt:1",
                status="succeeded",
                acked_after_domain_commit=True,
            )

    class FakePublisher:
        def __init__(self, **kwargs):
            return None

        async def publish_batch(self, *, limit):
            return SimpleNamespace(published=(object(), object()), failed=())

    worker = PackageAProductionQueueWorker(
        engine=object(),
        runtime=FakeRuntime(),
        transport=FakeTransport(),
        topology=package_a_rabbitmq_topology(SimpleNamespace(rabbitmq={})),
        trace_id="trace-reject-continue",
    )

    receipt = await worker.publish_and_consume_once(
        publish_limit=2,
        consume_limit=2,
        publisher_factory=FakePublisher,
    )

    assert processed == ["poison-event", "valid-event"]
    assert receipt.delivery_received is True
    assert receipt.rejected_delivery_count == 1
    assert len(receipt.worker_receipts) == 1
    assert receipt.worker_receipt.parse_job_id == "parse-job-valid"


async def _assert_package_a_queue_worker_does_not_consume_after_publish_failure() -> None:
    events: list[str] = []

    class FakeTransport:
        async def declare_topology(self, topology):
            events.append("declare")

        async def get(self, queue_name, *, timeout):
            raise AssertionError("publish failure must stop this pump before consuming RabbitMQ deliveries")

    class FakeRuntime:
        async def process_rabbitmq_delivery(self, delivery):
            raise AssertionError("publish failure must not enter Package A worker runtime")

    class FakePublisher:
        def __init__(self, **kwargs):
            events.append("publisher")

        async def publish_batch(self, *, limit):
            events.append("publish_batch")
            return SimpleNamespace(published=(), failed=(object(),))

    worker = PackageAProductionQueueWorker(
        engine=object(),
        runtime=FakeRuntime(),
        transport=FakeTransport(),
        topology=package_a_rabbitmq_topology(SimpleNamespace(rabbitmq={})),
        trace_id="trace-publish-failure",
    )

    receipt = await worker.publish_and_consume_once(
        publish_limit=2,
        consume_limit=2,
        publisher_factory=FakePublisher,
    )

    assert receipt.published_count == 0
    assert receipt.failed_publish_count == 1
    assert receipt.delivery_received is False
    assert receipt.worker_receipts == ()
    assert receipt.rejected_delivery_count == 0
    assert events == ["declare", "publisher", "publish_batch"]


async def _assert_package_a_queue_worker_replays_one_dead_letter_delivery() -> None:
    events: list[tuple[str, object]] = []

    class FakeDelivery:
        message_id = "dead-letter-event-1"

        async def ack(self):
            events.append(("ack", self.message_id))

    class FakeTransport:
        async def declare_topology(self, topology):
            events.append(("declare", topology.dead_letter_queue))

        async def get(self, queue_name, *, timeout):
            events.append(("get", (queue_name, timeout)))
            return FakeDelivery()

        async def replay_dead_letter(self, topology, delivery, *, replay_trace_id):
            events.append(("replay", (delivery.message_id, topology.queue, replay_trace_id)))

    worker = PackageAProductionQueueWorker(
        engine=object(),
        runtime=object(),
        transport=FakeTransport(),
        topology=package_a_rabbitmq_topology(SimpleNamespace(rabbitmq={})),
        trace_id="trace-worker",
    )

    receipt = await worker.replay_dead_letter_once(
        replay_trace_id="trace-dlq-replay",
        consume_timeout_seconds=0.25,
    )

    assert receipt.replayed is True
    assert receipt.message_id == "dead-letter-event-1"
    assert receipt.source_queue == "zuno.ingestion.parse.dlq"
    assert receipt.target_queue == "zuno.ingestion.parse"
    assert receipt.replay_trace_id == "trace-dlq-replay"
    assert events == [
        ("declare", "zuno.ingestion.parse.dlq"),
        ("get", ("zuno.ingestion.parse.dlq", 0.25)),
        ("replay", ("dead-letter-event-1", "zuno.ingestion.parse", "trace-dlq-replay")),
        ("ack", "dead-letter-event-1"),
    ]


async def _assert_package_a_rabbitmq_replay_increments_outbox_replay_count() -> None:
    published: list[dict] = []

    class FakeExchange:
        async def publish(self, message, *, routing_key):
            published.append({"headers": dict(message.headers or {}), "routing_key": routing_key})

    delivery = SimpleNamespace(
        message_id="dead-letter-event-1",
        payload={"event_id": "dead-letter-event-1"},
        headers={
            "tenant_id": "tenant-a",
            "trace_id": "trace-before-replay",
            "outbox_publish_attempt": 1,
            "outbox_retry_count": 0,
            "outbox_replay_count": 0,
        },
    )
    topology = package_a_rabbitmq_topology(SimpleNamespace(rabbitmq={}))
    transport = RabbitMQTransport("amqp://unused")
    transport._exchanges[topology.exchange] = FakeExchange()

    await transport.replay_dead_letter(topology, delivery, replay_trace_id="trace-dlq-replay")

    assert published == [
        {
            "headers": {
                "tenant_id": "tenant-a",
                "trace_id": "trace-dlq-replay",
                "outbox_publish_attempt": 1,
                "outbox_retry_count": 0,
                "outbox_replay_count": 1,
                "replayed_from_dlq": True,
            },
            "routing_key": "ingestion.parse.requested",
        }
    ]


def test_package_a_queue_worker_replay_reports_empty_dlq() -> None:
    asyncio.run(_assert_package_a_queue_worker_replay_reports_empty_dlq())


async def _assert_package_a_queue_worker_replay_reports_empty_dlq() -> None:
    events: list[tuple[str, object]] = []

    class FakeTransport:
        async def declare_topology(self, topology):
            events.append(("declare", topology.dead_letter_queue))

        async def get(self, queue_name, *, timeout):
            events.append(("get", (queue_name, timeout)))
            return None

        async def replay_dead_letter(self, topology, delivery, *, replay_trace_id):
            raise AssertionError("empty DLQ must not replay")

    worker = PackageAProductionQueueWorker(
        engine=object(),
        runtime=object(),
        transport=FakeTransport(),
        topology=package_a_rabbitmq_topology(SimpleNamespace(rabbitmq={})),
        trace_id="trace-worker",
    )

    receipt = await worker.replay_dead_letter_once(
        replay_trace_id="trace-dlq-replay",
        consume_timeout_seconds=0.25,
    )

    assert receipt.replayed is False
    assert receipt.message_id is None
    assert receipt.source_queue == "zuno.ingestion.parse.dlq"
    assert receipt.target_queue == "zuno.ingestion.parse"
    assert events == [
        ("declare", "zuno.ingestion.parse.dlq"),
        ("get", ("zuno.ingestion.parse.dlq", 0.25)),
    ]


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


async def _assert_outbox_publisher_maps_envelope_security_epoch_to_rabbitmq_header() -> None:
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
        trace_id="trace-security-epoch",
    )
    await publisher._publish_record(
        OutboxEventRecord(
            event_id="event-security-epoch",
            aggregate_id="job-security-epoch",
            topic="ingestion.parse.requested",
            payload={
                "effective_security_epoch_ref": "security-epoch-a",
                "payload": {
                    "parse_job_id": "job-security-epoch",
                    "security_epoch_ref": "security-epoch-a",
                },
            },
            payload_hash="hash",
            idempotency_key="tenant-a:parse:job-security-epoch",
            claim_owner="phase11-package-a-outbox-dispatcher",
            tenant_id="tenant-a",
            ordering_key="job-security-epoch",
            ordering_sequence=1,
            publish_attempts=0,
            retry_count=0,
            replay_count=0,
        )
    )

    assert published[0]["security_epoch_ref"] == "security-epoch-a"


async def _assert_outbox_publisher_maps_envelope_workspace_to_rabbitmq_header() -> None:
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
        trace_id="trace-workspace",
    )
    await publisher._publish_record(
        OutboxEventRecord(
            event_id="event-workspace",
            aggregate_id="job-workspace",
            topic="ingestion.parse.requested",
            payload={
                "workspace_id": "workspace-a",
                "payload": {
                    "parse_job_id": "job-workspace",
                    "workspace_id": "workspace-a",
                },
            },
            payload_hash="hash",
            idempotency_key="tenant-a:parse:job-workspace",
            claim_owner="phase11-package-a-outbox-dispatcher",
            tenant_id="tenant-a",
            ordering_key="job-workspace",
            ordering_sequence=1,
            publish_attempts=0,
            retry_count=0,
            replay_count=0,
        )
    )

    assert published[0]["workspace_id"] == "workspace-a"


async def _assert_outbox_publisher_maps_envelope_trace_to_rabbitmq_header() -> None:
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
        trace_id="trace-dispatcher",
    )
    await publisher._publish_record(
        OutboxEventRecord(
            event_id="event-trace",
            aggregate_id="job-trace",
            topic="ingestion.parse.requested",
            payload={
                "trace_id": "trace-canonical",
                "payload": {
                    "parse_job_id": "job-trace",
                },
            },
            payload_hash="hash",
            idempotency_key="tenant-a:parse:job-trace",
            claim_owner="phase11-package-a-outbox-dispatcher",
            tenant_id="tenant-a",
            ordering_key="job-trace",
            ordering_sequence=1,
            publish_attempts=0,
            retry_count=0,
            replay_count=0,
        )
    )

    assert published[0]["trace_id"] == "trace-canonical"


async def _assert_outbox_publisher_maps_envelope_data_classification_to_rabbitmq_header() -> None:
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
        trace_id="trace-classification",
    )
    await publisher._publish_record(
        OutboxEventRecord(
            event_id="event-classification",
            aggregate_id="job-classification",
            topic="ingestion.parse.requested",
            payload={
                "data_classification": "restricted",
                "payload": {
                    "parse_job_id": "job-classification",
                },
            },
            payload_hash="hash",
            idempotency_key="tenant-a:parse:job-classification",
            claim_owner="phase11-package-a-outbox-dispatcher",
            tenant_id="tenant-a",
            ordering_key="job-classification",
            ordering_sequence=1,
            publish_attempts=0,
            retry_count=0,
            replay_count=0,
        )
    )

    assert published[0]["data_classification"] == "restricted"


async def _assert_outbox_publisher_maps_envelope_contract_version_to_rabbitmq_header() -> None:
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
        trace_id="trace-version",
    )
    await publisher._publish_record(
        OutboxEventRecord(
            event_id="event-version",
            aggregate_id="job-version",
            topic="ingestion.parse.requested",
            payload={
                "contract_version": "v2",
                "payload": {
                    "parse_job_id": "job-version",
                },
            },
            payload_hash="hash",
            idempotency_key="tenant-a:parse:job-version",
            claim_owner="phase11-package-a-outbox-dispatcher",
            tenant_id="tenant-a",
            ordering_key="job-version",
            ordering_sequence=1,
            publish_attempts=0,
            retry_count=0,
            replay_count=0,
        )
    )

    assert published[0]["version"] == "v2"
