from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError

from zuno.platform.database.foundation import create_foundation_engine

DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/zuno"
ADMIN_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"


def verify_phase04_postgres_connection_loss() -> list[str]:
    engine = create_foundation_engine(DATABASE_URL, pool_size=1, max_overflow=0)
    admin_engine = create_engine(ADMIN_URL, future=True)
    errors: list[str] = []
    try:
        connection = engine.connect()
        try:
            backend_pid = int(connection.execute(text("SELECT pg_backend_pid()")).scalar_one())
            with admin_engine.begin() as admin:
                terminated = bool(
                    admin.execute(
                        text("SELECT pg_terminate_backend(:backend_pid)"),
                        {"backend_pid": backend_pid},
                    ).scalar_one()
                )
            if not terminated:
                errors.append(f"PostgreSQL backend was not terminated: {backend_pid!r}")
            try:
                connection.execute(text("SELECT 1")).scalar_one()
                errors.append("terminated PostgreSQL connection did not fail closed")
            except DBAPIError:
                pass
        finally:
            connection.close()

        with engine.connect() as recovered:
            if recovered.execute(text("SELECT 1")).scalar_one() != 1:
                errors.append("PostgreSQL engine did not recover after terminated connection")
    finally:
        admin_engine.dispose()
        engine.dispose()
    return errors


def main() -> int:
    errors = verify_phase04_postgres_connection_loss()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 PostgreSQL connection loss verification failed.")
        return 1
    print("PHASE04 PostgreSQL connection loss verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
