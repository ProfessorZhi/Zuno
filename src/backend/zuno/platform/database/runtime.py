from __future__ import annotations

import math
from dataclasses import dataclass

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession


@dataclass(frozen=True, slots=True)
class PostgresRuntimeConfig:
    sync_url: str
    async_url: str
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout_seconds: float = 30.0
    pool_recycle_seconds: int = 1800
    statement_timeout_ms: int = 30_000
    lock_timeout_ms: int = 5_000
    echo: bool = False

    def __post_init__(self) -> None:
        if not self.sync_url.startswith("postgresql+"):
            raise ValueError("sync_url must use a PostgreSQL SQLAlchemy driver")
        if not self.async_url.startswith("postgresql+"):
            raise ValueError("async_url must use a PostgreSQL SQLAlchemy driver")
        if make_url(self.sync_url).get_dialect().is_async:
            raise ValueError("sync_url must use a synchronous PostgreSQL driver")
        if not make_url(self.async_url).get_dialect().is_async:
            raise ValueError("async_url must use an asynchronous PostgreSQL driver")
        if self.pool_size < 1 or self.max_overflow < 0:
            raise ValueError("pool_size must be positive and max_overflow must not be negative")
        if not math.isfinite(self.pool_timeout_seconds) or self.pool_timeout_seconds <= 0:
            raise ValueError("pool_timeout_seconds must be finite and positive")
        if self.pool_recycle_seconds < 1:
            raise ValueError("pool_recycle_seconds must be positive")
        if self.statement_timeout_ms < 1 or self.lock_timeout_ms < 1:
            raise ValueError("statement and lock timeouts must be positive")


@dataclass(frozen=True, slots=True)
class PostgresHealthReceipt:
    healthy: bool
    ready: bool
    server_version_num: int | None
    pool_size: int
    checked_out: int
    overflow: int
    error_code: str | None = None


class UnitOfWorkSession(Session):
    def commit(self) -> None:
        raise RuntimeError("transaction commit is owned by the Unit of Work")


class AsyncUnitOfWorkSession(AsyncSession):
    async def commit(self) -> None:
        raise RuntimeError("transaction commit is owned by the Unit of Work")


class SyncSessionUnitOfWork:
    def __init__(
        self,
        runtime: PostgresRuntime,
        *,
        tenant_id: str | None,
        statement_timeout_ms: int,
        lock_timeout_ms: int,
        isolation_level: str | None,
        read_only: bool,
    ) -> None:
        self.runtime = runtime
        self.tenant_id = tenant_id
        self.statement_timeout_ms = statement_timeout_ms
        self.lock_timeout_ms = lock_timeout_ms
        self.isolation_level = isolation_level
        self.read_only = read_only
        self._active = False

    def __enter__(self) -> Session:
        if self._active:
            raise RuntimeError("SyncSessionUnitOfWork cannot be nested or entered concurrently")
        self._active = True
        bind = self.runtime.sync_engine
        if self.isolation_level is not None:
            bind = bind.execution_options(isolation_level=self.isolation_level)
        self.session = self.runtime.sync_session_factory(bind=bind)
        self._transaction = self.session.begin()
        try:
            self._transaction.__enter__()
            self._configure_transaction()
            return self.session
        except BaseException:
            try:
                self._transaction.__exit__(*self._current_exception())
            finally:
                self.session.close()
                self._active = False
            raise

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        try:
            self._transaction.__exit__(exc_type, exc, tb)
        finally:
            self.session.close()
            self._active = False

    def _configure_transaction(self) -> None:
        if self.read_only:
            self.session.execute(text("SET TRANSACTION READ ONLY"))
        self.session.execute(
            text("SELECT set_config('statement_timeout', :value, true)"),
            {"value": str(self.statement_timeout_ms)},
        )
        self.session.execute(
            text("SELECT set_config('lock_timeout', :value, true)"),
            {"value": str(self.lock_timeout_ms)},
        )
        if self.tenant_id is not None:
            self.session.execute(
                text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
                {"tenant_id": self.tenant_id},
            )

    @staticmethod
    def _current_exception() -> tuple[type[BaseException] | None, BaseException | None, object | None]:
        import sys

        return sys.exc_info()


class AsyncSessionUnitOfWork:
    def __init__(
        self,
        runtime: PostgresRuntime,
        *,
        tenant_id: str | None,
        statement_timeout_ms: int,
        lock_timeout_ms: int,
        isolation_level: str | None,
        read_only: bool,
    ) -> None:
        self.runtime = runtime
        self.tenant_id = tenant_id
        self.statement_timeout_ms = statement_timeout_ms
        self.lock_timeout_ms = lock_timeout_ms
        self.isolation_level = isolation_level
        self.read_only = read_only
        self._active = False

    async def __aenter__(self) -> AsyncSession:
        if self._active:
            raise RuntimeError("AsyncSessionUnitOfWork cannot be nested or entered concurrently")
        self._active = True
        bind = self.runtime.async_engine
        if self.isolation_level is not None:
            bind = bind.execution_options(isolation_level=self.isolation_level)
        self.session = self.runtime.async_session_factory(bind=bind)
        self._transaction = self.session.begin()
        try:
            await self._transaction.__aenter__()
            await self._configure_transaction()
            return self.session
        except BaseException:
            try:
                await self._transaction.__aexit__(*self._current_exception())
            finally:
                await self.session.close()
                self._active = False
            raise

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        try:
            await self._transaction.__aexit__(exc_type, exc, tb)
        finally:
            await self.session.close()
            self._active = False

    async def _configure_transaction(self) -> None:
        if self.read_only:
            await self.session.execute(text("SET TRANSACTION READ ONLY"))
        await self.session.execute(
            text("SELECT set_config('statement_timeout', :value, true)"),
            {"value": str(self.statement_timeout_ms)},
        )
        await self.session.execute(
            text("SELECT set_config('lock_timeout', :value, true)"),
            {"value": str(self.lock_timeout_ms)},
        )
        if self.tenant_id is not None:
            await self.session.execute(
                text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
                {"tenant_id": self.tenant_id},
            )

    @staticmethod
    def _current_exception() -> tuple[type[BaseException] | None, BaseException | None, object | None]:
        import sys

        return sys.exc_info()


class PostgresRuntime:
    def __init__(self, config: PostgresRuntimeConfig) -> None:
        self.config = config
        engine_options = {
            "pool_pre_ping": True,
            "pool_size": config.pool_size,
            "max_overflow": config.max_overflow,
            "pool_timeout": config.pool_timeout_seconds,
            "pool_recycle": config.pool_recycle_seconds,
            "echo": config.echo,
        }
        self.sync_engine = create_engine(config.sync_url, future=True, **engine_options)
        self.async_engine = create_async_engine(config.async_url, **engine_options)
        self.sync_session_factory = sessionmaker(
            bind=self.sync_engine,
            class_=UnitOfWorkSession,
            expire_on_commit=False,
            autoflush=False,
        )
        self.async_session_factory = async_sessionmaker(
            bind=self.async_engine,
            class_=AsyncUnitOfWorkSession,
            expire_on_commit=False,
            autoflush=False,
        )

    def sync_uow(
        self,
        *,
        tenant_id: str | None = None,
        statement_timeout_ms: int | None = None,
        lock_timeout_ms: int | None = None,
        isolation_level: str | None = None,
        read_only: bool = False,
    ) -> SyncSessionUnitOfWork:
        return SyncSessionUnitOfWork(
            self,
            tenant_id=tenant_id,
            statement_timeout_ms=self._timeout(
                "statement_timeout_ms",
                statement_timeout_ms,
                self.config.statement_timeout_ms,
            ),
            lock_timeout_ms=self._timeout(
                "lock_timeout_ms",
                lock_timeout_ms,
                self.config.lock_timeout_ms,
            ),
            isolation_level=isolation_level,
            read_only=read_only,
        )

    def async_uow(
        self,
        *,
        tenant_id: str | None = None,
        statement_timeout_ms: int | None = None,
        lock_timeout_ms: int | None = None,
        isolation_level: str | None = None,
        read_only: bool = False,
    ) -> AsyncSessionUnitOfWork:
        return AsyncSessionUnitOfWork(
            self,
            tenant_id=tenant_id,
            statement_timeout_ms=self._timeout(
                "statement_timeout_ms",
                statement_timeout_ms,
                self.config.statement_timeout_ms,
            ),
            lock_timeout_ms=self._timeout(
                "lock_timeout_ms",
                lock_timeout_ms,
                self.config.lock_timeout_ms,
            ),
            isolation_level=isolation_level,
            read_only=read_only,
        )

    def sync_health(self) -> PostgresHealthReceipt:
        try:
            with self.sync_engine.connect() as connection:
                row = connection.execute(
                    text(
                        """
                        SELECT current_setting('server_version_num')::integer AS version,
                               NOT pg_is_in_recovery() AS ready
                        """
                    )
                ).one()
            return self._health_receipt(
                self.sync_engine,
                healthy=True,
                ready=bool(row.ready),
                server_version_num=int(row.version),
            )
        except SQLAlchemyError as exc:
            return self._health_receipt(
                self.sync_engine,
                healthy=False,
                ready=False,
                server_version_num=None,
                error_code=type(exc).__name__,
            )

    async def async_health(self) -> PostgresHealthReceipt:
        try:
            async with self.async_engine.connect() as connection:
                row = (
                    await connection.execute(
                        text(
                            """
                            SELECT current_setting('server_version_num')::integer AS version,
                                   NOT pg_is_in_recovery() AS ready
                            """
                        )
                    )
                ).one()
            return self._health_receipt(
                self.async_engine,
                healthy=True,
                ready=bool(row.ready),
                server_version_num=int(row.version),
            )
        except SQLAlchemyError as exc:
            return self._health_receipt(
                self.async_engine,
                healthy=False,
                ready=False,
                server_version_num=None,
                error_code=type(exc).__name__,
            )

    async def rotate_connections(self) -> None:
        self.sync_engine.dispose()
        await self.async_engine.dispose()

    async def close(self) -> None:
        await self.rotate_connections()

    @staticmethod
    def _timeout(name: str, override: int | None, default: int) -> int:
        value = default if override is None else override
        if value < 1:
            raise ValueError(f"{name} must be positive")
        return value

    @staticmethod
    def _health_receipt(
        engine: Engine | AsyncEngine,
        *,
        healthy: bool,
        ready: bool,
        server_version_num: int | None,
        error_code: str | None = None,
    ) -> PostgresHealthReceipt:
        pool = engine.pool
        size = getattr(pool, "size", lambda: 0)()
        checked_out = getattr(pool, "checkedout", lambda: 0)()
        overflow = getattr(pool, "overflow", lambda: 0)()
        return PostgresHealthReceipt(
            healthy=healthy,
            ready=ready,
            server_version_num=server_version_num,
            pool_size=int(size),
            checked_out=int(checked_out),
            overflow=int(overflow),
            error_code=error_code,
        )


__all__ = [
    "AsyncUnitOfWorkSession",
    "AsyncSessionUnitOfWork",
    "PostgresHealthReceipt",
    "PostgresRuntime",
    "PostgresRuntimeConfig",
    "SyncSessionUnitOfWork",
    "UnitOfWorkSession",
]
