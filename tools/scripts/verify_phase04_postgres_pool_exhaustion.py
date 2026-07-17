from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import TimeoutError

from zuno.platform.database.foundation import create_foundation_engine

DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/zuno"


def verify_phase04_postgres_pool_exhaustion() -> list[str]:
    engine = create_foundation_engine(
        DATABASE_URL,
        pool_size=1,
        max_overflow=0,
        pool_timeout=1,
    )
    errors: list[str] = []
    try:
        first_connection = engine.connect()
        try:
            if first_connection.execute(text("SELECT 1")).scalar_one() != 1:
                errors.append("PostgreSQL first pooled connection readiness failed")
            try:
                with engine.connect() as second_connection:
                    second_connection.execute(text("SELECT 1")).scalar_one()
                errors.append("PostgreSQL pool exhaustion did not reject second checkout")
            except TimeoutError:
                pass
        finally:
            first_connection.close()

        with engine.connect() as recovered_connection:
            if recovered_connection.execute(text("SELECT 1")).scalar_one() != 1:
                errors.append("PostgreSQL pool did not recover after checkout was released")
    finally:
        engine.dispose()
    return errors


def main() -> int:
    errors = verify_phase04_postgres_pool_exhaustion()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 PostgreSQL pool exhaustion verification failed.")
        return 1
    print("PHASE04 PostgreSQL pool exhaustion verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
