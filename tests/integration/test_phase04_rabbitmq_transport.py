from __future__ import annotations

import asyncio
from uuid import uuid4

from zuno.platform.queue import RabbitMQTopology, RabbitMQTransport

RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"


def _topology() -> RabbitMQTopology:
    suffix = uuid4().hex
    return RabbitMQTopology(
        exchange=f"phase04.exchange.{suffix}",
        queue=f"phase04.queue.{suffix}",
        routing_key=f"phase04.route.{suffix}",
        dead_letter_exchange=f"phase04.dlx.{suffix}",
        dead_letter_queue=f"phase04.dlq.{suffix}",
        dead_letter_routing_key=f"phase04.dead.{suffix}",
    )


def test_rabbitmq_transport_confirm_redelivery_and_dlq() -> None:
    asyncio.run(_verify_rabbitmq_transport_confirm_redelivery_and_dlq())


async def _verify_rabbitmq_transport_confirm_redelivery_and_dlq() -> None:
    topology = _topology()
    async with RabbitMQTransport(RABBITMQ_URL) as transport:
        await transport.declare_topology(topology)
        try:
            await transport.publish(
                topology,
                message_id="msg-redelivery",
                payload={"kind": "phase04", "attempt": 1},
                tenant_id="tenant-a",
                trace_id="trace-redelivery",
            )
            first = await transport.get(topology.queue)
            assert first is not None
            assert first.payload == {"kind": "phase04", "attempt": 1}
            assert first.headers["tenant_id"] == "tenant-a"
            assert first.headers["trace_id"] == "trace-redelivery"
            assert first.redelivered is False
            await first.nack(requeue=True)

            redelivered = await transport.get(topology.queue)
            assert redelivered is not None
            assert redelivered.message_id == "msg-redelivery"
            assert redelivered.redelivered is True
            await redelivered.ack()

            await transport.publish(
                topology,
                message_id="msg-poison",
                payload={"kind": "phase04", "poison": True},
                tenant_id="tenant-a",
                trace_id="trace-dlq",
            )
            poison = await transport.get(topology.queue)
            assert poison is not None
            await poison.reject(requeue=False)

            dead_letter = await transport.get(topology.dead_letter_queue)
            assert dead_letter is not None
            assert dead_letter.message_id == "msg-poison"
            assert dead_letter.payload == {"kind": "phase04", "poison": True}
            assert dead_letter.headers["message_version"] == "v1"
            await transport.replay_dead_letter(topology, dead_letter, replay_trace_id="trace-dlq-replay")
            await dead_letter.ack()

            replayed = await transport.get(topology.queue)
            assert replayed is not None
            assert replayed.message_id == "msg-poison"
            assert replayed.payload == {"kind": "phase04", "poison": True}
            assert replayed.headers["replayed_from_dlq"] is True
            assert replayed.headers["trace_id"] == "trace-dlq-replay"
            await replayed.ack()
        finally:
            await transport.delete_topology(topology)
