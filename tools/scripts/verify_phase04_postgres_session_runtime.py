from __future__ import annotations

import asyncio
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, SQLAlchemyError

from zuno.platform.database.foundation import InfrastructureUnitOfWork
from zuno.platform.database.runtime import PostgresRuntime, PostgresRuntimeConfig

SYNC_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/zuno"
ASYNC_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/zuno"


def _runtime() -> PostgresRuntime:
    return PostgresRuntime(
        PostgresRuntimeConfig(
            sync_url=SYNC_URL,
            async_url=ASYNC_URL,
            pool_size=2,
            max_overflow=1,
            pool_timeout_seconds=2,
            pool_recycle_seconds=300,
            statement_timeout_ms=5_000,
            lock_timeout_ms=1_000,
        )
    )


async def _tenant_probe(runtime: PostgresRuntime, tenant_id: str) -> str:
    async with runtime.async_uow(tenant_id=tenant_id) as session:
        await asyncio.sleep(0.05)
        return str(
            (
                await session.execute(text("SELECT current_setting('app.tenant_id', true)"))
            ).scalar_one()
            or ""
        )


async def _cancel_slow_query(runtime: PostgresRuntime) -> None:
    async with runtime.async_uow(statement_timeout_ms=30_000) as session:
        await session.execute(text("SELECT pg_sleep(30)"))


async def _verify() -> list[str]:
    errors: list[str] = []
    invalid_configs = [
        {"sync_url": ASYNC_URL, "async_url": ASYNC_URL},
        {"sync_url": SYNC_URL, "async_url": SYNC_URL},
        {"sync_url": SYNC_URL, "async_url": ASYNC_URL, "pool_size": 0},
        {
            "sync_url": SYNC_URL,
            "async_url": ASYNC_URL,
            "pool_timeout_seconds": float("nan"),
        },
        {"sync_url": SYNC_URL, "async_url": ASYNC_URL, "statement_timeout_ms": 0},
    ]
    for invalid_config in invalid_configs:
        try:
            PostgresRuntimeConfig(**invalid_config)
            errors.append(f"PostgreSQL runtime config accepted invalid values: {invalid_config}")
        except ValueError:
            pass

    runtime = _runtime()
    marker = uuid4().hex
    committed_resource = f"phase04-session-commit-{marker}"
    rolled_back_resource = f"phase04-session-rollback-{marker}"
    read_only_resource = f"phase04-session-read-only-{marker}"
    try:
        sync_health = runtime.sync_health()
        async_health = await runtime.async_health()
        for name, health in [("sync", sync_health), ("async", async_health)]:
            if not health.healthy or not health.ready or (health.server_version_num or 0) < 160000:
                errors.append(f"{name} PostgreSQL health/readiness receipt was not production-ready")
            if health.pool_size != 2 or health.checked_out != 0:
                errors.append(f"{name} PostgreSQL pool metrics did not reflect the configured idle pool")

        foundation_uow = InfrastructureUnitOfWork(runtime.sync_engine)
        with foundation_uow:
            try:
                with foundation_uow:
                    pass
                errors.append("foundation UoW allowed nested entry")
            except RuntimeError:
                pass

        try:
            with InfrastructureUnitOfWork(runtime.sync_engine, statement_timeout_ms=-1):
                pass
            errors.append("foundation UoW accepted an invalid transaction-local timeout")
        except DBAPIError:
            pass
        if runtime.sync_engine.pool.checkedout() != 0:
            errors.append("foundation UoW leaked a connection after transaction setup failed")

        sync_uow = runtime.sync_uow(tenant_id="tenant-sync", isolation_level="SERIALIZABLE")
        with sync_uow as session:
            tenant = session.execute(text("SELECT current_setting('app.tenant_id', true)")).scalar_one()
            isolation = session.execute(text("SHOW transaction_isolation")).scalar_one()
            if tenant != "tenant-sync" or isolation != "serializable":
                errors.append("sync session UoW lost tenant or isolation configuration")
            try:
                with sync_uow:
                    pass
                errors.append("sync session UoW allowed nested entry")
            except RuntimeError:
                pass
            session.execute(
                text(
                    """
                    INSERT INTO infra_worker_leases(resource_id, owner_id, lease_id, epoch, expires_at)
                    VALUES (:resource_id, 'session-runtime', :lease_id, 1, now() + interval '30 seconds')
                    """
                ),
                {"resource_id": committed_resource, "lease_id": f"lease-{marker}"},
            )
        with runtime.sync_engine.connect() as connection:
            if connection.execute(
                text("SELECT count(*) FROM infra_worker_leases WHERE resource_id = :resource_id"),
                {"resource_id": committed_resource},
            ).scalar_one() != 1:
                errors.append("sync session UoW did not commit its transaction")

        try:
            with runtime.sync_uow() as session:
                session.execute(
                    text(
                        """
                        INSERT INTO infra_worker_leases(resource_id, owner_id, lease_id, epoch, expires_at)
                        VALUES (:resource_id, 'session-runtime', :lease_id, 1, now() + interval '30 seconds')
                        """
                    ),
                    {"resource_id": rolled_back_resource, "lease_id": f"rollback-{marker}"},
                )
                raise RuntimeError("simulate domain rollback")
        except RuntimeError:
            pass
        with runtime.sync_engine.connect() as connection:
            if connection.execute(
                text("SELECT count(*) FROM infra_worker_leases WHERE resource_id = :resource_id"),
                {"resource_id": rolled_back_resource},
            ).scalar_one() != 0:
                errors.append("sync session UoW did not roll back after an exception")

        try:
            with runtime.sync_uow(read_only=True) as session:
                session.execute(
                    text(
                        """
                        INSERT INTO infra_worker_leases(resource_id, owner_id, lease_id, epoch, expires_at)
                        VALUES (:resource_id, 'read-only', :lease_id, 1, now() + interval '30 seconds')
                        """
                    ),
                    {"resource_id": read_only_resource, "lease_id": f"read-only-{marker}"},
                )
            errors.append("sync read-only UoW accepted a write")
        except DBAPIError:
            pass

        tenants = await asyncio.gather(
            _tenant_probe(runtime, "tenant-async-a"),
            _tenant_probe(runtime, "tenant-async-b"),
        )
        if tenants != ["tenant-async-a", "tenant-async-b"]:
            errors.append("concurrent async sessions leaked tenant context")
        async with runtime.async_uow() as session:
            tenant = (
                await session.execute(text("SELECT current_setting('app.tenant_id', true)"))
            ).scalar_one()
            if tenant not in (None, ""):
                errors.append("async tenant context leaked into a later transaction")

        async_uow = runtime.async_uow(isolation_level="REPEATABLE READ")
        async with async_uow as session:
            isolation = (await session.execute(text("SHOW transaction_isolation"))).scalar_one()
            if isolation != "repeatable read":
                errors.append("async session UoW did not apply transaction isolation")
            try:
                async with async_uow:
                    pass
                errors.append("async session UoW allowed nested entry")
            except RuntimeError:
                pass

        try:
            async with runtime.async_uow(read_only=True) as session:
                await session.execute(
                    text(
                        """
                        INSERT INTO infra_worker_leases(resource_id, owner_id, lease_id, epoch, expires_at)
                        VALUES (:resource_id, 'read-only', :lease_id, 1, now() + interval '30 seconds')
                        """
                    ),
                    {"resource_id": read_only_resource, "lease_id": f"async-read-only-{marker}"},
                )
            errors.append("async read-only UoW accepted a write")
        except DBAPIError:
            pass

        try:
            async with runtime.async_uow(statement_timeout_ms=100) as session:
                await session.execute(text("SELECT pg_sleep(1)"))
            errors.append("async statement timeout did not cancel a slow query")
        except DBAPIError:
            pass
        if not (await runtime.async_health()).ready:
            errors.append("async pool did not recover after statement timeout")

        cancellation = asyncio.create_task(_cancel_slow_query(runtime))
        await asyncio.sleep(0.2)
        cancellation.cancel()
        try:
            await cancellation
            errors.append("async slow query ignored task cancellation")
        except asyncio.CancelledError:
            pass
        if not (await runtime.async_health()).ready:
            errors.append("async pool did not recover after task cancellation")

        try:
            async with runtime.async_uow() as session:
                backend_pid = int((await session.execute(text("SELECT pg_backend_pid()"))).scalar_one())
                with runtime.sync_engine.begin() as connection:
                    terminated = connection.execute(
                        text("SELECT pg_terminate_backend(:backend_pid)"),
                        {"backend_pid": backend_pid},
                    ).scalar_one()
                if not terminated:
                    errors.append("async PostgreSQL backend was not terminated for connection-loss test")
                await session.execute(text("SELECT 1"))
            errors.append("terminated async connection did not fail closed")
        except SQLAlchemyError:
            pass
        if not (await runtime.async_health()).ready:
            errors.append("async engine did not recover after backend termination")

        async with runtime.async_uow() as session:
            pid_before_rotation = int((await session.execute(text("SELECT pg_backend_pid()"))).scalar_one())
        await runtime.rotate_connections()
        async with runtime.async_uow() as session:
            pid_after_rotation = int((await session.execute(text("SELECT pg_backend_pid()"))).scalar_one())
        if pid_before_rotation == pid_after_rotation:
            errors.append("connection rotation reused the disposed async backend")
        if not runtime.sync_health().ready or not (await runtime.async_health()).ready:
            errors.append("sync/async runtime did not recover after connection rotation")
    finally:
        try:
            with runtime.sync_engine.begin() as connection:
                connection.execute(
                    text(
                        """
                        DELETE FROM infra_worker_leases
                        WHERE resource_id IN (:committed, :rolled_back, :read_only)
                        """
                    ),
                    {
                        "committed": committed_resource,
                        "rolled_back": rolled_back_resource,
                        "read_only": read_only_resource,
                    },
                )
        finally:
            await runtime.close()
    return errors


def verify_phase04_postgres_session_runtime() -> list[str]:
    return asyncio.run(_verify())


def main() -> int:
    errors = verify_phase04_postgres_session_runtime()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 PostgreSQL session runtime verification failed.")
        return 1
    print("PHASE04 PostgreSQL session runtime verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
