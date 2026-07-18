from __future__ import annotations

import os
import subprocess
from pathlib import Path
from uuid import uuid4

from sqlalchemy import text

from zuno.platform.database.foundation import (
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
            text(
                """
                DELETE FROM infra_active_snapshot_refs
                WHERE target_id LIKE :prefix OR snapshot_id LIKE :prefix
                """
            ),
            {"prefix": f"phase04-cutover-{marker}%"},
        )
        connection.execute(
            text(
                """
                UPDATE infra_cutover_targets
                SET active_snapshot_id = NULL
                WHERE target_id LIKE :prefix
                """
            ),
            {"prefix": f"phase04-cutover-{marker}%"},
        )
        connection.execute(
            text("DELETE FROM infra_cutover_snapshots WHERE target_id LIKE :prefix"),
            {"prefix": f"phase04-cutover-{marker}%"},
        )
        connection.execute(
            text("DELETE FROM infra_cutover_targets WHERE target_id LIKE :prefix"),
            {"prefix": f"phase04-cutover-{marker}%"},
        )


def _snapshot_statuses(engine, target_id: str) -> dict[str, str]:
    with engine.connect() as connection:
        return {
            str(row.snapshot_id): str(row.status)
            for row in connection.execute(
                text(
                    """
                    SELECT snapshot_id, status
                    FROM infra_cutover_snapshots
                    WHERE target_id = :target_id
                    ORDER BY snapshot_id
                    """
                ),
                {"target_id": target_id},
            ).all()
        }


def verify_phase04_cutover_snapshot() -> list[str]:
    errors = _upgrade_head()
    if errors:
        return errors

    marker = uuid4().hex[:12]
    target_id = f"phase04-cutover-{marker}"
    snapshot_1 = f"phase04-cutover-{marker}-snapshot-1"
    snapshot_2 = f"phase04-cutover-{marker}-snapshot-2"
    engine = create_foundation_engine(DATABASE_URL, pool_size=4, max_overflow=2)
    try:
        _cleanup(engine, marker)
        with InfrastructureUnitOfWork(engine) as repo:
            initial_generation = repo.configure_cutover_target(
                target_id=target_id,
                owner_id="cutover-owner",
            )
            if initial_generation != 1:
                errors.append(f"initial cutover generation mismatch: {initial_generation}")
            repo.register_cutover_snapshot(
                target_id=target_id,
                snapshot_id=snapshot_1,
                owner_id="snapshot-owner",
                payload={"version": 1, "marker": marker},
            )
            activation_1 = repo.activate_cutover_snapshot(
                target_id=target_id,
                snapshot_id=snapshot_1,
                expected_generation=1,
                owner_id="cutover-owner",
            )
            if activation_1.active_generation != 2:
                errors.append(f"first activation generation mismatch: {activation_1!r}")

        with InfrastructureUnitOfWork(engine) as repo:
            active_ref = repo.acquire_active_snapshot_ref(
                target_id=target_id,
                owner_id="reader-a",
            )
            if active_ref.snapshot_id != snapshot_1 or active_ref.generation != 2:
                errors.append(f"active snapshot ref mismatch: {active_ref!r}")
            repo.register_cutover_snapshot(
                target_id=target_id,
                snapshot_id=snapshot_2,
                owner_id="snapshot-owner",
                payload={"version": 2, "marker": marker},
            )

        try:
            with InfrastructureUnitOfWork(engine) as repo:
                repo.activate_cutover_snapshot(
                    target_id=target_id,
                    snapshot_id=snapshot_2,
                    expected_generation=1,
                    owner_id="stale-writer",
                )
                errors.append("stale cutover generation was accepted")
        except FencingRejectedError:
            pass

        with InfrastructureUnitOfWork(engine) as repo:
            activation_2 = repo.activate_cutover_snapshot(
                target_id=target_id,
                snapshot_id=snapshot_2,
                expected_generation=2,
                owner_id="cutover-owner",
            )
            if (
                activation_2.previous_generation != 2
                or activation_2.active_generation != 3
            ):
                errors.append(f"second activation generation mismatch: {activation_2!r}")

        try:
            with InfrastructureUnitOfWork(engine) as repo:
                repo.retire_cutover_snapshot(
                    target_id=target_id,
                    snapshot_id=snapshot_1,
                    owner_id="retire-owner",
                )
                errors.append("active snapshot reference did not block retirement")
        except FencingRejectedError:
            pass

        try:
            with InfrastructureUnitOfWork(engine) as repo:
                repo.retire_cutover_snapshot(
                    target_id=target_id,
                    snapshot_id=snapshot_2,
                    owner_id="retire-owner",
                )
                errors.append("current active snapshot was retired")
        except FencingRejectedError:
            pass

        with InfrastructureUnitOfWork(engine) as repo:
            repo.release_active_snapshot_ref(
                ref_id=active_ref.ref_id,
                owner_id="reader-a",
            )
            repo.retire_cutover_snapshot(
                target_id=target_id,
                snapshot_id=snapshot_1,
                owner_id="retire-owner",
            )

        statuses = _snapshot_statuses(engine, target_id)
        expected_statuses = {snapshot_1: "retired", snapshot_2: "active"}
        if statuses != expected_statuses:
            errors.append(f"unexpected cutover snapshot statuses: {statuses!r}")
    finally:
        _cleanup(engine, marker)
        engine.dispose()

    return errors


def main() -> int:
    errors = verify_phase04_cutover_snapshot()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 cutover snapshot verification failed.")
        return 1
    print("PHASE04 cutover snapshot verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
