from __future__ import annotations

import asyncio
from uuid import uuid4

from zuno.platform.queue import RabbitMQTopology, RabbitMQTransport

RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"


def _topology() -> RabbitMQTopology:
    suffix = uuid4().hex
    return RabbitMQTopology(
        exchange=f"phase04.backlog.exchange.{suffix}",
        queue=f"phase04.backlog.queue.{suffix}",
        routing_key=f"phase04.backlog.route.{suffix}",
        dead_letter_exchange=f"phase04.backlog.dlx.{suffix}",
        dead_letter_queue=f"phase04.backlog.dlq.{suffix}",
        dead_letter_routing_key=f"phase04.backlog.dead.{suffix}",
    )


async def _verify() -> list[str]:
    errors: list[str] = []
    topology = _topology()
    async with RabbitMQTransport(RABBITMQ_URL) as transport:
        await transport.declare_topology(topology)
        try:
            initial_depth = await transport.queue_depth(topology.queue)
            if initial_depth != 0:
                errors.append(f"RabbitMQ test queue was not empty initially: {initial_depth}")

            for index in range(5):
                await transport.publish(
                    topology,
                    message_id=f"phase04-backlog-{index}",
                    payload={"scenario": "backlog", "index": index},
                    tenant_id="tenant-phase04",
                    trace_id=f"trace-phase04-backlog-{index}",
                )

            backlog_depth = await transport.queue_depth(topology.queue)
            if backlog_depth != 5:
                errors.append(f"RabbitMQ backlog depth mismatch after publish: {backlog_depth}")

            for index in range(5):
                delivery = await transport.get(topology.queue)
                if delivery is None:
                    errors.append(f"RabbitMQ missing backlog message at index {index}")
                    break
                await delivery.ack()
                expected_depth = 4 - index
                depth = await transport.queue_depth(topology.queue)
                if depth != expected_depth:
                    errors.append(f"RabbitMQ backlog depth mismatch after ACK {index}: {depth}")

            final_depth = await transport.queue_depth(topology.queue)
            if final_depth != 0:
                errors.append(f"RabbitMQ backlog depth did not drain to zero: {final_depth}")
        finally:
            await transport.delete_topology(topology)
    return errors


def verify_phase04_rabbitmq_backlog() -> list[str]:
    return asyncio.run(_verify())


def main() -> int:
    errors = verify_phase04_rabbitmq_backlog()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 RabbitMQ backlog verification failed.")
        return 1
    print("PHASE04 RabbitMQ backlog verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
