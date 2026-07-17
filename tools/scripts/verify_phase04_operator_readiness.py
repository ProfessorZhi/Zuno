from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from sqlalchemy import text

from zuno.platform.contracts import canonical_sha256
from zuno.platform.database.foundation import (
    InfrastructureUnitOfWork,
    create_foundation_engine,
)
from zuno.platform.database.runtime import PostgresRuntime, PostgresRuntimeConfig
from zuno.platform.queue.rabbitmq import RabbitMQTopology, RabbitMQTransport
from zuno.platform.storage import MinioObjectStore

POSTGRES_SQLALCHEMY_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/zuno"
POSTGRES_ASYNC_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/zuno"
RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"

REPO_ROOT = Path(__file__).resolve().parents[2]


def _utc_now() -> str:
    return datetime.now(tz=UTC).isoformat()


def _topology(marker: str) -> RabbitMQTopology:
    return RabbitMQTopology(
        exchange=f"phase04.operator.{marker}",
        queue=f"phase04.operator.{marker}",
        routing_key=f"phase04.operator.{marker}",
        dead_letter_exchange=f"phase04.operator.dlx.{marker}",
        dead_letter_queue=f"phase04.operator.dlq.{marker}",
        dead_letter_routing_key=f"phase04.operator.dlq.{marker}",
    )


def _postgres_runtime() -> PostgresRuntime:
    return PostgresRuntime(
        PostgresRuntimeConfig(
            sync_url=POSTGRES_SQLALCHEMY_URL,
            async_url=POSTGRES_ASYNC_URL,
            pool_size=2,
            max_overflow=1,
            pool_timeout_seconds=2,
            statement_timeout_ms=5_000,
            lock_timeout_ms=1_000,
        )
    )


def _store() -> MinioObjectStore:
    return MinioObjectStore(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
    )


def _insert_operator_outbox_marker(marker: str, trace_id: str) -> str:
    engine = create_foundation_engine(POSTGRES_SQLALCHEMY_URL)
    try:
        with InfrastructureUnitOfWork(engine, tenant_id="phase04-operator") as repo:
            return repo.enqueue_outbox(
                aggregate_id=f"phase04-operator-{marker}",
                topic="phase04.operator.readiness",
                payload={
                    "marker": marker,
                    "trace_id": trace_id,
                    "operator_probe": True,
                },
                idempotency_key=f"phase04-operator-{marker}",
            )
    finally:
        engine.dispose()


def _postgres_backlog(marker_event_id: str) -> dict[str, Any]:
    engine = create_foundation_engine(POSTGRES_SQLALCHEMY_URL)
    try:
        with InfrastructureUnitOfWork(engine) as repo:
            backlog = repo.outbox_backlog(topic="phase04.operator.readiness")
        return {
            "ready": backlog.ready,
            "delayed": backlog.delayed,
            "claimed": backlog.claimed,
            "dead_letter": backlog.dead_letter,
            "oldest_pending_at": (
                None
                if backlog.oldest_pending_at is None
                else backlog.oldest_pending_at.isoformat()
            ),
            "marker_event_id": marker_event_id,
        }
    finally:
        engine.dispose()


def _cleanup_postgres(marker: str, event_id: str) -> None:
    engine = create_foundation_engine(POSTGRES_SQLALCHEMY_URL)
    try:
        with engine.begin() as connection:
            connection.execute(
                text("DELETE FROM infra_outbox_events WHERE event_id = :event_id"),
                {"event_id": event_id},
            )
            connection.execute(
                text(
                    "DELETE FROM infra_inbox_messages "
                    "WHERE message_id = :message_id OR payload::text LIKE :marker"
                ),
                {
                    "message_id": f"phase04-operator-message-{marker}",
                    "marker": f"%{marker}%",
                },
            )
    finally:
        engine.dispose()


async def _rabbitmq_probe(marker: str, trace_id: str) -> dict[str, Any]:
    topology = _topology(marker)
    async with RabbitMQTransport(RABBITMQ_URL) as transport:
        await transport.declare_topology(topology)
        try:
            initial_depth = await transport.queue_depth(topology.queue)
            await transport.publish(
                topology,
                message_id=f"phase04-operator-message-{marker}",
                payload={"marker": marker, "trace_id": trace_id},
                tenant_id="phase04-operator",
                trace_id=trace_id,
            )
            after_publish_depth = await transport.queue_depth(topology.queue)
            delivery = await transport.get(topology.queue, timeout=5)
            if delivery is None:
                raise RuntimeError(
                    "operator RabbitMQ probe did not receive its marker message"
                )
            await delivery.ack()
            final_depth = await transport.queue_depth(topology.queue)
            dead_letter_depth = await transport.queue_depth(topology.dead_letter_queue)
            return {
                "queue": topology.queue,
                "initial_depth": initial_depth,
                "after_publish_depth": after_publish_depth,
                "final_depth": final_depth,
                "dead_letter_depth": dead_letter_depth,
                "message_trace_id": delivery.headers.get("trace_id"),
            }
        finally:
            await transport.delete_topology(topology)


def _minio_probe(marker: str, trace_id: str) -> dict[str, Any]:
    store = _store()
    bucket = f"phase04-operator-{marker}"
    object_name = "readiness/probe.json"
    payload = json.dumps(
        {"marker": marker, "trace_id": trace_id, "created_at": _utc_now()},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    try:
        staged = store.stage_object(
            bucket=bucket, object_name=object_name, content=payload
        )
        committed = store.commit_object(
            bucket=bucket,
            staged_object_name=staged.object_name,
            committed_object_name=object_name,
            expected_hash=staged.content_hash,
        )
        observed = store.read_object(bucket=bucket, object_name=object_name)
        return {
            "bucket": bucket,
            "object_name": object_name,
            "size_bytes": committed.size_bytes,
            "content_hash": committed.content_hash,
            "read_hash": canonical_sha256({"bytes": observed.hex()}),
            "raw_sha256_matches": observed == payload,
        }
    finally:
        store.remove_bucket_tree(bucket)


async def _operator_snapshot(marker: str) -> dict[str, Any]:
    trace_id = f"trace-phase04-operator-{marker}"
    event_id = _insert_operator_outbox_marker(marker, trace_id)
    runtime = _postgres_runtime()
    try:
        sync_health = runtime.sync_health()
        async_health = await runtime.async_health()
        postgres_backlog = _postgres_backlog(event_id)
        rabbitmq = await _rabbitmq_probe(marker, trace_id)
        minio = _minio_probe(marker, trace_id)
        dependencies = [
            _dependency_snapshot(
                name="postgresql",
                health=(
                    "healthy"
                    if sync_health.healthy and async_health.healthy
                    else "unhealthy"
                ),
                readiness=(
                    "ready" if sync_health.ready and async_health.ready else "not_ready"
                ),
                capacity={
                    "sync_pool_size": sync_health.pool_size,
                    "sync_checked_out": sync_health.checked_out,
                    "sync_overflow": sync_health.overflow,
                    "async_pool_size": async_health.pool_size,
                    "async_checked_out": async_health.checked_out,
                    "async_overflow": async_health.overflow,
                },
                backlog=postgres_backlog,
                failure_owner="Infrastructure/PostgreSQL Runtime",
                retry_owner="Infrastructure transaction retry boundary",
                recovery_owner="P04-T07 restore/runbook owner",
                evidence_ref="docs/evidence/phase04-postgres-session-runtime.md",
            ),
            _dependency_snapshot(
                name="rabbitmq",
                health="healthy",
                readiness=(
                    "ready" if rabbitmq["message_trace_id"] == trace_id else "not_ready"
                ),
                capacity={"declared_queue": rabbitmq["queue"]},
                backlog={
                    "initial_depth": rabbitmq["initial_depth"],
                    "after_publish_depth": rabbitmq["after_publish_depth"],
                    "final_depth": rabbitmq["final_depth"],
                    "dead_letter_depth": rabbitmq["dead_letter_depth"],
                },
                failure_owner="Infrastructure/RabbitMQ Transport",
                retry_owner="Outbox publisher retry policy",
                recovery_owner="P04-T07 failure recovery runbook owner",
                evidence_ref="docs/evidence/phase04-rabbitmq-transport.md",
            ),
            _dependency_snapshot(
                name="minio",
                health="healthy",
                readiness="ready" if minio["raw_sha256_matches"] else "not_ready",
                capacity={
                    "probe_object_size_bytes": minio["size_bytes"],
                    "bucket": minio["bucket"],
                },
                backlog={"staging_or_restore_queue": "not_applicable_for_probe"},
                failure_owner="Infrastructure/Object Store",
                retry_owner="Object reconciliation owner",
                recovery_owner="P04-T07 backup/restore runbook owner",
                evidence_ref="docs/evidence/phase04-minio-object-store.md",
            ),
        ]
        return {
            "schema_version": "phase04.operator_readiness.v1",
            "event_type": "phase04_operator_readiness_snapshot",
            "created_at": _utc_now(),
            "trace_id": trace_id,
            "tenant_id": "phase04-operator",
            "dependencies": dependencies,
            "eval_verdict": None,
            "boundary": "operator telemetry only; this snapshot does not score eval quality or domain success",
        }
    finally:
        await runtime.close()
        _cleanup_postgres(marker, event_id)


def _dependency_snapshot(
    *,
    name: str,
    health: str,
    readiness: str,
    capacity: dict[str, Any],
    backlog: dict[str, Any],
    failure_owner: str,
    retry_owner: str,
    recovery_owner: str,
    evidence_ref: str,
) -> dict[str, Any]:
    return {
        "name": name,
        "health": health,
        "readiness": readiness,
        "capacity": capacity,
        "backlog": backlog,
        "failure_owner": failure_owner,
        "retry_owner": retry_owner,
        "recovery_owner": recovery_owner,
        "evidence_ref": evidence_ref,
    }


def _validate_snapshot(snapshot: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if snapshot.get("schema_version") != "phase04.operator_readiness.v1":
        errors.append("operator snapshot schema version is missing")
    if not str(snapshot.get("trace_id", "")).startswith("trace-phase04-operator-"):
        errors.append("operator snapshot trace correlation is missing")
    if snapshot.get("eval_verdict") is not None:
        errors.append("operator telemetry must not produce an eval verdict")
    dependencies = snapshot.get("dependencies")
    if not isinstance(dependencies, list) or {
        item.get("name") for item in dependencies
    } != {
        "postgresql",
        "rabbitmq",
        "minio",
    }:
        errors.append("operator snapshot does not cover PostgreSQL, RabbitMQ and MinIO")
        return errors
    for dependency in dependencies:
        name = dependency.get("name", "<unknown>")
        if dependency.get("health") != "healthy":
            errors.append(f"{name} health was not healthy")
        if dependency.get("readiness") != "ready":
            errors.append(f"{name} readiness was not ready")
        for key in ["capacity", "backlog"]:
            if not isinstance(dependency.get(key), dict) or not dependency[key]:
                errors.append(f"{name} {key} metrics are missing")
        for key in ["failure_owner", "retry_owner", "recovery_owner", "evidence_ref"]:
            if not str(dependency.get(key, "")).strip():
                errors.append(f"{name} {key} is missing")
    return errors


def verify_phase04_operator_readiness() -> list[str]:
    marker = uuid4().hex
    try:
        snapshot = asyncio.run(_operator_snapshot(marker))
    except Exception as exc:
        return [f"operator readiness probe failed: {type(exc).__name__}: {exc}"]
    return _validate_snapshot(snapshot)


def main() -> int:
    errors = verify_phase04_operator_readiness()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 operator readiness verification failed.")
        return 1
    print("PHASE04 operator readiness verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
