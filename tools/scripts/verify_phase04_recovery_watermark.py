from __future__ import annotations

import os
import subprocess
from pathlib import Path
from uuid import uuid4

from sqlalchemy import text

from zuno.platform.database.foundation import (
    InfrastructureConflictError,
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
            text(
                """
                DELETE FROM infra_recovery_set_members
                WHERE recovery_set_id LIKE :prefix OR component_id LIKE :prefix
                """
            ),
            {"prefix": f"phase04-recovery-{marker}%"},
        )
        connection.execute(
            text("DELETE FROM infra_recovery_sets WHERE recovery_set_id LIKE :prefix"),
            {"prefix": f"phase04-recovery-{marker}%"},
        )
        connection.execute(
            text("DELETE FROM infra_recovery_watermarks WHERE component_id LIKE :prefix"),
            {"prefix": f"phase04-recovery-{marker}%"},
        )


def verify_phase04_recovery_watermark() -> list[str]:
    errors = _upgrade_head()
    if errors:
        return errors

    marker = uuid4().hex[:12]
    recovery_point = f"phase04-rp-{marker}-002"
    stale_point = f"phase04-rp-{marker}-001"
    component_ids = (
        f"phase04-recovery-{marker}-db",
        f"phase04-recovery-{marker}-object",
        f"phase04-recovery-{marker}-checkpoint",
        f"phase04-recovery-{marker}-index",
    )
    engine = create_foundation_engine(DATABASE_URL, pool_size=4, max_overflow=2)
    try:
        _cleanup(engine, marker)
        with InfrastructureUnitOfWork(engine) as repo:
            repo.record_recovery_watermark(
                component_id=component_ids[0],
                service_kind="postgresql",
                authority="authoritative",
                watermark=recovery_point,
                owner_id="db-owner",
                payload={"lsn": recovery_point, "scope": "domain-facts"},
            )
            repo.record_recovery_watermark(
                component_id=component_ids[1],
                service_kind="object_manifest",
                authority="authoritative",
                watermark=recovery_point,
                owner_id="object-owner",
                payload={"manifest_watermark": recovery_point},
            )
            repo.record_recovery_watermark(
                component_id=component_ids[2],
                service_kind="checkpoint",
                authority="derived",
                watermark=recovery_point,
                owner_id="checkpoint-owner",
                payload={"checkpoint_watermark": recovery_point},
            )
            repo.record_recovery_watermark(
                component_id=component_ids[3],
                service_kind="derived_index",
                authority="derived",
                watermark=stale_point,
                owner_id="index-owner",
                payload={"index_watermark": stale_point},
            )

        try:
            with InfrastructureUnitOfWork(engine) as repo:
                repo.create_recovery_set(
                    recovery_set_id=f"phase04-recovery-{marker}-mismatch",
                    recovery_point=recovery_point,
                    component_ids=component_ids,
                    owner_id="recovery-owner",
                )
                errors.append("mismatched derived watermark was accepted")
        except InfrastructureConflictError:
            pass

        with InfrastructureUnitOfWork(engine) as repo:
            repo.record_recovery_watermark(
                component_id=component_ids[3],
                service_kind="derived_index",
                authority="derived",
                watermark=recovery_point,
                owner_id="index-owner",
                payload={"index_watermark": recovery_point},
            )
            receipt = repo.create_recovery_set(
                recovery_set_id=f"phase04-recovery-{marker}-verified",
                recovery_point=recovery_point,
                component_ids=component_ids,
                owner_id="recovery-owner",
            )
            if receipt.recovery_point != recovery_point:
                errors.append(f"recovery set point mismatch: {receipt!r}")
            if receipt.component_ids != component_ids:
                errors.append(f"recovery set components mismatch: {receipt!r}")
            if len(receipt.verification_hash) != 64:
                errors.append(f"recovery set verification hash invalid: {receipt!r}")

        with engine.connect() as connection:
            member_count = int(
                connection.execute(
                    text(
                        """
                        SELECT COUNT(*)
                        FROM infra_recovery_set_members
                        WHERE recovery_set_id = :recovery_set_id
                          AND watermark = :recovery_point
                        """
                    ),
                    {
                        "recovery_set_id": f"phase04-recovery-{marker}-verified",
                        "recovery_point": recovery_point,
                    },
                ).scalar_one()
            )
            authorities = {
                str(row.authority)
                for row in connection.execute(
                    text(
                        """
                        SELECT DISTINCT authority
                        FROM infra_recovery_set_members
                        WHERE recovery_set_id = :recovery_set_id
                        """
                    ),
                    {"recovery_set_id": f"phase04-recovery-{marker}-verified"},
                ).all()
            }
        if member_count != len(component_ids):
            errors.append(f"recovery set member count mismatch: {member_count}")
        if authorities != {"authoritative", "derived"}:
            errors.append(f"recovery set authority coverage mismatch: {authorities!r}")
    finally:
        _cleanup(engine, marker)
        engine.dispose()

    return errors


def main() -> int:
    errors = verify_phase04_recovery_watermark()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 recovery watermark verification failed.")
        return 1
    print("PHASE04 recovery watermark verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
