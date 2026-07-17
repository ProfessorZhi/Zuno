from __future__ import annotations

import math
import threading
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

from sqlalchemy import Engine

from zuno.platform.database.foundation import (
    FencingRejectedError,
    FencingToken,
    InfrastructureRepository,
    InfrastructureUnitOfWork,
)

PreparedT = TypeVar("PreparedT")
CommittedT = TypeVar("CommittedT")


@dataclass(frozen=True, slots=True)
class FencedWorkReceipt(Generic[CommittedT]):
    resource_id: str
    owner_id: str
    lease_id: str
    epoch: int
    result: CommittedT


class _LeaseHeartbeat:
    def __init__(
        self,
        *,
        engine: Engine,
        token: FencingToken,
        ttl_seconds: int,
        interval_seconds: float,
    ) -> None:
        self.engine = engine
        self.token = token
        self.ttl_seconds = ttl_seconds
        self.interval_seconds = interval_seconds
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self.error: BaseException | None = None

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=max(5.0, self.interval_seconds * 2))
        if self._thread.is_alive() and self.error is None:
            self.error = TimeoutError("lease heartbeat thread did not stop")

    @property
    def is_alive(self) -> bool:
        return self._thread.is_alive()

    def _run(self) -> None:
        while not self._stop.wait(self.interval_seconds):
            try:
                with InfrastructureUnitOfWork(self.engine) as repo:
                    self.token = repo.renew_lease(self.token, ttl_seconds=self.ttl_seconds)
            except BaseException as exc:
                self.error = exc
                return


class LeaseWorkerCoordinator:
    def __init__(
        self,
        engine: Engine,
        *,
        ttl_seconds: int = 30,
        heartbeat_interval_seconds: float | None = None,
        clock_tolerance_seconds: float = 0,
    ) -> None:
        if ttl_seconds < 1:
            raise ValueError("ttl_seconds must be positive")
        interval = ttl_seconds / 3 if heartbeat_interval_seconds is None else heartbeat_interval_seconds
        if not math.isfinite(interval) or interval <= 0 or interval >= ttl_seconds:
            raise ValueError("heartbeat interval must be finite, positive and shorter than ttl_seconds")
        if not math.isfinite(clock_tolerance_seconds) or clock_tolerance_seconds < 0:
            raise ValueError("clock_tolerance_seconds must be finite and non-negative")
        if clock_tolerance_seconds >= ttl_seconds:
            raise ValueError("clock_tolerance_seconds must be shorter than ttl_seconds")
        self.engine = engine
        self.ttl_seconds = ttl_seconds
        self.heartbeat_interval_seconds = interval
        self.clock_tolerance_seconds = clock_tolerance_seconds

    def acquire(self, *, resource_id: str, owner_id: str) -> FencingToken:
        with InfrastructureUnitOfWork(self.engine) as repo:
            return repo.acquire_lease(
                resource_id=resource_id,
                owner_id=owner_id,
                ttl_seconds=self.ttl_seconds,
            )

    def transfer(self, token: FencingToken, *, new_owner_id: str) -> FencingToken:
        with InfrastructureUnitOfWork(self.engine) as repo:
            return repo.transfer_lease(
                token,
                new_owner_id=new_owner_id,
                ttl_seconds=self.ttl_seconds,
            )

    def cancel(self, token: FencingToken) -> None:
        with InfrastructureUnitOfWork(self.engine) as repo:
            repo.cancel_lease(token)

    def commit(
        self,
        token: FencingToken,
        prepared: PreparedT,
        commit: Callable[[InfrastructureRepository, PreparedT], CommittedT],
    ) -> FencedWorkReceipt[CommittedT]:
        with InfrastructureUnitOfWork(self.engine) as repo:
            repo.assert_fence(
                token,
                clock_tolerance_seconds=self.clock_tolerance_seconds,
            )
            result = commit(repo, prepared)
        return FencedWorkReceipt(
            resource_id=token.resource_id,
            owner_id=token.owner_id,
            lease_id=token.lease_id,
            epoch=token.epoch,
            result=result,
        )

    def execute(
        self,
        *,
        resource_id: str,
        owner_id: str,
        work: Callable[[], PreparedT],
        commit: Callable[[InfrastructureRepository, PreparedT], CommittedT],
    ) -> FencedWorkReceipt[CommittedT]:
        token = self.acquire(resource_id=resource_id, owner_id=owner_id)
        heartbeat = _LeaseHeartbeat(
            engine=self.engine,
            token=token,
            ttl_seconds=self.ttl_seconds,
            interval_seconds=self.heartbeat_interval_seconds,
        )
        heartbeat.start()
        try:
            prepared = work()
            heartbeat.stop()
            self._raise_heartbeat_error(heartbeat)
            return self.commit(token, prepared, commit)
        finally:
            if heartbeat.is_alive:
                heartbeat.stop()

    @staticmethod
    def _raise_heartbeat_error(heartbeat: _LeaseHeartbeat) -> None:
        if heartbeat.error is None:
            return
        if isinstance(heartbeat.error, FencingRejectedError):
            raise heartbeat.error
        raise FencingRejectedError("lease heartbeat failed; ownership is unknown") from heartbeat.error


__all__ = ["FencedWorkReceipt", "LeaseWorkerCoordinator"]
