from __future__ import annotations

import asyncio
from uuid import uuid4

from zuno.platform.queue import RabbitMQTopology, RabbitMQTransport

RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"


def _topology() -> RabbitMQTopology:
    suffix = uuid4().hex
    return RabbitMQTopology(
        exchange=f"phase04.verify.exchange.{suffix}",
        queue=f"phase04.verify.queue.{suffix}",
        routing_key=f"phase04.verify.route.{suffix}",
        dead_letter_exchange=f"phase04.verify.dlx.{suffix}",
        dead_letter_queue=f"phase04.verify.dlq.{suffix}",
        dead_letter_routing_key=f"phase04.verify.dead.{suffix}",
    )


async def _verify() -> list[str]:
    errors: list[str] = []
    topology = _topology()
    async with RabbitMQTransport(RABBITMQ_URL) as transport:
        await transport.declare_topology(topology)
        try:
            await transport.publish(
                topology,
                message_id="phase04-confirm-redelivery",
                payload={"scenario": "redelivery"},
                tenant_id="tenant-phase04",
                trace_id="trace-phase04-redelivery",
            )
            first = await transport.get(topology.queue)
            if first is None:
                errors.append("RabbitMQ published message was not delivered")
            else:
                await first.nack(requeue=True)
                redelivered = await transport.get(topology.queue)
                if redelivered is None:
                    errors.append("RabbitMQ requeued message was not delivered")
                else:
                    if not redelivered.redelivered:
                        errors.append("RabbitMQ redelivery flag was not set")
                    if redelivered.headers.get("tenant_id") != "tenant-phase04":
                        errors.append("RabbitMQ tenant header was not preserved")
                    await redelivered.ack()

            await transport.publish(
                topology,
                message_id="phase04-poison",
                payload={"scenario": "dlq"},
                tenant_id="tenant-phase04",
                trace_id="trace-phase04-dlq",
            )
            poison = await transport.get(topology.queue)
            if poison is None:
                errors.append("RabbitMQ poison message was not delivered")
            else:
                await poison.reject(requeue=False)
                dead_letter = await transport.get(topology.dead_letter_queue)
                if dead_letter is None:
                    errors.append("RabbitMQ rejected message did not reach DLQ")
                else:
                    if dead_letter.message_id != "phase04-poison":
                        errors.append("RabbitMQ DLQ message id changed")
                    await dead_letter.ack()
        finally:
            await transport.delete_topology(topology)
    return errors


def verify_phase04_rabbitmq_transport() -> list[str]:
    return asyncio.run(_verify())


def main() -> int:
    errors = verify_phase04_rabbitmq_transport()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 RabbitMQ transport verification failed.")
        return 1
    print("PHASE04 RabbitMQ transport verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
