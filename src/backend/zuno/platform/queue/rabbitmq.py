from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Any

import aio_pika
from aiormq.exceptions import AMQPConnectionError
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustChannel, AbstractRobustConnection


@dataclass(frozen=True, slots=True)
class RabbitMQTopology:
    exchange: str
    queue: str
    routing_key: str
    dead_letter_exchange: str
    dead_letter_queue: str
    dead_letter_routing_key: str


@dataclass(slots=True)
class RabbitMQDelivery:
    message_id: str
    payload: dict[str, Any]
    headers: dict[str, Any]
    redelivered: bool
    _message: AbstractIncomingMessage

    async def ack(self) -> None:
        await self._message.ack()

    async def nack(self, *, requeue: bool) -> None:
        await self._message.nack(requeue=requeue)

    async def reject(self, *, requeue: bool = False) -> None:
        await self._message.reject(requeue=requeue)


class RabbitMQTransport:
    def __init__(self, url: str) -> None:
        self.url = url
        self._connection: AbstractRobustConnection | None = None
        self._channel: AbstractRobustChannel | None = None

    async def __aenter__(self) -> RabbitMQTransport:
        await self.connect()
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        await self.close()

    async def connect(self, *, timeout_seconds: int = 90) -> None:
        deadline = time.time() + timeout_seconds
        last_error: Exception | None = None
        while time.time() < deadline:
            try:
                self._connection = await aio_pika.connect_robust(self.url)
                self._channel = await self._connection.channel(publisher_confirms=True)
                return
            except (AMQPConnectionError, ConnectionError, OSError) as exc:
                last_error = exc
                await self.close()
                await asyncio.sleep(1)
        raise TimeoutError(f"RabbitMQTransport did not connect before deadline: {last_error}")

    async def close(self) -> None:
        if self._channel is not None and not self._channel.is_closed:
            await self._channel.close()
        if self._connection is not None and not self._connection.is_closed:
            await self._connection.close()

    @property
    def channel(self) -> AbstractRobustChannel:
        if self._channel is None:
            raise RuntimeError("RabbitMQTransport is not connected")
        return self._channel

    async def declare_topology(self, topology: RabbitMQTopology) -> None:
        channel = self.channel
        await channel.declare_exchange(topology.dead_letter_exchange, aio_pika.ExchangeType.DIRECT, durable=True)
        await channel.declare_queue(topology.dead_letter_queue, durable=True)
        dead_letter_exchange = await channel.get_exchange(topology.dead_letter_exchange)
        dead_letter_queue = await channel.get_queue(topology.dead_letter_queue)
        await dead_letter_queue.bind(dead_letter_exchange, routing_key=topology.dead_letter_routing_key)

        await channel.declare_exchange(topology.exchange, aio_pika.ExchangeType.DIRECT, durable=True)
        await channel.declare_queue(
            topology.queue,
            durable=True,
            arguments={
                "x-dead-letter-exchange": topology.dead_letter_exchange,
                "x-dead-letter-routing-key": topology.dead_letter_routing_key,
            },
        )
        exchange = await channel.get_exchange(topology.exchange)
        queue = await channel.get_queue(topology.queue)
        await queue.bind(exchange, routing_key=topology.routing_key)

    async def delete_topology(self, topology: RabbitMQTopology) -> None:
        channel = self.channel
        for queue_name in [topology.queue, topology.dead_letter_queue]:
            queue = await channel.get_queue(queue_name, ensure=False)
            if queue is not None:
                await queue.delete(if_unused=False, if_empty=False)
        for exchange_name in [topology.exchange, topology.dead_letter_exchange]:
            exchange = await channel.get_exchange(exchange_name, ensure=False)
            if exchange is not None:
                await exchange.delete(if_unused=False)

    async def publish(
        self,
        topology: RabbitMQTopology,
        *,
        message_id: str,
        payload: dict[str, Any],
        tenant_id: str,
        trace_id: str,
        version: str = "v1",
    ) -> None:
        exchange = await self.channel.get_exchange(topology.exchange)
        message = aio_pika.Message(
            body=json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            message_id=message_id,
            headers={
                "tenant_id": tenant_id,
                "trace_id": trace_id,
                "message_version": version,
            },
        )
        await exchange.publish(message, routing_key=topology.routing_key)

    async def replay_dead_letter(
        self,
        topology: RabbitMQTopology,
        delivery: RabbitMQDelivery,
        *,
        replay_trace_id: str,
    ) -> None:
        exchange = await self.channel.get_exchange(topology.exchange)
        headers = dict(delivery.headers)
        headers["trace_id"] = replay_trace_id
        headers["replayed_from_dlq"] = True
        message = aio_pika.Message(
            body=json.dumps(delivery.payload, sort_keys=True, separators=(",", ":")).encode("utf-8"),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            message_id=delivery.message_id,
            headers=headers,
        )
        await exchange.publish(message, routing_key=topology.routing_key)

    async def get(self, queue_name: str, *, timeout: float = 5.0) -> RabbitMQDelivery | None:
        queue = await self.channel.get_queue(queue_name)
        message = await queue.get(timeout=timeout, fail=False)
        if message is None:
            return None
        return RabbitMQDelivery(
            message_id=message.message_id or "",
            payload=json.loads(message.body.decode("utf-8")),
            headers=dict(message.headers or {}),
            redelivered=bool(message.redelivered),
            _message=message,
        )
