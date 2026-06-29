import logging
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncIterator, Iterator

from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession

from zuno.database import async_engine, engine

logger = logging.getLogger(__name__)


@contextmanager
def session_getter() -> Iterator[Session]:
    session = Session(engine)
    try:
        yield session
    except Exception as exc:
        logger.info("Session rollback because of exception: %s", exc)
        session.rollback()
        raise
    finally:
        session.close()


@asynccontextmanager
async def async_session_getter() -> AsyncIterator[AsyncSession]:
    session = AsyncSession(async_engine)
    try:
        yield session
    except Exception as exc:
        logger.info("Session rollback because of exception: %s", exc)
        await session.rollback()
        raise
    finally:
        await session.close()


__all__ = ["async_session_getter", "session_getter"]
