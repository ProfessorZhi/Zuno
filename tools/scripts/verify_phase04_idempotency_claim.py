from __future__ import annotations

from sqlalchemy import text

from zuno.platform.database.foundation import (
    FencingRejectedError,
    InfrastructureConflictError,
    InfrastructureUnitOfWork,
    create_foundation_engine,
)

DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/zuno"


def verify_phase04_idempotency_claim() -> list[str]:
    engine = create_foundation_engine(DATABASE_URL)
    errors: list[str] = []
    scope = "phase04-idempotency"
    key = "claim-lifecycle"
    request = {"operation": "publish", "target": "phase04"}
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

        uow = InfrastructureUnitOfWork(engine)
        with uow as repo:
            status, generation, result_ref = repo.claim_idempotency(
                scope=scope,
                key=key,
                owner="worker-a",
                request=request,
                ttl_seconds=30,
            )
            if (status, generation, result_ref) != ("in_progress", 1, ""):
                errors.append(f"initial claim mismatch: {(status, generation, result_ref)!r}")
            repo.renew_idempotency(scope=scope, key=key, owner="worker-a", generation=generation, ttl_seconds=120)
            try:
                repo.renew_idempotency(scope=scope, key=key, owner="worker-b", generation=generation, ttl_seconds=120)
                errors.append("wrong owner renewed idempotency claim")
            except FencingRejectedError:
                pass
            try:
                repo.claim_idempotency(
                    scope=scope,
                    key=key,
                    owner="worker-b",
                    request={"operation": "publish", "target": "other"},
                )
                errors.append("different request hash did not fail closed")
            except InfrastructureConflictError:
                pass

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

        with uow as repo:
            expired = repo.expire_stale_idempotency_claims()
            if f"{scope}:{key}" not in expired:
                errors.append(f"expired claim was not returned: {expired!r}")
            status, replacement_generation, result_ref = repo.claim_idempotency(
                scope=scope,
                key=key,
                owner="worker-b",
                request=request,
                ttl_seconds=30,
            )
            if (status, replacement_generation, result_ref) != ("in_progress", generation + 1, ""):
                errors.append(f"replacement claim mismatch: {(status, replacement_generation, result_ref)!r}")
            try:
                repo.complete_idempotency(scope=scope, key=key, generation=generation, result_ref="effect:stale")
                errors.append("stale generation completed idempotency claim")
            except FencingRejectedError:
                pass
            repo.complete_idempotency(
                scope=scope,
                key=key,
                generation=replacement_generation,
                result_ref="effect:new",
            )

        with uow as repo:
            status, completed_generation, result_ref = repo.claim_idempotency(
                scope=scope,
                key=key,
                owner="worker-c",
                request=request,
            )
            if (status, completed_generation, result_ref) != ("completed", replacement_generation, "effect:new"):
                errors.append(f"completed result replay mismatch: {(status, completed_generation, result_ref)!r}")
    finally:
        engine.dispose()
    return errors


def main() -> int:
    errors = verify_phase04_idempotency_claim()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 idempotency claim verification failed.")
        return 1
    print("PHASE04 idempotency claim verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
