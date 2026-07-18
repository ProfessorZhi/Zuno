from __future__ import annotations

import asyncio
import hashlib
import subprocess
import time
from pathlib import Path
from uuid import uuid4

import psycopg
from importlib.util import find_spec
from langgraph.checkpoint.base import empty_checkpoint
from langgraph.checkpoint.postgres import PostgresSaver
from sqlalchemy import text

from zuno.platform.database.foundation import InfrastructureUnitOfWork, create_foundation_engine
from zuno.platform.database.runtime import PostgresRuntime, PostgresRuntimeConfig
from zuno.platform.queue.outbox import PostgresOutboxRabbitMQPublisher
from zuno.platform.queue.rabbitmq import RabbitMQTopology, RabbitMQTransport
from zuno.platform.storage import MinioObjectStore

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICES = ("zuno-postgres", "zuno-rabbitmq", "zuno-minio")
POSTGRES_DSN = "postgresql://postgres:postgres@localhost:5432/zuno"
POSTGRES_SYNC_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/zuno"
POSTGRES_ASYNC_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/zuno"
RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
TENANT_ID = "tenant-phase04-combined-fault"


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=False)


def _wait_for_healthy(timeout_seconds: int = 120) -> list[str]:
    deadline = time.time() + timeout_seconds
    statuses: dict[str, str] = {}
    while time.time() < deadline:
        statuses = {}
        for service in SERVICES:
            result = _run(["docker", "inspect", "-f", "{{.State.Health.Status}}", service])
            statuses[service] = result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
        if all(status == "healthy" for status in statuses.values()):
            return []
        time.sleep(1)
    return [f"combined services did not become healthy: {statuses}"]


def _start_services() -> list[str]:
    start = _run(["docker", "start", *SERVICES])
    if start.returncode != 0:
        return [f"combined services failed to start: {start.stderr.strip()}"]
    return _wait_for_healthy()


def _topology(marker: str) -> RabbitMQTopology:
    prefix = f"phase04.combined.{marker}"
    return RabbitMQTopology(
        exchange=f"{prefix}.exchange",
        queue=f"{prefix}.queue",
        routing_key=f"{prefix}.route",
        dead_letter_exchange=f"{prefix}.dlx",
        dead_letter_queue=f"{prefix}.dlq",
        dead_letter_routing_key=f"{prefix}.dead",
    )


def _store() -> MinioObjectStore:
    return MinioObjectStore(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
    )


def _official_checkpoint(marker: str, *, version: str) -> dict[str, object]:
    checkpoint = empty_checkpoint()
    checkpoint["channel_values"] = {
        "marker": marker,
        "fault_scope": "phase04-combined-service-fault",
    }
    checkpoint["channel_versions"] = {"marker": version}
    checkpoint["versions_seen"] = {"phase04": {"marker": version}}
    checkpoint["updated_channels"] = ["marker"]
    return checkpoint


def _seed_official_checkpointer(marker: str) -> dict[str, object]:
    thread_id = f"phase04-combined-official-{marker}"
    namespace = "phase04-combined-fault"
    with PostgresSaver.from_conn_string(POSTGRES_DSN) as saver:
        saver.setup()
        config = {"configurable": {"thread_id": thread_id, "checkpoint_ns": namespace}}
        version = saver.get_next_version(None, None)
        saved = saver.put(
            config,
            _official_checkpoint(marker, version=version),
            {"source": "phase04-combined-service-fault", "step": "pre-fault"},
            {"marker": version},
        )
        saver.put_writes(
            saved,
            [("combined_fault", {"marker": marker, "thread_id": thread_id})],
            f"combined-task-{marker}",
        )
    return {
        "thread_id": thread_id,
        "namespace": namespace,
        "checkpoint_id": str(saved["configurable"]["checkpoint_id"]),
        "config": saved,
    }


def _verify_official_checkpointer_recovery(
    errors: list[str],
    *,
    marker: str,
    official_seed: dict[str, object],
) -> None:
    with PostgresSaver.from_conn_string(POSTGRES_DSN) as saver:
        restored = saver.get_tuple(official_seed["config"])
        listed = list(
            saver.list(
                {
                    "configurable": {
                        "thread_id": str(official_seed["thread_id"]),
                        "checkpoint_ns": str(official_seed["namespace"]),
                    }
                },
                limit=5,
            )
        )
        delta_history = saver.get_delta_channel_history(
            config=official_seed["config"],
            channels=["marker"],
        )
    if restored is None:
        errors.append("official Checkpointer checkpoint did not survive combined outage")
        return
    if restored.checkpoint["channel_values"].get("marker") != marker:
        errors.append("official Checkpointer restored wrong marker after combined outage")
    if str(restored.config["configurable"]["checkpoint_id"]) != str(official_seed["checkpoint_id"]):
        errors.append("official Checkpointer restored wrong checkpoint id after combined outage")
    if len(listed) != 1:
        errors.append(f"official Checkpointer history changed across combined outage: {len(listed)}")
    if "marker" not in delta_history:
        errors.append("official Checkpointer delta history missing after combined outage")


def _runtime() -> PostgresRuntime:
    return PostgresRuntime(
        PostgresRuntimeConfig(
            sync_url=POSTGRES_SYNC_URL,
            async_url=POSTGRES_ASYNC_URL,
            pool_size=2,
            max_overflow=1,
            pool_timeout_seconds=2,
            statement_timeout_ms=5_000,
            lock_timeout_ms=1_000,
        )
    )


def _seed_database(marker: str, object_ref: str, content: bytes) -> tuple[str, str]:
    engine = create_foundation_engine(POSTGRES_SYNC_URL)
    try:
        with InfrastructureUnitOfWork(engine, tenant_id=TENANT_ID) as repo:
            event_id = repo.enqueue_outbox(
                aggregate_id=f"combined-fault-{marker}",
                topic="phase04.combined.recovery",
                payload={"marker": marker, "object_ref": object_ref},
                idempotency_key=f"combined-fault-{marker}",
            )
            manifest_hash = repo.put_object_manifest(
                object_ref=object_ref,
                content=content,
                owner="phase04-combined-fault",
                visibility="visible",
            )
            repo.save_checkpoint(
                thread_id=f"combined-thread-{marker}",
                checkpoint_id=f"combined-checkpoint-{marker}",
                generation=1,
                state={"marker": marker, "event_id": event_id, "object_ref": object_ref},
                owner="phase04-combined-fault",
            )
        return event_id, manifest_hash
    finally:
        engine.dispose()


def _verify_postgres_unavailable(errors: list[str]) -> None:
    try:
        with psycopg.connect(POSTGRES_DSN, connect_timeout=1):
            errors.append("PostgreSQL accepted a new connection during combined outage")
    except psycopg.OperationalError:
        pass


async def _verify_rabbitmq_unavailable(errors: list[str]) -> None:
    transport = RabbitMQTransport(RABBITMQ_URL, robust=False)
    try:
        await transport.connect(timeout_seconds=2)
        errors.append("RabbitMQ accepted a new connection during combined outage")
    except TimeoutError:
        pass
    finally:
        await transport.close()


def _verify_minio_unavailable(
    errors: list[str],
    store: MinioObjectStore,
    *,
    bucket: str,
    object_name: str,
) -> None:
    try:
        store.read_object(bucket=bucket, object_name=object_name)
        errors.append("MinIO returned an object during combined outage")
    except Exception:
        pass


async def _verify_recovery(
    errors: list[str],
    *,
    marker: str,
    event_id: str,
    manifest_hash: str,
    content: bytes,
    bucket: str,
    object_name: str,
    topology: RabbitMQTopology,
    official_seed: dict[str, object],
) -> tuple[PostgresRuntime, RabbitMQTransport]:
    runtime = _runtime()
    transport = RabbitMQTransport(RABBITMQ_URL)
    try:
        sync_health = runtime.sync_health()
        async_health = await runtime.async_health()
        if not sync_health.ready or not async_health.ready:
            errors.append("new PostgresRuntime was not ready after combined service recovery")

        await transport.connect()
        await transport.declare_topology(topology)
        durable = await transport.get(topology.queue, timeout=10)
        if durable is None or durable.message_id != f"pre-fault-{marker}":
            errors.append("RabbitMQ durable pre-fault message was not recovered")
        else:
            await durable.ack()

        publisher = PostgresOutboxRabbitMQPublisher(
            engine=runtime.sync_engine,
            transport=transport,
            topology=topology,
            worker_id=f"combined-publisher-{marker}",
            tenant_id=TENANT_ID,
            trace_id=f"combined-trace-{marker}",
        )
        published = await publisher.publish_event(event_id=event_id)
        if published.event_id != event_id:
            errors.append("recovered Outbox publisher returned the wrong event")

        delivery = await transport.get(topology.queue, timeout=10)
        if delivery is None or delivery.message_id != event_id:
            errors.append("recovered Outbox event did not reach RabbitMQ")
        else:
            with InfrastructureUnitOfWork(runtime.sync_engine, tenant_id=TENANT_ID) as repo:
                receipt = repo.record_inbox_receipt(
                    consumer="phase04-combined-recovery",
                    message_id=delivery.message_id,
                    payload=delivery.payload,
                )
                checkpoint = repo.latest_checkpoint(thread_id=f"combined-thread-{marker}")
            if not receipt.first_seen or receipt.status != "received":
                errors.append("recovered RabbitMQ delivery did not create one durable Inbox receipt")
            if checkpoint is None or checkpoint["state"].get("marker") != marker:
                errors.append("PostgreSQL checkpoint primitive did not survive combined outage")
            await delivery.ack()

        with runtime.sync_engine.connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT event.status, manifest.content_hash, manifest.visibility
                    FROM infra_outbox_events AS event
                    JOIN infra_object_manifests AS manifest ON manifest.object_ref = :object_ref
                    WHERE event.event_id = :event_id
                    """
                ),
                {
                    "event_id": event_id,
                    "object_ref": f"s3://{bucket}/{object_name}",
                },
            ).one_or_none()
        if row is None or tuple(row) != ("published", manifest_hash, "visible"):
            errors.append(f"PostgreSQL recovery reconciliation mismatch: {row!r}")

        recovered_content = _store().read_object(bucket=bucket, object_name=object_name)
        if recovered_content != content or hashlib.sha256(recovered_content).digest() != hashlib.sha256(content).digest():
            errors.append("MinIO committed object changed across combined outage")
        _verify_official_checkpointer_recovery(
            errors,
            marker=marker,
            official_seed=official_seed,
        )
    except Exception:
        await transport.close()
        await runtime.close()
        raise
    return runtime, transport


async def _cleanup(
    *,
    marker: str,
    event_id: str | None,
    bucket: str,
    topology: RabbitMQTopology,
    runtime: PostgresRuntime | None,
    transport: RabbitMQTransport | None,
    official_thread_id: str | None,
) -> list[str]:
    errors: list[str] = []
    if transport is None:
        transport = RabbitMQTransport(RABBITMQ_URL)
        try:
            await transport.connect(timeout_seconds=20)
            await transport.declare_topology(topology)
        except Exception as exc:
            errors.append(f"RabbitMQ cleanup connection failed: {type(exc).__name__}")
    if transport is not None:
        try:
            await transport.delete_topology(topology)
        except Exception as exc:
            errors.append(f"RabbitMQ topology cleanup failed: {type(exc).__name__}")
        finally:
            await transport.close()

    try:
        _store().remove_bucket_tree(bucket)
    except Exception as exc:
        errors.append(f"MinIO cleanup failed: {type(exc).__name__}")

    if event_id is not None:
        cleanup_runtime = runtime or _runtime()
        try:
            with cleanup_runtime.sync_engine.begin() as connection:
                connection.execute(
                    text(
                        "DELETE FROM infra_inbox_messages "
                        "WHERE consumer = 'phase04-combined-recovery' AND message_id = :event_id"
                    ),
                    {"event_id": event_id},
                )
                connection.execute(
                    text("DELETE FROM infra_outbox_events WHERE event_id = :event_id"),
                    {"event_id": event_id},
                )
                connection.execute(
                    text("DELETE FROM infra_object_manifests WHERE object_ref = :object_ref"),
                    {"object_ref": f"s3://{bucket}/committed/recovery.txt"},
                )
                connection.execute(
                    text("DELETE FROM infra_checkpoints WHERE thread_id = :thread_id"),
                    {"thread_id": f"combined-thread-{marker}"},
                )
        except Exception as exc:
            errors.append(f"PostgreSQL cleanup failed: {type(exc).__name__}")
        finally:
            if cleanup_runtime is not runtime:
                await cleanup_runtime.close()
    if runtime is not None:
        await runtime.close()
    if official_thread_id is not None:
        try:
            with PostgresSaver.from_conn_string(POSTGRES_DSN) as saver:
                saver.delete_thread(official_thread_id)
        except Exception as exc:
            errors.append(f"official Checkpointer cleanup failed: {type(exc).__name__}")
    return errors


async def _verify() -> list[str]:
    marker = uuid4().hex
    bucket = f"phase04-combined-{marker}"
    object_name = "committed/recovery.txt"
    object_ref = f"s3://{bucket}/{object_name}"
    content = f"phase04-combined:{marker}".encode("utf-8")
    topology = _topology(marker)
    errors: list[str] = []
    event_id: str | None = None
    runtime: PostgresRuntime | None = None
    recovered_transport: RabbitMQTransport | None = None
    official_seed: dict[str, object] | None = None
    services_stopped = False

    try:
        if find_spec("langgraph.checkpoint.postgres") is None:
            return ["official LangGraph PostgreSQL Checkpointer package is not importable"]
        store = _store()
        staged = store.stage_object(bucket=bucket, object_name=object_name, content=content)
        committed = store.commit_object(
            bucket=bucket,
            staged_object_name=staged.object_name,
            committed_object_name=object_name,
            expected_hash=staged.content_hash,
        )
        if committed.content_hash != hashlib.sha256(content).hexdigest():
            errors.append("MinIO pre-fault commit hash mismatch")

        event_id, manifest_hash = _seed_database(marker, object_ref, content)
        official_seed = _seed_official_checkpointer(marker)

        transport = RabbitMQTransport(RABBITMQ_URL)
        await transport.connect()
        await transport.declare_topology(topology)
        await transport.publish(
            topology,
            message_id=f"pre-fault-{marker}",
            payload={"kind": "pre-fault-durable", "marker": marker},
            tenant_id=TENANT_ID,
            trace_id=f"pre-fault-trace-{marker}",
        )
        await transport.close()

        stop = _run(["docker", "stop", "--time", "20", *SERVICES])
        services_stopped = True
        if stop.returncode != 0:
            errors.append(f"combined services failed to stop: {stop.stderr.strip()}")
        else:
            _verify_postgres_unavailable(errors)
            await _verify_rabbitmq_unavailable(errors)
            _verify_minio_unavailable(
                errors,
                store,
                bucket=bucket,
                object_name=object_name,
            )

        start_errors = _start_services()
        errors.extend(start_errors)
        services_stopped = bool(start_errors)
        if not start_errors:
            runtime, recovered_transport = await _verify_recovery(
                errors,
                marker=marker,
                event_id=event_id,
                manifest_hash=manifest_hash,
                content=content,
                bucket=bucket,
                object_name=object_name,
                topology=topology,
                official_seed=official_seed,
            )
    except Exception as exc:
        errors.append(f"combined service fault drill failed: {type(exc).__name__}: {exc}")
    finally:
        if services_stopped:
            errors.extend(_start_services())
        if not _wait_for_healthy(timeout_seconds=30):
            errors.extend(
                await _cleanup(
                    marker=marker,
                    event_id=event_id,
                    bucket=bucket,
                    topology=topology,
                    runtime=runtime,
                    transport=recovered_transport,
                    official_thread_id=(
                        None if official_seed is None else str(official_seed["thread_id"])
                    ),
                )
            )
        else:
            errors.append("combined services were not healthy enough to run cleanup")
    return errors


def verify_phase04_combined_service_fault() -> list[str]:
    return asyncio.run(_verify())


def main() -> int:
    errors = verify_phase04_combined_service_fault()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 combined service fault verification failed.")
        return 1
    print("PHASE04 combined service fault verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
