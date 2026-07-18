from __future__ import annotations

import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

from sqlalchemy import text

from zuno.platform.database.foundation import (
    CapacityBackpressureError,
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
                "DELETE FROM infra_capacity_reservations WHERE resource_id LIKE :prefix"
            ),
            {"prefix": f"phase04-capacity-{marker}%"},
        )
        connection.execute(
            text(
                "DELETE FROM infra_capacity_admissions WHERE resource_id LIKE :prefix"
            ),
            {"prefix": f"phase04-capacity-{marker}%"},
        )


def _try_reserve(resource_id: str, owner_id: str) -> tuple[str, str]:
    engine = create_foundation_engine(DATABASE_URL)
    try:
        with InfrastructureUnitOfWork(engine) as repo:
            receipt = repo.reserve_capacity(
                resource_id=resource_id,
                owner_id=owner_id,
                amount=1,
                ttl_seconds=30,
            )
            return ("reserved", receipt.reservation_id)
    except CapacityBackpressureError:
        return ("backpressure", owner_id)
    finally:
        engine.dispose()


def verify_phase04_capacity_admission() -> list[str]:
    errors = _upgrade_head()
    if errors:
        return errors

    marker = uuid4().hex[:12]
    resource_id = f"phase04-capacity-{marker}"
    engine = create_foundation_engine(DATABASE_URL, pool_size=8, max_overflow=4)
    try:
        _cleanup(engine, marker)
        with InfrastructureUnitOfWork(engine) as repo:
            generation_1 = repo.configure_capacity(
                resource_id=resource_id,
                capacity_limit=1,
                owner_id="capacity-owner",
            )
            if generation_1 != 1:
                errors.append(f"initial capacity generation mismatch: {generation_1}")

        with ThreadPoolExecutor(max_workers=2) as executor:
            outcomes = sorted(
                future.result(timeout=15)
                for future in [
                    executor.submit(_try_reserve, resource_id, "worker-a"),
                    executor.submit(_try_reserve, resource_id, "worker-b"),
                ]
            )
        reserved = [item for item in outcomes if item[0] == "reserved"]
        backpressured = [item for item in outcomes if item[0] == "backpressure"]
        if len(reserved) != 1 or len(backpressured) != 1:
            errors.append(f"capacity reservation did not have one winner: {outcomes!r}")

        reservation_id = reserved[0][1] if reserved else ""
        winning_owner_id = ""
        if reservation_id:
            with engine.connect() as connection:
                winning_owner_id = str(
                    connection.execute(
                        text("""
                            SELECT owner_id
                            FROM infra_capacity_reservations
                            WHERE reservation_id = :reservation_id
                            """),
                        {"reservation_id": reservation_id},
                    ).scalar_one()
                )
        with InfrastructureUnitOfWork(engine) as repo:
            try:
                repo.reserve_capacity(
                    resource_id=resource_id,
                    owner_id="worker-c",
                    amount=1,
                    ttl_seconds=30,
                )
                errors.append("capacity exhaustion did not return backpressure")
            except CapacityBackpressureError:
                pass
            try:
                repo.release_capacity(
                    reservation_id=reservation_id,
                    owner_id="wrong-owner",
                )
                errors.append("wrong owner released a capacity reservation")
            except FencingRejectedError:
                pass
            repo.release_capacity(
                reservation_id=reservation_id,
                owner_id=winning_owner_id,
            )

        with InfrastructureUnitOfWork(engine) as repo:
            after_release = repo.reserve_capacity(
                resource_id=resource_id,
                owner_id="worker-after-release",
                amount=1,
                ttl_seconds=30,
            )
            if after_release.remaining_capacity != 0:
                errors.append(
                    f"capacity remaining after release mismatch: {after_release!r}"
                )
            repo.release_capacity(
                reservation_id=after_release.reservation_id,
                owner_id="worker-after-release",
            )
            generation_2 = repo.set_capacity_drain(
                resource_id=resource_id,
                drained=True,
                owner_id="drain-owner",
            )
            if generation_2 <= after_release.generation:
                errors.append("drain did not advance capacity generation")
            try:
                repo.reserve_capacity(
                    resource_id=resource_id,
                    owner_id="worker-drained",
                    amount=1,
                    ttl_seconds=30,
                )
                errors.append("drained admission accepted a new capacity reservation")
            except CapacityBackpressureError:
                pass
    finally:
        _cleanup(engine, marker)
        engine.dispose()

    return errors


def main() -> int:
    errors = verify_phase04_capacity_admission()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 capacity admission verification failed.")
        return 1
    print("PHASE04 capacity admission verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
