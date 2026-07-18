from __future__ import annotations

import os
import subprocess
from pathlib import Path
from uuid import uuid4

from sqlalchemy import text

from zuno.platform.database.foundation import (
    AuditCapacityError,
    AuditPersistenceReceipt,
    FencingRejectedError,
    InfrastructureUnitOfWork,
    create_foundation_engine,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno",
)


def _upgrade_head() -> list[str]:
    result = subprocess.run(
        ["alembic", "-c", "infra/db/alembic.ini", "upgrade", "head"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    if result.returncode != 0:
        return [f"alembic upgrade head failed: {result.stdout}{result.stderr}"]
    return []


def _cleanup(engine, marker: str) -> None:
    with engine.begin() as connection:
        connection.execute(
            text("""
                DELETE FROM infra_outbox_events
                WHERE aggregate_id LIKE :prefix OR idempotency_key LIKE :prefix
                """),
            {"prefix": f"phase04-audit-{marker}%"},
        )
        connection.execute(
            text("""
                DELETE FROM infra_mandatory_audit_events
                WHERE channel_id LIKE :prefix OR effect_id LIKE :prefix
                """),
            {"prefix": f"phase04-audit-{marker}%"},
        )
        connection.execute(
            text("DELETE FROM infra_audit_channels WHERE channel_id LIKE :prefix"),
            {"prefix": f"phase04-audit-{marker}%"},
        )


def _effect_count(engine, effect_id: str) -> int:
    with engine.connect() as connection:
        return int(
            connection.execute(
                text("""
                    SELECT COUNT(*)
                    FROM infra_outbox_events
                    WHERE aggregate_id = :effect_id
                    """),
                {"effect_id": effect_id},
            ).scalar_one()
        )


def _run_effect_after_audit(
    engine,
    *,
    receipt: AuditPersistenceReceipt,
) -> str:
    with InfrastructureUnitOfWork(engine) as repo:
        repo.assert_audit_durable_for_effect(
            audit_id=receipt.audit_id,
            effect_id=receipt.effect_id,
            owner_id=receipt.owner_id,
        )
        event_id = repo.enqueue_outbox(
            aggregate_id=receipt.effect_id,
            topic="phase04.audit.effect",
            payload={
                "audit_id": receipt.audit_id,
                "effect_id": receipt.effect_id,
                "payload_hash": receipt.payload_hash,
            },
            idempotency_key=receipt.effect_id,
            tenant_id="phase04-audit",
        )
        repo.mark_audited_effect_observed(
            audit_id=receipt.audit_id,
            effect_id=receipt.effect_id,
            owner_id=receipt.owner_id,
        )
        return event_id


def verify_phase04_mandatory_audit() -> list[str]:
    errors = _upgrade_head()
    if errors:
        return errors

    marker = uuid4().hex[:12]
    channel_id = f"phase04-audit-{marker}"
    effect_1 = f"phase04-audit-{marker}-effect-1"
    effect_2 = f"phase04-audit-{marker}-effect-2"
    effect_without_audit = f"phase04-audit-{marker}-effect-without-audit"
    engine = create_foundation_engine(DATABASE_URL, pool_size=4, max_overflow=2)
    try:
        _cleanup(engine, marker)
        with InfrastructureUnitOfWork(engine) as repo:
            generation_1 = repo.configure_audit_channel(
                channel_id=channel_id,
                capacity_limit=1,
                owner_id="audit-owner",
                fail_mode="fail_closed",
            )
            if generation_1 != 1:
                errors.append(
                    f"initial audit channel generation mismatch: {generation_1}"
                )

        try:
            with InfrastructureUnitOfWork(engine) as repo:
                repo.assert_audit_durable_for_effect(
                    audit_id="audit:missing",
                    effect_id=effect_without_audit,
                    owner_id="worker-without-audit",
                )
                repo.enqueue_outbox(
                    aggregate_id=effect_without_audit,
                    topic="phase04.audit.effect",
                    payload={"unexpected": "effect_without_durable_audit"},
                    idempotency_key=effect_without_audit,
                    tenant_id="phase04-audit",
                )
                errors.append("effect was accepted without durable mandatory audit")
        except FencingRejectedError:
            pass
        if _effect_count(engine, effect_without_audit) != 0:
            errors.append("effect without durable audit reached outbox")

        with InfrastructureUnitOfWork(engine) as repo:
            receipt_1 = repo.record_mandatory_audit(
                channel_id=channel_id,
                effect_id=effect_1,
                owner_id="worker-1",
                payload={"effect_id": effect_1, "risk": "mandatory"},
            )
            if receipt_1.remaining_capacity != 0:
                errors.append(f"unexpected audit remaining capacity: {receipt_1!r}")

        try:
            with InfrastructureUnitOfWork(engine) as repo:
                repo.record_mandatory_audit(
                    channel_id=channel_id,
                    effect_id=effect_2,
                    owner_id="worker-2",
                    payload={"effect_id": effect_2, "risk": "mandatory"},
                )
                errors.append("audit capacity exhaustion did not fail closed")
        except AuditCapacityError:
            pass
        if _effect_count(engine, effect_2) != 0:
            errors.append("capacity-failed audit still produced an effect")

        event_1 = _run_effect_after_audit(engine, receipt=receipt_1)
        if not event_1:
            errors.append("effect after durable audit did not return an outbox event")
        if _effect_count(engine, effect_1) != 1:
            errors.append("effect after durable audit was not persisted once")

        with InfrastructureUnitOfWork(engine) as repo:
            receipt_2 = repo.record_mandatory_audit(
                channel_id=channel_id,
                effect_id=effect_2,
                owner_id="worker-2",
                payload={"effect_id": effect_2, "risk": "mandatory"},
            )
        _run_effect_after_audit(engine, receipt=receipt_2)
        if _effect_count(engine, effect_2) != 1:
            errors.append("audit capacity did not recover after observed effect")

        with engine.connect() as connection:
            statuses = {
                str(row.effect_id): str(row.status)
                for row in connection.execute(
                    text("""
                        SELECT effect_id, status
                        FROM infra_mandatory_audit_events
                        WHERE channel_id = :channel_id
                        """),
                    {"channel_id": channel_id},
                ).all()
            }
        if statuses != {effect_1: "effect_observed", effect_2: "effect_observed"}:
            errors.append(f"unexpected mandatory audit statuses: {statuses!r}")
    finally:
        _cleanup(engine, marker)
        engine.dispose()

    return errors


def main() -> int:
    errors = verify_phase04_mandatory_audit()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 mandatory audit verification failed.")
        return 1
    print("PHASE04 mandatory audit verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
