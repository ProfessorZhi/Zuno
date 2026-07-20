import asyncio
from types import SimpleNamespace

from zuno.knowledge.ingestion.production_runtime import PackageAWorkerReceipt
from zuno.knowledge.ingestion.worker import (
    PackageAProductionQueueWorker,
    package_a_rabbitmq_topology,
)


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
        async def declare_topology(self, topology):
            events.append(("declare", topology.queue))

        async def get(self, queue_name, *, timeout):
            events.append(("get", (queue_name, timeout)))
            return delivery

    class FakeRuntime:
        async def process_rabbitmq_delivery(self, received_delivery):
            events.append(("process", received_delivery.message_id))
            return worker_receipt

    class FakePublisher:
        def __init__(self, **kwargs):
            events.append(("publisher", kwargs["worker_id"]))

        async def publish_batch(self, *, limit):
            events.append(("publish_batch", limit))
            return SimpleNamespace(published=(object(),), failed=())

    topology = package_a_rabbitmq_topology(SimpleNamespace(rabbitmq={}))
    worker = PackageAProductionQueueWorker(
        engine=object(),
        runtime=FakeRuntime(),
        transport=FakeTransport(),
        topology=topology,
        tenant_id="tenant-1",
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
        ("publish_batch", 3),
        ("get", ("zuno.ingestion.parse", 0.25)),
        ("process", "event-1"),
    ]
