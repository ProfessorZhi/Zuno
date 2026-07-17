from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

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


def _crashed_owner_code() -> str:
    return """
import os

from zuno.platform.database.foundation import InfrastructureUnitOfWork, create_foundation_engine

database_url = os.environ["ZUNO_TEST_POSTGRES_URL"]
engine = create_foundation_engine(database_url)
try:
    with InfrastructureUnitOfWork(engine) as repo:
        receipt = repo.claim_idempotency_receipt(
            scope="phase04-idempotency-owner-crash",
            key="owner-crash",
            owner="worker-crashed",
            request={"operation": "publish", "target": "phase04-owner-crash"},
            ttl_seconds=300,
        )
        assert receipt.acquired is True
        assert receipt.status == "in_progress"
        assert receipt.generation == 1
finally:
    engine.dispose()

os._exit(0)
"""


def verify_phase04_idempotency_owner_crash() -> list[str]:
    engine = create_foundation_engine(DATABASE_URL)
    errors: list[str] = []
    scope = "phase04-idempotency-owner-crash"
    key = "owner-crash"
    request = {"operation": "publish", "target": "phase04-owner-crash"}
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    DELETE FROM infra_idempotency_claims
                    WHERE scope = :scope AND idempotency_key = :key
                    """
                ),
                {"scope": scope, "key": key},
            )

        env = os.environ.copy()
        env["ZUNO_TEST_POSTGRES_URL"] = DATABASE_URL
        result = subprocess.run(
            [sys.executable, "-c", _crashed_owner_code()],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=30,
        )
        if result.returncode != 0:
            return [
                "owner subprocess failed before crash simulation: "
                f"returncode={result.returncode} stdout={result.stdout!r} stderr={result.stderr!r}"
            ]

        with engine.connect() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT owner, status, generation, result_ref
                    FROM infra_idempotency_claims
                    WHERE scope = :scope AND idempotency_key = :key
                    """
                ),
                {"scope": scope, "key": key},
            ).first()
        if row is None:
            return ["crashed owner claim was not committed before process exit"]
        if (row.owner, row.status, row.generation, row.result_ref) != ("worker-crashed", "in_progress", 1, None):
            errors.append(
                "crashed owner claim mismatch: "
                f"{(row.owner, row.status, row.generation, row.result_ref)!r}"
            )

        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    UPDATE infra_idempotency_claims
                    SET expires_at = now() - interval '1 second'
                    WHERE scope = :scope AND idempotency_key = :key
                    """
                ),
                {"scope": scope, "key": key},
            )

        uow = InfrastructureUnitOfWork(engine)
        with uow as repo:
            expired = repo.expire_stale_idempotency_claims()
            if f"{scope}:{key}" not in expired:
                errors.append(f"crashed owner claim was not expired: {expired!r}")
            replacement = repo.claim_idempotency_receipt(
                scope=scope,
                key=key,
                owner="worker-replacement",
                request=request,
                ttl_seconds=60,
            )
            if (
                replacement.acquired is not True
                or replacement.status != "in_progress"
                or replacement.generation != 2
                or replacement.result_ref != ""
                or replacement.owner != "worker-replacement"
            ):
                errors.append(f"replacement owner claim mismatch: {replacement!r}")
            try:
                repo.complete_idempotency(
                    scope=scope,
                    key=key,
                    owner="worker-crashed",
                    generation=1,
                    result_ref="effect:stale-crashed-owner",
                )
                errors.append("crashed owner stale generation completed after replacement")
            except FencingRejectedError:
                pass
            repo.complete_idempotency(
                scope=scope,
                key=key,
                owner="worker-replacement",
                generation=replacement.generation,
                result_ref="effect:replacement-owner",
            )

        with uow as repo:
            replay = repo.claim_idempotency_receipt(
                scope=scope,
                key=key,
                owner="worker-replay",
                request=request,
                ttl_seconds=60,
            )
            if (
                replay.acquired is not False
                or replay.status != "completed"
                or replay.generation != 2
                or replay.result_ref != "effect:replacement-owner"
            ):
                errors.append(f"replacement result replay mismatch: {replay!r}")
    finally:
        engine.dispose()
    return errors


def main() -> int:
    errors = verify_phase04_idempotency_owner_crash()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 idempotency owner crash verification failed.")
        return 1
    print("PHASE04 idempotency owner crash verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
