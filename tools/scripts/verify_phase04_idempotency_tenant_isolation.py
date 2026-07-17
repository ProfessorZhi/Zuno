from __future__ import annotations

from sqlalchemy import text

from zuno.platform.database.foundation import (
    InfrastructureConflictError,
    InfrastructureUnitOfWork,
    create_foundation_engine,
)

DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/zuno"


def verify_phase04_idempotency_tenant_isolation() -> list[str]:
    engine = create_foundation_engine(DATABASE_URL)
    errors: list[str] = []
    scope = "phase04-idempotency-tenant"
    key = "same-key"
    request_a = {"operation": "publish", "tenant": "a"}
    request_b = {"operation": "publish", "tenant": "b"}
    try:
        with engine.begin() as conn:
            conn.execute(
                text("DELETE FROM infra_idempotency_claims WHERE scope = :scope AND idempotency_key = :key"),
                {"scope": scope, "key": key},
            )

        with InfrastructureUnitOfWork(engine, tenant_id="tenant-a") as repo:
            status, generation, result_ref = repo.claim_idempotency(
                scope=scope,
                key=key,
                owner="worker-a",
                request=request_a,
            )
            if (status, generation, result_ref) != ("in_progress", 1, ""):
                errors.append(f"tenant-a initial claim mismatch: {(status, generation, result_ref)!r}")
            repo.complete_idempotency(
                scope=scope,
                key=key,
                owner="worker-a",
                generation=generation,
                result_ref="effect:tenant-a",
            )

        with InfrastructureUnitOfWork(engine, tenant_id="tenant-b") as repo:
            status, generation, result_ref = repo.claim_idempotency(
                scope=scope,
                key=key,
                owner="worker-b",
                request=request_b,
            )
            if (status, generation, result_ref) != ("in_progress", 1, ""):
                errors.append(f"tenant-b isolated claim mismatch: {(status, generation, result_ref)!r}")
            repo.complete_idempotency(
                scope=scope,
                key=key,
                owner="worker-b",
                generation=generation,
                result_ref="effect:tenant-b",
            )

        with InfrastructureUnitOfWork(engine, tenant_id="tenant-a") as repo:
            status, generation, result_ref = repo.claim_idempotency(
                scope=scope,
                key=key,
                owner="worker-a-replay",
                request=request_a,
            )
            if (status, generation, result_ref) != ("completed", 1, "effect:tenant-a"):
                errors.append(f"tenant-a replay mismatch: {(status, generation, result_ref)!r}")
            try:
                repo.claim_idempotency(
                    scope=scope,
                    key=key,
                    owner="worker-a-conflict",
                    request=request_b,
                )
                errors.append("tenant-a accepted same key with tenant-b request hash")
            except InfrastructureConflictError:
                pass

        with InfrastructureUnitOfWork(engine, tenant_id="tenant-b") as repo:
            status, generation, result_ref = repo.claim_idempotency(
                scope=scope,
                key=key,
                owner="worker-b-replay",
                request=request_b,
            )
            if (status, generation, result_ref) != ("completed", 1, "effect:tenant-b"):
                errors.append(f"tenant-b replay mismatch: {(status, generation, result_ref)!r}")

        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    """
                    SELECT tenant_id, status, generation, result_ref
                    FROM infra_idempotency_claims
                    WHERE scope = :scope AND idempotency_key = :key
                    ORDER BY tenant_id
                    """
                ),
                {"scope": scope, "key": key},
            ).all()
        expected = [
            ("tenant-a", "completed", 1, "effect:tenant-a"),
            ("tenant-b", "completed", 1, "effect:tenant-b"),
        ]
        actual = [(str(row.tenant_id), str(row.status), int(row.generation), str(row.result_ref)) for row in rows]
        if actual != expected:
            errors.append(f"tenant isolated idempotency rows mismatch: {actual!r}")
    finally:
        engine.dispose()
    return errors


def main() -> int:
    errors = verify_phase04_idempotency_tenant_isolation()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 idempotency tenant isolation verification failed.")
        return 1
    print("PHASE04 idempotency tenant isolation verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
