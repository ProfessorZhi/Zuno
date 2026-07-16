from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from sqlalchemy import text

from zuno.platform.database.foundation import (
    InfrastructureRepository,
    create_foundation_engine,
    run_transaction_with_retry,
)

DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/zuno"


def verify_phase04_postgres_deadlock_retry() -> list[str]:
    engine = create_foundation_engine(DATABASE_URL)
    errors: list[str] = []
    resources = ("phase04-deadlock-a", "phase04-deadlock-b")
    barrier = Barrier(2)
    invocations = {"worker-a": 0, "worker-b": 0}
    try:
        with engine.begin() as conn:
            conn.execute(
                text("DELETE FROM infra_worker_leases WHERE resource_id = ANY(:resources)"),
                {"resources": list(resources)},
            )
            for resource_id in resources:
                conn.execute(
                    text(
                        """
                        INSERT INTO infra_worker_leases(resource_id, owner_id, lease_id, epoch, expires_at)
                        VALUES (:resource_id, 'seed', :lease_id, 1, now() + interval '30 seconds')
                        """
                    ),
                    {"resource_id": resource_id, "lease_id": f"lease:{resource_id}"},
                )

        def operate(worker_id: str, first_resource: str, second_resource: str) -> tuple[str, int, tuple[str, ...]]:
            def transaction(repo: InfrastructureRepository) -> str:
                invocations[worker_id] += 1
                invocation = invocations[worker_id]
                repo.connection.execute(
                    text("SELECT resource_id FROM infra_worker_leases WHERE resource_id = :resource_id FOR UPDATE"),
                    {"resource_id": first_resource},
                ).one()
                if invocation == 1:
                    barrier.wait(timeout=10)
                repo.connection.execute(
                    text("SELECT resource_id FROM infra_worker_leases WHERE resource_id = :resource_id FOR UPDATE"),
                    {"resource_id": second_resource},
                ).one()
                repo.connection.execute(
                    text(
                        """
                        UPDATE infra_worker_leases
                        SET owner_id = owner_id || ':' || :worker_id
                        WHERE resource_id IN (:first_resource, :second_resource)
                        """
                    ),
                    {
                        "worker_id": worker_id,
                        "first_resource": first_resource,
                        "second_resource": second_resource,
                    },
                )
                return worker_id

            receipt = run_transaction_with_retry(
                engine,
                transaction,
                max_attempts=3,
                retry_sqlstates=("40P01",),
                backoff_seconds=0.02,
                statement_timeout_ms=5000,
            )
            return receipt.result, receipt.attempts, receipt.retried_sqlstates

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(
                executor.map(
                    lambda args: operate(*args),
                    [
                        ("worker-a", resources[0], resources[1]),
                        ("worker-b", resources[1], resources[0]),
                    ],
                )
            )

        if sorted(result[0] for result in results) != ["worker-a", "worker-b"]:
            errors.append(f"deadlock retry workers did not both complete: {results!r}")
        if sorted(result[1] for result in results) != [1, 2]:
            errors.append(f"deadlock retry attempt counts did not prove one retry: {results!r}")
        retried_sqlstates = [sqlstate for result in results for sqlstate in result[2]]
        if retried_sqlstates != ["40P01"]:
            errors.append(f"deadlock retry did not capture exactly one 40P01 retry: {results!r}")

        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    """
                    SELECT resource_id, owner_id
                    FROM infra_worker_leases
                    WHERE resource_id = ANY(:resources)
                    ORDER BY resource_id
                    """
                ),
                {"resources": list(resources)},
            ).all()
        if len(rows) != 2:
            errors.append(f"deadlock retry rows missing after verification: {rows!r}")
        for row in rows:
            owner_id = str(row.owner_id)
            if "worker-a" not in owner_id or "worker-b" not in owner_id:
                errors.append(f"deadlock retry row missing worker commits: {row!r}")
    finally:
        with engine.begin() as conn:
            conn.execute(
                text("DELETE FROM infra_worker_leases WHERE resource_id = ANY(:resources)"),
                {"resources": list(resources)},
            )
        engine.dispose()
    return errors


def main() -> int:
    errors = verify_phase04_postgres_deadlock_retry()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 PostgreSQL deadlock retry verification failed.")
        return 1
    print("PHASE04 PostgreSQL deadlock retry verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
