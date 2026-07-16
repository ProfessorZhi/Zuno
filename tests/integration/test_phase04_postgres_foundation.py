from __future__ import annotations

import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import pytest
from sqlalchemy import text

from zuno.platform.database.foundation import (
    FencingRejectedError,
    InfrastructureConflictError,
    InfrastructureUnitOfWork,
    create_foundation_engine,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno",
)


@pytest.fixture(scope="session", autouse=True)
def migrated_postgres() -> None:
    result = subprocess.run(
        ["alembic", "-c", "infra/db/alembic.ini", "upgrade", "head"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.fixture()
def engine(migrated_postgres):
    engine = create_foundation_engine(DATABASE_URL)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                TRUNCATE
                    infra_outbox_events,
                    infra_inbox_messages,
                    infra_idempotency_claims,
                    infra_worker_leases,
                    infra_object_manifests,
                    infra_checkpoints
                RESTART IDENTITY
                """
            )
        )
    try:
        yield engine
    finally:
        engine.dispose()


def test_uow_commit_and_rollback(engine) -> None:
    uow = InfrastructureUnitOfWork(engine)
    with uow as repo:
        event_id = repo.enqueue_outbox(
            aggregate_id="run-1",
            topic="agent.step",
            payload={"step": 1},
            idempotency_key="idem-1",
        )

    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM infra_outbox_events")).scalar_one() == 1
        assert conn.execute(
            text("SELECT payload_hash FROM infra_outbox_events WHERE event_id = :event_id"),
            {"event_id": event_id},
        ).scalar_one()

    with pytest.raises(RuntimeError):
        with uow as repo:
            repo.enqueue_outbox(
                aggregate_id="run-2",
                topic="agent.step",
                payload={"step": 2},
                idempotency_key="idem-2",
            )
            raise RuntimeError("force rollback")

    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM infra_outbox_events")).scalar_one() == 1


def test_outbox_claim_and_inbox_hash_conflict(engine) -> None:
    uow = InfrastructureUnitOfWork(engine)
    with uow as repo:
        event_id = repo.enqueue_outbox(
            aggregate_id="run-1",
            topic="tool.effect",
            payload={"effect": "prepared"},
            idempotency_key="tool-1",
        )

    with uow as repo:
        assert repo.claim_outbox(worker_id="worker-a") == [event_id]
        assert repo.claim_outbox(worker_id="worker-b") == []
        with pytest.raises(FencingRejectedError):
            repo.complete_outbox(event_id=event_id, worker_id="worker-b")
        repo.complete_outbox(event_id=event_id, worker_id="worker-a")

    with uow as repo:
        first_hash = repo.record_inbox(consumer="consumer-a", message_id="msg-1", payload={"a": 1})
        assert repo.record_inbox(consumer="consumer-a", message_id="msg-1", payload={"a": 1}) == first_hash
        with pytest.raises(InfrastructureConflictError):
            repo.record_inbox(consumer="consumer-a", message_id="msg-1", payload={"a": 2})


def test_idempotency_claim_reuses_result_and_rejects_hash_conflict(engine) -> None:
    uow = InfrastructureUnitOfWork(engine)
    with uow as repo:
        status, generation, result_ref = repo.claim_idempotency(
            scope="tool",
            key="idem-1",
            owner="worker-a",
            request={"operation": "send", "target": "x"},
        )
        assert (status, generation, result_ref) == ("in_progress", 1, "")
        repo.complete_idempotency(scope="tool", key="idem-1", generation=generation, result_ref="effect:1")

    with uow as repo:
        status, generation, result_ref = repo.claim_idempotency(
            scope="tool",
            key="idem-1",
            owner="worker-b",
            request={"operation": "send", "target": "x"},
        )
        assert (status, generation, result_ref) == ("completed", 1, "effect:1")
        with pytest.raises(InfrastructureConflictError):
            repo.claim_idempotency(
                scope="tool",
                key="idem-1",
                owner="worker-b",
                request={"operation": "send", "target": "y"},
            )


def test_idempotency_claim_expiry_renew_and_stale_generation(engine) -> None:
    uow = InfrastructureUnitOfWork(engine)
    with uow as repo:
        status, generation, result_ref = repo.claim_idempotency(
            scope="tool",
            key="idem-expiry",
            owner="worker-a",
            request={"operation": "send", "target": "x"},
            ttl_seconds=30,
        )
        assert (status, generation, result_ref) == ("in_progress", 1, "")
        renewed_at = repo.renew_idempotency(
            scope="tool",
            key="idem-expiry",
            owner="worker-a",
            generation=generation,
            ttl_seconds=120,
        )
        assert renewed_at is not None
        with pytest.raises(FencingRejectedError):
            repo.renew_idempotency(
                scope="tool",
                key="idem-expiry",
                owner="worker-b",
                generation=generation,
                ttl_seconds=120,
            )

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE infra_idempotency_claims
                SET expires_at = now() - interval '1 second'
                WHERE scope = 'tool' AND idempotency_key = 'idem-expiry'
                """
            )
        )

    with uow as repo:
        assert repo.expire_stale_idempotency_claims() == ["tool:idem-expiry"]
        status, replacement_generation, result_ref = repo.claim_idempotency(
            scope="tool",
            key="idem-expiry",
            owner="worker-b",
            request={"operation": "send", "target": "x"},
            ttl_seconds=30,
        )
        assert (status, replacement_generation, result_ref) == ("in_progress", generation + 1, "")
        with pytest.raises(FencingRejectedError):
            repo.complete_idempotency(
                scope="tool",
                key="idem-expiry",
                generation=generation,
                result_ref="effect:stale",
            )
        repo.complete_idempotency(
            scope="tool",
            key="idem-expiry",
            generation=replacement_generation,
            result_ref="effect:new",
        )

    with uow as repo:
        status, generation_after_completion, result_ref = repo.claim_idempotency(
            scope="tool",
            key="idem-expiry",
            owner="worker-c",
            request={"operation": "send", "target": "x"},
        )
        assert (status, generation_after_completion, result_ref) == (
            "completed",
            replacement_generation,
            "effect:new",
        )


def test_idempotency_claim_concurrent_single_winner(engine) -> None:
    contenders = 12
    barrier = Barrier(contenders)

    def claim(index: int):
        barrier.wait(timeout=10)
        uow = InfrastructureUnitOfWork(engine)
        with uow as repo:
            return repo.claim_idempotency_receipt(
                scope="tool",
                key="idem-concurrent",
                owner=f"worker-{index}",
                request={"operation": "send", "target": "x"},
                ttl_seconds=30,
            )

    with ThreadPoolExecutor(max_workers=contenders) as executor:
        receipts = list(executor.map(claim, range(contenders)))

    winners = [receipt for receipt in receipts if receipt.acquired]
    assert len(winners) == 1
    assert winners[0].status == "in_progress"
    assert winners[0].generation == 1
    assert winners[0].result_ref == ""
    assert all(receipt.status == "in_progress" for receipt in receipts)
    assert all(receipt.generation == 1 for receipt in receipts)
    assert all(receipt.result_ref == "" for receipt in receipts)
    assert all(receipt.owner == winners[0].owner for receipt in receipts)

    with engine.connect() as conn:
        assert conn.execute(
            text(
                """
                SELECT count(*)
                FROM infra_idempotency_claims
                WHERE scope = 'tool' AND idempotency_key = 'idem-concurrent'
                """
            )
        ).scalar_one() == 1

    uow = InfrastructureUnitOfWork(engine)
    with uow as repo:
        repo.complete_idempotency(
            scope="tool",
            key="idem-concurrent",
            generation=winners[0].generation,
            result_ref="effect:concurrent",
        )

    with uow as repo:
        receipt = repo.claim_idempotency_receipt(
            scope="tool",
            key="idem-concurrent",
            owner="worker-after",
            request={"operation": "send", "target": "x"},
        )
        assert receipt.status == "completed"
        assert receipt.generation == 1
        assert receipt.result_ref == "effect:concurrent"
        assert receipt.acquired is False


def test_lease_fencing_rejects_late_owner(engine) -> None:
    uow = InfrastructureUnitOfWork(engine)
    with uow as repo:
        token = repo.acquire_lease(resource_id="run-1", owner_id="worker-a", ttl_seconds=30)
        repo.assert_fence(token)
        renewed = repo.renew_lease(token, ttl_seconds=60)
        assert renewed.resource_id == token.resource_id
        assert renewed.owner_id == token.owner_id
        assert renewed.lease_id == token.lease_id
        assert renewed.epoch == token.epoch
        repo.assert_fence(renewed)
        with pytest.raises(FencingRejectedError):
            repo.acquire_lease(resource_id="run-1", owner_id="worker-b", ttl_seconds=30)

    with engine.begin() as conn:
        conn.execute(text("UPDATE infra_worker_leases SET expires_at = now() - interval '1 second'"))

    with uow as repo:
        replacement = repo.acquire_lease(resource_id="run-1", owner_id="worker-b", ttl_seconds=30)
        assert replacement.epoch == renewed.epoch + 1
        with pytest.raises(FencingRejectedError):
            repo.assert_fence(renewed)
        with pytest.raises(FencingRejectedError):
            repo.renew_lease(renewed, ttl_seconds=60)


def test_lease_cancel_allows_transfer_and_rejects_late_result(engine) -> None:
    uow = InfrastructureUnitOfWork(engine)
    with uow as repo:
        token = repo.acquire_lease(resource_id="run-cancel", owner_id="worker-a", ttl_seconds=30)
        repo.cancel_lease(token)
        with pytest.raises(FencingRejectedError):
            repo.assert_fence(token)
        with pytest.raises(FencingRejectedError):
            repo.cancel_lease(token)

    with uow as repo:
        replacement = repo.acquire_lease(resource_id="run-cancel", owner_id="worker-b", ttl_seconds=30)
        assert replacement.epoch == token.epoch + 1
        repo.assert_fence(replacement)


def test_object_manifest_and_checkpoint_hash_boundaries(engine) -> None:
    uow = InfrastructureUnitOfWork(engine)
    with uow as repo:
        object_hash = repo.put_object_manifest(
            object_ref="s3://bucket/object-1",
            content=b"hello",
            owner="input",
            visibility="visible",
        )
        assert len(object_hash) == 64
        with pytest.raises(InfrastructureConflictError):
            repo.put_object_manifest(
                object_ref="s3://bucket/object-1",
                content=b"changed",
                owner="input",
                visibility="visible",
            )

        repo.save_checkpoint(
            thread_id="thread-1",
            checkpoint_id="checkpoint-1",
            generation=1,
            state={"node": "plan"},
            owner="agent-core",
        )
        repo.save_checkpoint(
            thread_id="thread-1",
            checkpoint_id="checkpoint-2",
            generation=2,
            state={"node": "execute"},
            owner="agent-core",
        )
        with pytest.raises(InfrastructureConflictError):
            repo.save_checkpoint(
                thread_id="thread-1",
                checkpoint_id="checkpoint-duplicate",
                generation=2,
                state={"node": "other"},
                owner="agent-core",
            )
        latest = repo.latest_checkpoint(thread_id="thread-1")
        assert latest == {
            "checkpoint_id": "checkpoint-2",
            "generation": 2,
            "state": {"node": "execute"},
        }
