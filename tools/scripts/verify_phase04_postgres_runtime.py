from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from zuno.platform.database.foundation import InfrastructureUnitOfWork, create_foundation_engine

DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/zuno"


def verify_phase04_postgres_runtime() -> list[str]:
    engine = create_foundation_engine(DATABASE_URL)
    errors: list[str] = []
    try:
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM infra_worker_leases WHERE resource_id = 'phase04-lock-target'"))

        with InfrastructureUnitOfWork(engine, tenant_id="tenant-phase04") as repo:
            if not repo.check_readiness():
                errors.append("PostgreSQL readiness check failed")
            if repo.current_tenant_id() != "tenant-phase04":
                errors.append("PostgreSQL tenant context was not set inside UoW")

        with InfrastructureUnitOfWork(engine) as repo:
            if repo.current_tenant_id() != "":
                errors.append("PostgreSQL tenant context leaked outside transaction")

        try:
            with InfrastructureUnitOfWork(engine, statement_timeout_ms=100) as repo:
                repo.connection.execute(text("SELECT pg_sleep(1)"))
            errors.append("PostgreSQL statement_timeout did not cancel slow query")
        except DBAPIError:
            pass

        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO infra_worker_leases(resource_id, owner_id, lease_id, epoch, expires_at)
                    VALUES ('phase04-lock-target', 'worker-a', 'lease-a', 1, now() + interval '30 seconds')
                    """
                )
            )

        lock_conn = engine.connect()
        lock_tx = lock_conn.begin()
        try:
            lock_conn.execute(
                text("SELECT * FROM infra_worker_leases WHERE resource_id = 'phase04-lock-target' FOR UPDATE")
            )
            try:
                with InfrastructureUnitOfWork(engine, lock_timeout_ms=100) as repo:
                    repo.connection.execute(
                        text("SELECT * FROM infra_worker_leases WHERE resource_id = 'phase04-lock-target' FOR UPDATE")
                    )
                errors.append("PostgreSQL lock_timeout did not reject blocked lock acquisition")
            except DBAPIError:
                pass
        finally:
            lock_tx.rollback()
            lock_conn.close()

        with engine.begin() as conn:
            conn.execute(text("DELETE FROM infra_worker_leases WHERE resource_id = 'phase04-lock-target'"))
    finally:
        engine.dispose()
    return errors


def main() -> int:
    errors = verify_phase04_postgres_runtime()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 PostgreSQL runtime verification failed.")
        return 1
    print("PHASE04 PostgreSQL runtime verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
