from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from threading import get_ident
from typing import Protocol

from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession

from zuno.platform.database import postgres_runtime
from zuno.platform.database.runtime import AsyncSessionUnitOfWork, SyncSessionUnitOfWork

logger = logging.getLogger(__name__)


class SessionRuntimePort(Protocol):
    def sync_uow(
        self,
        *,
        tenant_id: str | None = None,
        statement_timeout_ms: int | None = None,
        lock_timeout_ms: int | None = None,
        isolation_level: str | None = None,
        read_only: bool = False,
    ) -> SyncSessionUnitOfWork: ...

    def async_uow(
        self,
        *,
        tenant_id: str | None = None,
        statement_timeout_ms: int | None = None,
        lock_timeout_ms: int | None = None,
        isolation_level: str | None = None,
        read_only: bool = False,
    ) -> AsyncSessionUnitOfWork: ...


@dataclass(frozen=True, slots=True)
class _SyncScope:
    session: Session
    owner_thread_id: int


@dataclass(frozen=True, slots=True)
class _AsyncScope:
    session: AsyncSession
    owner_task_id: int


_sync_scope: ContextVar[_SyncScope | None] = ContextVar("zuno_sync_uow", default=None)
_async_scope: ContextVar[_AsyncScope | None] = ContextVar("zuno_async_uow", default=None)


@contextmanager
def domain_uow(
    *,
    tenant_id: str | None = None,
    statement_timeout_ms: int | None = None,
    lock_timeout_ms: int | None = None,
    isolation_level: str | None = None,
    read_only: bool = False,
    runtime: SessionRuntimePort | None = None,
) -> Iterator[Session]:
    if _sync_scope.get() is not None:
        raise RuntimeError("domain_uow cannot be nested; repositories reuse the active UoW")
    selected_runtime = runtime or postgres_runtime
    with selected_runtime.sync_uow(
        tenant_id=tenant_id,
        statement_timeout_ms=statement_timeout_ms,
        lock_timeout_ms=lock_timeout_ms,
        isolation_level=isolation_level,
        read_only=read_only,
    ) as session:
        token = _sync_scope.set(_SyncScope(session=session, owner_thread_id=get_ident()))
        try:
            yield session
        finally:
            _sync_scope.reset(token)


@asynccontextmanager
async def async_domain_uow(
    *,
    tenant_id: str | None = None,
    statement_timeout_ms: int | None = None,
    lock_timeout_ms: int | None = None,
    isolation_level: str | None = None,
    read_only: bool = False,
    runtime: SessionRuntimePort | None = None,
) -> AsyncIterator[AsyncSession]:
    if _async_scope.get() is not None:
        raise RuntimeError("async_domain_uow cannot be nested; repositories reuse the active UoW")
    task = asyncio.current_task()
    if task is None:
        raise RuntimeError("async_domain_uow requires an active asyncio task")
    selected_runtime = runtime or postgres_runtime
    async with selected_runtime.async_uow(
        tenant_id=tenant_id,
        statement_timeout_ms=statement_timeout_ms,
        lock_timeout_ms=lock_timeout_ms,
        isolation_level=isolation_level,
        read_only=read_only,
    ) as session:
        token = _async_scope.set(_AsyncScope(session=session, owner_task_id=id(task)))
        try:
            yield session
        finally:
            _async_scope.reset(token)


@contextmanager
def session_getter() -> Iterator[Session]:
    active_scope = _sync_scope.get()
    if active_scope is not None:
        if active_scope.owner_thread_id != get_ident():
            raise RuntimeError("a sync Unit of Work cannot be shared across threads")
        yield active_scope.session
        return
    try:
        with domain_uow() as session:
            yield session
    except Exception as exc:
        logger.info("Session rollback because of exception: %s", exc)
        raise


@asynccontextmanager
async def async_session_getter() -> AsyncIterator[AsyncSession]:
    active_scope = _async_scope.get()
    if active_scope is not None:
        task = asyncio.current_task()
        if task is None or active_scope.owner_task_id != id(task):
            raise RuntimeError("an async Unit of Work cannot be shared across tasks")
        yield active_scope.session
        return
    try:
        async with async_domain_uow() as session:
            yield session
    except Exception as exc:
        logger.info("Session rollback because of exception: %s", exc)
        raise


__all__ = [
    "SessionRuntimePort",
    "async_domain_uow",
    "async_session_getter",
    "domain_uow",
    "session_getter",
]
