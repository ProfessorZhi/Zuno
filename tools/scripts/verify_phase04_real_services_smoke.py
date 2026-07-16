from __future__ import annotations

import hashlib
import json
import subprocess
import time
from io import BytesIO
from pathlib import Path
from uuid import uuid4

import psycopg
from minio import Minio
from minio.error import S3Error

REPO_ROOT = Path(__file__).resolve().parents[2]
POSTGRES_DSN = "postgresql://postgres:postgres@localhost:5432/zuno"
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=False)


def _wait_for_rabbitmq_health(timeout_seconds: int = 90) -> list[str]:
    deadline = time.time() + timeout_seconds
    last_status = ""
    while time.time() < deadline:
        result = _run(["docker", "inspect", "-f", "{{.State.Health.Status}}", "zuno-rabbitmq"])
        last_status = result.stdout.strip() or result.stderr.strip()
        if result.returncode == 0 and last_status == "healthy":
            return []
        time.sleep(1)
    return [f"RabbitMQ container did not become healthy: {last_status}"]


def _verify_postgres_schema_backup() -> list[str]:
    errors: list[str] = []
    try:
        with psycopg.connect(POSTGRES_DSN, connect_timeout=3) as conn:
            with conn.cursor() as cur:
                cur.execute("select count(*) from information_schema.tables where table_schema = 'public'")
                table_count = cur.fetchone()[0]
    except Exception as exc:
        return [f"PostgreSQL connection/query failed: {exc}"]
    if table_count < 6:
        errors.append(f"PostgreSQL public table count too low: {table_count}")

    dump = _run(
        [
            "docker",
            "exec",
            "zuno-postgres",
            "pg_dump",
            "-U",
            "postgres",
            "-d",
            "zuno",
            "--schema-only",
        ]
    )
    if dump.returncode != 0:
        errors.append(f"PostgreSQL schema backup failed: {dump.stderr.strip()}")
    elif "infra_outbox_events" not in dump.stdout or "infra_checkpoints" not in dump.stdout:
        errors.append("PostgreSQL schema backup missing infrastructure tables")
    return errors


def _verify_rabbitmq_publish_get() -> list[str]:
    health_errors = _wait_for_rabbitmq_health()
    if health_errors:
        return health_errors
    queue = f"phase04-smoke-{uuid4().hex}"
    payload = json.dumps({"phase": "PHASE04", "message_id": queue}, sort_keys=True)
    declare = _run(
        [
            "docker",
            "exec",
            "zuno-rabbitmq",
            "rabbitmqadmin",
            "--username=guest",
            "--password=guest",
            "declare",
            "queue",
            f"name={queue}",
            "durable=true",
        ]
    )
    if declare.returncode != 0:
        return [f"RabbitMQ queue declare failed: {declare.stderr.strip()}"]
    publish = _run(
        [
            "docker",
            "exec",
            "zuno-rabbitmq",
            "rabbitmqadmin",
            "--username=guest",
            "--password=guest",
            "publish",
            "exchange=amq.default",
            f"routing_key={queue}",
            f"payload={payload}",
        ]
    )
    if publish.returncode != 0:
        return [f"RabbitMQ publish failed: {publish.stderr.strip()}"]
    get = _run(
        [
            "docker",
            "exec",
            "zuno-rabbitmq",
            "rabbitmqadmin",
            "--username=guest",
            "--password=guest",
            "get",
            f"queue={queue}",
            "ackmode=ack_requeue_false",
            "count=1",
        ]
    )
    errors: list[str] = []
    if get.returncode != 0:
        errors.append(f"RabbitMQ get failed: {get.stderr.strip()}")
    elif payload not in get.stdout:
        errors.append("RabbitMQ get did not return published payload")
    _run(
        [
            "docker",
            "exec",
            "zuno-rabbitmq",
            "rabbitmqadmin",
            "--username=guest",
            "--password=guest",
            "delete",
            "queue",
            f"name={queue}",
        ]
    )
    return errors


def _verify_minio_object_round_trip() -> list[str]:
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )
    bucket = f"phase04-smoke-{uuid4().hex}"
    object_name = "object.txt"
    payload = b"phase04-minio-smoke\n"
    expected_hash = hashlib.sha256(payload).hexdigest()
    errors: list[str] = []
    try:
        client.make_bucket(bucket)
        client.put_object(bucket, object_name, BytesIO(payload), length=len(payload))
        response = client.get_object(bucket, object_name)
        try:
            actual = response.read()
        finally:
            response.close()
            response.release_conn()
        if hashlib.sha256(actual).hexdigest() != expected_hash:
            errors.append("MinIO object round-trip hash mismatch")
        client.remove_object(bucket, object_name)
        client.remove_bucket(bucket)
    except S3Error as exc:
        errors.append(f"MinIO S3 operation failed: {exc}")
    except Exception as exc:
        errors.append(f"MinIO object round-trip failed: {exc}")
    return errors


def verify_phase04_real_services_smoke() -> list[str]:
    errors: list[str] = []
    errors.extend(_verify_postgres_schema_backup())
    errors.extend(_verify_rabbitmq_publish_get())
    errors.extend(_verify_minio_object_round_trip())
    return errors


def main() -> int:
    errors = verify_phase04_real_services_smoke()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 real service smoke verification failed.")
        return 1
    print("PHASE04 real service smoke verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
