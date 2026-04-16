import json

from agentchat.settings import app_settings


def get_queue_names() -> dict[str, str]:
    config = app_settings.rabbitmq or {}
    return {
        "parse": config.get("parse_queue", "knowledge.parse"),
        "index": config.get("index_queue", "knowledge.index"),
        "graph": config.get("graph_queue", "knowledge.graph"),
    }


class QueueClient:
    def __init__(self, url: str | None = None):
        self.url = url or (app_settings.rabbitmq or {}).get("url", "")

    @classmethod
    def is_enabled(cls) -> bool:
        return bool((app_settings.rabbitmq or {}).get("enabled"))

    async def publish(self, queue_name: str, payload: dict):
        import aio_pika

        connection = await aio_pika.connect_robust(self.url)
        try:
            channel = await connection.channel()
            await channel.declare_queue(queue_name, durable=True)
            message = aio_pika.Message(
                body=json.dumps(payload).encode("utf-8"),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )
            await channel.default_exchange.publish(message, routing_key=queue_name)
            await channel.close()
        finally:
            await connection.close()

    async def consume_once(self, queue_name: str) -> dict | None:
        import aio_pika

        connection = await aio_pika.connect_robust(self.url)
        try:
            channel = await connection.channel()
            queue = await channel.declare_queue(queue_name, durable=True)
            message = await queue.get(fail=False)
            if message is None:
                await channel.close()
                return None
            async with message.process():
                payload = json.loads(message.body.decode("utf-8"))
            await channel.close()
            return payload
        finally:
            await connection.close()
