from __future__ import annotations

import socket
import subprocess
import time
from uuid import uuid4

from minio.error import S3Error

from zuno.platform.storage import MinioObjectStore

MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"


def _store() -> MinioObjectStore:
    return MinioObjectStore(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
    )


def _docker_restart_minio() -> str:
    result = subprocess.run(
        ["docker", "restart", "zuno-minio"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        if "is not running" in message:
            start = subprocess.run(
                ["docker", "start", "zuno-minio"],
                text=True,
                capture_output=True,
                check=False,
            )
            if start.returncode == 0:
                return start.stdout.strip()
        raise RuntimeError(message)
    return result.stdout.strip()


def _wait_for_minio_port(timeout_seconds: int = 90) -> None:
    deadline = time.time() + timeout_seconds
    last_error: OSError | None = None
    while time.time() < deadline:
        try:
            with socket.create_connection(("localhost", 9000), timeout=2):
                return
        except OSError as exc:
            last_error = exc
            time.sleep(1)
    raise TimeoutError(f"MinIO port did not recover: {last_error}")


def _wait_for_container_health(timeout_seconds: int = 90) -> None:
    deadline = time.time() + timeout_seconds
    last_status = ""
    while time.time() < deadline:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Health.Status}}", "zuno-minio"],
            text=True,
            capture_output=True,
            check=False,
        )
        last_status = result.stdout.strip() or result.stderr.strip()
        if result.returncode == 0 and last_status == "healthy":
            return
        time.sleep(1)
    raise TimeoutError(f"MinIO container did not become healthy: {last_status}")


def _wait_for_bucket(store: MinioObjectStore, bucket: str, timeout_seconds: int = 90) -> None:
    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            if store.client.bucket_exists(bucket):
                return
        except (S3Error, OSError) as exc:
            last_error = exc
        time.sleep(1)
    raise TimeoutError(f"MinIO bucket was not readable after restart: {last_error}")


def verify_phase04_minio_storage_restart() -> list[str]:
    errors: list[str] = []
    bucket = f"phase04-minio-restart-{uuid4().hex}"
    committed_name = "committed/restart.txt"
    restore_name = "_restore/restart.txt"
    content = b"phase04-minio-storage-restart"
    store = _store()
    try:
        staged = store.stage_object(bucket=bucket, object_name="workspace/restart.txt", content=content)
        committed = store.commit_object(
            bucket=bucket,
            staged_object_name=staged.object_name,
            committed_object_name=committed_name,
            expected_hash=staged.content_hash,
        )
        restore_point = store.create_restore_point(
            bucket=bucket,
            object_name=committed.object_name,
            restore_point_name=restore_name,
        )

        _docker_restart_minio()
        _wait_for_minio_port()
        _wait_for_container_health()

        restarted_store = _store()
        _wait_for_bucket(restarted_store, bucket)
        committed_bytes = restarted_store.read_object(bucket=bucket, object_name=committed.object_name)
        restore_bytes = restarted_store.read_object(bucket=bucket, object_name=restore_point.object_name)
        if committed_bytes != content:
            errors.append("MinIO committed object bytes changed after storage restart")
        if restore_bytes != content:
            errors.append("MinIO restore point bytes changed after storage restart")
        if committed.content_hash != restore_point.content_hash:
            errors.append("MinIO committed object and restore point hash diverged before restart")
    finally:
        _wait_for_minio_port()
        try:
            _store().remove_bucket_tree(bucket)
        except Exception as exc:  # cleanup failure should be visible but not hide verification errors
            errors.append(f"MinIO restart verifier cleanup failed: {exc}")
    return errors


def main() -> int:
    errors = verify_phase04_minio_storage_restart()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 MinIO storage restart verification failed.")
        return 1
    print("PHASE04 MinIO storage restart verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
