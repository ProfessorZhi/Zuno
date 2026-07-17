from __future__ import annotations

from collections.abc import Callable
from contextlib import contextmanager
from typing import Iterator

from sqlmodel import Session

from zuno.platform.database.session import session_getter


class MemoryRuntimeDao:
    """Sync session factory for PHASE07 memory runtime adapters."""

    @staticmethod
    @contextmanager
    def session_scope(session_factory: Callable[[], Session] | None = None) -> Iterator[Session]:
        if session_factory is None:
            with session_getter() as session:
                yield session
            return
        session = session_factory()
        try:
            with session.begin():
                yield session
        finally:
            session.close()


__all__ = ["MemoryRuntimeDao"]
