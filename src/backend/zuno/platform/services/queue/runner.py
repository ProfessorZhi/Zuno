import asyncio
from collections.abc import Callable

from loguru import logger

from zuno.settings import app_settings, initialize_app_settings


async def initialize_worker_runtime():
    await initialize_app_settings()

    from zuno.database.init_data import init_database

    await init_database()


async def consume_forever(
    *,
    queue_name: str,
    handler: Callable[[dict], object],
    poll_interval: float = 1.0,
):
    from zuno.services.queue.client import QueueClient

    queue_client = QueueClient()
    logger.info(f"RabbitMQ worker listening on queue: {queue_name}")
    while True:
        try:
            payload = await queue_client.consume_once(queue_name)
            if payload is None:
                await asyncio.sleep(poll_interval)
                continue
            logger.info(f"RabbitMQ worker received message: queue={queue_name} payload={payload}")
            await handler(payload)
        except Exception as err:
            logger.exception(f"RabbitMQ worker error on queue={queue_name}: {err}")
            await asyncio.sleep(poll_interval)


async def run_package_a_ingestion_worker_forever(
    *,
    poll_interval: float = 1.0,
    publish_limit: int = 10,
    consume_timeout_seconds: float = 5.0,
) -> None:
    from zuno.api.services.workspace_task_runtime import build_package_a_production_ingestion_runtime
    from zuno.knowledge.ingestion import PackageAProductionQueueWorker, package_a_rabbitmq_topology
    from zuno.platform.database import engine
    from zuno.platform.queue import RabbitMQTransport

    rabbitmq = app_settings.rabbitmq or {}
    rabbitmq_url = str(rabbitmq.get("url") or "").strip()
    if not rabbitmq_url:
        raise RuntimeError("Package A ingestion worker requires rabbitmq.url")
    runtime = build_package_a_production_ingestion_runtime(
        engine=engine,
        settings=app_settings,
        worker_id=str(rabbitmq.get("ingestion_worker_id") or "phase11-package-a-parser-worker"),
    )
    if runtime is None:
        raise RuntimeError("Package A ingestion worker requires production MinIO storage configuration")
    topology = package_a_rabbitmq_topology(app_settings)
    configured_tenant_id = rabbitmq.get("tenant_id")
    tenant_id = str(configured_tenant_id).strip() if configured_tenant_id else None
    trace_id = str(rabbitmq.get("ingestion_trace_id") or "phase11-package-a-worker")
    publisher_worker_id = str(
        rabbitmq.get("ingestion_outbox_worker_id") or "phase11-package-a-outbox-dispatcher"
    )
    async with RabbitMQTransport(rabbitmq_url) as transport:
        worker = PackageAProductionQueueWorker(
            engine=engine,
            runtime=runtime,
            transport=transport,
            topology=topology,
            tenant_id=tenant_id,
            trace_id=trace_id,
            publisher_worker_id=publisher_worker_id,
        )
        logger.info(
            "Package A ingestion worker listening: exchange={} queue={}",
            topology.exchange,
            topology.queue,
        )
        while True:
            try:
                await worker.publish_and_consume_once(
                    publish_limit=publish_limit,
                    consume_timeout_seconds=consume_timeout_seconds,
                )
            except Exception as err:
                logger.exception(f"Package A ingestion worker error: {err}")
            await asyncio.sleep(poll_interval)


async def main():
    await initialize_worker_runtime()

    if not (app_settings.rabbitmq or {}).get("enabled"):
        raise RuntimeError("RabbitMQ worker started while rabbitmq.enabled is false")

    if (app_settings.rabbitmq or {}).get("package_a_ingestion_enabled", True):
        await run_package_a_ingestion_worker_forever()
        return

    from zuno.services.pipeline.manager import KnowledgePipelineManager
    from zuno.services.queue.client import QueueClient, get_queue_names
    from zuno.services.queue.workers import GraphWorker, IndexWorker, ParseWorker

    queue_client = QueueClient()
    pipeline_manager = KnowledgePipelineManager(
        enable_graph_indexing=True,
        enable_elasticsearch=app_settings.rag.enable_elasticsearch,
    )
    queue_names = get_queue_names()

    parse_worker = ParseWorker(
        queue_client=queue_client,
        pipeline_manager=pipeline_manager,
        queue_names=queue_names,
    )
    index_worker = IndexWorker(
        queue_client=queue_client,
        pipeline_manager=pipeline_manager,
        queue_names=queue_names,
    )
    graph_worker = GraphWorker(
        queue_client=queue_client,
        pipeline_manager=pipeline_manager,
        queue_names=queue_names,
    )

    await asyncio.gather(
        consume_forever(queue_name=queue_names["parse"], handler=parse_worker.handle),
        consume_forever(queue_name=queue_names["index"], handler=index_worker.handle),
        consume_forever(queue_name=queue_names["graph"], handler=graph_worker.handle),
    )


__all__ = [
    "consume_forever",
    "initialize_worker_runtime",
    "main",
    "run_package_a_ingestion_worker_forever",
]


if __name__ == "__main__":
    asyncio.run(main())
