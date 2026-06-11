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


async def main():
    await initialize_worker_runtime()

    if not (app_settings.rabbitmq or {}).get("enabled"):
        raise RuntimeError("RabbitMQ worker started while rabbitmq.enabled is false")

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


__all__ = ["consume_forever", "initialize_worker_runtime", "main"]


if __name__ == "__main__":
    asyncio.run(main())
