from __future__ import annotations

import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event
from uuid import uuid4

from sqlalchemy import text

from zuno.platform.database.foundation import (
    FencingRejectedError,
    InfrastructureUnitOfWork,
    create_foundation_engine,
)
from zuno.platform.database.idempotency import (
    IdempotencyClaimBusyError,
    IdempotencyWorkerSupervisor,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno",
)
SCOPE = "phase04-idempotency-supervision"


def _crashed_effect_owner_code() -> str:
    return """
import os

from zuno.platform.database.foundation import InfrastructureUnitOfWork, create_foundation_engine

engine = create_foundation_engine(os.environ["ZUNO_TEST_POSTGRES_URL"])
marker = os.environ["ZUNO_IDEMPOTENCY_MARKER"]
try:
    with InfrastructureUnitOfWork(engine) as repo:
        claim = repo.claim_idempotency_receipt(
            scope="phase04-idempotency-supervision",
            key=f"lost-completion-{marker}",
            owner="worker-crashed-after-effect",
            request={"operation": "publish", "marker": marker},
            ttl_seconds=300,
        )
        assert claim.acquired is True
        event_id = repo.enqueue_outbox(
            aggregate_id=f"idempotency-effect-{marker}",
            topic="phase04.idempotency.effect",
            payload={"marker": marker},
            idempotency_key=f"idempotency-effect-{marker}",
        )
        assert event_id
finally:
    engine.dispose()

os._exit(0)
"""


def _cleanup(engine, marker: str) -> None:
    with engine.begin() as connection:
        connection.execute(
            text("DELETE FROM infra_idempotency_claims WHERE scope = :scope"),
            {"scope": SCOPE},
        )
        connection.execute(
            text("DELETE FROM infra_outbox_events WHERE aggregate_id = :aggregate_id"),
            {"aggregate_id": f"idempotency-effect-{marker}"},
        )


def _verify_owner_expiry_boundary(engine, marker: str, errors: list[str]) -> None:
    key = f"owner-boundary-{marker}"
    request = {"operation": "owner-boundary", "marker": marker}
    with InfrastructureUnitOfWork(engine) as repo:
        claim = repo.claim_idempotency_receipt(
            scope=SCOPE,
            key=key,
            owner="owner-a",
            request=request,
            ttl_seconds=30,
        )
        try:
            repo.complete_idempotency(
                scope=SCOPE,
                key=key,
                owner="owner-b",
                generation=claim.generation,
                result_ref="effect:wrong-owner",
            )
            errors.append("wrong owner completed a live idempotency claim")
        except FencingRejectedError:
            pass

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                UPDATE infra_idempotency_claims
                SET expires_at = now() - interval '1 second'
                WHERE scope = :scope AND idempotency_key = :key
                """
            ),
            {"scope": SCOPE, "key": key},
        )

    with InfrastructureUnitOfWork(engine) as repo:
        try:
            repo.complete_idempotency(
                scope=SCOPE,
                key=key,
                owner="owner-a",
                generation=claim.generation,
                result_ref="effect:expired-owner",
            )
            errors.append("expired owner completed an idempotency claim before replacement")
        except FencingRejectedError:
            pass
        repo.abort_idempotency(
            scope=SCOPE,
            key=key,
            owner="owner-a",
            generation=claim.generation,
        )
        replacement = repo.claim_idempotency_receipt(
            scope=SCOPE,
            key=key,
            owner="owner-b",
            request=request,
            ttl_seconds=30,
        )
        if not replacement.acquired or replacement.generation != claim.generation + 1:
            errors.append(f"aborted claim did not transfer to the next generation: {replacement!r}")
        try:
            repo.abort_idempotency(
                scope=SCOPE,
                key=key,
                owner="owner-a",
                generation=claim.generation,
            )
            errors.append("stale owner aborted a replacement idempotency generation")
        except FencingRejectedError:
            pass
        repo.complete_idempotency(
            scope=SCOPE,
            key=key,
            owner="owner-b",
            generation=replacement.generation,
            result_ref="effect:owner-b",
        )


def _verify_heartbeat_and_replay(engine, marker: str, errors: list[str]) -> None:
    key = f"heartbeat-{marker}"
    request = {"operation": "long-task", "marker": marker}
    started = Event()
    executions: list[str] = []
    supervisor = IdempotencyWorkerSupervisor(
        engine,
        ttl_seconds=1,
        heartbeat_interval_seconds=0.2,
    )

    def operation() -> str:
        executions.append("worker-long")
        started.set()
        time.sleep(1.6)
        return f"effect:heartbeat:{marker}"

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            supervisor.execute,
            scope=SCOPE,
            key=key,
            owner="worker-long",
            request=request,
            operation=operation,
            reconcile=lambda: None,
        )
        if not started.wait(timeout=5):
            errors.append("long idempotent operation did not start")
        time.sleep(1.2)
        with InfrastructureUnitOfWork(engine) as repo:
            contender = repo.claim_idempotency_receipt(
                scope=SCOPE,
                key=key,
                owner="worker-contender",
                request=request,
                ttl_seconds=1,
            )
        if contender.acquired or contender.owner != "worker-long" or contender.generation != 1:
            errors.append(f"heartbeat did not preserve the live owner: {contender!r}")
        receipt = future.result(timeout=10)

    if (
        receipt.status != "completed"
        or receipt.result_ref != f"effect:heartbeat:{marker}"
        or not receipt.executed
        or receipt.reconciled
        or receipt.replayed
        or executions != ["worker-long"]
    ):
        errors.append(f"heartbeat-supervised completion mismatch: {receipt!r}, {executions!r}")

    replay = supervisor.execute(
        scope=SCOPE,
        key=key,
        owner="worker-replay",
        request=request,
        operation=lambda: (_ for _ in ()).throw(RuntimeError("replay executed operation")),
        reconcile=lambda: None,
    )
    if not replay.replayed or replay.executed or replay.result_ref != receipt.result_ref:
        errors.append(f"completed supervisor result did not replay: {replay!r}")

    with InfrastructureUnitOfWork(engine) as repo:
        busy = repo.claim_idempotency_receipt(
            scope=SCOPE,
            key=f"busy-{marker}",
            owner="busy-owner-a",
            request=request,
            ttl_seconds=30,
        )
    try:
        supervisor.execute(
            scope=SCOPE,
            key=f"busy-{marker}",
            owner="busy-owner-b",
            request=request,
            operation=lambda: "effect:must-not-run",
            reconcile=lambda: None,
        )
        errors.append("worker supervisor executed while another live owner held the claim")
    except IdempotencyClaimBusyError:
        pass
    if not busy.acquired:
        errors.append("busy-owner setup did not acquire its claim")


def _verify_abort_and_retry(engine, marker: str, errors: list[str]) -> None:
    key = f"abort-{marker}"
    request = {"operation": "abort", "marker": marker}
    supervisor = IdempotencyWorkerSupervisor(engine, ttl_seconds=5, heartbeat_interval_seconds=1)
    try:
        supervisor.execute(
            scope=SCOPE,
            key=key,
            owner="worker-failing",
            request=request,
            operation=lambda: (_ for _ in ()).throw(RuntimeError("deterministic failure")),
            reconcile=lambda: None,
        )
        errors.append("deterministic operation failure was swallowed")
    except RuntimeError as exc:
        if str(exc) != "deterministic failure":
            errors.append(f"supervisor raised the wrong deterministic error: {exc!r}")

    retry = supervisor.execute(
        scope=SCOPE,
        key=key,
        owner="worker-retry",
        request=request,
        operation=lambda: f"effect:retry:{marker}",
        reconcile=lambda: None,
    )
    if retry.generation != 2 or not retry.executed or retry.result_ref != f"effect:retry:{marker}":
        errors.append(f"aborted claim did not execute at the next generation: {retry!r}")


def _verify_process_cancellation_propagates(engine, marker: str, errors: list[str]) -> None:
    key = f"process-cancel-{marker}"
    supervisor = IdempotencyWorkerSupervisor(engine, ttl_seconds=5, heartbeat_interval_seconds=1)
    try:
        supervisor.execute(
            scope=SCOPE,
            key=key,
            owner="worker-cancelled",
            request={"operation": "cancel", "marker": marker},
            operation=lambda: (_ for _ in ()).throw(KeyboardInterrupt()),
            reconcile=lambda: None,
        )
        errors.append("worker supervisor swallowed process-level cancellation")
    except KeyboardInterrupt:
        pass

    with InfrastructureUnitOfWork(engine) as repo:
        state = repo.claim_idempotency_receipt(
            scope=SCOPE,
            key=key,
            owner="worker-after-cancel",
            request={"operation": "cancel", "marker": marker},
            ttl_seconds=5,
        )
        if state.acquired or state.owner != "worker-cancelled" or state.status != "in_progress":
            errors.append(f"process cancellation changed an unknown-effect claim: {state!r}")
        repo.abort_idempotency(
            scope=SCOPE,
            key=key,
            owner="worker-cancelled",
            generation=state.generation,
        )


def _verify_effect_reconciliation_after_process_exit(engine, marker: str, errors: list[str]) -> None:
    key = f"lost-completion-{marker}"
    request = {"operation": "publish", "marker": marker}
    env = os.environ.copy()
    env["ZUNO_TEST_POSTGRES_URL"] = DATABASE_URL
    env["ZUNO_IDEMPOTENCY_MARKER"] = marker
    result = subprocess.run(
        [sys.executable, "-c", _crashed_effect_owner_code()],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
    )
    if result.returncode != 0:
        errors.append(
            "effect owner subprocess failed before exit simulation: "
            f"returncode={result.returncode} stdout={result.stdout!r} stderr={result.stderr!r}"
        )
        return

    with engine.connect() as connection:
        state = connection.execute(
            text(
                """
                SELECT claim.status, claim.generation, event.event_id
                FROM infra_idempotency_claims AS claim
                JOIN infra_outbox_events AS event
                  ON event.idempotency_key = :effect_key
                WHERE claim.scope = :scope AND claim.idempotency_key = :key
                """
            ),
            {
                "scope": SCOPE,
                "key": key,
                "effect_key": f"idempotency-effect-{marker}",
            },
        ).one_or_none()
    if state is None or state.status != "in_progress" or state.generation != 1:
        errors.append(f"crashed effect owner did not leave the expected durable boundary: {state!r}")
        return

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                UPDATE infra_idempotency_claims
                SET expires_at = now() - interval '1 second'
                WHERE scope = :scope AND idempotency_key = :key
                """
            ),
            {"scope": SCOPE, "key": key},
        )

    operation_calls: list[str] = []

    def reconcile() -> str | None:
        with engine.connect() as connection:
            event_id = connection.execute(
                text(
                    """
                    SELECT event_id
                    FROM infra_outbox_events
                    WHERE idempotency_key = :effect_key
                    """
                ),
                {"effect_key": f"idempotency-effect-{marker}"},
            ).scalar_one_or_none()
        return None if event_id is None else str(event_id)

    supervisor = IdempotencyWorkerSupervisor(engine, ttl_seconds=5, heartbeat_interval_seconds=1)
    recovered = supervisor.execute(
        scope=SCOPE,
        key=key,
        owner="worker-reconciler",
        request=request,
        operation=lambda: operation_calls.append("called") or "effect:duplicate",
        reconcile=reconcile,
    )
    if (
        recovered.generation != 2
        or recovered.result_ref != str(state.event_id)
        or recovered.executed
        or not recovered.reconciled
        or operation_calls
    ):
        errors.append(f"lost completion did not reconcile without re-execution: {recovered!r}")

    with InfrastructureUnitOfWork(engine) as repo:
        try:
            repo.complete_idempotency(
                scope=SCOPE,
                key=key,
                owner="worker-crashed-after-effect",
                generation=1,
                result_ref="effect:stale",
            )
            errors.append("crashed effect owner completed after reconciliation advanced generation")
        except FencingRejectedError:
            pass


def verify_phase04_idempotency_supervision() -> list[str]:
    marker = uuid4().hex
    engine = create_foundation_engine(DATABASE_URL, pool_size=8, max_overflow=4, pool_timeout=5)
    errors: list[str] = []
    try:
        _cleanup(engine, marker)
        _verify_owner_expiry_boundary(engine, marker, errors)
        _verify_heartbeat_and_replay(engine, marker, errors)
        _verify_abort_and_retry(engine, marker, errors)
        _verify_process_cancellation_propagates(engine, marker, errors)
        _verify_effect_reconciliation_after_process_exit(engine, marker, errors)
    finally:
        _cleanup(engine, marker)
        engine.dispose()
    return errors


def main() -> int:
    errors = verify_phase04_idempotency_supervision()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 idempotency supervision verification failed.")
        return 1
    print("PHASE04 idempotency supervision verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
