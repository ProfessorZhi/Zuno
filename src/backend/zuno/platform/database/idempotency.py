from __future__ import annotations

import math
import threading
from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy import Engine

from zuno.platform.database.foundation import (
    FencingRejectedError,
    IdempotencyClaimReceipt,
    InfrastructureUnitOfWork,
)


class IdempotencyClaimBusyError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class IdempotencyWorkReceipt:
    status: str
    generation: int
    result_ref: str
    executed: bool
    reconciled: bool
    replayed: bool


class _ClaimHeartbeat:
    def __init__(
        self,
        *,
        engine: Engine,
        tenant_id: str | None,
        scope: str,
        key: str,
        owner: str,
        generation: int,
        ttl_seconds: int,
        interval_seconds: float,
    ) -> None:
        self.engine = engine
        self.tenant_id = tenant_id
        self.scope = scope
        self.key = key
        self.owner = owner
        self.generation = generation
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
            self.error = TimeoutError("idempotency heartbeat thread did not stop")

    @property
    def is_alive(self) -> bool:
        return self._thread.is_alive()

    def _run(self) -> None:
        while not self._stop.wait(self.interval_seconds):
            try:
                with InfrastructureUnitOfWork(self.engine, tenant_id=self.tenant_id) as repo:
                    repo.renew_idempotency(
                        scope=self.scope,
                        key=self.key,
                        owner=self.owner,
                        generation=self.generation,
                        ttl_seconds=self.ttl_seconds,
                    )
            except BaseException as exc:
                self.error = exc
                return


class IdempotencyWorkerSupervisor:
    def __init__(
        self,
        engine: Engine,
        *,
        tenant_id: str | None = None,
        ttl_seconds: int = 30,
        heartbeat_interval_seconds: float | None = None,
    ) -> None:
        if ttl_seconds < 1:
            raise ValueError("ttl_seconds must be positive")
        interval = ttl_seconds / 3 if heartbeat_interval_seconds is None else heartbeat_interval_seconds
        if not math.isfinite(interval) or interval <= 0 or interval >= ttl_seconds:
            raise ValueError("heartbeat interval must be finite, positive and shorter than ttl_seconds")
        self.engine = engine
        self.tenant_id = tenant_id
        self.ttl_seconds = ttl_seconds
        self.heartbeat_interval_seconds = interval

    def execute(
        self,
        *,
        scope: str,
        key: str,
        owner: str,
        request: dict[str, object],
        operation: Callable[[], str],
        reconcile: Callable[[], str | None],
    ) -> IdempotencyWorkReceipt:
        claim = self._claim(scope=scope, key=key, owner=owner, request=request)
        if claim.status == "completed":
            return IdempotencyWorkReceipt(
                status=claim.status,
                generation=claim.generation,
                result_ref=claim.result_ref,
                executed=False,
                reconciled=False,
                replayed=True,
            )
        if not claim.acquired:
            raise IdempotencyClaimBusyError("idempotency claim is held by another live owner")

        heartbeat = _ClaimHeartbeat(
            engine=self.engine,
            tenant_id=self.tenant_id,
            scope=scope,
            key=key,
            owner=owner,
            generation=claim.generation,
            ttl_seconds=self.ttl_seconds,
            interval_seconds=self.heartbeat_interval_seconds,
        )
        heartbeat.start()
        try:
            recovered = reconcile()
            if recovered:
                heartbeat.stop()
                self._raise_heartbeat_error(heartbeat)
                self._complete(scope, key, owner, claim.generation, recovered)
                return IdempotencyWorkReceipt(
                    status="completed",
                    generation=claim.generation,
                    result_ref=recovered,
                    executed=False,
                    reconciled=True,
                    replayed=False,
                )

            try:
                result_ref = operation()
            except Exception:
                recovered = reconcile()
                heartbeat.stop()
                self._raise_heartbeat_error(heartbeat)
                if recovered:
                    self._complete(scope, key, owner, claim.generation, recovered)
                    return IdempotencyWorkReceipt(
                        status="completed",
                        generation=claim.generation,
                        result_ref=recovered,
                        executed=True,
                        reconciled=True,
                        replayed=False,
                    )
                self._abort(scope, key, owner, claim.generation)
                raise

            heartbeat.stop()
            self._raise_heartbeat_error(heartbeat)
            if not result_ref:
                self._abort(scope, key, owner, claim.generation)
                raise ValueError("idempotent operation must return a non-empty result_ref")
            self._complete(scope, key, owner, claim.generation, result_ref)
            return IdempotencyWorkReceipt(
                status="completed",
                generation=claim.generation,
                result_ref=result_ref,
                executed=True,
                reconciled=False,
                replayed=False,
            )
        finally:
            if heartbeat.is_alive:
                heartbeat.stop()

    def _claim(
        self,
        *,
        scope: str,
        key: str,
        owner: str,
        request: dict[str, object],
    ) -> IdempotencyClaimReceipt:
        with InfrastructureUnitOfWork(self.engine, tenant_id=self.tenant_id) as repo:
            return repo.claim_idempotency_receipt(
                scope=scope,
                key=key,
                owner=owner,
                request=request,
                ttl_seconds=self.ttl_seconds,
            )

    def _complete(self, scope: str, key: str, owner: str, generation: int, result_ref: str) -> None:
        with InfrastructureUnitOfWork(self.engine, tenant_id=self.tenant_id) as repo:
            repo.complete_idempotency(
                scope=scope,
                key=key,
                owner=owner,
                generation=generation,
                result_ref=result_ref,
            )

    def _abort(self, scope: str, key: str, owner: str, generation: int) -> None:
        with InfrastructureUnitOfWork(self.engine, tenant_id=self.tenant_id) as repo:
            repo.abort_idempotency(
                scope=scope,
                key=key,
                owner=owner,
                generation=generation,
            )

    @staticmethod
    def _raise_heartbeat_error(heartbeat: _ClaimHeartbeat) -> None:
        if heartbeat.error is None:
            return
        if isinstance(heartbeat.error, FencingRejectedError):
            raise heartbeat.error
        raise FencingRejectedError("idempotency heartbeat failed; claim ownership is unknown") from heartbeat.error


__all__ = [
    "IdempotencyClaimBusyError",
    "IdempotencyWorkReceipt",
    "IdempotencyWorkerSupervisor",
]
