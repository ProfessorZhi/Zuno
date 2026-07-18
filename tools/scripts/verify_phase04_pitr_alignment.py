from __future__ import annotations

import os
import shutil
import socket
import subprocess
import tempfile
import time
from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine, text

from zuno.platform.database.foundation import (
    InfrastructureUnitOfWork,
    create_foundation_engine,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
POSTGRES_IMAGE = os.environ.get("ZUNO_PITR_POSTGRES_IMAGE", "postgres:16")


def _run(command: list[str], *, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_ready(container: str, database: str = "zuno", timeout_seconds: int = 60) -> list[str]:
    deadline = time.monotonic() + timeout_seconds
    last = ""
    while time.monotonic() < deadline:
        result = _run(
            ["docker", "exec", container, "pg_isready", "-U", "postgres", "-d", database],
            timeout=10,
        )
        last = (result.stdout + result.stderr).strip()
        if result.returncode == 0:
            return []
        time.sleep(1)
    return [f"{container} did not become ready: {last}"]


def _write_alembic_config(path: Path, port: int) -> None:
    url = f"postgresql+psycopg://postgres:postgres@127.0.0.1:{port}/zuno"
    path.write_text(
        "\n".join(
            [
                "database:",
                f'  sync_endpoint: "{url}"',
                f'  async_endpoint: "{url.replace("+psycopg://", "+asyncpg://")}"',
                "  echo: false",
                "  pool_size: 2",
                "  max_overflow: 2",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _run_alembic_head(config_path: Path) -> list[str]:
    env = os.environ.copy()
    env["ZUNO_CONFIG"] = str(config_path)
    result = subprocess.run(
        ["alembic", "-c", "infra/db/alembic.ini", "upgrade", "head"],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=180,
        check=False,
    )
    if result.returncode != 0:
        return [f"alembic upgrade head failed: {result.stdout}{result.stderr}"]
    return []


def _start_primary(container: str, port: int) -> list[str]:
    command = (
        "export PATH=/usr/lib/postgresql/16/bin:$PATH && "
        "mkdir -p /var/lib/postgresql/wal_archive && "
        "chown -R postgres:postgres /var/lib/postgresql/wal_archive && "
        "exec docker-entrypoint.sh postgres "
        "-c wal_level=replica "
        "-c archive_mode=on "
        "-c archive_timeout=1s "
        "-c max_wal_senders=5 "
        "-c \"archive_command=cp %p /var/lib/postgresql/wal_archive/%f\""
    )
    result = _run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            container,
            "-e",
            "POSTGRES_PASSWORD=postgres",
            "-e",
            "POSTGRES_DB=zuno",
            "-p",
            f"127.0.0.1:{port}:5432",
            POSTGRES_IMAGE,
            "bash",
            "-lc",
            command,
        ],
        timeout=60,
    )
    if result.returncode != 0:
        return [f"primary container start failed: {result.stdout}{result.stderr}"]
    return _wait_ready(container)


def _take_basebackup(primary: str) -> list[str]:
    result = _run(
        [
            "docker",
            "exec",
            primary,
            "bash",
            "-lc",
            "rm -rf /tmp/basebackup && "
            "PGPASSWORD=postgres pg_basebackup "
            "-h 127.0.0.1 -U postgres -D /tmp/basebackup -X stream -Fp",
        ],
        timeout=180,
    )
    if result.returncode != 0:
        return [f"pg_basebackup failed: {result.stdout}{result.stderr}"]
    return []


def _seed_target_window(port: int, marker: str) -> tuple[list[str], str, str]:
    errors: list[str] = []
    url = f"postgresql+psycopg://postgres:postgres@127.0.0.1:{port}/zuno"
    engine = create_foundation_engine(url, pool_size=2, max_overflow=2)
    recovery_point = f"phase04-pitr-rp-{marker}"
    recovery_set_id = f"phase04-pitr-set-{marker}"
    component_ids = (
        f"phase04-pitr-{marker}-db",
        f"phase04-pitr-{marker}-object",
        f"phase04-pitr-{marker}-checkpoint",
        f"phase04-pitr-{marker}-index",
    )
    try:
        with InfrastructureUnitOfWork(engine) as repo:
            repo.record_recovery_watermark(
                component_id=component_ids[0],
                service_kind="postgresql",
                authority="authoritative",
                watermark=recovery_point,
                owner_id="pitr-db-owner",
                payload={"postgres_lsn": recovery_point},
            )
            repo.record_recovery_watermark(
                component_id=component_ids[1],
                service_kind="object_manifest",
                authority="authoritative",
                watermark=recovery_point,
                owner_id="pitr-object-owner",
                payload={"object_manifest_watermark": recovery_point},
            )
            repo.record_recovery_watermark(
                component_id=component_ids[2],
                service_kind="checkpoint",
                authority="derived",
                watermark=recovery_point,
                owner_id="pitr-checkpoint-owner",
                payload={"checkpoint_generation": recovery_point},
            )
            repo.record_recovery_watermark(
                component_id=component_ids[3],
                service_kind="derived_index",
                authority="derived",
                watermark=recovery_point,
                owner_id="pitr-index-owner",
                payload={"index_generation": recovery_point},
            )
            repo.create_recovery_set(
                recovery_set_id=recovery_set_id,
                recovery_point=recovery_point,
                component_ids=component_ids,
                owner_id="pitr-recovery-owner",
            )
        with engine.connect() as connection:
            target_time = str(
                connection.execute(
                    text("SELECT to_char(clock_timestamp() + interval '500 milliseconds', 'YYYY-MM-DD HH24:MI:SS.MS TZH:TZM')")
                ).scalar_one()
            )
        time.sleep(2)
        with InfrastructureUnitOfWork(engine) as repo:
            repo.record_recovery_watermark(
                component_id=component_ids[3],
                service_kind="derived_index",
                authority="derived",
                watermark=f"{recovery_point}-ahead",
                owner_id="pitr-index-owner",
                payload={"index_generation": f"{recovery_point}-ahead"},
            )
        return errors, recovery_set_id, target_time
    finally:
        engine.dispose()


def _archive_wal(primary: str) -> list[str]:
    result = _run(
        [
            "docker",
            "exec",
            primary,
            "psql",
            "-U",
            "postgres",
            "-d",
            "zuno",
            "-c",
            "SELECT pg_switch_wal(); CHECKPOINT;",
        ],
        timeout=60,
    )
    if result.returncode != 0:
        return [f"WAL archive switch failed: {result.stdout}{result.stderr}"]
    time.sleep(2)
    return []


def _copy_pitr_artifacts(primary: str, workspace: Path) -> list[str]:
    basebackup = workspace / "basebackup"
    archive = workspace / "wal_archive"
    if basebackup.exists():
        shutil.rmtree(basebackup)
    if archive.exists():
        shutil.rmtree(archive)
    workspace.mkdir(parents=True, exist_ok=True)
    for source, target in [
        (f"{primary}:/tmp/basebackup", basebackup),
        (f"{primary}:/var/lib/postgresql/wal_archive", archive),
    ]:
        result = _run(["docker", "cp", source, str(target)], timeout=180)
        if result.returncode != 0:
            return [f"docker cp {source} failed: {result.stdout}{result.stderr}"]
    return []


def _start_recovery(
    container: str,
    port: int,
    workspace: Path,
    target_time: str,
) -> list[str]:
    start = _run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            container,
            "-e",
            "POSTGRES_PASSWORD=postgres",
            "-p",
            f"127.0.0.1:{port}:5432",
            POSTGRES_IMAGE,
            "bash",
            "-lc",
            "sleep 600",
        ],
        timeout=60,
    )
    if start.returncode != 0:
        return [f"recovery container start failed: {start.stdout}{start.stderr}"]

    for command in [
        ["docker", "exec", container, "bash", "-lc", "rm -rf /var/lib/postgresql/data/* /var/lib/postgresql/wal_archive && mkdir -p /var/lib/postgresql/wal_archive"],
        ["docker", "cp", str(workspace / "basebackup") + "/.", f"{container}:/var/lib/postgresql/data/"],
        ["docker", "cp", str(workspace / "wal_archive") + "/.", f"{container}:/var/lib/postgresql/wal_archive/"],
        [
            "docker",
            "exec",
            container,
            "bash",
            "-lc",
            (
                "touch /var/lib/postgresql/data/recovery.signal && "
                "printf '%s\\n' "
                "\"restore_command = 'cp /var/lib/postgresql/wal_archive/%f %p'\" "
                f"\"recovery_target_time = '{target_time}'\" "
                "\"recovery_target_action = 'promote'\" "
                ">> /var/lib/postgresql/data/postgresql.auto.conf && "
                "chown -R postgres:postgres /var/lib/postgresql/data /var/lib/postgresql/wal_archive && "
                "chmod 700 /var/lib/postgresql/data"
            ),
        ],
    ]:
        result = _run(command, timeout=180)
        if result.returncode != 0:
            return [f"recovery setup failed: {command!r}: {result.stdout}{result.stderr}"]

    launch = _run(
        [
            "docker",
            "exec",
            "-d",
            "-u",
            "postgres",
            container,
            "/usr/lib/postgresql/16/bin/postgres",
            "-D",
            "/var/lib/postgresql/data",
            "-c",
            "listen_addresses=*",
        ],
        timeout=30,
    )
    if launch.returncode != 0:
        return [f"recovery postgres launch failed: {launch.stdout}{launch.stderr}"]
    return _wait_ready(container)


def _verify_recovery(port: int, recovery_set_id: str) -> list[str]:
    url = f"postgresql+psycopg://postgres:postgres@127.0.0.1:{port}/zuno"
    engine = create_engine(url, future=True)
    errors: list[str] = []
    try:
        deadline = time.monotonic() + 60
        in_recovery = True
        while time.monotonic() < deadline:
            with engine.connect() as connection:
                in_recovery = bool(
                    connection.execute(text("SELECT pg_is_in_recovery()")).scalar_one()
                )
            if not in_recovery:
                break
            time.sleep(1)
        with engine.connect() as connection:
            if in_recovery:
                errors.append("PITR target did not promote after recovery")
            set_row = connection.execute(
                text(
                    """
                    SELECT recovery_point, status, length(verification_hash)
                    FROM infra_recovery_sets
                    WHERE recovery_set_id = :recovery_set_id
                    """
                ),
                {"recovery_set_id": recovery_set_id},
            ).first()
            if set_row is None or str(set_row.status) != "verified" or int(set_row.length) != 64:
                errors.append(f"restored recovery set mismatch: {set_row!r}")
                return errors
            recovery_point = str(set_row.recovery_point)
            member_rows = connection.execute(
                text(
                    """
                    SELECT authority, watermark
                    FROM infra_recovery_set_members
                    WHERE recovery_set_id = :recovery_set_id
                    """
                ),
                {"recovery_set_id": recovery_set_id},
            ).all()
            if len(member_rows) != 4:
                errors.append(f"restored recovery set member count mismatch: {len(member_rows)}")
            authorities = {str(row.authority) for row in member_rows}
            if authorities != {"authoritative", "derived"}:
                errors.append(f"restored recovery set authorities mismatch: {authorities!r}")
            if {str(row.watermark) for row in member_rows} != {recovery_point}:
                errors.append("restored recovery set members are not aligned to the PITR point")
            ahead_count = int(
                connection.execute(
                    text(
                        """
                        SELECT COUNT(*)
                        FROM infra_recovery_watermarks
                        WHERE watermark LIKE :ahead
                        """
                    ),
                    {"ahead": "%-ahead"},
                ).scalar_one()
            )
            if ahead_count != 0:
                errors.append("post-target derived index watermark survived PITR")
    finally:
        engine.dispose()
    return errors


def verify_phase04_pitr_alignment() -> list[str]:
    marker = uuid4().hex[:12]
    primary = f"zuno-pitr-primary-{marker}"
    recovery = f"zuno-pitr-recovery-{marker}"
    primary_port = _free_port()
    recovery_port = _free_port()
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="zuno-phase04-pitr-") as tmp:
        workspace = Path(tmp)
        config_path = workspace / "config.yaml"
        _write_alembic_config(config_path, primary_port)
        try:
            errors.extend(_start_primary(primary, primary_port))
            if errors:
                return errors
            errors.extend(_run_alembic_head(config_path))
            if errors:
                return errors
            errors.extend(_take_basebackup(primary))
            if errors:
                return errors
            seed_errors, recovery_set_id, target_time = _seed_target_window(primary_port, marker)
            errors.extend(seed_errors)
            if errors:
                return errors
            errors.extend(_archive_wal(primary))
            if errors:
                return errors
            errors.extend(_copy_pitr_artifacts(primary, workspace))
            if errors:
                return errors
            errors.extend(_start_recovery(recovery, recovery_port, workspace, target_time))
            if errors:
                logs = _run(["docker", "logs", recovery], timeout=30)
                errors.append(f"recovery logs: {logs.stdout}{logs.stderr}")
                return errors
            errors.extend(_verify_recovery(recovery_port, recovery_set_id))
        finally:
            _run(["docker", "rm", "-f", primary], timeout=60)
            _run(["docker", "rm", "-f", recovery], timeout=60)
    return errors


def main() -> int:
    errors = verify_phase04_pitr_alignment()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 PITR alignment verification failed.")
        return 1
    print("PHASE04 PITR alignment verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
