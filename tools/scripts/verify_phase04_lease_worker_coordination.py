from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier, Event
from uuid import uuid4

from sqlalchemy import text

from zuno.platform.database.foundation import (
    FencingRejectedError,
    FencingToken,
    InfrastructureUnitOfWork,
    create_foundation_engine,
)
from zuno.platform.database.lease import LeaseWorkerCoordinator

REPO_ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno",
)
POSTGRES_HOST = "127.0.0.1"
POSTGRES_PORT = 5432
RESOURCE_PREFIX = "phase04-lease-coordination"
EFFECT_PREFIX = "phase04-lease-effect"


class _TcpPartitionProxy:
    def __init__(self, upstream_host: str, upstream_port: int) -> None:
        self.upstream_host = upstream_host
        self.upstream_port = upstream_port
        self.server: asyncio.AbstractServer | None = None
        self.forwarding = asyncio.Event()
        self.forwarding.set()
        self.connections: set[tuple[asyncio.StreamWriter, asyncio.StreamWriter]] = set()

    async def start(self) -> int:
        self.server = await asyncio.start_server(self._handle, "127.0.0.1", 0)
        socket = self.server.sockets[0]
        return int(socket.getsockname()[1])

    def partition(self) -> None:
        self.forwarding.clear()

    def restore(self) -> None:
        self.forwarding.set()

    async def close(self) -> None:
        self.forwarding.set()
        connections = list(self.connections)
        self.connections.clear()
        for client_writer, upstream_writer in connections:
            client_writer.close()
            upstream_writer.close()
        try:
            await asyncio.wait_for(
                asyncio.gather(
                    *(writer.wait_closed() for pair in connections for writer in pair),
                    return_exceptions=True,
                ),
                timeout=2,
            )
        except TimeoutError:
            pass
        if self.server is not None:
            self.server.close()
            await self.server.wait_closed()

    async def _handle(self, client_reader: asyncio.StreamReader, client_writer: asyncio.StreamWriter) -> None:
        try:
            upstream_reader, upstream_writer = await asyncio.open_connection(
                self.upstream_host,
                self.upstream_port,
            )
        except OSError:
            client_writer.close()
            await client_writer.wait_closed()
            return
        pair = (client_writer, upstream_writer)
        self.connections.add(pair)
        try:
            await asyncio.gather(
                self._pipe(client_reader, upstream_writer),
                self._pipe(upstream_reader, client_writer),
            )
        finally:
            self.connections.discard(pair)
            client_writer.close()
            upstream_writer.close()
            try:
                await asyncio.wait_for(
                    asyncio.gather(
                        client_writer.wait_closed(),
                        upstream_writer.wait_closed(),
                        return_exceptions=True,
                    ),
                    timeout=2,
                )
            except TimeoutError:
                pass

    async def _pipe(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            while data := await reader.read(64 * 1024):
                await self.forwarding.wait()
                writer.write(data)
                await writer.drain()
        except (ConnectionError, OSError):
            pass


def _cleanup(engine) -> None:
    with engine.begin() as connection:
        connection.execute(
            text("DELETE FROM infra_worker_leases WHERE resource_id LIKE :prefix"),
            {"prefix": f"{RESOURCE_PREFIX}%"},
        )
        connection.execute(
            text("DELETE FROM infra_outbox_events WHERE aggregate_id LIKE :prefix"),
            {"prefix": f"{EFFECT_PREFIX}%"},
        )


def _load_token(engine, resource_id: str) -> FencingToken:
    with engine.connect() as connection:
        row = connection.execute(
            text(
                """
                SELECT resource_id, owner_id, lease_id, epoch, expires_at
                FROM infra_worker_leases
                WHERE resource_id = :resource_id
                """
            ),
            {"resource_id": resource_id},
        ).one()
    return FencingToken(
        resource_id=str(row.resource_id),
        owner_id=str(row.owner_id),
        lease_id=str(row.lease_id),
        epoch=int(row.epoch),
        expires_at=row.expires_at,
    )


def _effect_commit(marker: str):
    def commit(repo, prepared: str) -> str:
        return repo.enqueue_outbox(
            aggregate_id=f"{EFFECT_PREFIX}-{marker}",
            topic="phase04.lease.fenced-result",
            payload={"marker": marker, "prepared": prepared},
            idempotency_key=f"lease-effect-{marker}",
        )

    return commit


def _verify_database_clock_transfer_and_tolerance(engine, marker: str, errors: list[str]) -> None:
    resource = f"{RESOURCE_PREFIX}-transfer-{marker}"
    with InfrastructureUnitOfWork(engine) as repo:
        token = repo.acquire_lease(resource_id=resource, owner_id="worker-a", ttl_seconds=3)
        same_owner = repo.acquire_lease(resource_id=resource, owner_id="worker-a", ttl_seconds=5)
        if same_owner.lease_id != token.lease_id or same_owner.epoch != token.epoch:
            errors.append("same-owner live reacquire changed lease identity")
        renewed = repo.renew_lease(token, ttl_seconds=1)
        if renewed.expires_at < same_owner.expires_at:
            errors.append("lease renew shortened an existing deadline")
        repo.assert_fence(token, clock_tolerance_seconds=0)
        try:
            repo.assert_fence(token, clock_tolerance_seconds=6)
            errors.append("clock tolerance accepted a lease without enough remaining lifetime")
        except FencingRejectedError:
            pass
        transferred = repo.transfer_lease(token, new_owner_id="worker-b", ttl_seconds=3)
        if transferred.owner_id != "worker-b" or transferred.epoch != token.epoch + 1:
            errors.append(f"explicit lease transfer mismatch: {transferred!r}")
        try:
            repo.assert_fence(token)
            errors.append("old token passed after explicit transfer")
        except FencingRejectedError:
            pass
        repo.assert_fence(transferred)


def _verify_heartbeat_and_atomic_commit(engine, marker: str, errors: list[str]) -> None:
    resource = f"{RESOURCE_PREFIX}-heartbeat-{marker}"
    started = Event()
    coordinator = LeaseWorkerCoordinator(
        engine,
        ttl_seconds=1,
        heartbeat_interval_seconds=0.2,
        clock_tolerance_seconds=0.1,
    )

    def work() -> str:
        started.set()
        time.sleep(1.6)
        return "prepared-heartbeat-result"

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            coordinator.execute,
            resource_id=resource,
            owner_id="worker-heartbeat",
            work=work,
            commit=_effect_commit(f"heartbeat-{marker}"),
        )
        if not started.wait(timeout=5):
            errors.append("heartbeat-coordinated work did not start")
        time.sleep(1.2)
        with InfrastructureUnitOfWork(engine) as repo:
            try:
                repo.acquire_lease(resource_id=resource, owner_id="worker-contender", ttl_seconds=1)
                errors.append("contender acquired a heartbeat-protected lease")
            except FencingRejectedError:
                pass
        receipt = future.result(timeout=10)
    if receipt.owner_id != "worker-heartbeat" or receipt.epoch != 1 or not str(receipt.result).startswith("outbox:"):
        errors.append(f"heartbeat fenced commit receipt mismatch: {receipt!r}")


def _verify_pause_and_crash_handoff(engine, marker: str, errors: list[str]) -> None:
    pause_resource = f"{RESOURCE_PREFIX}-pause-{marker}"
    old = LeaseWorkerCoordinator(engine, ttl_seconds=1, heartbeat_interval_seconds=0.2).acquire(
        resource_id=pause_resource,
        owner_id="worker-paused",
    )
    time.sleep(1.2)
    replacement_coordinator = LeaseWorkerCoordinator(engine, ttl_seconds=3, heartbeat_interval_seconds=1)
    replacement = replacement_coordinator.acquire(
        resource_id=pause_resource,
        owner_id="worker-after-pause",
    )
    try:
        LeaseWorkerCoordinator(engine).commit(
            old,
            "late-paused-result",
            _effect_commit(f"late-pause-{marker}"),
        )
        errors.append("paused worker committed after lease expiry and replacement")
    except FencingRejectedError:
        pass
    if replacement.epoch != old.epoch + 1:
        errors.append("pause handoff did not increment epoch")

    crash_resource = f"{RESOURCE_PREFIX}-crash-{marker}"
    code = """
import json
import os

from zuno.platform.database.foundation import InfrastructureUnitOfWork, create_foundation_engine

engine = create_foundation_engine(os.environ["ZUNO_TEST_POSTGRES_URL"])
try:
    with InfrastructureUnitOfWork(engine) as repo:
        token = repo.acquire_lease(
            resource_id=os.environ["ZUNO_LEASE_RESOURCE"],
            owner_id="worker-crashed",
            ttl_seconds=300,
        )
    print(json.dumps({
        "resource_id": token.resource_id,
        "owner_id": token.owner_id,
        "lease_id": token.lease_id,
        "epoch": token.epoch,
        "expires_at": token.expires_at.isoformat(),
    }), flush=True)
finally:
    engine.dispose()
os._exit(0)
"""
    env = os.environ.copy()
    env["ZUNO_TEST_POSTGRES_URL"] = DATABASE_URL
    env["ZUNO_LEASE_RESOURCE"] = crash_resource
    child = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
    )
    if child.returncode != 0 or not child.stdout.strip():
        errors.append(f"crashed lease owner setup failed: {child.stderr!r}")
        return
    payload = json.loads(child.stdout.strip())
    crashed = _load_token(engine, crash_resource)
    if crashed.lease_id != payload["lease_id"] or crashed.epoch != payload["epoch"]:
        errors.append("crashed owner token did not persist before process exit")
    with engine.begin() as connection:
        connection.execute(
            text(
                "UPDATE infra_worker_leases SET expires_at = now() - interval '1 second' "
                "WHERE resource_id = :resource_id"
            ),
            {"resource_id": crash_resource},
        )
    after_crash = replacement_coordinator.acquire(
        resource_id=crash_resource,
        owner_id="worker-after-crash",
    )
    try:
        replacement_coordinator.commit(
            crashed,
            "late-crashed-result",
            _effect_commit(f"late-crash-{marker}"),
        )
        errors.append("crashed worker committed after handoff")
    except FencingRejectedError:
        pass
    if after_crash.epoch != crashed.epoch + 1:
        errors.append("crash handoff did not increment epoch")


def _verify_cancel_transfer_race(engine, marker: str, errors: list[str]) -> None:
    resource = f"{RESOURCE_PREFIX}-cancel-race-{marker}"
    with InfrastructureUnitOfWork(engine) as repo:
        token = repo.acquire_lease(resource_id=resource, owner_id="worker-race-a", ttl_seconds=30)
    barrier = Barrier(2)

    def cancel():
        barrier.wait(timeout=5)
        try:
            with InfrastructureUnitOfWork(engine) as repo:
                repo.cancel_lease(token)
            return "cancelled", None
        except FencingRejectedError:
            return "rejected", None

    def transfer():
        barrier.wait(timeout=5)
        try:
            with InfrastructureUnitOfWork(engine) as repo:
                transferred = repo.transfer_lease(
                    token,
                    new_owner_id="worker-race-b",
                    ttl_seconds=30,
                )
            return "transferred", transferred
        except FencingRejectedError:
            return "rejected", None

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = [future.result(timeout=10) for future in [executor.submit(cancel), executor.submit(transfer)]]
    winners = [outcome for outcome in outcomes if outcome[0] != "rejected"]
    if len(winners) != 1:
        errors.append(f"cancel/transfer race did not have one winner: {outcomes!r}")
        return
    if winners[0][0] == "cancelled":
        with InfrastructureUnitOfWork(engine) as repo:
            current = repo.acquire_lease(resource_id=resource, owner_id="worker-race-b", ttl_seconds=30)
    else:
        current = winners[0][1]
    if current is None or current.owner_id != "worker-race-b" or current.epoch != token.epoch + 1:
        errors.append(f"cancel/transfer race did not converge on generation 2: {current!r}")


async def _verify_postgres_partition(engine, marker: str, errors: list[str]) -> None:
    resource = f"{RESOURCE_PREFIX}-partition-{marker}"
    proxy = _TcpPartitionProxy(POSTGRES_HOST, POSTGRES_PORT)
    port = await proxy.start()
    proxy_url = f"postgresql+psycopg://postgres:postgres@127.0.0.1:{port}/zuno?connect_timeout=2"
    code = """
import os
import sys
import time

from zuno.platform.database.foundation import FencingRejectedError, create_foundation_engine
from zuno.platform.database.lease import LeaseWorkerCoordinator

engine = create_foundation_engine(
    os.environ["ZUNO_TEST_POSTGRES_URL"],
    pool_size=2,
    max_overflow=0,
    pool_timeout=2,
)
coordinator = LeaseWorkerCoordinator(engine, ttl_seconds=1, heartbeat_interval_seconds=0.2)

def commit(repo, prepared):
    return repo.enqueue_outbox(
        aggregate_id=os.environ["ZUNO_LEASE_EFFECT"],
        topic="phase04.lease.partition-old",
        payload={"prepared": prepared},
        idempotency_key=os.environ["ZUNO_LEASE_EFFECT"],
    )

try:
    coordinator.execute(
        resource_id=os.environ["ZUNO_LEASE_RESOURCE"],
        owner_id="worker-partitioned",
        work=lambda: time.sleep(1.3) or "prepared-during-partition",
        commit=commit,
    )
except FencingRejectedError:
    sys.exit(17)
finally:
    engine.dispose(close=False)
sys.exit(0)
"""
    env = os.environ.copy()
    env["ZUNO_TEST_POSTGRES_URL"] = proxy_url
    env["ZUNO_LEASE_RESOURCE"] = resource
    env["ZUNO_LEASE_EFFECT"] = f"{EFFECT_PREFIX}-partition-old-{marker}"
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-c",
        code,
        cwd=str(REPO_ROOT),
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    old_token: FencingToken | None = None
    try:
        for _ in range(50):
            try:
                old_token = _load_token(engine, resource)
                break
            except Exception:
                await asyncio.sleep(0.1)
        if old_token is None:
            errors.append("partitioned lease worker did not acquire before fault injection")
            return
        proxy.partition()
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=12)
        except TimeoutError:
            process.kill()
            stdout, stderr = await process.communicate()
            errors.append("partitioned worker did not fail closed before the process deadline")
        else:
            if process.returncode != 17:
                errors.append(
                    "partitioned heartbeat did not produce fencing rejection: "
                    f"returncode={process.returncode} stdout={stdout!r} stderr={stderr!r}"
                )
        proxy.restore()
        await asyncio.sleep(0.5)
        with engine.begin() as connection:
            connection.execute(
                text(
                    "UPDATE infra_worker_leases SET expires_at = now() - interval '1 second' "
                    "WHERE resource_id = :resource_id"
                ),
                {"resource_id": resource},
            )
        replacement_coordinator = LeaseWorkerCoordinator(engine, ttl_seconds=3, heartbeat_interval_seconds=1)
        replacement = replacement_coordinator.acquire(
            resource_id=resource,
            owner_id="worker-after-partition",
        )
        try:
            replacement_coordinator.commit(
                old_token,
                "late-partition-result",
                _effect_commit(f"partition-late-{marker}"),
            )
            errors.append("old worker committed after PostgreSQL partition recovery and handoff")
        except FencingRejectedError:
            pass
        receipt = replacement_coordinator.commit(
            replacement,
            "replacement-partition-result",
            _effect_commit(f"partition-new-{marker}"),
        )
        if not str(receipt.result).startswith("outbox:"):
            errors.append("replacement worker did not commit after partition recovery")
    finally:
        proxy.restore()
        if process.returncode is None:
            process.kill()
            await process.communicate()
        await proxy.close()


async def _verify() -> list[str]:
    marker = uuid4().hex
    engine = create_foundation_engine(DATABASE_URL, pool_size=8, max_overflow=4, pool_timeout=5)
    errors: list[str] = []
    try:
        _cleanup(engine)
        _verify_database_clock_transfer_and_tolerance(engine, marker, errors)
        _verify_heartbeat_and_atomic_commit(engine, marker, errors)
        _verify_pause_and_crash_handoff(engine, marker, errors)
        _verify_cancel_transfer_race(engine, marker, errors)
        await _verify_postgres_partition(engine, marker, errors)
    finally:
        _cleanup(engine)
        engine.dispose()
    return errors


def verify_phase04_lease_worker_coordination() -> list[str]:
    return asyncio.run(_verify())


def main() -> int:
    errors = verify_phase04_lease_worker_coordination()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 lease worker coordination verification failed.")
        return 1
    print("PHASE04 lease worker coordination verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
