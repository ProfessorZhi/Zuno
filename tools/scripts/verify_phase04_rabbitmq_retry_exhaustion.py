from __future__ import annotations

import asyncio
from uuid import uuid4

from zuno.platform.queue import RabbitMQTopology, RabbitMQTransport

RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"


def _topology() -> RabbitMQTopology:
    suffix = uuid4().hex
    return RabbitMQTopology(
        exchange=f"phase04.retry.exchange.{suffix}",
        queue=f"phase04.retry.queue.{suffix}",
        routing_key=f"phase04.retry.route.{suffix}",
        dead_letter_exchange=f"phase04.retry.dlx.{suffix}",
        dead_letter_queue=f"phase04.retry.dlq.{suffix}",
        dead_letter_routing_key=f"phase04.retry.dead.{suffix}",
    )


async def _verify() -> list[str]:
    errors: list[str] = []
    topology = _topology()
    async with RabbitMQTransport(RABBITMQ_URL) as transport:
        await transport.declare_topology(topology)
        try:
            await transport.publish(
                topology,
                message_id="phase04-retry-exhaustion",
                payload={"scenario": "retry-exhaustion"},
                tenant_id="tenant-phase04",
                trace_id="trace-phase04-retry-start",
            )

            for expected_attempt in [1, 2, 3]:
                delivery = await transport.get(topology.queue)
                if delivery is None:
                    errors.append(f"RabbitMQ retry delivery missing for attempt {expected_attempt}")
                    break
                attempt = await transport.retry_or_dead_letter(
                    topology,
                    delivery,
                    max_attempts=3,
                    retry_trace_id=(
                        "trace-phase04-retry-exhausted"
                        if expected_attempt == 3
                        else f"trace-phase04-retry-{expected_attempt}"
                    ),
                )
                if attempt != expected_attempt:
                    errors.append(f"RabbitMQ retry attempt mismatch: {attempt!r} != {expected_attempt!r}")

                if expected_attempt == 2:
                    if delivery.headers.get("retry_attempt") != 1:
                        errors.append(f"RabbitMQ second delivery retry header mismatch: {delivery.headers!r}")
                    if delivery.headers.get("retry_exhausted") is not False:
                        errors.append(f"RabbitMQ retry exhausted header set too early: {delivery.headers!r}")
                if expected_attempt == 3:
                    if delivery.headers.get("retry_attempt") != 2:
                        errors.append(f"RabbitMQ final delivery retry header mismatch: {delivery.headers!r}")
                    if delivery.headers.get("tenant_id") != "tenant-phase04":
                        errors.append("RabbitMQ retry did not preserve tenant header")
                    break

            dead_letter = await transport.get(topology.dead_letter_queue)
            if dead_letter is None:
                errors.append("RabbitMQ retry exhausted message did not reach DLQ")
            else:
                if dead_letter.message_id != "phase04-retry-exhaustion":
                    errors.append("RabbitMQ retry exhausted message id changed")
                if dead_letter.payload != {"scenario": "retry-exhaustion"}:
                    errors.append("RabbitMQ retry exhausted payload changed")
                if dead_letter.headers.get("retry_attempt") != 3:
                    errors.append(f"RabbitMQ exhausted retry count mismatch: {dead_letter.headers!r}")
                if dead_letter.headers.get("retry_exhausted") is not True:
                    errors.append(f"RabbitMQ exhausted header missing: {dead_letter.headers!r}")
                if dead_letter.headers.get("trace_id") != "trace-phase04-retry-exhausted":
                    errors.append("RabbitMQ exhausted trace id was not applied")
                await dead_letter.ack()

            if await transport.queue_depth(topology.queue) != 0:
                errors.append("RabbitMQ retry main queue did not drain after exhaustion")
        finally:
            await transport.delete_topology(topology)
    return errors


def verify_phase04_rabbitmq_retry_exhaustion() -> list[str]:
    return asyncio.run(_verify())


def main() -> int:
    errors = verify_phase04_rabbitmq_retry_exhaustion()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 RabbitMQ retry exhaustion verification failed.")
        return 1
    print("PHASE04 RabbitMQ retry exhaustion verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
